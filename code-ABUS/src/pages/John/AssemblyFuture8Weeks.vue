<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <template #breadcrumb-actions>
      <el-button type="success" @click="exportExcel">导出</el-button>
    </template>

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
                <el-select
                  v-model="searchForm.生产车间"
                  placeholder="请选择生产车间"
                  clearable
                  filterable
                >
                  <el-option
                    v-for="item in workshopOptions"
                    :key="item"
                    :label="item"
                    :value="item"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="料品编码">
                <el-input v-model="searchForm.料品编码" placeholder="请输入料品编码" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="生产线编号">
                <el-select
                  v-model="searchForm.生产线编号"
                  placeholder="请选择生产线编号"
                  clearable
                  filterable
                  @change="handleLineChange"
                >
                  <el-option
                    v-for="line in filteredLineOptions"
                    :key="line"
                    :label="line"
                    :value="line"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="料品名称">
                <el-select
                  ref="productSelect"
                  v-model="searchForm.料品名称"
                  placeholder="请选择料品名称"
                  clearable
                  filterable
                  @change="handleProductChange"
                >
                  <el-option
                    v-for="product in filteredProductOptions"
                    :key="product"
                    :label="product"
                    :value="product"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="确定交期">
                <el-date-picker
                  v-model="searchForm.确定交期"
                  type="daterange"
                  :unlink-panels="true"
                  range-separator="-"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  value-format="yyyy-MM-dd"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <div v-if="searchForm.生产线编号" class="linkage-preview">
            <span class="preview-label">可生产产品：</span>
            <template v-if="filteredProductOptions.length">
              <el-tag
                v-for="product in filteredProductOptions.slice(0, 12)"
                :key="product"
                class="preview-tag"
                size="mini"
                @click="selectProductFromPreview(product)"
              >
                {{ product }}
              </el-tag>
              <span v-if="filteredProductOptions.length > 12" class="preview-more">
                还有 {{ filteredProductOptions.length - 12 }} 个产品，请在下拉中查看
              </span>
            </template>
            <span v-else class="preview-empty">该生产线在资源表中未匹配到可生产产品</span>
          </div>

          <div class="form-actions">
            <el-button type="default" @click="resetForm">重置</el-button>
            <el-button type="primary" @click="searchData">查询</el-button>
          </div>
        </el-form>
      </div>
    </div>

    <div class="el-card is-always-shadow mb-4">
      <div class="el-card__body">
        <div class="section-title">工单明细表</div>
        <el-table
          v-loading="loading"
          element-loading-text="查询中，请稍候..."
          element-loading-spinner="el-icon-loading"
          element-loading-background="rgba(0, 0, 0, 0.35)"
          :data="tableData"
          stripe
          border
          highlight-current-row
          :height="workOrderTableHeight"
          style="width: 100%"
          :header-cell-style="{ backgroundColor: '#f5f7fa' }"
          @row-click="handleWorkOrderRowClick"
        >
          <el-table-column
            type="index"
            label="序号"
            width="60"
            align="center"
            :index="getTableIndex"
          />
          <el-table-column
            v-for="col in dynamicColumns"
            :key="col.prop"
            :prop="col.prop"
            :label="col.label"
            :min-width="col.minWidth || 120"
          >
            <template slot-scope="{ row }">
              <span
                v-if="isRemarkColumn(col.prop)"
                class="remark-preview"
                :title="row[col.prop] || ''"
                @click="openRemarkDialog(col.label, row[col.prop])"
              >
                {{ formatRemarkPreview(row[col.prop]) }}
              </span>
              <span v-else>{{ row[col.prop] }}</span>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="tableData.length === 0 && !loading" class="no-data">暂无数据</div>

        <div class="pagination-wrapper">
          <el-pagination
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="pagination.currentPage"
            :page-sizes="[10, 20, 50, 100, 200, 500]"
            :page-size="pagination.pageSize"
            :pager-count="11"
            background
            layout="total, sizes, prev, pager, next, jumper"
            :total="pagination.total"
          />
        </div>
      </div>
    </div>

    <div class="el-card is-always-shadow" ref="resourceSection">
      <div class="el-card__body">
        <div class="section-title">
          生产资源表
          <span class="section-subtitle">点击下表行可回填上方筛选并查询</span>
        </div>
        <el-table
          v-loading="resourceLoading"
          element-loading-text="资源加载中，请稍候..."
          element-loading-spinner="el-icon-loading"
          element-loading-background="rgba(0, 0, 0, 0.25)"
          :data="resourceData"
          stripe
          border
          highlight-current-row
          :height="resourceTableHeight"
          style="width: 100%"
          :header-cell-style="{ backgroundColor: '#f5f7fa' }"
          @row-click="handleResourceRowClick"
        >
          <el-table-column
            type="index"
            label="序号"
            width="60"
            align="center"
            :index="getResourceTableIndex"
          />
          <el-table-column
            v-for="col in resourceColumns"
            :key="col.prop"
            :prop="col.prop"
            :label="col.label"
            :min-width="col.minWidth || 120"
          />
        </el-table>

        <div v-if="resourceData.length === 0 && !resourceLoading" class="no-data">暂无资源数据</div>

        <div class="pagination-wrapper">
          <el-pagination
            @size-change="handleResourceSizeChange"
            @current-change="handleResourceCurrentChange"
            :current-page="resourcePagination.currentPage"
            :page-sizes="[20, 50, 100, 200, 500, 1000]"
            :page-size="resourcePagination.pageSize"
            :pager-count="11"
            background
            layout="total, sizes, prev, pager, next, jumper"
            :total="resourcePagination.total"
          />
        </div>
      </div>
    </div>

    <el-dialog
      title="订单备注详情"
      :visible.sync="remarkDialogVisible"
      width="680px"
    >
      <div class="remark-dialog-label">{{ remarkDialogLabel }}</div>
      <div class="remark-dialog-content">{{ remarkDialogContent || '无备注内容' }}</div>
      <div slot="footer">
        <el-button type="primary" @click="remarkDialogVisible = false">关闭</el-button>
      </div>
    </el-dialog>
  </Layout>
