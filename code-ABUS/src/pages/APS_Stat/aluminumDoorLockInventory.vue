<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <div class="report-container">
      <div class="el-card is-always-shadow mb-4">
        <div class="el-card__body">
          <el-form :model="searchForm" inline label-width="90px">
            <el-row :gutter="16">
              <el-col :span="6">
                <el-form-item label="料品名称">
                  <el-select v-model="searchForm.料品名称" placeholder="请选择料品名称" clearable style="width:100%" @change="onNameChange">
                    <el-option v-for="item in nameOptions" :key="item" :label="item" :value="item" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="料品规格">
                  <el-select v-model="searchForm.料品规格" placeholder="请选择料品规格" clearable filterable style="width:100%" @change="onSpecChange">
                    <el-option v-for="item in specOptions" :key="item" :label="item" :value="item" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="存放位置">
                  <el-select v-model="searchForm.存放位置" placeholder="请选择存放位置" clearable style="width:100%" @change="onLocationChange">
                    <el-option v-for="item in locationOptions" :key="item" :label="item" :value="item" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="4">
                <div class="form-actions">
                  <el-button type="primary" @click="searchData">查询</el-button>
                  <el-button @click="resetSearch">重置</el-button>
                </div>
              </el-col>
            </el-row>
          </el-form>
        </div>
      </div>

      <div class="el-card is-always-shadow mb-4">
        <div class="el-card__body" style="display:flex;align-items:center;justify-content:space-between;">
          <div style="display:flex;align-items:center;gap:12px;">
            <el-button type="primary" icon="el-icon-data-analysis" @click="showStats = true">查看统计</el-button>
            <span style="color:#909399;font-size:13px;">按【料品规格】汇总库存、减单数量、原始库存的累计和</span>
          </div>
          <div style="font-size:13px;color:#606266;">数据总条数：<b>{{ rawData.length }}</b> 条</div>
        </div>
      </div>

      <el-table
        v-if="hasSearched"
        :data="tableData"
        border
        stripe
        max-height="620"
        style="width: 100%"
        :header-cell-style="{ background: '#eef1f6', color: '#606266' }"
      >
        <el-table-column prop="序号" label="序号" width="70" align="center" fixed="left" />
        <el-table-column prop="料品编码" label="料品编码" min-width="130" show-overflow-tooltip />
        <el-table-column prop="料品名称" label="料品名称" min-width="110" show-overflow-tooltip />
        <el-table-column prop="料品规格" label="料品规格" min-width="200" show-overflow-tooltip />
        <el-table-column prop="存放位置" label="存放位置" min-width="130" show-overflow-tooltip />
        <el-table-column prop="库存" label="库存" min-width="90" align="right" />
        <el-table-column prop="减单数量" label="减单数量" min-width="100" align="right" />
        <el-table-column prop="原始库存" label="原始库存" min-width="100" align="right" />
        <el-table-column prop="单位" label="单位" width="70" align="center" />
      </el-table>

      <el-empty v-if="hasSearched && !tableData.length" description="暂无数据" />

      <el-pagination
        v-if="hasSearched && allData.length > 0"
        background
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        :page-size="pageSize"
        :current-page="currentPage"
        :page-sizes="[100, 200, 500]"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />

      <el-dialog title="按料品规格统计" :visible.sync="showStats" width="800px" top="6vh">
        <el-table :data="statsData" border stripe style="width:100%" :header-cell-style="{ background:'#eef1f6', color:'#606266' }" max-height="500" show-summary :summary-method="statsSummary">
          <el-table-column type="index" label="序号" width="60" align="center" />
          <el-table-column prop="料品规格" label="料品规格" min-width="260" show-overflow-tooltip />
          <el-table-column prop="库存" label="库存累计" min-width="100" align="right">
            <template slot-scope="{ row }">{{ formatNum(row.库存) }}</template>
          </el-table-column>
          <el-table-column prop="减单数量" label="减单数量累计" min-width="110" align="right">
            <template slot-scope="{ row }">{{ formatNum(row.减单数量) }}</template>
          </el-table-column>
          <el-table-column prop="原始库存" label="原始库存累计" min-width="110" align="right">
            <template slot-scope="{ row }">{{ formatNum(row.原始库存) }}</template>
          </el-table-column>
        </el-table>
        <div style="margin-top:12px;text-align:right;color:#909399;font-size:13px;">
          共 {{ statsData.length }} 种规格，基于当前筛选条件统计
        </div>
      </el-dialog>
    </div>
  </Layout>
</template>

<script>
import Layout from '@/components/Layout.vue';
import axios from 'axios';

