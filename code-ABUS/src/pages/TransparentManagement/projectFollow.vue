<!-- 项目跟进 -->

<template>
  <Layout>
    <!-- 负责人统计区域 -->
    <div class="owner-stats-container">
      <div class="collapse-header" @click="toggleOwnerStats">
        <i :class="ownerStatsExpanded ? 'el-icon-arrow-down' : 'el-icon-arrow-right'"></i>
        <span>负责人项目统计</span>
      </div>
      <div v-if="ownerStatsExpanded" class="owner-stats-content">
        <el-table :data="ownerStatsTableData" border stripe style="width: 100%" max-height="300">
          <el-table-column prop="owner" label="负责人" width="150" align="center">
          </el-table-column>
          <el-table-column prop="projects" label="负责项目" align="left">
            <template slot-scope="{row}">
              <el-tag v-for="(project, index) in row.projects" :key="index" size="small" style="margin: 2px 5px">
                {{ project }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="count" label="项目数量" width="100" align="center">
          </el-table-column>
        </el-table>
      </div>
    </div>

    <div class="action-search-container">
      <!-- 添加项目按钮 -->
      <div class="action-bar">
        <el-button type="primary" @click="showAddDialog">添加项目</el-button>
      </div>
      <div class="right-container">
        <div class="reset-bar">
          <el-button type="warning" @click="clearSearch">刷新重置</el-button>
        </div>
        <!--搜索框-->
        <div class="search-box">
          <input type="text" placeholder="搜索..." v-model="searchQuery" @keyup.enter="handleSearch"
            style="border-radius: 10px;" />
          <img v-if="searchQuery" class="clear-icon" src="../photo/delete.png" @click="clearSearch" alt="清除" />
          <img v-else class="search-icon" src="../photo/search.png" @click="performSearch" alt="搜索" />
        </div>
      </div>
    </div>

    <!-- 数据表格 -->
    <div v-if="dynamicData.length > 0" class="data-preview">
      <!-- 添加搜索结果提示 -->
      <div v-if="showSearchMessage" class="search-result-message">
        <el-alert :title="searchMessage" type="info" :closable="false" show-icon>
        </el-alert>
      </div>
      <!-- 表格下方分页器 -->
      <el-table :key="tableKey" :data="dynamicData" border stripe v-loading="loading" element-loading-text="数据加载中..."
        style="width: 100%; margin-top: 20px">
        <el-table-column v-for="(col, index) in pagedColumns" :key="index" :prop="col.prop"
          :label="col.label.length > 10 ? col.label.substring(0, 10) + '...' : col.label" :width="col.width"
          :sortable="col.sortable" align="center">
          <template slot="header">
            <div class="column-header" @click="handleHeaderClick(col)">
              <div class="status-tag" v-if="col.prop !== '日期'" @click.stop="handleStatusClick(col)">
                <el-tag v-if="getProjectOwners(col.prop)" type="info" size="small" style="margin-right: 5px;">
                  {{ getProjectOwners(col.prop) }}
                </el-tag>
                <el-tag :type="getProjectStatus(col.prop) === '结案' ? 'success' : 'warning'" size="small">
                  {{ getProjectStatus(col.prop) }}
                </el-tag>
              </div>
              <span>{{ col.label.length > 20 ? col.label.substring(0, 20) + '...' : col.label }}</span>
            </div>
          </template>
          <template slot-scope="{row}">
            <span v-if="col.prop === '日期'">
              {{ row[col.prop] }}
            </span>
            <span v-else-if="typeof row[col.prop] === 'number'" @click="handleCellClick(row, col)"
              class="clickable-cell">
              {{ row[col.prop].toLocaleString() }}
            </span>
            <span v-else @click="handleCellClick(row, col)" class="clickable-cell">
              {{ row[col.prop] ? (row[col.prop].length > 10 ? row[col.prop].substring(0, 10) + '...' : row[col.prop]) :
                '' }}
            </span>
          </template>
        </el-table-column>
      </el-table>

      <div class="horizontal-pagination-bottom" v-if="totalPages > 1">
        <el-pagination background layout="prev, pager, next" :current-page="currentPage" :page-size="columnsPerPage"
          :total="totalColumns" @current-change="handlePageChange" />
      </div>
    </div>
    <div v-else-if="loading" class="loading-message">
      <p>数据加载中，请稍候...</p>
    </div>
    <!-- 数据为空提示 -->
    <div v-else>
      <p style="padding-top: 200px;padding-left: 700px;font-size: 35px;color: #002060;">暂无数据</p>
    </div>

    <!-- 添加项目弹窗 -->
    <el-dialog title="添加新项目" :visible.sync="addDialogVisible" width="50%" :close-on-click-modal="!hasAddProjectInput"
      :before-close="handleAddDialogClose">
      <el-form :model="newProject" label-width="100px">
        <el-form-item label="项目名">
          <el-input v-model="newProject.name" placeholder="请输入项目名"></el-input>
        </el-form-item>
        <el-form-item label="项目负责人">
          <el-input type="textarea" v-model="newProject.owners" placeholder="请输入项目负责人"
            :autosize="{ minRows: 1, maxRows: 3 }">
          </el-input>
        </el-form-item>
        <el-form-item label="项目内容">
          <el-input type="textarea" v-model="newProject.content" placeholder="请输入项目内容" :rows="9"
            :style="{ height: '200px', width: '750px' }">
          </el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="handleAddDialogClose">取消</el-button>
        <el-button type="primary" @click="handleAddProject">确认</el-button>
      </span>
    </el-dialog>

    <!-- 详细信息弹窗 -->
    <el-dialog title="项目详细信息" :visible.sync="dialogVisible" width="70%" :before-close="handleClose"
      :close-on-click-modal="!isEditing">
      <div class="detail-content">
        <div class="detail-item">
          <span class="detail-label">项目进度更新时间：</span>
          <span class="detail-value">{{ selectedCellData.date }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">项目名:</span>
          <span class="detail-value">{{ selectedCellData.label }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">项目负责人:</span>
          <span class="detail-value">{{ getProjectOwners(selectedCellData.label) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">项目内容:</span>
          <div v-if="!isEditing" class="detail-value text-wrap">{{ selectedCellData.value }}</div>
          <el-input v-else type="textarea" v-model="editContent" placeholder="请输入项目内容" :rows="12"
            :style="{ height: '250px', width: '1000px' }">
          </el-input>
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <template v-if="!isEditing">
          <el-button type="warning" @click="startEditing">修改内容</el-button>
          <el-button type="primary" @click="handleComplete">结案</el-button>
        </template>
        <template v-else>
          <el-button @click="cancelEditing">取消</el-button>
          <el-button type="primary" @click="saveEditing">保存</el-button>
        </template>
      </span>
    </el-dialog>

    <!-- 更新项目内容弹窗 -->
    <el-dialog title="更新项目进度" :visible.sync="updateDialogVisible" width="80%" custom-class="update-dialog" :top="'10vh'"
      :close-on-click-modal="!hasUpdateProjectInput" :before-close="handleUpdateDialogClose">
      <el-form :model="updateProject" label-width="100px">
        <el-form-item label="项目名">
          <el-input v-model="updateProject.name" disabled></el-input>
        </el-form-item>
        <el-form-item label="项目负责人">
          <el-input v-model="updateProject.owners" placeholder="请输入项目负责人" @blur="handleOwnersBlur">
          </el-input>
        </el-form-item>
        <el-form-item label="最新进度">
          <el-input type="textarea" v-model="updateProject.latestContent" disabled :rows="7"
            :style="{ height: '250px' }" placeholder="暂无内容">
          </el-input>
        </el-form-item>
        <el-form-item label="更新内容">
          <el-input type="textarea" v-model="updateProject.content" placeholder="请输入更新内容" :rows="7"
            :style="{ height: '200px' }">
          </el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="handleUpdateDialogClose">取消</el-button>
        <el-button type="info" @click="copyLatestContent">复制内容</el-button>
        <el-button type="warning" @click="clearContent">清空</el-button>
        <el-button type="primary" @click="handleUpdateProject">确认</el-button>
      </span>
    </el-dialog>
  </Layout>
</template>

<script>
import axios from 'axios'
import Layout from '@/components/Layout.vue'
import { eventBus } from '../../eventBus'
import { Converter } from 'opencc-js';

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
      allColumns: [], // 存储所有列配置
      sidebarMenus: [],
      showDynamicTable: false,
      attributeMap: new Map(),
      loading: false,
      dialogVisible: false,
      selectedCellData: {},
      addDialogVisible: false,
      searchQuery: '',
      searchResults: [],
      showSearchResults: false,
      isSearching: false,
      searchMessage: '',
      showSearchMessage: false,
      converter: null,
      clearSearchDebounce: null,
      newProject: {
        name: '',
        content: '',
        owners: ''
      },
      updateDialogVisible: false,
      updateProject: {
        name: '',
        content: '',
        latestContent: '',
        owners: ''
      },
      editContent: '',
      isEditing: false,
      tableKey: 0,
      savedScrollLeft: 0,
      pagedColumns: [],
      columnsPerPage: 7,
      currentPage: 1,
      totalPages: 1,
      totalColumns: 0,
      ownerStatsExpanded: false,
      ownerStatsData: {},
      ownerStatsTableData: [],
    }
  },
  computed: {
    hasAddProjectInput() {
      return this.newProject.name.trim() !== '' || this.newProject.content.trim() !== '' || this.newProject.owners.trim() !== '';
    },
    hasUpdateProjectInput() {
      return this.updateProject.content.trim() !== '';
    }
  },
  async mounted() {
    await this.fetchData();
    await this.fetchOwnerStats();
  },
  created() {
    eventBus.$on('sidebar-Menus-Updated', (menus) => {
      this.sidebarMenus = menus;
      this.generateBreadcrumb(this.$route.path);
    });

    this.converter = Converter({ from: 'hk', to: 'cn' });
  },
  watch: {
    $route(newVal) {
      this.activeMenu = newVal;
      this.generateBreadcrumb(newVal.path)
    }
  },
  methods: {
    calculatePagination() {
      // 以 dynamicColumns（已过滤搜索）为基础计算分页
      const nonDateCols = this.dynamicColumns.filter(col => col.prop !== '日期');
      this.totalColumns = nonDateCols.length;
      this.totalPages = Math.max(1, Math.ceil(nonDateCols.length / this.columnsPerPage));
      if (this.currentPage > this.totalPages) {
        this.currentPage = this.totalPages;
      }
      const startIdx = (this.currentPage - 1) * this.columnsPerPage;
      const pageSlice = nonDateCols.slice(startIdx, startIdx + this.columnsPerPage);
      const dateCol = this.dynamicColumns.find(col => col.prop === '日期');
      this.pagedColumns = dateCol ? [dateCol, ...pageSlice] : pageSlice;
    },
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
        this.calculatePagination();
        this.tableKey += 1;
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
        this.calculatePagination();
        this.tableKey += 1;
      }
    },
    handlePageChange(page) {
      this.currentPage = page;
      this.calculatePagination();
      this.tableKey += 1;
    },
    getScrollContainer() {
      return this.$el.querySelector('.data-preview .el-table__body-wrapper');
    },
    saveScrollPosition() {
      const container = this.getScrollContainer();
      if (container) {
        this.savedScrollLeft = container.scrollLeft;
      }
    },
    restoreScrollPosition() {
      this.$nextTick(() => {
        const container = this.getScrollContainer();
        if (container) {
          container.scrollLeft = this.savedScrollLeft || 0;
        }
      });
    },
    convertText(text) {
      return this.converter(text);
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
        this.breadcrumbItems = ['项目跟进'];
      }
    },
    async fetchOwnerStats() {
      try {
        const response = await axios.get('/api/manage/owners');
        if (response.data?.status === 'success') {
          this.ownerStatsData = response.data.data || {};
          // 转换为表格数据格式并按负责人名称字母排序
          this.ownerStatsTableData = Object.entries(this.ownerStatsData)
            .map(([owner, projects]) => ({
              owner: owner,
              projects: projects,
              count: projects.length
            }))
            .sort((a, b) => {
              // 按照负责人名称的拼音首字母排序
              return a.owner.localeCompare(b.owner, 'zh-CN');
            });
        }
      } catch (error) {
        console.error('获取负责人统计失败:', error);
        // 失败时不影响页面，只是不显示负责人统计
        this.ownerStatsData = {};
        this.ownerStatsTableData = [];
      }
    },
    toggleOwnerStats() {
      this.ownerStatsExpanded = !this.ownerStatsExpanded;
    },
    getProjectOwners(projectName) {
      if (this.originalDataBackup.length > 0) {
        const ownerKey = `${projectName}_负责人`;
        const owners = this.originalDataBackup[0][ownerKey] || '';
        // 将 - 分隔符转换为中文顿号显示
        return owners.replace(/-/g, '、') || '未指定';
      }
      return '未指定';
    },
    async fetchData() {
      this.loading = true;
      // const startTime=new Date().getTime();
      try {
        const response = await axios.post('/api/manage', {}, {
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
          }
        });
        // const endTime=new Date().getTime();
        // const responseTime=endTime-startTime;
        // console.log(`请求耗时：${responseTime}ms`);


        if (response.data?.status === 'success') {
          this.originalDataBackup = [];
          this.dynamicData = [];
          this.allColumns = [];
          this.dynamicColumns = [];

          this.originalDataBackup = [...(response.data.data || [])];

          const processedData = this.originalDataBackup.map(item => {
            const processedItem = {};
            Object.entries(item).forEach(([key, val]) => {
              if (!key.endsWith('_状态')) {
                processedItem[key] = val;
              }
            });
            return processedItem;
          });

          if (processedData.length > 0) {
            const newColumns = Object.keys(processedData[0]).map(key => ({
              prop: key,
              label: key,
              width: key === '日期' ? '120px' : '200px',
              sortable: key === '日期'
            }));


            this.allColumns = newColumns;
            this.dynamicColumns = [...newColumns];
            this.calculatePagination();

            this.dynamicData = processedData.sort((a, b) => {
              const dateA = new Date(a['日期']);
              const dateB = new Date(b['日期']);
              return dateB - dateA;
            });
          }

          this.$nextTick(() => {
            this.$forceUpdate();
            this.restoreScrollPosition();
          });
        }
      } catch (error) {
        console.error('数据获取失败:', error);
        this.$message.error('数据加载失败，请检查网络连接');
      } finally {
        this.loading = false;
        this.tableKey += 1;
      }
    },
    handleCellClick(row, col) {
      const status = this.getProjectStatus(col.prop);

      if (status === '结案') {
        return;
      }

      this.selectedCellData = {
        label: col.prop,
        value: row[col.prop],
        date: row['日期']
      };
      this.dialogVisible = true;
    },
    handleClose() {
      if (this.isEditing) {
        this.$confirm('您有未保存的修改，确定要关闭吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          this.dialogVisible = false;
          this.selectedCellData = {};
          this.isEditing = false;
          this.editContent = '';
        }).catch(() => {
        });
      } else {
        this.dialogVisible = false;
        this.selectedCellData = {};
        this.isEditing = false;
        this.editContent = '';
      }
    },
    async handleComplete() {
      try {
        const response = await axios.post('/api/manage/update', {
          projectName: this.selectedCellData.label,
          status: '结案'
        });

        if (response.data?.status === 'success') {
          this.$message.success('结案成功');
          this.saveScrollPosition();
          await this.fetchData();
          this.restoreScrollPosition();
          this.handleClose();
          this.$forceUpdate();
        }
      } catch (error) {
        console.error('结案失败:', error);
        this.$message.error('结案失败，请重试');
      }
    },
    showAddDialog() {
      this.addDialogVisible = true;
      this.newProject = {
        name: '',
        content: '',
        owners: ''
      };
    },
    handleAddDialogClose() {
      if (this.hasAddProjectInput) {
        this.$confirm('您有未保存的修改，确定要关闭吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          this.addDialogVisible = false;
          this.newProject = {
            name: '',
            content: '',
            owners: ''
          };
        }).catch(() => {
        });
      } else {
        this.addDialogVisible = false;
        this.newProject = {
          name: '',
          content: '',
          owners: ''
        };
      }
    },
    async handleAddProject() {
      try {
        const response = await axios.post('/api/manage/add', {
          projectName: this.newProject.name,
          projectContent: this.newProject.content,
          projectOwners: this.newProject.owners
        });

        if (response.data?.status === 'success') {
          this.$message.success('项目添加成功');
          this.addDialogVisible = false;
          this.saveScrollPosition();
          await this.fetchData();
          await this.fetchOwnerStats();
          this.restoreScrollPosition();
          this.$forceUpdate();
        }
      } catch (error) {
        console.error('添加项目失败:', error);
        this.$message.error('添加项目失败，请重试');
      }
    },
    getProjectStatus(projectName) {
      if (this.originalDataBackup.length > 0) {
        const statusKey = `${projectName}_状态`;
        return this.originalDataBackup[0][statusKey] || '未结案';
      }
      return '未结案';
    },
    handleStatusClick(col) {
      const currentStatus = this.getProjectStatus(col.prop);
      const action = currentStatus === '结案' ? '反结案' : '结案';

      this.$confirm(`是否确认${action}该项目?`, `${action}确认`, {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          const response = await axios.post('/api/manage/update', {
            projectName: col.prop,
            status: currentStatus === '结案' ? '未结案' : '结案'
          });

          if (response.data?.status === 'success') {
            this.$message.success(`${action}成功`);
            this.saveScrollPosition();
            this.dynamicData = [];
            this.dynamicColumns = [];
            await this.fetchData();
            this.restoreScrollPosition();
            this.$nextTick(() => {
              this.$forceUpdate();
            });
          }
        } catch (error) {
          console.error(`${action}失败：`, error);
          this.$message.error(`${action}失败, 请重试`);
        }
      }).catch(() => {
        this.$message.info(`已取消${action}`);
      });
    },
    handleHeaderClick(col) {
      if (col.prop === '日期') {
        return;
      }
      const status = this.getProjectStatus(col.prop);

      if (status === '结案') {
        this.$message.warning('该项目已结案，无法更新');
        return;
      }

      let latestContent = '';
      //console.log('原始数据!!!!',this.originalDataBackup);
      if (this.originalDataBackup.length > 0) {
        for (let i = this.originalDataBackup.length - 1; i >= 0; i--) {
          const data = this.originalDataBackup[i];
          if (data[col.prop]) {
            latestContent = data[col.prop];
            break;
          }
        }
      }
      this.updateProject = {
        name: col.prop,
        content: '',
        latestContent: latestContent,
        owners: this.getProjectOwners(col.prop)
      };

      this.updateDialogVisible = true;
    },
    async handleUpdateProject() {
      try {
        if (!this.updateProject.content.trim()) {
          this.$message.warning('请输入更新内容');
          return;
        }

        const response = await axios.post('/api/manage/add', {
          projectName: this.updateProject.name,
          projectContent: this.updateProject.content,
        });

        if (response.data?.status === 'success') {
          this.$message.success('更新成功');
          this.updateDialogVisible = false;
          this.saveScrollPosition();
          await this.fetchData();
          this.restoreScrollPosition();
          this.$forceUpdate();
        } else {
          this.$message.error(response.data?.message || '更新失败');
        }
      } catch (error) {
        console.error('更新失败:', error);
        if (error.response) {
          this.$message.error(error.response.data?.message || '更新失败，请重试');
        } else {
          this.$message.error('更新失败，请检查网络连接');
        }
      }
    },
    startEditing() {
      this.isEditing = true;
      this.editContent = this.selectedCellData.value;
    },

    cancelEditing() {
      this.isEditing = false;
      this.editContent = '';
    },

    async saveEditing() {
      try {
        if (!this.editContent.trim()) {
          this.$message.warning('请输入项目内容');
          return;
        }
        const response = await axios.post('/api/manage/edit', {
          projectName: this.selectedCellData.label,
          projectContent: this.editContent,
          date: this.selectedCellData.date
        });

        if (response.data?.status === 'success') {
          this.$message.success('修改成功');
          this.isEditing = false;
          this.editContent = '';
          this.dialogVisible = false;
          this.saveScrollPosition();
          await this.fetchData();
          this.restoreScrollPosition();
        } else {
          this.$message.error(response.data?.message || '修改失败');
        }
      } catch (error) {
        console.error('修改失败:', error);
        if (error.response) {
          this.$message.error(error.response.data?.message || '修改失败，请重试');
        } else {
          this.$message.error('修改失败，请检查网络连接');
        }
      }
    },
    handleCloseEdit() {
      this.editDialogVisible = false;
      this.editProject = {
        name: '',
        content: ''
      };
    },
    copyLatestContent() {
      this.updateProject.content = this.updateProject.latestContent;
      this.$message.success('已复制最新进度内容');
    },
    clearContent() {
      this.updateProject.content = '';
      this.$message.success('已清空更新内容');
    },
    handleUpdateDialogClose() {
      if (this.hasUpdateProjectInput) {
        this.$confirm('您有未保存的修改，确定要关闭吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          this.updateDialogVisible = false;
          this.updateProject = {
            name: '',
            content: '',
            latestContent: '',
            owners: ''
          };
        }).catch(() => {
        });
      } else {
        this.updateDialogVisible = false;
        this.updateProject = {
          name: '',
          content: '',
          latestContent: '',
          owners: ''
        };
      }
    },
    async handleOwnersBlur() {
      // 获取当前输入的负责人信息，去除前后空格
      const currentOwners = this.updateProject.owners.trim();
      const projectName = this.updateProject.name;

      // 获取原始的负责人信息（从 originalDataBackup 中获取）
      const originalOwners = this.getProjectOwners(projectName);

      // 如果负责人信息没有变化，不执行更新
      if (currentOwners.replace(/\n/g, '、') === originalOwners) {
        return;
      }

      try {
        const response = await axios.post('/api/manage/update-owners', {
          projectName: projectName,
          owners: currentOwners
        });

        if (response.data?.status === 'success') {
          this.$alert(
            `${response.data.message}`,
            '负责人更新成功',
            {
              confirmButtonText: '确定',
              type: 'success'
            }
          );

          // 刷新数据
          await this.fetchData();
          await this.fetchOwnerStats();
        }
      } catch (error) {
        console.error('更新负责人失败:', error);
        this.$alert(
          '更新负责人失败，请重试',
          '错误',
          {
            confirmButtonText: '确定',
            type: 'error'
          }
        );
      }
    },
    handleSearch(event) {
      if (event.key === 'Enter') {
        this.performSearch();
      }
    },
    performSearch() {
      if (!this.searchQuery.trim()) {
        this.dynamicColumns = [...this.allColumns];
        this.showSearchMessage = false;
        return;
      }
      this.isSearching = false;
      this.showSearchResults = true;
      this.showSearchMessage = true;
      this.searchMessage = '正在搜索中...';

      const searchKeyword = this.convertText(this.searchQuery.toLowerCase());

      this.dynamicColumns = this.allColumns.filter(col => {
        const convertedLabel = this.convertText(col.label.toLowerCase());
        return col.prop === '日期' || convertedLabel.includes(searchKeyword);
      });
      // console.log('搜索结果',this.dynamicColumns);

      this.searchMessage = this.dynamicColumns.length > 0
        ? `找到 ${this.dynamicColumns.length - 1} 个相关列`
        : '暂无符合相关要求的列';

      this.currentPage = 1;
      this.calculatePagination();
    },
    clearSearch() {
      if (this.clearSearchDebounce) {
        clearTimeout(this.clearSearchDebounce);
      }

      this.clearSearchDebounce = setTimeout(async () => {
        this.loading = true;
        try {
          this.searchQuery = '';
          this.showSearchResults = false;
          this.searchResults = [];
          this.showSearchMessage = false;

          this.saveScrollPosition();
          await this.fetchData();
          this.restoreScrollPosition();
          this.dynamicColumns = [...this.allColumns];
          this.currentPage = 1;
          this.calculatePagination();

          this.$message.success('已重置');
        } catch (error) {
          console.error('数据刷新失败:', error);
          this.$message.error('数据刷新失败，请重试');
        } finally {
          this.loading = false;
        }
      }, 300);
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
  max-height: calc(100% - 60px);
  /* 根据实际高度调整 */
  overflow-y: auto;
}

