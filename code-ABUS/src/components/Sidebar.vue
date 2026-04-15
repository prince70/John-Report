<template>
  <div class="sidebar">
    <div class="header">
      <div class="brand">
        <img class="logo" :src="logoImage" />
        <div class="title">数据系统</div>
      </div>
    </div>

    <nav class="nav-menu">
      <div v-for="(menu, index) in menus" :key="index" :class="['nav-item', { active: activeMenu === menu.path }]">
        <div class="nav-main" @click="handleMenuClick(menu)">
          <img :src="menu.icon" class="nav-icon" />
          <span>{{ menu.name }}</span>
          <img v-if="menu.children" :src="menu.isExpanded ? arrowUp : arrowDown" class="arrow-icon"
            @click.stop="toggleSubMenu(menu)" />
        </div>

        <transition name="slide">
          <div v-if="menu.children && menu.isExpanded" class="sub-menu">
            <div v-for="(sub, subIndex) in menu.children" :key="subIndex" 
              v-if="!sub.hidden"
              class="sub-item"
              :class="{ active: activeMenu === sub.path }" @click.stop="changeMenu(sub.path)">
              <img :src="sub.icon" class="sub-icon" />
              <span>{{ sub.name }}</span>
            </div>
          </div>
        </transition>
      </div>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'Sidebar',
  data() {
    // 检查用户角色
    const userInfoStr = localStorage.getItem('userInfo');
    let userRole = 'normal';
    if (userInfoStr) {
      try {
        const userInfo = JSON.parse(userInfoStr);
        userRole = userInfo.role || 'normal';
      } catch (e) {
        userRole = 'normal';
      }
    }
    
    // 如果是 file_viewer 角色（Eva），只显示文件查询菜单
    const menusForFileViewer = [
      {
        name: '文件查询',
        icon: require('../pages/photo/inventory.png'),
        path: '/file'
      },
    ];
    
    // 如果是 10070 用户，只显示迟到缺勤统计菜单
    const menusFor10070 = [
      {
        name: '迟到缺勤统计',
        icon: require('../pages/photo/inventory.png'),
        path: '/attendanceStatistics'
      },
    ];
    
    return {
      activeMenu: this.$route.path,
      arrowDown: require('../pages/photo/down.png'),
      arrowUp: require('../pages/photo/up.png'),
      logoImage: require('../pages/photo/logo.png'),
            menus: userRole === 'file_viewer' ? menusForFileViewer :
              userRole === '10070' ? menusFor10070 : [
        {
          path: '/home',
          name: '首页',
          icon: require('../pages/photo/home.png')
        },
        {
          path: '/people',
          name: '员工信息表',
          icon: require('../pages/photo/team.png')
        },
        {
          name: 'All Process 全流程',
          path: '',
          icon: require('../pages/photo/tech.png'),
          isExpanded: false,
          children: [
            {   //原理的指向是   name: 'G3工序-後端未完成',  2025-10-13改动  全流程工序
              name: '报工查询',
              icon: require('../pages/photo/tech.png'),
              path: '/allProcessWorkReport',
              hidden: !this.isUserAllowed('John') && !this.isUserAllowed('admin')
            }
          ]
        },
        {
          name: '项目申请',
          icon: require('../pages/photo/team.png'),
          path: '',
          isExpanded: false,
          children: [
            {
              name: 'Transparent Management透明化管理申请',
              icon: require('../pages/photo/team.png'),
              path: '/transparent'
            },
            {
              name: 'APS Requirements 项目申请',
              icon: require('../pages/photo/team.png'),
              path: '/apsRequirements'
            }
          ]
        },
        ...(this.isUserAllowed('John') || this.isUserAllowed('admin') ? [{
          name: 'John项目',
          icon: require('../pages/photo/Jhon.png'),
          isExpanded: false,
          children: [
            {
              name: '项目表',
              icon: require('../pages/photo/Jhon.png'),
              path: '/personal'
            },
            {
              name: '生产预警数据(装嵌提前一周完成数据)',
              icon: require('../pages/photo/warning.png'),
              path: '/AssemblyEarly'
            },
            {
              name: '装嵌工单预警列表',
              icon: require('../pages/photo/inventory.png'),
              path: '/AssemblyEarlyList'
            },
            {
              name: '成本计算应用',
              icon: require('../pages/photo/data.png'),
              path: '/CostCalculation'
            }
          ]
        },
        {
          path: '',
          name: '报表页面',
          icon: require('../pages/photo/data.png'),
          isExpanded: false,
          children: [
            {
              name: '开料、锁体A全工序报工查询',
              icon: require('../pages/photo/data.png'),
              path: '/fullProcessQuery',
            },
            {
              name: '开料、锁体A首尾工序报工查询',
              icon: require('../pages/photo/data.png'),
              path: '/report'
            },
            {
              name: '全流程工序查询',
              icon: require('../pages/photo/data.png'),
              path: '/reportTemp'
            },
            {
                name: 'CISA库存表 ',
                icon: require('../pages/photo/data.png'),
                path: '/cisaInventory'
            },
            {
                name: '装嵌未来8周需求明细',
                icon: require('../pages/photo/data.png'),
              path: '/assemblyFuture8Weeks'
            }
          ]
        }
      ] : [
        {
          path: '',
          name: '报表页面',
          icon: require('../pages/photo/data.png'),
          isExpanded: false,
          children: [
            {
              name: '开料、锁体A全工序报工查询',
              icon: require('../pages/photo/data.png'),
              path: '/fullProcessQuery'
            },
            {
              name: '开料、锁体A首尾工序报工查询',
              icon: require('../pages/photo/data.png'),
              path: '/report'
            },
            {
              name: '全流程工序查询',
              icon: require('../pages/photo/data.png'),
              path: '/reportTemp'
            },
            {
              name: 'CISA库存表 ',
              icon: require('../pages/photo/data.png'),
              path: '/cisaInventory'
            },
            {
              name: '装嵌未来8周需求明细',
              icon: require('../pages/photo/data.png'),
              path: '/assemblyFuture8Weeks'
            }
          ]
        }
      ])]
    }
  },
  created() {
    this.updateMenuExpanded(this.$route.path);
    this.$emit('menus-updated', this.menus);

    if (!this.$store) {
      console.error('Vuex store is not available');
    } else if (!this.$store.state) {
      console.error('Vuex store state is not available');
    } else if (!this.$store.state.user) {
      console.error('User information is not available in Vuex store');
    } else {
      console.log('Current user:', this.$store.state.user);
      console.log('Username:', this.$store.state.user.username);
    }

  },
  watch: {
    $route(newVal) {
      this.activeMenu = newVal.path;
      this.updateMenuExpanded(newVal.path);
      this.$emit('menus-updated', this.menus);
    }
  },
  methods: {
    updateMenuExpanded(currentPath) {
      this.menus.forEach(menu => {
        if (menu.children) {
          menu.isExpanded = menu.children.some(child =>
            child.path === currentPath
          );
        }
      });
    },
    handleMenuClick(menu) {
      if (!menu.children) {
        this.$router.push(menu.path)
        this.activeMenu = menu.path
        this.changeMenu(menu.path);
      } else {
        this.toggleSubMenu(menu)
      }
    },
    toggleSubMenu(menu) {
      this.menus.forEach(m => {
        if (m !== menu && m.children) {
          m.isExpanded = false;
        }
      });
      menu.isExpanded = !menu.isExpanded;
    },
    changeMenu(path) {
      this.$router.push(path)
      this.activeMenu = path
    },
    isUserAllowed(username) {
      if (!this.$store || !this.$store.state || !this.$store.state.user) {
        return false;
      }
      const currentUser = this.$store.state.user.username;
      return currentUser && currentUser.toLowerCase() === username.toLowerCase();
    }
  }
}
</script>

