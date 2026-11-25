<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <!-- 面包屑右侧导出按钮 -->
    <template #breadcrumb-actions>
      <el-button type="success" @click="exportExcel">导出</el-button>
    </template>
    <!-- 筛选卡片 -->
    <div class="el-card is-always-shadow mb-4">
      <div class="el-card__body">
        <el-form @submit.native.prevent="searchData" label-width="120px">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="工单编号">
                <el-input v-model="searchForm.工单编号" placeholder="请输入工单编号" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="订单批号">
                <el-input v-model="searchForm.订单批号" placeholder="请输入订单批号" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="生产车间">
                <el-select v-model="searchForm.生产车间" placeholder="请选择生产车间" clearable>
                  <el-option label="打磨车间-装配区" value="打磨车间-装配区" />
                  <el-option label="装嵌车间-功能锁区" value="装嵌车间-功能锁区" />
                  <el-option label="装嵌车间-铝门锁区" value="装嵌车间-铝门锁区" />
                  <el-option label="装嵌车间-胆仔锁区" value="装嵌车间-胆仔锁区" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="料品编码">
                <el-input v-model="searchForm.料品编码" placeholder="请输入料品编码" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="预警状态">
                <el-select v-model="searchForm.是否需要预警" placeholder="请选择预警状态" clearable>
                  <el-option label="需要预警" value="需要预警" />
                  <el-option label="正常" value="正常" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="是否打磨工艺">
                <el-select v-model="searchForm.是否打磨工艺" placeholder="请选择是否打磨工艺" clearable>
                  <el-option label="有打磨" value="有打磨" />
                  <el-option label="无打磨" value="无打磨" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="报表日期">
                <el-date-picker v-model="searchForm.报表日期" type="date" placeholder="选择报表日期" value-format="yyyy-MM-dd" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="确定交期">
                <el-date-picker
                  v-model="searchForm.确定交期"
                  type="daterange"
                  range-separator="-"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  value-format="yyyy-MM-dd"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <div class="form-actions">
            <el-button type="default" @click="resetForm">重置</el-button>
            <el-button type="primary" @click="searchData">查询</el-button>
          </div>
        </el-form>
      </div>
    </div>

    <!-- 列表卡片 -->
    <div class="el-card is-always-shadow">
      <div class="el-card__body">
        <el-table
          v-loading="loading"
          element-loading-text="查询中，请稍候..."
          element-loading-spinner="el-icon-loading"
          element-loading-background="rgba(0, 0, 0, 0.8)"
          :data="tableData"
          stripe
          border
          :row-class-name="getRowClassName"
          height="500"
          style="width: 100%"
          :header-cell-style="{ backgroundColor: '#f5f7fa' }"
        >
          <!-- 序号列 -->
          <el-table-column
            type="index"
            label="序号"
            width="60"
            align="center"
            :index="getTableIndex"
          />
          <!-- 动态列 -->
          <el-table-column
            v-for="col in dynamicColumns"
            :key="col.prop"
            :prop="col.prop"
            :label="col.label"
            :min-width="col.minWidth || 120"
          />
        </el-table>
        <div v-if="tableData.length === 0 && !loading" class="no-data">
          暂无数据
        </div>
        <!-- 分页器 -->
        <div class="pagination-wrapper">
          <el-pagination
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="pagination.currentPage"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="pagination.pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="pagination.total">
          </el-pagination>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script>
import Layout from '../../components/Layout.vue';
import axios from 'axios';
import { eventBus } from '../../eventBus';
import * as XLSX from 'xlsx';

