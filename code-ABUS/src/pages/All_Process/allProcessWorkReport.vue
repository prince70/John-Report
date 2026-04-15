<!-- 2025-10-14 全流程工序报工查询（使用临时表 现在改为了报工查询）-->
<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="all-process-work-report">
      <!-- 筛选卡片 -->
      <div class="filter-card">
        <el-form :model="filters" label-width="100px" size="small">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-form-item label="生产车间">
                <el-select v-model="filters.workshop" placeholder="请选择生产车间" clearable filterable
                  @keyup.enter.native="handleSearch">
                  <el-option v-for="item in workshopList" :key="item" :label="item" :value="item" />
                </el-select>
              </el-form-item>
            </el-col>

            <el-col :span="6">
              <el-form-item label="工序">
                <el-select v-model="filters.process" placeholder="请输入或选择工序" clearable filterable
                  @keyup.enter.native="handleSearch">
                  <el-option v-for="item in processList" :key="item" :label="item" :value="item" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="订单批号">
                <el-input v-model="filters.orderNumber" placeholder="请输入订单批号" clearable
                  @keyup.enter.native="handleSearch" />
              </el-form-item>
            </el-col>

          </el-row>

          <el-row :gutter="20">

            <el-col :span="8">
              <el-form-item label="结束时间">
                <el-date-picker class="date-range-picker" v-model="filters.dateRange" type="daterange"
                  format="yyyy-MM-dd" value-format="yyyy-MM-dd" range-separator="-" start-placeholder="结束时间-start"
                  end-placeholder="结束时间-end" :unlink-panels="true" clearable />
              </el-form-item>
            </el-col>

            <el-col :span="8">
              <el-form-item label="姓名">
                <el-select v-model="filters.empName" placeholder="请输入或选择姓名" clearable filterable
                  @keyup.enter.native="handleSearch">
                  <el-option v-for="item in empNameList" :key="item" :label="item" :value="item" />
                </el-select>
              </el-form-item>
            </el-col>

          </el-row>

          <div class="filter-actions">
            <!-- 缓存机制说明已暂时注释 -->
            <!-- <el-tooltip effect="dark" placement="top">
              <div slot="content" style="max-width: 320px; line-height: 1.6;">
                <div style="font-weight: 600; margin-bottom: 8px;">💡 缓存机制说明</div>
                <div>• <strong>数据范围</strong>：仅查询最近 7 天的数据（约2万条）</div>
                <div>• <strong>首次查询</strong>：需要约 1-2 分钟加载数据到缓存</div>
                <div>• <strong>后续查询</strong>：直接使用缓存，响应速度 &lt;1 秒</div>
                <div>• <strong>缓存有效期</strong>：30 分钟自动过期</div>
                <div>• <strong>数据更新</strong>：缓存过期后再次查询会重新加载</div>
              </div>
              <i class="el-icon-info" style="color: #409EFF; font-size: 16px; margin-right: 8px; cursor: pointer;"></i>
            </el-tooltip> -->
            <el-button type="primary" size="small" @click="handleSearch">查询</el-button>
            <el-button size="small" @click="handleReset">重置</el-button>
            <el-button type="success" size="small" @click="handleExport" :loading="exporting">
              <i class="el-icon-download"></i> 导出Excel
            </el-button>
          </div>

        </el-form>
      </div>

      <!-- 提示信息 -->
      <div class="info-summary">
        <div class="info-item">
          <span class="info-label">数据总数：</span>
          <span class="info-value">{{ pagination.table_total.toLocaleString() }} 条</span>
        </div>
        <div class="info-item">
          <span class="info-label" v-if="pagination.limit_applied">默认显示：</span>
          <span class="info-label" v-else>查询结果：</span>
          <span class="info-value">
            <span v-if="pagination.limit_applied">
              前 {{ pagination.filtered_total.toLocaleString() }} 条（共 {{
                pagination.filtered_total_actual.toLocaleString() }} 条）
            </span>
            <span v-else>
              {{ pagination.filtered_total_actual.toLocaleString() }} 条
            </span>
          </span>
        </div>
        <div class="info-item" v-if="pagination.limit_applied">
          <span class="info-label" style="color: #E6A23C;">
            💡 提示：添加筛选条件可查看更多数据
          </span>
        </div>
        <div class="info-item">
          <span class="info-label">当前页：</span>
          <span class="info-value">{{ pagination.page }} / {{ pagination.total_pages }} 页</span>
        </div>
      </div>

      <!-- 数据展示区域 -->
      <div class="table-card">
        <el-table v-loading="loading" :data="tableDataWithSummary" border height="620" style="width: 100%"
          element-loading-text="加载中..." :header-cell-style="{ background: '#409EFF', color: 'white', fontWeight: 600 }"
          :row-class-name="tableRowClassName">

          <!-- 序号列 -->
          <el-table-column type="index" label="序号" width="80" align="center" :index="indexMethod" />

          <!-- 动态渲染每一列 -->
          <el-table-column v-for="column in columns" :key="column.prop" :prop="column.prop" :label="column.label"
            :width="column.width" align="center">
            <template slot-scope="scope">
              <span v-if="scope.row.isSummary">
                <span v-if="column.prop === '工序'">{{ scope.row[column.prop] }}</span>
                <span v-else-if="column.prop === '报工数量' || column.prop === '理论工时'">
                  {{ Number(scope.row[column.prop]).toLocaleString() }}
                </span>
                <span v-else></span>
              </span>
              <span v-else-if="column.isNumeric && scope.row[column.prop] !== null && scope.row[column.prop] !== undefined">
                {{ Number(scope.row[column.prop]).toLocaleString() }}
              </span>
              <span v-else>
                {{ formatDisplayValue(scope.row[column.prop]) }}
              </span>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-wrapper">
          <!-- 分页 -->
          <el-pagination background layout="total, sizes, prev, pager, next, jumper" :current-page="pagination.page"
            :page-size="pagination.page_size" :page-sizes="[50, 100, 200, 500]" :total="pagination.filtered_total"
            @current-change="handlePageChange" @size-change="handleSizeChange" />
        </div>
      </div>

    </div>
  </Layout>
