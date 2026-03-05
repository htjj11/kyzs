<template>
  <div class="patent-search-container">
    <!-- 搜索区域 -->
    <div class="search-section">
      <div class="search-form">
        <el-form :model="searchForm" label-width="80px" class="demo-ruleForm">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="关键词" prop="exp">
                <el-input 
                  v-model="searchForm.exp" 
                  placeholder="请输入搜索关键词"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="年份" prop="date">
                <el-input 
                  v-model.number="searchForm.date" 
                  placeholder="请输入年份"
                  type="number"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item>
                <el-button type="primary" @click="handleSearch">搜索</el-button>
                <el-button @click="resetForm">重置</el-button>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>
    </div>

    <!-- 搜索结果区域 -->
    <div class="result-section">
      <el-table 
        v-loading="loading" 
        :data="patentList" 
        style="width: 100%"
        border
      >
        <el-table-column prop="专利名称" label="专利标题" min-width="200" />
        <el-table-column prop="申请人" label="申请机构" min-width="150" />
        <el-table-column prop="发明人" label="发明人" min-width="120" />
        <el-table-column prop="申请日" label="申请日期" width="150" />
        <el-table-column prop="公开日" label="公开日期" width="150" />
        <el-table-column prop="申请号" label="申请号" min-width="150" />
        <el-table-column prop="公开号" label="公开号" min-width="150" />
        <el-table-column prop="IPC分类号" label="IPC分类号" min-width="180" />
        <el-table-column prop="摘要" label="摘要" min-width="300">
          <template #default="scope">
            <el-tooltip class="item" effect="dark" :content="scope.row['摘要']" placement="top">
              <div class="abstract-text">{{ scope.row['摘要'] }}</div>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="is_collected" label="收藏状态" width="100">
          <template #default="scope">
            <span v-if="scope.row.is_collected === 1" style="color: #67c23a">已收藏</span>
            <span v-else style="color: #909399">未收藏</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button 
              v-if="scope.row.is_collected === 0"
              type="primary" 
              size="small" 
              @click="handleAddToKnowledgeBase(scope.row)"
            >
              添加到知识库
            </el-button>
            <el-button 
              v-else
              type="success" 
              size="small" 
              disabled
            >
              已收藏
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="searchForm.page"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="sizes, prev, pager, next, jumper"
          :background="true"
          :total="computedTotal"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
  
  <!-- 标签选择弹窗组件 -->
  <GetLabelList
    v-model:visible="showLabelDialog"
    @select-label="handleLabelSelect"
  />
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import { ElMessage } from 'element-plus';
import request from '@/api/request';
import { getUserIdFromCookie } from '@/utils/authUtils';
import GetLabelList from '@/components/small/get_label_list.vue';

// 搜索表单数据
const searchForm = reactive({
  exp: '',
  date: null,
  page: 1
});

// 分页相关
const pageSize = ref(10);
const loading = ref(false);
const patentList = ref([]);
const total = ref(1000); // 默认值确保页码选择器显示

// 添加计算属性监控total的变化
const computedTotal = computed(() => {
  console.log('计算属性total的值:', total.value);
  return total.value;
});

// 标签选择弹窗控制
const showLabelDialog = ref(false);
const currentPatentRow = ref(null);

// 搜索函数
const handleSearch = async () => {
  if (!searchForm.exp) {
    ElMessage.warning('请输入搜索关键词');
    return;
  }
  
  loading.value = true;

  
  try {
    const user_id = getUserIdFromCookie() || 1; // 默认用户ID为1
    console.log('搜索参数:', { exp: [searchForm.exp], date: searchForm.date, page: searchForm.page, user_id });
    
    const response = await request.post('/get_from_oilink/get_patent_from_wanfang', {
      exp: [searchForm.exp],
      date: searchForm.date || null,
      page: searchForm.page,
      user_id
    });
    
    console.log('API响应数据:', response);
    console.log('响应中的data字段:', response.data);
    console.log('响应中的total_count:', response.data?.total_count);
    console.log('搜索前的total值:', total.value);
    
    if (response.data && response.data.code === 200) {
      patentList.value = response.data.data || [];
      console.log('专利列表数据长度:', patentList.value.length);
      
      // 检查total_count是否存在且有效
      if (response.data.total_count !== undefined) {
        console.log('获取到total_count:', response.data.total_count);
        // 无论total_count是否为0，都使用它
        total.value = Number(response.data.total_count);
      } else {
        console.log('未获取到total_count字段，保留当前值');
      }
      
      console.log('搜索后的total值:', total.value);
      
      // 检查返回的数据是否为空，如果为空且不是第一页，提示用户
      if (patentList.value.length === 0 && searchForm.page > 1) {
        ElMessage.info('当前页没有数据，请尝试查看前面的页面');
      }
    } else {
      console.log('API返回错误状态:', response.data?.code, response.data?.msg);
      ElMessage.error(response.data?.msg || '搜索失败');
    }
  } catch (error) {
    console.error('搜索专利失败:', error);
    ElMessage.error('搜索失败，请稍后重试');
  } finally {
    loading.value = false;
    console.log('搜索完成后的total值:', total.value);
  }
};

