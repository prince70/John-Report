<template>
    <Layout :breadcrumbItems="breadcrumbItems">
      <div class="el-card is-always-shadow mb-4">
        <div class="el-card__body">
          <el-form @submit.native.prevent="applyFilters" label-width="100px">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="订单批号">
                  <el-input v-model="filterForm.订单批号" placeholder="请输入订单批号" clearable></el-input>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="确定交期">
                  <el-date-picker
                    v-model="filterForm.确定交期"
                    type="date"
                    placeholder="选择交期"
                    format="yyyy-MM-dd"
                    value-format="yyyy-MM-dd"
                    clearable>
                  </el-date-picker>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="报工完成时间">
                  <el-date-picker
                    v-model="filterForm.报工完成时间"
                    type="date"
                    placeholder="选择完成时间"
                    format="yyyy-MM-dd"
                    value-format="yyyy-MM-dd"
                    clearable>
                  </el-date-picker>
                </el-form-item>
              </el-col>
            </el-row>
            <div class="form-actions">
              <el-button type="default" @click="resetFilters">重置</el-button>
              <el-button type="primary" @click="applyFilters">查询</el-button>
            </div>
          </el-form>
        </div>
      </div>
  
      <div class="el-card is-always-shadow">
        <div class="el-card__body">
            <el-table
              :data="paginatedDisplayedData"  style="width: 100%"
              border
              stripe
              v-loading="loading"
              :header-cell-style="{background: '#eef1f6', color: '#606266'}">
              <el-table-column prop="工单编号" label="工单编号" align="center" width="220"></el-table-column>
              <el-table-column prop="订单批号" label="订单批号" align="center" width="150"></el-table-column>
              <el-table-column prop="料品编码" label="料品编码" align="center" width="120"></el-table-column>
              <el-table-column prop="生产线编号" label="生产线编号" align="center" width="120"></el-table-column>
              <el-table-column prop="规格型号" label="规格型号" align="center" width="220"></el-table-column>
              <el-table-column prop="工号" label="工号" align="center" width="120"></el-table-column>
              <el-table-column prop="姓名" label="姓名" align="center" width="100"></el-table-column>
              <el-table-column prop="报工数量" label="报工数量" align="center" width="100"></el-table-column>
              <el-table-column prop="返修数量" label="返修数量" align="center" width="100"></el-table-column>
              <el-table-column prop="报废数量" label="报废数量" align="center" width="100"></el-table-column>
              <el-table-column label="报工开始时间" align="center" width="180">
                <template slot-scope="scope">
                  {{ formatDate(scope.row.报工开始时间) }}
                </template>
              </el-table-column>
              <el-table-column label="报工结束时间" align="center" width="180">
                <template slot-scope="scope">
                  {{ formatDate(scope.row.报工结束时间) }}
                </template>
              </el-table-column>
              <el-table-column label="确定交期" align="center" width="180">
                <template slot-scope="scope">
                  {{ formatDate(scope.row.确定交期) }}
                </template>
              </el-table-column>
              <el-table-column label="提前天数" align="center" width="100">
                <template slot-scope="scope">
                  {{ calculateDaysDifference(scope.row.报工结束时间, scope.row.确定交期) }}
                </template>
              </el-table-column>
            </el-table>
  
            <div class="pagination-container">
              <el-pagination
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
                :current-page="currentPage"
                :page-sizes="[10, 20, 50, 100]"
                :page-size="pageSize"
                layout="total, sizes, prev, pager, next, jumper"
                :total="totalDisplayedItems"> </el-pagination>
            </div>
          </div>
        </div>
    </Layout>
</template>
  
