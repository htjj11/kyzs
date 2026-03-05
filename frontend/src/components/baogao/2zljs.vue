<script setup>
import { ref, onMounted } from 'vue';
import * as textUtils from '@/utils/textUtils';
import { ElTable, ElTableColumn, ElInput, ElButton, ElDialog,ElMessage } from 'element-plus';
import axios from "@/api/request.js";
import { getUserIdFromCookie } from '@/utils/authUtils.js';



// 状态定义
const searchKeyword = ref('');
const patentData = ref([]);
const loading = ref(false);
const dialogVisible = ref(false);
const collectedPatentBoxVisible = ref(false);
const currentPatent = ref(null);
// 分页相关
const currentPage = ref(0); // 起始页码设为0

const tagDialogVisible = ref(false);
const selectedTag = ref('');
const userTags = ref([]);
const currentCollectRow = ref(null);

// 搜索专利
const searchPatents = async () => {
  if (!searchKeyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词');
    return;
  }

  try {
    loading.value = true;
    console.log('搜索页码:', currentPage.value);
    const response = await axios.post('/get_from_oilink/get_patent', {
     query: searchKeyword.value.trim() ,
     page: currentPage.value,
     size: 10
    });
    
    const responseData = response.data;
    // 处理API返回的数据结构
    // 从API响应中提取专利数据。假设响应数据结构为 response.data.data，
    // 取其第一个元素作为专利数据。若数据不存在或为空，则将 patentData 设置为空数组。
    patentData.value = responseData['data'] ;
    console.log('查询专利数据：',patentData.value);

  } catch (error) {
    ElMessage.error('搜索失败: ' + (error.message || '未知错误'));
    console.error('Error searching patents:', error);
  } finally {
    loading.value = false;
  }
};

// 查看专利详情
const viewPatentDetail = (patent) => {
  currentPatent.value = { ...patent };
  dialogVisible.value = true;
};

// 上一页
const prevPage = () => {
  if (currentPage.value > 0) {
    currentPage.value--;
    searchPatents();
  } else {
    ElMessage.info('已经是第一页');
  }
};

// 下一页
const nextPage = () => {
  currentPage.value++;
  searchPatents();
};


// 显示收藏标签选择对话框
const showTagDialog = async (row) => {
  currentCollectRow.value = row;
  selectedTag.value = '';
  
  try {
    // 获取用户标签
    const response = await axios.post('/get_setting/get_all_label', {
    });
    
    if (response.data.code === 200) {
      userTags.value = response.data.data || [];
      tagDialogVisible.value = true;
    } else {
      ElMessage.error(response.data.msg || '获取标签失败');
    }
  } catch (error) {
    ElMessage.error('网络错误，请稍后重试');
    console.error('获取标签失败:', error);
  }
};

// 确认添加收藏
const confirmCollect = () => {
  if (!selectedTag.value) {
    ElMessage.warning('请选择标签');
    return;
  }
  
  axios.post('/add_to_knowledge/add_knowledge', {
    data_dict: currentCollectRow.value,
    type_id: 2,
    label_id: selectedTag.value
  }).then(res => {
    console.log('增加收藏接口返回：', res.data);
    if (res.data['code'] == 200) {
      ElMessage.success('收藏成功');
      currentCollectRow.value.is_collected = 1;
      tagDialogVisible.value = false;
    } else {
      ElMessage.error(res.data.msg || '收藏失败');
    }
  }).catch(error => {
    ElMessage.error('网络错误，请稍后重试');
    console.error('API请求错误:', error);
  });
};

</script>

