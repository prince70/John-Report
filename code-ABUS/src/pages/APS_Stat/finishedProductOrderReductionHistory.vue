<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="report-container">
      <div class="el-card is-always-shadow mb-4">
        <div class="el-card__body">
          <el-form @submit.native.prevent="searchData" label-width="100px">
            <el-row :gutter="20">
              <template v-if="activeTab === 'stock'">
                <el-col :span="6">
                  <el-form-item label="料品编码">
                    <el-input v-model="stockFilters.item_no" placeholder="请输入料品编码" clearable @keyup.enter.native="searchData" />
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item label="产品名称">
                    <el-select v-model="stockFilters.产品名称" placeholder="请选择产品名称" filterable clearable allow-create @change="onStockOptionChange">
                      <el-option v-for="n in stockOptions.产品名称" :key="n" :label="n" :value="n" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item label="系列">
                    <el-select v-model="stockFilters.系列" placeholder="请选择系列" filterable clearable allow-create @change="onStockOptionChange">
                      <el-option v-for="n in stockOptions.系列" :key="n" :label="n" :value="n" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item label="产品规格">
                    <el-select v-model="stockFilters.产品规格" placeholder="请选择产品规格" filterable clearable allow-create @change="onStockOptionChange">
                      <el-option v-for="n in stockOptions.产品规格" :key="n" :label="n" :value="n" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </template>
              <template v-else>
                <el-col :span="6">
                  <el-form-item label="规格型号">
                    <el-input v-model="reductionFilters.规格型号" placeholder="请输入规格型号" clearable @keyup.enter.native="searchData" />
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item label="订单批号">
                    <el-input v-model="reductionFilters.订单批号" placeholder="请输入订单批号" clearable @keyup.enter.native="searchData" />
                  </el-form-item>
                </el-col>
              </template>
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
          <div class="tab-buttons">
            <el-radio-group v-model="activeTab" size="small" @change="onTabChange">
              <el-radio-button label="stock">成品库存</el-radio-button>
              <el-radio-button label="reduction">成品减单</el-radio-button>
            </el-radio-group>
            <el-button v-if="activeTab === 'stock'" type="success" size="small" plain style="margin-left:12px" @click="openStatsDialog">查看统计</el-button>
            <el-button v-if="activeTab === 'reduction'" type="success" size="small" plain style="margin-left:12px" @click="openReductionStatsDialog">查看统计</el-button>
          </div>
          <div class="summary-right">
            <span v-if="activeTab === 'stock'" class="inventory-info">当前页库存数: <b>{{ currentPageInventory }}</b>　全部库存数: <b>{{ totalInventory }}</b></span>
            <span>总条数: <b>{{ total }}</b></span>
          </div>
        </div>
      </div>

      <div class="el-card is-always-shadow table-card" v-loading="loading" element-loading-text="加载中...">
        <div class="el-card__body">
          <template v-if="activeTab === 'stock'">
            <el-table v-if="tableData.length" :data="tableData" border stripe max-height="620" style="width: 100%" :header-cell-style="{ background: '#eef1f6', color: '#606266' }">
              <el-table-column type="index" label="序号" width="60" align="center" :index="indexMethod" />
              <el-table-column prop="item_no" label="料品编码" min-width="140" show-overflow-tooltip />
              <el-table-column prop="产品名称" label="产品名称" min-width="160" show-overflow-tooltip />
              <el-table-column prop="系列" label="系列" min-width="140" show-overflow-tooltip />
              <el-table-column prop="产品规格" label="产品规格" min-width="160" show-overflow-tooltip />
              <el-table-column prop="库存" label="库存" min-width="100" align="right">
                <template #default="scope"><span>{{ formatNumber(scope.row.库存) }}</span></template>
              </el-table-column>
              <el-table-column prop="存放位置" label="存放位置" min-width="120" show-overflow-tooltip />
            </el-table>
            <el-empty v-else description="暂无数据" />
          </template>
          <template v-else>
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
          </template>
          <div class="pagination-row">
            <el-pagination background layout="total, sizes, prev, pager, next, jumper" :total="total" :current-page="currentPage" :page-sizes="[50, 100, 200, 500]" :page-size="pageSize" @current-change="handlePageChange" @size-change="handleSizeChange" />
          </div>
        </div>
      </div>
    </div>

    <el-dialog title="按系列统计库存" :visible.sync="statsDialogVisible" width="600px" top="8vh">
      <div class="stats-dialog-total">所有系列库存合计：<b>{{ statsTotalInventory }}</b></div>
      <el-table :data="statsData" border stripe max-height="500" style="width: 100%" :header-cell-style="{ background: '#eef1f6', color: '#606266' }">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="系列" label="系列" min-width="200" show-overflow-tooltip />
        <el-table-column prop="库存" label="库存" min-width="150" align="right">
          <template #default="scope"><span>{{ formatNumber(scope.row.库存) }}</span></template>
        </el-table-column>
      </el-table>
      <span slot="footer">
        <el-button @click="statsDialogVisible = false">关闭</el-button>
      </span>
    </el-dialog>

    <el-dialog title="按月计算减单数量" :visible.sync="reductionStatsDialogVisible" width="600px" top="8vh">
      <div class="stats-dialog-total">所有月份减单合计：<b>{{ reductionTotalStats }}</b></div>
      <el-table :data="reductionStatsData" border stripe max-height="500" style="width: 100%" :header-cell-style="{ background: '#eef1f6', color: '#606266' }">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="月份" label="月份" min-width="150" show-overflow-tooltip />
        <el-table-column prop="减单数量" label="减单数量" min-width="150" align="right" />
      </el-table>
      <span slot="footer">
        <el-button @click="reductionStatsDialogVisible = false">关闭</el-button>
      </span>
    </el-dialog>
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
      breadcrumbItems: ['报工', '成品库存及成品减单历史记录'],
      activeTab: 'stock',
      stockFilters: { item_no: '', 产品名称: '', 系列: '', 产品规格: '' },
      reductionFilters: { 规格型号: '', 订单批号: '' },
      tableData: [], allData: [], loading: false,
      currentPage: 1, pageSize: 100, total: 0, sidebarMenus: [],
      stockOptions: { 产品名称: [], 系列: [], 产品规格: [] },
      totalInventory: 0, currentPageInventory: 0,
      statsDialogVisible: false, statsData: [], statsTotalInventory: 0,
      reductionStatsDialogVisible: false, reductionStatsData: [], reductionTotalStats: 0
    }
  },
  created() {
    eventBus.$on('sidebar-Menus-Updated', (menus) => { this.sidebarMenus = menus; this.generateBreadcrumb(this.$route.path) })
    this.loadStockOptions()
    this.searchData()
  },
  watch: { $route(v) { this.generateBreadcrumb(v.path) } },
  methods: {
    generateBreadcrumb() { this.breadcrumbItems = ['报工', '成品库存及成品减单历史记录'] },
    async loadStockOptions() {
      try {
        const params = {}
        if (this.stockFilters.产品名称) params.产品名称 = this.stockFilters.产品名称
        if (this.stockFilters.系列) params.系列 = this.stockFilters.系列
        if (this.stockFilters.产品规格) params.产品规格 = this.stockFilters.产品规格
        for (const field of ['产品名称', '系列', '产品规格']) {
          const res = await axios.get('/api/finishedProductStock/options', { params: { ...params, field } })
          if (res.data?.status === 'success') this.stockOptions[field] = res.data.data || []
        }
      } catch {}
    },
    onStockOptionChange() { this.loadStockOptions() },
    formatNumber(v) { return (v === null || v === undefined || v === '') ? '-' : Number(v).toLocaleString() },
    indexMethod(i) { return (this.currentPage - 1) * this.pageSize + i + 1 },
    onTabChange() { this.currentPage = 1; this.searchData() },
    async searchData() {
      this.loading = true; this.currentPage = 1
      try {
        if (this.activeTab === 'stock') {
          const params = this._getStockParams()
          const res = await axios.get('/api/finishedProductStock', { params })
          if (res.data?.status === 'success') {
            this.allData = res.data.data || []
            this.total = res.data.total_count || this.allData.length
            this.totalInventory = res.data.total_inventory || 0
            this.updateTableData()
          } else { this.$message.error('数据获取失败') }
        } else {
          const params = {}
          if (this.reductionFilters.规格型号) params.规格型号 = this.reductionFilters.规格型号.trim()
          if (this.reductionFilters.订单批号) params.订单批号 = this.reductionFilters.订单批号.trim()
          const res = await axios.get('/api/finishedProductOrderReductionHistory', { params })
          if (res.data?.status === 'success') {
            this.allData = res.data.data || []
            this.total = res.data.total_count || this.allData.length
            this.totalInventory = 0
            this.updateTableData()
          } else { this.$message.error('数据获取失败') }
        }
      } catch { this.$message.error('数据加载失败') } finally { this.loading = false }
    },
    _getStockParams() {
      const params = {}
      if (this.stockFilters.item_no) params.item_no = this.stockFilters.item_no.trim()
      if (this.stockFilters.产品名称) params.产品名称 = this.stockFilters.产品名称.trim()
      if (this.stockFilters.系列) params.系列 = this.stockFilters.系列.trim()
      if (this.stockFilters.产品规格) params.产品规格 = this.stockFilters.产品规格.trim()
      return params
    },
    updateTableData() {
      const s = (this.currentPage - 1) * this.pageSize
      const pageData = this.allData.slice(s, s + this.pageSize)
      this.tableData = pageData
      this.currentPageInventory = pageData.reduce((sum, r) => sum + (parseFloat(r.库存) || 0), 0)
    },
    handlePageChange(p) { this.currentPage = p; this.updateTableData() },
    handleSizeChange(s) { this.pageSize = s; this.currentPage = 1; this.updateTableData() },
    resetFilters() {
      if (this.activeTab === 'stock') {
        this.stockFilters = { item_no: '', 产品名称: '', 系列: '', 产品规格: '' }
      } else {
        this.reductionFilters = { 规格型号: '', 订单批号: '' }
      }
      this.searchData()
    },
    async openStatsDialog() {
      try {
        const res = await axios.get('/api/finishedProductStock/stats')
        if (res.data?.status === 'success') {
          this.statsData = res.data.data || []
          this.statsTotalInventory = res.data.total_inventory || 0
          this.statsDialogVisible = true
        }
      } catch { this.$message.error('统计加载失败') }
    },
    async openReductionStatsDialog() {
      try {
        const params = {}
        if (this.reductionFilters.规格型号) params.规格型号 = this.reductionFilters.规格型号.trim()
        if (this.reductionFilters.订单批号) params.订单批号 = this.reductionFilters.订单批号.trim()
        const res = await axios.get('/api/finishedProductOrderReduction/stats', { params })
        if (res.data?.status === 'success') {
          this.reductionStatsData = res.data.data || []
          this.reductionTotalStats = res.data.total_reduction || 0
          this.reductionStatsDialogVisible = true
        }
      } catch { this.$message.error('统计加载失败') }
    }
  }
}
</script>

<style scoped>
.report-container { padding: 0; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; padding-top: 10px; }
.summary-row { display: flex; justify-content: space-between; align-items: center; color: #303133; }
.tab-buttons { display: flex; align-items: center; }
.summary-right { display: flex; align-items: center; gap: 20px; }
.inventory-info { color: #409eff; font-size: 13px; }
.inventory-info b { font-size: 14px; color: #409eff; }
.table-card { min-height: 100px; }
.pagination-row { display: flex; justify-content: flex-end; margin-top: 16px; }
.mb-4 { margin-bottom: 16px; }
.stats-dialog-total { margin-bottom: 12px; font-size: 15px; color: #303133; }
.stats-dialog-total b { color: #409eff; font-size: 16px; }
</style>
