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
                <el-form-item label="计划开始时间">
                  <el-date-picker
                    v-model="filters.scheduleDate"
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

      <div class="chart-row mb-4">
        <div class="el-card is-always-shadow chart-card">
          <div class="el-card__body">
            <div ref="pieChart" class="pie-chart"></div>
          </div>
        </div>
      </div>

      <div class="el-card is-always-shadow mb-4 summary-card">
        <div class="el-card__body summary-row">
          <div class="summary-left">
            <span class="summary-label">各车间欠料数:</span>
            <span v-for="(item, idx) in pieData" :key="item.name" class="summary-tag">
              <span class="color-dot" :style="{ background: pieColors[idx % pieColors.length] }"></span>
              {{ item.name }}: <b>{{ formatNumber(item.value) }}</b>
            </span>
          </div>
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
            <el-table-column prop="vFactory" label="车间" min-width="120" show-overflow-tooltip />
            <el-table-column prop="产品系列" label="产品系列" min-width="120" show-overflow-tooltip />
            <el-table-column prop="产品名称" label="产品名称" min-width="180" show-overflow-tooltip />
            <el-table-column prop="产品描述" label="规格型号" min-width="180" show-overflow-tooltip />
            <el-table-column prop="OrderNumber" label="订单号" min-width="150" show-overflow-tooltip />
            <el-table-column prop="Customer" label="客户" min-width="120" show-overflow-tooltip />
            <el-table-column prop="ScheduledStartDate" label="计划开始时间" min-width="110" show-overflow-tooltip />
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
import * as echarts from 'echarts'
import axios from 'axios'
import Layout from '@/components/Layout.vue'

export default {
  name: 'LackMaterial',
  components: {
    Layout
  },
  data() {
    return {
      breadcrumbItems: ['报表页面', '各车间欠料'],
      filters: {
        productSeries: '',
        productDesc: '',
        scheduleDate: []
      },
      seriesOptions: [],
      descOptions: [],
      tableData: [],
      allData: [],
      loading: false,
      currentPage: 1,
      pageSize: 50,
      total: 0,
      pieData: [],
      pieInstance: null,
      pieColors: ['#003A6B', '#005B9F', '#007CD4', '#3D9EF9', '#7ABEFD', '#B8DFFF', '#DBEAFE', '#F0C040', '#E68A2E', '#C0504D']
    }
  },
  created() {
    this.loadDropdownOptions()
    this.searchData(false)
  },
  mounted() {
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
    if (this.pieInstance) {
      this.pieInstance.dispose()
      this.pieInstance = null
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
        if (Array.isArray(this.filters.scheduleDate) && this.filters.scheduleDate.length === 2) {
          params.start_date = this.filters.scheduleDate[0]
          params.end_date = this.filters.scheduleDate[1]
        }

        const response = await axios.get('/api/lackMaterial', { params })

        if (response.data?.status === 'success') {
          this.allData = response.data.data?.details || []
          this.pieData = response.data.data?.pie || []
          this.total = this.allData.length
          this.updateTableData()
          this.$nextTick(() => {
            this.renderPieChart()
          })
        } else {
          this.$message.error('数据获取失败')
        }
      } catch (error) {
        console.error('获取各车间欠料数据失败:', error)
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
    renderPieChart() {
      if (!this.$refs.pieChart) return
      if (!this.pieInstance) {
        this.pieInstance = echarts.init(this.$refs.pieChart)
      }
      const option = {
        color: this.pieColors,
        title: {
          text: '各车间欠料占比',
          left: 'center',
          textStyle: { fontSize: 16, fontWeight: 'bold' }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          bottom: 10,
          itemWidth: 14,
          itemHeight: 14
        },
        series: [
          {
            name: '欠料数',
            type: 'pie',
            radius: '60%',
            avoidLabelOverlap: false,
            itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
            label: {
              show: true,
              formatter: function (params) {
                return params.name + '\n' + params.value.toLocaleString() + ' (' + params.percent + '%)'
              }
            },
            emphasis: {
              label: { show: true, fontSize: 14, fontWeight: 'bold' }
            },
            data: this.pieData.map((item, index) => ({
              ...item,
              itemStyle: {
                color: this.pieColors[index % this.pieColors.length]
              }
            }))
          }
        ]
      }
      this.pieInstance.setOption(option, true)
    },
    handleResize() {
      if (this.pieInstance) {
        this.pieInstance.resize()
      }
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
        scheduleDate: []
      }
      this.searchData(true)
    },
    async loadDropdownOptions() {
      try {
        const [seriesRes, descRes] = await Promise.all([
          axios.get('/api/lackMaterial/suggestions', { params: { field: 'product_series', q: '' } }),
          axios.get('/api/lackMaterial/suggestions', { params: { field: 'product_desc', q: '' } })
        ])
        if (seriesRes.data?.status === 'success') {
          this.seriesOptions = (seriesRes.data.data || []).map(i => i.value)
        }
        if (descRes.data?.status === 'success') {
          this.descOptions = (descRes.data.data || []).map(i => i.value)
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

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 10px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #303133;
}

.summary-left {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.summary-label {
  white-space: nowrap;
  margin-right: 4px;
}

.summary-tag {
  font-size: 13px;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.color-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.chart-row {
  display: flex;
}

.chart-card {
  width: 100%;
}

.chart-card .el-card__body {
  padding: 10px;
}

.pie-chart {
  width: 100%;
  height: 450px;
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
