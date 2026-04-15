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
        <el-table :data="tableData" v-loading="loading" border stripe height="600" style="width:100%" :header-cell-style="{backgroundColor:'#f5f7fa'}" :show-summary="true" :summary-method="getSummaries">
          <!-- similar columns as BeamWork vue -->
          <el-table-column prop="锁类分区" label="锁类分区" width="120" />
          <el-table-column prop="周数" label="周数" width="80" />
          <el-table-column prop="落货总数/只" label="落货总数/只" width="120" />
          <el-table-column prop="落货总数需时/h" label="落货总数需时/h" width="140" />
          <el-table-column prop="落货欠数/只" label="落货欠数/只" width="120" />
          <el-table-column prop="落货欠数需时/h" label="落货欠数需时/h" width="140" />
          <el-table-column prop="数控车床区/只" label="数控车床区/只" width="120" />
          <el-table-column prop="弯锁梁区/只" label="弯锁梁区/只" width="120" />
          <el-table-column prop="线外工序/只" label="线外工序/只" width="120" />
          <el-table-column prop="仪表车床区/只" label="仪表车床区/只" width="120" />
          <el-table-column prop="自动车床区/只" label="自动车床区/只" width="120" />
          <el-table-column prop="数控车床区/h" label="数控车床区/h" width="120" />
          <el-table-column prop="弯锁梁区/h" label="弯锁梁区/h" width="120" />
          <el-table-column prop="线外工序/h" label="线外工序/h" width="120" />
          <el-table-column prop="仪表车床区/h" label="仪表车床区/h" width="120" />
          <el-table-column prop="自动车床区/h" label="自动车床区/h" width="120" />
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
  name:'BeamNeed',
  components:{Layout},
  data()
  {
    return{
      breadcrumbItems:[],
      sidebarMenus:[],
      tableData:[],
      loading:false,
      searchForm:{锁类分区:''},
      areaOptions:['数控车床区','弯锁梁区','线外工序','仪表车床区','自动车床区']
      };
    },
    created()
    {
      eventBus.$on('sidebar-Menus-Updated',m=>{this.sidebarMenus=m;this.genBread(this.$route.path)});
      if(this.sidebarMenus.length===0)
        {
          this.breadcrumbItems=['锁梁计划欠数']}
          this.searchData();
        },
      watch:{
        $route(n){this.genBread(n.path)}
      },
      methods:{
      genBread(p)
        {
          try
          {
            const find=(m,t)=>{
              for(const menu of m)
              {
                if(menu.path===t) return menu.name;
                if(menu.children){
                  for(const c of menu.children)
                  {
                    if(c.path===t) return [menu.name,c.name]
                  }
                }
              }
              return p.split('/').pop()};
              const names=find(this.sidebarMenus,p);
              this.breadcrumbItems=Array.isArray(names)?names:[names];}
              catch(e)
              {
                this.breadcrumbItems=['锁梁计划欠数']}},
                async searchData(){
                  this.loading=true;
                try
                {
                  const params={};
                  if(this.searchForm.锁类分区)
                    params['锁类分区']=this.searchForm.锁类分区;
                const r=await axios.get('/api/beamneed',{params});
                if(r.data.status==='success')
                  {this.tableData=r.data.data}
                else{
                  this.$message.error(r.data.message||'查询失败')
                }
              }catch(e)
              {
                console.error(e);this.$message.error('查询失败')
              }
              finally{
                this.loading=false}
        },
      resetForm()
      {
        this.searchForm.锁类分区='';this.searchData();
      },
      getSummaries({ columns, data }) {
        const sums = [];
        columns.forEach((column, index) => {
          if (index === 0) {
            sums[index] = '总计';
            return;
          }
          const prop = column.property;
          if (prop === '落货总数需时/h') {
            const total = data.reduce((acc, item) => {
              const val = Number(item[prop]) || 0;
              return acc + val;
            }, 0);
            sums[index] = total.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
          } else {
            sums[index] = '';
          }
        });
        return sums;
      },
  }
}
</script>

<style scoped>
.mb-4{margin-bottom:20px}.card-title{font-size:16px;font-weight:bold}.form-actions{display:flex;justify-content:flex-end;margin-top:20px}.no-data{text-align:center;padding:30px 0;color:#909399;font-size:14px}
</style>