.form-actions {
  display: flex;
  justify-content: right;
  /* 水平居中 */
  width: 100%;
  margin-top: 15px;
}

.center-actions {
  display: flex;
  gap: 10px;
  /* 按钮间距 */
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
  margin-top: 10px;
  padding: 15px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, .1);
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
}

.data-preview /deep/ .el-table {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.data-preview /deep/ .el-table__header-wrapper {
  position: sticky;
  top: 0;
  z-index: 1;
}

.data-preview /deep/ .el-table__body-wrapper {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.data-preview /deep/ .el-table__body {
  width: 100%;
}

.data-preview /deep/ .el-table__header {
  width: 100%;
}


/* 添加底部滚动条容器 */
.data-preview::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 15px;
  background: #fff;
  overflow-x: auto;
  overflow-y: hidden;
  z-index: 2;
}

/* 自定义滚动条样式 */
.data-preview /deep/ .el-table__body-wrapper::-webkit-scrollbar,
.data-preview::after::-webkit-scrollbar {
  height: 8px;
  width: 8px;
}

.data-preview /deep/ .el-table__body-wrapper::-webkit-scrollbar-thumb,
.data-preview::after::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 4px;
}

.data-preview /deep/ .el-table__body-wrapper::-webkit-scrollbar-track,
.data-preview::after::-webkit-scrollbar-track {
  background: #f5f5f5;
}

