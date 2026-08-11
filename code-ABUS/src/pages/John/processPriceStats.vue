<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="el-card is-always-shadow mb-4">
      <div class="el-card__body">
        <el-form @submit.native.prevent="searchData" label-width="100px">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-form-item label="车间">
                <el-select
                  v-model="filters.部门"
                  placeholder="选择车间"
                  filterable
                  clearable
                >
                  <el-option
                    v-for="d in departmentOptions"
                    :key="d"
                    :label="d"
                    :value="d"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="工序名称">
                <el-select
                  v-model="filters.工序名称"
                  placeholder="选择工序名称"
                  filterable
                  clearable
                >
                  <el-option
                    v-for="n in processOptions"
                    :key="n"
                    :label="n"
                    :value="n"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <div class="stats-right-col">
                <div class="stats-card stats-card--all">
                  <span class="stats-card__title">所有车间</span>
                  <span class="stats-card__item">工序：<b>{{ allStatsData.length }}</b></span>
                  <span class="stats-card__item">单价：<b>{{ allTotal }}</b></span>
                </div>
              </div>
            </el-col>
          </el-row>
          <div class="stats-bottom-row">
            <div class="stats-card stats-card--current">
              <span class="stats-card__title">当前车间</span>
              <span class="stats-card__item">工序：<b>{{ statsData.length }}</b></span>
              <span class="stats-card__item">单价：<b>{{ total }}</b></span>
            </div>
            <div class="stats-buttons">
              <el-button type="primary" :loading="loading" @click="searchData">查询</el-button>
              <el-button @click="resetFilters">重置</el-button>
            </div>
          </div>
        </el-form>
      </div>
    </div>

    <div v-if="statsData.length" class="el-card is-always-shadow mb-4">
      <div class="el-card__body">
        <div class="stats-title">统计（按车间+工序名称）</div>
        <el-table
          :data="paginatedStats"
          border
          stripe
          style="width: 100%"
          :header-cell-style="{ background: '#eef1f6', color: '#606266' }"
        >
          <el-table-column type="index" label="序号" width="60" align="center" :index="statsIndex" />
          <el-table-column prop="部门" label="车间" min-width="150" show-overflow-tooltip />
          <el-table-column prop="工序名称" label="工序名称" min-width="150" show-overflow-tooltip />
          <el-table-column prop="记录数" label="记录数" width="80" align="center" />
          <el-table-column prop="最高价" label="最高价" width="100" align="right">
            <template #default="scope"><span style="color:#e6a23c">{{ formatNumber(scope.row.最高价) }}</span></template>
          </el-table-column>
          <el-table-column prop="最低价" label="最低价" width="100" align="right">
            <template #default="scope"><span style="color:#67c23a">{{ formatNumber(scope.row.最低价) }}</span></template>
          </el-table-column>
          <el-table-column prop="平均价" label="平均价" width="100" align="right">
            <template #default="scope"><span style="color:#409eff;font-weight:bold">{{ formatNumber(scope.row.平均价) }}</span></template>
          </el-table-column>
        </el-table>
        <div class="pagination-row">
          <el-pagination
            background
            layout="total, sizes, prev, pager, next, jumper"
            :total="statsData.length"
            :current-page="statsPage"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="statsPageSize"
            @size-change="handleStatsSizeChange"
            @current-change="handleStatsPageChange"
          />
        </div>
      </div>
    </div>

    <div class="el-card is-always-shadow table-card" v-loading="loading" element-loading-text="加载中...">
      <div class="el-card__body">
        <el-table
          v-if="tableData.length"
          :data="tableData"
          border
          stripe
          max-height="500"
          style="width: 100%"
          :header-cell-style="{ background: '#eef1f6', color: '#606266' }"
        >
          <el-table-column type="index" label="序号" width="60" align="center" />
          <el-table-column prop="部门" label="车间" min-width="120" show-overflow-tooltip />
          <el-table-column prop="工序名称" label="工序名称" min-width="120" show-overflow-tooltip />
          <el-table-column prop="产品规格" label="产品规格" min-width="150" show-overflow-tooltip />
          <el-table-column prop="单位" label="单位" width="60" align="center" />
          <el-table-column prop="生效单价" label="生效单价" width="100" align="right">
            <template #default="scope"><span>{{ formatNumber(scope.row.生效单价) }}</span></template>
          </el-table-column>
          <el-table-column prop="每小时产量" label="每小时产量" width="110" align="right">
            <template #default="scope"><span>{{ formatNumber(scope.row.每小时产量) }}</span></template>
          </el-table-column>
          <el-table-column prop="调整前单价" label="调整前单价" width="100" align="right">
            <template #default="scope"><span>{{ formatNumber(scope.row.调整前单价) }}</span></template>
          </el-table-column>
          <el-table-column prop="调整单价" label="调整单价" width="100" align="right">
            <template #default="scope"><span>{{ formatNumber(scope.row.调整单价) }}</span></template>
          </el-table-column>
          <el-table-column prop="工序规格码" label="工序规格码" min-width="120" show-overflow-tooltip />
          <el-table-column prop="规格次序" label="规格次序" width="80" align="center" />
          <el-table-column prop="单价状态" label="单价状态" width="80" align="center" />
          <el-table-column prop="产品分区" label="产品分区" min-width="100" show-overflow-tooltip />
          <el-table-column prop="通用规格" label="通用规格" min-width="120" show-overflow-tooltip />
          <el-table-column prop="工序内容" label="工序内容" min-width="150" show-overflow-tooltip />
          <el-table-column prop="作业人数" label="作业人数" width="80" align="center" />
          <el-table-column prop="加工尺寸" label="加工尺寸" min-width="100" show-overflow-tooltip />
          <el-table-column prop="修改时间" label="修改时间" width="110" show-overflow-tooltip />
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
            @size-change="handlePageSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </div>
  </Layout>
