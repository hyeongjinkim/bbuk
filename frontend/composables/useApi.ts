export const useApi = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  const api = $fetch.create({
    baseURL: `${apiBase}/api`,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  return {
    // 게시판
    async getBoards() {
      return await api('/boards/')
    },

    // 게시글 목록
    async getPosts(boardType?: string, page = 1, sort = 'recent') {
      const params = new URLSearchParams()
      if (boardType) params.append('board_type', boardType)
      params.append('page', page.toString())
      params.append('sort', sort)
      
      return await api(`/posts/?${params.toString()}`)
    },

    // 게시글 상세
    async getPost(id: number) {
      return await api(`/posts/${id}/`)
    },

    // 게시글 작성
    async createPost(data: any) {
      return await api('/posts/', {
        method: 'POST',
        body: data,
      })
    },

    // 게시글 수정
    async updatePost(id: number, data: any) {
      return await api(`/posts/${id}/`, {
        method: 'PUT',
        body: data,
      })
    },

    // 게시글 삭제
    async deletePost(id: number, password: string) {
      return await api(`/posts/${id}/`, {
        method: 'DELETE',
        body: { password },
      })
    },

    // 추천/비추천
    async votePost(id: number, voteType: number) {
      return await api(`/posts/${id}/vote/`, {
        method: 'POST',
        body: { vote_type: voteType },
      })
    },

    // 댓글 작성
    async createComment(postId: number, data: any) {
      return await api(`/posts/${postId}/comment/`, {
        method: 'POST',
        body: data,
      })
    },

    // 댓글 삭제
    async deleteComment(id: number, password: string) {
      return await api(`/comments/${id}/`, {
        method: 'DELETE',
        body: { password },
      })
    },

    // 관리자 뉴스 작성
    async createNews(data: any, adminToken: string) {
      return await api('/admin/news/', {
        method: 'POST',
        body: data,
        headers: {
          'X-Admin-Token': adminToken,
        },
      })
    },
  }
}
