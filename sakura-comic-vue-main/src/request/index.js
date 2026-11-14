import axios from 'axios'
import { localGet } from '../utils'

const token = localGet('token')

// 定义API基础URL，包含FastAPI和Flask服务
const API_BASE_URLS = [
  'http://127.0.0.1:8000', // FastAPI服务
  'http://127.0.0.1:5000'  // Flask服务
]

// 当前使用的基础URL索引
let currentBaseUrlIndex = 0

// 获取当前基础URL
const getCurrentBaseUrl = () => API_BASE_URLS[currentBaseUrlIndex]

// 切换基础URL
const switchBaseUrl = () => {
  currentBaseUrlIndex = (currentBaseUrlIndex + 1) % API_BASE_URLS.length
  console.log(`切换到${getCurrentBaseUrl()}`)
  // 更新axios实例的baseURL
  service.defaults.baseURL = getCurrentBaseUrl()
}

// 创建一个 axios 实例
const service = axios.create({
	baseURL: getCurrentBaseUrl(), // 动态获取当前基础URL
	timeout: 10000, // 请求超时时间毫秒（改为10秒）
	withCredentials: false, // 关闭跨域携带cookie以避免CORS问题
	headers: {
		// 设置后端需要的传参类型
		'Content-Type': 'application/json',
		'Authorization': token,
		'X-Requested-With': 'XMLHttpRequest',
	},
})

// 添加请求拦截器
service.interceptors.request.use(
	function (config) {
		// 在发送请求之前做些什么
		// 动态获取 token
		const token = localGet('token')
		const adminToken = localGet('admin_token')
		
		// 如果是管理后台接口，使用管理员 token
		if (config.url && config.url.includes('/admin')) {
			if (adminToken) {
				// 将 jwt 前缀改为 Bearer
				const token = adminToken.startsWith('jwt ') 
					? 'Bearer ' + adminToken.slice(4)
					: adminToken
				config.headers.Authorization = token
				console.log('Admin API request:', config.url, 'Token:', token.substring(0, 20) + '...')
			} else {
				console.warn('Admin API 请求但未找到 admin_token')
			}
		} else if (token) {
			// 处理普通用户 token 格式
			if (token.startsWith('jwt ')) {
				// 如果 token 以 'jwt ' 开头，将其改为 'Bearer '
				config.headers.Authorization = 'Bearer ' + token.slice(4)
			} else if (!token.startsWith('Bearer ')) {
				// 如果 token 没有 'Bearer ' 前缀，添加它
				config.headers.Authorization = 'Bearer ' + token
			} else {
				// token 已经是正确的格式
				config.headers.Authorization = token
			}
		}
		
		return config
	},
	function (error) {
		// 对请求错误做些什么
		console.log(error)
		return Promise.reject(error)
	}
)

// 添加响应拦截器
service.interceptors.response.use(
	function (response) {
		// 2xx 范围内的状态码都会触发该函数。
		// 对响应数据做点什么
		// dataAxios 是 axios 返回数据中的 data
		const dataAxios = response.data
		// 这个状态码是和后端约定的
		const code = dataAxios.reset
		return dataAxios
	},
	function (error) {
		// 超出 2xx 范围的状态码都会触发该函数。
		// 对响应错误做点什么
		console.log('请求失败:', error)
		
		// 检查是否是网络错误（如服务器未响应）
		if (!error.response) {
			// 尝试切换到另一个URL并重试
			switchBaseUrl()
			
			// 创建一个新的请求配置
			const config = error.config
			// 确保不会无限重试
			if (!config._retry) {
				config._retry = true
				// 更新配置中的URL
				config.baseURL = getCurrentBaseUrl()
				// 重新发送请求
				return axios(config)
			}
		}
		
		return Promise.reject(error)
	}
)

export default service
export { switchBaseUrl } // 导出切换URL函数供外部使用