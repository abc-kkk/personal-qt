<template>
  <div class="daily-funds-container">
    <div class="page-header">
      <h2><el-icon><DataLine /></el-icon> 资金曲线</h2>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon> 新增资金记录
      </el-button>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-container">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          ></el-date-picker>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchDailyFunds">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 资金曲线图表 -->
    <el-card shadow="hover" class="chart-card">
      <div v-loading="loading">
        <div class="chart-header">
          <h3>总资金曲线</h3>
          <div class="chart-actions">
            <el-select v-model="chartPeriod" placeholder="选择时间范围" style="width: 120px;">
              <el-option label="最近一周" value="7"></el-option>
              <el-option label="最近一月" value="30"></el-option>
              <el-option label="最近三月" value="90"></el-option>
              <el-option label="最近半年" value="180"></el-option>
              <el-option label="最近一年" value="365"></el-option>
            </el-select>
          </div>
        </div>
        <div id="fund-chart" style="width: 100%; height: 400px;"></div>
      </div>
    </el-card>

    <!-- 资金记录列表 -->
    <el-card shadow="hover" class="fund-records-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>总资金记录列表</span>
        </div>
      </template>
      <el-table :data="dailyFunds" style="width: 100%" v-loading="loading" border stripe>
        <el-table-column prop="fund_date" label="日期" width="150">
          <template #default="scope">
            {{ formatDate(scope.row.fund_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="总资金" width="200">
          <template #default="scope">
            {{ formatMoney(scope.row.total_amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="250"></el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" @click="openDialog(scope.row)">
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-popconfirm title="确定删除该记录吗？" @confirm="deleteDailyFund(scope.row.id)">
              <template #reference>
                <el-button size="small" type="danger">
                  <el-icon><Delete /></el-icon> 删除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 表单对话框 -->
    <el-dialog
      :title="isEdit ? '编辑总资金记录' : '新增总资金记录'"
      v-model="dialogVisible"
      width="600px"
    >
      <el-form :model="form" :rules="rules" ref="dailyFundForm" label-width="120px">
        <el-form-item label="日期" prop="fund_date">
          <el-date-picker
            v-model="form.fund_date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="总资金" prop="total_amount">
          <el-input-number
            v-model="form.total_amount"
            :precision="2"
            :step="1000"
            :min="0"
            style="width: 200px;"
          ></el-input-number>
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="form.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
            style="width: 100%;"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { DataLine, Plus, Edit, Delete } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '@/api'

/**
 * 每日资金组件
 * 
 * @description 管理每日资金记录，显示资金曲线图表
 */
export default {
  name: 'DailyFunds',
  components: {
    DataLine,
    Plus,
    Edit,
    Delete
  },
  setup() {
    // 状态
    const dailyFunds = ref([])
    const loading = ref(false)
    const dialogVisible = ref(false)
    const isEdit = ref(false)
    const dailyFundForm = ref(null)
    const chartInstance = ref(null)
    const chartPeriod = ref('30') // 默认显示最近30天
    
    // 筛选表单
    const filterForm = reactive({
      dateRange: []
    })
    
    // 编辑表单
    const form = reactive({
      id: '',
      fund_date: '',
      total_amount: null,
      notes: ''
    })
    
    // 表单验证规则
    const rules = {
      fund_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
      total_amount: [{ required: true, message: '请输入总资金', trigger: 'blur' }]
    }

    /**
     * 获取每日资金列表
     */
    const fetchDailyFunds = async () => {
      loading.value = true
      try {
        let params = {}
        
        if (filterForm.dateRange && filterForm.dateRange.length === 2) {
          params.start_date = filterForm.dateRange[0]
          params.end_date = filterForm.dateRange[1]
        }
        
        console.log('请求参数:', params)
        
        const response = await api.get('/daily-funds/', { params })
        console.log('API响应:', response.data)
        dailyFunds.value = response.data || []
        // 对数据按日期进行倒序排序
        dailyFunds.value.sort((a, b) => {
          return new Date(b.fund_date) - new Date(a.fund_date)
        })
        initChart()
      } catch (error) {
        console.error('获取资金列表失败:', error)
        if (error.response) {
          console.error('错误状态:', error.response.status)
          console.error('错误数据:', error.response.data)
        }
        ElMessage.error('获取资金记录列表失败')
      } finally {
        loading.value = false
      }
    }

    /**
     * 测试API连接
     */
    const testApiConnection = async () => {
      try {
        console.log('测试API连接...')
        const response = await api.get('/health')
        console.log('API健康状态:', response.data)
        ElMessage.success(`API连接成功: ${JSON.stringify(response.data)}`)
        return true
      } catch (error) {
        console.error('API连接测试失败:', error)
        ElMessage.error('API连接失败，请检查后端服务是否正常运行')
        return false
      }
    }

    /**
     * 获取最近N天的资金记录
     */
    const fetchRecentDailyFunds = async () => {
      loading.value = true
      try {
        // 先测试API连接
        const connectionOk = await testApiConnection()
        if (!connectionOk) {
          loading.value = false
          return
        }
        
        console.log(`获取最近${chartPeriod.value}天的资金记录`)
        const response = await api.get(`/daily-funds/recent?days=${chartPeriod.value}`)
        console.log('API响应:', response.data)
        dailyFunds.value = response.data || []
        // 对数据按日期进行倒序排序
        dailyFunds.value.sort((a, b) => {
          return new Date(b.fund_date) - new Date(a.fund_date)
        })
        initChart()
      } catch (error) {
        console.error('获取资金记录列表失败:', error)
        if (error.response) {
          console.error('错误状态:', error.response.status)
          console.error('错误数据:', error.response.data)
        }
        ElMessage.error('获取资金记录列表失败')
      } finally {
        loading.value = false
      }
    }

    /**
     * 初始化图表
     */
    const initChart = () => {
      try {
        // 如果没有数据，显示空数据提示
        if (!dailyFunds.value || dailyFunds.value.length === 0) {
          if (chartInstance.value) {
            chartInstance.value.dispose();
            chartInstance.value = null;
          }
          
          const chartDom = document.getElementById('fund-chart');
          if (!chartDom) {
            console.warn('找不到图表DOM元素');
            return;
          }
          
          chartInstance.value = echarts.init(chartDom);
          chartInstance.value.setOption({
            title: {
              text: '暂无总资金数据',
              left: 'center',
              top: 'center',
              textStyle: {
                fontSize: 20,
                color: '#999'
              }
            }
          });
          return;
        }
        
        // 确保DOM元素存在
        const chartDom = document.getElementById('fund-chart');
        if (!chartDom) {
          console.warn('找不到图表DOM元素');
          return;
        }
        
        // 如果已存在实例，先销毁
        if (chartInstance.value) {
          chartInstance.value.dispose();
        }
        
        // 初始化新实例
        chartInstance.value = echarts.init(chartDom);
        
        // 为图表创建一个新的数据副本并按日期升序排序
        const chartData = [...dailyFunds.value].sort((a, b) => {
          return new Date(a.fund_date) - new Date(b.fund_date);
        });
        
        // 准备数据
        const dates = chartData.map(item => formatDate(item.fund_date));
        const totalAmounts = chartData.map(item => Number(item.total_amount));
        
        // 设置选项
        const option = {
          tooltip: {
            trigger: 'axis',
            formatter: function(params) {
              let result = params[0].name + '<br/>';
              const colorSpan = `<span style="display:inline-block;margin-right:5px;border-radius:50%;width:10px;height:10px;background-color:${params[0].color};"></span>`;
              result += `${colorSpan}总资金: ${formatMoney(params[0].value)}<br/>`;
              return result;
            }
          },
          legend: {
            data: ['总资金']
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
          },
          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: dates
          },
          yAxis: [
            {
              type: 'value',
              name: '金额',
              axisLabel: {
                formatter: '{value} 元'
              }
            }
          ],
          series: [
            {
              name: '总资金',
              type: 'line',
              smooth: true,
              data: totalAmounts,
              itemStyle: {
                color: '#409EFF'
              },
              lineStyle: {
                width: 3
              },
              symbolSize: 8,
              areaStyle: {
                color: {
                  type: 'linear',
                  x: 0,
                  y: 0,
                  x2: 0,
                  y2: 1,
                  colorStops: [
                    { offset: 0, color: 'rgba(64, 158, 255, 0.5)' },
                    { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
                  ]
                }
              }
            }
          ]
        };
        
        // 设置图表
        chartInstance.value.setOption(option);
        
        // 响应窗口大小变化
        window.addEventListener('resize', () => {
          if (chartInstance.value) {
            chartInstance.value.resize();
          }
        });
      } catch (error) {
        console.error('初始化图表出错:', error);
        ElMessage.error('初始化图表失败，请刷新页面重试');
      }
    }

    /**
     * 打开对话框
     * @param {Object} item - 要编辑的资金记录
     */
    const openDialog = (item) => {
      resetForm()
      if (item) {
        isEdit.value = true
        form.id = item.id
        form.fund_date = formatDate(item.fund_date)
        form.total_amount = Number(item.total_amount)
        form.notes = item.notes || ''
      } else {
        isEdit.value = false
        form.fund_date = formatDate(new Date())
      }
      dialogVisible.value = true
    }

    /**
     * 重置表单
     */
    const resetForm = () => {
      form.id = ''
      form.fund_date = ''
      form.total_amount = null
      form.notes = ''
      
      if (dailyFundForm.value) {
        dailyFundForm.value.resetFields()
      }
    }

    /**
     * 重置筛选条件
     */
    const resetFilter = () => {
      filterForm.dateRange = []
      fetchDailyFunds()
    }

    /**
     * 提交表单
     */
    const submitForm = async () => {
      if (!dailyFundForm.value) return
      
      await dailyFundForm.value.validate(async (valid) => {
        if (valid) {
          try {
            const data = {
              fund_date: form.fund_date,
              total_amount: form.total_amount,
              notes: form.notes
            }
            
            if (isEdit.value) {
              await api.put(`/daily-funds/${form.id}`, data)
              ElMessage.success('更新资金记录成功')
            } else {
              await api.post('/daily-funds/', data)
              ElMessage.success('创建资金记录成功')
            }
            
            dialogVisible.value = false
            fetchDailyFunds()
          } catch (error) {
            ElMessage.error(isEdit.value ? '更新资金记录失败' : '创建资金记录失败')
            console.error(error)
          }
        }
      })
    }

    /**
     * 删除资金记录
     * @param {string} id - 资金记录ID
     */
    const deleteDailyFund = async (id) => {
      try {
        await api.delete(`/daily-funds/${id}`)
        ElMessage.success('删除资金记录成功')
        fetchDailyFunds()
      } catch (error) {
        ElMessage.error('删除资金记录失败')
        console.error(error)
      }
    }

    /**
     * 格式化日期
     * @param {string} dateString - 日期字符串
     * @returns {string} 格式化后的日期字符串
     */
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    }

    /**
     * 格式化金额
     * @param {number} value - 金额数值
     * @returns {string} 格式化后的金额字符串
     */
    const formatMoney = (value) => {
      if (value === null || value === undefined) return '-'
      return Number(value).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' 元'
    }

    // 监听图表周期变化
    watch(chartPeriod, () => {
      fetchRecentDailyFunds()
    })

    // 在组件卸载时释放资源
    onUnmounted(() => {
      if (chartInstance.value) {
        chartInstance.value.dispose();
        chartInstance.value = null;
      }
      window.removeEventListener('resize', () => {});
    });

    onMounted(() => {
      // 延迟执行，确保DOM已渲染
      setTimeout(() => {
        fetchRecentDailyFunds();
      }, 100);
    });

    return {
      dailyFunds,
      loading,
      dialogVisible,
      isEdit,
      form,
      rules,
      dailyFundForm,
      filterForm,
      chartPeriod,
      formatDate,
      formatMoney,
      fetchDailyFunds,
      resetFilter,
      openDialog,
      submitForm,
      deleteDailyFund
    }
  }
}
</script>

<style scoped>
.daily-funds-container {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.page-header h2 {
  margin: 0;
  font-size: 22px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-header h2 .el-icon {
  font-size: 24px;
  color: #409eff;
}

.filter-container {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.chart-card {
  margin-bottom: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}

.profit {
  color: #f56c6c;
}

.loss {
  color: #67c23a;
}

/* 响应式调整 */
@media screen and (max-width: 768px) {
  .filter-form {
    display: flex;
    flex-direction: column;
  }
  
  .filter-form .el-form-item {
    margin-right: 0;
  }
}
</style> 