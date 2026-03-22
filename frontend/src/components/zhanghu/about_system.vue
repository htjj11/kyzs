<template>
    <div class="about-container">
        <div class="about-header">
            <div class="system-logo">
                <el-icon :size="40" color="#409eff">
                    <InfoFilled />
                </el-icon>
            </div>
            <div class="system-main-info">
                <h2 class="system-name">科研助手系统</h2>
                <div class="system-version">当前版本：<el-tag size="small" effect="dark">v1.2.5</el-tag></div>
            </div>
        </div>

        <el-divider>更新日志</el-divider>

        <div class="log-container">
            <el-timeline>
                <el-timeline-item timestamp="2026-03-22" placement="top" type="primary">
                    <el-card class="log-card">
                        <h4>v1.2.5 稳定性与功能增强</h4>
                        <ul>
                            <li>优化了公共知识库的目录树加载逻辑。</li>
                            <li>新增文档搜索结果弹窗展示，优化交互体验。</li>
                            <li>重构了文档详情页布局。</li>
                            <li>增强了系统侧边栏的用户中心功能。</li>
                        </ul>
                    </el-card>
                </el-timeline-item>
                <el-timeline-item timestamp="2026-03-15" placement="top">
                    <el-card class="log-card">
                        <h4>v1.1.0 核心模块升级</h4>
                        <ul>
                            <li>优化界面。</li>

                        </ul>
                    </el-card>
                </el-timeline-item>
            </el-timeline>
        </div>

        <div class="about-footer">
            <div class="copyright">AI生成内容仅供参考</div>
            <div class="support">技术支持：舒新阳15733233837</div>
        </div>
    </div>
</template>

<script setup>
import { InfoFilled } from '@element-plus/icons-vue'
</script>

<style scoped>
.about-container {
    padding: 10px 20px;
}

.about-header {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 20px;
}

.system-name {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
    color: #303133;
}

.system-version {
    margin-top: 8px;
    font-size: 13px;
    color: #909399;
}

.log-container {
    max-height: 350px;
    overflow-y: auto;
    padding-right: 10px;
}

.log-card h4 {
    margin: 0 0 10px 0;
    font-size: 14px;
    color: #303133;
}

.log-card ul {
    margin: 0;
    padding-left: 18px;
    font-size: 13px;
    color: #606266;
    line-height: 1.8;
}

.about-footer {
    margin-top: 30px;
    text-align: center;
    border-top: 1px solid #ebeef5;
    padding-top: 20px;
    color: #909399;
    font-size: 12px;
}

.copyright {
    margin-bottom: 5px;
}

/* 隐藏滚动条但保留功能 */
.log-container::-webkit-scrollbar {
    width: 6px;
}

.log-container::-webkit-scrollbar-thumb {
    background: #e4e7ed;
    border-radius: 3px;
}
</style>