</template>

<script>
import axios from 'axios'
import Layout from '../../components/Layout.vue'
import { eventBus } from '../../eventBus'

export default {
  name: 'ProcessPriceStats',
  components: {
    Layout
  },
  data() {
    return {
      breadcrumbItems: [],
      sidebarMenus: [],
      filters: {
        部门: '',
        工序名称: ''
      },
      departmentOptions: [],
      processOptions: [],
      statsData: [],
      statsPage: 1,
      statsPageSize: 20,
      tableData: [],
      allData: [],
      allStatsData: [],
      allTotal: 0,
      loading: false,
      currentPage: 1,
      currentPage: 1,
      pageSize: 50,
      total: 0
    }
  },
  created() {
    console.log('[ProcessPriceStats] 组件已挂载')
    eventBus.$on('sidebar-Menus-Updated', (menus) => {
      this.sidebarMenus = menus
      this.generateBreadcrumb(this.$route.path)
    })
    if (this.sidebarMenus.length === 0) {
      this.breadcrumbItems = ['报表页面', '单价', '工序规格码单价明细与统计']
    }
    this.loadDepartments()
    this.loadProcessNames('')
    this.searchData()
  },
  computed: {
    paginatedStats() {
      const start = (this.statsPage - 1) * this.statsPageSize
      return this.statsData.slice(start, start + this.statsPageSize)
    },
    statsIndex() {
      return (this.statsPage - 1) * this.statsPageSize + 1
    }
  },
  watch: {
    $route(newVal) {
      this.generateBreadcrumb(newVal.path)
    },
    'filters.部门': {
      handler(val) {
        console.log('[ProcessPriceStats] filters.部门 changed:', val)
        this.filters.工序名称 = ''
        this.processOptions = []
        this.loadProcessNames(val)
      }
    }
  },
  methods: {
    generateBreadcrumb(path) {
      try {
        const menus = this.sidebarMenus
        const findMenuName = (menus, targetPath) => {
          for (const menu of menus) {
            if (menu.path === targetPath) return [menu.name]
            if (menu.children) {
              for (const child of menu.children) {
                if (child.path === targetPath) return [menu.name, child.name]
                if (child.children) {
                  for (const grandchild of child.children) {
                    if (grandchild.path === targetPath) return [menu.name, child.name, grandchild.name]
                  }
                }
              }
            }
          }
          return null
        }
        const paths = path.split('/').filter(p => p)
        const menuNames = findMenuName(menus, '/' + paths.join('/'))
        this.breadcrumbItems = menuNames || ['报表页面', '单价', '工序规格码单价明细与统计']
      } catch {
        this.breadcrumbItems = ['报表页面', '单价', '工序规格码单价明细与统计']
      }
    },
    formatNumber(value) {
      if (value === null || value === undefined || value === '') {
        return '-'
      }
      return Number(value).toLocaleString()
    },
    async loadDepartments() {
      try {
        const res = await axios.get('/api/processPriceStats/departments')
        if (res.data?.status === 'success') {
          this.departmentOptions = res.data.data || []
        }
      } catch {}
    },
    async loadProcessNames(部门) {
      try {
        const params = {}
        if (部门) params.部门 = 部门
        const res = await axios.get('/api/processPriceStats/processNames', { params })
        if (res.data?.status === 'success') {
          this.processOptions = res.data.data || []
        }
      } catch (e) {
        console.error('loadProcessNames error:', e)
      }
    },
    on车间Change(val) {
      console.log('on车间Change triggered, val:', val, 'filters.部门:', this.filters.部门)
      this.filters.工序名称 = ''
      this.processOptions = []
      this.loadProcessNames(val || this.filters.部门)
    },
    handleStatsPageChange(page) {
      this.statsPage = page
    },
    handleStatsSizeChange(size) {
      this.statsPageSize = size
      this.statsPage = 1
    },
    async searchData() {
      this.currentPage = 1
      this.statsPage = 1
      this.loading = true
      try {
        const params = {}
        if (this.filters.部门) {
          params.部门 = this.filters.部门
        }
        if (this.filters.工序名称) {
          params.工序名称 = this.filters.工序名称
        }

        const response = await axios.get('/api/processPriceStats', { params })

        if (response.data?.status === 'success') {
          this.statsData = response.data.data?.stats || []
          this.allData = response.data.data?.details || []
          this.total = this.allData.length
          if (!this.filters.部门 && !this.filters.工序名称) {
            this.allStatsData = this.statsData
            this.allTotal = this.total
          }
          this.updateTableData()
        } else {
          this.$message.error('数据获取失败')
        }
      } catch (error) {
        console.error('获取工序单价数据失败:', error)
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
      this.filters = { 部门: '', 工序名称: '' }
      this.searchData()
    }
  }
}
</script>

<style scoped>
.mb-4 {
  margin-bottom: 16px;
}
.stats-right-col {
  display: flex;
  flex-direction: column;
  gap: 8px;
  justify-content: center;
  height: 100%;
  align-items: flex-end;
}
.stats-bottom-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}
.stats-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
.stats-card {
  display: inline-flex;
  align-items: center;
  gap: 16px;
  padding: 8px 20px;
  border-radius: 6px;
  font-size: 14px;
  height: 32px;
}
.stats-card--current {
  background: #ecf5ff;
  border: 1px solid #b3d8ff;
  margin-top: 10px;
}
.stats-card--all {
  background: #f4f4f5;
  border: 1px solid #dcdfe6;
}
.stats-card__title {
  font-size: 15px;
  font-weight: bold;
  color: #303133;
}
.stats-card--current .stats-card__title {
  color: #409eff;
}
.stats-card__item {
  color: #606266;
}
.stats-card__item b {
  font-size: 15px;
  font-weight: bold;
  color: #303133;
}
.stats-card--current .stats-card__item b {
  color: #409eff;
}
.table-card {
  min-height: 100px;
}
.pagination-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
