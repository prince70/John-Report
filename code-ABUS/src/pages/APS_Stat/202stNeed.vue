<!-- 锁体车间落货需求 -->

<template>
    <Layout :breadcrumbItems="breadcrumbItems">
        <!-- 搜索表单 -->
        <div class="search-form">
            <el-form :model="queryParams" label-width="100px">
                <el-row :gutter="20">
                <el-col :span="8">
                    <el-form-item label="锁类分区">
                    <el-select
                        v-model="queryParams.productAttribute"
                        placeholder="请选择类型"
                        clearable
                    >
                        <el-option
                        v-for="item in productAttributes"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value"
                        />
                    </el-select>
                    </el-form-item>
                </el-col>
                <el-col :span="8">
                    <el-form-item label="开始时间">
                    <el-date-picker
                        v-model="queryParams.startTime"
                        type="date"
                        placeholder="选择开始时间"
                        value-format="yyyy-MM-dd"
                        :picker-options="{
                        disabledDate: time => queryParams.endTime && time > new Date(queryParams.endTime)
                        }"
                    />
                    </el-form-item>
                </el-col>
                <el-col :span="8">
                    <el-form-item label="结束时间">
                    <el-date-picker
                        v-model="queryParams.endTime"
                        type="date"
                        placeholder="选择结束时间"
                        value-format="yyyy-MM-dd"
                        :picker-options="{
                        disabledDate: time => queryParams.startTime && time < new Date(queryParams.startTime)
                        }"
                    />
                    </el-form-item>
                </el-col>
                </el-row>

                <!-- 周数据统计显示区域 -->
                <el-row v-if="isSearched && weeklyStats.totalHours !== null" :gutter="20">
                    <el-col :span="8">
                        <el-form-item label="落货资讯" label-width="100px">
                            <el-input
                                :value="`未来4周需时= ${weeklyStats.totalHours.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`"
                                disabled
                                class="stats-input"
                            />
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
            <el-table
                :data="dynamicData"
                border
                stripe
                v-loading="loading"
                element-loading-text="数据加载中..."
                style="width: 100%; margin-top: 5px"
                max-height="500"
                :show-summary="true"
                :summary-method="getSummaries"
                >
                <el-table-column
                v-for="(col, index) in dynamicColumns"
                :key="index"
                :prop="col.prop"
                :label="col.label"
                :width="col.width"
                align="center">
                <!-- 添加数字格式化 -->
                <template slot-scope="{row}">
                    <span v-if="typeof row[col.prop] === 'number'">
                    {{ row[col.prop].toLocaleString() }}
                    </span>
                    <span v-else>
                    {{ row[col.prop] }}
                    </span>
                </template>
                </el-table-column>
            </el-table>
        </div>   
        <div v-else-if="loading" class="loading-message">
            <p>数据加载中，请稍候...</p>
        </div>
            <!-- 数据为空提示 -->
        <div v-else>
            <p style="padding-top: 200px;padding-left: 700px;font-size: 35px;color: #001E38;">暂无数据</p>
        </div>
    </Layout>  
</template>
    
<script>
import axios from 'axios'
import Layout from '@/components/Layout.vue'
import { eventBus } from '../../eventBus'
    
