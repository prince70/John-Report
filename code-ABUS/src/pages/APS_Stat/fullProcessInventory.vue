<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="report-container">
      <div class="el-card is-always-shadow mb-4">
        <div class="el-card__body">
          <el-form @submit.native.prevent="searchData" label-width="100px">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="订单批号">
                  <el-input
                    v-model="filters.订单批号"
                    placeholder="请输入订单批号"
                    clearable
                    @keyup.enter.native="searchData"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="料品编码">
                  <el-input
                    v-model="filters.料品编码"
                    placeholder="请输入料品编码"
                    clearable
                    @keyup.enter.native="searchData"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="part_name">
                  <el-select
                    v-model="filters.part_name"
                    placeholder="选择part_name"
                    filterable
                    clearable
                  >
                    <el-option
                      v-for="option in partNameOptions"
                      :key="option"
                      :label="option"
                      :value="option"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="part_spec">
                  <el-select
                    v-model="filters.part_spec"
                    placeholder="选择part_spec"
                    filterable
                    clearable
                  >
                    <el-option
                      v-for="option in partSpecOptions"
                      :key="option"
                      :label="option"
                      :value="option"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="生产车间">
                  <el-select
                    v-model="filters.生产车间"
                    placeholder="选择生产车间"
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
            <el-table-column type="index" label="序号" width="60" align="center" :index="indexMethod" />
            <el-table-column prop="订单批号" label="订单批号" min-width="150" show-overflow-tooltip />
            <el-table-column prop="料品编码" label="料品编码" min-width="150" show-overflow-tooltip />
            <el-table-column prop="part_name" label="part_name" min-width="180" show-overflow-tooltip />
            <el-table-column prop="part_spec" label="part_spec" min-width="150" show-overflow-tooltip />
            <el-table-column prop="生产车间" label="生产车间" min-width="120" show-overflow-tooltip />
            <el-table-column prop="当前工序ID" label="当前工序ID" min-width="100" show-overflow-tooltip />
            <el-table-column prop="下一道工序ID" label="下一道工序ID" min-width="110" show-overflow-tooltip />
            <el-table-column prop="报工数量总和" label="报工数量总和" min-width="120" align="right">
              <template #default="scope">
                <span>{{ formatNumber(scope.row.报工数量总和) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="库存" label="库存" min-width="100" align="right">
              <template #default="scope">
                <span>{{ formatNumber(scope.row.库存) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="备注" label="备注" min-width="120" show-overflow-tooltip />
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
              @current-change="handlePageChange"
              @size-change="handleSizeChange"
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
import { eventBus } from '../../eventBus'

export default {
  name: 'FullProcessInventory',
  components: {
    Layout
  },
  data() {
    return {
      breadcrumbItems: ['报表页面', '全流程报工库存'],
      filters: {
        订单批号: '',
        料品编码: '',
        part_name: '',
        part_spec: '',
        生产车间: ''
      },
      workshopOptions: [],
      partNameOptions: [],
      partSpecOptions: [],
      tableData: [],
      allData: [],
      loading: false,
      currentPage: 1,
      pageSize: 100,
      total: 0,
      sidebarMenus: []
    }
  },
  computed: {
    tableType() {
      const path = this.$route.path
      if (path.includes('CNC')) return 'CNC'
      if (path.includes('DZS')) return 'DZS'
      return 'CNC'
    }
  },
  created() {
    eventBus.$on('sidebar-Menus-Updated', (menus) => {
      this.sidebarMenus = menus
      this.generateBreadcrumb(this.$route.path)
    })
    this.loadOptions()
    this.searchData()
  },
  watch: {
    tableType() {
      this.loadOptions()
      this.resetFilters()
    },
    $route(newVal) {
      this.generateBreadcrumb(newVal.path)
    }
  },
  methods: {
    generateBreadcrumb(path) {
      try {
        const menus = this.sidebarMenus
        const findMenuName = (menus, targetPath) => {
          for (const menu of menus) {
            if (menu.path === targetPath) {
              return menu.name
            }
            if (menu.children) {
              for (const child of menu.children) {
                if (child.path === targetPath) {
                  return [menu.name, child.name]
                }
              }
            }
          }
          return targetPath.split('/').pop()
        }
        const paths = path.split('/').filter(p => p)
        const menuNames = findMenuName(menus, '/' + paths.join('/'))
        if (Array.isArray(menuNames)) {
          this.breadcrumbItems = menuNames
        } else {
          this.breadcrumbItems = [menuNames]
        }
      } catch (error) {
        this.breadcrumbItems = ['报表页面', '全流程报工库存']
      }
    },
    formatNumber(value) {
      if (value === null || value === undefined || value === '') {
        return '-'
      }
      return Number(value).toLocaleString()
    },
    indexMethod(index) {
      return (this.currentPage - 1) * this.pageSize + index + 1
    },
    async loadOptions() {
      try {
        const fields = ['生产车间', 'part_name', 'part_spec']
        const results = await Promise.all(
          fields.map(f =>
            axios.get(`/api/fullProcessInventory/${this.tableType}/options`, { params: { field: f } })
              .then(res => ({ field: f, data: res.data }))
              .catch(() => ({ field: f, data: { status: 'error', data: [] } }))
          )
        )
        for (const r of results) {
          if (r.data?.status === 'success' && Array.isArray(r.data.data)) {
            const values = r.data.data.map(i => i.value)
            if (r.field === '生产车间') this.workshopOptions = values
            else if (r.field === 'part_name') this.partNameOptions = values
            else if (r.field === 'part_spec') this.partSpecOptions = values
          }
        }
      } catch (e) {
        console.error('[loadOptions] 错误:', e)
      }
    },
    async searchData() {
      this.loading = true
      this.currentPage = 1
      try {
        const params = {}
        if (this.filters.订单批号) params.订单批号 = this.filters.订单批号.trim()
        if (this.filters.料品编码) params.料品编码 = this.filters.料品编码.trim()
        if (this.filters.part_name) params.part_name = this.filters.part_name.trim()
        if (this.filters.part_spec) params.part_spec = this.filters.part_spec.trim()
        if (this.filters.生产车间) params.生产车间 = this.filters.生产车间

        const response = await axios.get(`/api/fullProcessInventory/${this.tableType}`, { params })

        if (response.data?.status === 'success') {
          this.allData = response.data.data || []
          this.total = response.data.total_count || this.allData.length
          this.updateTableData()
        } else {
          this.$message.error('数据获取失败')
        }
      } catch (error) {
        console.error('获取全流程报工库存数据失败:', error)
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
    handleSizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
      this.updateTableData()
    },
    resetFilters() {
      this.filters = {
        订单批号: '',
        料品编码: '',
        part_name: '',
        part_spec: '',
        生产车间: ''
      }
      this.searchData()
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
