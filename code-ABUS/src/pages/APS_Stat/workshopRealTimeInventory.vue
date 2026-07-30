<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="report-container">
      <div class="el-card is-always-shadow mb-4">
        <div class="el-card__body">
          <el-form @submit.native.prevent="searchData" label-width="100px">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="存放位置">
                  <el-select v-model="filters.存放位置" placeholder="全部" clearable filterable style="width:100%">
                    <el-option v-for="item in 存放位置列表" :key="item" :label="item" :value="item" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <div class="form-actions">
              <el-button type="primary" :loading="loading" @click="searchData">查询</el-button>
              <el-button @click="resetFilters">重置</el-button>
              <el-button type="success" @click="exportData" :disabled="!tableData.length">导出</el-button>
            </div>
          </el-form>
        </div>
      </div>

      <div v-if="hasSearched" class="el-card is-always-shadow mb-4 summary-card">
        <div class="el-card__body summary-row">
          <span>更新时间: <b>{{ update_time }}</b></span>
          <span style="margin-left:30px">总库存: <b>{{ formatNumber(total_inventory) }}</b></span>
          <span style="margin-left:30px">总条数: <b>{{ total }}</b></span>
        </div>
      </div>

      <div v-if="hasSearched" class="el-card is-always-shadow table-card" v-loading="loading" element-loading-text="加载中...">
        <div class="el-card__body">
          <el-table v-if="tableData.length" :data="tableData" border stripe max-height="620" style="width:100%" :header-cell-style="{ background: '#eef1f6', color: '#606266' }">
            <el-table-column prop="item_no" label="item_no" min-width="150" show-overflow-tooltip />
            <el-table-column prop="产品名称" label="产品名称" min-width="150" show-overflow-tooltip />
            <el-table-column prop="产品规格" label="产品规格" min-width="150" show-overflow-tooltip />
            <el-table-column prop="库存" label="库存" min-width="100" align="right">
              <template #default="scope"><span>{{ formatNumber(scope.row.库存) }}</span></template>
            </el-table-column>
            <el-table-column prop="存放位置" label="存放位置" min-width="120" show-overflow-tooltip />
            <el-table-column prop="备注" label="备注" min-width="150" show-overflow-tooltip />
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
import * as XLSX from 'xlsx'
import Layout from '@/components/Layout.vue'
import { eventBus } from '../../eventBus'

export default {
  name: 'WorkshopRealTimeInventory',
  components: { Layout },
  data() {
    return {
      breadcrumbItems: ['报工', '车间实时库存'],
      filters: { 存放位置: '' },
      tableData: [], allData: [], loading: false, hasSearched: false,
      currentPage: 1, pageSize: 100, total: 0, total_inventory: 0, update_time: '',
      存放位置列表: [], sidebarMenus: []
    }
  },
  created() {
    eventBus.$on('sidebar-Menus-Updated', (m) => { this.sidebarMenus = m; this.generateBreadcrumb(this.$route.path) });
    this.searchData()
  },
  watch: { $route(v) { this.generateBreadcrumb(v.path) } },
  methods: {
    generateBreadcrumb() { this.breadcrumbItems = ['报工', '车间实时库存'] },
    formatNumber(v) { return (v === null || v === undefined || v === '') ? '-' : Number(v).toLocaleString() },
    async searchData() {
      this.loading = true; this.currentPage = 1; this.hasSearched = true
      try {
        const params = {}
        if (this.filters.存放位置) params.存放位置 = this.filters.存放位置.trim()
        const res = await axios.get('/api/workshopRealTimeInventory', { params })
        if (res.data?.status === 'success') {
          this.allData = res.data.data || []
          this.total = this.allData.length
          this.total_inventory = this.allData.reduce((sum, r) => sum + (r.库存 || 0), 0)
          this.update_time = res.data.update_time || ''
          this.存放位置列表 = res.data.存放位置列表 || []
          this.updateTableData()
        } else this.$message.error('数据获取失败')
      } catch { this.$message.error('数据加载失败') } finally { this.loading = false }
    },
    updateTableData() { const s = (this.currentPage-1)*this.pageSize; this.tableData = this.allData.slice(s, s+this.pageSize) },
    handlePageChange(p) { this.currentPage = p; this.updateTableData() },
    handleSizeChange(s) { this.pageSize = s; this.currentPage = 1; this.updateTableData() },
    resetFilters() {
      this.filters = { 存放位置: '' }
      this.currentPage = 1
      this.searchData()
    },
    exportData() {
      const data = this.allData.map(r => ({
        'item_no': r.item_no, '产品名称': r.产品名称, '产品规格': r.产品规格,
        '库存': r.库存, '存放位置': r.存放位置, '备注': r.备注
      }))
      const ws = XLSX.utils.json_to_sheet(data)
      const wb = XLSX.utils.book_new()
      XLSX.utils.book_append_sheet(wb, ws, '车间实时库存')
      XLSX.writeFile(wb, `车间实时库存_${this.update_time}.xlsx`)
    }
  }
}
</script>

<style scoped>
.report-container { padding: 0; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; padding-top: 10px; }
.summary-row { display: flex; justify-content: flex-end; color: #303133; gap: 10px; }
.table-card { min-height: 100px; }
.pagination-row { display: flex; justify-content: flex-end; margin-top: 16px; }
.mb-4 { margin-bottom: 16px; }
</style>
