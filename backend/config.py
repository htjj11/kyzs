from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 优先读取同级 .env 文件；若字段在 .env 中未设置则使用下方默认值
    # extra="ignore" 表示 .env 中多余的变量不会报错
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 数据库
    sql_ip: str = "127.0.0.1"
    sql_port: int = 3306
    sql_user: str = "root"
    sql_password: str = ""
    sql_database: str = "kyzs"

    # SiliconFlow（DeepSeek-V3 推理服务）
    siliconflow_api_key: str = ""

    # 讯飞星火（用于联网搜索，格式：AppId:APISecret）
    xunfei_api_key: str = ""

    # 火山方舟豆包（联网搜索）：控制台 API Key + 推理接入点 ID（ep- 开头）
    doubao_ark_api_key: str = ""
    doubao_ark_model: str = ""
    doubao_ark_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"

    # 秘塔 AI 搜索（https://metaso.cn/search-api/api-keys）
    metaso_api_key: str = ""

    # 重庆聚合文献（内网文献检索服务）
    juhe_token: str = ""

    # AnythingLLM（本地 RAG 向量知识库，默认端口 3001）
    anythingllm_base_url: str = "http://localhost:3001"
    anythingllm_api_key: str = ""
    anythingllm_workspace: str = "kyzs"


# 全局单例，所有模块通过 from app.config import settings 使用
settings = Settings()
