<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="report-container">
      <template v-if="!detailData">
        <div class="el-card is-always-shadow mb-4">
          <div class="el-card__body">
            <el-form @submit.native.prevent="loadSummary" label-width="80px">
              <el-row :gutter="15">
                <el-col :span="4">
                  <el-form-item label="确定交期">
                    <el-date-picker v-model="filters.交期范围" type="daterange" :unlink-panels="true" range-separator="-" start-placeholder="开始" end-placeholder="结束" value-format="yyyy-MM-dd" style="width:100%" />
                  </el-form-item>
                </el-col>
                <el-col :span="4">
                  <el-form-item label="订单批号">
                    <el-input v-model="filters.订单批号" placeholder="订单批号" clearable @keyup.enter.native="loadSummary" />
                  </el-form-item>
                </el-col>
                <el-col :span="4">
                  <el-form-item label="工序">
                    <el-select v-model="filters.工序" placeholder="选择工序" filterable clearable>
                      <el-option v-for="o in processOptions" :key="o" :label="o" :value="o" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="4">
                  <el-form-item label="料品编码">
                    <el-input v-model="filters.料品编码" placeholder="料品编码" clearable @keyup.enter.native="loadSummary" />
                  </el-form-item>
                </el-col>
                <el-col :span="4">
                  <el-form-item label="料品名称">
                    <el-input v-model="filters.料品名称" placeholder="料品名称" clearable @keyup.enter.native="loadSummary" />
                  </el-form-item>
                </el-col>
              </el-row>
              <div class="form-actions">
                <el-button type="primary" :loading="loading" @click="loadSummary">查询</el-button>
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

      <div v-if="processSummary.length" class="el-card is-always-shadow mb-4 summary-form">
        <div class="el-card__body">
          <div class="summary-form-title">工序统计</div>
          <el-table :data="processTableData" border size="small" style="width: 100%" :header-cell-style="{ background: '#eef1f6', color: '#606266' }">
            <el-table-column prop="label" label="" min-width="110" fixed />
            <el-table-column v-for="item in processSummary" :key="item.工序" :label="item.工序" min-width="110" align="right">
              <template #default="scope">
                <span>{{ formatNumber(scope.row[item.工序]) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

        <div class="el-card is-always-shadow table-card" v-loading="loading" element-loading-text="加载中...">
          <div class="el-card__body">
            <el-table v-if="tableData.length" :key="'main-' + total" :data="tableData" border stripe max-height="620" style="width: 100%" :header-cell-style="{ background: '#eef1f6', color: '#606266' }">
              <el-table-column type="index" label="序号" width="60" align="center" :index="indexMethod" />
              <el-table-column prop="客户" label="客户" min-width="120" show-overflow-tooltip />
              <el-table-column prop="订单批号" label="订单批号" min-width="140" show-overflow-tooltip>
                <template #default="scope">
                  <el-button type="text" @click="loadDetail(scope.row.订单批号, scope.row.工序)">{{ scope.row.订单批号 }}</el-button>
                </template>
              </el-table-column>
              <el-table-column prop="确定交期" label="确定交期" min-width="110" align="center" show-overflow-tooltip />
              <el-table-column prop="料品编码" label="料品编码" min-width="130" show-overflow-tooltip />
              <el-table-column prop="料品名称" label="料品名称" min-width="160" show-overflow-tooltip />
              <el-table-column prop="规格型号" label="规格型号" min-width="140" show-overflow-tooltip />
              <el-table-column prop="工序" label="工序" min-width="120" show-overflow-tooltip />
              <el-table-column prop="半成品料品名称" label="半成品料品名称" min-width="160" show-overflow-tooltip />
              <el-table-column prop="订单数量" label="订单数量" min-width="90" align="right">
                <template #default="scope"><span>{{ formatNumber(scope.row.订单数量) }}</span></template>
              </el-table-column>
              <el-table-column prop="计划产量" label="计划产量" min-width="90" align="right">
                <template #default="scope"><span>{{ formatNumber(scope.row.计划产量) }}</span></template>
              </el-table-column>
              <el-table-column prop="完成数量" label="完成数量" min-width="90" align="right">
                <template #default="scope"><span>{{ formatNumber(scope.row.完成数量) }}</span></template>
              </el-table-column>
              <el-table-column prop="未完成数量" label="未完成数量" min-width="100" align="right">
                <template #default="scope"><span :style="{ color: scope.row.未完成数量 > 0 ? '#e6a23c' : '#67c23a' }">{{ formatNumber(scope.row.未完成数量) }}</span></template>
              </el-table-column>
              <el-table-column prop="最早完成日期" label="最早完成日期" min-width="110" align="center" show-overflow-tooltip />
              <el-table-column prop="最晚完成日期" label="最晚完成日期" min-width="110" align="center" show-overflow-tooltip />
            </el-table>
            <el-empty v-else description="暂无数据" />
            <div class="pagination-row">
              <el-pagination background layout="total, sizes, prev, pager, next, jumper" :total="total" :current-page="currentPage" :page-sizes="[50, 100, 200, 500]" :page-size="pageSize" @current-change="handlePageChange" @size-change="handleSizeChange" />
            </div>
          </div>
        </div>
      </template>

      <template v-else>
        <div class="el-card is-always-shadow mb-4">
          <div class="el-card__body">
            <div class="detail-header">
              <el-button @click="backToSummary" icon="el-icon-arrow-left">返回汇总</el-button>
              <span class="detail-title">订单批号: {{ detailOrderNo }} 的报工详情</span>
              <span class="detail-count">共 <b>{{ detailData.length }}</b> 条</span>
            </div>
          </div>
        </div>

        <div class="el-card is-always-shadow table-card" v-loading="detailLoading" element-loading-text="加载中...">
          <div class="el-card__body">
            <el-table v-if="detailData.length" :key="'detail-' + detailData.length" :data="detailData" border stripe max-height="620" style="width: 100%" :header-cell-style="{ background: '#eef1f6', color: '#606266' }">
              <el-table-column type="index" label="序号" width="60" align="center" />
              <el-table-column prop="工单编号" label="工单编号" min-width="140" show-overflow-tooltip />
              <el-table-column prop="工单状态" label="工单状态" min-width="90" show-overflow-tooltip />
              <el-table-column prop="生产车间" label="生产车间" min-width="100" show-overflow-tooltip />
              <el-table-column prop="订单批号" label="订单批号" min-width="130" show-overflow-tooltip />
              <el-table-column prop="料品编码" label="料品编码" min-width="130" show-overflow-tooltip />
              <el-table-column prop="规格型号" label="规格型号" min-width="140" show-overflow-tooltip />
              <el-table-column prop="生产线编号" label="生产线编号" min-width="110" show-overflow-tooltip />
              <el-table-column prop="报工人" label="报工人" min-width="90" show-overflow-tooltip />
              <el-table-column prop="工单数量" label="工单数量" min-width="90" align="right">
                <template #default="scope"><span>{{ formatNumber(scope.row.工单数量) }}</span></template>
              </el-table-column>
              <el-table-column prop="报工数量" label="报工数量" min-width="90" align="right">
                <template #default="scope"><span>{{ formatNumber(scope.row.报工数量) }}</span></template>
              </el-table-column>
              <el-table-column prop="报废数量" label="报废数量" min-width="90" align="right">
                <template #default="scope"><span>{{ formatNumber(scope.row.报废数量) }}</span></template>
              </el-table-column>
              <el-table-column prop="返修数量" label="返修数量" min-width="90" align="right">
                <template #default="scope"><span>{{ formatNumber(scope.row.返修数量) }}</span></template>
              </el-table-column>
              <el-table-column prop="理论产能" label="理论产能" min-width="100" align="right">
                <template #default="scope"><span>{{ scope.row.理论产能 != null ? formatNumber(scope.row.理论产能) : '-' }}</span></template>
              </el-table-column>
              <el-table-column prop="理论工时" label="理论工时" min-width="90" align="right">
                <template #default="scope"><span>{{ scope.row.理论工时 != null ? scope.row.理论工时 : '-' }}</span></template>
              </el-table-column>
              <el-table-column prop="开工时间" label="开工时间" min-width="150" show-overflow-tooltip />
              <el-table-column prop="完工时间" label="完工时间" min-width="150" show-overflow-tooltip />
              <el-table-column prop="确定交期" label="确定交期" min-width="110" align="center" show-overflow-tooltip />
              <el-table-column prop="工序" label="工序" min-width="140" show-overflow-tooltip />
              <el-table-column prop="客户" label="客户" min-width="110" show-overflow-tooltip />
            </el-table>
            <el-empty v-else description="暂无数据" />
          </div>
        </div>
      </template>
    </div>
  </Layout>
</template>

<script>
import axios from 'axios'
import Layout from '@/components/Layout.vue'
import { eventBus } from '../../eventBus'

export default {
  name: 'LockCWorkProgress',
  components: { Layout },
  data() {
    return {
      breadcrumbItems: ['报表页面', '锁体C车间生产进度表'],
      filters: { 订单批号: '', 料品编码: '', 料品名称: '', 工序: '', 交期范围: [] },
      processOptions: [],
      tableData: [], allData: [], processSummary: [], loading: false,
      currentPage: 1, pageSize: 100, total: 0, sidebarMenus: [],
      detailData: null, detailLoading: false, detailOrderNo: ''
    }
  },
  created() {
    eventBus.$on('sidebar-Menus-Updated', (menus) => { this.sidebarMenus = menus; this.generateBreadcrumb(this.$route.path) })
    this.loadOptions(); this.loadSummary()
  },
  watch: { $route(v) { this.generateBreadcrumb(v.path) } },
  computed: {
    processTableData() {
      if (!this.processSummary.length) return []
      const finishedRow = { label: '完成数量' }
      const unfinishedRow = { label: '未完成数量' }
      this.processSummary.forEach(item => {
        finishedRow[item.工序] = item.完成数量
        unfinishedRow[item.工序] = item.未完成数量
      })
      return [finishedRow, unfinishedRow]
    }
  },
  methods: {
    generateBreadcrumb(path) {
      try {
        const find = (menus, p) => { for (const m of menus) { if (m.path === p) return m.name; if (m.children) for (const c of m.children) if (c.path === p) return [m.name, c.name] } return p.split('/').pop() }
        const r = find(this.sidebarMenus, '/' + path.split('/').filter(p => p).join('/'))
        this.breadcrumbItems = Array.isArray(r) ? r : [r]
      } catch { this.breadcrumbItems = ['报表页面', '锁体C车间生产进度表'] }
    },
    formatNumber(v) { return (v === null || v === undefined || v === '') ? '-' : Number(v).toLocaleString() },
    indexMethod(i) { return (this.currentPage - 1) * this.pageSize + i + 1 },
    async loadOptions() {
      try {
        const fields = ['工序']
        const results = await Promise.all(fields.map(f => axios.get('/api/lockCWorkProgress/options', { params: { field: f } }).then(res => ({ f, d: res.data })).catch(() => ({ f, d: { data: [] } }))))
        for (const r of results) {
          const vals = (r.d.data || []).map(i => i.value)
          if (r.f === '工序') this.processOptions = vals
        }
      } catch {}
    },
    async loadSummary() {
      this.loading = true; this.currentPage = 1
      try {
        const params = {}
        if (this.filters.订单批号) params.订单批号 = this.filters.订单批号.trim()
        if (this.filters.料品编码) params.料品编码 = this.filters.料品编码.trim()
        if (this.filters.料品名称) params.料品名称 = this.filters.料品名称.trim()
        if (this.filters.工序) params.工序 = this.filters.工序
        if (Array.isArray(this.filters.交期范围) && this.filters.交期范围.length === 2) {
          params.交期开始 = this.filters.交期范围[0]
          params.交期结束 = this.filters.交期范围[1]
        }
        const res = await axios.get('/api/lockCWorkProgress', { params })
        if (res.data?.status === 'success') {
          this.allData = res.data.data || []; this.total = this.allData.length; this.updateTableData()
          const map = {}
          this.allData.forEach(row => {
            const k = row.工序 || '未知'
            if (!map[k]) map[k] = { 工序: k, 完成数量: 0, 未完成数量: 0 }
            map[k].完成数量 += Number(row.完成数量) || 0
            map[k].未完成数量 += Number(row.未完成数量) || 0
          })
          this.processSummary = Object.values(map).sort((a, b) => a.工序.localeCompare(b.工序))
        }
        else this.$message.error('数据获取失败')
      } catch { this.$message.error('数据加载失败') } finally { this.loading = false }
    },
    updateTableData() { const s = (this.currentPage - 1) * this.pageSize; this.tableData = this.allData.slice(s, s + this.pageSize) },
    handlePageChange(p) { this.currentPage = p; this.updateTableData() },
    handleSizeChange(s) { this.pageSize = s; this.currentPage = 1; this.updateTableData() },
    async loadDetail(订单批号, 工序) {
      this.detailLoading = true; this.detailOrderNo = `${订单批号} - ${工序}`; this.detailData = []
      try {
        const params = { 订单批号 }
        if (工序) params.工序 = 工序
        const res = await axios.get('/api/lockCWorkProgress/detail', { params })
        if (res.data?.status === 'success') this.detailData = res.data.data || []
        else this.$message.error('详情获取失败')
      } catch { this.$message.error('详情加载失败') } finally { this.detailLoading = false }
    },
    backToSummary() { this.detailData = null; this.detailOrderNo = '' },
    resetFilters() { this.filters = { 订单批号: '', 料品编码: '', 料品名称: '', 工序: '', 交期范围: [] }; this.processSummary = []; this.loadSummary() }
  }
}
</script>

<style scoped>
.report-container { padding: 0; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; padding-top: 10px; }
.summary-row { display: flex; justify-content: flex-end; color: #303133; }
.summary-form { background: #f5f7fa; }
.summary-form-title { font-size: 15px; font-weight: bold; color: #303133; margin-bottom: 12px; }
.table-card { min-height: 100px; }
.pagination-row { display: flex; justify-content: flex-end; margin-top: 16px; }
.mb-4 { margin-bottom: 16px; }
.detail-header { display: flex; align-items: center; gap: 16px; }
.detail-title { font-size: 15px; font-weight: bold; color: #303133; }
.detail-count { font-size: 13px; color: #909399; margin-left: auto; }
</style>
