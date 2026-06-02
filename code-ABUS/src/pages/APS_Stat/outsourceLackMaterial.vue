<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="report-container">
      <div class="el-card is-always-shadow mb-4">
        <div class="el-card__body">
          <el-form @submit.native.prevent="searchData(true)" label-width="100px">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="产品系列">
                  <el-select
                    v-model="filters.productSeries"
                    placeholder="选择产品系列"
                    filterable
                    clearable
                  >
                    <el-option
                      v-for="option in seriesOptions"
                      :key="option"
                      :label="option"
                      :value="option"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="规格型号">
                  <el-select
                    v-model="filters.productDesc"
                    placeholder="选择规格型号"
                    filterable
                    clearable
                  >
                    <el-option
                      v-for="option in descOptions"
                      :key="option"
                      :label="option"
                      :value="option"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="车间">
                  <el-select
                    v-model="filters.vFactory"
                    placeholder="选择车间"
                    filterable
                    clearable
                  >
                    <el-option
                      v-for="option in workshopOptions"
                      :key="option"
                      :label="option"
                      :value="option"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="外协项目1">
                  <el-select
                    v-model="filters.waisProject"
                    placeholder="选择外协项目1"
                    filterable
                    clearable
                  >
                    <el-option
                      v-for="option in waisOptions"
                      :key="option"
                      :label="option"
                      :value="option"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="确定交期">
                  <el-date-picker
                    v-model="filters.deliveryDate"
                    type="daterange"
                    :unlink-panels="true"
                    range-separator="-"
                    start-placeholder="开始日期"
                    end-placeholder="结束日期"
                    value-format="yyyy-MM-dd"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <div class="form-actions">
              <el-button type="primary" :loading="loading" @click="searchData(true)">查询</el-button>
              <el-button @click="resetFilters">重置</el-button>
            </div>
          </el-form>
        </div>
      </div>

      <div v-if="summaryData.length" class="el-card is-always-shadow mb-4">
        <div class="el-card__body">
          <div class="stats-title">车间+产品系列 欠料汇总</div>
          <el-table
            :data="paginatedSummary"
            border
            stripe
            style="width: 100%"
            :header-cell-style="{ background: '#eef1f6', color: '#606266' }"
            show-summary
            :summary-method="getSummarySummaries"
          >
            <el-table-column type="index" label="序号" width="60" align="center" :index="summaryIndex" />
            <el-table-column prop="vFactory" label="车间" min-width="150" show-overflow-tooltip />
            <el-table-column prop="产品系列" label="产品系列" min-width="150" show-overflow-tooltip />
            <el-table-column prop="欠料数" label="欠料数" min-width="120" align="right">
              <template #default="scope">
                <span style="color:#e6a23c;font-weight:bold">{{ formatNumber(scope.row.欠料数) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="记录数" label="记录数" width="80" align="center" />
          </el-table>
          <div class="pagination-row">
            <el-pagination
              background
              layout="total, sizes, prev, pager, next, jumper"
              :total="summaryData.length"
              :current-page="summaryPage"
              :page-sizes="[10, 20, 50, 100]"
              :page-size="summaryPageSize"
              @size-change="handleSummarySizeChange"
              @current-change="handleSummaryPageChange"
            />
          </div>
        </div>
      </div>

      <div class="el-card is-always-shadow mb-4 summary-card">
        <div class="el-card__body summary-row">
          <span>总条数: <b>{{ total }}</b></span>
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
            <el-table-column type="index" label="序号" width="60" align="center" />
            <el-table-column prop="外协项目1" label="外协项目1" min-width="100" show-overflow-tooltip />
            <el-table-column prop="vFactory" label="车间" min-width="120" show-overflow-tooltip />
            <el-table-column prop="产品系列" label="产品系列" min-width="100" show-overflow-tooltip />
            <el-table-column prop="产品名称" label="产品名称" min-width="180" show-overflow-tooltip />
            <el-table-column prop="产品描述" label="规格型号" min-width="150" show-overflow-tooltip />
            <el-table-column prop="OrderNumber" label="订单号" min-width="150" show-overflow-tooltip />
            <el-table-column prop="Customer" label="客户" min-width="100" show-overflow-tooltip />
            <el-table-column prop="确定交期" label="确定交期" min-width="100" show-overflow-tooltip />
            <el-table-column prop="TotalRequiredQty" label="总需求" min-width="100" align="right">
              <template #default="scope">
                <span>{{ formatNumber(scope.row.TotalRequiredQty) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="IssuedQty" label="已发料" min-width="100" align="right">
              <template #default="scope">
                <span>{{ formatNumber(scope.row.IssuedQty) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="LackQty" label="欠料数" min-width="100" align="right">
              <template #default="scope">
                <span style="color:#e6a23c">{{ formatNumber(scope.row.LackQty) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="资源名称" label="资源名称" min-width="120" show-overflow-tooltip />
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
              @size-change="handlePageSizeChange"
              @current-change="handlePageChange"
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

export default {
  name: 'OutsourceLackMaterial',
  components: {
    Layout
  },
  data() {
    return {
      breadcrumbItems: ['报表页面', '外协欠料明细'],
      filters: {
        productSeries: '',
        productDesc: '',
        vFactory: '',
        waisProject: '',
        deliveryDate: []
      },
      seriesOptions: [],
      descOptions: [],
      workshopOptions: [],
      waisOptions: [],
      summaryData: [],
      summaryPage: 1,
      summaryPageSize: 10,
      tableData: [],
      allData: [],
      loading: false,
      currentPage: 1,
      pageSize: 50,
      total: 0
    }
  },
  created() {
    this.loadDropdownOptions()
    this.searchData(false)
  },
  computed: {
    paginatedSummary() {
      const start = (this.summaryPage - 1) * this.summaryPageSize
      return this.summaryData.slice(start, start + this.summaryPageSize)
    },
    summaryIndex() {
      return (this.summaryPage - 1) * this.summaryPageSize + 1
    }
  },
  methods: {
    formatNumber(value) {
      if (value === null || value === undefined || value === '') {
        return '-'
      }
      return Number(value).toLocaleString()
    },
    async searchData(resetPage = true) {
      if (resetPage) {
        this.currentPage = 1
      }
      this.loading = true
      try {
        const params = {}
        if (this.filters.productSeries) {
          params.product_series = this.filters.productSeries.trim()
        }
        if (this.filters.productDesc) {
          params.product_desc = this.filters.productDesc.trim()
        }
        if (this.filters.waisProject) {
          params.外协项目1 = this.filters.waisProject
        }
        if (this.filters.vFactory) {
          params.vFactory = this.filters.vFactory
        }
        if (Array.isArray(this.filters.deliveryDate) && this.filters.deliveryDate.length === 2) {
          params.start_date = this.filters.deliveryDate[0]
          params.end_date = this.filters.deliveryDate[1]
        }

        const response = await axios.get('/api/outsourceLackMaterial', { params })

        if (response.data?.status === 'success') {
          this.allData = response.data.data || []
          this.total = response.data.total_count || this.allData.length
          this.loadSummary()
          this.updateTableData()
        } else {
          this.$message.error('数据获取失败')
        }
      } catch (error) {
        console.error('获取外协欠料明细数据失败:', error)
        this.$message.error('数据加载失败，请检查网络连接')
      } finally {
        this.loading = false
      }
    },
    updateTableData() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      this.tableData = this.allData.slice(start, end)
    },
    handlePageChange(page) {
      this.currentPage = page
      this.updateTableData()
    },
    handlePageSizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
      this.updateTableData()
    },
    resetFilters() {
      this.filters = {
        productSeries: '',
        productDesc: '',
        vFactory: '',
        waisProject: '',
        deliveryDate: []
      }
      this.searchData(true)
    },
    loadSummary() {
      const map = {}
      this.allData.forEach(item => {
        const key = (item.vFactory || '未知车间') + '|' + (item.产品系列 || '未知系列')
        if (!map[key]) {
          map[key] = { vFactory: item.vFactory || '未知车间', 产品系列: item.产品系列 || '未知系列', 欠料数: 0, 记录数: 0 }
        }
        map[key].欠料数 += item.LackQty || 0
        map[key].记录数++
      })
      this.summaryData = Object.values(map).sort((a, b) => b.欠料数 - a.欠料数)
      this.summaryPage = 1
    },
    handleSummaryPageChange(page) {
      this.summaryPage = page
    },
    handleSummarySizeChange(size) {
      this.summaryPageSize = size
      this.summaryPage = 1
    },
    getSummarySummaries({ columns, data }) {
      const sums = []
      columns.forEach((column, index) => {
        if (index === 0) {
          sums[index] = '合计'
          return
        }
        if (column.property === 'vFactory' || column.property === '产品系列') {
          sums[index] = ''
          return
        }
        if (column.property === '欠料数') {
          const total = data.reduce((acc, item) => acc + (item.欠料数 || 0), 0)
          sums[index] = total.toLocaleString()
          return
        }
        if (column.property === '记录数') {
          const total = data.reduce((acc, item) => acc + (item.记录数 || 0), 0)
          sums[index] = total.toLocaleString()
          return
        }
        sums[index] = ''
      })
      return sums
    },
    async loadDropdownOptions() {
      try {
        const [seriesRes, descRes, waisRes, workshopRes] = await Promise.all([
          axios.get('/api/outsourceLackMaterial/suggestions', { params: { field: 'product_series', q: '' } }),
          axios.get('/api/outsourceLackMaterial/suggestions', { params: { field: 'product_desc', q: '' } }),
          axios.get('/api/outsourceLackMaterial/suggestions', { params: { field: 'wais项目1', q: '' } }),
          axios.get('/api/outsourceLackMaterial/suggestions', { params: { field: 'vFactory', q: '' } })
        ])
        if (seriesRes.data?.status === 'success') {
          this.seriesOptions = (seriesRes.data.data || []).map(i => i.value)
        }
        if (descRes.data?.status === 'success') {
          this.descOptions = (descRes.data.data || []).map(i => i.value)
        }
        if (waisRes.data?.status === 'success') {
          this.waisOptions = (waisRes.data.data || []).map(i => i.value)
        }
        if (workshopRes.data?.status === 'success') {
          this.workshopOptions = (workshopRes.data.data || []).map(i => i.value)
        }
      } catch {
        // ignore
      }
    }
  }
}
</script>

<style scoped>
.report-container {
  padding: 0;
}

.stats-title {
  font-size: 15px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 12px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 10px;
}

.summary-row {
  display: flex;
  justify-content: flex-end;
  color: #303133;
}

.table-card {
  min-height: 100px;
}

.pagination-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.mb-4 {
  margin-bottom: 16px;
}
</style>