export default {
    components: {
        Layout
    },
    data() {
        return {
        breadcrumbItems: ['../'],
        originalDataBackup: [],
        dynamicData: [],
        dynamicColumns: [], // 动态生成的列配置
        sidebarMenus: [],
        showDynamicTable: false,
        attributeMap: new Map(),
        queryParams: {
            productAttribute: '', // 产品属性
            startTime: null,        // 开始时间
            endTime: null          // 结束时间
        },
        productAttributes:[
            { value: '1', label: '锁体A车间' },
            { value: '2', label: '锁体B车间' },
            { value: '3', label: '锁体B车间-混线' },
            { value: '4', label: '锁体C车间' },
            { value: '5', label: '锁体C车间-铝门锁' },
            { value: '6', label: '锁体D车间' },
        ],
        tableData: [],
        loading: false,
        // 新增：周数据统计
        isSearched: false,
        weeklyStats: {
            totalHours: null
        }
        }
    },
    async mounted() {
        await this.fetchData();
        this.productAttributes.forEach(attr => {
        this.attributeMap.set(attr.value, attr.label);
        });
    },
    created() {
        eventBus.$on('sidebar-Menus-Updated', (menus) => {
            this.sidebarMenus = menus;
            this.generateBreadcrumb(this.$route.path);
        });
    },
    watch: {
        $route(newVal) {
        this.generateBreadcrumb(newVal.path)
        }
    },
    methods: {
    // 获取选中区域标签
    getSelectedAreaLabel() {
        return this.attributeMap.get(this.queryParams.productAttribute) || '';
    },
    // 计算未来四周统计数据
    calculateWeeklyStats() {
        if (!this.dynamicData.length) {
            this.weeklyStats.totalHours = null;
            return;
        }

        // 获取当前日期和本周开始日期（周一开始）
        const now = new Date();
        const currentWeekStart = new Date(now);
        const dayOfWeek = now.getDay(); // 0=周日, 1=周一, ..., 6=周六
        const daysToMonday = dayOfWeek === 0 ? 6 : dayOfWeek - 1; // 计算到本周一的天数
        currentWeekStart.setDate(now.getDate() - daysToMonday);
        currentWeekStart.setHours(0, 0, 0, 0);

        // 计算未来四周结束日期
        const fourWeeksEnd = new Date(currentWeekStart);
        fourWeeksEnd.setDate(currentWeekStart.getDate() + 28); // 4周 = 28天
        fourWeeksEnd.setHours(23, 59, 59, 999);

        console.log('统计时间范围:', currentWeekStart, '到', fourWeeksEnd);

        let totalHours = 0;

        // 遍历筛选后的数据
        this.dynamicData.forEach(item => {
            if (item['日期范围']) {
                try {
                    const [startPart, endPart] = item['日期范围'].split('-');
                    const [startYear, startMonth, startDay] = startPart.split('/').map(Number);
                    const [endYear, endMonth, endDay] = endPart.split('/').map(Number);

                    const dataStart = new Date(startYear, startMonth - 1, startDay);
                    const dataEnd = new Date(endYear, endMonth - 1, endDay);

                    // 检查数据时间段是否与统计时间段重叠
                    if (dataStart <= fourWeeksEnd && dataEnd >= currentWeekStart) {
                        // 累加落货总数需时/h
                        const hours = Number(item['落货总数需时/h']) || 0;
                        totalHours += hours;
                        console.log(`添加数据: ${item['日期范围']}, 小时: ${hours}`);
                    }
                } catch (error) {
                    console.error('解析日期范围失败:', item['日期范围'], error);
                }
            }
        });

        this.weeklyStats.totalHours = totalHours;
        console.log('未来四周总小时数:', totalHours);
    },
    generateBreadcrumb(path) {
        try {
        const menus =this.sidebarMenus;

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
        this.breadcrumbItems = ['锁体车间-落货需求统计工时'];
        }
    },
    async fetchData() {
        this.loading = true;
        try {
            console.log('连接中！！！');
            const response = await axios.get('/api/stNeed');
            
            if (response.data?.status === 'success') {
            this.originalDataBackup = response.data.data || [];
            
            const processedData = this.originalDataBackup.map(item => {
                return Object.fromEntries(
                Object.entries(item).map(([key, val]) => [key, val || 0])
                );
            });
    
            this.dynamicColumns = Object.keys(processedData[0]).map(key => ({
                prop: key,
                label: key,
                width: key.includes('日期') ? 180 : 120
            }));
            
            this.dynamicData = processedData;
            console.log('数据初始化完成');
            }
        } catch (error) {
            console.error('数据获取失败:', error);
            this.$message.error('数据加载失败，请检查网络连接');
        } finally {
            this.loading = false;
        }
        },
        navigateTo(path) {
        this.$router.push(path);
        },
        handleSearch() {
        this.isSearched = true;
        this.fetchData().then(() => {
            const queryStart = this.queryParams.startTime ? new Date(this.queryParams.startTime) : null;
            const queryEnd = this.queryParams.endTime ? new Date(this.queryParams.endTime) : null;
            const selectedLabel = this.attributeMap.get(this.queryParams.productAttribute);
    
            if (!Array.isArray(this.originalDataBackup)) {
            console.error('原始数据未正确加载');
            return;
            }
            this.dynamicData = this.originalDataBackup.filter(item => {
            if (this.queryParams.productAttribute && 
                item.锁类分区 !== selectedLabel) {
                return false;
            }
    
            if (item['日期范围']) {
                const [startPart, endPart] = item['日期范围'].split('-');
                //console.log(startPart,endPart)
                const [startYear, startMonth, startDay] = startPart.split('/').map(Number);
                const [endYear, endMonth, endDay] = endPart.split('/').map(Number);
    
                const dataStart = new Date(startYear, startMonth - 1, startDay);
                const dataEnd = new Date(endYear, endMonth - 1, endDay);
    
                //console.log(queryStart,queryEnd,dataStart,dataEnd)
                if (queryStart && !queryEnd) {
                    if(dataEnd < queryStart) return false;
                }
                if (!queryStart && queryEnd) {
                    if(dataStart > queryEnd) return false;
                }
                if (queryStart && queryEnd) {
                    if (dataStart > queryEnd || dataEnd < queryStart) return false;
                }
            }
    
            return true;
            });
            
            // 计算未来四周统计数据
            this.calculateWeeklyStats();
        });
        if (!this.queryParams.productAttribute && 
            !this.queryParams.startTime && 
            !this.queryParams.endTime) {
            this.dynamicData = [...this.originalDataBackup];
            // 计算未来四周统计数据
            this.calculateWeeklyStats();
        }
        },
        resetForm() {
        this.queryParams = {
            productAttribute: '',
            startTime: null,
            endTime: null
        };
        this.dynamicData = [...this.originalDataBackup];
        // 重置统计数据显示
        this.isSearched = false;
        this.weeklyStats.totalHours = null;
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
.search-form {
padding: 15px;
background: #fff;
border-radius: 4px;
margin-bottom: 8px;
max-height: calc(100% - 60px); /* 根据实际高度调整 */
overflow-y: auto;
}

.form-actions {
display: flex;
justify-content: right; /* 水平居中 */
width: 100%;
margin-top: 15px;
}

.center-actions {
display: flex;
gap: 10px; /* 按钮间距 */
}

.upload-wrapper {
display: inline-block;
margin-left: 10px;
}
.el-date-editor {
width: 100%;
}

.search-form .el-form-item__content {
width: 100%;
}
.search-form .el-input,
.search-form .el-select {
width: 80% !important;
}

/* 保持表单布局稳定 */
.el-row {
margin-bottom: 18px;
}
.el-col {
display: flex;
flex-direction: column;
}
.import-preview {
background: #f8f9fa;
border: 1px solid #ebeef5;
border-radius: 4px;
padding: 15px;
margin-bottom: 20px;
}

.import-preview h4 {
color: #606266;
margin-bottom: 10px;
}

.preview-actions {
margin-top: 15px;
text-align: right;
}
.data-preview {
margin-top: 25px;
padding: 15px;
background: #fff;
border-radius: 4px;
box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
overflow-x: auto;
}

.data-preview h4 {
margin-bottom: 0px;
color: #606266;
}

.data-preview table {
width: 100%;
margin-top: 15px;
border-collapse: collapse;
background: white;
}

.data-preview th {
background-color: #7799AA !important;
color: white !important;
padding: 8px !important;
}

.data-preview td {
padding: 8px !important;
border: 1px solid #ebeef5;
}

.data-preview tr:nth-child(even) {
background-color: #fafafa !important;
}


/* 优化表格显示 */

.data-preview /deep/ .el-table {
max-height: 500px !important; /* 增大表格高度 */
font-size: 15px;
}
/* 表头样式 */
.el-table th {
background-color: #f5f7fa !important;
color: #333;
}


/* 数字列右对齐 */
.el-table .cell {
text-align: center;
}

.el-table .cell.number-cell {
text-align: right;
padding-right: 15px;
}

/* 加载提示样式 */
.el-loading-mask {
background-color: rgba(255, 255, 255, 0.8);
}
.loading-message {
text-align: center;
padding: 230px;
font-size: 30px;
color: #606266;
}
.cascading-select {
position: relative;
display: inline-block;
width: 100%;
}

.sub-menu-popup {
position: fixed;
background: white;
border: 1px solid #DCDFE6;
border-radius: 4px;
box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
z-index: 2000;
min-width: 150px;
max-height: 300px;
overflow-y: auto;
}

.sub-menu-item {
padding: 8px 16px;
cursor: pointer;
transition: background-color 0.3s;
}

.sub-menu-item:hover {
background-color: #f5f7fa;
}

/* 统计输入框样式 */
.stats-input /deep/ .el-input__inner {
  background-color: #ffffff !important;
  border: 1px solid #dcdfe6 !important;
  color: #303133 !important;
  font-weight: normal !important;
  text-align: left;
}
</style>