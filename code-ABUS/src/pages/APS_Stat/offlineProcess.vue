<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="report-container">
      <div class="el-card is-always-shadow mb-4">
        <div class="el-card__body">
          <el-form @submit.native.prevent="searchData" label-width="100px">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="料品名称">
                  <el-select
                    v-model="filters.料品名称"
                    placeholder="选择或搜索料品名称"
                    filterable
                    clearable
                    @change="onNameChange"
                  >
                    <el-option v-for="o in nameOptions" :key="o" :label="o" :value="o" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="生产车间">
                  <el-select
                    v-model="filters.生产车间"
                    placeholder="选择车间"
                    filterable
                    clearable
                    @change="onWorkshopChange"
                  >
                    <el-option v-for="o in workshopOptions" :key="o" :label="o" :value="o" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="工序">
                  <el-select
                    v-model="filters.工序"
                    placeholder="选择工序"
                    filterable
                    clearable
                    @change="onProcessChange"
                  >
                    <el-option v-for="o in processOptions" :key="o" :label="o" :value="o" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <div class="form-actions">
              <el-button type="primary" :loading="loading" @click="searchData">查询</el-button>
              <el-button @click="resetFilters">重置</el-button>
              <el-button type="success" :loading="exporting" @click="exportExcel">
                {{ exporting ? '导出中...' : '导出Excel' }}
              </el-button>
            </div>
          </el-form>
        </div>
      </div>

      <div v-if="statsData.length" class="el-card is-always-shadow mb-4">
        <div class="el-card__body">
          <div class="stats-title">各车间统计</div>
          <el-table
            :data="paginatedStats"
            border
            stripe
            style="width: 100%"
            :header-cell-style="{ background: '#eef1f6', color: '#606266' }"
          >
            <el-table-column type="index" label="序号" width="60" align="center" :index="statsIndex" />
            <el-table-column prop="生产车间" label="生产车间" min-width="150" show-overflow-tooltip />
            <el-table-column prop="规格数" label="规格种类数" width="120" align="center">
              <template #default="scope">
                <el-tooltip placement="top" popper-class="stats-tooltip">
                  <template #content>
                    <div style="max-height:200px;overflow-y:auto;white-space:pre-wrap;">
                      {{ scope.row.规格列表.join('\n') }}
                    </div>
                  </template>
                  <span class="stats-count">{{ scope.row.规格数 }}</span>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column prop="工序数" label="工序种类数" width="120" align="center">
              <template #default="scope">
                <el-tooltip placement="top" popper-class="stats-tooltip">
                  <template #content>
                    <div style="max-height:200px;overflow-y:auto;white-space:pre-wrap;">
                      {{ scope.row.工序列表.join('\n') }}
                    </div>
                  </template>
                  <span class="stats-count">{{ scope.row.工序数 }}</span>
                </el-tooltip>
              </template>
            </el-table-column>
          </el-table>
          <div class="pagination-row" style="margin-top:12px;">
            <el-pagination
              background
              small
              layout="total, sizes, prev, pager, next, jumper"
              :total="statsData.length"
              :current-page="statsPage"
              :page-sizes="[5, 10, 20, 50]"
              :page-size="statsPageSize"
              @size-change="handleStatsSizeChange"
              @current-change="handleStatsPageChange"
            />
          </div>
        </div>
      </div>

      <div class="el-card is-always-shadow mb-4 summary-card">
        <div class="el-card__body summary-row">
          <span>总条数: <b>{{ total }}</b> | 车间数: <b>{{ statsData.length }}</b></span>
        </div>
      </div>

      <div
        class="el-card is-always-shadow table-card"
        v-loading="loading"
        element-loading-text="加载中..."
      >
        <div class="el-card__body">
          <el-table
            v-if="tableData.length"
            :data="tableData"
            border
            stripe
            max-height="620"
            style="width: 100%"
            :header-cell-style="{ background: '#eef1f6', color: '#606266' }"
          >
            <el-table-column type="index" label="序号" width="60" align="center" :index="indexMethod" />
            <el-table-column prop="物料类型" label="物料类型" min-width="120" show-overflow-tooltip />
            <el-table-column prop="料品编码" label="料品编码" min-width="150" show-overflow-tooltip />
            <el-table-column prop="料品名称" label="料品名称" min-width="150" show-overflow-tooltip />
            <el-table-column prop="料品规格" label="料品规格" min-width="180" show-overflow-tooltip />
            <el-table-column prop="生产车间" label="生产车间" min-width="120" show-overflow-tooltip />
            <el-table-column prop="工序" label="工序" min-width="150" show-overflow-tooltip />
            <el-table-column prop="工序规格码" label="工序规格码" min-width="130" show-overflow-tooltip />
            <el-table-column prop="生效单价" label="生效单价" width="100" align="right">
              <template #default="scope">
                <span style="color:#e6a23c;font-weight:bold">{{ formatPrice(scope.row.生效单价) }}</span>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="暂无数据" />

          <div class="pagination-row">
            <el-pagination
              background
              layout="total, sizes, prev, pager, next, jumper"
              :total="total"
              :current-page="currentPage"
              :page-sizes="[50, 100, 200, 500]"
              :page-size="pageSize"
              @current-change="handlePageChange"
              @size-change="handleSizeChange"
            />
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script>
import axios from 'axios'
import Layout from '@/components/Layout.vue'
import { eventBus } from '../../eventBus'

