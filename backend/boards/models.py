from django.db import models
from django.utils import timezone


class Board(models.Model):
    """게시판"""
    BOARD_TYPE_CHOICES = [
        ('free', '자유게시판'),
        ('news', '뉴스게시판'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='게시판명')
    board_type = models.CharField(
        max_length=10, 
        choices=BOARD_TYPE_CHOICES, 
        unique=True,
        verbose_name='게시판 타입'
    )
    description = models.TextField(blank=True, verbose_name='설명')
    order = models.IntegerField(default=0, verbose_name='정렬순서')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'id']
        verbose_name = '게시판'
        verbose_name_plural = '게시판'
    
    def __str__(self):
        return self.name


class Post(models.Model):
    """게시글"""
    board = models.ForeignKey(
        Board, 
        on_delete=models.CASCADE, 
        related_name='posts',
        verbose_name='게시판'
    )
    title = models.CharField(max_length=200, verbose_name='제목')
    content = models.TextField(verbose_name='내용')
    author_name = models.CharField(max_length=50, verbose_name='작성자')
    
    # 비밀번호 해시 (수정/삭제용)
    password_hash = models.CharField(max_length=64)
    
    # 작성자 고유 식별자 (니모닉 단어)
    author_fingerprint = models.CharField(max_length=20, db_index=True)
    
    # 추천/비추천 카운트 (캐시)
    upvote_count = models.IntegerField(default=0, verbose_name='추천수')
    downvote_count = models.IntegerField(default=0, verbose_name='비추천수')
    
    # 조회수
    view_count = models.IntegerField(default=0, verbose_name='조회수')
    
    # 댓글수 캐시
    comment_count = models.IntegerField(default=0, verbose_name='댓글수')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['board', '-created_at']),
            models.Index(fields=['-upvote_count']),
        ]
        verbose_name = '게시글'
        verbose_name_plural = '게시글'
    
    def __str__(self):
        return self.title


class Comment(models.Model):
    """댓글"""
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='comments',
        verbose_name='게시글'
    )
    content = models.TextField(verbose_name='내용')
    author_name = models.CharField(max_length=50, verbose_name='작성자')
    
    # 비밀번호 해시 (삭제용)
    password_hash = models.CharField(max_length=64)
    
    # 작성자 고유 식별자 (니모닉 단어)
    author_fingerprint = models.CharField(max_length=20, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
        ]
        verbose_name = '댓글'
        verbose_name_plural = '댓글'
    
    def __str__(self):
        return f"{self.post.title} - {self.author_name}"


class Vote(models.Model):
    """추천/비추천"""
    VOTE_TYPE_CHOICES = [
        (1, '추천'),
        (-1, '비추천'),
    ]
    
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='votes',
        verbose_name='게시글'
    )
    
    # 투표자 고유 식별자 (fingerprint)
    voter_fingerprint = models.CharField(max_length=20, db_index=True)
    
    vote_type = models.SmallIntegerField(
        choices=VOTE_TYPE_CHOICES,
        verbose_name='투표 타입'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # 한 사용자가 한 게시글에 한 번만 투표 가능
        unique_together = [['post', 'voter_fingerprint']]
        indexes = [
            models.Index(fields=['post', 'voter_fingerprint']),
        ]
        verbose_name = '투표'
        verbose_name_plural = '투표'
    
    def __str__(self):
        return f"{self.post.title} - {self.get_vote_type_display()}"
