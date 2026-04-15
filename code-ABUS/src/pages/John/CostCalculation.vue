<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="el-card is-always-shadow mb-4">
      <div class="el-card__body">
        <el-form @submit.native.prevent="filterResults" label-width="100px">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-form-item label="产品ID">
                <el-select
                  v-model="filters.product_id"
                  placeholder="选择产品ID"
                  filterable
                  clearable
                  @change="handleFilterChange('product_id')"
                >
                  <el-option
                    v-for="option in dropdownOptions.product_id"
                    :key="option"
                    :label="option"
                    :value="option"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="产品名称">
                <el-select
                  v-model="filters.product_name"
                  placeholder="选择产品名称"
                  filterable
                  clearable
                  @change="handleFilterChange('product_name')"
                  @input="handleInputChange('product_name')"
                >
                  <el-option
                    v-for="option in dropdownOptions.product_name"
                    :key="option"
                    :label="option"
                    :value="option"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="产品规格">
                <el-select
                  v-model="filters.product_spec"
                  placeholder="选择产品规格"
                  filterable
                  clearable
                  @change="handleFilterChange('product_spec')"
                >
                  <el-option
                    v-for="option in dropdownOptions.product_spec"
                    :key="option"
                    :label="option"
                    :value="option"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="零件ID">
                <el-select
                  v-model="filters.part_id"
                  placeholder="选择零件ID"
                  filterable
                  clearable
                  @change="handleFilterChange('part_id')"
                >
                  <el-option
                    v-for="option in dropdownOptions.part_id"
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
              <el-form-item label="零件名称">
                <el-select
                  v-model="filters.part_name"
                  placeholder="选择零件名称"
                  filterable
                  clearable
                  @change="handleFilterChange('part_name')"
                >
                  <el-option
                    v-for="option in dropdownOptions.part_name"
                    :key="option"
                    :label="option"
                    :value="option"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="工序ID">
                <el-select
                  v-model="filters.processes_id"
                  placeholder="选择工序ID"
                  filterable
                  clearable
                  @change="handleFilterChange('processes_id')"
                >
                  <el-option
                    v-for="option in dropdownOptions.processes_id"
                    :key="option"
                    :label="option"
                    :value="option"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="工序名称">
                <el-select
                  v-model="filters.processes_name"
                  placeholder="选择工序名称"
                  filterable
                  clearable
                  @change="handleFilterChange('processes_name')"
                >
                  <el-option
                    v-for="option in dropdownOptions.processes_name"
                    :key="option"
                    :label="option"
                    :value="option"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <div class="form-actions">
            <el-button type="default" @click="resetFilters">重置</el-button>
            <el-button type="primary" @click="filterResults" :loading="loading">查询</el-button>
          </div>
        </el-form>
      </div>
    </div>

    <!-- 总成本统计区域 -->
    <div class="el-card is-always-shadow mb-4" v-if="hasSearched">
      <div class="el-card__body">
        <div class="cost-summary">
          <div class="summary-item">
            <span class="label">筛选结果总数</span>
            <span class="value">{{ filteredData.length }}</span>
          </div>
          <div class="summary-item">
            <span class="label">总成本</span>
            <span class="value cost-value">¥{{ totalCost.toFixed(4) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据表格区域 -->
    <div class="el-card is-always-shadow" v-if="filteredData.length > 0">
      <div class="el-card__body">
        <div class="section-header">
          <h2>筛选结果</h2>
          <el-button type="success" @click="exportToCSV" :loading="exporting">
            导出CSV
          </el-button>
        </div>
        
        <el-table
          :data="filteredData"
          border
          stripe
          max-height="600"
          style="width: 100%"
          v-loading="loading"
          :header-cell-style="{background: '#eef1f6', color: '#606266'}"
        >
          <el-table-column
            v-for="(config, key) in columnConfigs"
            :key="key"
            :prop="key"
            :label="config.label"
            :width="config.width"
            show-overflow-tooltip
            align="center"
          >
            <template #default="scope">
              <span v-if="key === 'unit_cost'" class="cost-cell">
                ¥{{ scope.row[key] ? Number(scope.row[key]).toFixed(4) : '0.0000' }}
              </span>
              <span v-else>{{ scope.row[key] || '-' }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="el-card is-always-shadow" v-if="!loading && filteredData.length === 0 && hasSearched">
      <div class="el-card__body">
        <el-empty description="没有找到匹配的数据" />
      </div>
    </div>
  </Layout>
</template>

<script>
import Layout from '../../components/Layout.vue';
import axios from 'axios';
import { eventBus } from '../../eventBus';

export default {
  name: 'CostCalculation',
  components: {
    Layout
  },
  data() {
    return {
      breadcrumbItems: [],
      sidebarMenus: [],
      loading: false,
      exporting: false,
      hasSearched: false,
      filters: {
        product_id: '',
        product_name: '',
        product_spec: '',
        part_id: '',
        part_name: '',
        processes_id: '',
        processes_name: '',
        processes_unit: '',
        processes_sort: '',
        unit_cost: ''
      },
      dropdownOptions: {
        product_id: ['全部'],
        product_name: ['全部'],
        product_spec: ['全部'],
        part_id: ['全部'],
        part_name: ['全部'],
        processes_id: ['全部'],
        processes_name: ['全部'],
        processes_unit: ['全部'],
        processes_sort: ['全部'],
        unit_cost: ['全部']
      },
      columnConfigs: {
        product_id: { label: '产品ID', width: 120 },
        product_name: { label: '产品名称', width: 150 },
        product_spec: { label: '产品规格', width: 150 },
        part_id: { label: '零件ID', width: 120 },
        part_name: { label: '零件名称', width: 150 },
        processes_id: { label: '工序ID', width: 120 },
        processes_name: { label: '工序名称', width: 150 },
        processes_unit: { label: '工序单位', width: 100 },
        processes_sort: { label: '工序排序', width: 100 },
        unit_cost: { label: '单位成本', width: 120 }
      },
      filteredData: [],
      totalCost: 0
    }
  },
  created() {
    eventBus.$on('sidebar-Menus-Updated', (menus) => {
      this.sidebarMenus = menus;
      this.generateBreadcrumb(this.$route.path);
    });
    if (this.sidebarMenus.length === 0) {
      this.breadcrumbItems = ['成本计算应用'];
    }
    this.loadAllDropdownOptions();
  },
  watch: {
    $route(newVal) {
      this.generateBreadcrumb(newVal.path);
    }
  },
  async mounted() {
    await this.loadAllDropdownOptions()
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
        this.breadcrumbItems = ['成本计算应用'];
      }
    },
    async loadAllDropdownOptions() {
      try {
        this.loading = true
        const columns = Object.keys(this.columnConfigs)
        
        for (const column of columns) {
          await this.loadDropdownOptions(column)
        }
      } catch (error) {
        console.error('加载下拉选项失败:', error)
        this.$message.error('加载筛选选项失败')
      } finally {
        this.loading = false
      }
    },

    async loadDropdownOptions(column) {
      try {
        // 构建筛选参数，只包含已选择的筛选条件；排除当前列，避免将自身值作为过滤条件
        const filterParams = {}
        Object.keys(this.filters).forEach(key => {
          if (key !== column && this.filters[key] && this.filters[key] !== '全部') {
            filterParams[key] = this.filters[key]
          }
        })
        
        const response = await axios.get(`/api/cost/columns`, {
          params: { 
            column,
            ...filterParams
          }
        })
        
        if (response.data && response.data.values) {
          this.dropdownOptions[column] = ['全部', ...response.data.values]
        }
      } catch (error) {
        console.error(`加载${column}选项失败:`, error)
      }
    },

    async handleFilterChange(column) {
      // 实现筛选条件的级联关系
      if (column === 'product_id' && this.filters.product_id) {
        // 当产品ID改变时，清空下级筛选条件
        this.filters.product_name = ''
        this.filters.product_spec = ''
        this.filters.part_id = ''
        this.filters.part_name = ''
        this.filters.processes_id = ''
        this.filters.processes_name = ''
        this.filters.processes_unit = ''
        this.filters.processes_sort = ''
        this.filters.unit_cost = ''
        
        // 重新加载下级选项
        await Promise.all([
          this.loadDropdownOptions('product_name')
        ])
        
      } else if (column === 'product_name' && this.filters.product_name) {
        // 当产品名称改变时，清空下级筛选条件
        this.filters.product_spec = ''
        this.filters.part_id = ''
        this.filters.part_name = ''
        this.filters.processes_id = ''
        this.filters.processes_name = ''
        this.filters.processes_unit = ''
        this.filters.processes_sort = ''
        this.filters.unit_cost = ''
        
        // 重新加载下级选项
        await Promise.all([
          this.loadDropdownOptions('product_spec'),
          this.loadDropdownOptions('part_id'),
          this.loadDropdownOptions('part_name')
        ])
        
      } else if (column === 'product_spec' && this.filters.product_spec) {
        // 当产品规格改变时，清空下级筛选条件
        this.filters.part_id = ''
        this.filters.part_name = ''
        this.filters.processes_id = ''
        this.filters.processes_name = ''
        this.filters.processes_unit = ''
        this.filters.processes_sort = ''
        this.filters.unit_cost = ''
        
        // 重新加载下级选项
        await Promise.all([
          this.loadDropdownOptions('part_id'),
          this.loadDropdownOptions('part_name')
        ])
        
      } else if (column === 'part_id' && this.filters.part_id) {
        // 当零件ID改变时，清空下级筛选条件
        this.filters.processes_id = ''
        this.filters.processes_name = ''
        this.filters.processes_unit = ''
        this.filters.processes_sort = ''
        this.filters.unit_cost = ''
        
        // 重新加载下级选项
        await Promise.all([
          this.loadDropdownOptions('processes_id'),
          this.loadDropdownOptions('processes_name'),
          this.loadDropdownOptions('processes_unit'),
          this.loadDropdownOptions('processes_sort')
        ])
      } else if (column === 'part_name' && this.filters.part_name) {
        // 当零件名称改变时，清空下级筛选条件
        this.filters.processes_id = ''
        this.filters.processes_name = ''
        this.filters.processes_unit = ''
        this.filters.processes_sort = ''
        this.filters.unit_cost = ''
        
        // 重新加载下级选项
        await Promise.all([
          this.loadDropdownOptions('processes_id'),
          this.loadDropdownOptions('processes_name'),
          this.loadDropdownOptions('processes_unit'),
          this.loadDropdownOptions('processes_sort')
        ])
      } else {
        // 其他列变化时，仅刷新该列（排除自身做过滤）
        await this.loadDropdownOptions(column)
      }

      // 每次筛选变更后，同步刷新所有未锁定的上层列选项，确保选项与当前表单一致
      const columnsToRefresh = Object.keys(this.columnConfigs).filter(c => c !== column)
      for (const col of columnsToRefresh) {
        await this.loadDropdownOptions(col)
      }
    },

    async handleInputChange(column) {
      // 处理输入变化，实现模糊搜索
      if (column === 'product_name') {
        const inputValue = this.filters.product_name
        if (inputValue && inputValue.length > 0) {
          // 过滤匹配的选项
          const filteredOptions = this.dropdownOptions.product_name.filter(
            option => option !== '全部' && 
            option.toLowerCase().includes(inputValue.toLowerCase())
          )
          
          // 临时更新选项
          this.dropdownOptions.product_name = ['全部', ...filteredOptions]
        } else {
          // 如果输入为空，重新加载所有选项
          await this.loadDropdownOptions('product_name')
        }
      }
    },



    async filterResults() {
      try {
        this.loading = true
        this.hasSearched = true
        
        // 构建筛选条件
        const filterParams = {}
        Object.keys(this.filters).forEach(key => {
          if (this.filters[key] && this.filters[key] !== '全部') {
            filterParams[key] = this.filters[key]
          }
        })

        console.log('发送筛选请求，参数:', filterParams)
        const response = await axios.post('/api/cost/filter', filterParams)
        
        console.log('筛选响应:', response.data)
        
        if (response.data) {
          this.filteredData = response.data.data || []
          console.log('筛选结果数量:', this.filteredData.length)
          // 传递筛选条件给总成本计算，如果没有条件则传递空对象
          await this.calculateTotalCost(filterParams)

          // 查询完成后，基于当前条件刷新所有下拉选项，使其动态反映筛选后可选范围
          const columns = Object.keys(this.columnConfigs)
          for (const column of columns) {
            await this.loadDropdownOptions(column)
          }
        }
      } catch (error) {
        console.error('筛选失败:', error)
        this.$message.error('筛选数据失败')
        this.filteredData = []
        this.totalCost = 0
      } finally {
        this.loading = false
      }
    },

    async calculateTotalCost(filterParams) {
      try {
        console.log('计算总成本，筛选条件:', filterParams)
        
        const response = await axios.post('/api/cost/calculate', filterParams)
        
        console.log('总成本计算响应:', response.data)
        
        if (response.data) {
          this.totalCost = response.data.total_cost || 0
          console.log('设置总成本:', this.totalCost)
        }
      } catch (error) {
        console.error('计算总成本失败:', error)
        this.totalCost = 0
      }
    },

    async resetFilters() {
      this.filters = {
        product_id: '',
        product_name: '',
        product_spec: '',
        part_id: '',
        part_name: '',
        processes_id: '',
        processes_name: '',
        processes_unit: '',
        processes_sort: '',
        unit_cost: ''
      }
      this.filteredData = []
      this.totalCost = 0
      this.hasSearched = false
      
      // 重新加载所有下拉选项
      await this.loadAllDropdownOptions()
    },

    async exportToCSV() {
      if (this.filteredData.length === 0) {
        this.$message.warning('没有数据可导出')
        return
      }

      try {
        this.exporting = true
        
        // 准备CSV数据
        const headers = Object.values(this.columnConfigs).map(config => config.label)
        const csvData = [
          headers.join(','),
          ...this.filteredData.map(row => 
            Object.keys(this.columnConfigs).map(key => {
              const value = row[key] || ''
              // 处理包含逗号的值
              return value.toString().includes(',') ? `"${value}"` : value
            }).join(',')
          )
        ].join('\n')

        // 创建下载链接
        const blob = new Blob(['\ufeff' + csvData], { type: 'text/csv;charset=utf-8;' })
        const link = document.createElement('a')
        const url = URL.createObjectURL(blob)
        
        link.setAttribute('href', url)
        link.setAttribute('download', `成本计算数据_${new Date().toISOString().split('T')[0]}.csv`)
        link.style.visibility = 'hidden'
        
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        this.$message.success('CSV文件导出成功')
      } catch (error) {
        console.error('导出失败:', error)
        this.$message.error('导出CSV文件失败')
      } finally {
        this.exporting = false
      }
    }
  }
}
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

.summary-content {
  display: flex;
  gap: 40px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.summary-item .label {
  color: #909399;
  font-size: 14px;
  margin-bottom: 4px;
}

.summary-item .value {
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.cost-value {
  color: #67c23a !important;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  color: #303133;
  font-size: 18px;
}

.cost-cell {
  color: #67c23a;
  font-weight: 500;
}

.cost-summary {
  display: flex;
  gap: 40px;
  align-items: center;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  min-width: 120px;
}

.summary-item .label {
  color: #909399;
  font-size: 14px;
  margin-bottom: 8px;
}

.summary-item .value {
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.cost-value {
  color: #67c23a !important;
}
</style> 