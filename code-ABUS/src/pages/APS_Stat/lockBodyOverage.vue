<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <template #breadcrumb-actions>
      <el-alert title="首次数据加载时间较长，请耐心等待" type="warning" :closable="false" show-icon style="display:inline-flex;align-items:center;height:28px;padding:0 10px;margin-left:12px;font-size:12px" />
    </template>
    <div class="report-container">
      <div class="el-card is-always-shadow mb-4">
        <div class="el-card__body">
          <el-form @submit.native.prevent="searchData" label-width="120px">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="订单批号">
                  <el-select v-model="filters.订单批号" placeholder="选择订单批号" filterable clearable @change="searchData">
                    <el-option v-for="o in orderNoOptions" :key="o" :label="o" :value="o" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="物料编码">
                  <el-select v-model="filters.锁体品号" placeholder="选择物料编码" filterable clearable @change="searchData">
                    <el-option v-for="o in materialCodeOptions" :key="o" :label="o" :value="o" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="锁体规格">
                  <el-select v-model="filters.锁体规格" placeholder="选择规格" filterable clearable @change="searchData">
                    <el-option v-for="o in specOptions" :key="o" :label="o" :value="o" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <div class="form-actions">
              <el-button type="primary" :loading="loading" @click="searchData">查询</el-button>
              <el-button @click="resetFilters">重置</el-button>
              <el-button type="success" :loading="exporting" @click="exportExcel">
                {{ exporting ? '导出中...' : '导出Excel' }}
              </el-button>
            </div>
          </el-form>
        </div>
      </div>

      <div class="el-card is-always-shadow mb-4 summary-card">
        <div class="el-card__body summary-row">
          <span>总条数: <b>{{ total }}</b></span>
        </div>
      </div>

      <div class="el-card is-always-shadow table-card" v-loading="loading" element-loading-text="加载中...">
        <div class="el-card__body">
          <el-table v-if="tableData.length" :data="tableData" border stripe max-height="620"
            style="width:100%" :header-cell-style="{ background: '#eef1f6', color: '#606266' }">
            <el-table-column type="index" label="序号" width="60" align="center" :index="indexMethod" />
            <el-table-column prop="订单批号" label="订单批号" min-width="160" show-overflow-tooltip />
            <el-table-column prop="锁类分区" label="锁类分区" width="100" />
            <el-table-column prop="锁体品号" label="物料编码" min-width="130" show-overflow-tooltip />
            <el-table-column prop="锁体物料名称" label="锁体物料名称" min-width="160" show-overflow-tooltip />
            <el-table-column prop="锁体规格" label="锁体规格" min-width="160" show-overflow-tooltip />
            <el-table-column prop="订单需求数量" label="订单需求数量" width="120" align="right" />
            <el-table-column prop="锁体历史入库数量" label="锁体历史入库数量" width="140" align="right" />
            <el-table-column prop="超入库数量" label="超入库数量" width="110" align="right">
              <template #default="scope">
                <span style="color:#e6a23c;font-weight:bold">{{ scope.row['超入库数量'] }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="是否超入库" label="是否超入库" width="100" align="center" />
            <el-table-column prop="入库完成率" label="入库完成率" width="110" align="right">
              <template #default="scope">
                <span v-if="scope.row['入库完成率'] !== null">{{ (scope.row['入库完成率'] * 100).toFixed(2) }}%</span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="订单单位" label="订单单位" width="90" />
            <el-table-column prop="入库单位" label="入库单位" width="90" />
            <el-table-column prop="入库仓库" label="入库仓库" min-width="120" show-overflow-tooltip />
            <el-table-column prop="最早入库日期" label="最早入库日期" width="160" />
            <el-table-column prop="最后入库日期" label="最后入库日期" width="160" />
            <el-table-column prop="要求交期" label="要求交期" width="160" />
            <el-table-column prop="确定交期" label="确定交期" width="160" />
            <el-table-column prop="订单状态" label="订单状态" width="100" />
          </el-table>
          <el-empty v-else description="暂无数据" />

          <div class="pagination-row">
            <el-pagination background layout="total, sizes, prev, pager, next, jumper"
              :total="total" :current-page="currentPage" :page-sizes="[50, 100, 200, 500]"
              :page-size="pageSize" @current-change="handlePageChange"
              @size-change="handleSizeChange" />
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
  name: 'LockBodyOverage',
  components: { Layout },
  data() {
    return {
      breadcrumbItems: ['报表页面', '超市多出的损耗数'],
      filters: {
        订单批号: '',
        锁体品号: '',
        锁体规格: '',
      },
      orderNoOptions: [],
      materialCodeOptions: [],
      specOptions: [],
      tableData: [],
      allData: [],
      loading: false,
      exporting: false,
      currentPage: 1,
      pageSize: 100,
      total: 0,
      sidebarMenus: [],
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
          return path.split('/').pop()
        }
        const paths = path.split('/').filter(p => p)
        const menuNames = findMenuName(menus, '/' + paths.join('/'))
        this.breadcrumbItems = Array.isArray(menuNames) ? menuNames : ['报表页面', '超市多出的损耗数']
      } catch {
        this.breadcrumbItems = ['报表页面', '超市多出的损耗数']
      }
    },
    indexMethod(index) {
      return (this.currentPage - 1) * this.pageSize + index + 1
    },
    async loadOptions() {
      try {
        const fields = ['订单批号', '锁体品号', '锁体规格']
        const results = await Promise.all(fields.map(f =>
          axios.get('/api/lockBodyOverage/options', { params: { field: f } })
            .then(res => ({ f, d: res.data }))
            .catch(() => ({ f, d: { data: [] } }))
        ))
        for (const r of results) {
          const vals = (r.d.data || []).map(i => i.value)
          if (r.f === '订单批号') this.orderNoOptions = vals
          else if (r.f === '锁体品号') this.materialCodeOptions = vals
          else if (r.f === '锁体规格') this.specOptions = vals
        }
      } catch {}
    },
    getFilterParams() {
      const params = {}
      if (this.filters.订单批号) params.订单批号 = this.filters.订单批号
      if (this.filters.锁体品号) params.物料编码 = this.filters.锁体品号
      if (this.filters.锁体规格) params.锁体规格 = this.filters.锁体规格
      return params
    },
    async searchData() {
      this.loading = true
      this.currentPage = 1
      try {
        const params = this.getFilterParams()
        const response = await axios.get('/api/lockBodyOverage', { params })
        if (response.data?.status === 'success') {
          this.allData = response.data.data || []
          this.total = response.data.total_count || this.allData.length
          this.updateTableData()
        } else {
          this.$message.error('数据获取失败')
        }
      } catch (error) {
        console.error('获取数据失败:', error)
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
      this.filters = { 订单批号: '', 锁体品号: '', 锁体规格: '' }
      this.searchData()
    },
    async exportExcel() {
      this.exporting = true
      try {
        const params = this.getFilterParams()
        const response = await axios.get('/api/lockBodyOverage/export', {
          params,
          responseType: 'blob'
        })

        let filename = '超市多出的损耗数.xlsx'
        const disposition = response.headers['content-disposition']
        if (disposition) {
          const match = disposition.match(/filename\*=UTF-8''(.+?)(?:;|$)/)
          if (match) {
            filename = decodeURIComponent(match[1])
          }
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
        this.$message.success('导出成功')
      } catch (error) {
        console.error('导出失败:', error)
        this.$message.error('导出失败，请检查网络连接')
      } finally {
        this.exporting = false
      }
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
