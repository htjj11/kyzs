"""
科研助手后端 API 测试用例
运行方法：
    cd backend
    source .venv/bin/activate
    pytest tests/test_api.py -v

说明：
- 需要先启动 MySQL 并导入 kyzs.sql
- 不需要启动服务，使用 FastAPI TestClient 直接测试
- 涉及外部 API（AI/AnythingLLM/OilLink）的接口会跳过，标记为 skip
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ──────────────────────────────────────────────
# 测试用常量
# ──────────────────────────────────────────────
TEST_USER_ID = 1
TEST_USERNAME = "admin"
TEST_PASSWORD = "Xxzx@123"

created_label_id = None
created_prompt_id = None
created_review_id = None
created_knowledge_id = None
created_word_id = None


# ──────────────────────────────────────────────
# 基础
# ──────────────────────────────────────────────
class TestRoot:
    def test_root(self):
        res = client.get("/")
        assert res.status_code == 200
        assert res.json()["message"] == "欢迎使用科研助手后端！"


# ──────────────────────────────────────────────
# 登录
# ──────────────────────────────────────────────
class TestAuth:
    def test_login_success(self):
        res = client.post("/system/login", json={"username": TEST_USERNAME, "password": TEST_PASSWORD})
        assert res.status_code == 200
        data = res.json()
        assert data["code"] == 200
        assert data["data"]["user_name"] == TEST_USERNAME

    def test_login_wrong_password(self):
        res = client.post("/system/login", json={"username": TEST_USERNAME, "password": "wrongpass"})
        assert res.status_code == 200
        assert res.json()["code"] == 400

    def test_login_wrong_user(self):
        res = client.post("/system/login", json={"username": "nobody", "password": "xxx"})
        assert res.status_code == 200
        assert res.json()["code"] == 400


# ──────────────────────────────────────────────
# 标签管理
# ──────────────────────────────────────────────
class TestLabel:
    def test_get_all_label(self):
        res = client.post("/get_setting/get_all_label", json={"user_id": TEST_USER_ID})
        assert res.status_code == 200
        assert res.json()["code"] == 200

    def test_get_label(self):
        res = client.post("/get_setting/get_label", json={"user_id": TEST_USER_ID})
        assert res.status_code == 200
        assert res.json()["code"] == 200

    def test_add_label(self):
        global created_label_id
        res = client.post("/get_setting/add_label", json={"user_id": TEST_USER_ID, "label_name": "测试标签_pytest"})
        assert res.status_code == 200
        assert res.json()["code"] == 200

        # 取刚创建的标签 id
        labels = client.post("/get_setting/get_all_label", json={"user_id": TEST_USER_ID}).json()["data"]
        for label in labels:
            if label["label_name"] == "测试标签_pytest":
                created_label_id = label["id"]
                break
        assert created_label_id is not None

    def test_delete_label(self):
        assert created_label_id is not None, "需先运行 test_add_label"
        res = client.post("/get_setting/delete_label", json={"id": created_label_id})
        assert res.status_code == 200
        assert res.json()["code"] == 200


# ──────────────────────────────────────────────
# 提示词管理
# ──────────────────────────────────────────────
class TestPrompt:
    def test_get_all_prompt(self):
        res = client.post("/get_setting/get_all_prompt", json={"user_id": TEST_USER_ID})
        assert res.status_code == 200
        assert res.json()["code"] == 200

    def test_get_all_prompt_type(self):
        res = client.post("/get_setting/get_all_prompt_type", json={"user_id": TEST_USER_ID})
        assert res.status_code == 200
        assert res.json()["code"] == 200

    def test_add_prompt(self):
        global created_prompt_id
        res = client.post("/get_setting/add_prompt", json={
            "user_id": TEST_USER_ID, "name": "测试提示词_pytest",
            "text": "这是一个测试提示词", "type": 1
        })
        assert res.status_code == 200
        assert res.json()["code"] == 200

        prompts = client.post("/get_setting/get_all_prompt", json={"user_id": TEST_USER_ID}).json()["data"]
        for p in prompts:
            if p["name"] == "测试提示词_pytest":
                created_prompt_id = p["id"]
                break
        assert created_prompt_id is not None

    def test_update_prompt(self):
        assert created_prompt_id is not None, "需先运行 test_add_prompt"
        res = client.post("/get_setting/update_prompt", json={
            "id": created_prompt_id, "name": "测试提示词_pytest_updated",
            "text": "更新后的提示词", "type": 1
        })
        assert res.status_code == 200
        assert res.json()["code"] == 200

    def test_delete_prompt(self):
        assert created_prompt_id is not None, "需先运行 test_add_prompt"
        res = client.post("/get_setting/delete_prompt", json={"id": created_prompt_id})
        assert res.status_code == 200
        assert res.json()["code"] == 200


# ──────────────────────────────────────────────
# 知识库管理
# ──────────────────────────────────────────────
class TestKnowledge:
    def test_get_all_knowledge(self):
        res = client.post("/get_knowledge/get_all_knowledge", json={"user_id": TEST_USER_ID})
        assert res.status_code == 200
        assert res.json()["code"] == 200

    def test_add_custom_knowledge(self):
        global created_knowledge_id
        res = client.post("/add_to_knowledge/add_knowledge", json={
            "data_dict": {"content_string": "这是一段测试内容", "title_string": "pytest测试知识"},
            "label_id": 1,
            "user_id": TEST_USER_ID,
            "type_id": 4
        })
        assert res.status_code == 200
        assert res.json()["code"] == 200

        knowledge = client.post("/get_knowledge/get_all_knowledge", json={"user_id": TEST_USER_ID}).json()["data"]
        for k in knowledge:
            if k["title"] == "pytest测试知识":
                created_knowledge_id = k["id"]
                break

    def test_update_knowledge(self):
        assert created_knowledge_id is not None, "需先运行 test_add_custom_knowledge"
        res = client.post("/get_knowledge/update_knoledge_by_id", json={
            "knowledge_id": created_knowledge_id,
            "knowledge_title": "pytest测试知识_updated",
            "knowledge_content": "更新后的内容",
            "knowledge_label": 1,
            "knowledge_type": 4,
            "knowledge_mark_info": "用户自定义"
        })
        assert res.status_code == 200
        assert res.json()["code"] == 200

    def test_delete_knowledge(self):
        assert created_knowledge_id is not None, "需先运行 test_add_custom_knowledge"
        res = client.post("/get_knowledge/delete_knoledge_by_id", json={"knowledge_id": created_knowledge_id})
        assert res.status_code == 200
        assert res.json()["code"] == 200


# ──────────────────────────────────────────────
# 综述报告管理
# ──────────────────────────────────────────────
class TestReview:
    def test_get_all_review(self):
        res = client.post("/get_review/get_all_review", json={"user_id": TEST_USER_ID})
        assert res.status_code == 200
        assert res.json()["code"] == 200

    def test_get_all_template(self):
        res = client.post("/get_review/get_all_template", json={"user_id": TEST_USER_ID})
        assert res.status_code == 200
        assert res.json()["code"] == 200

    def test_create_review(self):
        global created_review_id
        res = client.post("/get_review/create_review", json={
            "user_id": TEST_USER_ID, "title": "pytest测试综述"
        })
        assert res.status_code == 200
        assert res.json()["code"] == 200

        reviews = client.post("/get_review/get_all_review", json={"user_id": TEST_USER_ID}).json()["data"]
        for r in reviews:
            if r["title"] == "pytest测试综述":
                created_review_id = r["id"]
                break
        assert created_review_id is not None

    def test_modify_review_new(self):
        assert created_review_id is not None, "需先运行 test_create_review"
        res = client.post("/get_review/modify_review_new", json={
            "review_id": created_review_id,
            "review_body": "这是修改后的综述内容"
        })
        assert res.status_code == 200
        assert res.json()["code"] == 200

    def test_modify_review(self):
        assert created_review_id is not None, "需先运行 test_create_review"
        res = client.post("/get_review/modify_review", json={
            "review_id": created_review_id,
            "start_position": 0,
            "end_position": 4,
            "replaced_text": "替换后"
        })
        assert res.status_code == 200
        assert res.json()["code"] == 200

    def test_delete_review(self):
        assert created_review_id is not None, "需先运行 test_create_review"
        res = client.post("/get_review/delete_review", json={"review_id": created_review_id})
        assert res.status_code == 200
        assert res.json()["code"] == 200

    def test_delete_summary(self):
        # 先创建一条
        client.post("/get_review/create_review", json={"user_id": TEST_USER_ID, "title": "pytest删除测试"})
        reviews = client.post("/get_review/get_all_review", json={"user_id": TEST_USER_ID}).json()["data"]
        target_id = next((r["id"] for r in reviews if r["title"] == "pytest删除测试"), None)
        if target_id:
            res = client.post("/delete_summary", json={"id": target_id, "user_id": str(TEST_USER_ID)})
            assert res.status_code == 200
            assert res.json()["code"] == 200


# ──────────────────────────────────────────────
# 翻译词汇管理
# ──────────────────────────────────────────────
class TestTranslateWord:
    def test_get_translate_word(self):
        res = client.post("/translate/get_translate_word_by_content", json={"content1": "drill"})
        assert res.status_code == 200
        assert res.json()["code"] in [200, 404]

    def test_add_translate_word(self):
        global created_word_id
        res = client.post("/translate/add_translate_word", json={
            "ts_type": "en", "field_id": 1,
            "content1": "pytest_test_word", "content2": "测试词汇",
            "content3": "用于pytest测试的词汇", "from_source": "pytest"
        })
        assert res.status_code == 200
        assert res.json()["code"] == 200
        created_word_id = res.json()["data"]["id"]

    def test_update_translate_word(self):
        assert created_word_id is not None, "需先运行 test_add_translate_word"
        res = client.post("/translate/update_translate_word", json={
            "word_id": created_word_id, "content3": "更新后的解释"
        })
        assert res.status_code == 200
        assert res.json()["code"] == 200

    def test_delete_translate_word(self):
        assert created_word_id is not None, "需先运行 test_add_translate_word"
        res = client.post("/translate/delete_translate_word", json={"word_id": created_word_id})
        assert res.status_code == 200
        assert res.json()["code"] == 200


# ──────────────────────────────────────────────
# 需要 API Key 但可本地测试的接口
# ──────────────────────────────────────────────
class TestWithApiKey:
    def test_translate_keyword(self):
        """关键词翻译：中文关键词 → 调用 DeepSeek 翻译"""
        res = client.post("/get_from_oilink/translate_keyword", json={"keyword": "钻井技术"})
        assert res.status_code == 200
        data = res.json()
        assert data["code"] == 200
        assert data["data"] is not None

    def test_get_online_infomation(self):
        """讯飞联网搜索：返回结构化互联网信息"""
        res = client.post("/get_from_oilink/get_online_infomation", json={"keyword": "钻井机器人最新进展"})
        assert res.status_code == 200
        data = res.json()
        assert data["code"] == 200

    def test_get_online_infomation_summary(self):
        """讯飞联网摘要：与 get_online_infomation 同源"""
        res = client.post("/get_from_oilink/get_online_infomation_summary", json={"online_infomation": "页岩气开采技术"})
        assert res.status_code == 200
        assert res.json()["code"] == 200

    def test_generate_content_by_ai(self):
        """AI 生成内容：传入知识内容和提示词，调用 DeepSeek 生成"""
        res = client.post("/get_knowledge/generate_content_by_ai", json={
            "knowledge_content": "钻井技术是石油工程的核心，包括定向井、水平井等工艺。",
            "prompt": "用一句话总结这段内容的核心要点"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["code"] == 200
        assert data["data"] is not None


# ──────────────────────────────────────────────
# 翻译文档列表（只查数据库，无需外部服务）
# ──────────────────────────────────────────────
class TestTranslateDoc:
    def test_get_all_translate_doc_list(self):
        res = client.post("/translate/get_all_translate_doc_list", json={"user_id": TEST_USER_ID})
        assert res.status_code == 200
        data = res.json()
        assert "translate_doc_list" in data


# ──────────────────────────────────────────────
# LLM 知识库（只查数据库，无需 AnythingLLM）
# ──────────────────────────────────────────────
class TestAnythingDB:
    def test_get_all_anything_db(self):
        res = client.post("/llm/get_all_anything_db", json={"user_id": TEST_USER_ID})
        assert res.status_code == 200
        assert res.json()["code"] == 200

    def test_get_public_anything_db(self):
        res = client.post("/llm/get_public_anything_db", json={"user_id": TEST_USER_ID})
        assert res.status_code == 200
        assert res.json()["code"] == 200

    def test_get_all_folders(self):
        res = client.post("/llm/get_all_folders", json={"user_id": TEST_USER_ID})
        assert res.status_code == 200
        assert res.json()["code"] == 200

    def test_get_anything_db_by_id_not_found(self):
        res = client.post("/llm/get_anything_db_by_id", json={"id": 999999})
        assert res.status_code == 200
        assert res.json()["code"] == 500

    def test_get_anything_db_by_id_found(self):
        """如果数据库有数据则验证返回结构"""
        all_res = client.post("/llm/get_all_anything_db", json={"user_id": TEST_USER_ID}).json()
        items = all_res.get("data", [])
        if not items:
            pytest.skip("anything_db 表暂无数据，跳过")
        first_id = items[0]["id"]
        res = client.post("/llm/get_anything_db_by_id", json={"id": first_id})
        assert res.status_code == 200
        assert res.json()["code"] == 200
        assert "text_title" in res.json()["data"]


# ──────────────────────────────────────────────
# 外部依赖接口（跳过，需手动测试）
# ──────────────────────────────────────────────
class TestExternal:
    @pytest.mark.skip(reason="需要 OilLink 外网访问")
    def test_get_articles(self):
        res = client.post("/get_from_oilink/get_articles", json={
            "keywords_list": ["钻井"], "page": 1, "size": 5, "user_id": TEST_USER_ID
        })
        assert res.status_code == 200

    @pytest.mark.skip(reason="需要 OilLink 外网访问")
    def test_get_patent(self):
        res = client.post("/get_from_oilink/get_patent", json={
            "query": "钻井机器人", "page": 0, "size": 5
        })
        assert res.status_code == 200

    @pytest.mark.skip(reason="需要讯飞 API Key")
    def test_get_online_information(self):
        res = client.post("/get_from_oilink/get_online_infomation", json={"keyword": "钻井技术"})
        assert res.status_code == 200

    @pytest.mark.skip(reason="需要 SiliconFlow API Key 和知识库数据")
    def test_get_summary_by_ai(self):
        res = client.post("/get_review/get_summary_by_ai", json={
            "knowledge_ids": [1], "prompt_ids": [1], "user_need": "生成一段综述"
        })
        assert res.status_code == 200

    @pytest.mark.skip(reason="需要 AnythingLLM 本地服务")
    def test_stream_chat(self):
        res = client.post("/llm/stream_chat", json={"message": "你好"})
        assert res.status_code == 200

    @pytest.mark.skip(reason="需要万方内网访问 (10.68.16.2)")
    def test_get_article_from_wanfang(self):
        res = client.post("/get_from_oilink/get_article_from_wanfang", json={
            "Keywords": ["钻井"], "StartRecord": 1, "MaximumRecords": 5
        })
        assert res.status_code == 200
