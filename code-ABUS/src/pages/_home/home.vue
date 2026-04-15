<template>
  <Layout>
    <!-- 本月订单统计 -->
    <div class="order-section" v-loading="isLoadingOrders" element-loading-text="统计数据加载中...">
      <div class="section-header">
        <h3 class="section-title">本月订单统计</h3>
      </div>
      <div class="order-stats">
        <div
          v-for="(item, index) in orderItems.slice(0, 6)"
          :key="index"
          class="stat-item"
          @click="navigateTo(item.path)"
        >
          <svg class="stat-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- 订单 -->
            <template v-if="item.icon === 'order'">
              <rect x="4" y="3" width="16" height="18" rx="2" stroke="currentColor" stroke-width="1.5"/>
              <line x1="8" y1="8" x2="16" y2="8" stroke="currentColor" stroke-width="1.5"/>
              <line x1="8" y1="12" x2="16" y2="12" stroke="currentColor" stroke-width="1.5"/>
              <line x1="8" y1="16" x2="12" y2="16" stroke="currentColor" stroke-width="1.5"/>
            </template>
            <!-- 地球/国家 -->
            <template v-else-if="item.icon === 'globe'">
              <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.5"/>
              <ellipse cx="12" cy="12" rx="4" ry="9" stroke="currentColor" stroke-width="1.5"/>
              <line x1="3" y1="12" x2="21" y2="12" stroke="currentColor" stroke-width="1.5"/>
              <path d="M3 6h18M3 18h18" stroke="currentColor" stroke-width="1.5"/>
            </template>
            <!-- 盒子/数量 -->
            <template v-else-if="item.icon === 'box'">
              <rect x="4" y="6" width="16" height="14" rx="2" stroke="currentColor" stroke-width="1.5"/>
              <path d="M4 10h16M12 10v10" stroke="currentColor" stroke-width="1.5"/>
              <path d="M8 6V4a4 4 0 0 1 8 0v2" stroke="currentColor" stroke-width="1.5"/>
            </template>
            <!-- 装嵌/装配 -->
            <template v-else-if="item.icon === 'assembly'">
              <rect x="3" y="8" width="8" height="8" rx="1" stroke="currentColor" stroke-width="1.5"/>
              <rect x="13" y="8" width="8" height="8" rx="1" stroke="currentColor" stroke-width="1.5"/>
              <path d="M7 12h10M12 8v4" stroke="currentColor" stroke-width="1.5"/>
            </template>
            <!-- 包装 -->
            <template v-else-if="item.icon === 'pack'">
              <rect x="3" y="8" width="18" height="13" rx="2" stroke="currentColor" stroke-width="1.5"/>
              <path d="M3 12h18" stroke="currentColor" stroke-width="1.5"/>
              <path d="M10 3l2 5h-4l2-5z" stroke="currentColor" stroke-width="1.5"/>
              <line x1="8" y1="5" x2="8" y2="8" stroke="currentColor" stroke-width="1.5"/>
              <line x1="16" y1="5" x2="16" y2="8" stroke="currentColor" stroke-width="1.5"/>
            </template>
            <!-- 完成/落货 -->
            <template v-else-if="item.icon === 'check'">
              <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.5"/>
              <path d="M8 12l3 3 5-6" stroke="currentColor" stroke-width="1.5"/>
            </template>
          </svg>
          <div class="stat-details">
            <div class="stat-title">{{ item.title }}</div>
            <div class="stat-value">{{ item.value }}</div>
          </div>
        </div>
      </div>
    </div>
    <!-- 下月订单统计 -->
    <div class="order-section" v-loading="isLoadingOrders" element-loading-text="统计数据加载中...">
      <div class="section-header">
        <h3 class="section-title">下月订单统计</h3>
      </div>
      <div class="order-stats">
        <div
          v-for="(item, index) in orderItems.slice(6)"
          :key="index + 6"
          class="stat-item"
          @click="navigateTo(item.path)"
        >
          <svg class="stat-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <template v-if="item.icon === 'order'">
              <rect x="4" y="3" width="16" height="18" rx="2" stroke="currentColor" stroke-width="1.5"/>
              <line x1="8" y1="8" x2="16" y2="8" stroke="currentColor" stroke-width="1.5"/>
              <line x1="8" y1="12" x2="16" y2="12" stroke="currentColor" stroke-width="1.5"/>
              <line x1="8" y1="16" x2="12" y2="16" stroke="currentColor" stroke-width="1.5"/>
            </template>
            <template v-else-if="item.icon === 'globe'">
              <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.5"/>
              <ellipse cx="12" cy="12" rx="4" ry="9" stroke="currentColor" stroke-width="1.5"/>
              <line x1="3" y1="12" x2="21" y2="12" stroke="currentColor" stroke-width="1.5"/>
              <path d="M3 6h18M3 18h18" stroke="currentColor" stroke-width="1.5"/>
            </template>
            <template v-else-if="item.icon === 'box'">
              <rect x="4" y="6" width="16" height="14" rx="2" stroke="currentColor" stroke-width="1.5"/>
              <path d="M4 10h16M12 10v10" stroke="currentColor" stroke-width="1.5"/>
              <path d="M8 6V4a4 4 0 0 1 8 0v2" stroke="currentColor" stroke-width="1.5"/>
            </template>
            <template v-else-if="item.icon === 'assembly'">
              <rect x="3" y="8" width="8" height="8" rx="1" stroke="currentColor" stroke-width="1.5"/>
              <rect x="13" y="8" width="8" height="8" rx="1" stroke="currentColor" stroke-width="1.5"/>
              <path d="M7 12h10M12 8v4" stroke="currentColor" stroke-width="1.5"/>
            </template>
            <template v-else-if="item.icon === 'pack'">
              <rect x="3" y="8" width="18" height="13" rx="2" stroke="currentColor" stroke-width="1.5"/>
              <path d="M3 12h18" stroke="currentColor" stroke-width="1.5"/>
              <path d="M10 3l2 5h-4l2-5z" stroke="currentColor" stroke-width="1.5"/>
              <line x1="8" y1="5" x2="8" y2="8" stroke="currentColor" stroke-width="1.5"/>
              <line x1="16" y1="5" x2="16" y2="8" stroke="currentColor" stroke-width="1.5"/>
            </template>
            <template v-else-if="item.icon === 'check'">
              <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.5"/>
              <path d="M8 12l3 3 5-6" stroke="currentColor" stroke-width="1.5"/>
            </template>
          </svg>
          <div class="stat-details">
            <div class="stat-title">{{ item.title }}</div>
            <div class="stat-value">{{ item.value }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 原因统计 -->
    <div class="section-header">
      <h3 class="section-title">原因统计</h3>
    </div>
    <div class="reason-stats">
      <div
        v-for="(reason, index) in reasonItems"
        :key="index"
        class="reason-item"
      >
        <div class="reason-title">{{ reason.title }}</div>
        <div class="reason-content">
          <span class="reason-total">{{ reason.total }}</span>
          <span class="reason-separator">/</span>
          <span class="reason-completed">{{ reason.completed }}</span>
        </div>
      </div>
    </div>

    <!-- 订单分析图表 -->
    <div class="section-header">
      <h3 class="section-title">订单分析</h3>
    </div>
    <div class="charts">
      <div ref="pieChart" class="chart">
        <h4 class="chart-title">订单分布</h4>
      </div>
      <div ref="barChart" class="chart">
        <h4 class="chart-title">订单趋势</h4>
      </div>
    </div>

    <!-- 完成率与交货地址 -->
    <div class="section-header">
      <h3 class="section-title">完成率与交货地址</h3>
    </div>
    <div class="new-charts">
      <div ref="orderCompletionChart" class="chart">
        <h4 class="chart-title">订单完成率</h4>
      </div>
      <div class="chart-container">
        <div class="delivery-table">
          <h4 class="table-title">本月交货地址</h4>
          <div class="address-count">共 {{ translatedAddresses.length }} 个地址</div>
          <div class="table-wrapper">
            <table class="address-table">
              <thead>
                <tr>
                  <th class="index-column">#</th>
                  <th class="address-column">地址（中文）</th>
                  <th class="address-column">地址（English）</th>
                  <th class="qty-column">销量</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="(item, index) in translatedAddresses" 
                  :key="index"
                  class="address-row"
                  :class="{ 'has-translation': item.hasTranslation }"
                >
                  <td class="index-cell">{{ index + 1 }}</td>
                  <td class="address-cell original">{{ item.original }}</td>
                  <td class="address-cell translated">
                    {{ item.hasTranslation ? item.translated : '无翻译' }}
                  </td>
                  <td class="qty-cell">{{ formatNumber(item.qty) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script>
import Layout from '@/components/Layout.vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { translateAddresses } from '@/utils/translator.js'

export default {
  components: {
    Layout
  },
  data() {
    return {
      isLoadingOrders: false,
      showUserDropdown: false,
      expandedStates: new Map(),
      activeNav: '/home',
      arrowDown: require('../photo/down.png'),
      arrowUp: require('../photo/up.png'),
      orderItems: [
        {
          title: '本月订单数量/订单批号数量',
          value: '0/0',
          path: '',
          icon: 'order'
        },
        {
          title: '本月产品销往国家总数',
          value: '0',
          path: '',
          icon: 'globe'
        },
        {
          title: '本月订单总只数',
          value: '0',
          path: '',
          icon: 'box'
        },
        {
          title: '本月装嵌已完成数量/只',
          value: '0',
          path: '',
          icon: 'assembly'
        },
        {
          title: '本月包装已完成数量/只',
          value: '0',
          path: '',
          icon: 'pack'
        },
        {
          title: '本月已落货数量/只',
          value: '0',
          path: '',
          icon: 'check'
        },
        {
          title: '下月订单数量/订单批号数量',
          value: '0/0',
          path: '',
          icon: 'order'
        },
        {
          title: '下月产品销往国家总数',
          value: '0',
          path: '',
          icon: 'globe'
        },
        {
          title: '下月订单总只数',
          value: '0',
          path: '',
          icon: 'box'
        },
        {
          title: '下月装嵌已完成数量/只',
          value: '0',
          path: '',
          icon: 'assembly'
        },
        {
          title: '下月包装已完成数量/只',
          value: '0',
          path: '',
          icon: 'pack'
        },
        {
          title: '下月已落货数量/只',
          value: '0',
          path: '',
          icon: 'check'
        },
      ],
      // 用于存储单独的订单数据，便于合并显示
      orderData: {
        totalOrders: '0',
        batchCount: '0'
      },
      // 用于存储下个月订单数据
      nextOrderData: {
        totalOrders: '0',
        batchCount: '0'
      },
      pieData: [],
      barData: [],
      pieInstance: null,
      barInstance: null,
      // 新增数据
      orderCompletionData: [],
      deliveryAddresses: [],
      orderCompletionInstance: null,
      // 翻译相关数据
      translatedAddresses: [],
      // 4个原因数据
      reasonItems: [
        { title: '客人原因：多少数量從上月改到這個月/已完成了多少', total: '0', completed: '0' },
        { title: '客人原因：多少數量從當月改到下個月及以后/已完成了多少', total: '0', completed: '0' },
        { title: '我們原因：多少數量從上月改到這個月/已完成了多少', total: '0', completed: '0' },
        { title: '我們原因：多少數量從上月改到下個月及以后/已完成了多少', total: '0', completed: '0' }
      ]
    }
  },
  mounted() {
    this.$nextTick(async () => {
      this.isLoadingOrders = true
      try {
        await Promise.allSettled([
          this.fetchDashboard(),
          this.fetchNextMonthDashboard(),
          this.fetchFinishedQty()
        ])
      } finally {
        this.isLoadingOrders = false
      }
      // 其他数据异步加载，不阻塞订单统计的loading
      this.fetchOrderCompletion()
      this.fetchDeliveryAddresses()
      this.fetchOrderChangeReasons()
    })
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
    this.disposeCharts()
  },
  methods: {
    navigateTo(path) {
      if (path) {
        this.$router.push(path)
      }
    },
    formatNumber(num) {
      const n = Number(num || 0)
      return n.toLocaleString()
    },
    async fetchDashboard() {
      try {
        const res = await axios.get('/api/home/dashboard')
        const data = (res && res.data && res.data.data) ? res.data.data : null
        if (!data) return

        this.orderCompletionData[1] = 
        {
          "name": "进行中",
          "value": data.monthly_order_count
        }  || {}
        
        // 存储订单批号数量
        this.orderData.batchCount = this.formatNumber(data.monthly_order_count)
        
        // 更新卡片数值
        this.orderItems[1].value = this.formatNumber(data.country_count)
        this.orderItems[2].value = this.formatNumber(data.monthly_total_qty)
        this.orderItems[5].value = this.formatNumber(data.monthly_completed_qty)
        
        // 更新合并后的订单显示
        this.updateMergedOrderDisplay()

        // 图表数据
        this.pieData = data.pie || []
        this.barData = data.category_bar || []
        this.renderCharts()
      } catch (e) {
        // 可根据需要提示
        // console.error(e)
      }
    },
    renderCharts() {
      this.$nextTick(() => {
        // 饼图
        if (!this.pieInstance && this.$refs.pieChart) {
          this.pieInstance = echarts.init(this.$refs.pieChart)
        }
        if (this.pieInstance) {
          const pieOption = {
            color: ['#DBEAFE', '#003A6B', '#005B9F', '#007CD4', '#3D9EF9', '#7ABEFD', '#B8DFFF'],
            title: { 
              text: '本月完成情况', 
              left: 'center',
              textStyle: { fontSize: 16, fontWeight: 'bold' }
            },
            tooltip: { trigger: 'item' },
            legend: { 
              bottom: 10,
              itemWidth: 14,
              itemHeight: 14
            },
            series: [
              {
                name: '只数',
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
                label: { show: true, formatter: '{b}: {c}' },
                data: this.pieData
              }
            ]
          }
          this.pieInstance.setOption(pieOption, true)
        }

        // 柱状图
        if (!this.barInstance && this.$refs.barChart) {
          this.barInstance = echarts.init(this.$refs.barChart)
        }
        if (this.barInstance) {
          const categories = this.barData.map(i => i.category)
          const values = this.barData.map(i => i.qty)
          const barOption = {
            title: { 
              text: '本月锁类分区只数', 
              left: 'center',
              textStyle: { fontSize: 16, fontWeight: 'bold' }
            },
            tooltip: { trigger: 'axis' },
            grid: { left: 80, right: 20, bottom: 60, top: 50 },
            xAxis: {
              type: 'category',
              data: categories,
              axisLabel: { rotate: 30, fontSize: 12 }
            },
            yAxis: {
              type: 'value',
              axisLabel: {
                formatter: value => echarts.format.addCommas(value),
                fontSize: 12
              }
            },
            series: [
              {
                name: '只数',
                type: 'bar',
                data: values,
                itemStyle: { 
                  color: '#003A6B',
                  borderRadius: [4, 4, 0, 0]
                },
                emphasis: {
                  itemStyle: {
                    color: '#408FFF'
                  }
                },
                barWidth: '40%'
              }
            ]
          }
          this.barInstance.setOption(barOption, true)
        }
      })
    },
    async fetchOrderCompletion() {
      try {
        const res = await axios.get('/api/home/order-completion')
        const data = (res && res.data && res.data.data) ? res.data.data : null
        if (!data) return
        this.orderCompletionData[0] = 
        {
          "name": "已完成",
          "value": data.completed_orders
        }  || {}
        
        // 存储订单总数量
        this.orderData.totalOrders = this.formatNumber(data.total_orders)
        
        // 更新合并后的订单显示
        this.updateMergedOrderDisplay()
        
        this.renderOrderCompletionChart()
      } catch (e) {
        console.error('获取订单完成情况失败:', e)
      }
    },
    async fetchDeliveryAddresses() {
      try {
        const res = await axios.get('/api/home/delivery-address-sales')
        const data = (res && res.data && res.data.data) ? res.data.data : null
        if (!data) return
        
        this.deliveryAddresses = data.addresses || []
        // 翻译地址
        this.translatedAddresses = translateAddresses(this.deliveryAddresses)
      } catch (e) {
        console.error('获取交货地址失败:', e)
      }
    },
    // 更新合并后的订单显示
    updateMergedOrderDisplay() {
      this.orderItems[0].value = `${this.orderData.totalOrders}/${this.orderData.batchCount}`
      this.orderItems[6].value = `${this.nextOrderData.totalOrders}/${this.nextOrderData.batchCount}`
    },
    
    // 获取下个月数据
    async fetchNextMonthDashboard() {
      try {
        const res = await axios.get('/api/home/next-month-dashboard')
        const data = (res && res.data && res.data.data) ? res.data.data : null
        if (!data) return
        
        // 存储下个月订单数据
        this.nextOrderData.totalOrders = this.formatNumber(data.next_month_total_orders)
        this.nextOrderData.batchCount = this.formatNumber(data.next_month_batch_count)
        
        // 更新下个月卡片数值
        this.orderItems[7].value = this.formatNumber(data.next_month_country_count)
        this.orderItems[8].value = this.formatNumber(data.next_month_total_qty)
        this.orderItems[9].value = this.formatNumber(data.next_month_assembly_qty)
        this.orderItems[10].value = this.formatNumber(data.next_month_packaging_qty)
        this.orderItems[11].value = this.formatNumber(data.next_month_shipped_qty)
        
        // 更新合并后的订单显示
        this.updateMergedOrderDisplay()
      } catch (e) {
        console.error('获取下个月数据失败:', e)
      }
    },

    renderOrderCompletionChart() {
      this.$nextTick(() => {
        if (!this.orderCompletionInstance && this.$refs.orderCompletionChart) {
          this.orderCompletionInstance = echarts.init(this.$refs.orderCompletionChart)
        }
        if (this.orderCompletionInstance) {
          const option = {
            title: { 
              text: '本月订单完成情况', 
              left: 'center',
              textStyle: {
                fontSize: 16,
                fontWeight: 'bold',
              },
            },
            tooltip: { 
              trigger: 'item',
              formatter: '{b}: {c} ({d}%)'
            },
            legend: { 
              bottom: 5,
              itemWidth: 14,
              itemHeight: 14
            },
            series: [
              {
                name: '订单情况',
                type: 'pie',
                radius: ['50%', '65%'],
                center: ['50%', '50%'],
                avoidLabelOverlap: false,
                itemStyle: { 
                  borderRadius: 8, 
                  borderColor: '#fff', 
                  borderWidth: 3 
                },
                label: { 
                  show: true, 
                  formatter: '{b}\n{c}',
                  fontSize: 12,
                  position: 'outside'
                },
                labelLine: {
                  show: true
                },
                data: this.orderCompletionData.map(item => ({
                  ...item,
                  itemStyle: {
                    color: item.name === '已完成' ? '#003A6B' : '#DBEAFE'
                  }
                }))
              }
            ]
          }
          this.orderCompletionInstance.setOption(option, true)
        }
      })
    },
    handleResize() {
      this.$nextTick(() => {
        if (this.pieInstance) {
          this.pieInstance.resize()
        }
        if (this.barInstance) {
          this.barInstance.resize()
        }
        if (this.orderCompletionInstance) {
          this.orderCompletionInstance.resize()
        }
      })
    },
    disposeCharts() {
      if (this.pieInstance) {
        this.pieInstance.dispose()
        this.pieInstance = null
      }
      if (this.barInstance) {
        this.barInstance.dispose()
        this.barInstance = null
      }
      if (this.orderCompletionInstance) {
        this.orderCompletionInstance.dispose()
        this.orderCompletionInstance = null
      }
    },
    
    // 获取完成数量数据
    async fetchFinishedQty() {
      try {
        const res = await axios.get('/finished_qty')
        const data = (res && res.data && res.data.data) ? res.data.data : null
        if (!data) return
        
        // 更新装嵌和包装完成数量
        this.orderItems[3].value = this.formatNumber(data['本月装嵌完成数量'])
        this.orderItems[4].value = this.formatNumber(data['本月包装完成数量'])
        this.orderItems[9].value = this.formatNumber(data['下月装嵌完成数量'])
        this.orderItems[10].value = this.formatNumber(data['下月包装完成数量'])
      } catch (e) {
        console.error('获取完成数量数据失败:', e)
      }
    },
    
    // 获取订单交期修改原因数据
    async fetchOrderChangeReasons() {
      try {
        const res = await axios.get('/api/home/order-change-reasons')
        const data = (res && res.data && res.data.data) ? res.data.data : null
        if (!data || !Array.isArray(data)) return
        
        // 根据统计类型更新对应的 reasonItems
        data.forEach(item => {
          const type = item['统计类型']
          const total = this.formatNumber(item['订单数量总和'])
          const completed = this.formatNumber(item['装嵌完成数量总和'])
          
          if (type === '客人原因-上月改当月') {
            this.reasonItems[0].total = total
            this.reasonItems[0].completed = completed
          } else if (type === '客人原因-当月改下月') {
            this.reasonItems[1].total = total
            this.reasonItems[1].completed = completed
          } else if (type === '工厂原因-上月改当月') {
            this.reasonItems[2].total = total
            this.reasonItems[2].completed = completed
          } else if (type === '工厂原因-当月改下月') {
            this.reasonItems[3].total = total
            this.reasonItems[3].completed = completed
          }
        })
      } catch (e) {
        console.error('获取订单交期修改原因数据失败:', e)
      }
    }
  },
}
</script>

<style scoped>
/* ==================== 页面整体布局 ==================== */
.home-container {
  padding: 16px 20px;
  background: #f4f6f9; /* 更浅更高级的灰蓝底 */
  min-height: calc(100vh - 60px);
}

/* ==================== 区块标题 ==================== */
.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  padding-left: 10px;
  border-left: 4px solid #005B9F;
  border-radius: 2px;
  height: 16px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #1f2d3d;
  margin: 0;
  line-height: 1;
}

/* ==================== 订单统计区（本月/下月分开） ==================== */
.order-section {
  margin-bottom: 16px;
}

.order-stats {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
  width: 100%;
  box-sizing: border-box;
}

.stat-item {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.04);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  padding: 14px 12px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.stat-item:hover {
  transform: translateY(-2px);
  border-color: rgba(0, 91, 159, 0.2);
  box-shadow: 0 8px 24px rgba(0, 91, 159, 0.08);
}

.stat-icon {
  width: 32px;
  height: 32px;
  margin-right: 12px;
  flex-shrink: 0;
  color: #005B9F;
  fill: none;
  opacity: 0.9;
}

.stat-details {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.stat-title {
  color: #909399;
  font-size: 11px;
  font-weight: 500;
  line-height: 1.3;
  word-wrap: break-word;
  margin-bottom: 2px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #1f2d3d;
  line-height: 1.2;
  word-wrap: break-word;
}

/* ==================== 原因统计区 ==================== */
.reason-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
  width: 100%;
  box-sizing: border-box;
}

.reason-item {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.04);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  padding: 12px 16px;
  transition: all 0.3s ease;
}

.reason-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 91, 159, 0.08);
  border-color: rgba(0, 91, 159, 0.2);
}

