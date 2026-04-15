<!-- 2026.3.10新增报表页面 -->
<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="report-container">
      <div class="el-card is-always-shadow mb-4 filter-card">
        <div class="el-card__body">
          <el-form @submit.native.prevent="searchReport(true)" label-width="90px">
            <el-row :gutter="20">
              <el-col :xs="24" :sm="8">
                <el-form-item label="料品编码">
                  <el-input
                    v-model.trim="filters.item_code"
                    clearable
                    placeholder="请输入料品编码"
                    @keyup.enter.native="searchReport(true)"
                  />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item label="产品名称">
                  <el-input
                    v-model.trim="filters.product_name"
                    clearable
                    placeholder="请输入产品名称"
                    @keyup.enter.native="searchReport(true)"
                  />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item label="产品规格">
                  <el-input
                    v-model.trim="filters.product_spec"
                    clearable
                    placeholder="请输入产品规格"
                    @keyup.enter.native="searchReport(true)"
                  />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item label="工序筛选">
                  <el-select
                    v-model="selectedProcesses"
                    multiple
                    clearable
                    collapse-tags
                    filterable
                    @visible-change="onProcessDropdownVisible"
                    :loading="processOptionLoading"
                    placeholder="请选择工序"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="item in processFilterOptions"
                      :key="item"
                      :label="item"
                      :value="item"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item label="车间筛选">
                  <el-select
                    v-model="selectedWorkshops"
                    multiple
                    clearable
                    collapse-tags
                    filterable
                    @change="markWorkshopSelectionByUser"
                    @visible-change="onWorkshopDropdownVisible"
                    :loading="workshopLoading || workshopOptionLoading"
                    loading-text="车间筛选中..."
                    placeholder="请选择车间"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="item in workshopFilterOptions"
                      :key="item"
                      :label="item"
                      :value="item"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item label="日期字段">
                  <el-select
                    v-model="selectedDateColumn"
                    clearable
                    filterable
                    @visible-change="onDateDropdownVisible"
                    :loading="dateOptionLoading"
                    placeholder="请选择工序日期列"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="item in dateColumnOptions"
                      :key="item"
                      :label="item"
                      :value="item"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item label="日期范围">
                  <el-date-picker
                    v-model="selectedDateRange"
                    type="daterange"
                    :unlink-panels="true"
                    range-separator="至"
                    start-placeholder="开始日期"
                    end-placeholder="结束日期"
                    value-format="yyyy-MM-dd"
                    style="width: 100%"
                    :disabled="!selectedDateColumn"
                    clearable
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <div class="query-tip">页面已自动加载，修改条件后请点击查询</div>
            <div class="form-actions">
              <el-button @click="resetFilters">重置</el-button>
              <el-upload
                action="#"
                :show-file-list="false"
                :before-upload="beforeImport"
                :http-request="handleImportRequest"
                accept=".xlsx,.xlsm,.xltx,.xltm"
              >
                <el-button type="warning" :loading="importLoading">导入Excel</el-button>
              </el-upload>
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

      <div
        class="el-card is-always-shadow table-card"
        v-loading="loading || workshopLoading"
        :element-loading-text="loading ? '加载中...' : '车间筛选中...'"
      >
        <div class="el-card__body">
          <el-table
            v-if="filteredTableData.length"
            :data="filteredTableData"
            border
            stripe
            max-height="650"
            style="width: 100%"
            :header-cell-style="{ background: '#eef1f6', color: '#606266' }"
          >
            <el-table-column
              v-for="col in displayTableColumns"
              :key="col"
              :prop="col"
              :label="col"
              :min-width="getColumnMinWidth(col)"
              show-overflow-tooltip
              align="center"
            >
              <template #header>
                <div class="table-header-wrap">
                  <span>{{ col }}</span>
                  <el-dropdown
                    v-if="isProcessNameColumn(col)"
                    trigger="click"
                    popper-class="process-filter-dropdown"
                    @visible-change="(visible) => onProcessColumnDropdownVisible(col, visible)"
                    @command="(value) => handleProcessColumnFilter(col, value)"
                  >
                    <span class="process-filter-trigger" :class="{ active: !!processColumnFilters[col] }">
                      <i class="el-icon-caret-bottom" />
                    </span>
                    <el-dropdown-menu slot="dropdown">
                      <el-dropdown-item command="__all__">全部工序</el-dropdown-item>
                      <el-dropdown-item
                        v-for="item in getProcessColumnFilterOptions(col)"
                        :key="`${col}-${item}`"
                        :command="item"
                      >
                        {{ item }}
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </el-dropdown>
                </div>
              </template>
              <template #default="scope">
                <span>{{ formatCell(scope.row[col], col) }}</span>
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
  name: 'Report',
  components: {
    Layout
  },
  created() {
    this.initPage()
  },
  computed: {
    workshopColumn() {
      return this.tableColumns.find((col) => /车间/.test(String(col || ''))) || ''
    },
    workshopFilteredData() {
      if (!this.selectedWorkshops.length || !this.workshopColumn) {
        return this.tableData
      }

      const normalizedSelected = this.selectedWorkshops
        .map((item) => this.normalizeWorkshopText(item))
        .filter((item) => item)

      return this.tableData.filter((row) => {
        const fullText = this.normalizeWorkshopText(row?.[this.workshopColumn])
        return normalizedSelected.includes(fullText)
      })
    },
    filteredTableData() {
      let rows = this.processFilteredData

      if (this.selectedDateColumn && this.selectedDateRange.length === 2) {
        const startDate = this.parseDateValue(this.selectedDateRange[0])
        const endDate = this.parseDateValue(this.selectedDateRange[1])
        if (startDate && endDate) {
          // 结束日期按当天 23:59:59 处理
          endDate.setHours(23, 59, 59, 999)

          rows = rows.filter((row) => {
            const rawValue = row?.[this.selectedDateColumn]
            const rowDate = this.parseDateValue(rawValue)
            if (!rowDate) {
              return false
            }
            return rowDate >= startDate && rowDate <= endDate
          })
        }
      }

      const activeColumnFilters = Object.keys(this.processColumnFilters)
        .filter((col) => this.processColumnFilters[col])
      if (!activeColumnFilters.length) {
        return rows
      }

      return rows.filter((row) => {
        return activeColumnFilters.every((col) => {
          const expected = String(this.processColumnFilters[col] || '').trim()
          const actual = String(row?.[col] ?? '').trim()
          return expected && actual === expected
        })
      })
    },
    processFilteredData() {
      if (!this.selectedProcesses.length || !this.processColumns.length) {
        return this.workshopFilteredData
      }

      return this.workshopFilteredData.filter((row) => {
        const rowProcesses = this.processColumns
          .map((col) => row?.[col])
          .filter((val) => val !== null && val !== undefined && String(val).trim() !== '')
          .map((val) => String(val).trim())

        return this.selectedProcesses.some((selected) => rowProcesses.includes(selected))
      })
    },
    filteredTotal() {
      return this.filteredTableData.length
    },
    maxProcessIndexForCurrentWorkshops() {
      if (!this.selectedWorkshops.length || !this.processColumns.length) {
        return null
      }

      let maxIndex = 0
      this.workshopFilteredData.forEach((row) => {
        this.processColumns.forEach((col) => {
          const index = this.getProcessIndex(col)
          if (!index) {
            return
          }
          const text = String(row?.[col] ?? '').trim()
          if (text && index > maxIndex) {
            maxIndex = index
          }
        })
      })

      return maxIndex || null
    },
    displayTableColumns() {
      if (!this.selectedWorkshops.length) {
        return this.tableColumns
      }

      return this.tableColumns.filter((col) => {
        const processIndex = this.getProcessIndex(col)
        const isProcessRelated = this.isProcessRelatedColumn(col)

        // 车间已选时，工序相关列只保留到该车间的最长工序序号
        if (this.maxProcessIndexForCurrentWorkshops && processIndex && processIndex > this.maxProcessIndexForCurrentWorkshops) {
          return false
        }

        // 车间已选时，工序相关列若整列为空，直接隐藏
        if (isProcessRelated) {
          return this.filteredTableData.some((row) => {
            const val = row?.[col]
            return val !== null && val !== undefined && String(val).trim() !== ''
          })
        }

        if (!this.processColumns.includes(col)) {
          return true
        }
        return this.filteredTableData.some((row) => {
          const val = row?.[col]
          return val !== null && val !== undefined && String(val).trim() !== ''
        })
      })
    }
  },
  watch: {
    selectedWorkshops() {
      const showPopup = this.showWorkshopLoadingPopup
      this.showWorkshopLoadingPopup = false
      this.handleWorkshopSelectionChange(showPopup)
    },
    selectedProcesses() {
      this.updateColumnWidthMap()
    },
    selectedDateColumn() {
      if (!this.selectedDateColumn) {
        this.selectedDateRange = []
      }
      this.updateColumnWidthMap()
    },
    selectedDateRange() {
      this.updateColumnWidthMap()
    }
  },
  data() {
    return {
      breadcrumbItems: ['报表页面'],
      loading: false,
      exportLoading: false,
      importLoading: false,
      total: 0,
      tableData: [],
      tableColumns: [],
      columnWidthMap: {},
      processColumns: [],
      processFilterOptions: [],
      processOptionLoading: false,
      selectedProcesses: [],
      dateColumnOptions: [],
      dateOptionLoading: false,
      selectedDateColumn: '',
      selectedDateRange: [],
      workshopFilterOptions: [],
      workshopLoading: false,
      workshopOptionLoading: false,
      showWorkshopLoadingPopup: false,
      currentPage: 1,
      pageSize: 100,
      pageSizeOptions: [50, 100, 200, 500, 1000, 3000, 5000],
      processColumnFilters: {},
      processColumnOptionMap: {},
      processColumnOptionLoadingMap: {},
      lastQuerySignature: '',
      selectedWorkshops: [],
      filters: {
        item_code: '',
        product_name: '',
        product_spec: ''
      }
    }
  },
  methods: {
    async initPage() {
      try {
        await this.loadWorkshopOptions()
        await this.loadProcessDateOptions()
        await this.searchReport(true)
      } catch (error) {
        console.error('页面初始化加载失败:', error)
      }
    },
    normalizeWorkshopText(value) {
      return String(value ?? '')
        .replace(/，/g, ',')
        .replace(/\s+/g, '')
        .trim()
    },
    getDefaultWorkshopSelection(options = []) {
      const defaults = ['开料车间,锁体A车间']
      return defaults.filter((target) => {
        const normalizedTarget = this.normalizeWorkshopText(target)
        return options.some((item) => this.normalizeWorkshopText(item) === normalizedTarget)
      })
    },
    applyDefaultWorkshopSelection(options = []) {
      // 仅在未手动选择时自动套用默认车间，避免覆盖用户操作。
      if (Array.isArray(this.selectedWorkshops) && this.selectedWorkshops.length) {
        return
      }
      const preferred = this.getDefaultWorkshopSelection(options)
      if (preferred.length) {
        this.selectedWorkshops = preferred
      }
    },
    sanitizeMultiValues(values) {
      if (!Array.isArray(values)) {
        return []
      }
      return values
        .map((item) => String(item ?? '').trim())
        .filter((item) => item)
    },
    normalizeWorkshopValues(value) {
      const text = String(value ?? '').trim()
      if (!text) {
        return []
      }
      return text
        .split(/[，,]/)
        .map((item) => item.trim())
        .filter((item) => item)
    },
    async loadWorkshopOptions(force = false) {
      if ((this.workshopFilterOptions.length && !force) || this.workshopOptionLoading) {
        return
      }

      this.workshopOptionLoading = true
      try {
        const params = {
          item_code: this.filters.item_code || undefined,
          product_name: this.filters.product_name || undefined,
          product_spec: this.filters.product_spec || undefined,
          _t: Date.now()
        }
        const { data } = await axios.get('/api/report_sw/report/workshops', { params })
        if (data?.status !== 'success') {
          throw new Error('车间选项状态异常')
        }

        const options = Array.isArray(data.data) ? data.data : []
        const normalized = Array.from(new Set(
          options
            .map((item) => this.normalizeWorkshopText(item))
            .filter((item) => item)
        )).sort((a, b) => a.localeCompare(b, 'zh-CN'))

        this.workshopFilterOptions = normalized
        this.selectedWorkshops = this.selectedWorkshops.filter((item) => normalized.includes(item))
        this.applyDefaultWorkshopSelection(normalized)
      } catch (error) {
        console.error('加载车间选项失败:', error)
      } finally {
        this.workshopOptionLoading = false
      }
    },
    getWorkshopQueryValue() {
      const selected = this.sanitizeMultiValues(this.selectedWorkshops)
      if (!selected.length) {
        return undefined
      }
      // 含逗号值按 JSON 数组整体下发，后端将其作为一个值解析。
      if (selected.some((item) => String(item).includes(','))) {
        return JSON.stringify(selected)
      }
      return selected.join(',')
    },
    getProcessQueryValue() {
      const selected = this.sanitizeMultiValues(this.selectedProcesses)
      if (!selected.length) {
        return undefined
      }
      return selected.join(',')
    },
    getDateStartValue() {
      if (!this.selectedDateColumn || !Array.isArray(this.selectedDateRange) || this.selectedDateRange.length !== 2) {
        return undefined
      }
      return this.selectedDateRange[0] || undefined
    },
    getDateEndValue() {
      if (!this.selectedDateColumn || !Array.isArray(this.selectedDateRange) || this.selectedDateRange.length !== 2) {
        return undefined
      }
      return this.selectedDateRange[1] || undefined
    },
    getQueryParams() {
      const columnFilterValues = {}
      Object.keys(this.processColumnFilters || {}).forEach((col) => {
        const value = String(this.processColumnFilters[col] || '').trim()
        if (value) {
          columnFilterValues[col] = value
        }
      })

      return {
        item_code: this.filters.item_code || undefined,
        product_name: this.filters.product_name || undefined,
        product_spec: this.filters.product_spec || undefined,
        workshop_values: this.getWorkshopQueryValue(),
        process_values: this.getProcessQueryValue(),
        date_column: this.selectedDateColumn || undefined,
        date_start: this.getDateStartValue(),
        date_end: this.getDateEndValue(),
        column_filters: Object.keys(columnFilterValues).length
          ? JSON.stringify(columnFilterValues)
          : undefined
      }
    },
    async fetchReportBatch(params = {}, offset = 0, limit = 2000) {
      const reqParams = {
        ...params,
        offset,
        limit,
        _t: Date.now()
      }
      const { data } = await axios.get('/api/report_sw/report', { params: reqParams })
      if (data?.status !== 'success') {
        throw new Error('返回状态异常')
      }
      return data
    },
    async loadProcessDateOptions(force = false) {
      if ((this.processFilterOptions.length || this.dateColumnOptions.length) && !force) {
        return
      }
      if (this.processOptionLoading || this.dateOptionLoading) {
        return
      }

      this.processOptionLoading = true
      this.dateOptionLoading = true
      try {
        const params = {
          item_code: this.filters.item_code || undefined,
          product_name: this.filters.product_name || undefined,
          product_spec: this.filters.product_spec || undefined,
          workshop_values: this.getWorkshopQueryValue(),
          _t: Date.now()
        }
        const { data } = await axios.get('/api/report_sw/report/filter-options', { params })
        if (data?.status !== 'success') {
          throw new Error('工序/日期选项状态异常')
        }

        const processOptions = Array.isArray(data.process_options)
          ? data.process_options.map((item) => String(item || '').trim()).filter((item) => item)
          : []
        const uniqueProcessOptions = Array.from(new Set(processOptions)).sort((a, b) => a.localeCompare(b, 'zh-CN'))

        const processColumns = Array.isArray(data.process_columns)
          ? data.process_columns
          : []
        const dateColumns = Array.isArray(data.date_columns)
          ? data.date_columns
          : []

        this.processColumns = processColumns.length ? processColumns : this.processColumns
        this.processFilterOptions = uniqueProcessOptions
        this.selectedProcesses = this.selectedProcesses.filter((item) => uniqueProcessOptions.includes(item))

        this.dateColumnOptions = dateColumns
        if (!dateColumns.includes(this.selectedDateColumn)) {
          this.selectedDateColumn = ''
          this.selectedDateRange = []
        }
      } catch (error) {
        console.error('加载工序/日期选项失败:', error)
      } finally {
        this.processOptionLoading = false
        this.dateOptionLoading = false
      }
    },
    onWorkshopDropdownVisible(visible) {
      if (!visible) {
        return
      }
      this.loadWorkshopOptions(true)
    },
    onProcessDropdownVisible(visible) {
      if (!visible) {
        return
      }
      this.loadProcessDateOptions(true)
    },
    onDateDropdownVisible(visible) {
      if (!visible) {
        return
      }
      this.loadProcessDateOptions(true)
    },
    async waitWorkshopFilterDone() {
      while (this.workshopLoading) {
        await new Promise((resolve) => setTimeout(resolve, 30))
      }
    },
    markWorkshopSelectionByUser() {
      this.showWorkshopLoadingPopup = true
    },
    async handleWorkshopSelectionChange(showPopup = false) {
      let loadingInstance = null
      const loadingStartAt = Date.now()
      this.workshopLoading = true

      if (showPopup && this.$loading) {
        loadingInstance = this.$loading({
          lock: true,
          text: '车间筛选中...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.18)'
        })
      }

      // 先渲染 loading，再执行联动计算，避免无反馈。
      await this.$nextTick()
      try {
        this.updateProcessOptions()
        this.loadProcessDateOptions(true)
        this.updateColumnWidthMap()

        // 最短显示时长，避免计算太快导致用户看不到提示。
        const minLoadingMs = 300
        const elapsed = Date.now() - loadingStartAt
        if (elapsed < minLoadingMs) {
          await new Promise((resolve) => setTimeout(resolve, minLoadingMs - elapsed))
        }
      } finally {
        this.workshopLoading = false
        if (loadingInstance) {
          loadingInstance.close()
        }
      }
    },
    async searchReport(resetPage = false) {
      // 若车间选项刚变更，先等待本地预筛选完成，再发起查询。
      await this.waitWorkshopFilterDone()
      if (resetPage) {
        this.currentPage = 1
      }
      this.loading = true
      try {
        const offset = (this.currentPage - 1) * this.pageSize
        const params = this.getQueryParams()
        const querySignature = JSON.stringify(params)
        if (querySignature !== this.lastQuerySignature) {
          this.processColumnOptionMap = {}
          this.lastQuerySignature = querySignature
        }
        const data = await this.fetchReportBatch(params, offset, this.pageSize)

        const rows = Array.isArray(data.data) ? data.data : []
        this.tableData = rows
        this.tableColumns = Array.isArray(data.columns)
          ? data.columns
          : (rows.length ? Object.keys(rows[0]) : [])
        this.total = Number(data.total) || rows.length
        this.pruneProcessColumnFilters()

        await this.loadWorkshopOptions(true)
        this.loadProcessDateOptions(true)
        this.updateWorkshopOptions()
        this.updateProcessOptions()
        this.updateDateColumnOptions()
        this.updateColumnWidthMap()
      } catch (error) {
        console.error('加载报表失败:', error)
        this.$message.error(error?.response?.data?.detail || '加载报表失败')
        this.tableData = []
        this.tableColumns = []
        this.total = 0
        this.columnWidthMap = {}
        this.processColumns = []
        this.processFilterOptions = []
        this.selectedProcesses = []
        this.dateColumnOptions = []
        this.selectedDateColumn = ''
        this.selectedDateRange = []
        this.workshopFilterOptions = []
        this.selectedWorkshops = []
      } finally {
        this.loading = false
      }
    },
    resetFilters() {
      this.filters.item_code = ''
      this.filters.product_name = ''
      this.filters.product_spec = ''
      this.selectedProcesses = []
      this.selectedWorkshops = []
      this.selectedDateColumn = ''
      this.selectedDateRange = []
      this.processColumnFilters = {}
      this.searchReport(true)
    },
    handlePageChange(page) {
      this.currentPage = page
      this.searchReport(false)
    },
    handlePageSizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
      this.searchReport(false)
    },
    async exportExcel() {
      this.exportLoading = true
      try {
        const params = {
          item_code: this.filters.item_code || undefined,
          product_name: this.filters.product_name || undefined,
          product_spec: this.filters.product_spec || undefined
        }

        const response = await axios.get('/api/report_sw/report/export', {
          params,
          responseType: 'blob'
        })

        let filename = `盘点报表_${new Date().toISOString().slice(0, 10)}.xlsx`
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
        let msg = '导出Excel失败'
        const blob = error?.response?.data
        if (blob instanceof Blob) {
          try {
            const text = await blob.text()
            const data = JSON.parse(text)
            msg = data?.detail || msg
          } catch {
            msg = error?.message || msg
          }
        } else {
          msg = error?.response?.data?.detail || error?.message || msg
        }
        this.$message.error(msg)
      } finally {
        this.exportLoading = false
      }
    },
    beforeImport(file) {
      const lowerName = (file?.name || '').toLowerCase()
      const validType = /\.(xlsx|xlsm|xltx|xltm)$/.test(lowerName)
      if (!validType) {
        this.$message.error('请上传 .xlsx/.xlsm 格式文件')
        return false
      }

      const maxSizeMb = 20
      const validSize = file.size / 1024 / 1024 <= maxSizeMb
      if (!validSize) {
        this.$message.error(`文件不能超过${maxSizeMb}MB`)
        return false
      }

      return true
    },
    async handleImportRequest({ file }) {
      this.importLoading = true
      try {
        const formData = new FormData()
        formData.append('file', file)

        const { data } = await axios.post('/api/report_sw/report/import', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        if (data?.status !== 'success') {
          throw new Error('导入失败')
        }

        const addedCount = Array.isArray(data?.added_columns) ? data.added_columns.length : 0
        const droppedCount = Array.isArray(data?.dropped_columns) ? data.dropped_columns.length : 0
        const dbTotal = Number.isFinite(data?.db_total) ? data.db_total : null
        const message = (addedCount > 0 || droppedCount > 0)
          ? `导入成功，已写入${data?.inserted_rows || 0}条，新增${addedCount}列，删除${droppedCount}列${dbTotal !== null ? `，库内共${dbTotal}条` : ''}`
          : `导入成功，已写入${data?.inserted_rows || 0}条数据${dbTotal !== null ? `，库内共${dbTotal}条` : ''}`
        this.$message.success(message)
        this.filters.item_code = ''
        this.filters.product_name = ''
        this.filters.product_spec = ''
        this.selectedWorkshops = []
        this.selectedProcesses = []
        this.selectedDateColumn = ''
        this.selectedDateRange = []
        await this.searchReport(true)
      } catch (error) {
        console.error('导入Excel失败:', error)
        this.$message.error(error?.response?.data?.detail || '导入Excel失败')
      } finally {
        this.importLoading = false
      }
    },
    updateColumnWidthMap() {
      const widthMap = {}
      const sampleRows = this.filteredTableData.slice(0, 80)

      this.displayTableColumns.forEach((col) => {
        let maxLen = String(col || '').length
        sampleRows.forEach((row) => {
          const val = row?.[col]
          const text = val === null || val === undefined ? '' : String(val)
          if (text.length > maxLen) {
            maxLen = text.length
          }
        })

        const baseWidth = maxLen * 16 + 32
        widthMap[col] = Math.max(120, Math.min(baseWidth, 420))
      })

      this.columnWidthMap = widthMap
    },
    updateWorkshopOptions() {
      if (!this.workshopColumn) {
        return
      }

      const set = new Set()
      this.tableData.forEach((row) => {
        const text = this.normalizeWorkshopText(row?.[this.workshopColumn])
        if (text) {
          set.add(text)
        }
      })

      const options = Array.from(set)
      options.sort((a, b) => a.localeCompare(b, 'zh-CN'))

      // 合并接口选项和当前结果选项，避免“当前页无结果”时下拉被清空。
      const merged = Array.from(new Set([...(this.workshopFilterOptions || []), ...options]))
      merged.sort((a, b) => a.localeCompare(b, 'zh-CN'))
      this.workshopFilterOptions = merged
      this.selectedWorkshops = this.selectedWorkshops.filter((item) => merged.includes(item))
      this.applyDefaultWorkshopSelection(merged)
    },
    updateProcessOptions() {
      const processColumns = this.tableColumns.filter((col) => {
        const name = String(col || '')
        const isLegacy = /第\s*\d+\s*道工序/.test(name)
        const isRenamed = /开料尾工序|锁体A首工序/.test(name)
        return (isLegacy || isRenamed) && !/报工数|结束时间|最早结束时间|最晚结束时间|时间|日期/.test(name)
      })

      const valueSet = new Set()
      this.workshopFilteredData.forEach((row) => {
        processColumns.forEach((col) => {
          const val = row?.[col]
          const text = val === null || val === undefined ? '' : String(val).trim()
          if (text) {
            valueSet.add(text)
          }
        })
      })

      const options = Array.from(valueSet)
      options.sort((a, b) => a.localeCompare(b, 'zh-CN'))

      this.processColumns = processColumns
      const mergedOptions = Array.from(new Set([...(this.processFilterOptions || []), ...options]))
      mergedOptions.sort((a, b) => a.localeCompare(b, 'zh-CN'))
      this.processFilterOptions = mergedOptions
      this.selectedProcesses = this.selectedProcesses.filter((item) => mergedOptions.includes(item))
    },
    isProcessNameColumn(colName) {
      const text = String(colName || '').trim()
      const isLegacy = /第\s*\d+\s*道工序/.test(text)
      const isRenamed = /开料尾工序|锁体A首工序/.test(text)
      return (isLegacy || isRenamed) && !/报工数|结束时间|最早结束时间|最晚结束时间|时间|日期/.test(text)
    },
    getProcessColumnFilterOptions(colName) {
      const apiOptions = this.processColumnOptionMap[colName]
      if (Array.isArray(apiOptions) && apiOptions.length) {
        return apiOptions
      }

      const valueSet = new Set()
      this.tableData.forEach((row) => {
        const val = row?.[colName]
        const text = val === null || val === undefined ? '' : String(val).trim()
        if (text) {
          valueSet.add(text)
        }
      })
      return Array.from(valueSet).sort((a, b) => a.localeCompare(b, 'zh-CN'))
    },
    async onProcessColumnDropdownVisible(colName, visible) {
      if (!visible || !this.isProcessNameColumn(colName)) {
        return
      }

      if (this.processColumnOptionLoadingMap[colName]) {
        return
      }

      this.$set(this.processColumnOptionLoadingMap, colName, true)
      try {
        const queryParams = this.getQueryParams()
        const cascadeFilters = this.getCascadeProcessFiltersForColumn(colName)
        queryParams.column_filters = Object.keys(cascadeFilters).length
          ? JSON.stringify(cascadeFilters)
          : undefined

        const params = {
          column_name: colName,
          ...queryParams,
          _t: Date.now()
        }
        const { data } = await axios.get('/api/report_sw/report/column-options', { params })
        if (data?.status !== 'success') {
          throw new Error('列筛选选项状态异常')
        }

        const options = Array.isArray(data.data)
          ? data.data.map((item) => String(item || '').trim()).filter((item) => item)
          : []
        this.$set(this.processColumnOptionMap, colName, options)
      } catch (error) {
        console.error('加载列筛选选项失败:', error)
      } finally {
        this.$set(this.processColumnOptionLoadingMap, colName, false)
      }
    },
    async handleProcessColumnFilter(colName, value) {
      const selected = value === '__all__' ? '' : String(value || '').trim()
      if (!selected) {
        this.$delete(this.processColumnFilters, colName)
      } else {
        this.$set(this.processColumnFilters, colName, selected)
      }

      // 当前置工序筛选变更时，清理后续工序筛选，避免无效条件导致空结果。
      this.clearLaterProcessColumnFilters(colName)

      await this.searchReport(true)
    },
    getCascadeProcessFiltersForColumn(targetCol) {
      const targetIndex = this.getProcessIndex(targetCol)
      if (!targetIndex) {
        return {}
      }

      const filters = {}
      Object.keys(this.processColumnFilters || {}).forEach((col) => {
        if (!this.isProcessNameColumn(col)) {
          return
        }
        const colIndex = this.getProcessIndex(col)
        const value = String(this.processColumnFilters[col] || '').trim()
        if (!colIndex || !value) {
          return
        }
        if (colIndex < targetIndex) {
          filters[col] = value
        }
      })
      return filters
    },
    clearLaterProcessColumnFilters(baseCol) {
      const baseIndex = this.getProcessIndex(baseCol)
      if (!baseIndex) {
        return
      }

      Object.keys(this.processColumnFilters || {}).forEach((col) => {
        const colIndex = this.getProcessIndex(col)
        if (colIndex && colIndex > baseIndex) {
          this.$delete(this.processColumnFilters, col)
        }
      })

      Object.keys(this.processColumnOptionMap || {}).forEach((col) => {
        const colIndex = this.getProcessIndex(col)
        if (colIndex && colIndex > baseIndex) {
          this.$delete(this.processColumnOptionMap, col)
        }
      })
    },
    pruneProcessColumnFilters() {
      const nextFilters = {}
      Object.keys(this.processColumnFilters).forEach((col) => {
        if (this.tableColumns.includes(col) && this.isProcessNameColumn(col)) {
          const val = String(this.processColumnFilters[col] || '').trim()
          if (val) {
            nextFilters[col] = val
          }
        }
      })
      this.processColumnFilters = nextFilters
    },
    updateDateColumnOptions() {
      const options = this.tableColumns.filter((col) => {
        const name = String(col || '')
        return (/第\s*\d+\s*道工序/.test(name) || /开料尾工序|锁体A首工序/.test(name)) && /时间|日期/.test(name)
      })
      this.dateColumnOptions = options
      if (!options.includes(this.selectedDateColumn)) {
        const firstProcessDate = options.find((col) => /第\s*1\s*道工序|开料尾工序/.test(col))
        this.selectedDateColumn = firstProcessDate || options[0] || ''
        if (!this.selectedDateColumn) {
          this.selectedDateRange = []
        }
      }
    },
    parseDateValue(value) {
      if (value === null || value === undefined || value === '') {
        return null
      }
      if (value instanceof Date) {
        return Number.isNaN(value.getTime()) ? null : new Date(value.getTime())
      }
      const text = String(value).trim()
      if (!text) {
        return null
      }

      // 兼容 2026-03-12、2026/03/12、2026-03-12T08:00:00 等格式
      let parsed = new Date(text)
      if (Number.isNaN(parsed.getTime())) {
        parsed = new Date(text.replace(/-/g, '/'))
      }
      return Number.isNaN(parsed.getTime()) ? null : parsed
    },
    isProcessRelatedColumn(colName) {
      const text = String(colName || '').trim()
      return /第\s*\d+\s*道工序|开料尾工序|锁体A首工序/.test(text)
    },
    getProcessIndex(colName) {
      const text = String(colName || '').trim()
      const match = text.match(/^第\s*(\d+)\s*道工序/)
      if (match) {
        return Number(match[1])
      }
      if (/开料尾工序/.test(text)) {
        return 1
      }
      if (/锁体A首工序/.test(text)) {
        return 2
      }
      return null
    },
    getColumnMinWidth(col) {
      return this.columnWidthMap[col] || 120
    },
    formatCell(value, colName = '') {
      if (value === null || value === undefined || value === '') {
        return '-'
      }

      // 时间/日期列中 0 基本是空值占位，按空显示，避免误判为有效时间。
      const isDateTimeCol = /时间|日期/.test(String(colName || ''))
      if (isDateTimeCol && (value === 0 || value === '0' || value === 0.0 || value === '0.0')) {
        return '-'
      }

      return value
    }
  }
}
</script>