export default {
  name: 'AluminumDoorLockInventory',
  components: { Layout },
  mounted() {
    this.loadData();
  },
  data() {
    return {
      breadcrumbItems: ['报表系统', '报工', '铝门锁锁体即时库存'],
      searchForm: { 料品名称: '', 料品规格: '', 存放位置: '' },
      tableData: [],
      allData: [],
      rawData: [],
      total: 0,
      currentPage: 1,
      pageSize: 200,
      loading: false,
      hasSearched: false,
      showStats: false,
    };
  },
  computed: {
    nameOptions() {
      const { 料品规格: spec, 存放位置: loc } = this.searchForm;
      const set = new Set();
      this.rawData.forEach(r => {
        if (spec && r['料品规格'] !== spec) return;
        if (loc && r['存放位置'] !== loc) return;
        if (r['料品名称']) set.add(r['料品名称']);
      });
      return [...set].sort();
    },
    specOptions() {
      const { 料品名称: name, 存放位置: loc } = this.searchForm;
      const set = new Set();
      this.rawData.forEach(r => {
        if (name && r['料品名称'] !== name) return;
        if (loc && r['存放位置'] !== loc) return;
        if (r['料品规格']) set.add(r['料品规格']);
      });
      return [...set].sort();
    },
    locationOptions() {
      const { 料品名称: name, 料品规格: spec } = this.searchForm;
      const set = new Set();
      this.rawData.forEach(r => {
        if (name && r['料品名称'] !== name) return;
        if (spec && r['料品规格'] !== spec) return;
        if (r['存放位置']) set.add(r['存放位置']);
      });
      return [...set].sort();
    },
    statsData() {
      const map = {};
      this.allData.forEach(r => {
        const key = r['料品规格'] || '未知';
        if (!map[key]) map[key] = { 料品规格: key, 库存: 0, 减单数量: 0, 原始库存: 0 };
        map[key].库存 += parseFloat(r['库存']) || 0;
        map[key].减单数量 += parseFloat(r['减单数量']) || 0;
        map[key].原始库存 += parseFloat(r['原始库存']) || 0;
      });
      return Object.values(map).sort((a, b) => a['料品规格'].localeCompare(b['料品规格']));
    },
  },
  watch: {
    'searchForm.料品名称'() { this.clearInvalidSelection(); },
    'searchForm.料品规格'() { this.clearInvalidSelection(); },
    'searchForm.存放位置'() { this.clearInvalidSelection(); },
  },
  methods: {
    formatNum(val) {
      const n = parseFloat(val) || 0;
      return n % 1 === 0 ? n.toLocaleString() : n.toLocaleString(undefined, { minimumFractionDigits: 3, maximumFractionDigits: 3 });
    },
    statsSummary({ columns, data }) {
      const sums = [];
      columns.forEach((col, i) => {
        if (i === 0) { sums[i] = ''; return; }
        if (i === 1) { sums[i] = '总计'; return; }
        const prop = col.property;
        const total = data.reduce((s, r) => s + (parseFloat(r[prop]) || 0), 0);
        sums[i] = this.formatNum(total);
      });
      return sums;
    },
    clearInvalidSelection() {
      const name = this.searchForm.料品名称;
      const spec = this.searchForm.料品规格;
      const loc = this.searchForm.存放位置;
      if (name && !this.nameOptions.includes(name)) this.searchForm.料品名称 = '';
      if (spec && !this.specOptions.includes(spec)) this.searchForm.料品规格 = '';
      if (loc && !this.locationOptions.includes(loc)) this.searchForm.存放位置 = '';
    },
    onNameChange() { this.$nextTick(() => { this.clearInvalidSelection(); this.searchData(); }); },
    onSpecChange() { this.$nextTick(() => { this.clearInvalidSelection(); this.searchData(); }); },
    onLocationChange() { this.$nextTick(() => { this.clearInvalidSelection(); this.searchData(); }); },
    handleSizeChange(val) { this.pageSize = val; this.currentPage = 1; this.sliceData(); },
    handleCurrentChange(val) { this.currentPage = val; this.sliceData(); },
    sliceData() {
      const start = (this.currentPage - 1) * this.pageSize;
      this.tableData = this.allData.slice(start, start + this.pageSize);
    },
    async loadData() {
      this.loading = true;
      try {
        const res = await axios.get('/api/file/pandian');
        if (res.data.status === 'success') {
          this.rawData = res.data.data || [];
          this.hasSearched = true;
          this.applyFilter();
        } else {
          this.$message.error('加载数据失败: ' + (res.data.message || '未知错误'));
        }
      } catch (e) {
        console.error(e);
        this.$message.error('加载数据失败，请检查网络');
      } finally {
        this.loading = false;
      }
    },
    applyFilter() {
      const { 料品名称: name, 料品规格: spec, 存放位置: loc } = this.searchForm;
      let filtered = this.rawData;
      if (name) filtered = filtered.filter(r => r['料品名称'] === name);
      if (spec) filtered = filtered.filter(r => r['料品规格'] === spec);
      if (loc) filtered = filtered.filter(r => r['存放位置'] === loc);
      this.allData = filtered;
      this.total = this.allData.length;
      this.currentPage = 1;
      this.sliceData();
      this.hasSearched = true;
    },
    searchData() { this.applyFilter(); },
    resetSearch() {
      this.searchForm = { 料品名称: '', 料品规格: '', 存放位置: '' };
      this.applyFilter();
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
.form-actions {
  display: flex;
  align-items: center;
  height: 100%;
  padding-top: 0;
}
</style>
