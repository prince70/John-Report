<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <el-card class="search-card">
      <el-form :model="queryParams" inline>
        <el-form-item label="姓名">
          <el-input v-model="queryParams.姓名" placeholder="输入姓名" clearable style="width: 140px"
            @keyup.enter.native="handleSearch" />
        </el-form-item>
        <el-form-item label="工号">
          <el-input v-model="queryParams.工号" placeholder="输入工号" clearable style="width: 120px"
            @keyup.enter.native="handleSearch" />
        </el-form-item>
        <el-form-item label="工卡号">
          <el-input v-model="queryParams.工卡号" placeholder="输入工卡号" clearable style="width: 120px"
            @keyup.enter.native="handleSearch" />
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="queryParams.性别" placeholder="全部" clearable style="width: 90px">
            <el-option v-for="g in genders" :key="g" :label="g" :value="g" />
          </el-select>
        </el-form-item>
        <el-form-item label="年龄">
          <el-select v-model="queryParams.年龄" placeholder="全部" clearable style="width: 110px">
            <el-option v-for="r in ageRanges" :key="r" :label="r" :value="r" />
          </el-select>
        </el-form-item>
        <el-form-item label="学历">
          <el-select v-model="queryParams.学历" placeholder="全部" clearable style="width: 100px">
            <el-option v-for="s in studys" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="queryParams.部门" placeholder="全部" clearable filterable style="width: 150px">
            <el-option v-for="d in departments" :key="d" :label="d" :value="d" />
          </el-select>
        </el-form-item>
        <el-form-item label="车间">
          <el-select v-model="queryParams.车间" placeholder="全部" clearable filterable style="width: 130px">
            <el-option v-for="w in workshops" :key="w" :label="w" :value="w" />
          </el-select>
        </el-form-item>
        <el-form-item label="分区">
          <el-select v-model="queryParams.分区" placeholder="全部" clearable filterable style="width: 120px">
            <el-option v-for="z in zones" :key="z" :label="z" :value="z" />
          </el-select>
        </el-form-item>
        <el-form-item label="前线员工">
          <el-select v-model="queryParams.是否前线员工" placeholder="全部" clearable style="width: 90px">
            <el-option label="是" value="是" />
            <el-option label="否" value="否" />
          </el-select>
        </el-form-item>
        <el-form-item label="已婚">
          <el-select v-model="queryParams.是否已婚" placeholder="全部" clearable style="width: 90px">
            <el-option label="是" value="是" />
            <el-option label="否" value="否" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button type="success" :loading="exportLoading" @click="exportExcel">导出Excel</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <div class="table-header">
        <div class="header-left">
          <span class="title">员工信息表</span>
        </div>
        <div class="header-right">
          <span class="stat-item">总人数：<strong>{{ filteredData.length }}</strong></span>
          <span class="stat-item">当前页：<strong>{{ currentPage }}</strong> / {{ totalPages }}</span>
        </div>
      </div>

      <el-table :data="paginatedData" v-loading="loading" border stripe style="width: 100%" max-height="600"
        :header-cell-style="{ background: '#409EFF', color: '#fff', fontWeight: 'bold' }">
        <el-table-column type="index" label="#" width="50" align="center" :index="indexMethod" fixed />
        <el-table-column prop="工号" label="工号" width="80" align="center" fixed />
        <el-table-column prop="姓名" label="姓名" width="80" align="center" fixed />
        <el-table-column prop="性别" label="性别" width="55" align="center" />
        <el-table-column prop="年龄" label="年龄" width="55" align="center" />
        <el-table-column prop="是否已婚" label="已婚" width="55" align="center" />
        <el-table-column prop="入职时间" label="入职时间" width="110" align="center" />
        <el-table-column prop="部门" label="部门" width="130" align="center" />
        <el-table-column prop="职务" label="职务" width="100" align="center" />
        <el-table-column prop="是否前线员工" label="前线" width="55" align="center" />
        <el-table-column prop="是否退休返聘" label="退休返聘" width="75" align="center" />
        <el-table-column prop="车间" label="车间" width="100" align="center" />
        <el-table-column prop="分区" label="分区" width="80" align="center" />
        <el-table-column prop="工位" label="工位" width="80" align="center" />
        <el-table-column prop="线别" label="线别" width="80" align="center" />
        <el-table-column prop="所属技工" label="所属技工" width="80" align="center" />
        <el-table-column prop="所属上级" label="所属上级" width="80" align="center" />
        <el-table-column prop="学历" label="学历" width="70" align="center" />
        <el-table-column prop="毕业学校" label="毕业学校" width="140" align="center" show-overflow-tooltip />
        <el-table-column prop="专业" label="专业" width="120" align="center" show-overflow-tooltip />
        <el-table-column prop="工卡号" label="工卡号" width="80" align="center" />
        <el-table-column prop="联系方式" label="联系方式" width="120" align="center" />
        <el-table-column prop="身份证" label="身份证" width="175" align="center" />
        <el-table-column prop="居住地址" label="居住地址" min-width="200" align="center" show-overflow-tooltip />
        <el-table-column prop="电子邮箱" label="电子邮箱" width="160" align="center" show-overflow-tooltip />
        <el-table-column prop="亲属关系" label="亲属关系" width="100" align="center" show-overflow-tooltip />
        <el-table-column prop="宿舍房号" label="宿舍房号" width="80" align="center" />
      </el-table>

      <div class="pagination-container">
        <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange"
          :current-page="currentPage" :page-size="pageSize" :page-sizes="[100, 200, 500, 1000, 2000]"
          layout="total, sizes, prev, pager, next, jumper" :total="filteredData.length" background />
      </div>
    </el-card>
  </Layout>
