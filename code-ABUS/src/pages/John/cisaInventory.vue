<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="inventory-container">
      <div class="el-card is-always-shadow mb-4">
        <div class="el-card__body">
          <el-form @submit.native.prevent="search(true)" label-width="90px">
            <el-row :gutter="16">
              <el-col :xs="24" :sm="8">
                <el-form-item label="料品编码">
                  <el-input
                    v-model.trim="filters.item_code"
                    clearable
                    placeholder="请输入料品编码"
                    @keyup.enter.native="search(true)"
                  />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item label="产品名称">
                  <el-input
                    v-model.trim="filters.product_name"
                    clearable
                    placeholder="请输入产品名称"
                    @keyup.enter.native="search(true)"
                  />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item label="产品规格">
                  <el-input
                    v-model.trim="filters.product_spec"
                    clearable
                    placeholder="请输入产品规格"
                    @keyup.enter.native="search(true)"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <div class="form-actions">
              <el-button @click="resetFilters">重置</el-button>
              <el-button type="primary" :loading="loading" @click="search(true)">查询</el-button>
            </div>
          </el-form>
        </div>
      </div>

      <div class="el-card is-always-shadow mb-4">
        <div class="el-card__body summary-row">
          <span>当前页条数: <b>{{ rows.length }}</b> / 总条数: <b>{{ total }}</b></span>
        </div>
      </div>

      <div class="el-card is-always-shadow" v-loading="loading" element-loading-text="加载中...">
        <div class="el-card__body">
          <el-table
            v-if="rows.length"
            :data="rows"
            border
            stripe
            max-height="650"
            style="width: 100%"
            :header-cell-style="{ background: '#eef1f6', color: '#606266' }"
          >
            <el-table-column
              v-for="col in columns"
              :key="col"
              :prop="col"
              :label="col"
              :min-width="getColumnMinWidth(col)"
              show-overflow-tooltip
              align="center"
            >
              <template #default="scope">
                <span>{{ formatCell(col, scope.row[col]) }}</span>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="暂无数据" />

          <div class="pagination-row">
            <el-pagination
              background
              layout="total, sizes, prev, pager, next, jumper"
              :total="total"
              :current-page="currentPage"
              :page-sizes="pageSizeOptions"
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
  name: 'CisaInventory',
  components: {
    Layout
  },
  data() {
    return {
      breadcrumbItems: ['报表页面', 'CISA库存表'],
      loading: false,
      rows: [],
      columns: [],
      total: 0,
      currentPage: 1,
      pageSize: 100,
      pageSizeOptions: [50, 100, 200, 500, 1000],
      columnWidthMap: {},
      filters: {
        item_code: '',
        product_name: '',
        product_spec: ''
      }
    }
  },
  created() {
    this.search(true)
  },
  methods: {
    getColumnMinWidth(col) {
      return this.columnWidthMap[col] || 120
    },
    updateColumnWidthMap() {
      const widthMap = {}
      const sampleRows = this.rows.slice(0, 80)
      this.columns.forEach((col) => {
        let maxLen = String(col || '').length
        sampleRows.forEach((row) => {
          const text = row?.[col] === null || row?.[col] === undefined ? '' : String(row[col])
          if (text.length > maxLen) {
            maxLen = text.length
          }
        })
        const baseWidth = maxLen * 16 + 32
        widthMap[col] = Math.max(120, Math.min(baseWidth, 420))
      })
      this.columnWidthMap = widthMap
    },
    formatCell(col, value) {
      return value === null || value === undefined || value === '' ? '-' : value
    },
    async search(resetPage = false) {
      if (resetPage) {
        this.currentPage = 1
      }
      this.loading = true
      try {
        const offset = (this.currentPage - 1) * this.pageSize
        const params = {
          item_code: this.filters.item_code || undefined,
          product_name: this.filters.product_name || undefined,
          product_spec: this.filters.product_spec || undefined,
          offset,
          limit: this.pageSize,
          _t: Date.now()
        }
        const { data } = await axios.get('/api/cisa_inventory/list', { params })
        if (data?.status !== 'success') {
          throw new Error('返回状态异常')
        }

        this.rows = Array.isArray(data.data) ? data.data : []
        this.columns = Array.isArray(data.columns)
          ? data.columns
          : (this.rows.length ? Object.keys(this.rows[0]) : [])
        this.total = Number(data.total) || this.rows.length
        this.updateColumnWidthMap()
      } catch (error) {
        console.error('加载CISA库存表失败:', error)
        this.$message.error(error?.response?.data?.detail || '加载CISA库存表失败')
        this.rows = []
        this.columns = []
        this.total = 0
        this.columnWidthMap = {}
      } finally {
        this.loading = false
      }
    },
    resetFilters() {
      this.filters.item_code = ''
      this.filters.product_name = ''
      this.filters.product_spec = ''
      this.search(true)
    },
    handlePageChange(page) {
      this.currentPage = page
      this.search(false)
    },
    handlePageSizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
      this.search(false)
    }
  }
}
</script>

<style scoped>
.inventory-container {
  padding: 10px 12px 12px;
}

.mb-4 {
  margin-bottom: 10px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.summary-row {
  display: flex;
  justify-content: flex-end;
  color: #303133;
}

.pagination-row {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}
</style>
