<template>
  <div>
    <div v-if="pending" class="text-center py-8">
      로딩중...
    </div>
    
    <div v-else-if="error" class="text-center py-8 text-red-600">
      게시글을 찾을 수 없습니다.
    </div>
    
    <div v-else-if="post">
      <!-- 헤더 -->
      <NuxtLink :to="`/board/${post.board_name === '자유게시판' ? 'free' : 'news'}`" class="text-sm text-gray-600 mb-2 inline-block">
        ← {{ post.board_name }}으로 돌아가기
      </NuxtLink>

      <!-- 게시글 -->
      <div class="bg-white border border-gray-300 rounded mb-4">
        <!-- 제목 -->
        <div class="border-b border-gray-300 p-4">
          <h1 class="text-xl font-bold mb-2">{{ post.title }}</h1>
          <div class="text-sm text-gray-600">
            <span class="text-blue-600">{{ post.author_fingerprint }}</span>
            · {{ formatDate(post.created_at) }}
            · 조회 {{ post.view_count }}
          </div>
        </div>

        <!-- 내용 -->
        <div class="p-4 whitespace-pre-wrap break-words">
          {{ post.content }}
        </div>

        <!-- 추천/비추천 -->
        <div class="border-t border-gray-300 p-4 flex justify-center gap-3">
          <button 
            @click="vote(1)"
            class="px-6 py-2 bg-red-50 text-red-600 rounded hover:bg-red-100 transition-colors font-medium"
          >
            👍 추천 {{ post.upvote_count }}
          </button>
          <button 
            @click="vote(-1)"
            class="px-6 py-2 bg-blue-50 text-blue-600 rounded hover:bg-blue-100 transition-colors font-medium"
          >
            👎 비추천 {{ post.downvote_count }}
          </button>
        </div>

        <!-- 수정/삭제 버튼 -->
        <div class="border-t border-gray-300 p-3 flex justify-end gap-2">
          <button 
            @click="showEditModal = true"
            class="text-sm text-gray-600 hover:text-gray-900"
          >
            수정
          </button>
          <button 
            @click="showDeleteModal = true"
            class="text-sm text-red-600 hover:text-red-800"
          >
            삭제
          </button>
        </div>
      </div>

      <!-- 댓글 목록 -->
      <div class="bg-white border border-gray-300 rounded">
        <div class="border-b border-gray-300 p-3">
          <h2 class="font-bold">댓글 {{ post.comment_count }}개</h2>
        </div>

        <div v-for="comment in post.comments" :key="comment.id" class="border-b border-gray-200 p-3">
          <div class="text-sm text-gray-600 mb-1">
            <span class="text-blue-600">{{ comment.author_fingerprint }}</span>
            · {{ formatDate(comment.created_at) }}
          </div>
          <div class="whitespace-pre-wrap break-words mb-2">{{ comment.content }}</div>
          <button 
            @click="deleteComment(comment.id)"
            class="text-xs text-red-600 hover:text-red-800"
          >
            삭제
          </button>
        </div>

        <!-- 댓글 작성 -->
        <div class="p-3">
          <textarea 
            v-model="commentForm.content"
            placeholder="댓글을 입력하세요"
            class="input-field mb-2 h-20 resize-none"
          ></textarea>
          <div class="flex gap-2">
            <input 
              v-model="commentForm.author_name"
              placeholder="닉네임"
              class="input-field flex-1"
              maxlength="50"
            />
            <input 
              v-model="commentForm.password"
              type="password"
              placeholder="비밀번호"
              class="input-field flex-1"
              maxlength="20"
            />
          </div>
          <button 
            @click="submitComment"
            :disabled="!commentForm.content || !commentForm.author_name || !commentForm.password"
            class="btn-primary w-full mt-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            댓글 작성
          </button>
        </div>
      </div>
    </div>

    <!-- 수정 모달 -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-lg font-bold mb-4">게시글 수정</h3>
        <input 
          v-model="editPassword"
          type="password"
          placeholder="비밀번호"
          class="input-field mb-4"
        />
        <div class="flex gap-2">
          <button @click="showEditModal = false" class="btn-secondary flex-1">
            취소
          </button>
          <button @click="editPost" class="btn-primary flex-1">
            확인
          </button>
        </div>
      </div>
    </div>

    <!-- 삭제 모달 -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-lg font-bold mb-4">게시글 삭제</h3>
        <p class="text-sm text-gray-600 mb-4">정말로 삭제하시겠습니까?</p>
        <input 
          v-model="deletePassword"
          type="password"
          placeholder="비밀번호"
          class="input-field mb-4"
        />
        <div class="flex gap-2">
          <button @click="showDeleteModal = false" class="btn-secondary flex-1">
            취소
          </button>
          <button @click="deletePost" class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 flex-1">
            삭제
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const api = useApi()
const userStore = useUserStore()

const postId = parseInt(route.params.id as string)

const { data: post, pending, error, refresh } = await useAsyncData(
  `post-${postId}`,
  () => api.getPost(postId)
)

const commentForm = reactive({
  content: '',
  author_name: userStore.savedAuthorName,
  password: ''
})

const showEditModal = ref(false)
const showDeleteModal = ref(false)
const editPassword = ref('')
const deletePassword = ref('')

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const vote = async (voteType: number) => {
  try {
    const result = await api.votePost(postId, voteType)
    if (post.value) {
      post.value.upvote_count = result.upvote_count
      post.value.downvote_count = result.downvote_count
    }
  } catch (err: any) {
    alert(err?.data?.error || '투표 중 오류가 발생했습니다.')
  }
}

const submitComment = async () => {
  if (!commentForm.content || !commentForm.author_name || !commentForm.password) {
    alert('모든 항목을 입력해주세요.')
    return
  }

  try {
    await api.createComment(postId, commentForm)
    userStore.saveAuthorName(commentForm.author_name)
    commentForm.content = ''
    commentForm.password = ''
    await refresh()
    alert('댓글이 작성되었습니다.')
  } catch (err: any) {
    alert(err?.data?.error || '댓글 작성 중 오류가 발생했습니다.')
  }
}

const deleteComment = async (commentId: number) => {
  const password = prompt('비밀번호를 입력하세요:')
  if (!password) return

  try {
    await api.deleteComment(commentId, password)
    await refresh()
    alert('댓글이 삭제되었습니다.')
  } catch (err: any) {
    alert(err?.data?.error || '댓글 삭제 중 오류가 발생했습니다.')
  }
}

const editPost = async () => {
  if (!editPassword.value) {
    alert('비밀번호를 입력해주세요.')
    return
  }

  // 수정 페이지로 이동 (비밀번호를 쿼리로 전달)
  router.push(`/edit/${postId}?password=${editPassword.value}`)
}

const deletePost = async () => {
  if (!deletePassword.value) {
    alert('비밀번호를 입력해주세요.')
    return
  }

  try {
    await api.deletePost(postId, deletePassword.value)
    alert('게시글이 삭제되었습니다.')
    const boardType = post.value?.board_name === '자유게시판' ? 'free' : 'news'
    router.push(`/board/${boardType}`)
  } catch (err: any) {
    alert(err?.data?.error || '게시글 삭제 중 오류가 발생했습니다.')
  }
}
</script>
