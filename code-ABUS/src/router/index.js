import Vue from 'vue';
import VueRouter from 'vue-router';
import Login from '../pages/_login/login.vue';
import Home from '../pages/_home/home.vue';
import personal from '../pages/John/personal.vue';
import transparent from '../pages/TransparentManagement/transparent.vue';
import AssemblyEarly from '../pages/John/AssemblyEarly.vue';
import AssemblyEarlyList from '../pages/John/AssemblyEarlyList.vue';
import AssemblyFuture8Weeks from '../pages/John/AssemblyFuture8Weeks.vue';
import CostCalculation from '../pages/John/CostCalculation.vue';
import APSRequirements from '../pages/TransparentManagement/apsRequirements.vue';
import AllProcessWorkReport from '../pages/All_Process/allProcessWorkReport.vue';
import Report from '../pages/John/gongxu_sw.vue';
import ReportSw from '../pages/John/gongxu.vue';
import ReportTemp from '../pages/John/quanliucheng.vue';
import CisaInventory from '../pages/John/cisaInventory.vue';
import People from '../pages/HR/people.vue';

Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    name: 'login',
    component: Login,
  },
  {
    path: '/home',
    name: 'home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path:'/personal',
    component:personal,
    meta:{ requiresAuth: true}
  },
  {
    path:'/transparent',
    component:transparent,
    meta:{ requiresAuth: true}
  },
  {
    path:'/AssemblyEarly',
    name: 'AssemblyEarly',
    component:AssemblyEarly,
    meta:{ requiresAuth: true}
  },
  {
    path:'/AssemblyEarlyList',
    name:'AssemblyEarlyList',
    component:AssemblyEarlyList,
    meta:{ requiresAuth: true}
  },
  {
    path:'/assemblyFuture8Weeks',
    name:'AssemblyFuture8Weeks',
    component: AssemblyFuture8Weeks,
    meta:{ requiresAuth: true}
  },
  {
    path:'/CostCalculation',
    name:'CostCalculation',
    component:CostCalculation,
    meta:{ requiresAuth: true}
  },
  {
    path:'/apsRequirements',
    name:'apsRequirements',
    component:APSRequirements,
    meta:{ requiresAuth: true}
  },
  {
    path:'/allProcessWorkReport',
    name: 'AllProcessWorkReport',
    component: AllProcessWorkReport,
    meta: { requiresAuth: true }
  },
  {
    path:'/report',
    name: 'Report',
    component: Report,
    meta: { requiresAuth: true }
  },
  {
    path:'/report_sw',
    name: 'ReportSw',
    component: ReportSw,
    meta: { requiresAuth: true }
  },
  {
    path:'/fullProcessQuery',
    name: 'FullProcessQuery',
    component: ReportSw,
    meta: { requiresAuth: true }
  },
  {
    path:'/reportTemp',
    name: 'ReportTemp',
    component: ReportTemp,
    meta: { requiresAuth: true }
  },
  {
    path:'/cisaInventory',
    name: 'CisaInventory',
    component: CisaInventory,
    meta: { requiresAuth: true }
  },
  {
    path: '/people',
    name: 'People',
    component: People,
    meta: { requiresAuth: true }
  },
  // 添加通配符路由，捕获所有未定义的路由
  {
    path: '*',
    redirect: '/'
  }
];

const router = new VueRouter({
  mode: 'history', // 修改为history模式
  base: process.env.BASE_URL,
  routes,
});
router.beforeEach((to, from, next) => {
  const isAuthenticated = Boolean(localStorage.getItem('token'));
  let userInfo = null;

  try {
    const userInfoStr = localStorage.getItem('userInfo');
    userInfo = userInfoStr ? JSON.parse(userInfoStr) : null;
  } catch (error) {
    userInfo = null;
    localStorage.removeItem('userInfo');
  }

  const userRole = userInfo ? userInfo.role : null;

  // 未登录用户只能访问登录页
  if (!isAuthenticated && to.path !== '/') {
    next('/');
    return;
  }

  // 已登录用户访问登录页时，直接回到默认首页
  if (isAuthenticated && to.path === '/') {
    if (userRole === 'file_viewer') {
      next('/file');
    } else {
      next('/home');
    }
    return;
  }
  
  // Eva 用户（file_viewer 角色）只能访问 /file 页面
  if (userRole === 'file_viewer') {
    if (to.path === '/file' || to.path === '/') {
      next();
    } else {
      // 尝试访问其他页面，强制跳转到 /file
      next('/file');
    }
    return;
  }
  // 用户10070 只能查看 迟到缺勤统计 /attendanceStatistics 页面
  if (userRole === '10070') {
    if (to.path === '/home' || to.path === '/') {
      next();
    } else {
      // 尝试访问其他页面，强制跳转到 /home
      next('/home');
    }
    return;
  }
  
  // allProcessWorkReport 页面只允许 John 和 admin 访问
  if (to.path === '/allProcessWorkReport') {
    const username = userInfo ? userInfo.username : null;
    if (!username || (username !== 'John' && username !== 'admin')) {
      next('/home');
      return;
    }
  }
  
  // 其他用户正常访问
  next(); 
});
const originalPush = VueRouter.prototype.push;
VueRouter.prototype.push = function push(location) {
  return originalPush.call(this, location).catch(err => err);
};

const originalReplace = VueRouter.prototype.replace;
VueRouter.prototype.replace = function replace(location) {
  return originalReplace.call(this, location).catch(err => err);
};

export default router;