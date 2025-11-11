# 비백억 커뮤니티

Python 3 + Django 4 + Nuxt 3 기반의 현대적인 비회원제 커뮤니티

## 주요 특징

- ✅ **비회원 시스템**: 디시인사이드처럼 닉네임+비밀번호로 작성
- ✅ **고유 식별자**: IP+시간 해시를 비트코인 니모닉 단어로 변환하여 사용자 식별
- ✅ **추천/비추천**: 효율적인 투표 시스템 (중복 방지)
- ✅ **2개 게시판**: 자유게시판 + 뉴스게시판
- ✅ **모바일 최적화**: 한국 전통 커뮤니티 스타일의 모바일 UI
- ✅ **레이트 리밋**: 1분에 최대 3개 글 작성 제한

## 기술 스택

### 백엔드
- Python 3.11
- Django 4.2 + Django REST Framework
- PostgreSQL 15
- Redis 7

### 프론트엔드
- Nuxt 3
- Vue 3 (Composition API)
- Tailwind CSS
- Pinia

## 설치 및 실행

### 1. 프로젝트 클론

```bash
git clone <repository-url>
cd biback-community
```

### 2. Docker로 실행

```bash
# 모든 서비스 시작
docker-compose up -d

# 백엔드 마이그레이션
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

# 초기 게시판 데이터 생성
docker-compose exec backend python init_data.py

# 관리자 계정 생성 (선택사항)
docker-compose exec backend python manage.py createsuperuser
```

### 3. 접속

- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:8000/api
- **관리자 페이지**: http://localhost:8000/admin

## API 엔드포인트

### 게시판
- `GET /api/boards/` - 게시판 목록

### 게시글
- `GET /api/posts/` - 게시글 목록 (페이징)
  - Query: `board_type`, `page`, `sort`
- `GET /api/posts/{id}/` - 게시글 상세
- `POST /api/posts/` - 게시글 작성
- `PUT /api/posts/{id}/` - 게시글 수정
- `DELETE /api/posts/{id}/` - 게시글 삭제
- `POST /api/posts/{id}/vote/` - 추천/비추천
- `POST /api/posts/{id}/comment/` - 댓글 작성

### 댓글
- `DELETE /api/comments/{id}/` - 댓글 삭제

### 관리자
- `POST /api/admin/news/` - 뉴스 게시글 작성
  - Header: `X-Admin-Token: biback_admin_2024`

## 게시글 작성 예시

```json
POST /api/posts/
{
  "board": 1,
  "title": "안녕하세요",
  "content": "첫 게시글입니다.",
  "author_name": "홍길동",
  "password": "1234"
}
```

## 추천/비추천 예시

```json
POST /api/posts/1/vote/
{
  "vote_type": 1  // 1: 추천, -1: 비추천
}
```

## 관리자 뉴스 작성 예시

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

## 디렉토리 구조

```
biback-community/
├── backend/              # Django 백엔드
│   ├── config/          # 설정 파일
│   ├── boards/          # 게시판 앱
│   │   ├── models.py    # 데이터베이스 모델
│   │   ├── views.py     # API 뷰
│   │   ├── serializers.py
│   │   └── utils.py     # 유틸리티 (니모닉 변환)
│   └── manage.py
├── frontend/            # Nuxt 프론트엔드
│   ├── pages/          # 페이지 컴포넌트
│   ├── layouts/        # 레이아웃
│   ├── stores/         # Pinia 스토어
│   ├── composables/    # API 통신
│   └── assets/         # CSS
└── docker-compose.yml
```

## 주요 기능 설명

### 비회원 시스템
- 게시글/댓글 작성 시 닉네임과 비밀번호 입력
- IP + 시간(분 단위) 조합을 SHA256 해싱
- 해시값을 BIP39 니모닉 2048개 단어 중 하나로 변환
- 같은 분에 같은 IP는 같은 단어를 받음 (고유성 확인)

### 레이트 리밋
- Redis 기반으로 1분에 최대 3개 글 작성 제한
- 니모닉 단어를 키로 사용하여 추적

### 추천/비추천
- Vote 모델로 중복 투표 방지 (unique_together)
- Post 모델에 upvote_count, downvote_count 캐시
- F() 표현식으로 race condition 방지

## 환경 변수

`.env` 파일 생성 (선택사항):

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=biback
DB_USER=biback
DB_PASSWORD=biback2024
DB_HOST=db
DB_PORT=5432
REDIS_URL=redis://redis:6379/0
```

## 개발 모드

```bash
# 백엔드 개발 서버
cd backend
python manage.py runserver

# 프론트엔드 개발 서버
cd frontend
npm run dev
```

## 프로덕션 빌드

```bash
# 프론트엔드 빌드
cd frontend
npm run build

# 프로덕션 모드로 실행
npm run preview
```

## 라이센스

MIT

## 기여

Pull Request는 언제나 환영합니다!
