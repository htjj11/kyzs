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
                <el-timeline-item timestamp="2026-04-12" placement="top" type="success">
                    <el-card class="log-card">
                        <h4>v1.3.0 跨代升级：交互优化与核心能力跃升</h4>
                        <h5 style="margin-top: 10px; color: #409eff;">✨ 视觉与交互 (UI/UX) 改进</h5>
                        <ul>
                            <li>深度解决界面偏白板化审美疲劳，引入全新主题色、卡片物理阴影及界面降噪机制。</li>
                            <li>个人知识库重构成高密度列表展示模式。</li>
                            <li>对功能入口进行整合，将资料上传按钮收纳至个人知识库页面。</li>
                        </ul>
                        
                        <h5 style="margin-top: 10px; color: #409eff;">🧠 知识库及协同工作流扩容</h5>
                        <ul>
                            <li>实现个人知识库向公共知识库的一键无缝“转移”业务逻辑及视图体系。</li>
                            <li>添加公共知识库“重复检测”防火墙（基于 Hash 指纹精确防重传）。</li>
                            <li>内嵌 RAGFlow 技术栈，全面实现以公共知识库内容为基础的 RAG 智能检索问答功能。</li>
                            <li>应用复杂提示词工程，致使报告生成模块完美支持参考文献的自动排版引用。</li>
                        </ul>

                        <h5 style="margin-top: 10px; color: #409eff;">⚙️ 模型生态接入与策略配置</h5>
                        <ul>
                            <li>大幅拓展模型生态圈，成功接入“豆包”、“秘塔”等一流外部大模型服务 API。</li>
                            <li>实装并打通本地内部网络“长城大模型”与外网通用大模型的一键快速切换开关。</li>
                            <li>建立角色与控制体系，开发颗粒度达到功能级别（查看、上传、删除）的权限管理系统。</li>
                            <li>极限传输调优，上传大体量文件稳定性增强，最大文件限制提升至 200MB 级别。</li>
                        </ul>

                        <h5 style="margin-top: 10px; color: #409eff;">🔧 核心缺陷修复与链路闭环</h5>
                        <ul>
                            <li>完成针对 PDF 文件高频上传解析报错所做出的专项 Bug 修复计划。</li>
                            <li>将原有的纯文字文档模板器直接跃迁升级为现代富文本编辑器组件。</li>
                            <li>解决业务核心输出环节存在的 Word 文件导出/下载兼容性残损问题。</li>
                        </ul>
                    </el-card>
                </el-timeline-item>
                
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