.reason-title {
  color: #909399;
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 8px;
  line-height: 1.4;
}

.reason-content {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 6px;
}

.reason-total {
  color: #303133;
  font-size: 20px;
  font-weight: 700;
}

.reason-separator {
  color: #c0c4cc;
  font-size: 16px;
  font-weight: 400;
}

.reason-completed {
  color: #005B9F;
  font-size: 22px;
  font-weight: 700;
}

/* ==================== 图表区域 ==================== */
.charts {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 16px;
  width: 100%;
}

.chart {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.04);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  padding: 16px;
  height: 350px;
  box-sizing: border-box;
  overflow: hidden;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: #1f2d3d;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f2f5;
}

/* ==================== 新图表和交货地址 ==================== */
.new-charts {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  width: 100%;
}

.chart-container {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.04);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  padding: 16px;
  height: 350px;
  box-sizing: border-box;
  overflow: hidden;
}

/* ==================== 交货地址表格 ==================== */
.delivery-table {
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  background: #ffffff;
}

.table-title {
  font-size: 13px;
  font-weight: 600;
  color: #1f2d3d;
  margin: 0 0 6px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
  flex-shrink: 0;
}

.address-count {
  color: #909399;
  font-size: 12px;
  margin-bottom: 10px;
  flex-shrink: 0;
}

