<template>
  <Layout :breadcrumbItems="breadcrumbItems">
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

    <div class="el-card is-always-shadow">
      <div class="el-card__body">
        <el-table :data="tableData" v-loading="loading" border stripe height="450" style="width:100%" :header-cell-style="{backgroundColor:'#f5f7fa'}">
          <el-table-column prop="锁类分区" label="锁类分区" width="120" />
          <el-table-column prop="周数" label="周数" width="80" />
          <el-table-column prop="落货总数" label="落货总数/只" width="120" />
          <el-table-column prop="落货总数需时" label="落货总数需时/h" width="140" />
          <el-table-column prop="报工总数/只" label="报工总数/只" width="120" />
          <el-table-column prop="报工总工时/h" label="报工总工时/h" width="140" />
          <el-table-column prop="工人总工时/h" label="工人总工时/h" width="140" />
          <el-table-column prop="锁配件车间/只" label="锁配件车间/只" width="140" />
          <el-table-column prop="锁配件车间/h" label="锁配件车间/h" width="140" />
        </el-table>
        <div v-if="tableData.length===0&&!loading" class="no-data">暂无数据</div>
      </div>
    </div>
  </Layout>
</template>

<script>
import Layout from '../../components/Layout.vue';
import axios from 'axios';
import { eventBus } from '../../eventBus';
export default {
  name:'AccessoryNeed',
  components:{Layout},
  data(){return{
    breadcrumbItems:[],sidebarMenus:[],tableData:[],loading:false,
    searchForm:{锁类分区:'锁配件车间'},
    areaOptions:['锁配件车间']
  }},
  created(){
    eventBus.$on('sidebar-Menus-Updated',m=>{this.sidebarMenus=m;this.genBread(this.$route.path)});
    if(this.sidebarMenus.length===0){this.breadcrumbItems=['锁配件工时统计']}
    this.searchData();
  },
  watch:{$route(n){this.genBread(n.path)}},
  methods:{
    genBread(p){try{
      const find=(menus,t)=>{for(const m of menus){if(m.path===t)return m.name;if(m.children){for(const c of m.children){if(c.path===t)return [m.name,c.name]}}}return p.split('/').pop()};
      const names=find(this.sidebarMenus,p);this.breadcrumbItems=Array.isArray(names)?names:[names];
    }catch(e){this.breadcrumbItems=['锁配件工时统计']}}
    ,async searchData(){this.loading=true;try{const params={};if(this.searchForm.锁类分区)params['锁类分区']=this.searchForm.锁类分区;const r=await axios.get('/api/accessoryneed',{params});if(r.data.status==='success'){this.tableData=r.data.data}else{this.$message.error(r.data.message||'查询失败')}}catch(e){console.error(e);this.$message.error('查询失败')}finally{this.loading=false}},
    resetForm(){
      this.searchForm.锁类分区='锁配件车间';this.searchData();
    }
  }
}
</script>

<style scoped>
.mb-4{margin-bottom:20px}.card-title{font-size:16px;font-weight:bold}.form-actions{display:flex;justify-content:flex-end;margin-top:20px}.no-data{text-align:center;padding:30px 0;color:#909399;font-size:14px}
</style>
