# 비백억 커뮤니티 - 빠른 시작 가이드

## 🚀 5분 안에 시작하기

### 1️⃣ 필수 요구사항

- Docker
- Docker Compose

### 2️⃣ 설치 및 실행

```bash
# 프로젝트 디렉토리로 이동
cd biback-community

# 실행 권한 부여
chmod +x start.sh

# 한 번에 시작!
./start.sh
```

### 3️⃣ 접속

브라우저에서 접속:
- **커뮤니티**: http://localhost:3000

끝! 🎉

## 📱 기본 사용법

### 글 작성하기
1. 자유게시판 클릭
2. "글쓰기" 버튼 클릭
3. 제목, 내용, 닉네임, 비밀번호 입력
4. 작성하기!

### 추천/비추천
- 게시글 상세 페이지에서 👍/👎 버튼 클릭

### 댓글 달기
- 게시글 하단에서 댓글 작성

### 글 수정/삭제
- 작성 시 입력한 비밀번호로 수정/삭제 가능

## 🔧 관리자 기능

### 뉴스 게시글 작성

```bash
curl -X POST http://localhost:8000/api/admin/news/ \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: biback_admin_2024" \
  -d '{
    "title": "오늘의 뉴스",
    "content": "뉴스 내용입니다.",
    "author_name": "관리자"
  }'
```

## 🛑 종료

```bash
docker-compose down
```

## 📊 로그 확인

```bash
# 모든 서비스 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
docker-compose logs -f frontend
```

## ⚙️ 추가 설정

### 관리자 계정 생성 (Django Admin)

```bash
docker-compose exec backend python manage.py createsuperuser
```

그 다음 http://localhost:8000/admin 접속

### 데이터베이스 초기화

```bash
docker-compose down -v
./start.sh
```

## 🐛 문제 해결

### 포트가 이미 사용 중
```bash
# 포트 변경 (docker-compose.yml 수정)
ports:
  - "3001:3000"  # 프론트엔드
  - "8001:8000"  # 백엔드
```

### 컨테이너 재시작
```bash
docker-compose restart
```

### 완전히 재설치
```bash
docker-compose down -v
docker-compose up -d --build
./start.sh
```

## 💡 팁

1. **닉네임 저장**: 한 번 입력한 닉네임은 브라우저에 저장됩니다
2. **레이트 리밋**: 1분에 최대 3개 글만 작성 가능합니다
3. **고유 식별자**: 같은 시간대에 같은 IP는 같은 니모닉 단어를 받습니다
4. **추천수 정렬**: 게시판에서 "추천순" 정렬 가능합니다

## 📞 지원

문제가 있으시면 이슈를 등록해주세요!
