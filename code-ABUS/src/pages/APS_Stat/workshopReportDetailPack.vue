<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="report-container">
      <div class="el-card is-always-shadow mb-4">
        <div class="el-card__body">
          <el-form @submit.native.prevent="searchData" label-width="100px">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="开始时间">
                  <el-date-picker v-model="filters.start" type="date" placeholder="开始时间" value-format="yyyy-MM-dd" clearable style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="结束时间">
                  <el-date-picker v-model="filters.end" type="date" placeholder="结束时间" value-format="yyyy-MM-dd" clearable style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="序列号">
                  <el-input v-model="filters.序列号" placeholder="请输入序列号" clearable @keyup.enter.native="searchData" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="姓名">
                  <el-input v-model="filters.姓名" placeholder="请输入姓名" clearable @keyup.enter.native="searchData" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="生产线编号">
                  <el-input v-model="filters.生产线编号" placeholder="请输入生产线编号" clearable @keyup.enter.native="searchData" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="订单批号">
                  <el-input v-model="filters.订单批号" placeholder="请输入订单批号" clearable @keyup.enter.native="searchData" />
                </el-form-item>
              </el-col>
            </el-row>
            <div class="form-actions">
              <el-button type="primary" :loading="loading" @click="currentPage = 1; searchData()">查询</el-button>
              <el-button @click="resetFilters">重置</el-button>
              <el-button type="success" icon="el-icon-download" :loading="exporting" @click="exportData">导出</el-button>
            </div>
          </el-form>
        </div>
      </div>

      <div v-if="hasSearched" class="el-card is-always-shadow mb-4 summary-card">
        <div class="el-card__body summary-row">
          <span>总条数: <b>{{ total }}</b></span>
        </div>
      </div>

      <div v-if="hasSearched" class="el-card is-always-shadow table-card" v-loading="loading" element-loading-text="加载中...">
        <div class="el-card__body">
          <el-table v-if="tableData.length" :data="tableData" border stripe max-height="620" style="width: 100%" :header-cell-style="{ background: '#eef1f6', color: '#606266' }">
            <el-table-column prop="是否核对" label="是否核对" width="80" align="center" />
            <el-table-column prop="序列号" label="序列号" min-width="100" show-overflow-tooltip />
            <el-table-column prop="工单状态" label="工单状态" min-width="100" show-overflow-tooltip />
            <el-table-column prop="工单编号" label="工单编号" min-width="150" show-overflow-tooltip />
            <el-table-column prop="订单批号" label="订单批号" min-width="150" show-overflow-tooltip />
            <el-table-column prop="订单数量" label="订单数量" min-width="100" align="right">
              <template #default="scope"><span>{{ formatNumber(scope.row.订单数量) }}</span></template>
            </el-table-column>
            <el-table-column prop="料品编码" label="料品编码" min-width="150" show-overflow-tooltip />
            <el-table-column prop="生产线编号" label="生产线编号" min-width="120" show-overflow-tooltip />
            <el-table-column prop="规格型号" label="规格型号" min-width="150" show-overflow-tooltip />
            <el-table-column prop="报工人" label="报工人" min-width="100" show-overflow-tooltip />
            <el-table-column prop="工单数量" label="工单数量" min-width="100" align="right">
              <template #default="scope"><span>{{ formatNumber(scope.row.工单数量) }}</span></template>
            </el-table-column>
            <el-table-column prop="报工数量" label="报工数量" min-width="100" align="right">
              <template #default="scope"><span>{{ formatNumber(scope.row.报工数量) }}</span></template>
            </el-table-column>
            <el-table-column prop="报废数量" label="报废数量" min-width="100" align="right">
              <template #default="scope"><span>{{ formatNumber(scope.row.报废数量) }}</span></template>
            </el-table-column>
            <el-table-column prop="返修数量" label="返修数量" min-width="100" align="right">
              <template #default="scope"><span>{{ formatNumber(scope.row.返修数量) }}</span></template>
            </el-table-column>
            <el-table-column prop="车间提供" label="车间提供" min-width="100" align="right">
              <template #default="scope"><span>{{ formatNumber(scope.row.车间提供) }}</span></template>
            </el-table-column>
            <el-table-column prop="时间" label="时间" min-width="100" align="right">
              <template #default="scope"><span>{{ scope.row.时间 !== null ? scope.row.时间 : '-' }}</span></template>
            </el-table-column>
            <el-table-column prop="开工时间" label="开工时间" min-width="150" show-overflow-tooltip />
            <el-table-column prop="完工时间" label="完工时间" min-width="150" show-overflow-tooltip />
            <el-table-column prop="确定交期" label="确定交期" min-width="120" show-overflow-tooltip />
            <el-table-column prop="客户" label="客户" min-width="120" show-overflow-tooltip />
            <el-table-column prop="工序" label="工序" min-width="120" show-overflow-tooltip />
          </el-table>
          <el-empty v-else-if="!loading" description="暂无数据" />
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
  name: 'WorkshopReportDetailPack',
  components: { Layout },
  data() {
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)
    const today = new Date()
    const fmt = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    return {
      breadcrumbItems: ['报工', '车间报工详情', '包装车间报工详情'],
      filters: { start: fmt(yesterday), end: fmt(today), 序列号: '', 姓名: '', 生产线编号: '', 订单批号: '' },
      tableData: [], loading: false, hasSearched: false,
      currentPage: 1, pageSize: 100, total: 0, sidebarMenus: [], exporting: false
    }
  },
  created() {
    eventBus.$on('sidebar-Menus-Updated', (menus) => { this.sidebarMenus = menus; this.generateBreadcrumb(this.$route.path) })
  },
  watch: { $route(v) { this.generateBreadcrumb(v.path) } },
  methods: {
    generateBreadcrumb(path) {
      try {
        const find = (menus, p) => { for (const m of menus) { for (const s of (m.children || [])) { for (const gc of (s.children || [])) { for (const c of (gc.children || [])) { if (c.path === p) return [s.name, gc.name, c.name] } if (gc.path === p) return [s.name, gc.name] } } } const seg = p.split('/').pop(); return ['报工', '车间报工详情', '包装车间报工详情'] }
        const r = find(this.sidebarMenus, '/' + path.split('/').filter(p => p).join('/'))
        this.breadcrumbItems = Array.isArray(r) ? r : [r]
      } catch { this.breadcrumbItems = ['报工', '车间报工详情', '包装车间报工详情'] }
    },
    formatNumber(v) { return (v === null || v === undefined || v === '') ? '-' : Number(v).toLocaleString() },
    getFilterParams() {
      const params = {}
      if (this.filters.start) params.start = this.filters.start
      if (this.filters.end) params.end = this.filters.end
      if (this.filters.序列号) params.序列号 = this.filters.序列号.trim()
      if (this.filters.姓名) params.姓名 = this.filters.姓名.trim()
      if (this.filters.生产线编号) params.生产线编号 = this.filters.生产线编号.trim()
      if (this.filters.订单批号) params.订单批号 = this.filters.订单批号.trim()
      return params
    },
    async searchData() {
      if (!this.filters.start || !this.filters.end) { this.$message.warning('请选择时间范围'); return }
      this.loading = true; this.hasSearched = true
      try {
        const params = this.getFilterParams()
        params.page = this.currentPage; params.page_size = this.pageSize
        const res = await axios.get('/api/workshopReportDetail/Pack', { params })
        if (res.data?.status === 'success') {
          this.tableData = res.data.data || []
          this.total = res.data.total_count || 0
        } else this.$message.error('数据获取失败')
      } catch { this.$message.error('数据加载失败') } finally { this.loading = false }
    },
    handlePageChange(p) { this.currentPage = p; this.searchData() },
    handleSizeChange(s) { this.pageSize = s; this.currentPage = 1; this.searchData() },
    resetFilters() {
      const yesterday = new Date(); yesterday.setDate(yesterday.getDate() - 1)
      const today = new Date()
      const fmt = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
      this.filters = { start: fmt(yesterday), end: fmt(today), 序列号: '', 姓名: '', 生产线编号: '', 订单批号: '' }
      this.hasSearched = true; this.tableData = []; this.total = 0; this.currentPage = 1
      this.searchData()
    },
    async exportData() {
      if (!this.filters.start || !this.filters.end) { this.$message.warning('请选择时间范围'); return }
      this.exporting = true
      try {
        const params = { start: this.filters.start, end: this.filters.end }
        if (this.filters.序列号) params.序列号 = this.filters.序列号.trim()
        if (this.filters.姓名) params.姓名 = this.filters.姓名.trim()
        if (this.filters.生产线编号) params.生产线编号 = this.filters.生产线编号.trim()
        if (this.filters.订单批号) params.订单批号 = this.filters.订单批号.trim()
        const res = await axios.get('/api/workshopReportDetail/Pack/export', { params, responseType: 'blob' })
        const cd = res.headers['content-disposition']; let fname = '包装车间报工详情.xlsx'; if (cd) { const m = cd.match(/filename\*=UTF-8''(.+)/); if (m) fname = decodeURIComponent(m[1]); else { const p = cd.split('filename=')[1]; if (p) fname = p.replace(/"/g, '') } }
        const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        const link = document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = fname; link.click(); URL.revokeObjectURL(link.href)
        this.$message.success('导出成功')
      } catch { this.$message.error('导出失败') } finally { this.exporting = false }
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
</style>
