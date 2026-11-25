<template>
  <div class="breadcrumb-wrapper">
    <el-breadcrumb class="breadcrumb" separator="/">
      <el-breadcrumb-item 
        v-for="(item, index) in breadcrumbItems" 
        :key="index"
        :class="{ 'last-item': index === breadcrumbItems.length - 1 }"
      >
        {{ item }}
      </el-breadcrumb-item>
    </el-breadcrumb>
    <div class="actions">
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Breadcrumb',
  props: {
    breadcrumbItems: {
      type: Array,
      default: () => []
    }
  }
}
</script>

<style scoped>
.breadcrumb-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
  padding: 12px 20px;
  background: #f5f5f5;
  border-radius: 4px;
}

.breadcrumb {
  margin-bottom: 5px;
  padding: 12px 0;
  background: transparent;
  border-radius: 4px;
}

.el-breadcrumb {
  font-size: 16px;
  line-height: 1;
}

.el-breadcrumb__item:last-child .el-breadcrumb__inner {
  color: #606266;
  font-weight: normal;
}

.el-breadcrumb__item:not(:last-child) .el-breadcrumb__inner {
  color: #909399;
}

.actions {
  flex-shrink: 0;
}
</style> 