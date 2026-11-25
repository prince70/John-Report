<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="report-container">
      <div class="el-card is-always-shadow mb-4">
        <div class="el-card__body">
          <el-form @submit.native.prevent="searchInventory" label-width="100px">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="日期">
                  <el-date-picker
                    v-model="filters.date"
                    type="date"
                    placeholder="选择日期"
                    value-format="yyyy-MM-dd"
                    :picker-options="datePickerOptions"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="区域">
                  <el-select v-model="filters.area" clearable placeholder="全部区域" style="width: 100%">
                    <el-option
                      v-for="area in areas"
                      :key="area"
                      :label="area"
                      :value="area"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="料品编码">
                  <el-input
                    v-model.trim="filters.item_no"
                    clearable
                    placeholder="输入半成品编码"
                    @keyup.enter.native="searchInventory"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="只看有库存">
                  <el-switch v-model="filters.only_nonzero" />
                </el-form-item>
              </el-col>
            </el-row>
            <div class="form-actions">
              <el-button type="primary" :loading="loading" @click="searchInventory">查询</el-button>
              <el-button @click="resetFilters">重置</el-button>
              <el-button type="success" :loading="exportLoading" @click="exportExcel">导出Excel</el-button>
              <el-button type="warning" :loading="refreshLoading" @click="refreshData">刷新数据</el-button>
            </div>
          </el-form>
        </div>
      </div>

      <div class="el-card is-always-shadow mb-4 summary-card">
        <div class="el-card__body summary-row">
          <div class="summary-item">
            <span>行数</span>
            <b>{{ totals.rows }}</b>
          </div>
          <div class="summary-item">
            <span>期初</span>
            <b>{{ formatNumber(totals.opening_qty) }}</b>
          </div>
          <div class="summary-item">
            <span>当日流入</span>
            <b>{{ formatNumber(totals.in_qty) }}</b>
          </div>
          <div class="summary-item">
            <span>当日流出</span>
            <b>{{ formatNumber(totals.out_qty) }}</b>
          </div>
          <div class="summary-item">
            <span>累计流入</span>
            <b>{{ formatNumber(totals.cum_in_qty) }}</b>
          </div>
          <div class="summary-item">
            <span>累计流出</span>
            <b>{{ formatNumber(totals.cum_out_qty) }}</b>
          </div>
          <div class="summary-item">
            <span>实时库存</span>
            <b>{{ formatNumber(totals.stock_qty) }}</b>
          </div>
        </div>
      </div>

      <div class="el-card is-always-shadow table-card">
        <div class="el-card__body">
          <el-table
            v-if="inventoryData.length"
            :data="inventoryData"
            border
            stripe
            max-height="650"
            style="width: 100%"
            :header-cell-style="{ background: '#eef1f6', color: '#606266' }"
          >
            <el-table-column prop="inventory_date" label="日期" min-width="100" align="center" />
            <el-table-column prop="area" label="区域" min-width="120" align="center" />
            <el-table-column prop="item_no" label="料品编码" min-width="140" align="center" />
            <el-table-column prop="model_spec" label="型号规格" min-width="160" show-overflow-tooltip />
            <el-table-column prop="opening_qty" label="期初" min-width="100" align="right">
              <template #default="scope">
                {{ formatNumber(scope.row.opening_qty) }}
              </template>
            </el-table-column>
            <el-table-column prop="in_qty" label="当日流入" min-width="100" align="right">
              <template #default="scope">
                {{ formatNumber(scope.row.in_qty) }}
              </template>
            </el-table-column>
            <el-table-column prop="out_qty" label="当日流出" min-width="100" align="right">
              <template #default="scope">
                {{ formatNumber(scope.row.out_qty) }}
              </template>
            </el-table-column>
            <el-table-column prop="cum_in_qty" label="累计流入" min-width="100" align="right">
              <template #default="scope">
                {{ formatNumber(scope.row.cum_in_qty) }}
              </template>
            </el-table-column>
            <el-table-column prop="cum_out_qty" label="累计流出" min-width="100" align="right">
              <template #default="scope">
                {{ formatNumber(scope.row.cum_out_qty) }}
              </template>
            </el-table-column>
            <el-table-column prop="stock_qty" label="实时库存" min-width="100" align="right">
              <template #default="scope">
                {{ formatNumber(scope.row.stock_qty) }}
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-else description="暂无数据" />
        </div>
      </div>

      <div class="el-card is-always-shadow table-card">
        <div class="el-card__body">
          <h3 class="section-title">当日动作汇总</h3>
          <el-table
            v-if="movementData.length"
            :data="movementData"
            border
            stripe
            max-height="400"
            style="width: 100%"
            :header-cell-style="{ background: '#eef1f6', color: '#606266' }"
          >
            <el-table-column prop="movement_date" label="日期" min-width="100" align="center" />
            <el-table-column prop="area" label="区域" min-width="120" align="center" />
            <el-table-column prop="item_no" label="料品编码" min-width="140" align="center" />
            <el-table-column prop="source" label="来源" min-width="140" align="center" />
            <el-table-column prop="in_qty" label="流入" min-width="100" align="right">
              <template #default="scope">
                {{ formatNumber(scope.row.in_qty) }}
              </template>
            </el-table-column>
            <el-table-column prop="out_qty" label="流出" min-width="100" align="right">
              <template #default="scope">
                {{ formatNumber(scope.row.out_qty) }}
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-else description="暂无当日动作" />
        </div>
      </div>
    </div>
  </Layout>
</template>

<script>
import axios from 'axios'
import Layout from '@/components/Layout.vue'

