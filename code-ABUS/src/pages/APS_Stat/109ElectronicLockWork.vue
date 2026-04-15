<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <!-- 搜索表单 -->
    <div class="search-form">
      <el-form :model="queryParams" label-width="100px">
        <el-row :gutter="10">
          <el-col :span="8">
            <el-form-item label="锁类分区">
              <el-select v-model="queryParams.lockArea" placeholder="请选择类型" clearable>
                <el-option
                  v-for="item in lockAreas"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"/>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="开始周">
              <el-input-number v-model="queryParams.startWeek" :min="1" :max="53"/>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="结束周">
              <el-input-number v-model="queryParams.endWeek" :min="1" :max="53"/>
            </el-form-item>
          </el-col>
        </el-row>
        <div class="form-actions">
          <div class="center-actions">
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetForm">重置</el-button>
          </div>
        </div>
      </el-form>
    </div>

    <!-- 数据表格 -->
    <div v-if="dynamicData.length > 0" class="data-preview">
      <el-table :data="dynamicData" border stripe v-loading="loading" style="width:100%; margin-top:5px" max-height="500">
        <el-table-column v-for="(col,index) in dynamicColumns" :key="index" :prop="col.prop" :label="col.label" :width="col.width" align="center">
          <template slot-scope="{row}">
            <span v-if="typeof row[col.prop] === 'number'">{{ row[col.prop].toLocaleString() }}</span>
            <span v-else>{{ row[col.prop] }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <div v-else-if="loading" class="loading-message"><p>数据加载中，请稍候...</p></div>
    <div v-else><p style="padding-top:200px;padding-left:700px;font-size:35px;color:#001E38;">暂无数据</p></div>
  </Layout>
</template>

<script>
import axios from 'axios'
import Layout from '@/components/Layout.vue'
import { eventBus } from '../../eventBus'

export default {
  components: { Layout },
  data() {
    return {
      breadcrumbItems: [],
      sidebarMenus: [],
      queryParams: {
        lockArea: '',
        startWeek: 16,
        endWeek: 23
      },
      lockAreas:[
        { value: '电子软锁车间', label: '电子软锁车间' },
        { value: '电子锁软锁区', label: '电子锁软锁区' }
      ],
      dynamicData: [],
      dynamicColumns: [],
      loading:false
    }
  },
  async mounted(){
    await this.fetchData();
  },
  created(){
    // 监听侧边栏菜单更新以生成面包屑
    eventBus.$on('sidebar-Menus-Updated', menus => {
      this.sidebarMenus = menus;
      this.generateBreadcrumb(this.$route.path);
    });
    // 如果侧边栏菜单尚未加载，给一个默认面包屑
    if (this.sidebarMenus.length === 0) {
      this.breadcrumbItems = ['电子锁工时统计'];
    }
  },
  watch:{
    $route(newVal){
      this.generateBreadcrumb(newVal.path);
    }
  },
  methods:{
    async fetchData(){
      this.loading=true;
      try{
        const params={};
        if(this.queryParams.lockArea) params.lockArea=this.queryParams.lockArea;
        if(this.queryParams.startWeek) params.startWeek=this.queryParams.startWeek;
        if(this.queryParams.endWeek) params.endWeek=this.queryParams.endWeek;
        const resp=await axios.get('/api/electronicLockWork',{params});
        if(resp.data?.status==='success'){
          const rows=resp.data.data||[];
          if(rows.length){
            this.dynamicColumns=Object.keys(rows[0]).map(k=>({prop:k,label:k,width:k.includes('锁类分区')?140:120}));
          }
          this.dynamicData=rows;
        }
      }catch(e){
        console.error('数据获取失败',e);
        this.$message.error('数据获取失败');
      }finally{
        this.loading=false;
      }
    },
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
      this.breadcrumbItems = ['报工数量统计工时'];
        }
    },
    handleSearch(){
      this.fetchData();
    },
    resetForm(){
      this.queryParams={lockArea:'',startWeek:null,endWeek:null};
      this.fetchData();
    }
  }
}
</script>

<style scoped>
.search-form{padding:10px;background:#fff;border-radius:4px;margin-bottom:8px;}
.form-actions{display:flex;justify-content:right;width:100%;margin-top:15px;}
.center-actions{display:flex;gap:10px;}
.data-preview{margin-top:15px;padding:15px;background:#fff;border-radius:4px;box-shadow:0 2px 12px rgba(0,0,0,.1);}
.loading-message{text-align:center;padding:230px;font-size:30px;color:#606266;}
</style>
