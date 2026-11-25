<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="report-container">
      <div class="el-card is-always-shadow mb-4">
        <div class="el-card__body">
          <el-form @submit.native.prevent="searchData" label-width="100px">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="订单批号">
                  <el-input v-model="filters.订单批号" placeholder="请输入订单批号" clearable @keyup.enter.native="searchData" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="料品规格">
                  <el-select v-model="filters.料品规格" placeholder="选择料品规格" filterable clearable>
                    <el-option v-for="o in specOptions" :key="o" :label="o" :value="o" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="9">
                <el-form-item label="确定交期">
                  <div class="date-range-inline">
                    <el-date-picker v-model="filters.开始交期" type="date" placeholder="开始日期" value-format="yyyy-MM-dd" clearable style="width: 45%" />
                    <span class="date-separator">至</span>
                    <el-date-picker v-model="filters.结束交期" type="date" placeholder="结束日期" value-format="yyyy-MM-dd" clearable style="width: 45%" />
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="9">
                <el-form-item label="报工时间">
                  <div class="date-range-inline">
                    <el-date-picker v-model="filters.开始报工" type="date" placeholder="开始日期" value-format="yyyy-MM-dd" clearable style="width: 45%" />
                    <span class="date-separator">至</span>
                    <el-date-picker v-model="filters.结束报工" type="date" placeholder="结束日期" value-format="yyyy-MM-dd" clearable style="width: 45%" />
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
            <div class="form-actions">
              <el-button type="primary" :loading="loading" @click="searchData">查询</el-button>
              <el-button @click="resetFilters">重置</el-button>
            </div>
          </el-form>
        </div>
      </div>

      <div class="el-card is-always-shadow mb-4 summary-card">
        <div class="el-card__body summary-row">
          <span>总条数: <b>{{ total }}</b></span>
        </div>
      </div>

      <div class="el-card is-always-shadow table-card" v-loading="loading" element-loading-text="加载中...">
        <div class="el-card__body">
          <el-table v-if="tableData.length" :data="tableData" border stripe max-height="620" style="width: 100%" :header-cell-style="{ background: '#eef1f6', color: '#606266' }">
            <el-table-column type="index" label="序号" width="60" align="center" :index="indexMethod" />
            <el-table-column v-for="col in displayColumns" :key="col" :prop="col" :label="col" min-width="140" show-overflow-tooltip />
          </el-table>
          <el-empty v-else description="暂无数据" />
          <div class="pagination-row">
            <el-pagination background layout="total, sizes, prev, pager, next, jumper" :total="total" :current-page="currentPage" :page-sizes="[50, 100, 200, 500]" :page-size="pageSize" @current-change="handlePageChange" @size-change="handleSizeChange" />
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
  name: 'OverStockQuantity',
  components: { Layout },
  data() {
    return {
      breadcrumbItems: ['报表页面', '超库存数量'],
      filters: { 订单批号: '', 料品规格: '', 开始交期: '', 结束交期: '', 开始报工: '', 结束报工: '' },
      specOptions: [],
      tableData: [], allData: [], loading: false,
      currentPage: 1, pageSize: 100, total: 0, sidebarMenus: [],
      displayColumns: []
    }
  },
  created() {
    eventBus.$on('sidebar-Menus-Updated', (menus) => { this.sidebarMenus = menus; this.generateBreadcrumb(this.$route.path) })
    this.loadOptions(); this.searchData()
  },
  watch: { $route(v) { this.generateBreadcrumb(v.path) } },
  methods: {
    generateBreadcrumb(path) {
      try {
        const find = (menus, p) => { for (const m of menus) { if (m.path === p) return m.name; if (m.children) for (const c of m.children) if (c.path === p) return [m.name, c.name] } return p.split('/').pop() }
        const r = find(this.sidebarMenus, '/' + path.split('/').filter(p => p).join('/'))
        this.breadcrumbItems = Array.isArray(r) ? r : [r]
      } catch { this.breadcrumbItems = ['报表页面', '超库存数量'] }
    },
    indexMethod(i) { return (this.currentPage - 1) * this.pageSize + i + 1 },
    async loadOptions() {
      try {
        const res = await axios.get('/api/overStockQuantity/options', { params: { field: '料品规格' } })
        if (res.data?.status === 'success') this.specOptions = (res.data.data || []).map(i => i.value)
      } catch {}
    },
    getFilterParams() {
      const params = {}
      if (this.filters.订单批号) params.订单批号 = this.filters.订单批号.trim()
      if (this.filters.料品规格) params.料品规格 = this.filters.料品规格
      if (this.filters.开始交期) params.开始交期 = this.filters.开始交期
      if (this.filters.结束交期) params.结束交期 = this.filters.结束交期
      if (this.filters.开始报工) params.开始报工 = this.filters.开始报工
      if (this.filters.结束报工) params.结束报工 = this.filters.结束报工
      return params
    },
    async searchData() {
      this.loading = true; this.currentPage = 1
      try {
        const params = this.getFilterParams()
        const res = await axios.get('/api/overStockQuantity', { params })
        if (res.data?.status === 'success') {
          this.allData = res.data.data || []
          this.total = res.data.total_count || this.allData.length
          if (this.allData.length > 0) this.displayColumns = Object.keys(this.allData[0]).filter(k => k !== 'id')
          this.updateTableData()
        } else { this.$message.error('数据获取失败') }
      } catch { this.$message.error('数据加载失败') } finally { this.loading = false }
    },
    updateTableData() { const s = (this.currentPage - 1) * this.pageSize; this.tableData = this.allData.slice(s, s + this.pageSize) },
    handlePageChange(p) { this.currentPage = p; this.updateTableData() },
    handleSizeChange(s) { this.pageSize = s; this.currentPage = 1; this.updateTableData() },
    resetFilters() {
      this.filters = { 订单批号: '', 料品规格: '', 开始交期: '', 结束交期: '', 开始报工: '', 结束报工: '' }
      this.searchData()
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
.date-range-inline { display: flex; align-items: center; }
.date-separator { margin: 0 6px; color: #909399; font-size: 14px; white-space: nowrap; }
</style>