</template>

<script>
import axios from 'axios'
import Layout from '@/components/Layout.vue'
import { eventBus } from '../../eventBus'

// 控制一页展示的数据条数，可选50/100/200/500
const PAGE_SIZE = 50

// 表格列定义，与后端返回字段一一对应
const TABLE_COLUMNS = [
  { prop: '工序', label: '工序', width: 120 },
  { prop: '确定交期', label: '确定交期', width: 120 },
  { prop: '生产车间', label: '生产车间', width: 120, },
  { prop: '工单编号', label: '工单编号', width: 150 },
  { prop: '订单批号', label: '订单批号', width: 150 },
  { prop: '料品编码', label: '料品编码', width: 150 },
  { prop: '生产线编码', label: '生产线编码', width: 120 },
  { prop: '规格型号', label: '规格型号', width: 150 },
  { prop: '员工编号', label: '员工编号', width: 120 },
  { prop: '工号', label: '工号', width: 100 },
  { prop: '姓名', label: '姓名', width: 100 },
  { prop: '报工数量', label: '报工数量', width: 100, isNumeric: true },
  { prop: '报工重量', label: '报工重量', width: 100, isNumeric: true },
  { prop: '返修数量', label: '返修数量', width: 100, isNumeric: true },
  { prop: '每小时产能', label: '每小时产能', width: 100, isNumeric: true },
  { prop: '理论工时', label: '理论工时', width: 100, isNumeric: true },
  { prop: '开始时间', label: '开始时间', width: 150 },
  { prop: '结束时间', label: '结束时间', width: 150 }
]

