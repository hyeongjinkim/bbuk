<template>
  <div>
    <!-- 헤더 -->
    <div class="flex justify-between items-center mb-4">
      <div>
        <NuxtLink to="/" class="text-sm text-gray-600 mb-1 inline-block">
          ← 돌아가기
        </NuxtLink>
        <h1 class="text-2xl font-bold">
          {{ boardType === 'free' ? '자유게시판' : '뉴스' }}
        </h1>
      </div>
      <NuxtLink 
        v-if="boardType === 'free'"
        :to="`/write/${boardType}`" 
        class="btn-primary text-sm"
      >
        글쓰기
      </NuxtLink>
    </div>

    <!-- 정렬 -->
    <div class="flex gap-2 mb-3">
      <button 
        @click="changeSort('recent')"
        :class="[
          'px-3 py-1 text-sm rounded transition-colors',
          sort === 'recent' ? 'bg-primary text-white' : 'bg-gray-200 text-gray-700'
        ]"
      >
        최신순
      </button>
      <button 
        @click="changeSort('popular')"
        :class="[
          'px-3 py-1 text-sm rounded transition-colors',
          sort === 'popular' ? 'bg-primary text-white' : 'bg-gray-200 text-gray-700'
        ]"
      >
        추천순
      </button>
    </div>

    <!-- 게시글 목록 -->
    <div v-if="pending" class="text-center py-8">
      로딩중...
    </div>
    
    <div v-else-if="error" class="text-center py-8 text-red-600">
      오류가 발생했습니다.
    </div>
    
    <div v-else>
      <table class="board-table">
        <thead>
          <tr>
            <th class="w-12">번호</th>
            <th>제목</th>
            <th class="w-16">추천</th>
            <th class="w-16">조회</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="post in posts?.results" 
            :key="post.id"
            class="hover:bg-gray-50 cursor-pointer"
            @click="navigateTo(`/post/${post.id}`)"
          >
            <td class="text-center text-gray-600">{{ post.id }}</td>
            <td>
              <div class="font-medium truncate">{{ post.title }}</div>
              <div class="text-xs text-gray-500 mt-1">
                <span class="text-blue-600">{{ post.author_fingerprint }}</span>
                · {{ formatDate(post.created_at) }}
                <span v-if="post.comment_count > 0" class="text-red-600 ml-1">
                  [{{ post.comment_count }}]
                </span>
              </div>
            </td>
            <td class="text-center">
              <span :class="post.upvote_count > 0 ? 'text-red-600 font-medium' : ''">
                {{ post.upvote_count }}
              </span>
            </td>
            <td class="text-center text-gray-600">{{ post.view_count }}</td>
          </tr>
          <tr v-if="!posts?.results?.length">
            <td colspan="4" class="text-center py-8 text-gray-500">
              게시글이 없습니다.
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 페이지네이션 -->
      <div v-if="posts?.next || posts?.previous" class="flex justify-center gap-2 mt-4">
        <button 
          v-if="posts?.previous"
          @click="changePage(currentPage - 1)"
          class="btn-secondary text-sm"
        >
          이전
        </button>
        <span class="px-3 py-2 text-sm">{{ currentPage }}</span>
        <button 
          v-if="posts?.next"
          @click="changePage(currentPage + 1)"
          class="btn-secondary text-sm"
        >
          다음
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const api = useApi()

const boardType = route.params.type as string
const currentPage = ref(1)
const sort = ref('recent')

const { data: posts, pending, error, refresh } = await useAsyncData(
  `posts-${boardType}`,
  () => api.getPosts(boardType, currentPage.value, sort.value)
)

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const diffHours = Math.floor(diff / (1000 * 60 * 60))
  
  if (diffHours < 24) {
    return `${diffHours}시간 전`
  }
  
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${month}/${day}`
}

const changePage = (page: number) => {
  currentPage.value = page
  refresh()
}

const changeSort = (newSort: string) => {
  sort.value = newSort
  currentPage.value = 1
  refresh()
}
</script>
