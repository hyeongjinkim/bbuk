from django.contrib import admin
from .models import Board, Post, Comment, Vote


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ['name', 'board_type', 'order', 'created_at']
    list_filter = ['board_type']
    search_fields = ['name']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'board', 'author_name', 'author_fingerprint', 
                    'upvote_count', 'view_count', 'created_at']
    list_filter = ['board', 'created_at']
    search_fields = ['title', 'content', 'author_name']
    readonly_fields = ['author_fingerprint', 'password_hash', 'created_at', 'updated_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author_name', 'author_fingerprint', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'author_name']
    readonly_fields = ['author_fingerprint', 'password_hash', 'created_at']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['post', 'voter_fingerprint', 'vote_type', 'created_at']
    list_filter = ['vote_type', 'created_at']
    readonly_fields = ['created_at']