export default {
  name: 'AllProcessWorkReport',
  components: {
    Layout
  },
  data() {
    return {
      breadcrumbItems: ['All Process 全流程', '工序报工查询'],
      // 查询条件模型，对应筛选表单
      filters: {
        workshop: '',      // 生产车间（下拉选择）
        orderNumber: '',   // 订单批号（模糊查询）
        process: '',       // 工序（模糊查询）
        dateRange: [],     // 结束时间范围
        empName: ''        // 姓名（模糊查询）
      },
      // 车间列表（用于下拉菜单）
      workshopList: [],
      // 工序列表（用于下拉菜单）
      processList: [],
      // 员工姓名列表（用于下拉菜单）
      empNameList: [],
      // 列配置与表格数据
      columns: TABLE_COLUMNS,
      tableData: [],
      // 分页信息，部分字段由后端返回更新
      pagination: {
        page: 1,
        page_size: PAGE_SIZE,
        total_pages: 1,
        filtered_total: 0,
        filtered_total_actual: 0,
        table_total: 0,
        max_records: 1000,
        limit_applied: false
      },
      loading: false,
      exporting: false,
      sidebarMenus: [],
      pageSummaries: {
        finishedQtySum: 0,
        theoryHoursSum: 0
      }
    }
  },
  computed: {
    tableDataWithSummary() {
      if (this.tableData.length === 0) return [];
      
      // 创建统计行
      const summaryRow = {};
      this.columns.forEach(col => {
        summaryRow[col.prop] = null;
      });
      
      // 设置统计行的值
      summaryRow['工序'] = '';
      summaryRow['报工数量'] = this.pageSummaries.finishedQtySum;
      summaryRow['理论工时'] = this.pageSummaries.theoryHoursSum;
      summaryRow['isSummary'] = true;
      
      // 返回原数据加上统计行
      return [...this.tableData, summaryRow];
    }
  },
  created() {
    eventBus.$on('sidebar-Menus-Updated', (menus) => {
      this.sidebarMenus = menus;
      this.generateBreadcrumb(this.$route.path);
    });
    // 页面加载后立即获取车间列表、工序列表、员工姓名列表和首屏数据
    this.fetchWorkshops()
    this.fetchProcesses()
    this.fetchEmpNames()
    this.fetchData()
  },
  watch: {
    'filters.workshop'(newVal) {
      // 当车间变化时，清空工序和姓名选择
      this.filters.process = '';
      this.filters.empName = '';
      // 重新获取工序和姓名列表
      this.fetchProcesses(newVal);
      this.fetchEmpNames(newVal);
    },
    $route(newVal) {
      this.generateBreadcrumb(newVal.path)
    }
  },
  methods: {
    generateBreadcrumb(path) {
      try {
        const menus = this.sidebarMenus;

        const findMenuName = (menus, targetPath) => {
          for (const menu of menus) {
            if (menu.path === targetPath) {
              return menu.name;
            }
            if (menu.children) {
              for (const child of menu.children) {
                if (child.path === targetPath) {
                  return [menu.name, child.name];
                }
              }
            }
          }
          return targetPath.split('/').pop();
        };

        const paths = path.split('/').filter(p => p);
        const menuNames = findMenuName(menus, '/' + paths.join('/'));

        if (Array.isArray(menuNames)) {
          this.breadcrumbItems = menuNames;
        } else {
          this.breadcrumbItems = [menuNames];
        }
      } catch (error) {
        console.error('生成面包屑时出错:', error);
        this.breadcrumbItems = ['全流程工序报工查询'];
      }
    },
    // 将空值统一显示为 '-'，保持界面一致性
    formatDisplayValue(value) {
      if (value === null || value === undefined || value === '') {
        return '-'
      }
      return value
    },
    // 计算序号列的显示值（跨页连续）
    indexMethod(index) {
      // 如果是最后一行（统计行），不显示序号
      if (index === this.tableData.length) {
        return '';
      }
      return (this.pagination.page - 1) * this.pagination.page_size + index + 1
    },
    // 设置表格行的样式
    tableRowClassName({row, rowIndex}) {
      if (row.isSummary) {
        return 'summary-row';
      }
      return '';
    },
    // 获取车间列表
    async fetchWorkshops() {
      try {
        const response = await axios.get('/api/allProcessWorkReport/workshops')
        if (response.data?.status === 'success') {
          this.workshopList = response.data.data || []
          console.log('车间列表加载成功:', this.workshopList.length, '个车间')
        }
      } catch (error) {
        console.error('获取车间列表失败:', error)
        this.$message.warning('车间列表加载失败，请稍后重试')
      }
    },
    // 获取工序列表
    async fetchProcesses(workshop = '') {
      try {
        const params = workshop ? { workshop } : {};
        const response = await axios.get('/api/allProcessWorkReport/processes', { params })
        if (response.data?.status === 'success') {
          this.processList = response.data.data || []
          console.log('工序列表加载成功:', this.processList.length, '个工序')
        }
      } catch (error) {
        console.error('获取工序列表失败:', error)
        this.$message.warning('工序列表加载失败，请稍后重试')
      }
    },
    // 获取员工姓名列表
    async fetchEmpNames(workshop = '') {
      try {
        const params = workshop ? { workshop } : {};
        const response = await axios.get('/api/allProcessWorkReport/empNames', { params })
        if (response.data?.status === 'success') {
          this.empNameList = response.data.data || []
          console.log('员工姓名列表加载成功:', this.empNameList.length, '个姓名')
        }
      } catch (error) {
        console.error('获取员工姓名列表失败:', error)
        this.$message.warning('员工姓名列表加载失败，请稍后重试')
      }
    },
    // 调用后端 API 拉取数据
    async fetchData() {
      this.loading = true
      try {
        const params = {
          page: this.pagination.page,
          page_size: this.pagination.page_size
        }

        if (this.filters.workshop) {
          params.workshop = this.filters.workshop.trim()
        }
        if (this.filters.orderNumber) {
          params.order_number = this.filters.orderNumber.trim()
        }
        if (this.filters.process) {
          params.process = this.filters.process.trim()
        }
        if (this.filters.dateRange && this.filters.dateRange.length === 2) {
          params.start_date = this.filters.dateRange[0]
          params.end_date = this.filters.dateRange[1]
        }
        if (this.filters.empName) {
          params.emp_name = this.filters.empName.trim()
        }

        console.log('查询参数:', params)
        const response = await axios.get('/api/allProcessWorkReport', { params })

        if (response.data?.status === 'success') {
          this.tableData = response.data.data || []
          // 保留当前的page_size，只更新其他分页信息
          const currentPageSize = this.pagination.page_size
          this.pagination = {
            ...this.pagination,
            ...response.data.pagination,
            page_size: currentPageSize
          }
          // 计算当前页的统计
          this.calculatePageSummaries()
          console.log(`数据加载完成，共 ${this.tableData.length} 条记录`)
        } else {
          this.$message.error('数据获取失败')
        }
      } catch (error) {
        console.error('全流程工序报工数据获取失败:', error)
        this.$message.error('数据加载失败，请检查网络连接')
      } finally {
        this.loading = false
      }
    },
    // 点击"查询"按钮或按回车时重置页码重新查询
    handleSearch() {
      this.pagination.page = 1
      this.fetchData()
    },
    // 重置筛选条件并刷新数据
    handleReset() {
      this.filters = {
        workshop: '',
        orderNumber: '',
        process: '',
        dateRange: [],
        empName: ''
      }
      this.pagination.page = 1
      this.fetchData()
    },
    // 翻页时更新页码重新请求数据
    handlePageChange(page) {
      this.pagination.page = page
      this.fetchData()
    },
    // 每页条数变化时重新请求数据
    handleSizeChange(size) {
      this.pagination.page_size = size
      this.pagination.page = 1  // 重置到第一页
      this.fetchData()
    },
    // 计算当前页的统计
    calculatePageSummaries() {
      let finishedQtySum = 0;
      let theoryHoursSum = 0;
      
      this.tableData.forEach(item => {
        if (item['报工数量'] !== null && item['报工数量'] !== undefined) {
          finishedQtySum += Number(item['报工数量']) || 0;
        }
        if (item['理论工时'] !== null && item['理论工时'] !== undefined) {
          theoryHoursSum += Number(item['理论工时']) || 0;
        }
      });
      
      this.pageSummaries = {
        finishedQtySum: finishedQtySum,
        theoryHoursSum: theoryHoursSum
      };
    },
    // 导出Excel
    async handleExport() {
      this.exporting = true;
      try {
        const params = {};
        
        if (this.filters.workshop) {
          params.workshop = this.filters.workshop.trim();
        }
        if (this.filters.orderNumber) {
          params.order_number = this.filters.orderNumber.trim();
        }
        if (this.filters.process) {
          params.process = this.filters.process.trim();
        }
        if (this.filters.dateRange && this.filters.dateRange.length === 2) {
          params.start_date = this.filters.dateRange[0];
          params.end_date = this.filters.dateRange[1];
        }
        if (this.filters.empName) {
          params.emp_name = this.filters.empName.trim();
        }
        
        const response = await axios.get('/api/allProcessWorkReport/export', {
          params,
          responseType: 'blob'
        });
        
        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        
        // 从响应头获取文件名
        const contentDisposition = response.headers['content-disposition'];
        let filename = '报工数据.xlsx';
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="(.+)"/);
          if (filenameMatch) {
            filename = filenameMatch[1];
          }
        }
        
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
        
        this.$message.success('Excel导出成功');
      } catch (error) {
        console.error('导出Excel失败:', error);
        this.$message.error('导出Excel失败，请稍后重试');
      } finally {
        this.exporting = false;
      }
    }
  }
}
</script>

<style scoped>
.filter-card,
.table-card {
  background-color: #fff;
  border-radius: 6px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.filter-card {
  margin-bottom: 16px;
}

.filter-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  align-items: center;
}

.info-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  margin: 12px 0;
  font-size: 14px;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-label {
  color: #606266;
  margin-right: 4px;
}

.info-value {
  font-weight: 600;
  color: #303133;
}

.date-range-picker {
  width: 100% !important;
}

.el-select {
  width: 100%;
}

.table-card {
  overflow: hidden;
}

.el-table {
  font-size: 14px;
}

.el-table__body-wrapper {
  overflow-x: auto;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.summary-row td {
  background-color: #f5f7fa !important;
  color: #409EFF !important;
  font-weight: 600;
}

.summary-row td:nth-child(12),
.summary-row td:nth-child(16) {
  color: #606266 !important;
}
</style>