<script>
  import Layout from '../../components/Layout.vue';
  import axios from 'axios';
  import { eventBus } from '../../eventBus';
  
  export default {
    name: 'AssemblyEarly',
    components: {
      Layout
    },
    data() {
      return {
        breadcrumbItems: [],
        tableData: [], // This will hold the raw data fetched from the API
        displayedTableData: [], // This will hold the data after applying filters
        loading: false,
        currentPage: 1,
        pageSize: 10,
        totalItems: 0, // Total items from API (raw data length)
        totalDisplayedItems: 0, // Total items after filtering
        sidebarMenus: [],
        filterForm: {
          订单批号: '',
          确定交期: '',
          报工完成时间: ''
        }
      };
    },
    computed: {
      paginatedDisplayedData() {
        const startIndex = (this.currentPage - 1) * this.pageSize;
        const endIndex = startIndex + this.pageSize;
        return this.displayedTableData.slice(startIndex, endIndex);
      }
    },
    created() {
      eventBus.$on('sidebar-Menus-Updated', (menus) => {
        this.sidebarMenus = menus;
        this.generateBreadcrumb(this.$route.path);
      });
      if (this.sidebarMenus.length === 0) {
        this.breadcrumbItems = ['装嵌提前一周完成数据'];
      }
      this.fetchData();
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
          this.breadcrumbItems = ['装嵌提前一周完成数据'];
        }
      },
      fetchData() {
        this.loading = true;
  
        // 从后端API获取数据
        axios.get('/api/warning/assembly-early')
          .then(response => {
            if (response.data.status === 'success') {
              this.tableData = response.data.data; // Store raw data
              this.totalItems = response.data.data.length; // Total raw items
  
              // Initially apply filters to display all data
              this.applyFilters();
            } else {
              this.$message.error('获取数据失败: ' + (response.data.message || '未知错误'));
              console.error('获取数据失败:', response.data.message);
            }
            this.loading = false;
          })
          .catch(error => {
            console.error('获取数据失败:', error);
            this.$message.error('获取数据失败，请检查网络或后端服务。');
            this.loading = false;
          });
      },
      formatDate(dateString) {
        if (!dateString) return '';
        try {
          const date = new Date(dateString);
          if (isNaN(date.getTime())) return dateString; // Return original if invalid date
  
          return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
        } catch (e) {
          console.error('Date formatting error:', e);
          return dateString; // Return original on error
        }
      },
      calculateDaysDifference(startDateStr, endDateStr) {
        if (!startDateStr || !endDateStr) return '';
  
        try {
          const startDate = new Date(startDateStr);
          const endDate = new Date(endDateStr);
  
          if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) return '';
  
          // Calculate the difference in days
          const diffTime = Math.abs(endDate.getTime() - startDate.getTime()); // Use getTime() for reliable ms diff
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
          return diffDays;
        } catch (e) {
          console.error('Date calculation error:', e);
          return '';
        }
      },
      handleSizeChange(val) {
        this.pageSize = val;
        this.currentPage = 1; // Reset to first page when changing page size
      },
      handleCurrentChange(val) {
        this.currentPage = val;
      },
      applyFilters() {
        // Filter the raw tableData based on the filterForm
        this.displayedTableData = this.tableData.filter(row => {
          // 订单批号过滤
          if (this.filterForm.订单批号 && !row.订单批号.includes(this.filterForm.订单批号)) {
            return false;
          }
          // 确定交期过滤
          if (this.filterForm.确定交期) {
            const rowDate = row.确定交期 ? row.确定交期.substr(0, 10) : '';
            if (rowDate !== this.filterForm.确定交期) return false;
          }
          // 报工完成时间过滤 (对应 row.报工结束时间)
          if (this.filterForm.报工完成时间) {
            const rowFinish = row.报工结束时间 ? row.报工结束时间.substr(0, 10) : '';
            if (rowFinish !== this.filterForm.报工完成时间) return false;
          }
          return true;
        });
  
        // Update totalDisplayedItems and reset current page
        this.totalDisplayedItems = this.displayedTableData.length;
        this.currentPage = 1;
      },
      resetFilters() {
        this.filterForm.订单批号 = '';
        this.filterForm.确定交期 = '';
        this.filterForm.报工完成时间 = '';
        this.applyFilters(); // Re-apply filters to show all data
      }
    }
  };
</script>
  
<style scoped> 
  .panel {
    background-color: #fff;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  }
  
  .panel-header {
    padding: 15px 20px;
    border-bottom: 1px solid #ebeef5;
  }
  
  .panel-header h2 {
    font-size: 18px;
    color: #303133;
    margin: 0;
    font-weight: 500;
  }
  
  .panel-body {
    padding: 20px;
  }
  
  .pagination-container {
    margin-top: 20px;
    text-align: right;
  }
  
  .mb-4 {
    margin-bottom: 20px;
  }
  .form-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }
</style>