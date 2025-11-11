from rest_framework import serializers
from .models import Board, Post, Comment, Vote
from .utils import hash_password


class BoardSerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Board
        fields = ['id', 'name', 'board_type', 'description', 'post_count']
    
    def get_post_count(self, obj):
        return obj.posts.count()


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author_name', 'author_fingerprint', 'created_at']
        read_only_fields = ['id', 'author_fingerprint', 'created_at']


class CommentCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4, max_length=20)
    
    class Meta:
        model = Comment
        fields = ['content', 'author_name', 'password']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['password_hash'] = hash_password(password)
        return super().create(validated_data)


class PostListSerializer(serializers.ModelSerializer):
    """게시글 목록용 (가벼운 버전)"""
    board_name = serializers.CharField(source='board.name', read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'board', 'board_name', 'title', 'author_name', 
            'author_fingerprint', 'view_count', 'comment_count',
            'upvote_count', 'downvote_count', 'created_at'
        ]
        read_only_fields = fields


class PostDetailSerializer(serializers.ModelSerializer):
    """게시글 상세용"""
    board_name = serializers.CharField(source='board.name', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'board', 'board_name', 'title', 'content', 
            'author_name', 'author_fingerprint', 'view_count', 
            'comment_count', 'upvote_count', 'downvote_count',
            'created_at', 'updated_at', 'comments'
        ]
        read_only_fields = [
            'id', 'author_fingerprint', 'view_count', 'comment_count',
            'upvote_count', 'downvote_count', 'created_at', 'updated_at'
        ]


class PostCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4, max_length=20)
    
    class Meta:
        model = Post
        fields = ['board', 'title', 'content', 'author_name', 'password']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['password_hash'] = hash_password(password)
        return super().create(validated_data)


class PostUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4, max_length=20)
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'password']
    
    def validate_password(self, value):
        """비밀번호 검증"""
        from .utils import verify_password
        instance = self.instance
        if not verify_password(value, instance.password_hash):
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return value


class VoteSerializer(serializers.Serializer):
    vote_type = serializers.ChoiceField(choices=[1, -1])


class AdminPostCreateSerializer(serializers.ModelSerializer):
    """관리자용 뉴스 게시글 작성 (비밀번호 불필요)"""
    class Meta:
        model = Post
        fields = ['title', 'content', 'author_name']
    
    def create(self, validated_data):
        # 뉴스 게시판 자동 지정
        from .models import Board
        news_board = Board.objects.get(board_type='news')
        validated_data['board'] = news_board
        validated_data['password_hash'] = hash_password('admin_no_edit')
        validated_data['author_fingerprint'] = 'admin'
        return super().create(validated_data)
