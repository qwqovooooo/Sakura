import request from '../request/index'

// 管理员登录
export function adminLogin(data) {
  return request({
    url: '/auth/login',
    method: 'post',
    data
  })
}

// 获取用户列表
export function getUserList(params) {
  return request({
    url: '/admin/users',
    method: 'get',
    params
  })
}

// 更新用户权限
export function updateUserPermission(userId, data) {
  return request({
    url: `/admin/users/${userId}`,
    method: 'put',
    data
  })
}

// 删除用户
export function deleteUser(userId) {
  return request({
    url: `/admin/users/${userId}`,
    method: 'delete'
  })
}

// 获取电影列表
export function getMovieList(params) {
  return request({
    url: '/admin/movies',
    method: 'get',
    params
  })
}

// 创建电影
export function createMovie(data) {
  return request({
    url: '/admin/movies',
    method: 'post',
    data
  })
}

// 更新电影
export function updateMovie(vodId, data) {
  return request({
    url: `/admin/movies/${vodId}`,
    method: 'put',
    data
  })
}

// 删除电影
export function deleteMovie(vodId) {
  return request({
    url: `/admin/movies/${vodId}`,
    method: 'delete'
  })
}

// 获取评论列表
export function getCommentList(params) {
  return request({
    url: '/admin/comments',
    method: 'get',
    params
  })
}

// 删除评论
export function deleteComment(commentId) {
  return request({
    url: `/admin/comments/${commentId}`,
    method: 'delete'
  })
}

// 批量删除评论
export function batchDeleteComments(commentIds) {
  return request({
    url: '/admin/comments/batch-delete',
    method: 'post',
    data: commentIds
  })
}