export default {
  name: 'AttireInventory',
  components: {
    Layout
  },
  data() {
    return {
      breadcrumbItems: ['报表页面', '装嵌车间铝门锁区实时库存'],
      loading: false,
      exportLoading: false,
      refreshLoading: false,
      areas: [],
      inventoryData: [],
      movementData: [],
      totals: {
        rows: 0,
        opening_qty: 0,
        in_qty: 0,
        out_qty: 0,
        cum_in_qty: 0,
        cum_out_qty: 0,
        stock_qty: 0
      },
      filters: {
        date: '',
        area: '',
        item_no: '',
        only_nonzero: true
      },
      datePickerOptions: {
        disabledDate(time) {
          return time.getTime() > Date.now()
        }
      }
    }
  },
  created() {
    this.initializePage()
  },
  methods: {
    async initializePage() {
      try {
        await this.loadOptions()
        const today = new Date().toISOString().slice(0, 10)
        this.filters.date = today
        await this.searchInventory()
      } catch (error) {
        console.error('初始化页面失败:', error)
        this.$message.error('初始化页面失败')
      }
    },
    async loadOptions() {
      try {
        const { data } = await axios.get('/api/attireInventory/options')
        if (data.ok) {
          this.areas = data.areas || []
          this.filters.date = data.latest_date || new Date().toISOString().slice(0, 10)
        }
      } catch (error) {
        console.error('加载选项失败:', error)
        this.$message.error('加载选项失败')
      }
    },
    async searchInventory() {
      if (this.loading) return
      this.loading = true
      try {
        const params = {
          target_date: this.filters.date,
          area: this.filters.area,
          item_no: this.filters.item_no,
          only_nonzero: this.filters.only_nonzero ? '1' : '0'
        }
        const { data } = await axios.get('/api/attireInventory/inventory', { params })
        if (data.ok) {
          this.inventoryData = data.rows || []
          this.totals = data.totals || this.totals
          await this.loadMovements()
        } else {
          this.$message.error(data.error || '查询库存失败')
        }
      } catch (error) {
        console.error('查询库存失败:', error)
        this.$message.error(error.response?.data?.detail || '查询库存失败')
      } finally {
        this.loading = false
      }
    },
    async loadMovements() {
      try {
        const params = {
          target_date: this.filters.date,
          area: this.filters.area,
          item_no: this.filters.item_no
        }
        const { data } = await axios.get('/api/attireInventory/movements', { params })
        if (data.ok) {
          this.movementData = data.rows || []
        } else {
          this.$message.error(data.error || '查询动作汇总失败')
        }
      } catch (error) {
        console.error('查询动作汇总失败:', error)
        this.$message.error(error.response?.data?.detail || '查询动作汇总失败')
      }
    },
    async exportExcel() {
      if (this.exportLoading) return
      this.exportLoading = true
      try {
        const params = {
          target_date: this.filters.date,
          area: this.filters.area,
          item_no: this.filters.item_no,
          only_nonzero: this.filters.only_nonzero ? '1' : '0'
        }
        const response = await axios.get('/api/attireInventory/export', {
          params,
          responseType: 'blob'
        })

        let filename = `锁体实时库存_${this.filters.date}.xlsx`
        const disposition = response.headers['content-disposition'] || ''
        const utf8Match = disposition.match(/filename\*=UTF-8''([^;]+)/i)
        const normalMatch = disposition.match(/filename="?([^";]+)"?/i)
        if (utf8Match && utf8Match[1]) {
          filename = decodeURIComponent(utf8Match[1])
        } else if (normalMatch && normalMatch[1]) {
          filename = normalMatch[1]
        }

        const blob = new Blob([response.data], {
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        this.$message.success('Excel导出成功')
      } catch (error) {
        console.error('导出Excel失败:', error)
        this.$message.error(error.response?.data?.detail || '导出Excel失败')
      } finally {
        this.exportLoading = false
      }
    },
    async refreshData() {
      if (this.refreshLoading) return
      this.refreshLoading = true
      try {
        const { data } = await axios.post('/api/attireInventory/refresh')
        if (data.ok) {
          this.$message.success(`刷新完成：库存汇总 ${data.inventory_rows} 行`)
          await this.loadOptions()
          await this.searchInventory()
        } else {
          this.$message.error(data.error || '刷新数据失败')
        }
      } catch (error) {
        console.error('刷新数据失败:', error)
        this.$message.error(error.response?.data?.detail || '刷新数据失败')
      } finally {
        this.refreshLoading = false
      }
    },
    resetFilters() {
      this.filters = {
        date: new Date().toISOString().slice(0, 10),
        area: '',
        item_no: '',
        only_nonzero: true
      }
      this.searchInventory()
    },
    formatNumber(value) {
      const num = Number(value || 0)
      return num.toLocaleString('zh-CN', { maximumFractionDigits: 2 })
    }
  }
}
</script>

<style scoped>
.report-container { padding: 0; }
.mb-4 { margin-bottom: 16px; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; padding-top: 10px; }
.summary-row { display: flex; justify-content: space-around; color: #303133; flex-wrap: wrap; }
.summary-item { display: flex; flex-direction: column; align-items: center; padding: 8px 16px; }
.summary-item span { color: #909399; font-size: 13px; margin-bottom: 4px; }
.summary-item b { font-size: 18px; font-weight: 700; color: #303133; }
.section-title { font-size: 16px; font-weight: 600; color: #303133; margin: 0 0 16px 0; padding: 0 0 8px 0; border-bottom: 1px solid #ebeef5; }
.summary-card .el-card__body { padding: 8px 14px; }
.table-card .el-card__body { padding: 10px 14px; }
.table-card + .table-card { margin-top: 16px; }
@media (max-width: 768px) {
  .summary-row { justify-content: flex-start; }
  .summary-item { flex: 0 0 50%; box-sizing: border-box; }
}
</style>
