<template>
  <div class="page-container">
    <!-- 侧边栏 -->
    <Sidebar ref="sidebar" @menus-updated="handleMenusUpdated"/>
    
    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 顶部导航栏 -->
      <TopBar />
      
      <!-- 内容区域 -->
      <div class="content">
        <!-- 面包屑导航 -->
        <Breadcrumb v-if="breadcrumbItems && breadcrumbItems.length" :breadcrumbItems="breadcrumbItems">
          <template #actions>
            <slot name="breadcrumb-actions"></slot>
          </template>
        </Breadcrumb>
        
        <!-- 插槽内容 -->
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script>
import Sidebar from './Sidebar.vue'
import TopBar from './TopBar.vue'
import Breadcrumb from './Breadcrumb.vue'
import { eventBus } from '../eventBus.js';

export default {
  name: 'Layout',
  components: {
    Sidebar,
    TopBar,
    Breadcrumb
  },
  data(){
    return {
      sidebarMenus: []
    }
  },
  methods: {
    handleMenusUpdated(menus) {
      this.sidebarMenus = menus;
      // console.log('获取到的侧边栏菜单11111:', this.sidebarMenus);
      eventBus.$emit('sidebar-Menus-Updated', this.sidebarMenus); // 触发事件
    }
  },
  props: {
    breadcrumbItems: {
      type: Array,
      default: () => []
    }
  }
}
</script>

<style scoped>
.page-container {
  height: 100vh;
  overflow: hidden;
  display: flex;
}

.main-content {
  flex: 1;
  background: #E8E8E8;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content {
  flex: 1;
  padding: 20px;
  background: #f5f5f5;
  overflow: auto;
}
</style> 