/* 同步水平滚动 */
.data-preview /deep/ .el-table__body-wrapper,
.data-preview::after {
  scrollbar-width: thin;
  scrollbar-color: #ddd #f5f5f5;
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
  flex: 1;
  overflow: auto;
  max-height: calc(100vh - 250px);
}

/* 表头样式 */
.el-table th {
  background-color: #f5f7fa !important;
  color: #333;
  height: 40px !important;
  line-height: 20px !important;
  padding: 8px 0 !important;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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

.clickable-cell {
  cursor: pointer;
  display: inline-block;
  width: 100%;
  height: 100%;
}

.clickable-cell:hover {
  background-color: #f5f7fa;
}

.detail-content {
  padding: 20px;
  max-width: 100%;
  word-wrap: break-word;
}

.detail-item {
  margin-bottom: 15px;
  display: flex;
  align-items: flex-start;
}

.detail-label {
  font-weight: bold;
  margin-right: 10px;
  min-width: 60px;
  flex-shrink: 0;
  color: red;
}

.detail-value {
  color: #606266;
  flex: 1;
  font-size: 20px;
}

.text-wrap {
  white-space: pre-wrap;
  word-break: break-all;
  line-height: 1.5;
}

.dialog-footer {
  text-align: right;
  margin-top: 20px;
}

.data-preview /deep/ .el-table__body-wrapper {
  overflow-y: auto;
  overflow-x: auto;
}

.data-preview /deep/ .el-table__header-wrapper {
  overflow: hidden;
}

.data-preview /deep/ .el-table__body td:first-child,
.data-preview /deep/ .el-table__header th:first-child {
  position: sticky;
  left: 0;
  background-color: white;
  z-index: 1;
}

.data-preview /deep/ .el-table__header th:first-child {
  z-index: 2;
  /* 确保表头在内容之上 */
  background-color: #f5f7fa !important;
  /* 保持表头背景色 */
}

/* 负责人统计区域样式 */
.owner-stats-container {
  margin-bottom: 15px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, .1);
}

