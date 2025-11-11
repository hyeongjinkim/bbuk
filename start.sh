#!/bin/bash

echo "🚀 비백억 커뮤니티 시작 중..."
echo ""

# Docker Compose로 모든 서비스 시작
echo "📦 Docker 컨테이너 시작..."
docker-compose up -d

# 백엔드가 준비될 때까지 대기
echo "⏳ 백엔드 서비스 대기 중..."
sleep 10

# 마이그레이션
echo "🔧 데이터베이스 마이그레이션..."
docker-compose exec -T backend python manage.py makemigrations
docker-compose exec -T backend python manage.py migrate

# 초기 데이터 생성
echo "📝 초기 게시판 데이터 생성..."
docker-compose exec -T backend python init_data.py

echo ""
echo "✅ 설정 완료!"
echo ""
echo "🌐 접속 주소:"
echo "   프론트엔드: http://localhost:3000"
echo "   백엔드 API: http://localhost:8000/api"
echo "   관리자 페이지: http://localhost:8000/admin"
echo ""
echo "📋 로그 확인: docker-compose logs -f"
echo "🛑 종료: docker-compose down"
echo ""
