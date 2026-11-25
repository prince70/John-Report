<!-- 透明化管理申请页面 -->
<template>
  <Layout :breadcrumbItems="breadcrumbItems">
    <!-- 添加新建按钮 -->
    <div class="action-container">
      <el-button type="primary" @click="showDialog = true">新建项目</el-button>
    </div>
    <!-- 查询框 -->
    <div class="action-search-container">
      <div class="right-container">
        <div class="reset-bar">
          <el-button type="warning" @click="clearSearch">刷新重置</el-button>
        </div>
        <div class="search-box">
          <input type="text" placeholder="搜索..." v-model="searchQuery" @keyup.enter="performSearch"
            style="border-radius: 10px;" />
          <img v-if="searchQuery" class="clear-icon" src="../photo/delete.png" @click="clearSearch" alt="清除" />
          <img v-else class="search-icon" src="../photo/search.png" @click="performSearch" alt="搜索" />
        </div>
      </div>
    </div>
    <!-- 数据展示框 -->
    <div v-if="dynamicData.length > 0" class="data-preview">
      <div v-if="showSearchMessage" class="search-result-message">
        <el-alert :title="searchMessage" type="info" :closable="false" show-icon />
      </div>
      <el-table :data="dynamicData" border stripe v-loading="loading" element-loading-text="数据加载中..."
        style="width: 100%; margin-top: 20px" :max-height="560">
        <el-table-column v-for="(col, index) in dynamicColumns" :key="index" :prop="col.prop" :label="col.label"
          :width="col.width" :sortable="col.sortable" align="center">
          <template slot-scope="{row}">
            <div class="status-cell" v-if="col.prop === '状态'">
              <el-select v-model="row['状态']" placeholder="选择状态" size="mini" :disabled="!canAudit"
                :class="['status-select', statusSelectClass(row['状态'])]" :popper-class="'status-select-popper'"
                style="width: 100px;" @visible-change="(show) => { if (show) { row._oldStatus = row['状态'] } }"
                @change="(val) => handleStatusChange(row, val)">
                <el-option v-for="opt in statusOptions" :key="opt.value" :label="opt.label" :value="opt.value">
                  <span class="status-option-pill" :class="statusBgClass(opt.value)">{{ opt.label }}</span>
                </el-option>
              </el-select>
            </div>
            <div v-else-if="col.prop === '批复时间'" class="editable-cell" @click="canAudit && openDateEditor(row)">
              <span :class="{ 'editable-text': canAudit }">{{ row[col.prop] || '未设置' }}</span>
              <i v-if="canAudit" class="el-icon-edit edit-icon"></i>
            </div>
            <div v-else-if="col.prop === '批复意见'" class="editable-cell" @click="openOpinionViewer(row)">
              <span :class="{ 'editable-text': canAudit }" class="text-ellipsis">{{ row[col.prop] || '未填写' }}</span>
              <i v-if="canAudit" class="el-icon-edit edit-icon"></i>
              <i v-else-if="row[col.prop]" class="el-icon-view view-icon"></i>
            </div>
            <div v-else-if="col.prop === '项目名称' || col.prop === '申请原因'" class="clickable-cell"
              @click="openDetailViewer(row)">
              <span class="text-ellipsis" :title="row[col.prop]">{{ row[col.prop] || '-' }}</span>
            </div>
            <span v-else-if="dateFields.includes(col.prop)">{{ row[col.prop] }}</span>
            <span v-else-if="typeof row[col.prop] === 'number'">{{ row[col.prop].toLocaleString() }}</span>
            <span v-else>{{ row[col.prop] }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div v-else-if="loading" class="loading-message">
      <p>数据加载中，请稍候...</p>
    </div>
    <div v-else>
      <p style="padding-top: 200px;padding-left: 700px;font-size: 35px;color: #002060;">暂无数据</p>
    </div>

    <!-- 批复时间编辑对话框 -->
    <el-dialog title="编辑批复时间" :visible.sync="showDateDialog" width="400px">
      <el-date-picker v-model="editingDate" type="date" placeholder="选择批复时间" value-format="yyyy-MM-dd"
        style="width: 100%;" />
      <div slot="footer">
        <el-button @click="showDateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveDateEdit">保存</el-button>
      </div>
    </el-dialog>

    <!-- 项目详情查看对话框 -->
    <el-dialog title="项目详细信息" :visible.sync="showDetailDialog" width="600px">
      <div class="detail-content">
        <div class="detail-item">
          <label>项目名称：</label>
          <div class="detail-value">{{ detailRow['项目名称'] || '-' }}</div>
        </div>
        <div class="detail-item">
          <label>申请原因：</label>
          <div class="detail-value">{{ detailRow['申请原因'] || '-' }}</div>
        </div>
      </div>
      <div slot="footer">
        <el-button type="primary" @click="showDetailDialog = false">关闭</el-button>
      </div>
    </el-dialog>

    <!-- 批复意见编辑/查看对话框 -->
    <el-dialog :title="canAudit ? '编辑批复意见' : '查看批复意见'" :visible.sync="showOpinionDialog" width="500px">
      <el-input type="textarea" :rows="5" v-model="editingOpinion" placeholder="请输入批复意见" :disabled="!canAudit" 
        :class="{'readonly-opinion': !canAudit}" />
      <div slot="footer">
        <el-button @click="showOpinionDialog = false">{{ canAudit ? '取消' : '关闭' }}</el-button>
        <el-button v-if="canAudit" type="primary" @click="saveOpinionEdit">保存</el-button>
      </div>
    </el-dialog>

    <!-- 新建项目对话框 -->
    <el-dialog title="新建透明化管理项目" :visible.sync="showDialog" width="600px">
      <el-form :model="form" label-width="100px" :rules="rules" ref="form">
        <el-form-item label="项目名称" prop="项目名称">
          <el-input v-model="form.项目名称" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="申请经理" prop="申请经理">
          <el-input v-model="form.申请经理" placeholder="请输入申请人姓名" />
        </el-form-item>
        <el-form-item label="预计完成时间" prop="预计完成时间">
          <el-date-picker v-model="form.预计完成时间" type="date" placeholder="选择日期" value-format="yyyy-MM-dd" />
        </el-form-item>
        <el-form-item label="申请原因" prop="申请原因">
          <el-input type="textarea" :rows="3" v-model="form.申请原因" placeholder="请详细描述申请原因" />
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm">提交</el-button>
      </div>
    </el-dialog>

  </Layout>
</template>

<script>
import axios from 'axios'
import Layout from '@/components/Layout.vue'

export default {
  components: { Layout },
  data() {
    return {
      // ==================== 页面基础配置 ====================
      
      // 面包屑导航路径，显示在页面顶部
      breadcrumbItems: ['透明化管理', '项目申请'],
      
      // ==================== 表格数据相关 ====================
      
      // 表格显示的数据数组，从后端 API 获取
      dynamicData: [],
      
      // 表格列配置数组，定义每列的属性（prop, label, width, sortable）
      dynamicColumns: [],
      
      // 所有列的配置备份，用于搜索和重置时恢复
      allColumns: [],
      
      // 数据加载状态标志，true 时显示 loading 动画
      loading: false,
      
      // 日期字段名称数组，用于特殊处理日期格式化
      dateFields: ['申请时间', '预计完成时间', '批复时间'],
      
      // ==================== 搜索功能相关 ====================
      
      // 搜索框输入的关键词
      searchQuery: '',
      
      // 是否显示搜索结果提示信息
      showSearchMessage: false,
      
      // 搜索结果提示文本内容（如"找到 5 条相关记录"）
      searchMessage: '',
      
      // ==================== 新建项目对话框相关 ====================
      
      // 控制新建项目对话框的显示/隐藏
      showDialog: false,
      
      // 新建项目表单数据对象
      form: {
        项目名称: '',      // 项目的名称
        申请经理: '',      // 申请人的姓名
        预计完成时间: '',  // 项目预计完成的日期（格式：yyyy-MM-dd）
        申请原因: ''       // 申请该项目的详细原因说明
      },
      
      // 新建项目表单的验证规则
      rules: {
        项目名称: [{ required: true, message: '项目名称不能为空', trigger: 'blur' }],
        申请经理: [{ required: true, message: '申请人不能为空', trigger: 'blur' }],
        预计完成时间: [{ required: true, message: '请选择预计完成时间', trigger: 'change' }]
      },
      
      // ==================== 状态审核相关 ====================
      
      // 状态下拉选项配置数组，包含三种审核状态
      statusOptions: [
        { label: '待审核', value: '待审核' },  // 蓝色矩形按钮
        { label: '已审核', value: '已审核' },      // 绿色矩形按钮
        { label: '驳回', value: '驳回' }       // 红色矩形按钮
      ],
      
      // ==================== 批复时间编辑相关 ====================
      
      // 控制批复时间编辑对话框的显示/隐藏
      showDateDialog: false,
      
      // 当前正在编辑批复时间的行数据对象
      editingRow: null,
      
      // 批复时间编辑框中的日期值（格式：yyyy-MM-dd）
      editingDate: '',
      
      // ==================== 批复意见编辑相关 ====================
      
      // 控制批复意见编辑/查看对话框的显示/隐藏
      showOpinionDialog: false,
      
      // 批复意见编辑框中的文本内容
      editingOpinion: '',
      
      // ==================== 项目详情查看相关 ====================
      
      // 控制项目详情对话框的显示/隐藏
      showDetailDialog: false,
      
      // 当前查看详情的项目数据对象（包含项目名称和申请原因）
      detailRow: {}
    }
  },
  async mounted() {
    await this.fetchData()
  },
  computed: {
    // 获取当前登录用户名
    // 优先级：Vuex store > localStorage savedUsername
    // 注意：Vuex 的正确路径是 state.user.username，不是 state.username
    currentUsername() {
      // 从 Vuex store 获取用户名（登录时设置）
      const vuexUsername = this.$store?.state?.user?.username
      // 如果 Vuex 中有用户名，使用它
      if (vuexUsername) {
        return vuexUsername
      }
      // 否则尝试从 localStorage 获取（记住账号功能）
      const savedUsername = localStorage.getItem('savedUsername')
      if (savedUsername) {
        return savedUsername
      }
      // 都没有则返回空字符串
      return ''
    },
    // 判断当前用户是否有审核权限
    // 只有 admin 和 John 这两个用户名可以审核
    canAudit() {
      return ['admin', 'John'].includes(this.currentUsername)
    }
  },
  methods: {
    // ==================== 样式相关方法 ====================
    
    // 根据状态值返回选择器的 CSS 类名（用于边框和文字颜色）
    statusSelectClass(val) {
      switch (val) {
        case '已审核':
          return 'is-approved'
        case '驳回':
          return 'is-rejected'
        case '待审核':
        default:
          return 'is-pending'
      }
    },
    // 根据状态值返回下拉选项的 CSS 类名（用于矩形按钮背景色）
    statusBgClass(val) {
      switch (val) {
        case '已审核':
          return 'opt-approved'
        case '驳回':
          return 'opt-rejected'
        case '待审核':
        default:
          return 'opt-pending'
      }
    },
    // ==================== 数据加载相关方法 ====================
    
    // 从后端加载项目列表数据
    // @param {boolean} bust - 是否破坏缓存（更新后需要刷新数据时传 true）
    async fetchData(bust = false) {
      this.loading = true
      try {
        console.log('连接中！！！');
        const response = await axios.post('/api/team/'); // 使用正确的API路径
        
        if (response.data?.status === 'success') {
          console.log("原始数据",response.data.data);
          this.originalDataBackup = response.data.data || [];
          this.dynamicData = response.data.data || [];
          
          if (this.dynamicData.length > 0) {
            // 自动生成列配置，使用弹性布局
            this.allColumns = Object.keys(this.dynamicData[0]).map(key => {
              return {
                prop: key,
                label: key,
                minWidth: 100, // 设置最小宽度，确保内容不会被压缩得太小
                sortable: true
              };
            });
            this.dynamicColumns = [...this.allColumns];
          }
        }
      } catch (e) {
        console.error('数据获取失败:', e);
        this.$message.error('数据获取失败: ' + (e.message || '未知错误'));
      } finally {
        this.loading = false;
      }
    },
    // ==================== 搜索功能相关方法 ====================
    
    // 执行搜索操作，在当前数据中过滤
    performSearch() {
      if (!this.searchQuery.trim()) {
        this.dynamicData = [...this.dynamicData]
        this.showSearchMessage = false
        return
      }
      const keyword = this.searchQuery.toLowerCase()
      const filtered = this.dynamicData.filter(row =>
        Object.values(row).some(v => typeof v === 'string' && v.toLowerCase().includes(keyword))
      )
      this.searchMessage = filtered.length > 0 ? `找到 ${filtered.length} 条相关记录` : '暂无符合相关要求数据'
      this.showSearchMessage = true
      this.dynamicData = filtered
    },
    // 清空搜索并重新加载数据
    clearSearch() {
      this.searchQuery = ''
      this.showSearchMessage = false
      this.fetchData()
      this.$message.success('已重置')
    },
    // ==================== 项目创建相关方法 ====================
    
    // 提交新建项目表单
    async submitForm() {
      try {
        await this.$refs.form.validate()
        const res = await axios.post('/api/team/', this.form)
        if (res.data.status === 'success') {
          this.$message.success('创建成功')
          this.showDialog = false
          await this.fetchData(true)
        }
      } catch (error) {
        this.$message.error('提交失败：' + error.response?.data?.detail || error.message)
      }
    },
    // ==================== 批复时间编辑相关方法 ====================
    
    // 打开批复时间编辑对话框（仅审核员可用）
    openDateEditor(row) {
      this.editingRow = row
      this.editingDate = row['批复时间'] || ''
      this.showDateDialog = true
    },
    // 保存批复时间到后端数据库
    async saveDateEdit() {
      if (!this.editingRow) return
      try {
        const res = await axios.put(
          `/api/team/${this.editingRow.id}/approval`,
          { 批复时间: this.editingDate },
          { params: { username: this.currentUsername } }
        )
        if (res.data?.status === 'success') {
          this.$message.success('批复时间已更新')
          this.showDateDialog = false
          await this.fetchData(true)
        }
      } catch (err) {
        this.$message.error('更新失败：' + (err.response?.data?.detail || err.message))
      }
    },
    // ==================== 项目详情查看相关方法 ====================
    
    // 打开项目详情对话框（显示项目名称和申请原因的完整内容）
    openDetailViewer(row) {
      this.detailRow = row
      this.showDetailDialog = true
    },
    // ==================== 批复意见编辑相关方法 ====================
    
    // 打开批复意见对话框（审核员可编辑，非审核员只能查看）
    openOpinionViewer(row) {
      this.editingRow = row
      this.editingOpinion = row['批复意见'] || ''
      this.showOpinionDialog = true
    },
    // 保存批复意见到后端数据库
    async saveOpinionEdit() {
      if (!this.editingRow) return
      try {
        const res = await axios.put(
          `/api/team/${this.editingRow.id}/approval`,
          { 批复意见: this.editingOpinion },
          { params: { username: this.currentUsername } }
        )
        if (res.data?.status === 'success') {
          this.$message.success('批复意见已更新')
          this.showOpinionDialog = false
          await this.fetchData(true)
        }
      } catch (err) {
        this.$message.error('更新失败：' + (err.response?.data?.detail || err.message))
      }
    },
    // ==================== 状态审核相关方法 ====================
    
    // 处理状态下拉框变更事件
    async handleStatusChange(row, newVal) {
      // 权限检查：非审核员不能修改状态
      if (!this.canAudit) {
        this.$message.warning('您没有审核权限')
        row['状态'] = row._oldStatus
        return
      }
      try {
        await this.$confirm(`确认将项目状态修改为 “${newVal}” 吗？`, '确认修改', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
      } catch (e) {
        // 取消，恢复原值
        row['状态'] = row._oldStatus
        return
      }

      try {
        const res = await axios.put(`/api/team/${row.id}/status`, { 状态: newVal }, { params: { username: this.currentUsername } })
        if (res.data?.status === 'success') {
          this.$message.success('状态已更新')
          await this.fetchData(true)
        } else {
          throw new Error(res.data?.detail || '更新失败')
        }
      } catch (err) {
        this.$message.error('更新失败：' + (err.response?.data?.detail || err.message))
        row['状态'] = row._oldStatus
      }
    }
  }
}
</script>

<style scoped>
/* ==================== el-table 弹性布局样式 ==================== */

/* 为el-table及其相关类添加flex布局 */
el-table,
.el-table--fit,
.el-table--striped,
.el-table--border,
.el-table--fluid-height,
.el-table--scrollable-y,
.el-table--enable-row-hover,
.el-table--enable-row-transition {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  min-height: 400px;
}

/* 表格头部样式 */
el-table .el-table__header-wrapper {
  flex-shrink: 0;
}

/* 表格主体样式 */
el-table .el-table__body-wrapper {
  flex: 1;
  overflow: auto;
}

/* 表格底部样式 */
el-table .el-table__footer-wrapper {
  flex-shrink: 0;
}

/* 确保表格容器也使用弹性布局 */
.data-preview {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 400px;
}

/* 调整表格列的弹性布局 */
el-table .el-table__header th,
el-table .el-table__body td {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-cell {
  display: inline-flex;
  align-items: center;
}

.status-option-pill {
  padding: 4px 20px;
  border-radius: 4px;
  font-size: 13px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 28px;
  line-height: 1;
  text-align: center;
  font-weight: 500;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* 选项颜色（矩形按钮风格） */
.opt-pending {
  background: #409eff;
  color: #ffffff;
}

.opt-approved {
  background: #67c23a;
  color: #ffffff;
}

.opt-rejected {
  background: #f56c6c;
  color: #ffffff;
}

/* ==================== 状态选择器样式（表格中的"状态"列下拉框） ====================

/* 选择器输入框基础样式 - 控制下拉框本体的外观 */
.status-select>>>.el-input__inner,
.status-select /deep/ .el-input__inner {
  height: 26px;            
  line-height: 26px;        
  padding: 0 24px 0 10px;    
  background: #fff;        
  border-radius: 6px;        
  border-color: #dcdfe6;     
  font-size: 12px;           
}

/* 鼠标悬停时的边框颜色变化 */
.status-select>>>.el-input__inner:hover,
.status-select /deep/ .el-input__inner:hover {
  border-color: #c0c4cc;     
}

/* 获得焦点时的样式（点击下拉框时） */
.status-select>>>.el-input.is-focus .el-input__inner,
.status-select /deep/ .el-input.is-focus .el-input__inner {
  border-color: #409eff;    
  box-shadow: 0 0 0 1px rgba(64, 158, 255, .15) inset; 
}

/* 下拉箭头图标的位置调整 */
.status-select>>>.el-input__suffix,
.status-select /deep/ .el-input__suffix {
  right: 6px;                /* 距离右边6px */
}

/* 根据不同状态值改变输入框的边框和文字颜色 */

/* 待审核状态 - 蓝色 */
.status-select.is-pending>>>.el-input__inner,
.status-select.is-pending /deep/ .el-input__inner {
  border-color: #409eff;     
  color: #409eff;            
  font-weight: 500;        
}

/* 已审核状态 - 绿色 */
.status-select.is-approved>>>.el-input__inner,
.status-select.is-approved /deep/ .el-input__inner {
  border-color: #67c23a;    
  color: #67c23a;          
  font-weight: 500;          
}

/* 驳回状态 - 红色 */
.status-select.is-rejected>>>.el-input__inner,
.status-select.is-rejected /deep/ .el-input__inner {
  border-color: #f56c6c;    
  color: #f56c6c;          
  font-weight: 500;          
}

/* ==================== 下拉菜单弹出层样式 ====================

/* 下拉菜单项的基础样式 */
.status-select-popper>>>.el-select-dropdown__item,
.status-select-popper /deep/ .el-select-dropdown__item {
  padding: 6px 12px;        
  text-align: center;       
}

/* 鼠标悬停在下拉选项上时的效果 */
.status-select-popper>>>.el-select-dropdown__item.hover .status-option-pill,
.status-select-popper /deep/ .el-select-dropdown__item.hover .status-option-pill {
  filter: brightness(1.05);  
  transform: translateY(-1px);  
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15); 
  transition: all 0.2s;      /* 0.2秒平滑过渡动画 */
}

/* 当前选中项的样式（蓝色外发光） */
.status-select-popper>>>.el-select-dropdown__item.selected .status-option-pill,
.status-select-popper /deep/ .el-select-dropdown__item.selected .status-option-pill {
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.3), 0 2px 6px rgba(0, 0, 0, 0.15);  /* 蓝色光晕 + 阴影 */
}

/* 下拉菜单容器的内边距（上下留白） */
.status-select-popper>>>.el-select-dropdown__wrap,
.status-select-popper /deep/ .el-select-dropdown__wrap {
  padding: 8px 0;          
}

/* ==================== 禁用状态样式（非审核员用户） ====================

/* 当用户没有审核权限时，下拉框变灰色且不可点击 */
.status-select.is-pending.is-disabled>>>.el-input__inner,
.status-select.is-approved.is-disabled>>>.el-input__inner,
.status-select.is-rejected.is-disabled>>>.el-input__inner,
.status-select.is-disabled>>>.el-input__inner {
  color: #909399 !important;       
  border-color: #e4e7ed !important; 
}

.action-search-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.right-container {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-box input {
  padding: 8px 32px 8px 16px;
  border: 1px solid #ddd;
  width: 200px;
  transition: all 0.3s;
}

.search-box input:focus {
  width: 300px;
  border-color: #4b9eec;
  outline: none;
}

.search-icon,
.clear-icon {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  cursor: pointer;
  transition: opacity 0.3s;
}

.search-icon:hover,
.clear-icon:hover {
  opacity: 0.8;
}

.data-preview {
  margin-top: 10px;
  padding: 15px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, .1);
}

.loading-message {
  text-align: center;
  padding: 230px;
  font-size: 30px;
  color: #606266;
}

.action-container {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 可编辑单元格样式 */
.editable-cell {
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 28px;
}

.editable-cell:hover {
  background: #f5f7fa;
}

.editable-text {
  color: #409eff;
  text-decoration: underline;
  text-decoration-style: dotted;
}

.edit-icon {
  color: #909399;
  font-size: 12px;
}

.view-icon {
  color: #409eff;
  font-size: 12px;
}

/* 文本省略号样式 */
.text-ellipsis {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
}

/* 可点击单元格样式 */
.clickable-cell {
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
  display: inline-flex;
  align-items: center;
}

.clickable-cell:hover {
  background: #f5f7fa;
}

.clickable-cell .text-ellipsis {
  color: #409eff;
}

/* 项目详情对话框样式 */
.detail-content {
  padding: 10px 0;
}

.detail-item {
  margin-bottom: 20px;
}

.detail-item label {
  display: block;
  color: #f56c6c;
  font-weight: 500;
  margin-bottom: 8px;
  font-size: 14px;
}

.detail-item .detail-value {
  color: #333;
  line-height: 1.6;
  font-size: 14px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

/* 批复意见只读模式样式 - 覆盖禁用状态的灰色 */
.readonly-opinion >>> .el-textarea__inner,
.readonly-opinion /deep/ .el-textarea__inner {
  color: #333 !important;
  background-color: #f5f7fa;
  cursor: default;
}
</style>