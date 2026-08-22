<template>
  <div class="page-container">
    <div class="header-actions">
      <div class="header-left">
        <h2>投喂记录管理</h2>
        <el-input
          v-model="query_params.search"
          placeholder="搜索批次号/饲料名称"
          clearable
          class="search-input"
          :prefix-icon="Search"
        />
      </div>
      <div class="header-right" v-if="user_store.userInfo?.role === 'farmer'">
        <el-button 
          class="btn-standard btn-add"
          :disabled="!user_store.userInfo?.profile?.is_verified"
          @click="handle_add"
        >
          <el-icon><Plus /></el-icon>新增投喂
        </el-button>
      </div>
    </div>

    <el-card class="standard-card table-card" :body-style="{ padding: '0' }">
      <div class="mobile-list">
        <div v-for="item in feeding_list" :key="item.id" class="mobile-card">
          <div class="mobile-card-header">
            <el-tag size="small" effect="plain">
              <span v-html="highlight_text(item.batch_code, query_params.search)"></span>
            </el-tag>
            <span class="date">{{ format_date(item.feeding_time) }}</span>
          </div>
          <div class="mobile-card-content">
            <div class="info-item" v-if="user_store.userInfo?.role === 'admin'">
              <span class="label">养殖户：</span>
              <span class="value">{{ item.farmer_name || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">消耗饲料：</span>
              <span class="value" v-html="highlight_text(item.feed_name, query_params.search)"></span>
            </div>
            <div class="info-item">
              <span class="label">投喂重量：</span>
              <span class="value highlight">{{ item.feed_weight }} kg</span>
            </div>
            <div class="info-item" v-if="item.remark">
              <span class="label">备注：</span>
              <span class="value">{{ item.remark }}</span>
            </div>
          </div>
          <div class="mobile-card-footer table-ops">
            <el-button class="btn-action-delete" link v-if="user_store.userInfo?.profile?.is_verified" @click="handle_delete(item.id, '确定要删除这条投喂记录吗？')">删除</el-button>
          </div>
        </div>
        <el-empty v-if="!feeding_list.length" description="暂无投喂记录" />
      </div>

    <div class="pagination-container">
      <el-pagination
        v-model:current-page="query_params.page"
        :page-size="query_params.page_size"
        layout="total, prev, pager, next"
        :total="total"
        @current-change="handle_page_change"
        background
        size="small"
      />
    </div>
    </el-card>

    <!-- 新增投喂弹窗 -->
    <el-dialog
      v-model="dialog_visible"
      title="新增投喂记录"
      width="500px"
      class="standard-dialog"
      destroy-on-close
    >
      <el-form :model="form" :rules="rules" ref="form_ref" label-width="100px" label-position="top">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="选择批次" prop="batch">
              <el-select v-model="form.batch" placeholder="请选择牲畜批次" style="width: 100%" filterable>
                <el-option
                    v-for="item in batch_list"
                    :key="item.id"
                    :label="item.batch_code"
                    :value="item.id"
                  />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="选择饲料" prop="feed">
              <el-select v-model="form.feed" placeholder="请选择饲料" style="width: 100%" filterable>
                <el-option
                  v-for="item in feed_list"
                  :key="item.id"
                  :label="`${item.feed_name} (库存: ${item.stock_quantity}${item.unit})`"
                  :value="item.id"
                  :disabled="item.stock_quantity <= 0"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="投喂重量 (kg)" prop="feed_weight">
              <el-input-number 
                v-model="form.feed_weight" 
                :min="0.1" 
                :precision="2" 
                style="width: 100%" 
                controls-position="right"
              />
              <div class="form-tip">提交后将自动扣减对应饲料库存</div>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注说明" prop="remark">
              <el-input 
                v-model="form.remark" 
                type="textarea" 
                :rows="3" 
                placeholder="请输入相关的补充说明信息" 
                resize="none"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialog_visible = false">取 消</el-button>
          <el-button class="btn-add" @click="submit_form" :loading="submit_loading">确 定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
/**
 * 文件功能：投喂记录管理页面
 */
import { ref, onMounted, reactive } from 'vue'
import { useUserStore } from '@/store/user'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import { useCRUD } from '@/hooks/useCRUD'
import { Plus, Search } from '@element-plus/icons-vue'

const user_store = useUserStore()

// 使用通用 CRUD Hook
const {
  list: feeding_list,
  total,
  query_params,
  get_list,
  handle_page_change,
  handle_delete,
  highlight_text,
  format_date_time: format_date
} = useCRUD({
  api_url: '/api/production/feeding/',
  refresh_signals: ['feedingrecord'],
  delete_msg: '(注意：删除记录将自动恢复对应饲料库存)'
})

const batch_list = ref<any[]>([])
const feed_list = ref<any[]>([])

// 仅「养殖中」批次可投喂（已出栏不应出现在下拉框；与后端校验一致）
const get_batches = async () => {
  try {
    const res: any = await request.get('/api/livestock/batch/', {
      params: { status: 'active', page_size: 200 }
    })
    const raw = res?.results ?? res ?? []
    batch_list.value = Array.isArray(raw) ? raw : []
  } catch (error) {
    console.error(error)
  }
}

// 获取饲料列表
const get_feeds = async () => {
  try {
    const res: any = await request.get('/api/production/feed/')
    feed_list.value = res?.results || res || []
  } catch (error) {
    console.error(error)
  }
}

// 弹窗相关
const dialog_visible = ref(false)
const submit_loading = ref(false)
const form_ref = ref()
const form = reactive({
  batch: undefined,
  feed: undefined,
  feed_weight: 1.0,
  remark: ''
})

const rules = {
  batch: [{ required: true, message: '请选择批次', trigger: 'change' }],
  feed: [{ required: true, message: '请选择饲料', trigger: 'change' }],
  feed_weight: [{ required: true, message: '请输入重量', trigger: 'blur' }]
}

// 打开添加弹窗
const handle_add = () => {
  Object.assign(form, {
    batch: undefined,
    feed: undefined,
    feed_weight: 1.0,
    remark: ''
  })
  dialog_visible.value = true
}

// 提交表单
const submit_form = async () => {
  if (!form_ref.value) return
  try {
    const valid = await form_ref.value.validate()
    if (valid) {
      // 检查库存
      const selected_feed = feed_list.value.find((f: any) => f.id === form.feed) as any
      if (selected_feed && selected_feed.stock_quantity < form.feed_weight) {
        ElMessage.error(`饲料库存不足，当前库存: ${selected_feed.stock_quantity}kg`)
        return
      }

      submit_loading.value = true
      await request.post('/api/production/feeding/', { ...form })
      ElMessage.success('投喂记录已保存，库存已扣减')
      dialog_visible.value = false
      get_list()
      get_feeds() // 刷新库存
    }
  } catch (error: any) {
    // 验证失败或请求失败
    if (error === false) return // Element Plus 验证失败会返回 false
    console.error(error)
  } finally {
    submit_loading.value = false
  }
}

onMounted(() => {
  get_list()
  get_batches()
  get_feeds()
})
</script>

<style scoped>
.page-container {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.header-section {
  margin-bottom: 24px;
}

.header-title h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
  font-weight: 600;
}

.header-subtitle {
  color: #909399;
  font-size: 14px;
  margin-top: 4px;
  display: block;
}

.search-input {
  width: 280px;
}

.table-card {
  border-radius: 8px;
  overflow: hidden;
}

.feed-info, .time-info {
  display: flex;
  align-items: center;
  justify-content: center;
}

.weight-text {
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
}

.unit-text {
  font-size: 12px;
  color: #909399;
  margin-left: 2px;
}

.pagination-container {
  padding: 20px;
  display: flex;
  justify-content: flex-end;
  background: #fff;
}

/* 移动端卡片样式 */
.mobile-list {
  padding: 12px;
  background: #f5f7fa;
}

.mobile-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
}

.mobile-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f2f6fc;
}

.mobile-card-content .info-item {
  display: flex;
  margin-bottom: 8px;
  font-size: 14px;
}

.mobile-card-content .label {
  color: #909399;
  width: 80px;
  flex-shrink: 0;
}

.mobile-card-content .value {
  color: #303133;
}

.mobile-card-content .highlight {
  color: #409eff;
  font-weight: 600;
}

.form-tip {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
  line-height: 1.4;
}

.mb-4 { margin-bottom: 1rem; }
.mt-2 { margin-top: 0.5rem; }
.mr-1 { margin-right: 0.25rem; }

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }
  
  .header-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .search-input {
    width: 100% !important;
    margin-right: 0 !important;
    margin-bottom: 12px;
  }
}
</style>
