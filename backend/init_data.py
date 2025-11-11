#!/usr/bin/env python
"""
초기 게시판 데이터 생성 스크립트
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from boards.models import Board

def create_initial_boards():
    """초기 게시판 생성"""
    boards = [
        {
            'name': '자유게시판',
            'board_type': 'free',
            'description': '자유롭게 글을 작성할 수 있는 게시판입니다.',
            'order': 1
        },
        {
            'name': '뉴스',
            'board_type': 'news',
            'description': '최신 뉴스와 정보를 공유하는 게시판입니다.',
            'order': 2
        }
    ]
    
    for board_data in boards:
        board, created = Board.objects.get_or_create(
            board_type=board_data['board_type'],
            defaults=board_data
        )
        if created:
            print(f"✓ 게시판 생성됨: {board.name}")
        else:
            print(f"- 게시판 이미 존재: {board.name}")

if __name__ == '__main__':
    create_initial_boards()
    print("\n초기 데이터 설정 완료!")