export default {
  name: 'AssemblyEarlyList',
  components: { Layout },
  data() {
    return {
      breadcrumbItems: [],
      searchForm: {
        工单编号: '',
        订单批号: '',
        生产车间: '',
        料品编码: '',
        是否需要预警: '',
        是否打磨工艺: '',
        报表日期: '',
        确定交期: []
      },
      allData: [],
      tableData: [],
      dynamicColumns: [],
      loading: false,
      sidebarMenus: [],
      pagination: {
        currentPage: 1,
        pageSize: 20,
        total: 0
      }
    };
  },
  async mounted() {
    await this.fetchAllData();
  },
  created() {
    eventBus.$on('sidebar-Menus-Updated', menus => {
      this.sidebarMenus = menus;
      this.generateBreadcrumb(this.$route.path);
    });
    if (this.sidebarMenus.length === 0) {
      this.breadcrumbItems = ['装嵌预警列表'];
    }
  },
  watch: {
    $route(newVal) {
      this.generateBreadcrumb(newVal.path);
    }
  },
  methods: {
    generateBreadcrumb(path) {
      try {
        const menus = this.sidebarMenus;
        const findMenuName = (menusList, targetPath) => {
          for (const menu of menusList) {
            if (menu.path === targetPath) return menu.name;
            if (menu.children) {
              for (const child of menu.children) {
                if (child.path === targetPath) return [menu.name, child.name];
              }
            }
          }
          return path.split('/').pop();
        };
        const paths = path.split('/').filter(p => p);
        const menuNames = findMenuName(menus, '/' + paths.join('/'));
        this.breadcrumbItems = Array.isArray(menuNames) ? menuNames : [menuNames];
      } catch (err) {
        console.error('生成面包屑失败', err);
        this.breadcrumbItems = ['装嵌预警列表'];
      }
    },
    async fetchAllData() {
      this.loading = true;
      try {
        const params = {
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize,
          ...this.searchForm
        };
        
        // 处理日期范围参数
        if (this.searchForm.确定交期 && Array.isArray(this.searchForm.确定交期) && this.searchForm.确定交期.length === 2) {
          params.确定交期 = this.searchForm.确定交期.join(',');
        } else {
          delete params.确定交期;
        }
        
        // 移除空值参数
        Object.keys(params).forEach(key => {
          if (!params[key] || (Array.isArray(params[key]) && params[key].length === 0)) {
            delete params[key];
          }
        });
        
        const response = await axios.get('/api/assemblyEarlyList', { params });
        if (response.data.status === 'success') {
          this.tableData = response.data.data || [];
          this.pagination.total = response.data.total || 0;
          if (this.tableData.length && !this.dynamicColumns.length) {
            this.dynamicColumns = Object.keys(this.tableData[0]).map(k => ({ prop: k, label: k }));
          }
        } else {
          this.$message.error('获取数据失败');
        }
      } catch (error) {
        console.error('获取数据失败', error);
        this.$message.error('获取数据失败，请检查网络');
      } finally {
        this.loading = false;
      }
    },
    searchData() {
      this.pagination.currentPage = 1; // 重置到第一页
      this.fetchAllData();
    },
    resetForm() {
      Object.keys(this.searchForm).forEach(k => {
        if (k === '确定交期') {
          this.searchForm[k] = [];
        } else {
          this.searchForm[k] = '';
        }
      });
      this.searchData();
    },
    getRowClassName({ row }) {
      const days = parseInt(row['交期_装嵌完成天数']) || 0;
      if (row['是否打磨工艺'] === '有打磨' && days < 5) {
        return 'warning-row';
      }
      if (row['是否打磨工艺'] === '无打磨' && days < 3) {
        return 'warning-row';
      }
      return '';
    },
    getTableIndex(index) {
      return (this.pagination.currentPage - 1) * this.pagination.pageSize + index + 1;
    },
    handleSizeChange(val) {
      this.pagination.pageSize = val;
      this.pagination.currentPage = 1;
      this.fetchAllData();
    },
    handleCurrentChange(val) {
      this.pagination.currentPage = val;
      this.fetchAllData();
    },
    exportExcel() {
      if (!this.tableData.length) {
        this.$message.warning('暂无数据可导出');
        return;
      }
      const ws = XLSX.utils.json_to_sheet(this.tableData);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, '装嵌预警列表');
      const now = new Date();
      const filename = `装嵌预警列表_${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}${String(now.getDate()).padStart(2,'0')}.xlsx`;
      XLSX.writeFile(wb, filename);
    }
  }
};
</script>

<style>
/* 基本样式 */
.mb-4 { margin-bottom: 20px; }
.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
.no-data {
  text-align: center;
  padding: 30px 0;
  color: #909399;
  font-size: 14px;
}
.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  padding: 10px 0;
  border-top: 1px solid #ebeef5;
}

/* 警告行样式 */
.el-table .warning-row {
  background-color: #F56C6C;
  color: #ffffff;
}
.el-table .warning-row td {
  background-color: #F56C6C !important;
  color: #ffffff !important;
}
/* 确保鼠标悬停时样式保持一致 */
.el-table .warning-row:hover > td {
  background-color: #F56C6C !important;
  color: #ffffff !important;
}
.el-table--enable-row-hover .el-table__body tr.warning-row:hover > td {
  background-color: #F56C6C !important;
  color: #ffffff !important;
}
.el-table .warning-row.hover-row > td {
  background-color: #F56C6C !important;
  color: #ffffff !important;
}
</style>
