<template>
  <div>
    <NuxtLink :to="`/board/${boardType}`" class="text-sm text-gray-600 mb-2 inline-block">
      ← 돌아가기
    </NuxtLink>

    <h1 class="text-2xl font-bold mb-4">글쓰기</h1>

    <div class="bg-white border border-gray-300 rounded p-4">
      <div class="space-y-3">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">제목</label>
          <input 
            v-model="form.title"
            type="text"
            placeholder="제목을 입력하세요"
            class="input-field"
            maxlength="200"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">내용</label>
          <textarea 
            v-model="form.content"
            placeholder="내용을 입력하세요"
            class="input-field h-64 resize-none"
          ></textarea>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">닉네임</label>
            <input 
              v-model="form.author_name"
              type="text"
              placeholder="닉네임"
              class="input-field"
              maxlength="50"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">비밀번호</label>
            <input 
              v-model="form.password"
              type="password"
              placeholder="비밀번호 (4-20자)"
              class="input-field"
              minlength="4"
              maxlength="20"
            />
          </div>
        </div>

        <div class="text-xs text-gray-500">
          * 비밀번호는 게시글 수정/삭제 시 필요합니다.
        </div>

        <div class="flex gap-2 pt-2">
          <button 
            @click="router.back()"
            class="btn-secondary flex-1"
          >
            취소
          </button>
          <button 
            @click="submit"
            :disabled="!isValid || submitting"
            class="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ submitting ? '작성 중...' : '작성하기' }}
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

const boardType = route.params.type as string

const form = reactive({
  board: 0,
  title: '',
  content: '',
  author_name: userStore.savedAuthorName,
  password: ''
})

const submitting = ref(false)

// 게시판 ID 가져오기
const { data: boards } = await useAsyncData('boards', () => api.getBoards())

onMounted(() => {
  const board = boards.value?.find((b: any) => b.board_type === boardType)
  if (board) {
    form.board = board.id
  }
})

const isValid = computed(() => {
  return form.title.trim() && 
         form.content.trim() && 
         form.author_name.trim() && 
         form.password.length >= 4 &&
         form.password.length <= 20
})

const submit = async () => {
  if (!isValid.value) {
    alert('모든 항목을 올바르게 입력해주세요.')
    return
  }

  submitting.value = true

  try {
    const result = await api.createPost(form)
    userStore.saveAuthorName(form.author_name)
    alert('게시글이 작성되었습니다.')
    router.push(`/post/${result.id}`)
  } catch (err: any) {
    const errorMsg = err?.data?.error || '게시글 작성 중 오류가 발생했습니다.'
    alert(errorMsg)
    submitting.value = false
  }
}
</script>
