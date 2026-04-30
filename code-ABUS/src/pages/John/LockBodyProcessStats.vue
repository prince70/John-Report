<!-- 2026-04-22 锁体C分区域库存计算 -->
<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="report-container">
      <div class="el-card is-always-shadow mb-4 filter-card">
        <div class="el-card__body">
          <el-form @submit.native.prevent="searchReport(true)" label-width="90px">
            <el-row :gutter="20">
              <el-col :xs="24" :sm="8">
                <el-form-item label="订单批号">
                  <el-input
                    v-model.trim="filters.orderNo"
                    clearable
                    placeholder="请输入订单批号"
                    @keyup.enter.native="searchReport(true)"
                  />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item label="料品名称">
                  <el-input
                    v-model.trim="filters.itemName"
                    clearable
                    placeholder="请输入料品名称"
                    @keyup.enter.native="searchReport(true)"
                  />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item label="料品编码">
                  <el-input
                    v-model.trim="filters.itemCode"
                    clearable
                    placeholder="请输入料品编码"
                    @keyup.enter.native="searchReport(true)"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <div class="form-actions">
              <el-button @click="resetFilters">重置</el-button>
              <el-button type="success" :loading="exportLoading" @click="exportExcel">导出Excel</el-button>
              <el-button type="primary" :loading="loading" @click="searchReport(true)">查询</el-button>
            </div>
          </el-form>
        </div>
      </div>

      <div class="el-card is-always-shadow mb-4 summary-card">
        <div class="el-card__body summary-row">
          <span>显示条数: <b>{{ filteredTotal }}</b> / 总条数: <b>{{ total }}</b></span>
        </div>
      </div>

      <div v-if="showAllDataSummary && allDataSummary && allFilteredData.length > 0" class="el-card is-always-shadow mb-4 summary-form">
        <div class="el-card__body">
          <div class="summary-header">
            <div class="summary-form-title">汇总</div>
            <div class="summary-inventory-total">
              <span class="total-label">可用库存总和：</span>
              <span class="total-value">{{ formatNumber(totalAvailableInventory) }}&nbsp;</span>
              <el-tooltip content="可用库存总和 + 后工序-拣锁体的流转量 = 流转量" placement="top">
               <i class="el-icon-info tip-icon"></i>
               </el-tooltip>
            </div>
          </div>
          <el-table :data="[allDataSummary]" border stripe size="small" :show-header="true">
            <el-table-column label="流转" align="center">
              <el-table-column prop="流转_完成量" label="完成量" min-width="100" align="right">
                <template #default="scope">
                  <span>{{ formatNumber(scope.row.流转_完成量) }}</span>
                </template>
              </el-table-column>
            </el-table-column>
            <el-table-column label="自动机" align="center">
              <el-table-column prop="自动机_完成量" label="完成量" min-width="100" align="right">
                <template #default="scope">
                  <span>{{ formatNumber(scope.row.自动机_完成量) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="自动机_可用库存" label="可用库存" min-width="100" align="right">
                <template #default="scope">
                  <span>{{ formatNumber(scope.row.自动机_可用库存) }}</span>
                </template>
              </el-table-column>
            </el-table-column>
            <el-table-column label="加工线" align="center">
              <el-table-column prop="加工线_完成量" label="完成量" min-width="100" align="right">
                <template #default="scope">
                  <span>{{ formatNumber(scope.row.加工线_完成量) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="加工线_可用库存" label="可用库存" min-width="100" align="right">
                <template #default="scope">
                  <span>{{ formatNumber(scope.row.加工线_可用库存) }}</span>
                </template>
              </el-table-column>
            </el-table-column>
            <el-table-column label="后工序-拣锁体" align="center">
              <el-table-column prop="拣锁体_完成量" label="完成量" min-width="100" align="right">
                <template #default="scope">
                  <span>{{ formatNumber(scope.row.拣锁体_完成量) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="拣锁体_可用库存" label="可用库存" min-width="100" align="right">
                <template #default="scope">
                  <span>{{ formatNumber(scope.row.拣锁体_可用库存) }}</span>
                </template>
              </el-table-column>
            </el-table-column>
          </el-table>
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
            :show-summary="true"
            :summary-method="getPageSummaries"
          >
            <el-table-column type="index" label="序号" width="60" align="center" />
            
            <el-table-column prop="订单批号" label="订单批号" min-width="150" show-overflow-tooltip />
            
            <el-table-column prop="确定交期" label="确定交期" min-width="120" align="center" show-overflow-tooltip>
              <template #default="scope">
                <span>{{ formatDate(scope.row.确定交期) }}</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="料品名称" label="料品名称" min-width="180" show-overflow-tooltip />
            
            <el-table-column prop="规格型号" label="规格型号" min-width="150" show-overflow-tooltip />
            
            <el-table-column prop="计划产量" label="计划产量" min-width="100" align="right" show-overflow-tooltip>
              <template #default="scope">
                <span>{{ formatNumber(scope.row.计划产量) }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="流转" align="center">
              <el-table-column prop="流转_完成量" label="完成量" min-width="100" align="right" show-overflow-tooltip>
                <template #default="scope">
                  <span>{{ formatNumber(scope.row.流转_完成量) }}</span>
                </template>
              </el-table-column>
            </el-table-column>
            
            <el-table-column label="自动机" align="center">
              <el-table-column prop="自动机_完成量" label="完成量" min-width="100" align="right" show-overflow-tooltip>
                <template #default="scope">
                  <span>{{ formatNumber(scope.row.自动机_完成量) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="自动机_可用库存" label="可用库存" min-width="100" align="right" show-overflow-tooltip>
                <template #default="scope">
                  <span>{{ formatNumber(scope.row.自动机_可用库存) }}</span>
                </template>
              </el-table-column>
            </el-table-column>
            
            <el-table-column label="加工线" align="center">
              <el-table-column prop="加工线_完成量" label="完成量" min-width="100" align="right" show-overflow-tooltip>
                <template #default="scope">
                  <span>{{ formatNumber(scope.row.加工线_完成量) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="加工线_可用库存" label="可用库存" min-width="100" align="right" show-overflow-tooltip>
                <template #default="scope">
                  <span>{{ formatNumber(scope.row.加工线_可用库存) }}</span>
                </template>
              </el-table-column>
            </el-table-column>
            
            <el-table-column label="后工序-拣锁体" align="center">
              <el-table-column prop="拣锁体_完成量" label="完成量" min-width="100" align="right" show-overflow-tooltip>
                <template #default="scope">
                  <span>{{ formatNumber(scope.row.拣锁体_完成量) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="拣锁体_可用库存" label="可用库存" min-width="100" align="right" show-overflow-tooltip>
                <template #default="scope">
                  <span>{{ formatNumber(scope.row.拣锁体_可用库存) }}</span>
                </template>
              </el-table-column>
            </el-table-column>
          </el-table>

          <el-empty v-else description="暂无数据" />

          <div class="pagination-row">
            <el-pagination
              background
              layout="total, sizes, prev, pager, next, jumper"
              :total="filteredTotal"
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
  name: 'LockBodyProcessStats',
  components: {
    Layout
  },
  data() {
    return {
      breadcrumbItems: ['报表页面', '锁体C分区域库存计算'],
      filters: {
        orderNo: '',
        itemName: '',
        itemCode: ''
      },
      tableData: [],
      allFilteredData: [],
      loading: false,
      exportLoading: false,
      currentPage: 1,
      pageSize: 50,
      total: 0,
      filteredTotal: 0,
      showAllDataSummary: true
    }
  },
  created() {
    this.initializePageData()
  },
  computed: {
    allDataSummary() {
      if (!this.allFilteredData.length) return null
      const sum = (arr, prop) => arr.reduce((acc, item) => acc + (Number(item[prop]) || 0), 0)
      return {
        计划产量: sum(this.allFilteredData, '计划产量'),
        流转_完成量: sum(this.allFilteredData, '流转_完成量'),
        自动机_完成量: sum(this.allFilteredData, '自动机_完成量'),
        自动机_可用库存: sum(this.allFilteredData, '自动机_可用库存'),
        加工线_完成量: sum(this.allFilteredData, '加工线_完成量'),
        加工线_可用库存: sum(this.allFilteredData, '加工线_可用库存'),
        拣锁体_完成量: sum(this.allFilteredData, '拣锁体_完成量'),
        拣锁体_可用库存: sum(this.allFilteredData, '拣锁体_可用库存')
      }
    },
    totalAvailableInventory() {
      if (!this.allDataSummary) return 0
      return (this.allDataSummary.自动机_可用库存 || 0) 
           + (this.allDataSummary.加工线_可用库存 || 0) 
           + (this.allDataSummary.拣锁体_可用库存 || 0)
    }
  },
methods: {
    formatNumber(value) {
      if (value === null || value === undefined || value === '') {
        return '-'
      }
      return Number(value).toLocaleString()
    },
    formatDate(value) {
      if (!value) return '-'
      try {
        // 处理各种日期格式
        let dateStr = String(value)
        
        // 已经是 YYYY-MM-DD 格式
        if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
          return dateStr.replace(/-/g, '/')
        }
        
        // 处理带时间的格式（如 "2026-05-01 00:00:00" 或 "2026-05-01T00:00:00"）
        if (dateStr.includes(' ') || dateStr.includes('T')) {
          dateStr = dateStr.split(' ')[0].split('T')[0]
          return dateStr.replace(/-/g, '/')
        }
        
        const date = new Date(value)
        if (isNaN(date.getTime())) return String(value)
        return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
      } catch {
        return String(value)
      }
    },
    initializePageData() {
      this.searchReport(false)
    },
    async searchReport(resetPage = true) {
      if (resetPage) {
        this.currentPage = 1
      }
      this.loading = true
      try {
        const params = {}
        if (this.filters.orderNo) {
          params.order_no = this.filters.orderNo.trim()
        }
        if (this.filters.itemName) {
          params.item_name = this.filters.itemName.trim()
        }
        if (this.filters.itemCode) {
          params.item_code = this.filters.itemCode.trim()
        }
        
        const response = await axios.get('/api/lock_body_process_stats', { params })
        
        if (response.data?.status === 'success') {
          this.allFilteredData = response.data.data?.details || []
          this.total = this.allFilteredData.length
          this.filteredTotal = this.total
          // 根据业务逻辑计算库存字段
          this.calculateInventory()
          this.updateTableData()
        } else {
          this.$message.error('数据获取失败')
        }
      } catch (error) {
        console.error('获取锁体C分区域库存数据失败:', error)
        this.$message.error('数据加载失败，请检查网络连接')
      } finally {
        this.loading = false
      }
    },
    updateTableData() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      this.tableData = this.allFilteredData.slice(start, end)
    },
    calculateInventory() {
      // 业务逻辑：每个工序的库存 = 上游完成量 - 当前工序完成量
      // 自动机库存 = 流转完成量 - 自动机完成量（流转到自动机后还未加工的数量）
      // 加工线库存 = 自动机完成量 - 加工线完成量（自动机产出还未被加工线消耗的数量）
      // 拣锁体库存 = 加工线完成量 - 拣锁体完成量（加工线产出还未被拣锁体消耗的数量）
      this.allFilteredData.forEach(item => {
        item.自动机_可用库存 = (item.流转_完成量 || 0) - (item.自动机_完成量 || 0)
        item.加工线_可用库存 = (item.自动机_完成量 || 0) - (item.加工线_完成量 || 0)
        item.拣锁体_可用库存 = (item.加工线_完成量 || 0) - (item.拣锁体_完成量 || 0)
      })
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
        orderNo: '',
        itemName: '',
        itemCode: ''
      }
      this.searchReport(true)
    },
    getPageSummaries({ columns, data }) {
      const sums = []
      columns.forEach((column, index) => {
        if (index === 0) {
          sums[index] = '总计'
          return
        }
        if (index === 1 || index === 2 || index === 3 || index === 4) {
          sums[index] = ''
          return
        }
        const prop = column.property
        const needSumProps = ['计划产量', '流转_完成量', '自动机_完成量', '自动机_可用库存', '加工线_完成量', '加工线_可用库存', '拣锁体_完成量', '拣锁体_可用库存']
        if (needSumProps.includes(prop)) {
          const total = data.reduce((acc, item) => {
            const val = Number(item[prop]) || 0
            return acc + val
          }, 0)
          sums[index] = total.toLocaleString()
        } else {
          sums[index] = ''
        }
      })
      return sums
    },
    async exportExcel() {
      this.exportLoading = true
      try {
        const params = {}
        if (this.filters.orderNo) {
          params.order_no = this.filters.orderNo.trim()
        }
        if (this.filters.itemName) {
          params.item_name = this.filters.itemName.trim()
        }
        if (this.filters.itemCode) {
          params.item_code = this.filters.itemCode.trim()
        }
        
        const response = await axios.get('/api/lock_body_process_stats/export', {
          params,
          responseType: 'blob'
        })
        
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        const filename = response.headers['content-disposition'] 
          ? decodeURIComponent(response.headers['content-disposition'].split('filename=')[1] || '锁体C分区域库存计算.xlsx').replace(/"/g, '')
          : '锁体C分区域库存计算.xlsx'
        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        
        this.$message.success('Excel导出成功')
      } catch (error) {
        console.error('导出Excel失败:', error)
        this.$message.error('导出Excel失败，请稍后重试')
      } finally {
        this.exportLoading = false
      }
    }
  }
}
</script>

<style scoped>
.report-container {
  padding: 0;
}

.filter-card .el-card__body {
  padding-bottom: 10px;
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

.summary-form {
  background: #f5f7fa;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.summary-form-title {
  font-size: 14px;
  font-weight: bold;
  color: #303133;
}

.summary-inventory-total {
  background: #fff;
  padding: 8px 16px;
  border-radius: 4px;
  border: 1px solid #e1f3d8;
}

.summary-inventory-total .total-label {
  font-size: 13px;
  color: #606266;
  margin-right: 8px;
}

.summary-inventory-total .total-value {
  font-size: 16px;
  font-weight: bold;
  color: #67c23a;
}

.summary-form-table {
  width: 100%;
  border-collapse: collapse;
}

.summary-form-table .summary-item {
  padding: 10px;
  text-align: center;
  border: 1px solid #ebeef5;
  background: #fff;
}

.summary-form-table .summary-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.summary-form-table .summary-value {
  display: block;
  font-size: 14px;
  color: #606266;
  font-weight: 500;
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
