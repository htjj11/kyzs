# 文档翻译接口使用说明

## 接口概述
本模块提供了与文档翻译服务对接的API接口，包括文档上传、翻译进度查询功能。
## 接口地址
http://data.oillink.com/api/shengli/deep_translate
## 接口列表

### 1. 文档上传
- **接口名称**: upload
- **请求方式**: POST
- **接口路径**: http://data.oillink.com/api/shengli/deep_translate/upload
- **请求参数**:
  - file: 需要翻译的文档文件
  - targetLanguage: 目标语言代码(默认ZH)
出参列表：
参数名称	参数说明	参数类型
document_id	文档ID	Int
返回结果:
{
	"code": "success",
	"msg": {
		"code": 1,
		"info": "提交成功",
		"data": {
			"document_id": "3264"
		}
	},
	"time": "1750731683",
	"data": 200
}

### 2. 翻译进度查询
- **接口名称**: progress
- **请求方式**: GET
- **接口路径**: http://data.oillink.com/api/shengli/deep_translate/progress?document_id=DOCUMENT_ID
- **请求参数**:
  - document_id: 翻译任务ID
- 出参列表：

参数名称	参数说明	参数类型
status	状态（-1：翻译失败，0:正在翻译中，1:翻译成功）	String
download_url	下载链接	String
返回结果:
{
	"code": "success",
	"msg": {
		"code": 1,
		"info": "获取进度成功",
		"data": {
			"status": 1,
			"download_url": "https://codeai-document.oss-cn-hongkong.aliyuncs.com/document/168/3264.pdf"
		}
	},
	"time": "1750731788",
	"data": 200
}

### 3. 文本翻译
- **接口名称**: translate
- **请求方式**: POST
- **接口路径**: http://data.oillink.com/api/shengli/deep_translate/translate
- **请求参数**:
  - text: 需要翻译的文本
  - source_lang: 源语言代码(默认auto，中文：zh，英文：en)
  - target_lang: 目标语言代码(中文：zh，英文：en)
返回结果:
{
	"code": 1,
	"msg": "翻译成功",
	"data":"翻译后的文本"	
}
或
{
	"code": 0,
	"msg": "翻译失败",
	"data":"错误信息"
}
