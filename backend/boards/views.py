from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.db import transaction
from django.db.models import F

from .models import Board, Post, Comment, Vote
from .serializers import (
    BoardSerializer, PostListSerializer, PostDetailSerializer,
    PostCreateSerializer, PostUpdateSerializer,
    CommentSerializer, CommentCreateSerializer,
    VoteSerializer, AdminPostCreateSerializer
)
from .utils import get_user_fingerprint, check_rate_limit, verify_password


def get_client_ip(request):
    """클라이언트 IP 추출"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class BoardViewSet(viewsets.ReadOnlyModelViewSet):
    """게시판 목록/상세"""
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [AllowAny]


class PostViewSet(viewsets.ModelViewSet):
    """게시글 CRUD"""
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Post.objects.select_related('board').all()
        
        # 게시판 타입으로 필터
        board_type = self.request.query_params.get('board_type')
        if board_type:
            queryset = queryset.filter(board__board_type=board_type)
        
        # 정렬 옵션
        sort = self.request.query_params.get('sort', 'recent')
        if sort == 'popular':
            queryset = queryset.order_by('-upvote_count', '-created_at')
        else:  # recent
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        elif self.action == 'create':
            return PostCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PostUpdateSerializer
        return PostDetailSerializer
    
    def create(self, request, *args, **kwargs):
        """게시글 작성"""
        ip = get_client_ip(request)
        fingerprint = get_user_fingerprint(ip)
        
        # 레이트 리밋 체크
        if not check_rate_limit(fingerprint, cache):
            return Response(
                {'error': '너무 자주 글을 작성하고 있습니다. 잠시 후 다시 시도해주세요.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 뉴스 게시판은 일반 사용자가 작성 불가
        board_id = serializer.validated_data.get('board').id
        board = Board.objects.get(id=board_id)
        if board.board_type == 'news':
            return Response(
                {'error': '뉴스 게시판에는 관리자만 글을 작성할 수 있습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        post = serializer.save(author_fingerprint=fingerprint)
        
        return Response(
            PostDetailSerializer(post).data,
            status=status.HTTP_201_CREATED
        )
    
    def retrieve(self, request, *args, **kwargs):
        """게시글 조회 (조회수 증가)"""
        instance = self.get_object()
        
        # 조회수 증가 (F() 사용으로 race condition 방지)
        Post.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        instance.refresh_from_db()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """게시글 수정"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(PostDetailSerializer(instance).data)
    
    def destroy(self, request, *args, **kwargs):
        """게시글 삭제"""
        instance = self.get_object()
        password = request.data.get('password')
        
        if not password:
            return Response(
                {'error': '비밀번호를 입력해주세요.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not verify_password(password, instance.password_hash):
            return Response(
                {'error': '비밀번호가 일치하지 않습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        """추천/비추천"""
        post = self.get_object()
        ip = get_client_ip(request)
        fingerprint = get_user_fingerprint(ip)
        
        serializer = VoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        vote_type = serializer.validated_data['vote_type']
        
        with transaction.atomic():
            # 기존 투표 확인
            existing_vote = Vote.objects.filter(
                post=post,
                voter_fingerprint=fingerprint
            ).first()
            
            if existing_vote:
                # 이미 투표한 경우
                if existing_vote.vote_type == vote_type:
                    # 같은 투표 취소
                    existing_vote.delete()
                    if vote_type == 1:
                        post.upvote_count = F('upvote_count') - 1
                    else:
                        post.downvote_count = F('downvote_count') - 1
                    post.save(update_fields=['upvote_count', 'downvote_count'])
                    action_taken = 'cancelled'
                else:
                    # 다른 투표로 변경
                    existing_vote.vote_type = vote_type
                    existing_vote.save()
                    if vote_type == 1:
                        post.upvote_count = F('upvote_count') + 1
                        post.downvote_count = F('downvote_count') - 1
                    else:
                        post.upvote_count = F('upvote_count') - 1
                        post.downvote_count = F('downvote_count') + 1
                    post.save(update_fields=['upvote_count', 'downvote_count'])
                    action_taken = 'changed'
            else:
                # 새로운 투표
                Vote.objects.create(
                    post=post,
                    voter_fingerprint=fingerprint,
                    vote_type=vote_type
                )
                if vote_type == 1:
                    post.upvote_count = F('upvote_count') + 1
                else:
                    post.downvote_count = F('downvote_count') + 1
                post.save(update_fields=['upvote_count', 'downvote_count'])
                action_taken = 'voted'
            
            post.refresh_from_db()
        
        return Response({
            'action': action_taken,
            'upvote_count': post.upvote_count,
            'downvote_count': post.downvote_count
        })
    
    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        """댓글 작성"""
        post = self.get_object()
        ip = get_client_ip(request)
        fingerprint = get_user_fingerprint(ip)
        
        # 레이트 리밋 체크
        if not check_rate_limit(f"comment_{fingerprint}", cache):
            return Response(
                {'error': '너무 자주 댓글을 작성하고 있습니다. 잠시 후 다시 시도해주세요.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            comment = serializer.save(
                post=post,
                author_fingerprint=fingerprint
            )
            
            # 댓글 수 업데이트
            post.comment_count = F('comment_count') + 1
            post.save(update_fields=['comment_count'])
        
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED
        )


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_comment(request, pk):
    """댓글 삭제"""
    comment = get_object_or_404(Comment, pk=pk)
    password = request.data.get('password')
    
    if not password:
        return Response(
            {'error': '비밀번호를 입력해주세요.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not verify_password(password, comment.password_hash):
        return Response(
            {'error': '비밀번호가 일치하지 않습니다.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    with transaction.atomic():
        post = comment.post
        comment.delete()
        
        # 댓글 수 업데이트
        post.comment_count = F('comment_count') - 1
        post.save(update_fields=['comment_count'])
    
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_create_news(request):
    """관리자용 뉴스 게시글 작성"""
    # 간단한 토큰 인증 (실제로는 더 강력한 인증 사용)
    admin_token = request.headers.get('X-Admin-Token')
    if admin_token != 'biback_admin_2024':  # 환경변수로 관리 권장
        return Response(
            {'error': '관리자 권한이 필요합니다.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = AdminPostCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    post = serializer.save()
    
    return Response(
        PostDetailSerializer(post).data,
        status=status.HTTP_201_CREATED
    )
