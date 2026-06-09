<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="report-container">
      <div class="el-card is-always-shadow mb-4">
        <div class="el-card__body">
          <el-form @submit.native.prevent="searchData" label-width="100px">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="data_type">
                  <el-select
                    v-model="filters.data_type"
                    placeholder="选择data_type"
                    filterable
                    clearable
                  >
                    <el-option v-for="o in dataTypeOptions" :key="o" :label="o" :value="o" />
                  </el-select>
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
                    <el-option v-for="o in partNameOptions" :key="o" :label="o" :value="o" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="部门">
                  <el-select
                    v-model="filters.DepartmentName"
                    placeholder="选择部门"
                    filterable
                    clearable
                  >
                    <el-option v-for="o in departmentOptions" :key="o" :label="o" :value="o" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="工序">
                  <el-select
                    v-model="filters.proccess"
                    placeholder="选择工序"
                    filterable
                    clearable
                  >
                    <el-option v-for="o in proccessOptions" :key="o" :label="o" :value="o" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="item_no">
                  <el-input
                    v-model="filters.item_no"
                    placeholder="请输入item_no"
                    clearable
                    @keyup.enter.native="searchData"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="part_spec">
                  <el-input
                    v-model="filters.part_spec"
                    placeholder="请输入part_spec"
                    clearable
                    @keyup.enter.native="searchData"
                  />
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
            <el-table-column prop="data_type" label="data_type" min-width="120" show-overflow-tooltip />
            <el-table-column prop="item_no" label="item_no" min-width="150" show-overflow-tooltip />
            <el-table-column prop="part_name" label="part_name" min-width="150" show-overflow-tooltip />
            <el-table-column prop="part_spec" label="part_spec" min-width="180" show-overflow-tooltip />
            <el-table-column prop="before_proccess" label="上一工序" min-width="120" show-overflow-tooltip />
            <el-table-column prop="before_proccessNumber" label="上一工序编号" min-width="130" show-overflow-tooltip />
            <el-table-column prop="proccess" label="当前工序" min-width="120" show-overflow-tooltip />
            <el-table-column prop="proccessNumber" label="工序规格码" min-width="120" show-overflow-tooltip />
            <el-table-column prop="DepartmentName" label="部门" min-width="100" show-overflow-tooltip />
            <el-table-column prop="capacity" label="产能" min-width="80" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" min-width="80" show-overflow-tooltip />
            <el-table-column prop="days" label="天数" min-width="80" show-overflow-tooltip />
            <el-table-column prop="包装方式" label="包装方式" min-width="100" show-overflow-tooltip />
            <el-table-column prop="OpExternalId" label="OpExternalId" min-width="130" show-overflow-tooltip />
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
  name: 'OfflineProcess',
  components: { Layout },
  data() {
    return {
      breadcrumbItems: ['报表页面', '工序规格码单价对应产品明细与统计'],
      filters: {
        data_type: '',
        part_name: '',
        part_spec: '',
        DepartmentName: '',
        proccess: '',
        item_no: ''
      },
      dataTypeOptions: [],
      partNameOptions: [],
      departmentOptions: [],
      proccessOptions: [],
      tableData: [],
      allData: [],
      loading: false,
      currentPage: 1,
      pageSize: 100,
      total: 0,
      sidebarMenus: []
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
            if (menu.path === targetPath) return menu.name
            if (menu.children) {
              for (const child of menu.children) {
                if (child.path === targetPath) return [menu.name, child.name]
              }
            }
          }
          return targetPath.split('/').pop()
        }
        const paths = path.split('/').filter(p => p)
        const menuNames = findMenuName(menus, '/' + paths.join('/'))
        this.breadcrumbItems = Array.isArray(menuNames) ? menuNames : [menuNames]
      } catch {
        this.breadcrumbItems = ['报表页面', '工序规格码单价对应产品明细与统计']
      }
    },
    indexMethod(index) {
      return (this.currentPage - 1) * this.pageSize + index + 1
    },
    async loadOptions() {
      try {
        const fields = ['data_type', 'part_name', 'DepartmentName', 'proccess']
        const results = await Promise.all(
          fields.map(f =>
            axios.get('/api/offlineProcess/options', { params: { field: f } })
              .then(res => ({ field: f, data: res.data }))
              .catch(() => ({ field: f, data: { status: 'error', data: [] } }))
          )
        )
        for (const r of results) {
          if (r.data?.status === 'success' && Array.isArray(r.data.data)) {
            const values = r.data.data.map(i => i.value)
            if (r.field === 'data_type') this.dataTypeOptions = values
            else if (r.field === 'part_name') this.partNameOptions = values
            else if (r.field === 'DepartmentName') this.departmentOptions = values
            else if (r.field === 'proccess') this.proccessOptions = values
          }
        }
      } catch (e) {
        console.error('loadOptions error:', e)
      }
    },
    async searchData() {
      this.loading = true
      this.currentPage = 1
      try {
        const params = {}
        if (this.filters.data_type) params.data_type = this.filters.data_type.trim()
        if (this.filters.part_name) params.part_name = this.filters.part_name.trim()
        if (this.filters.part_spec) params.part_spec = this.filters.part_spec.trim()
        if (this.filters.DepartmentName) params.DepartmentName = this.filters.DepartmentName.trim()
        if (this.filters.proccess) params.proccess = this.filters.proccess.trim()
        if (this.filters.item_no) params.item_no = this.filters.item_no.trim()

        const response = await axios.get('/api/offlineProcess', { params })
        if (response.data?.status === 'success') {
          this.allData = response.data.data || []
          this.total = response.data.total_count || this.allData.length
          this.updateTableData()
        } else {
          this.$message.error('数据获取失败')
        }
      } catch (error) {
        console.error('获取offline_process数据失败:', error)
        this.$message.error('数据加载失败，请检查网络连接')
      } finally {
        this.loading = false
      }
    },
    updateTableData() {
      const start = (this.currentPage - 1) * this.pageSize
      this.tableData = this.allData.slice(start, start + this.pageSize)
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
      this.filters = { data_type: '', part_name: '', part_spec: '', DepartmentName: '', proccess: '', item_no: '' }
      this.searchData()
    }
  }
}
</script>

<style scoped>
.report-container { padding: 0; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; padding-top: 10px; }
.summary-row { display: flex; justify-content: flex-end; color: #303133; }
.table-card { min-height: 100px; }
.pagination-row { display: flex; justify-content: flex-end; margin-top: 16px; }
.mb-4 { margin-bottom: 16px; }
</style>