</template>

<script>
import axios from 'axios';
import * as XLSX from 'xlsx';
import Layout from '../../components/Layout.vue';
import { eventBus } from '../../eventBus';

export default {
  name: 'AssemblyFuture8Weeks',
  components: { Layout },
  data() {
    return {
      breadcrumbItems: [],
      searchForm: {
        工单编号: '',
        订单批号: '',
        生产车间: '',
        料品编码: '',
        生产线编号: '',
        料品名称: '',
        确定交期: []
      },
      tableData: [],
      dynamicColumns: [],
      lineOptions: [],
      productOptions: [],
      lineToProducts: {},
      productToLines: {},
      filteredLineOptions: [],
      filteredProductOptions: [],
      workshopOptions: [
        '打磨车间',
        '装嵌车间-功能锁区',
        '装嵌车间-铝门锁区',
        '装嵌车间-胆仔锁区'
      ],
      remarkDialogVisible: false,
      remarkDialogLabel: '订单备注',
      remarkDialogContent: '',
      workOrderTableHeight: '420px',
      resourceTableHeight: '320px',
      loading: false,
      resourceLoading: false,
      sidebarMenus: [],
      resourceData: [],
      resourceColumns: [],
      resourceLineColumn: 'ResourceExternalId',
      resourceProductColumn: 'Productname',
      pagination: {
        currentPage: 1,
        pageSize: 20,
        total: 0
      },
      resourcePagination: {
        currentPage: 1,
        pageSize: 50,
        total: 0
      }
    };
  },
  async mounted() {
    await this.fetchLinkageOptions();
    await this.fetchWorkshopOptions();
    this.updateTableHeight();
    window.addEventListener('resize', this.updateTableHeight);
    await Promise.all([this.fetchData(), this.fetchResourceData()]);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.updateTableHeight);
  },
  created() {
    eventBus.$on('sidebar-Menus-Updated', menus => {
      this.sidebarMenus = menus;
      this.generateBreadcrumb(this.$route.path);
    });
    if (this.sidebarMenus.length === 0) {
      this.breadcrumbItems = ['装嵌未来8周需求明细'];
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

        const paths = path.split('/').filter(Boolean);
        const menuNames = findMenuName(this.sidebarMenus, '/' + paths.join('/'));
        this.breadcrumbItems = Array.isArray(menuNames) ? menuNames : [menuNames];
      } catch (err) {
        console.error('生成面包屑失败', err);
        this.breadcrumbItems = ['装嵌未来8周需求明细'];
      }
    },
    updateTableHeight() {
      // 预留筛选区、分页区和内边距，上下双表按比例占满页面
      const available = Math.max(560, window.innerHeight - 500);
      const top = Math.floor(available * 0.55);
      const bottom = available - top;
      this.workOrderTableHeight = `${Math.max(260, top)}px`;
      this.resourceTableHeight = `${Math.max(220, bottom)}px`;
    },
    isRemarkColumn(prop) {
      return prop === '订单备注' || prop === '备注';
    },
    formatRemarkPreview(value) {
      const text = value ? String(value) : '';
      if (!text) return '-';
      const limit = 22;
      return text.length > limit ? `${text.slice(0, limit)}...` : text;
    },
    openRemarkDialog(label, value) {
      const text = value ? String(value).trim() : '';
      if (!text) return;
      this.remarkDialogLabel = label || '订单备注';
      this.remarkDialogContent = text;
      this.remarkDialogVisible = true;
    },
    async fetchData() {
      this.loading = true;
      try {
        const params = {
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize,
          ...this.searchForm
        };

        if (Array.isArray(this.searchForm.确定交期) && this.searchForm.确定交期.length === 2) {
          params.确定交期 = this.searchForm.确定交期.join(',');
        } else {
          delete params.确定交期;
        }

        Object.keys(params).forEach(key => {
          if (!params[key] || (Array.isArray(params[key]) && params[key].length === 0)) {
            delete params[key];
          }
        });

        const response = await axios.get('/api/assemblyFuture8Weeks', { params });
        if (response.data.status === 'success') {
          this.tableData = response.data.data || [];
          this.pagination.total = response.data.total || 0;
          if (this.tableData.length) {
            this.dynamicColumns = Object.keys(this.tableData[0]).map(k => ({ prop: k, label: k }));
          } else {
            this.dynamicColumns = [];
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
    async fetchResourceData() {
      this.resourceLoading = true;
      try {
        const params = {
          page: this.resourcePagination.currentPage,
          pageSize: this.resourcePagination.pageSize,
          line: this.searchForm.生产线编号 || undefined,
          product: this.searchForm.料品名称 || undefined
        };

        const response = await axios.get('/api/productRules', { params });
        if (response.data && response.data.status === 'success') {
          this.resourceData = response.data.data || [];
          this.resourcePagination.total = response.data.total || 0;
          if (this.resourceData.length) {
            this.resourceColumns = Object.keys(this.resourceData[0]).map(k => ({ prop: k, label: k }));
          } else {
            this.resourceColumns = [];
          }
        } else {
          this.$message.error('资源表获取失败');
        }
      } catch (error) {
        console.error('获取资源表失败', error);
        this.$message.error('资源表获取失败，请检查网络');
      } finally {
        this.resourceLoading = false;
      }
    },
    async fetchLinkageOptions() {
      try {
        const response = await axios.get('/api/productRules/linkage-options');
        if (response.data && response.data.status === 'success') {
          this.lineOptions = Array.isArray(response.data.lineOptions) ? response.data.lineOptions : [];
          this.productOptions = Array.isArray(response.data.productOptions) ? response.data.productOptions : [];
          this.lineToProducts = response.data.lineToProducts || {};
          this.productToLines = response.data.productToLines || {};
          this.resourceLineColumn = response.data.lineColumn || this.resourceLineColumn;
          this.resourceProductColumn = response.data.productColumn || this.resourceProductColumn;
          this.filteredLineOptions = [...this.lineOptions];
          this.filteredProductOptions = [...this.productOptions];
        } else {
          this.lineOptions = [];
          this.productOptions = [];
          this.lineToProducts = {};
          this.productToLines = {};
          this.filteredLineOptions = [];
          this.filteredProductOptions = [];
        }
      } catch (error) {
        this.lineOptions = [];
        this.productOptions = [];
        this.lineToProducts = {};
        this.productToLines = {};
        this.filteredLineOptions = [];
        this.filteredProductOptions = [];
        console.error('获取生产线与产品联动选项失败', error);
      }
    },
    async fetchWorkshopOptions() {
      try {
        const response = await axios.get('/api/assemblyFuture8Weeks/workshop-options');
        if (response.data && response.data.status === 'success' && Array.isArray(response.data.data)) {
          this.workshopOptions = response.data.data;
        }
      } catch (error) {
        console.error('获取生产车间选项失败', error);
      }
    },
    handleLineChange(line) {
      if (!line) {
        this.filteredProductOptions = [...this.productOptions];
        if (this.searchForm.料品名称) {
          this.handleProductChange(this.searchForm.料品名称);
        }
        this.resourcePagination.currentPage = 1;
        this.fetchResourceData();
        return;
      }

      const products = this.lineToProducts[line] || [];
      this.filteredProductOptions = products;
      if (this.searchForm.料品名称 && !products.includes(this.searchForm.料品名称)) {
        this.searchForm.料品名称 = '';
      }

      if (line && products.length) {
        this.$nextTick(() => {
          const productSelect = this.$refs.productSelect;
          if (productSelect && typeof productSelect.toggleMenu === 'function') {
            productSelect.toggleMenu();
          }
        });
      }

      this.resourcePagination.currentPage = 1;
      this.fetchResourceData();
    },
    handleProductChange(product) {
      if (!product) {
        this.filteredLineOptions = [...this.lineOptions];
        if (this.searchForm.生产线编号) {
          this.handleLineChange(this.searchForm.生产线编号);
        }
        this.resourcePagination.currentPage = 1;
        this.fetchResourceData();
        return;
      }

      const lines = this.productToLines[product] || [];
      this.filteredLineOptions = lines;
      if (this.searchForm.生产线编号 && !lines.includes(this.searchForm.生产线编号)) {
        this.searchForm.生产线编号 = '';
      }

      this.resourcePagination.currentPage = 1;
      this.fetchResourceData();
    },
    selectProductFromPreview(product) {
      this.searchForm.料品名称 = product;
      this.handleProductChange(product);
    },
    searchData() {
      this.pagination.currentPage = 1;
      this.resourcePagination.currentPage = 1;
      this.fetchData();
      this.fetchResourceData();
    },
    resetForm() {
      this.searchForm = {
        工单编号: '',
        订单批号: '',
        生产车间: '',
        料品编码: '',
        生产线编号: '',
        料品名称: '',
        确定交期: []
      };
      this.filteredLineOptions = [...this.lineOptions];
      this.filteredProductOptions = [...this.productOptions];
      this.searchData();
    },
    handleWorkOrderRowClick(row) {
      const line = row['生产线编号'] || '';
      if (!line) return;

      // 从工单选择后，优先展示该生产线可生产的全部产品，不预先锁定产品
      this.searchForm.生产线编号 = line;
      this.searchForm.料品名称 = '';
      this.handleLineChange(line);
      this.resourcePagination.currentPage = 1;
      this.fetchResourceData();
    },
    handleResourceRowClick(row) {
      const line = row[this.resourceLineColumn] || row['ResourceExternalId'] || '';
      const product = row[this.resourceProductColumn] || row['Productname'] || row['ProductName'] || '';

      if (line) {
        this.searchForm.生产线编号 = String(line);
        this.handleLineChange(this.searchForm.生产线编号);
      }

      if (product) {
        this.searchForm.料品名称 = String(product);
        this.handleProductChange(this.searchForm.料品名称);
      }

      this.searchData();
    },
    getTableIndex(index) {
      return (this.pagination.currentPage - 1) * this.pagination.pageSize + index + 1;
    },
    getResourceTableIndex(index) {
      return (this.resourcePagination.currentPage - 1) * this.resourcePagination.pageSize + index + 1;
    },
    handleSizeChange(val) {
      this.pagination.pageSize = val;
      this.pagination.currentPage = 1;
      this.fetchData();
    },
    handleCurrentChange(val) {
      this.pagination.currentPage = val;
      this.fetchData();
    },
    handleResourceSizeChange(val) {
      this.resourcePagination.pageSize = val;
      this.resourcePagination.currentPage = 1;
      this.fetchResourceData();
    },
    handleResourceCurrentChange(val) {
      this.resourcePagination.currentPage = val;
      this.fetchResourceData();
    },
    exportExcel() {
      if (!this.tableData.length) {
        this.$message.warning('暂无数据可导出');
        return;
      }
      const ws = XLSX.utils.json_to_sheet(this.tableData);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, '装嵌未来8周需求明细');
      const now = new Date();
      const filename = `装嵌未来8周需求明细_${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}.xlsx`;
      XLSX.writeFile(wb, filename);
    }
  }
};
</script>

<style>
.mb-4 {
  margin-bottom: 20px;
}
.section-title {
  display: flex;
  align-items: center;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 10px;
}
.section-subtitle {
  margin-left: 10px;
  font-size: 12px;
  color: #909399;
  font-weight: 400;
}
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
.linkage-preview {
  margin: 4px 0 16px;
  padding: 8px 10px;
  background: #f8fbff;
  border: 1px solid #dbe9ff;
  border-radius: 4px;
}
.preview-label {
  color: #409eff;
  font-weight: 600;
  margin-right: 6px;
}
.preview-tag {
  margin-right: 6px;
  margin-bottom: 6px;
  cursor: pointer;
}
.preview-more {
  margin-left: 4px;
  color: #909399;
  font-size: 12px;
}
.preview-empty {
  color: #f56c6c;
  font-size: 12px;
}
.remark-preview {
  display: inline-block;
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #409eff;
  cursor: pointer;
}
.remark-dialog-label {
  margin-bottom: 10px;
  font-weight: 600;
  color: #303133;
}
.remark-dialog-content {
  max-height: 420px;
  overflow: auto;
  white-space: pre-wrap;
  line-height: 1.7;
  color: #606266;
}
</style>