<style scoped>
.report-container {
  padding: 8px 12px 12px;
  margin-top: -6px;
}

.mb-4 {
  margin-bottom: 10px;
}

.query-tip {
  margin-bottom: 6px;
  color: #909399;
  font-size: 12px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 2px;
}

.summary-row {
  display: flex;
  justify-content: flex-end;
  color: #303133;
}

.pagination-row {
  margin-top: 50px;
  display: flex;
  justify-content: flex-end;
}

.table-header-wrap {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.process-filter-trigger {
  color: #909399;
  cursor: pointer;
  font-size: 12px;
  line-height: 1;
}

.process-filter-trigger.active {
  color: #409eff;
}

::v-deep(.process-filter-dropdown .el-dropdown-menu) {
  max-height: 320px;
  overflow-y: auto;
}

.filter-card .el-card__body {
  padding: 10px 14px 0px;
}

.summary-card .el-card__body {
  padding: 8px 14px;
}

.table-card .el-card__body {
  padding: 10px 1px;
}

::v-deep(.filter-card .el-form-item) {
  margin-bottom: 10px;
}

::v-deep(.filter-card .el-form-item__label) {
  line-height: 32px;
}

::v-deep(.filter-card .el-form-item__content) {
  line-height: 32px;
}

::v-deep(.filter-card .el-input__inner) {
  height: 32px;
  line-height: 32px;
}

::v-deep(.filter-card .el-range-editor.el-input__inner) {
  height: 32px;
  padding-top: 0;
  padding-bottom: 0;
}
</style>