// 重置表单
const resetForm = () => {
  console.log('执行重置表单');
  searchForm.exp = '';
  searchForm.date = null;
  searchForm.page = 1;
  patentList.value = [];
  // 重置时保持一个较大的值，确保页码选择器显示
  total.value = 1000;
  console.log('重置后的total值:', total.value);
};

// 分页大小变化
const handleSizeChange = (size) => {
  console.log('分页大小变化:', size);
  pageSize.value = size;
  // 保持当前页码不变，直接搜索
  handleSearch();
};

// 页码变化
const handleCurrentChange = (current) => {
  console.log('页码变化:', current);
  searchForm.page = current;
  handleSearch();
};

// 添加到知识库
const handleAddToKnowledgeBase = (row) => {
  // 保存当前行数据
  currentPatentRow.value = row;
  // 显示标签选择弹窗
  showLabelDialog.value = true;
};

// 处理标签选择
const handleLabelSelect = async ({ label_id }) => {
  if (currentPatentRow.value && label_id) {
    // 转换日期格式的辅助函数
    const formatDateToISO = (dateStr) => {
      if (!dateStr) return '';
      // 如果日期是'YYYY-MM-DD'格式，转换为'YYYY-MM-DDTHH:MM:SS'格式
      if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
        return dateStr + 'T00:00:00';
      }
      return dateStr;
    };
    
    // 转换专利数据为英文键名字典，并命名为data_dict
    const data_dict = {
     title: currentPatentRow.value['专利名称'] || '',
      abstract: currentPatentRow.value['摘要'] || '',
      country: 'CN', // 假设默认为中国专利，可根据实际情况调整
      app_num: currentPatentRow.value['申请号'] || '',
      app_date: formatDateToISO(currentPatentRow.value['申请日']) || '',
      pub_num: currentPatentRow.value['公开号'] || '',
      pub_date: formatDateToISO(currentPatentRow.value['公开日']) || '',
      pub_kind: '', // 接口返回数据中未提供，暂时为空
      applicant: currentPatentRow.value['申请人'] || '',
      id  :currentPatentRow.value['公开号'] || '',
    };
    
    // 获取用户ID
    const user_id = getUserIdFromCookie() || 1;
    // 专利类型ID为2
    const type_id = 2;
    
    // 输出到log
    console.log('专利数据（英文键名）:', data_dict);
    console.log('选择的标签ID:', label_id);
    console.log('用户ID:', user_id);
    console.log('类型ID:', type_id);
    
    try {
      // 调用收藏接口
      const response = await request.post('/add_to_knowledge/add_knowledge', {
        data_dict,
        label_id,
        user_id,
        type_id
      });
      
      if (response.data && response.data.code === 200) {
        // 添加成功后更新状态
        currentPatentRow.value.is_collected = 1;
        ElMessage.success('已添加到知识库');
      } else {
        ElMessage.error(response.data?.msg || '添加到知识库失败');
      }
    } catch (error) {
      console.error('调用收藏接口失败:', error);
      ElMessage.error('添加失败，请稍后重试');
    }
  }
};
</script>

<style scoped>
.patent-search-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.search-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.search-form {
  max-width: 1200px;
}

.result-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.abstract-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-form-item) {
  margin-bottom: 0;
}
</style>