export default {
  name: 'OfflineProcess',
  components: { Layout },
  data() {
    return {
      breadcrumbItems: ['报表页面', '排产所有工序对应单价'],
      filters: {
        料品名称: '',
        生产车间: '',
        工序: ''
      },
      nameOptions: [],
      workshopOptions: [],
      processOptions: [],
      tableData: [],
      allData: [],
      statsData: [],
      loading: false,
      exporting: false,
      currentPage: 1,
      pageSize: 100,
      total: 0,
      statsPage: 1,
      statsPageSize: 10,
      sidebarMenus: [],
    }
  },
  created() {
    eventBus.$on('sidebar-Menus-Updated', (menus) => {
      this.sidebarMenus = menus
      this.generateBreadcrumb(this.$route.path)
    })
    this.loadAllOptions()
    this.searchData()
  },
  computed: {
    paginatedStats() {
      const start = (this.statsPage - 1) * this.statsPageSize
      return this.statsData.slice(start, start + this.statsPageSize)
    },
    statsIndex() {
      return (this.statsPage - 1) * this.statsPageSize + 1
    }
  },
  watch: {
    $route(newVal) {
      this.generateBreadcrumb(newVal.path)
    }
  },
  methods: {
    generateBreadcrumb(path) {
      try {
        const menus = this.sidebarMenus
        const findMenuName = (menus, targetPath) => {
          for (const menu of menus) {
            if (menu.path === targetPath) return menu.name
            if (menu.children) {
              for (const child of menu.children) {
                if (child.path === targetPath) return [menu.name, child.name]
              }
            }
          }
          return path.split('/').pop()
        }
        const paths = path.split('/').filter(p => p)
        const menuNames = findMenuName(menus, '/' + paths.join('/'))
        this.breadcrumbItems = Array.isArray(menuNames) ? menuNames : ['报表页面', '排产所有工序对应单价']
      } catch {
        this.breadcrumbItems = ['报表页面', '排产所有工序对应单价']
      }
    },
    indexMethod(index) {
      return (this.currentPage - 1) * this.pageSize + index + 1
    },
    formatPrice(val) {
      if (val === null || val === undefined || val === 0) return '-'
      return Number(val).toFixed(4)
    },
    async loadAllOptions() {
      try {
        const res = await axios.get('/api/offlineProcess/cascade-options')
        if (res.data?.status === 'success') {
          const d = res.data.data || {}
          this.nameOptions = d['料品名称'] || []
          this.workshopOptions = d['生产车间'] || []
          this.processOptions = d['工序'] || []
        }
      } catch (e) {
        console.error('loadAllOptions error:', e)
      }
    },
    async loadCascadeOptions() {
      const params = {}
      if (this.filters['料品名称']) params['料品名称'] = this.filters['料品名称']
      if (this.filters['生产车间']) params['生产车间'] = this.filters['生产车间']
      if (this.filters['工序']) params['工序'] = this.filters['工序']
      try {
        const res = await axios.get('/api/offlineProcess/cascade-options', { params })
        if (res.data?.status === 'success') {
          const d = res.data.data || {}
          this.nameOptions = d['料品名称'] || []
          this.workshopOptions = d['生产车间'] || []
          this.processOptions = d['工序'] || []
        }
      } catch (e) {
        console.error('loadCascadeOptions error:', e)
      }
    },
    onNameChange() {
      this.loadCascadeOptions()
    },
    onWorkshopChange() {
      this.loadCascadeOptions()
    },
    onProcessChange() {
      this.loadCascadeOptions()
    },
    async searchData() {
      this.loading = true
      this.currentPage = 1
      this.statsPage = 1
      try {
        const params = {}
        if (this.filters.料品名称) params.料品名称 = this.filters.料品名称.trim()
        if (this.filters.生产车间) params.生产车间 = this.filters.生产车间.trim()
        if (this.filters.工序) params.工序 = this.filters.工序.trim()

        const response = await axios.get('/api/offlineProcess', { params })
        if (response.data?.status === 'success') {
          this.allData = response.data.data || []
          this.statsData = response.data.stats || []
          this.total = response.data.total_count || this.allData.length
          this.updateTableData()
        } else {
          this.$message.error('数据获取失败')
        }
      } catch (error) {
        console.error('获取数据失败:', error)
        this.$message.error('数据加载失败，请检查网络连接')
      } finally {
        this.loading = false
      }
    },
    updateTableData() {
      const start = (this.currentPage - 1) * this.pageSize
      this.tableData = this.allData.slice(start, start + this.pageSize)
    },
    handlePageChange(page) {
      this.currentPage = page
      this.updateTableData()
    },
    handleSizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
      this.updateTableData()
    },
    handleStatsPageChange(page) {
      this.statsPage = page
    },
    handleStatsSizeChange(size) {
      this.statsPageSize = size
      this.statsPage = 1
    },
    resetFilters() {
      this.filters = { 料品名称: '', 生产车间: '', 工序: '' }
      this.loadAllOptions()
      this.searchData()
    },
    async exportExcel() {
      this.exporting = true
      try {
        const params = {}
        if (this.filters.料品名称) params.料品名称 = this.filters.料品名称.trim()
        if (this.filters.生产车间) params.生产车间 = this.filters.生产车间.trim()
        if (this.filters.工序) params.工序 = this.filters.工序.trim()

        const response = await axios.get('/api/offlineProcess/export', {
          params,
          responseType: 'blob'
        })

        let filename = '排产所有工序对应单价.xlsx'
        const disposition = response.headers['content-disposition']
        if (disposition) {
          const match = disposition.match(/filename\*=UTF-8''(.+?)(?:;|$)/)
          if (match) {
            filename = decodeURIComponent(match[1])
          }
        }

        const blob = new Blob([response.data], {
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        this.$message.success('导出成功')
      } catch (error) {
        console.error('导出失败:', error)
        this.$message.error('导出失败，请检查网络连接')
      } finally {
        this.exporting = false
      }
    }
  }
}
</script>

<style scoped>
.report-container { padding: 0; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; padding-top: 10px; }
.summary-row { display: flex; justify-content: flex-end; color: #303133; }
.table-card { min-height: 100px; }
.pagination-row { display: flex; justify-content: flex-end; margin-top: 16px; }
.mb-4 { margin-bottom: 16px; }
.stats-title { font-size: 15px; font-weight: bold; color: #303133; margin-bottom: 12px; }
.stats-count { cursor: pointer; color: #409eff; font-weight: bold; }
</style>

<style>
.stats-tooltip { max-width: 400px; }
.stats-tooltip .el-tooltip__popper { max-width: 400px; }
</style>
