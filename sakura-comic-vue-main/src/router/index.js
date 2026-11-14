import { createRouter, createWebHashHistory, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/',
    component: () => import('../views/MovieHome.vue')
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/personSapce/:user_id',
    name: 'personSapce',
    component: () => import('../views/PersonalSapcePage.vue'),
    props: true,
    meta: {
      title: "用户空间",
      needLogin: true //需要登录
    }
  },
  {
    path: '/movtype/:movtype',
    component:  () => import('../views/MoviePage.vue'),
    props: true
  },
  {
    path: '/search',
    name: 'search',
    component: () => import('../views/MovieKeywordPage.vue')
  },
  {
    path: '/smart-search',
    name: 'smartSearch',
    component: () => import('../views/SmartSearch.vue'),
    meta: {
      errorHandler: true // 启用错误处理
    }
  },
  {
    path: '/movdetail/:vod_id',
    name: 'movdetail',
    component: () => import('../views/MovDetailPage.vue'),
    props: true
  },
  // 直播路由
  {
    path: '/live',
    name: 'live',
    component: () => import('../views/LivePage.vue')
  },
  {
    path: '/live/room/:roomId',
    name: 'liveRoom',
    component: () => import('../views/LiveRoomPage.vue'),
    props: true
  },
  {
    path: '/live/my-room',
    name: 'myLiveRoom',
    component: () => import('../views/MyLiveRoom.vue'),
    meta: {
      needLogin: true
    }
  },
  // 管理后台路由
  {
    path: '/admin/login',
    name: 'adminLogin',
    component: () => import('../views/admin/AdminLogin.vue')
  },
  {
    path: '/admin',
    component: () => import('../views/admin/AdminLayout.vue'),
    redirect: '/admin/dashboard',
    meta: {
      needAdminLogin: true
    },
    children: [
      {
        path: 'dashboard',
        name: 'adminDashboard',
        component: () => import('../views/admin/Dashboard.vue'),
        meta: { title: '控制台', needAdminLogin: true }
      },
      {
        path: 'users',
        name: 'adminUsers',
        component: () => import('../views/admin/Users.vue'),
        meta: { title: '用户管理', needAdminLogin: true }
      },
      {
        path: 'movies',
        name: 'adminMovies',
        component: () => import('../views/admin/Movies.vue'),
        meta: { title: '电影管理', needAdminLogin: true }
      },
      {
        path: 'comments',
        name: 'adminComments',
        component: () => import('../views/admin/Comments.vue'),
        meta: { title: '评论管理', needAdminLogin: true }
      }
    ]
  }
];


const router = createRouter({
  history: createWebHashHistory(),  // hash路由模式
  // history: createWebHistory(),  // history路由模式
  routes
});

// 全局路由守卫
router.beforeEach((to, from, next) => {
  let token = localStorage.getItem('token')
  let adminToken = localStorage.getItem('admin_token')
  
  // 管理后台登录验证
  if (to.meta.needAdminLogin) {
    if (adminToken) {
      next()
    } else {
      next({ path: '/admin/login' })
    }
  }
  // 普通用户登录验证
  else if (to.meta.needLogin) {
    if (token) {
      next()
    } else {
      next({path: '/login'})
    }
  } else { 
  	next()
  }
})

export default router;
