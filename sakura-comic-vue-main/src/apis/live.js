/**
 * 直播相关API
 */
import httpRequest from '../request/index'

/**
 * 创建直播间
 */
export const createLiveRoom = (data) => {
  return httpRequest({
    url: '/live/create',
    method: 'post',
    data
  })
}

/**
 * 获取我的直播间
 */
export const getMyLiveRoom = () => {
  return httpRequest({
    url: '/live/my-room',
    method: 'get'
  })
}

/**
 * 获取推流地址
 */
export const getStreamUrl = () => {
  return httpRequest({
    url: '/live/stream-url',
    method: 'get'
  })
}

/**
 * 开始直播
 */
export const startLive = () => {
  return httpRequest({
    url: '/live/start',
    method: 'post'
  })
}

/**
 * 结束直播
 */
export const stopLive = () => {
  return httpRequest({
    url: '/live/stop',
    method: 'post'
  })
}

/**
 * 获取直播间列表
 */
export const getLiveRoomList = (params) => {
  return httpRequest({
    url: '/live/list',
    method: 'get',
    params
  })
}

/**
 * 获取直播间详情
 */
export const getLiveRoomDetail = (roomId) => {
  return httpRequest({
    url: `/live/${roomId}`,
    method: 'get'
  })
}

/**
 * 更新直播间配置
 */
export const updateLiveRoom = (data) => {
  return httpRequest({
    url: '/live/update',
    method: 'put',
    data
  })
}
