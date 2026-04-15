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
          <!-- 本周差值 -->
          <el-row v-if="thisWeekDiff !== null" :gutter="20" style="margin-left:20px">
            <el-col :span="8">
              <el-form-item :label="diffLabel" label-width="250px">
                <el-input
                  class="no-bg diff-input"
                  :class="{ negative: thisWeekDiff < 0 }"
                  :value="formattedThisWeekDiff"
                  disabled
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

    <div class="el-card is-always-shadow">
      <div class="el-card__body">
        <el-table :data="tableData" v-loading="loading" border stripe height="480" style="width:100%" :header-cell-style="{backgroundColor:'#f5f7fa'}">
          <el-table-column prop="锁类分区" label="锁类分区" width="120" />
          <el-table-column prop="周数" label="周数" width="80" />
          <el-table-column prop="落货总数/只" label="落货总数/只" width="120" />
          <el-table-column prop="落货总数需时/h" label="落货总数需时/h" width="140" />
          <el-table-column prop="落货欠数/只" label="落货欠数/只" width="120" />
          <el-table-column prop="落货欠数需时/只" label="落货欠数需时/只" width="140" />
          <el-table-column prop="锁配件车间/只" label="锁配件车间/只" width="140" />
          <el-table-column prop="锁配件车间/h" label="锁配件车间/h" width="180" />
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
  name:'AccessoryWork',
  components:{Layout},
  data(){return{
    breadcrumbItems:[],sidebarMenus:[],tableData:[],loading:false,
    thisWeekDiff:null,thisWeekNumber:null,
    searchForm:{锁类分区:'锁配件车间'},
    areaOptions:['锁配件车间']
  }},
  created(){
    eventBus.$on('sidebar-Menus-Updated',m=>{this.sidebarMenus=m;this.genBread(this.$route.path)});
    if(this.sidebarMenus.length===0){this.breadcrumbItems=['锁配件报工工时统计']}
    this.searchData();
  },
  watch:{$route(n){this.genBread(n.path)}},
  computed:{
    diffLabel(){if(this.thisWeekDiff===null||this.thisWeekNumber===null)return '';return `${this.thisWeekNumber}周落货总数需时-锁配件车间工时差`;},
    formattedThisWeekDiff(){if(this.thisWeekDiff===null)return '';return this.thisWeekDiff.toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});}
  },
  methods:{
    genBread(p){try{
      const find=(menus,t)=>{for(const m of menus){if(m.path===t)return m.name;if(m.children){for(const c of m.children){if(c.path===t)return [m.name,c.name]}}}return p.split('/').pop()};
      const names=find(this.sidebarMenus,p);this.breadcrumbItems=Array.isArray(names)?names:[names];
    }catch(e){this.breadcrumbItems=['锁配件报工工时统计']}},
    async searchData(){this.loading=true;try{const params={};if(this.searchForm.锁类分区)params['锁类分区']=this.searchForm.锁类分区;const r=await axios.get('/api/accessorywork',{params});if(r.data.status==='success'){this.tableData=r.data.data;this.computeThisWeekDiff();}else{this.$message.error(r.data.message||'查询失败')}}catch(e){console.error(e);this.$message.error('查询失败')}finally{this.loading=false}},
    computeThisWeekDiff(){
      if(!Array.isArray(this.tableData)||this.tableData.length<1){
        this.thisWeekDiff=null;
        this.thisWeekNumber=null;
        return;
      }
      
      // 获取所有周数并排序
      const weeks=Array.from(new Set(this.tableData.map(r=>r['周数']).filter(w=>typeof w==='number'))).sort((a,b)=>a-b);
      if(weeks.length<1){
        this.thisWeekDiff=null;
        this.thisWeekNumber=null;
          return;
        }
      
      // 取第一周（最早的一周）计算差值
      const targetWeek=weeks[0];
      this.thisWeekNumber=targetWeek;
      const row=this.tableData.find(r=>r['周数']===targetWeek);
      
      if(!row){
        this.thisWeekDiff=null;
        return;
      }
      
      // 计算差值：落货总数需时 - 锁配件车间工时
      const 落货总数需时 = Number(row['落货总数需时/h']) || 0;
      const 锁配件车间工时 = Number(row['锁配件车间/h']) || 0;
      const diff = 落货总数需时 - 锁配件车间工时;
      this.thisWeekDiff = Number(diff.toFixed(2));
      
      console.log('差值计算:', {
        周数: targetWeek,
        落货总数需时,
        锁配件车间工时,
        差值: diff,
        格式化差值: this.thisWeekDiff
      });
    },
    resetForm(){this.searchForm.锁类分区='锁配件车间';this.searchData();}
  }
}
</script>

<style scoped>
.mb-4{margin-bottom:20px}.card-title{font-size:16px;font-weight:bold}.form-actions{display:flex;justify-content:flex-end;margin-top:20px}.no-data{text-align:center;padding:30px 0;color:#909399;font-size:14px}.lastweek-item{font-size:14px;margin-left:40px;padding-left:5px;}

/* 统一样式 */
.no-bg /deep/ .el-input__inner{background-color:#ffffff !important;}
.diff-input /deep/ .el-input__inner{color:#303133;}
.diff-input.negative /deep/ .el-input__inner{color:red !important;}
</style>