<style scoped>
.sidebar {
  width: 300px;
  /* background: #002060; */
  background:#001e38;
  color: white;
  overflow-y: auto;
}

.header {
  padding: 18px;
  border-bottom: 1px solid #2e4b68;
}

.brand {
  display: flex;
  align-items: center;
}

.logo {
  width: 100px;
  height: 32px;
  margin-right: 12px;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.nav-menu {
  padding: 15px;
}

.nav-item {
  margin-bottom: 8px;
  border-radius: 4px;
  overflow: hidden;
}

.nav-main {
  display: flex;
  align-items: center;
  padding: 12px;
  cursor: pointer;
  transition: background 0.3s;
}

.nav-main:hover {
  background: #0e7ce4;
}

.nav-icon {
  width: 20px;
  height: 20px;
  margin-right: 12px;
}

.arrow-icon {
  width: 16px;
  height: 16px;
  margin-left: auto;
}

.sub-menu {
  background: #102f4e;
  padding: 8px 0;
}

.sub-item {
  display: flex;
  align-items: center;
  padding: 10px 20px;
  cursor: pointer;
  transition: background 0.3s;
}

.sub-item span {
  font-size: 14px;
}

.sub-item:hover {
  background: #3b4f63;
}

.sub-icon {
  width: 12px;
  height: 12px;
  margin-right: 2px;
}

/* 过渡动画 */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
  max-height: 200px;
}

.slide-enter,
.slide-leave-to {
  opacity: 0;
  max-height: 0;
}

.nav-item.active>.nav-main {
  background: #0e7ce4;
}

.sub-item.active {
  background: #3b4f63;
}

.sub-item.active span {
  color: #ffffff;
}
</style>