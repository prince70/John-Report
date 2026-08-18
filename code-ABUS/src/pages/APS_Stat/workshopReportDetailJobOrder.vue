<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="report-container">
      <div class="el-card is-always-shadow mb-4">
        <div class="el-card__body">
          <el-form @submit.native.prevent="handleSearch" label-width="100px">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="开始时间">
                  <el-date-picker v-model="filters.startDate" type="date" placeholder="选择开始时间" value-format="yyyy-MM-dd" clearable style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="结束时间">
                  <el-date-picker v-model="filters.endDate" type="date" placeholder="选择结束时间" value-format="yyyy-MM-dd" clearable style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="工单编号">
                  <el-input v-model="filters.workOrderId" placeholder="请输入工单编号" clearable @keyup.enter.native="handleSearch" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="姓名">
                  <el-input v-model="filters.personName" placeholder="请输入姓名" clearable @keyup.enter.native="handleSearch" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="订单批号">
                  <el-input v-model="filters.orderNumbers" placeholder="请输入订单批号" clearable @keyup.enter.native="handleSearch" />
                </el-form-item>
              </el-col>
            </el-row>
            <div class="form-actions">
              <el-button type="primary" :loading="loading" @click="currentPage = 1; handleSearch()">查询</el-button>
              <el-button @click="resetFilters">重置</el-button>
              <el-button type="success" icon="el-icon-download" :loading="exporting" @click="exportData">导出</el-button>
            </div>
          </el-form>
        </div>
      </div>

      <div v-if="hasSearched && !loading" class="el-card is-always-shadow mb-4 summary-card">
        <div class="el-card__body summary-row">
          <span>总条数: <b>{{ total }}</b></span>
        </div>
      </div>

      <div class="el-card is-always-shadow table-card" v-loading="loading" element-loading-text="加载中...">
        <div class="el-card__body">
          <el-table v-if="tableData.length" border stripe max-height="620" style="width: 100%" :data="tableData" :header-cell-style="{ background: '#eef1f6', color: '#606266' }" show-overflow-tooltip>
            <!-- 订单明细 (ERP) -->
            <el-table-column prop="订单明细_订单编号" label="订单编号" min-width="150" />
            <el-table-column prop="订单明细_订单日期" label="订单日期" min-width="120" />
            <el-table-column prop="订单明细_客户名称" label="客户名称" min-width="200" />
            <el-table-column prop="订单明细_审核日期" label="审核日期" min-width="120" />
            <el-table-column prop="订单明细_确定交期" label="确定交期" min-width="120" />
            <el-table-column prop="订单明细_创建日期" label="创建日期" min-width="120" />
            <!-- 排产备份 (APS) -->
            <el-table-column prop="排产备份_工单编号" label="排产工单编号" min-width="180" />
            <el-table-column prop="排产备份_计划开始时间" label="排产计划开始时间" min-width="160" />
            <el-table-column prop="排产备份_计划完成时间" label="排产计划完成时间" min-width="160" />
            <el-table-column prop="排产备份_计划产量" label="排产计划产量" min-width="100" align="right" />
            <el-table-column prop="排产备份_确定交期" label="排产确定交期" min-width="140" />
            <el-table-column prop="排产备份_料品编码" label="排产料品编码" min-width="140" />
            <el-table-column prop="排产备份_料品名称" label="排产料品名称" min-width="160" />
            <el-table-column prop="排产备份_规格型号" label="排产规格型号" min-width="160" />
            <el-table-column prop="排产备份_生产车间" label="排产生产车间" min-width="140" />
            <!-- 派工单 (PGD_WorkOrder) -->
            <el-table-column prop="派工单_工单编号" label="派工工单编号" min-width="180" />
            <el-table-column prop="派工单_订单批号" label="订单批号" min-width="200" />
            <el-table-column prop="派工单_生产车间" label="生产车间" min-width="140" />
            <el-table-column prop="派工单_料品编码" label="料品编码" min-width="140" />
            <el-table-column prop="派工单_料品名称" label="料品名称" min-width="160" />
            <el-table-column prop="派工单_规格型号" label="规格型号" min-width="160" />
            <el-table-column prop="派工单_生产线编号" label="生产线编号" min-width="120" />
            <el-table-column prop="派工单_计划开始时间" label="计划开始时间" min-width="160" />
            <el-table-column prop="派工单_计划完成时间" label="计划完成时间" min-width="160" />
            <el-table-column prop="派工单_计划产量" label="计划产量" min-width="100" align="right">
              <template #default="scope"><span>{{ formatNumber(scope.row.派工单_计划产量) }}</span></template>
            </el-table-column>
            <el-table-column prop="派工单_确定交期" label="确定交期" min-width="140" />
            <!-- 报工 (FinishedQty) -->
            <el-table-column prop="报工_报工来源" label="报工来源" min-width="140" />
            <el-table-column prop="报工_FinishedDate" label="报工时间" min-width="160" />
            <el-table-column prop="报工_EachFinishedQty" label="报工数量" min-width="100" align="right">
              <template #default="scope"><span>{{ formatNumber(scope.row.报工_EachFinishedQty) }}</span></template>
            </el-table-column>
            <el-table-column prop="报工_scrapQty" label="报废数量" min-width="100" align="right">
              <template #default="scope"><span>{{ formatNumber(scope.row.报工_scrapQty) }}</span></template>
            </el-table-column>
            <el-table-column prop="报工_repairQty" label="返修数量" min-width="100" align="right">
              <template #default="scope"><span>{{ formatNumber(scope.row.报工_repairQty) }}</span></template>
            </el-table-column>
            <el-table-column prop="报工_ResName" label="报工人/线号" min-width="120" />
          </el-table>
          <el-empty v-else-if="hasSearched && !loading" description="暂无数据" />
          <div class="pagination-row" v-if="hasSearched">
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
  name: 'WorkshopReportDetailJobOrder',
  components: { Layout },
  data() {
    return {
      breadcrumbItems: ['报工', '车间报工详情', '基于派工单查订单和报工'],
      filters: { startDate: '', endDate: '', workOrderId: '', personName: '', orderNumbers: '' },
      tableData: [],
      total: 0,
      currentPage: 1,
      pageSize: 100,
      loading: false,
      exporting: false,
      hasSearched: false,
      sidebarMenus: []
    }
  },
  created() {
    eventBus.$on('sidebar-Menus-Updated', (menus) => { this.sidebarMenus = menus; this.generateBreadcrumb(this.$route.path) })
  },
  watch: { $route(v) { this.generateBreadcrumb(v.path) } },
  methods: {
    generateBreadcrumb(path) {
      try {
        const find = (menus, p) => {
          for (const m of menus) {
            for (const s of (m.children || [])) {
              for (const gc of (s.children || [])) {
                for (const c of (gc.children || [])) {
                  if (c.path === p) return [s.name, gc.name, c.name]
                }
                if (gc.path === p) return [s.name, gc.name]
              }
            }
          }
          return ['报工', '车间报工详情', '基于派工单查订单和报工']
        }
        const r = find(this.sidebarMenus, '/' + path.split('/').filter(p => p).join('/'))
        this.breadcrumbItems = Array.isArray(r) ? r : [r]
      } catch { this.breadcrumbItems = ['报工', '车间报工详情', '基于派工单查订单和报工'] }
    },
    formatNumber(val) {
      if (val == null || val === '') return 0
      return Number(val).toLocaleString()
    },
    async handleSearch() {
      this.loading = true
      this.hasSearched = true
      try {
        const res = await axios.get('/api/workshopReportDetail/JobOrder', {
          params: {
            ...this.filters,
            page: this.currentPage,
            page_size: this.pageSize
          }
        })
        if (res.data.status === 'success') {
          this.tableData = res.data.data
          this.total = res.data.total
        } else {
          this.$message.error(res.data.detail || '查询失败')
          this.tableData = []
          this.total = 0
        }
      } catch { this.$message.error('查询失败') } finally { this.loading = false }
    },
    handlePageChange(page) { this.currentPage = page; this.handleSearch() },
    handleSizeChange(size) { this.pageSize = size; this.currentPage = 1; this.handleSearch() },
    async exportData() {
      this.exporting = true
      try {
        const res = await axios.get('/api/workshopReportDetail/JobOrder/export', {
          params: this.filters,
          responseType: 'blob'
        })
        const cd = res.headers['content-disposition']
        let fname = `基于派工单查订单和报工_${Date.now()}.xlsx`
        if (cd) {
          const m = cd.match(/filename\*=UTF-8''(.+)/)
          if (m) fname = decodeURIComponent(m[1])
          else { const p = cd.split('filename=')[1]; if (p) fname = p.replace(/"/g, '') }
        }
        const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        const link = document.createElement('a')
        link.href = URL.createObjectURL(blob)
        link.download = fname
        link.click()
        URL.revokeObjectURL(link.href)
        this.$message.success('导出成功')
      } catch { this.$message.error('导出失败') } finally { this.exporting = false }
    },
    resetFilters() {
      this.filters = { startDate: '', endDate: '', workOrderId: '', personName: '', orderNumbers: '' }
      this.tableData = []
      this.total = 0
      this.currentPage = 1
      this.hasSearched = false
    }
  }
}
</script>

<style scoped>
.report-container { padding: 0; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; padding-top: 10px; padding-bottom: 5px; }
.summary-row { display: flex; justify-content: space-between; align-items: center; color: #303133; }
.table-card { min-height: 100px; }
.mb-4 { margin-bottom: 16px; }
.el-form-item { margin-bottom: 0; width: 100%; }
.pagination-row { padding: 10px 0; display: flex; justify-content: center; }
</style>
