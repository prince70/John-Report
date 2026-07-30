<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="report-container">
      <div class="el-card is-always-shadow mb-4">
        <div class="el-card__body">
          <el-form @submit.native.prevent="searchData" label-width="100px">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="报工日期始">
                  <el-date-picker v-model="filters.start" type="date" placeholder="报工日期始" value-format="yyyy-MM-dd" clearable style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="报工日期末">
                  <el-date-picker v-model="filters.end" type="date" placeholder="报工日期末" value-format="yyyy-MM-dd" clearable style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="序列号">
                  <el-input v-model="filters.序列号" placeholder="请输入序列号" clearable @keyup.enter.native="searchData" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="员工姓名">
                  <el-input v-model="filters.姓名" placeholder="请输入员工姓名" clearable @keyup.enter.native="searchData" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="规格型号">
                  <el-input v-model="filters.规格型号" placeholder="请输入规格型号" clearable @keyup.enter.native="searchData" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="工序">
                  <el-input v-model="filters.工序" placeholder="请输入工序" clearable @keyup.enter.native="searchData" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="生产线编号">
                  <el-input v-model="filters.生产线编号" placeholder="请输入生产线编号" clearable @keyup.enter.native="searchData" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="工单批号">
                  <el-input v-model="filters.工单批号" placeholder="请输入工单批号" clearable @keyup.enter.native="searchData" />
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

      <div v-if="hasSearched" class="el-card is-always-shadow mb-4 summary-card">
        <div class="el-card__body summary-row"><span>总条数: <b>{{ total }}</b></span></div>
      </div>

      <div v-if="hasSearched" class="el-card is-always-shadow table-card" v-loading="loading" element-loading-text="加载中...">
        <div class="el-card__body">
          <el-table v-if="tableData.length" :data="tableData" border stripe max-height="620" style="width:100%" :header-cell-style="{ background: '#eef1f6', color: '#606266' }">
            <el-table-column prop="是否核对" label="是否核对" width="80" align="center" />
            <el-table-column prop="序列号" label="序列号" min-width="100" show-overflow-tooltip />
            <el-table-column prop="生产车间" label="工单状态" min-width="120" show-overflow-tooltip />
            <el-table-column prop="工单编号" label="工单编号" min-width="150" show-overflow-tooltip />
            <el-table-column prop="工单状态" label="工单状态" min-width="100" show-overflow-tooltip />
            <el-table-column prop="订单批号" label="订单批号" min-width="150" show-overflow-tooltip />
            <el-table-column prop="确定交期" label="确定交期" min-width="120" show-overflow-tooltip />
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
            <el-table-column prop="客户" label="客户" min-width="120" show-overflow-tooltip />
            <el-table-column prop="工序" label="工序" min-width="120" show-overflow-tooltip />
            <el-table-column prop="料品名称" label="料品名称" min-width="150" show-overflow-tooltip />
            <el-table-column prop="急货" label="急货" min-width="80" show-overflow-tooltip />
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
  name: 'WorkshopReportDetailDamoDM',
  components: { Layout },
  data() {
    const yesterday = new Date(); yesterday.setDate(yesterday.getDate() - 1)
    const today = new Date()
    const fmt = d => `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
    return {
      breadcrumbItems: ['报工', '车间报工详情', '打磨-打磨区报工详情'],
      filters: { start: fmt(yesterday), end: fmt(today), 序列号: '', 姓名: '', 规格型号: '', 工序: '', 生产线编号: '', 工单批号: '' },
      tableData: [], allData: [], loading: false, hasSearched: false,
      currentPage: 1, pageSize: 100, total: 0, sidebarMenus: []
    }
  },
  created() { eventBus.$on('sidebar-Menus-Updated', (m) => { this.sidebarMenus = m; this.generateBreadcrumb(this.$route.path) }) },
  watch: { $route(v) { this.generateBreadcrumb(v.path) } },
  methods: {
    generateBreadcrumb() { this.breadcrumbItems = ['报工', '车间报工详情', '打磨-打磨区报工详情'] },
    formatNumber(v) { return (v === null || v === undefined || v === '') ? '-' : Number(v).toLocaleString() },
    async searchData() {
      if (!this.filters.start || !this.filters.end) { this.$message.warning('请选择时间范围'); return }
      this.loading = true; this.currentPage = 1; this.hasSearched = true
      try {
        const params = { start: this.filters.start, end: this.filters.end }
        if (this.filters.序列号) params.序列号 = this.filters.序列号.trim()
        if (this.filters.姓名) params.姓名 = this.filters.姓名.trim()
        if (this.filters.规格型号) params.规格型号 = this.filters.规格型号.trim()
        if (this.filters.工序) params.工序 = this.filters.工序.trim()
        if (this.filters.生产线编号) params.生产线编号 = this.filters.生产线编号.trim()
        if (this.filters.工单批号) params.工单批号 = this.filters.工单批号.trim()
        const res = await axios.get('/api/workshopReportDetail/DamoDM', { params })
        if (res.data?.status === 'success') { this.allData = res.data.data || []; this.total = res.data.total_count || this.allData.length; this.updateTableData() }
        else this.$message.error('数据获取失败')
      } catch { this.$message.error('数据加载失败') } finally { this.loading = false }
    },
    updateTableData() { const s = (this.currentPage-1)*this.pageSize; this.tableData = this.allData.slice(s, s+this.pageSize) },
    handlePageChange(p) { this.currentPage = p; this.updateTableData() },
    handleSizeChange(s) { this.pageSize = s; this.currentPage = 1; this.updateTableData() },
    resetFilters() {
      const yesterday = new Date(); yesterday.setDate(yesterday.getDate()-1)
      const today = new Date()
      const fmt = d => `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
      this.filters = { start: fmt(yesterday), end: fmt(today), 序列号: '', 姓名: '', 规格型号: '', 工序: '', 生产线编号: '', 工单批号: '' }
      this.hasSearched = false; this.tableData = []; this.allData = []; this.total = 0
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
