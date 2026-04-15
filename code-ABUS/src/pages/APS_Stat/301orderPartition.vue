<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <!-- 搜索表单 -->
    <div class="search-form">
      <el-form :model="queryParams" label-width="120px" inline>
        <el-form-item label="开始时间">
          <el-date-picker
            v-model="queryParams.startTime"
            type="date"
            placeholder="选择开始日期"
            value-format="yyyy-MM-dd"/>
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="queryParams.endTime"
            type="date"
            placeholder="选择结束日期"
            value-format="yyyy-MM-dd"/>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="handleSearch">查询</el-button>
          <el-button icon="el-icon-refresh" @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 图表 -->
    <div v-if="dynamicData.length" class="chart-wrapper">
      <div ref="chartRef" class="chart"></div>
    </div>

    <!-- 数据表格 -->
    <div v-if="dynamicData.length" class="data-preview">
      <el-table
        :data="dynamicData"
        border
        stripe
        v-loading="loading"
        element-loading-text="数据加载中..."
        style="width: 100%"
        max-height="500">
        <el-table-column
          v-for="(col, index) in dynamicColumns"
          :key="index"
          :prop="col.prop"
          :label="col.label"
          :width="col.width"
          :fixed="index === 0 ? 'left' : false"
          align="center">
          <template slot-scope="{ row }">
            <span v-if="typeof row[col.prop] === 'number'">
              {{ row[col.prop].toLocaleString() }}
            </span>
            <span v-else>{{ row[col.prop] }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 空数据提示 -->
    <div v-else-if="!loading" class="no-data">
      暂无数据
    </div>
  </Layout>
</template>

<script>
import axios from 'axios'
import Layout from '@/components/Layout.vue'
import * as echarts from 'echarts'
import { eventBus } from '@/eventBus'

export default {
  name: 'OrderPartition',
  components: { Layout },
  data () {
    return {
      breadcrumbItems: ['订单统计', '订单分区统计表'],
      queryParams: {
        startTime: this.getDefaultStartDate(), // This will now be '2025-01-01'
        endTime: this.getDefaultEndDate(), // This will remain today's date
      },
      dynamicData: [],
      dynamicColumns: [],
      loading: false,
      chartInstance: null,
      sidebarMenus: []
    }
  },
  mounted () {
    this.fetchData()
    // 监听侧边栏菜单更新以生成面包屑
    eventBus.$on('sidebar-Menus-Updated', menus => {
      this.sidebarMenus = menus
      this.generateBreadcrumb(this.$route.path)
    })
    window.addEventListener('resize', this.resizeChart)
  },
  beforeDestroy () {
    window.removeEventListener('resize', this.resizeChart)
    if (this.chartInstance) {
      this.chartInstance.dispose()
    }
  },
  watch: {
    $route (newVal) {
      this.generateBreadcrumb(newVal.path)
    }
  },
  methods: {
    generateBreadcrumb (path) {
      try {
        const menus = this.sidebarMenus
        const findMenuName = (menus, targetPath) => {
          for (const menu of menus) {
            if (menu.path === targetPath) {
              return menu.name
            }
            if (menu.children) {
              for (const child of menu.children) {
                if (child.path === targetPath) {
                  return [menu.name, child.name]
                }
              }
            }
          }
          return path.split('/').pop()
        }
        const paths = path.split('/').filter(p => p)
        const menuNames = findMenuName(menus, '/' + paths.join('/'))
        this.breadcrumbItems = Array.isArray(menuNames) ? menuNames : [menuNames]
      } catch (error) {
        this.breadcrumbItems = ['']
      }
    },
    getDefaultStartDate () {
      // Default to January 1st of the current year
      const now = new Date()
      const d = new Date(now.getFullYear(), 0, 1)
      return this.formatDate(d)
    },
    getDefaultEndDate () {
      // Default to December 31st of the current year
      const now = new Date()
      const d = new Date(now.getFullYear(), 11, 31)
      return this.formatDate(d)
    },
    formatDate (date) {
      const y = date.getFullYear()
      const m = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${y}-${m}-${day}`
    },
    async fetchData () {
      this.loading = true
      try {
        const res = await axios.get('/api/orderPartition', {
          params: {
            start_date: this.queryParams.startTime,
            end_date: this.queryParams.endTime,
          }
        })
        if (res.data && res.data.status === 'success') {
          const { data, columns } = res.data
          // 后端可能将月份列作为数字，Element-UI 需要字符串 prop / label
          const transformed = data.map(row => {
            const newRow = {}
            Object.keys(row).forEach(key => {
              newRow[String(key)] = row[key]
            })
            return newRow
          })
          this.dynamicData = transformed
          // 同样将列名全部转为字符串
          const colStrings = columns.map(c => String(c))
          this.generateColumns(colStrings)
          this.$nextTick(() => {
            this.initChart()
            this.updateChart()
          })
        }
      } catch (err) {
        this.$message.error('数据获取失败: ' + err)
      } finally {
        this.loading = false
      }
    },
    generateColumns (columnsArr) {
      // Element-UI 要求 prop / label 均为字符串
      this.dynamicColumns = columnsArr.map(col => {
        const key = String(col)
        return {
          prop: key,
          label: key === 'index' ? '锁类分区' : key,
          width: key === '分类' ? 150 : key === 'index' ? 110 : 110
        }
      })
    },
    handleSearch () {
      if (!this.queryParams.startTime || !this.queryParams.endTime) {
        this.$message.warning('请选择开始和结束日期')
        return
      }
      this.fetchData()
    },
    resetForm () {
      this.queryParams = {
        // Resetting to the new default start date
        startTime: this.getDefaultStartDate(),
        endTime: this.getDefaultEndDate(),
      }
      this.dynamicData = []
      this.dynamicColumns = []
      if (this.chartInstance) {
        this.chartInstance.dispose()
        this.chartInstance = null
      }
    },
    initChart () {
      if (!this.chartInstance) {
        this.chartInstance = echarts.init(this.$refs.chartRef)
      }
    },
    updateChart () {
      if (!this.chartInstance || !this.dynamicData.length) return
      const nameField = this.dynamicColumns.find(c => c.prop === '分类') ? '分类' : 'index'
      const months = this.dynamicColumns
        .map(c => c.prop)
        .filter(k => k !== nameField && k !== '合计')
        .sort() // 保证月份顺序
      const legendData = this.dynamicData
        .filter(r => r[nameField] !== '合计')
        .map(r => String(r[nameField]))
      const series = this.dynamicData
        .filter(r => r[nameField] !== '合计')
        .map(r => ({
          name: String(r[nameField]),
          type: 'bar',
          stack: 'total',
          emphasis: { focus: 'series' },
          data: months.map(m => r[m] || 0)
        }))
      const option = {
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        legend: { data: legendData },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: months },
        yAxis: { type: 'value' },
        series
      }
      this.chartInstance.setOption(option)
    },
    resizeChart () {
      if (this.chartInstance) {
        this.chartInstance.resize()
      }
    }
  }
}
</script>

<style scoped>
.search-form {
  padding: 15px;
  background: #fff;
  border-radius: 4px;
  margin-bottom: 10px;
}
.chart-wrapper {
  background: #fff;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
}
.chart {
  width: 100%;
  height: 400px;
}
.data-preview {
  background: #fff;
  padding: 10px;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}
.no-data {
  padding: 200px 0;
  text-align: center;
  font-size: 24px;
  color: #606266;
}
</style>
