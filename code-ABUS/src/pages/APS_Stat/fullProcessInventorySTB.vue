<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="report-container">
      <div class="el-card is-always-shadow mb-4">
        <div class="el-card__body">
          <el-form @submit.native.prevent="searchData" label-width="100px">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="订单批号">
                  <el-input v-model="filters.订单批号" placeholder="请输入订单批号" clearable @keyup.enter.native="searchData" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="料品编码">
                  <el-input v-model="filters.料品编码" placeholder="请输入料品编码" clearable @keyup.enter.native="searchData" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="料品名称">
                  <el-select v-model="filters.part_name" placeholder="选择料品名称" filterable clearable>
                    <el-option v-for="o in partNameOptions" :key="o" :label="o" :value="o" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="规格型号">
                  <el-select v-model="filters.part_spec" placeholder="选择规格型号" filterable clearable>
                    <el-option v-for="o in partSpecOptions" :key="o" :label="o" :value="o" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="5">
                <el-form-item label="当前工序">
                  <el-select v-model="filters.当前工序ID" placeholder="选择工序" filterable clearable>
                    <el-option v-for="o in processOptions" :key="o" :label="o" :value="o" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="5">
                <el-form-item label="下一道工序">
                  <el-select v-model="filters.下一道工序ID" placeholder="选择下一道工序" filterable clearable>
                    <el-option v-for="o in nextProcessOptions" :key="o" :label="o" :value="o" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="9">
                <el-form-item label="完成日期">
                  <div class="date-range-inline">
                    <el-date-picker v-model="filters.开始日期" type="date" placeholder="开始日期" value-format="yyyy-MM-dd" clearable style="width: 45%" />
                    <span class="date-separator">至</span>
                    <el-date-picker v-model="filters.结束日期" type="date" placeholder="结束日期" value-format="yyyy-MM-dd" clearable style="width: 45%" />
                  </div>
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

      <div v-if="summaryData.length" class="el-card is-always-shadow mb-4 summary-form">
        <div class="el-card__body">
          <div class="summary-form-title">汇总</div>
          <el-table :data="summaryData" border stripe size="medium" max-height="300" style="width: auto" :header-cell-style="{ background: '#eef1f6', color: '#606266', fontSize: '14px' }">
            <el-table-column prop="当前工序ID" label="当前工序ID" min-width="120" show-overflow-tooltip align="center" />
            <el-table-column prop="库存合计" label="库存合计" min-width="100" align="center">
              <template #default="scope"><span>{{ formatNumber(scope.row.库存合计) }}</span></template>
            </el-table-column>
            <el-table-column prop="记录数" label="记录数" min-width="70" align="center" />
          </el-table>
        </div>
      </div>

      <div class="el-card is-always-shadow mb-4">
        <div class="el-card__body" style="padding: 10px 20px;">
          <span style="font-size:14px;color:#606266;margin-right:12px;">分组方式：</span>
          <el-radio-group v-model="groupMode" @change="onGroupModeChange">
            <el-radio label="none">不分组</el-radio>
            <el-radio label="order">按订单批号+当前工序ID分组</el-radio>
            <el-radio label="spec">按规格型号+当前工序ID分组</el-radio>
          </el-radio-group>
        </div>
      </div>

      <div class="el-card is-always-shadow table-card" v-loading="loading" element-loading-text="加载中...">
        <div class="el-card__body">
          <el-table v-if="tableData.length" :data="tableData" border stripe max-height="620" style="width: 100%" :header-cell-style="{ background: '#eef1f6', color: '#606266' }">
            <el-table-column type="index" label="序号" width="60" align="center" :index="indexMethod" />
            <template v-if="groupMode === 'none'">
              <el-table-column prop="订单批号" label="订单批号" min-width="150" show-overflow-tooltip />
              <el-table-column prop="料品编码" label="料品编码" min-width="150" show-overflow-tooltip />
              <el-table-column prop="料品名称" label="料品名称" min-width="180" show-overflow-tooltip />
              <el-table-column prop="料品规格" label="规格型号" min-width="150" show-overflow-tooltip />
              <el-table-column prop="完成日期" label="完成日期" min-width="120" show-overflow-tooltip />
              <el-table-column prop="当前工序ID" label="当前工序ID" min-width="100" show-overflow-tooltip />
              <el-table-column prop="下一道工序ID" label="下一道工序ID" min-width="110" show-overflow-tooltip />
              <el-table-column prop="报工数量总和" label="报工数量总和" min-width="120" align="right">
                <template #default="scope"><span>{{ formatNumber(scope.row.报工数量总和) }}</span></template>
              </el-table-column>
              <el-table-column prop="库存" label="库存" min-width="100" align="right">
                <template #default="scope"><span>{{ formatNumber(scope.row.库存) }}</span></template>
              </el-table-column>
              <el-table-column prop="备注" label="备注" min-width="120" show-overflow-tooltip />
              <el-table-column prop="产品系列" label="系列" min-width="100" show-overflow-tooltip />
              <el-table-column prop="订单数量" label="订单数量" min-width="100" align="right">
                <template #default="scope"><span>{{ formatNumber(scope.row.订单数量) }}</span></template>
              </el-table-column>
              <el-table-column prop="确定交期" label="确定交期" min-width="120" show-overflow-tooltip />
              <el-table-column prop="下一工序原始上线期" label="下一工序原始上线期" min-width="150" show-overflow-tooltip />
              <el-table-column prop="emp_name" label="报工人" min-width="100" show-overflow-tooltip />
            </template>
            <template v-else-if="groupMode === 'order'">
              <el-table-column prop="订单批号" label="订单批号" min-width="150" show-overflow-tooltip />
              <el-table-column prop="当前工序ID" label="当前工序ID" min-width="100" show-overflow-tooltip />
              <el-table-column prop="报工数量总和" label="报工数量总和" min-width="120" align="right">
                <template #default="scope"><span>{{ formatNumber(scope.row.报工数量总和) }}</span></template>
              </el-table-column>
              <el-table-column prop="库存" label="库存" min-width="100" align="right">
                <template #default="scope"><span>{{ formatNumber(scope.row.库存) }}</span></template>
              </el-table-column>
              <el-table-column prop="记录数" label="记录数" min-width="80" align="center" />
            </template>
            <template v-else-if="groupMode === 'spec'">
              <el-table-column prop="料品规格" label="规格型号" min-width="150" show-overflow-tooltip />
              <el-table-column prop="当前工序ID" label="当前工序ID" min-width="100" show-overflow-tooltip />
              <el-table-column prop="报工数量总和" label="报工数量总和" min-width="120" align="right">
                <template #default="scope"><span>{{ formatNumber(scope.row.报工数量总和) }}</span></template>
              </el-table-column>
              <el-table-column prop="库存" label="库存" min-width="100" align="right">
                <template #default="scope"><span>{{ formatNumber(scope.row.库存) }}</span></template>
              </el-table-column>
              <el-table-column prop="记录数" label="记录数" min-width="80" align="center" />
            </template>
          </el-table>
          <el-empty v-else description="暂无数据" />
          <div class="pagination-row">
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
  name: 'FullProcessInventorySTB',
  components: { Layout },
  data() {
    return {
      breadcrumbItems: ['工序', '全流程报工库存', '锁体B车间'],
      filters: { 订单批号: '', 料品编码: '', part_name: '', part_spec: '', 当前工序ID: '', 下一道工序ID: '', 开始日期: '', 结束日期: '' },
      partNameOptions: [], partSpecOptions: [], processOptions: [], nextProcessOptions: [],
      tableData: [], allData: [], loading: false,
      currentPage: 1, pageSize: 100, total: 0, sidebarMenus: [],
      summaryData: [], groupMode: 'none', groupedData: []
    }
  },
  created() {
    eventBus.$on('sidebar-Menus-Updated', (menus) => { this.sidebarMenus = menus; this.generateBreadcrumb(this.$route.path) })
    this.loadOptions(); this.searchData()
  },
  watch: { $route(v) { this.generateBreadcrumb(v.path) } },
  methods: {
    generateBreadcrumb(path) {
      try {
        const nameMap = { CNC: 'CNC锁体车间', DZS: '电子锁车间', KEY: '钥匙车间', STA: '锁体A车间', STB: '锁体B车间', STC: '锁体C车间', KL: '开料车间', SL: '锁梁车间', STD: '锁体D车间', SX: '锁配件车间', ZQ_DZSQ: '装嵌车间-胆仔锁区', ZQ_GNSQ: '装嵌车间-功能锁区', ZQ_LMSQ: '装嵌车间-铝门锁区', DM_ZPQ: '打磨车间-装配区' }
        const find = (menus, p) => { for (const m of menus) { for (const s of (m.children || [])) { for (const gc of (s.children || [])) { for (const c of (gc.children || [])) { if (c.path === p) return [s.name, gc.name, c.name.replace(/^全流程报工库存-/, '')] } if (gc.path === p) return [s.name, gc.name] } } } const seg = p.split('/').pop(); return ['工序', '全流程报工库存', nameMap[seg] || seg] }
        const r = find(this.sidebarMenus, '/' + path.split('/').filter(p => p).join('/'))
        this.breadcrumbItems = Array.isArray(r) ? r : [r]
      } catch { this.breadcrumbItems = ['工序', '全流程报工库存', '锁体B车间'] }
    },
    formatNumber(v) { return (v === null || v === undefined || v === '') ? '-' : Number(v).toLocaleString() },
    indexMethod(i) { return (this.currentPage - 1) * this.pageSize + i + 1 },
    async loadOptions() {
      try {
        const fields = ['料品名称', '料品规格', '当前工序ID', '下一道工序ID']
        const results = await Promise.all(fields.map(f => axios.get('/api/fullProcessInventorySTB/options', { params: { field: f } }).then(res => ({ f, d: res.data })).catch(() => ({ f, d: { data: [] } }))))
        for (const r of results) {
          const vals = (r.d.data || []).map(i => i.value)
          if (r.f === '料品名称') this.partNameOptions = vals
          else if (r.f === '料品规格') this.partSpecOptions = vals
          else if (r.f === '当前工序ID') this.processOptions = vals
          else if (r.f === '下一道工序ID') this.nextProcessOptions = vals
        }
      } catch {}
    },
    getFilterParams() {
      const params = {}
      if (this.filters.订单批号) params.订单批号 = this.filters.订单批号.trim()
      if (this.filters.料品编码) params.料品编码 = this.filters.料品编码.trim()
      if (this.filters.part_name) params.料品名称 = this.filters.part_name.trim()
      if (this.filters.part_spec) params.料品规格 = this.filters.part_spec.trim()
      if (this.filters.当前工序ID) params.当前工序ID = this.filters.当前工序ID
      if (this.filters.下一道工序ID) params.下一道工序ID = this.filters.下一道工序ID
      if (this.filters.开始日期) params.开始日期 = this.filters.开始日期
      if (this.filters.结束日期) params.结束日期 = this.filters.结束日期
      return params
    },
    async searchData() {
      this.loading = true; this.currentPage = 1
      try {
        const params = this.getFilterParams()
        const [dataRes, summaryRes] = await Promise.all([
          axios.get('/api/fullProcessInventorySTB', { params }),
          axios.get('/api/fullProcessInventorySTB/summary', { params })
        ])
        if (dataRes.data?.status === 'success') { this.allData = dataRes.data.data || []; this.applyGrouping(); this.total = (this.groupMode === 'none' ? this.allData : this.groupedData).length; this.updateTableData() }
        else this.$message.error('数据获取失败')
        if (summaryRes.data?.status === 'success') {
          const order = ['钻水孔','第一夹','第二夹','倒角','加工螺丝孔','折弯','拈披风','磨角','第三夹','钻排孔','钻芯孔']
          const list = summaryRes.data.data || []
          this.summaryData = list.sort((a, b) => {
            const ia = order.indexOf(a.当前工序ID); const ib = order.indexOf(b.当前工序ID)
            return (ia === -1 ? 999 : ia) - (ib === -1 ? 999 : ib)
          })
        }
      } catch { this.$message.error('数据加载失败') } finally { this.loading = false }
    },
    updateTableData() {
      const source = this.groupMode === 'none' ? this.allData : this.groupedData
      this.total = source.length
      const s = (this.currentPage - 1) * this.pageSize
      this.tableData = source.slice(s, s + this.pageSize)
    },
    onGroupModeChange() {
      this.applyGrouping()
      this.currentPage = 1
      this.updateTableData()
    },
    applyGrouping() {
      if (this.groupMode === 'none') { this.groupedData = []; return }
      const map = new Map()
      for (const row of this.allData) {
        const key = this.groupMode === 'order'
          ? `${row.订单批号}||${row.当前工序ID}`
          : `${row.料品规格}||${row.当前工序ID}`
        if (map.has(key)) {
          const g = map.get(key)
          g.报工数量总和 = Number(g.报工数量总和 || 0) + Number(row.报工数量总和 || 0)
          g.库存 = Number(g.库存 || 0) + Number(row.库存 || 0)
          g.记录数 += 1
        } else {
          map.set(key, {
            订单批号: row.订单批号,
            料品规格: row.料品规格,
            当前工序ID: row.当前工序ID,
            报工数量总和: Number(row.报工数量总和 || 0),
            库存: Number(row.库存 || 0),
            记录数: 1
          })
        }
      }
      this.groupedData = Array.from(map.values())
    },
    handlePageChange(p) { this.currentPage = p; this.updateTableData() },
    handleSizeChange(s) { this.pageSize = s; this.currentPage = 1; this.updateTableData() },
    resetFilters() {
      this.filters = { 订单批号: '', 料品编码: '', part_name: '', part_spec: '', 当前工序ID: '', 下一道工序ID: '', 开始日期: '', 结束日期: '' }
      this.groupMode = 'none'
      this.searchData()
    }
  }
}
</script>

<style scoped>
.report-container { padding: 0; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; padding-top: 10px; }
.summary-row { display: flex; justify-content: flex-end; color: #303133; }
.summary-form { background: #f5f7fa; }
.summary-form-title { font-size: 15px; font-weight: bold; color: #303133; margin-bottom: 12px; }
.table-card { min-height: 100px; }
.pagination-row { display: flex; justify-content: flex-end; margin-top: 16px; }
.mb-4 { margin-bottom: 16px; }
.date-range-inline { display: flex; align-items: center; }
.date-separator { margin: 0 6px; color: #909399; font-size: 14px; white-space: nowrap; }
</style>
