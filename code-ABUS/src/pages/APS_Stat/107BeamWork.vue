<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <!-- 筛选表单 -->
    <div class="el-card is-always-shadow mb-4">
      <div class="el-card__body">
        <el-form @submit.native.prevent="searchData" label-width="120px">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="锁类分区">
                <el-select v-model="searchForm.锁类分区" placeholder="请选择锁类分区" clearable>
                  <el-option v-for="item in areaOptions" :key="item" :label="item" :value="item" />
                </el-select>
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

    <!-- 数据表格 -->
    <div class="el-card is-always-shadow">
      <div class="el-card__body">
        <el-table
          v-loading="loading"
          :data="tableData"
          border
          stripe
          height="600"
          style="width: 100%"
          :header-cell-style="{backgroundColor: '#f5f7fa'}"
        >
          <el-table-column prop="锁类分区" label="锁类分区" width="120" />
          <el-table-column prop="周数" label="周数" width="80" />
          <el-table-column prop="落货总数" label="落货总数/只" width="120" />
          <el-table-column prop="落货总数需时" label="落货总数需时/h" width="140" />
          <el-table-column prop="报工总数/只" label="报工总数/只" width="120" />
          <el-table-column prop="报工总工时/h" label="报工总工时/h" width="140" />
          <el-table-column prop="工人总工时/h" label="工人总工时/h" width="140" />
          <el-table-column prop="工时占比 * 工人总工时" label="工时占比 * 工人总工时" width="180" />
          <el-table-column prop="报工数/只" label="报工数/只" width="120" />
          <el-table-column prop="报工工时/h" label="报工工时/h" width="120" />
        </el-table>
        <div v-if="tableData.length === 0 && !loading" class="no-data">暂无数据</div>
      </div>
    </div>
  </Layout>
</template>

<script>
import Layout from '../../components/Layout.vue';
import axios from 'axios';
import { eventBus } from '../../eventBus';

export default {
  name: 'BeamWork',
  components: { Layout },
  data() {
    return {
      breadcrumbItems: [],
      sidebarMenus: [],
      tableData: [],
      loading: false,
      searchForm: { 锁类分区: '' },
      areaOptions: ['数控车床区', '弯锁梁区', '线外工序', '仪表车床区', '自动车床区']
    };
  },
  created() {
    eventBus.$on('sidebar-Menus-Updated', menus => {
      this.sidebarMenus = menus;
      this.generateBreadcrumb(this.$route.path);
    });
    if (this.sidebarMenus.length === 0) {
      this.breadcrumbItems = ['锁梁工时统计'];
    }
    this.searchData();
  },
  watch: {
    $route(newVal) {
      this.generateBreadcrumb(newVal.path);
    }
  },
  methods: {
    generateBreadcrumb(path) {
      try {
        const findMenuName = (menus, target) => {
          for (const menu of menus) {
            if (menu.path === target) return menu.name;
            if (menu.children) {
              for (const child of menu.children) {
                if (child.path === target) return [menu.name, child.name];
              }
            }
          }
          return path.split('/').pop();
        };
        const menuNames = findMenuName(this.sidebarMenus, path);
        this.breadcrumbItems = Array.isArray(menuNames) ? menuNames : [menuNames];
      } catch (e) {
        console.error('生成面包屑失败', e);
        this.breadcrumbItems = ['锁梁工时统计'];
      }
    },
    async searchData() {
      this.loading = true;
      try {
        const params = {};
        if (this.searchForm.锁类分区) params['锁类分区'] = this.searchForm.锁类分区;
        const res = await axios.get('/api/beamwork', { params });
        if (res.data.status === 'success') {
          this.tableData = res.data.data;
        } else {
          this.$message.error(res.data.message || '查询失败');
        }
      } catch (e) {
        console.error(e);
        this.$message.error('查询失败，请检查网络或后端');
      } finally {
        this.loading = false;
      }
    },
    resetForm() {
      this.searchForm.锁类分区 = '';
      this.searchData();
    }
  }
};
</script>

<style scoped>
.mb-4 {
  margin-bottom: 20px;
}
.card-title {
  font-size: 16px;
  font-weight: bold;
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
</style>
