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
import LockBodyProcessStats from '../pages/John/LockBodyProcessStats.vue';
import LackMaterial from '../pages/APS_Stat/lackMaterial.vue';
import OutsourceLackMaterial from '../pages/APS_Stat/outsourceLackMaterial.vue';
import ProcessPriceStats from '../pages/John/processPriceStats.vue';
import FullProcessInventoryCNC from '../pages/APS_Stat/fullProcessInventoryCNC.vue';
import FullProcessInventoryDZS from '../pages/APS_Stat/fullProcessInventoryDZS.vue';
import FullProcessInventoryKEY from '../pages/APS_Stat/fullProcessInventoryKEY.vue';
import FullProcessInventorySTA from '../pages/APS_Stat/fullProcessInventorySTA.vue';
import FullProcessInventorySTB from '../pages/APS_Stat/fullProcessInventorySTB.vue';
import FullProcessInventorySTC from '../pages/APS_Stat/fullProcessInventorySTC.vue';
import FullProcessInventoryKL from '../pages/APS_Stat/fullProcessInventoryKL.vue';
import FullProcessInventorySL from '../pages/APS_Stat/fullProcessInventorySL.vue';
import FullProcessInventorySTD from '../pages/APS_Stat/fullProcessInventorySTD.vue';
import FullProcessInventorySX from '../pages/APS_Stat/fullProcessInventorySX.vue';
import FullProcessInventoryZQ_DZSQ from '../pages/APS_Stat/fullProcessInventoryZQ_DZSQ.vue';
import FullProcessInventoryZQ_GNSQ from '../pages/APS_Stat/fullProcessInventoryZQ_GNSQ.vue';
import FullProcessInventoryZQ_LMSQ from '../pages/APS_Stat/fullProcessInventoryZQ_LMSQ.vue';
import FullProcessInventoryDM_ZPQ from '../pages/APS_Stat/fullProcessInventoryDM_ZPQ.vue';
import OverStockQuantity from '../pages/APS_Stat/overStockQuantity.vue';
import OfflineProcess from '../pages/APS_Stat/offlineProcess.vue';
import LockCWorkProgress from '../pages/APS_Stat/lockCWorkProgress.vue';
import LockBodyOverage from '../pages/APS_Stat/lockBodyOverage.vue';
import WorkshopReportDetailCNC from '../pages/APS_Stat/workshopReportDetailCNC.vue';
import WorkshopReportDetailPack from '../pages/APS_Stat/workshopReportDetailPack.vue';
import WorkshopReportDetailLockB from '../pages/APS_Stat/workshopReportDetailLockB.vue';
import WorkshopReportDetailLockC from '../pages/APS_Stat/workshopReportDetailLockC.vue';
import WorkshopReportDetailLockD from '../pages/APS_Stat/workshopReportDetailLockD.vue';
import WorkshopReportDetailLockA from '../pages/APS_Stat/workshopReportDetailLockA.vue';
import WorkshopReportDetailSuoliang from '../pages/APS_Stat/workshopReportDetailSuoliang.vue';
import WorkshopReportDetailMaterial from '../pages/APS_Stat/workshopReportDetailMaterial.vue';
import WorkshopReportDetailZhuangqian from '../pages/APS_Stat/workshopReportDetailZhuangqian.vue';
import WorkshopReportDetailDamo from '../pages/APS_Stat/workshopReportDetailDamo.vue';
import WorkshopReportDetailDamoDM from '../pages/APS_Stat/workshopReportDetailDamoDM.vue';

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
  {
    path: '/lockBodyProcessStats',
    name: 'LockBodyProcessStats',
    component: LockBodyProcessStats,
    meta: { requiresAuth: true }
  },
  {
    path: '/lackMaterial',
    name: 'LackMaterial',
    component: LackMaterial,
    meta: { requiresAuth: true }
  },
  {
    path: '/outsourceLackMaterial',
    name: 'OutsourceLackMaterial',
    component: OutsourceLackMaterial,
    meta: { requiresAuth: true }
  },
  {
    path: '/processPriceStats',
    name: 'ProcessPriceStats',
    component: ProcessPriceStats,
    meta: { requiresAuth: true }
  },
  {
    path: '/fullProcessInventory/CNC',
    name: 'FullProcessInventoryCNC',
    component: FullProcessInventoryCNC,
    meta: { requiresAuth: true }
  },
  {
    path: '/fullProcessInventory/DZS',
    name: 'FullProcessInventoryDZS',
    component: FullProcessInventoryDZS,
    meta: { requiresAuth: true }
  },
  {
    path: '/fullProcessInventory/KEY',
    name: 'FullProcessInventoryKEY',
    component: FullProcessInventoryKEY,
    meta: { requiresAuth: true }
  },
  {
    path: '/fullProcessInventory/STA',
    name: 'FullProcessInventorySTA',
    component: FullProcessInventorySTA,
    meta: { requiresAuth: true }
  },
  {
    path: '/fullProcessInventory/STB',
    name: 'FullProcessInventorySTB',
    component: FullProcessInventorySTB,
    meta: { requiresAuth: true }
  },
  {
    path: '/fullProcessInventory/STC',
    name: 'FullProcessInventorySTC',
    component: FullProcessInventorySTC,
    meta: { requiresAuth: true }
  },
  {
    path: '/fullProcessInventory/KL',
    name: 'FullProcessInventoryKL',
    component: FullProcessInventoryKL,
    meta: { requiresAuth: true }
  },
  {
    path: '/fullProcessInventory/SL',
    name: 'FullProcessInventorySL',
    component: FullProcessInventorySL,
    meta: { requiresAuth: true }
  },
  {
    path: '/fullProcessInventory/STD',
    name: 'FullProcessInventorySTD',
    component: FullProcessInventorySTD,
    meta: { requiresAuth: true }
  },
  {
    path: '/fullProcessInventory/SX',
    name: 'FullProcessInventorySX',
    component: FullProcessInventorySX,
    meta: { requiresAuth: true }
  },
  {
    path: '/fullProcessInventory/ZQ_DZSQ',
    name: 'FullProcessInventoryZQ_DZSQ',
    component: FullProcessInventoryZQ_DZSQ,
    meta: { requiresAuth: true }
  },
  {
    path: '/fullProcessInventory/ZQ_GNSQ',
    name: 'FullProcessInventoryZQ_GNSQ',
    component: FullProcessInventoryZQ_GNSQ,
    meta: { requiresAuth: true }
  },
  {
    path: '/fullProcessInventory/ZQ_LMSQ',
    name: 'FullProcessInventoryZQ_LMSQ',
    component: FullProcessInventoryZQ_LMSQ,
    meta: { requiresAuth: true }
  },
  {
    path: '/fullProcessInventory/DM_ZPQ',
    name: 'FullProcessInventoryDM_ZPQ',
    component: FullProcessInventoryDM_ZPQ,
    meta: { requiresAuth: true }
  },
  {
    path: '/overStockQuantity',
    name: 'OverStockQuantity',
    component: OverStockQuantity,
    meta: { requiresAuth: true }
  },
  {
    path: '/offlineProcess',
    name: 'OfflineProcess',
    component: OfflineProcess,
    meta: { requiresAuth: true }
  },
  {
    path: '/lockCWorkProgress',
    name: 'LockCWorkProgress',
    component: LockCWorkProgress,
    meta: { requiresAuth: true }
  },
  {
    path: '/lockBodyOverage',
    name: 'LockBodyOverage',
    component: LockBodyOverage,
    meta: { requiresAuth: true }
  },
  {
    path: '/workshopReportDetail/CNC',
    name: 'WorkshopReportDetailCNC',
    component: WorkshopReportDetailCNC,
    meta: { requiresAuth: true }
  },
  {
    path: '/workshopReportDetail/Pack',
    name: 'WorkshopReportDetailPack',
    component: WorkshopReportDetailPack,
    meta: { requiresAuth: true }
  },
  {
    path: '/workshopReportDetail/LockB',
    name: 'WorkshopReportDetailLockB',
    component: WorkshopReportDetailLockB,
    meta: { requiresAuth: true }
  },
  {
    path: '/workshopReportDetail/LockC',
    name: 'WorkshopReportDetailLockC',
    component: WorkshopReportDetailLockC,
    meta: { requiresAuth: true }
  },
  {
    path: '/workshopReportDetail/LockD',
    name: 'WorkshopReportDetailLockD',
    component: WorkshopReportDetailLockD,
    meta: { requiresAuth: true }
  },
  {
    path: '/workshopReportDetail/LockA',
    name: 'WorkshopReportDetailLockA',
    component: WorkshopReportDetailLockA,
    meta: { requiresAuth: true }
  },
  {
    path: '/workshopReportDetail/Suoliang',
    name: 'WorkshopReportDetailSuoliang',
    component: WorkshopReportDetailSuoliang,
    meta: { requiresAuth: true }
  },
  {
    path: '/workshopReportDetail/Material',
    name: 'WorkshopReportDetailMaterial',
    component: WorkshopReportDetailMaterial,
    meta: { requiresAuth: true }
  },
  {
    path: '/workshopReportDetail/Zhuangqian',
    name: 'WorkshopReportDetailZhuangqian',
    component: WorkshopReportDetailZhuangqian,
    meta: { requiresAuth: true }
  },
  {
    path: '/workshopReportDetail/Damo',
    name: 'WorkshopReportDetailDamo',
    component: WorkshopReportDetailDamo,
    meta: { requiresAuth: true }
  },
  {
    path: '/workshopReportDetail/DamoDM',
    name: 'WorkshopReportDetailDamoDM',
    component: WorkshopReportDetailDamoDM,
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