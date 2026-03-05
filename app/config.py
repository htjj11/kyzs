from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
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

    # SiliconFlow / DeepSeek
    siliconflow_api_key: str = ""

    # 讯飞星火
    xunfei_api_key: str = ""

    # 重庆聚合文献
    juhe_token: str = ""

    # AnythingLLM
    anythingllm_base_url: str = "http://localhost:3001"
    anythingllm_api_key: str = ""
    anythingllm_workspace: str = "kyzs"


settings = Settings()
