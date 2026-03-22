<template>
    <div class="count-setting-container">
        <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-position="top">
            <el-form-item label="原密码" prop="oldPassword">
                <el-input v-model="passwordForm.oldPassword" type="password" show-password placeholder="请输入当前密码" />
            </el-form-item>

            <el-form-item label="新密码" prop="newPassword">
                <el-input v-model="passwordForm.newPassword" type="password" show-password placeholder="请输入新密码" />
            </el-form-item>

            <el-form-item label="确认新密码" prop="confirmPassword">
                <el-input v-model="passwordForm.confirmPassword" type="password" show-password placeholder="请再次输入新密码" />
            </el-form-item>

            <div class="form-actions">
                <el-button type="primary" :loading="isSubmitting" @click="handleUpdatePassword" class="submit-btn">
                    确认修改密码
                </el-button>
            </div>
        </el-form>
    </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'
import { getUserIdFromCookie } from '@/utils/authUtils'

const passwordFormRef = ref(null)
const isSubmitting = ref(false)

const passwordForm = reactive({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
    if (value === '') {
        callback(new Error('请再次输入新密码'))
    } else if (value !== passwordForm.newPassword) {
        callback(new Error('两次输入密码不一致!'))
    } else {
        callback()
    }
}

const passwordRules = {
    oldPassword: [
        { required: true, message: '请输入原密码', trigger: 'blur' }
    ],
    newPassword: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
    ],
    confirmPassword: [
        { required: true, validator: validateConfirmPassword, trigger: 'blur' }
    ]
}

const handleUpdatePassword = async () => {
    if (!passwordFormRef.value) return

    try {
        await passwordFormRef.value.validate()

        isSubmitting.value = true
        const userId = getUserIdFromCookie()

        const response = await request.post('/get_setting/change_password', {
            user_id: userId,
            old_password: passwordForm.oldPassword,
            new_password: passwordForm.newPassword
        })

        if (response.data && response.data.code === 200) {
            ElMessage.success('密码修改成功')
            passwordFormRef.value.resetFields()
        } else {
            ElMessage.error(response.data?.msg || '密码修改失败')
        }
    } catch (error) {
        console.error('修改密码错误:', error)
        ElMessage.error('修改密码失败，请检查网络或原密码')
    } finally {
        isSubmitting.value = false
    }
}
</script>

<style scoped>
.count-setting-container {
    padding: 10px 20px;
}

.submit-btn {
    width: 100%;
    margin-top: 10px;
    border-radius: 0;
    height: 40px;
    font-weight: 600;
}

:deep(.el-input__wrapper) {
    border-radius: 0;
}

.form-actions {
    margin-top: 24px;
}
</style>