.table-wrapper {
  flex: 1;
  overflow: auto;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background: #ffffff;
}

.address-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  background: #ffffff;
}

.address-table thead {
  background: #ffffff;
  position: sticky;
  top: 0;
  z-index: 10;
}

.address-table th {
  padding: 10px 6px;
  text-align: left;
  font-weight: 600;
  color: #303133;
  border-bottom: 1px solid #ffffff;
  white-space: nowrap;
}

.index-column {
  width: 40px;
  text-align: center;
}

.address-column {
  width: calc((100% - 40px - 90px) / 2);
}

.qty-column {
  width: 90px;
  text-align: right;
}

.address-table tbody tr:hover {
  background-color: #ffffff;
}

.address-row.has-translation {
  background-color: #ffffff;
}

.address-row.has-translation:hover {
  background-color: #ffffff;
}

.address-table td {
  padding: 8px 6px;
  border-bottom: 1px solid #ebeef5;
  vertical-align: top;
  word-break: break-word;
  line-height: 1.4;
}

.qty-cell {
  text-align: right;
  color: #1f2d3d;
  font-weight: 600;
}

.index-cell {
  text-align: center;
  color: #909399;
  font-weight: 500;
}

.address-cell.original {
  color: #303133;
}

.address-cell.translated {
  color: #003A6B;
  font-weight: 500;
}

.address-row:not(.has-translation) .address-cell.translated {
  color: #c0c4cc;
}

/* 滚动条样式 */
.table-wrapper::-webkit-scrollbar {
  width: 4px;
  height: 4px;
}

.table-wrapper::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.table-wrapper::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

/* ==================== 响应式设计 ==================== */
@media (max-width: 1400px) {
  .order-stats {
    grid-template-columns: repeat(3, 1fr);
  }

  .reason-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1200px) {
  .charts,
  .new-charts {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .order-stats,
  .reason-stats {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .chart,
  .chart-container {
    height: 280px;
  }
}

/* 确保图表容器的尺寸正确 */
.chart > div,
.chart-container > div[ref] {
  width: 100% !important;
  height: 100% !important;
}
</style>
