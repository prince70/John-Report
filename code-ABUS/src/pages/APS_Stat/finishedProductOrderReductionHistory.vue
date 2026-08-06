<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="report-container">
      <div class="el-card is-always-shadow mb-4">
        <div class="el-card__body">
          <el-form @submit.native.prevent="searchData" label-width="100px">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="规格型号">
                  <el-input v-model="filters.规格型号" placeholder="请输入规格型号" clearable @keyup.enter.native="searchData" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="订单批号">
                  <el-input v-model="filters.订单批号" placeholder="请输入订单批号" clearable @keyup.enter.native="searchData" />
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
            <el-table-column prop="料品编码" label="料品编码" min-width="140" show-overflow-tooltip />
            <el-table-column prop="系列" label="系列" min-width="140" show-overflow-tooltip />
            <el-table-column prop="规格型号" label="规格型号" min-width="160" show-overflow-tooltip />
            <el-table-column prop="订单批号" label="订单批号" min-width="140" show-overflow-tooltip />
            <el-table-column prop="确定交期" label="确定交期" min-width="120" show-overflow-tooltip />
            <el-table-column prop="原订单数量" label="原订单数量" min-width="110" align="right" />
            <el-table-column prop="减单数量" label="减单数量" min-width="100" align="right" />
            <el-table-column prop="即时库存" label="即时库存" min-width="100" align="right">
              <template #default="scope"><span>{{ formatNumber(scope.row.即时库存) }}</span></template>
            </el-table-column>
            <el-table-column prop="减单时间" label="减单时间" min-width="160" show-overflow-tooltip />
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
  name: 'FinishedProductOrderReductionHistory',
  components: { Layout },
  data() {
    return {
      breadcrumbItems: ['报工', '成品减单历史记录'],
      filters: { 规格型号: '', 订单批号: '' },
      tableData: [], allData: [], loading: false,
      currentPage: 1, pageSize: 100, total: 0, sidebarMenus: []
    }
  },
  created() {
    eventBus.$on('sidebar-Menus-Updated', (menus) => { this.sidebarMenus = menus; this.generateBreadcrumb(this.$route.path) })
    this.searchData()
  },
  watch: { $route(v) { this.generateBreadcrumb(v.path) } },
  methods: {
    generateBreadcrumb() { this.breadcrumbItems = ['报工', '成品减单历史记录'] },
    formatNumber(v) { return (v === null || v === undefined || v === '') ? '-' : Number(v).toLocaleString() },
    indexMethod(i) { return (this.currentPage - 1) * this.pageSize + i + 1 },
    async searchData() {
      this.loading = true; this.currentPage = 1
      try {
        const params = {}
        if (this.filters.规格型号) params.规格型号 = this.filters.规格型号.trim()
        if (this.filters.订单批号) params.订单批号 = this.filters.订单批号.trim()
        const res = await axios.get('/api/finishedProductOrderReductionHistory', { params })
        if (res.data?.status === 'success') {
          this.allData = res.data.data || []
          this.total = res.data.total_count || this.allData.length
          this.updateTableData()
        } else { this.$message.error('数据获取失败') }
      } catch { this.$message.error('数据加载失败') } finally { this.loading = false }
    },
    updateTableData() { const s = (this.currentPage - 1) * this.pageSize; this.tableData = this.allData.slice(s, s + this.pageSize) },
    handlePageChange(p) { this.currentPage = p; this.updateTableData() },
    handleSizeChange(s) { this.pageSize = s; this.currentPage = 1; this.updateTableData() },
    resetFilters() {
      this.filters = { 规格型号: '', 订单批号: '' }
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
</style>
