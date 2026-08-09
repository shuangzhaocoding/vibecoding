import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { resolveHomeRoute } from '@/utils/access'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/Register.vue'),
    meta: { public: true },
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: () => import('@/views/ForgotPassword.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('@/layout/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'plaza',
        component: () => import('@/views/project/Plaza.vue'),
        meta: { public: true },
      },
      {
        path: 'ranking',
        name: 'ranking',
        component: () => import('@/views/project/Ranking.vue'),
        meta: { public: true },
      },
      {
        path: 'projects/:id',
        name: 'project-detail',
        component: () => import('@/views/project/ProjectDetail.vue'),
        meta: { public: true },
      },
      {
        path: 'authors/:id',
        name: 'author',
        component: () => import('@/views/project/Author.vue'),
        meta: { public: true },
      },
      {
        path: 'center',
        component: () => import('@/layout/CenterLayout.vue'),
        meta: { auth: true },
        redirect: { name: 'mine' },
        children: [
          {
            path: 'profile',
            name: 'profile',
            component: () => import('@/views/center/Profile.vue'),
            meta: { auth: true },
          },
          {
            path: 'mine',
            name: 'mine',
            component: () => import('@/views/project/Mine.vue'),
            meta: { auth: true },
          },
          {
            path: 'dashboard',
            name: 'dashboard',
            component: () => import('@/views/center/Dashboard.vue'),
            meta: { auth: true, perm: 'project:create' },
          },
          {
            path: 'likes',
            name: 'likes',
            component: () => import('@/views/project/Likes.vue'),
            meta: { auth: true },
          },
          {
            path: 'favorites',
            name: 'favorites',
            component: () => import('@/views/project/Favorites.vue'),
            meta: { auth: true },
          },
          {
            path: 'moderation',
            name: 'moderation',
            component: () => import('@/views/project/Moderation.vue'),
            meta: { auth: true, perm: 'project:manage' },
          },
          {
            path: 'publish',
            name: 'project-create',
            component: () => import('@/views/project/ProjectForm.vue'),
            meta: { auth: true, perm: 'project:create' },
          },
          {
            path: 'projects/:id/edit',
            name: 'project-edit',
            component: () => import('@/views/project/ProjectForm.vue'),
            meta: { auth: true, perm: 'project:update' },
          },
          {
            path: 'users',
            name: 'users',
            component: () => import('@/views/system/UserManage.vue'),
            meta: { auth: true, perm: 'system:user:view' },
          },
          {
            path: 'roles',
            name: 'roles',
            component: () => import('@/views/system/RoleManage.vue'),
            meta: { auth: true, perm: 'system:role:view' },
          },
          {
            path: 'permissions',
            name: 'permissions',
            component: () => import('@/views/system/PermissionManage.vue'),
            meta: { auth: true, perm: 'system:perm:view' },
          },
        ],
      },
      {
        path: '403',
        name: 'forbidden',
        component: () => import('@/views/Error403.vue'),
        meta: { public: true },
      },
      {
        path: '404',
        name: 'not-found',
        component: () => import('@/views/Error404.vue'),
        meta: { public: true },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'catch-all',
    redirect: { name: 'not-found' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const user = useUserStore()
  if (user.token && !user.isLogin) {
    user.clearSession()
    if (to.meta.public) return true
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.public) {
    if (user.isLogin && (to.name === 'login' || to.name === 'register')) {
      return resolveHomeRoute(user)
    }
    return true
  }
  const needAuth = to.matched.some((r) => r.meta.auth)
  if (needAuth && !user.isLogin) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  const permRoute = [...to.matched].reverse().find((r) => r.meta.perm)
  if (permRoute?.meta.perm && !user.hasPerm(permRoute.meta.perm)) {
    if (to.name === 'forbidden') return true
    return { name: 'forbidden' }
  }
  return true
})

export default router
