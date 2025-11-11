<template>
  <div>
    <div v-if="loading" class="text-center py-8">
      로딩중...
    </div>

    <div v-else-if="!post" class="text-center py-8 text-red-600">
      게시글을 찾을 수 없습니다.
    </div>

    <div v-else>
      <NuxtLink :to="`/post/${postId}`" class="text-sm text-gray-600 mb-2 inline-block">
        ← 돌아가기
      </NuxtLink>

      <h1 class="text-2xl font-bold mb-4">글 수정</h1>

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

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">비밀번호 확인</label>
            <input 
              v-model="form.password"
              type="password"
              placeholder="비밀번호"
              class="input-field"
            />
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
              {{ submitting ? '수정 중...' : '수정하기' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const api = useApi()

const postId = parseInt(route.params.id as string)
const passwordFromQuery = route.query.password as string

const loading = ref(true)
const post = ref<any>(null)
const submitting = ref(false)

const form = reactive({
  title: '',
  content: '',
  password: passwordFromQuery || ''
})

onMounted(async () => {
  try {
    post.value = await api.getPost(postId)
    form.title = post.value.title
    form.content = post.value.content
    loading.value = false
  } catch (err) {
    loading.value = false
  }
})

const isValid = computed(() => {
  return form.title.trim() && form.content.trim() && form.password
})

const submit = async () => {
  if (!isValid.value) {
    alert('모든 항목을 입력해주세요.')
    return
  }

  submitting.value = true

  try {
    await api.updatePost(postId, form)
    alert('게시글이 수정되었습니다.')
    router.push(`/post/${postId}`)
  } catch (err: any) {
    const errorMsg = err?.data?.error || '게시글 수정 중 오류가 발생했습니다.'
    alert(errorMsg)
    submitting.value = false
  }
}
</script>