<template>
  <div class="patent-search-container">
    <h1>专利检索</h1>
    <!-- 搜索区域 -->
    <div class="search-section">
      <el-input
        v-model="searchKeyword"
        placeholder="请输入关键词搜索专利"
        style="width: 500px; margin-right: 10px;"
        clearable
        @keyup.enter="searchPatents"
      />
      <el-button type="primary" @click="searchPatents">
        <i class="el-icon-search"></i> 查询
      </el-button>

      <el-dialog
        title="我的收藏"
        v-model="collectedPatentBoxVisible"
        width="80%"
        :close-on-click-modal="true"
      >
        <collected_patents_box />
        <!-- 移除无用内容 123 -->
        <template #footer class="dialog-footer">
          <el-button @click="collectedPatentBoxVisible = false">取 消</el-button>
        </template>
      </el-dialog>
    </div>

    <!-- 专利表格 -->
    <!-- {{ patentData }} -->
    <el-table
      v-loading="loading"
      :data="patentData"
      style="width: 100%; margin-top: 20px;"
      border
    >
      <el-table-column label="专利标题" width="800" >
        <template #default="{ row }">
          <a href="javascript:void(0)" @click="viewPatentDetail(row)" style="color: #409eff; cursor: pointer;">
            {{ textUtils.formatTitle(row.title) }}
          </a>
        </template>
      </el-table-column>
      <el-table-column prop="country" label="国家" width="80">
        <template #default="{ row }">
          {{ textUtils.formatCountry(row.country) }}
        </template>
      </el-table-column>
      <el-table-column prop="app_date" label="申请日" width="120">
        <template #default="{ row }">
          {{row.app_date }}
        </template>
      </el-table-column>

      <el-table-column label="摘要" width="400">
        <template #default="{ row }">
            {{ textUtils.formatAbstract(row.abstract) }}    
        </template>
      </el-table-column>

      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <template v-if="row.is_collected === 0">
            <el-button 
              type="text" 
              @click="() => {
                row.is_collected = 1;
                showTagDialog(row); 
              }"
            >
              添加收藏
            </el-button>
          </template>
          <template v-else>
            已收藏
          </template>
        </template>
      </el-table-column>
      
    
    </el-table>
    
    <!-- 页码选择器 -->
    <div class="pagination-controls" style="margin-top: 20px; display: flex; justify-content: center; align-items: center;">
      <el-button 
        @click="prevPage" 
        type="primary" 
        :disabled="currentPage === 0"
        style="margin-right: 10px;"
      >
        上一页
      </el-button>
      <span style="margin: 0 15px; font-size: 16px;">
        当前页码: {{ currentPage + 1 }}
      </span>
      <el-button 
        @click="nextPage" 
        type="primary"
      >
        下一页
      </el-button>
    </div>

    <!-- 专利详情弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      title="专利详情"
      :width="'85%'"
      :fullscreen="false"
    >
      <div class="patent-detail" v-if="currentPatent">
        <div class="detail-row">
          <div class="detail-label">申请号:</div>
          <div class="detail-value">{{ currentPatent.app_num }}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">申请日:</div>
          <div class="detail-value">{{ currentPatent.app_date }}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">公开号:</div>
          <div class="detail-value">{{ currentPatent.pub_num || '未公开' }}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">公开日:</div>
          <div class="detail-value">{{ currentPatent.pub_date }}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">专利名称:</div>
          <div class="detail-value">{{ textUtils.formatTitle(currentPatent.title) }}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">申请人:</div>
          <div class="detail-value">{{ textUtils.formatApplicants(currentPatent.applicant) }}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">发明人:</div>
          <div class="detail-value" style="white-space: pre-wrap;">
            {{ textUtils.formatInventors(currentPatent.inventor) }}
          </div>
        </div>
        <div class="detail-row">
          <div class="detail-label">IPC分类号:</div>
          <div class="detail-value" style="white-space: pre-wrap;">{{ textUtils.formatIPC(currentPatent.ipc) }}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">摘要:</div>
          <div class="detail-value" style="white-space: pre-wrap;">
            {{ textUtils.formatMultiParagraphAbstract(currentPatent.abstract) }}
          </div>
        </div>
        <div class="detail-row">
          <div class="detail-label">权利要求:</div>
          <div class="detail-value" style="white-space: pre-wrap;">
            {{ textUtils.formatClaims(currentPatent.claims) }}  
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 收藏标签选择对话框 -->
    <ElDialog
      title="选择标签"
      v-model="tagDialogVisible"
      width="400px"
      :close-on-click-modal="false"
    >
      <div style="margin-bottom: 20px;">
        <ElSelect
          v-model="selectedTag"
          placeholder="请选择标签"
          style="width: 100%;"
        >
          <ElOption
            v-for="tag in userTags"
            :key="tag.id"
            :label="tag.label_name"
            :value="tag.id"
          />
        </ElSelect>
      </div>
      <template #footer>
        <ElButton @click="cancelTagSelection">取消</ElButton>
        <ElButton type="primary" @click="confirmCollect">确认收藏</ElButton>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.patent-search-container {
  padding: 20px;
}

.search-section {
  margin: 20px 0;
  display: flex;
  align-items: center;
}

.result-stats {
  color: #606266;
  margin-bottom: 10px;
}

.no-data {
  text-align: center;
  padding: 50px 0;
  color: #909399;
}

.title-cell, .applicant-cell, .inventor-cell, .ipc-cell {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.patent-detail {
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 10px;
}

.detail-row {
  display: flex;
  margin-bottom: 16px;
}

.detail-label {
  width: 120px;
  font-weight: bold;
  color: #606266;
  flex-shrink: 0;
}

.detail-value {
  flex-grow: 1;
  color: #303133;
}

.abstract-content,
.claims-content {
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.claims-content div {
  margin-bottom: 8px;
}
</style>
