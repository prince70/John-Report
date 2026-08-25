<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="report-container">
      <div class="el-card is-always-shadow mb-4">
        <div class="el-card__body">
          <el-form @submit.native.prevent="(() => { currentPage = 1; searchData() })()" label-width="100px">
            <el-row :gutter="20">
              <el-col :span="5">
                <el-form-item label="订单编号">
                  <el-input v-model="filters.订单编号" placeholder="如: 26-1629" clearable @keyup.enter.native="searchData" />
                </el-form-item>
              </el-col>
              <el-col :span="5">
                <el-form-item label="开始时间">
                  <el-date-picker v-model="filters.开始时间" type="month" placeholder="年-月" value-format="yyyy-MM" clearable style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="5">
                <el-form-item label="结束时间">
                  <el-date-picker v-model="filters.结束时间" type="month" placeholder="年-月" value-format="yyyy-MM" clearable style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="5">
                <el-form-item label="工单编号">
                  <el-input v-model="filters.工单编号" placeholder="请输入工单编号" clearable @keyup.enter.native="searchData" />
                </el-form-item>
              </el-col>
              <el-col :span="4">
                <el-form-item label="姓名">
                  <el-input v-model="filters.姓名" placeholder="请输入姓名" clearable @keyup.enter.native="searchData" />
                </el-form-item>
              </el-col>
            </el-row>
            <div class="form-actions">
              <el-button type="primary" :loading="loading" @click="currentPage = 1; searchData()">查询</el-button>
              <el-button @click="resetFilters">重置</el-button>
              <el-button type="success" icon="el-icon-download" :loading="exporting" @click="exportData">导出</el-button>
            </div>
          </el-form>
        </div>
      </div>

      <div v-if="hasSearched" class="el-card is-always-shadow mb-4 summary-card">
        <div class="el-card__body summary-row">
          <span>总条数: <b>{{ total }}</b></span>
        </div>
      </div>

      <div v-if="hasSearched" class="el-card is-always-shadow table-card" v-loading="loading" element-loading-text="加载中...">
        <div class="el-card__body">
          <el-table v-if="tableData.length" :data="tableData" border stripe max-height="620" style="width: 100%" :header-cell-style="{ background: '#eef1f6', color: '#606266' }">
            <el-table-column prop="序列号" label="序列号" width="70" align="center" />
            <el-table-column v-for="col in dynamicColumns" :key="col" :prop="col" :label="col" min-width="140" show-overflow-tooltip />
          </el-table>
          <el-empty v-else description="暂无数据" />
        </div>
      </div>

      <div v-if="hasSearched && tableData.length > 0" class="pagination-container">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          :page-size="pageSize"
          :current-page="currentPage"
          :page-sizes="[100, 200, 500]"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </Layout>
</template>

<script>
import Layout from '@/components/Layout.vue';
import axios from 'axios'

export default {
  name: 'WorkorderQuery',
  components: { Layout },
  data() {
    return {
      breadcrumbItems: ['报表系统', '车间报工详情', '基于派工单查订单和报工'],
      filters: { 订单编号: '', 开始时间: '', 结束时间: '', 工单编号: '', 姓名: '' },
      tableData: [],
      total: 0,
      currentPage: 1,
      pageSize: 200,
      loading: false,
      exporting: false,
      hasSearched: false,
      dynamicColumns: [],
    };
  },
  methods: {
    async searchData() {
      if (!this.filters.订单编号) {
        this.$message.warning('订单编号为必填项');
        return;
      }
      if (!/^\d{2}-\d{4}/.test(this.filters.订单编号)) {
        this.$message.warning('订单编号格式不正确，如: 26-1629-01');
        return;
      }
      this.loading = true;
      this.hasSearched = true;
      try {
        const params = {
          订单编号: this.filters.订单编号,
          开始时间: this.filters.开始时间 || undefined,
          结束时间: this.filters.结束时间 || undefined,
          工单编号: this.filters.工单编号 || undefined,
          姓名: this.filters.姓名 || undefined,
        };
        const res = await axios.get('/api/workorderSummary', { params });
        const data = res.data.data || [];
        this.total = data.length;
        this.tableData = data.slice((this.currentPage - 1) * this.pageSize, this.currentPage * this.pageSize);
        if (data.length > 0) {
          const skip = { '序号': true, '序列号': true };
          this.dynamicColumns = Object.keys(data[0]).filter(k => !skip[k] && !k.startsWith('_'));
        }
      } catch (err) {
        this.$message.error('查询失败: ' + (err.response?.data?.detail || err.message));
      } finally {
        this.loading = false;
      }
    },
    async exportData() {
      if (!this.filters.订单编号) {
        this.$message.warning('订单编号为必填项');
        return;
      }
      if (!/^\d{2}-\d{4}/.test(this.filters.订单编号)) {
        this.$message.warning('订单编号格式不正确，如: 26-1629-01');
        return;
      }
      this.exporting = true;
      try {
        const params = {
          订单编号: this.filters.订单编号,
          开始时间: this.filters.开始时间 || undefined,
          结束时间: this.filters.结束时间 || undefined,
          工单编号: this.filters.工单编号 || undefined,
          姓名: this.filters.姓名 || undefined,
        };
        const response = await axios.get('/api/workorderSummaryExport', {
          params,
          responseType: 'blob',
        });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `派工单汇总_${this.filters.订单编号}.xlsx`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      } catch (err) {
        this.$message.error('导出失败: ' + (err.response?.data?.detail || err.message));
      } finally {
        this.exporting = false;
      }
    },
    resetFilters() {
      this.filters = { 订单编号: '', 开始时间: '', 结束时间: '', 工单编号: '', 姓名: '' };
      this.tableData = [];
      this.total = 0;
      this.hasSearched = false;
      this.currentPage = 1;
    },
    handleSizeChange(val) {
      this.pageSize = val;
      this.searchData();
    },
    handleCurrentChange(val) {
      this.currentPage = val;
      this.searchData();
    },
  },
};
</script>

<style scoped>
.report-container {
  padding: 20px;
  background-color: #f0f2f5;
  min-height: calc(100vh - 60px);
}
.mb-4 {
  margin-bottom: 16px;
}
.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}
.summary-card .summary-row {
  display: flex;
  gap: 30px;
  font-size: 14px;
  color: #606266;
}
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