</template>

<script>
// 控制台测试工卡号：打开本页后按 F12，在 Console 里粘贴运行下面整段：
// fetch('/api/people').then(r=>r.json()).then(d=>{ console.log('请求状态:', d.status); console.log('总条数:', d.data?.length); const hasCard = (d.data||[]).filter(x=>x.工卡号 && x.工卡号!=='未登记'); console.log('含有效工卡号条数:', hasCard.length); console.log('工卡号样例(前5条):', hasCard.slice(0,5).map(x=>({姓名:x.姓名, 工卡号:x.工卡号}))); }).catch(e=>console.error('请求失败', e));
import axios from 'axios'
import Layout from '@/components/Layout.vue'
import { eventBus } from '../../eventBus'
import * as XLSX from 'xlsx'

export default {
  components: { Layout },
  data() {
    return {
      breadcrumbItems: ['HR人力资源资讯', '员工信息表'],
      originalData: [],
      filteredData: [],
      loading: false,
      exportLoading: false,
      currentPage: 1,
      pageSize: 1000,
      sidebarMenus: [],
      genders: ['男', '女'],
      ageRanges: ['20-30', '30-40', '40-50', '50-60', '60以上', '未登记'],
      studys: ['小学', '初中', '中专', '高中', '大专', '本科', '研究生', '中技', '硕士'],
      departments: [],
      workshops: [],
      zones: [],
      queryParams: {
        姓名: '', 工号: '', 工卡号: '', 性别: '', 年龄: '', 学历: '',
        部门: '', 分区: '', 车间: '', 是否前线员工: '', 是否已婚: ''
      }
    }
  },
  computed: {
    paginatedData() {
      const start = (this.currentPage - 1) * this.pageSize
      return this.filteredData.slice(start, start + this.pageSize)
    },
    totalPages() {
      return Math.ceil(this.filteredData.length / this.pageSize) || 1
    }
  },
  async mounted() {
    await Promise.all([
      this.fetchData(),
      this.fetchDepartments(),
      this.fetchWorkshops(),
      this.fetchZones()
    ])
    this.fetchDebug()
  },
  created() {
    eventBus.$on('sidebar-Menus-Updated', (menus) => {
      this.sidebarMenus = menus
      this.generateBreadcrumb(this.$route.path)
    })
  },
  watch: {
    $route(newVal) {
      this.generateBreadcrumb(newVal.path)
    }
  },
  methods: {
    generateBreadcrumb(path) {
      try {
        const findMenuName = (menus, targetPath) => {
          for (const menu of menus) {
            if (menu.path === targetPath) return menu.name
            if (menu.children) {
              for (const child of menu.children) {
                if (child.path === targetPath) return [menu.name, child.name]
              }
            }
          }
          return targetPath.split('/').pop()
        }
        const paths = path.split('/').filter(p => p)
        const menuNames = findMenuName(this.sidebarMenus, '/' + paths.join('/'))
        this.breadcrumbItems = Array.isArray(menuNames) ? menuNames : [menuNames]
      } catch {
        this.breadcrumbItems = ['HR人力资源资讯', '员工信息表']
      }
    },

    async fetchData() {
      this.loading = true
      try {
        const res = await axios.get('/api/people')
        if (res.data?.status === 'success') {
          this.originalData = res.data.data || []
          this.filteredData = [...this.originalData]
        } else {
          console.warn('接口返回异常:', res.data)
          this.$message.warning(res.data?.detail || res.data?.message || '接口返回格式异常')
        }
      } catch (error) {
        console.error('数据获取失败:', error)
        const msg = error.response?.data?.detail || error.response?.data?.message || error.message || '请检查网络与后端服务'
        this.$message.error('数据加载失败: ' + msg)
      } finally {
        this.loading = false
      }
    },

    async fetchDepartments() {
      try {
        const res = await axios.get('/api/people/departments')
        if (res.data?.status === 'success') this.departments = res.data.data || []
      } catch (e) { console.error('部门列表获取失败:', e) }
    },

    async fetchWorkshops() {
      try {
        const res = await axios.get('/api/people/workshops')
        if (res.data?.status === 'success') this.workshops = res.data.data || []
      } catch (e) { console.error('车间列表获取失败:', e) }
    },

    async fetchZones() {
      try {
        const res = await axios.get('/api/people/zones')
        if (res.data?.status === 'success') this.zones = res.data.data || []
      } catch (e) { console.error('分区列表获取失败:', e) }
    },

    async fetchDebug() {
      try {
        const res = await axios.get('/api/people/debug')
        console.log('[HR/people 调试]', res.data)
        if (res.data?.status === 'error') {
          console.error('[HR/people] 数据库异常:', res.data.detail)
        }
      } catch (e) {
        console.error('[HR/people] 调试接口请求失败:', e?.response?.data || e.message)
      }
    },

    async exportExcel() {
      if (!this.filteredData.length) {
        this.$message.warning('当前没有可导出的数据')
        return
      }

      this.exportLoading = true
      try {
        const rows = this.filteredData.map(item => ({ ...item }))
        const worksheet = XLSX.utils.json_to_sheet(rows)
        const workbook = XLSX.utils.book_new()
        XLSX.utils.book_append_sheet(workbook, worksheet, '员工信息')

        const now = new Date()
        const pad = (n) => String(n).padStart(2, '0')
        const filename = `员工信息_${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}.xlsx`
        XLSX.writeFile(workbook, filename)
        this.$message.success(`Excel导出成功（${rows.length}条）`)
      } catch (error) {
        console.error('导出Excel失败:', error)
        this.$message.error('导出Excel失败，请稍后重试')
      } finally {
        this.exportLoading = false
      }
    },

    handleSearch() {
      const q = this.queryParams
      this.filteredData = this.originalData.filter(item => {
        if (q.姓名 && !(item.姓名 || '').includes(q.姓名)) return false
        if (q.工号 && !(item.工号 || '').includes(q.工号)) return false
        if (q.工卡号 && !(item.工卡号 || '').includes(q.工卡号)) return false
        if (q.性别 && item.性别 !== q.性别) return false
        if (q.学历 && item.学历 !== q.学历) return false
        if (q.部门 && item.部门 !== q.部门) return false
        if (q.车间 && item.车间 !== q.车间) return false
        if (q.分区 && !(item.分区 || '').includes(q.分区)) return false
        if (q.是否前线员工 && item.是否前线员工 !== q.是否前线员工) return false
        if (q.是否已婚 && item.是否已婚 !== q.是否已婚) return false
        if (q.年龄) {
          const age = parseInt(item.年龄)
          if (q.年龄 === '未登记') { if (!isNaN(age)) return false }
          else {
            let lo = 0
            let hi = Number.MAX_SAFE_INTEGER
            if (q.年龄.endsWith('以上')) {
              lo = Number(q.年龄.replace('以上', ''))
            } else {
              [lo, hi] = q.年龄.split('-').map(Number)
            }
            if (isNaN(age) || age < lo || age > hi) return false
          }
        }
        return true
      })
      this.currentPage = 1
    },

    resetForm() {
      this.queryParams = {
        姓名: '', 工号: '', 工卡号: '', 性别: '', 年龄: '', 学历: '',
        部门: '', 分区: '', 车间: '', 是否前线员工: '', 是否已婚: ''
      }
      this.filteredData = [...this.originalData]
      this.currentPage = 1
    },

    handleCurrentChange(val) { this.currentPage = val },
    handleSizeChange(val) { this.pageSize = val; this.currentPage = 1 },
    indexMethod(index) { return (this.currentPage - 1) * this.pageSize + index + 1 }
  }
}
</script>

<style scoped>
.search-card {
  margin-bottom: 10px;
}

.table-card {
  margin-top: 10px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 4px;
}

.header-left .title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.header-right {
  display: flex;
  gap: 20px;
}

.stat-item {
  font-size: 14px;
  color: #606266;
}

.stat-item strong {
  color: #409EFF;
  font-size: 16px;
  margin: 0 4px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