.collapse-header {
  padding: 12px 20px;
  background: #f5f7fa;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  border-radius: 4px 4px 0 0;
  transition: background 0.3s;
}

.collapse-header:hover {
  background: #e8eaed;
}

.collapse-header i {
  font-size: 16px;
  color: #606266;
  transition: transform 0.3s;
}

.collapse-header span {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.owner-stats-content {
  padding: 15px;
  border-top: 1px solid #ebeef5;
}

.action-bar {
  margin-bottom: 2px;
  display: flex;
  justify-content: left;
}

.reset-bar {
  margin-bottom: 2px;
  display: flex;
  justify-content: left;
}

.column-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.status-tag {
  margin-bottom: 5px;
}

.el-tag {
  margin: 0;
}


.action-search-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  /* 整体与下方内容的间距 */
}

.right-container {
  display: flex;
  align-items: center;
  gap: 16px;
  /* 重置按钮和搜索框之间的间距 */
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

.el-message {
  z-index: 99999 !important;
}

.page-indicator {
  font-size: 14px;
  color: #606266;
}

/* 隐藏旧的顶部分页条 */
.horizontal-pagination {
  display: none;
}

.horizontal-pagination-bottom {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}
</style>

<style>
.update-dialog .el-dialog__title {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.update-dialog .el-form-item__label {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.update-dialog .el-input__inner,
.update-dialog .el-textarea__inner {
  font-size: 20px;
  color: #303133;
  line-height: 1.5;
}

.update-dialog .el-dialog__body {
  padding: 20px 30px;
}

.update-dialog .el-dialog__footer {
  padding: 20px 30px;
}

.update-dialog .el-button {
  font-size: 16px;
  padding: 12px 20px;
}

.update-dialog .el-input.is-disabled .el-input__inner,
.update-dialog .el-textarea.is-disabled .el-textarea__inner {
  color: #303133;
  background-color: #f5f7fa;
}

.update-dialog .el-textarea__inner {
  min-height: 200px !important;
  resize: none;
}
</style>