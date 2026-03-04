# Pptapi 接口使用说明

## 简介

本文档提供了 `Pptapi` 的详细接口说明，用于生成和管理PPT。

## 基准 URL

所有API的基准URL为： `http://data.oillink.com/api/shengli/Pptapi/`

## 接口鉴权

创建 API Token 接口用于生成调用鉴权 Token，支持限制生成次数与数据隔离，通过 URL 拼接 Token 实现鉴权。

POST
http://data.oillink.com/api/shengli/Pptapi/createApiToken

请求 body

{
  // 用户ID（自定义用户ID，非必填，建议不超过32位字符串）
  // 第三方用户ID，不同uid创建的token数据会相互隔离，主要用于数据隔离
  "uid": null,
  // 限制 token 最大生成PPT次数（数字，为空则不限制，为0时不允许生成PPT，大于0时限制生成PPT次数）
  // UI iframe 接入时强烈建议传 limit 参数，避免 token 泄露照成损失！
  "limit": null,
  // 过期时间，单位：小时
  // 默认两小时过期，最大可设置为48小时
  "timeOfHours": 2
}

响应 body

{
  "data": {
    "token": "sk_xxx", // token (调用api接口鉴权用，请求头传token)
    "expireTime": 7200 // 过期时间（秒）
  },
  "code": 0,
  "message": "操作成功"
}

注意：该接口请在服务端调用，同一个 uid 创建 token 时，之前通过该 uid 创建的 token 会在 10 秒内过期


## 生成 PPT 相关接口

# 注意一下每个接口都要传递参数 apiToken，就是获取鉴权后的token。

### 创建任务
接口说明： 调用此接口可获得一个 任务 ID，即开启了一个生成 PPT 的任务，后续不管是生成大纲内容还是修改大纲内容都需要此任务 ID。

POST
http://data.oillink.com/api/shengli/Pptapi/createTask


multipart/form-data

参数	类型	是否必传	说明
type	1|2|3|4|5|6|7	是	类型：
1.智能生成（主题、要求）
2.上传文件生成
3.上传思维导图生成
4.通过 word 精准转 ppt
5.通过网页链接生成
6.粘贴文本内容生成
7.Markdown 大纲生成
content	String	否	内容：
type=1 用户输入主题或要求（不超过 1000 字符）
type=2、4 不传
type=3 幕布等分享链接
type=5 网页链接地址（http/https）
type=6 粘贴文本内容（不超过 20000 字符）
type=7 大纲内容（markdown）
file	File[]	否	文件列表（文件数不超过 5 个，总大小不超过 50M）：
type=1 上传参考文件（非必传，支持多个）
type=2 上传文件（支持多个）
type=3 上传思维导图（xmind/mm/md）（仅支持一个）
type=4 上传 word 文件（仅支持一个）
type=5、6、7 不传

支持格式：doc/docx/pdf/ppt/pptx/txt/md/xls/xlsx/csv/html/epub/mobi/xmind/mm
响应：

{
  "data": {
    "id": "xxx" // 任务ID
  },
  "code": 0,
  "message": "操作成功"
}

### 生成大纲内容
接口说明： 生成当前任务的大纲及内容

POST
http://data.oillink.com/api/shengli/Pptapi/generateContent


参数

{
  "id": "xxx", // 任务ID
  "stream": true, // 是否流式（默认 true）
  "length": "medium", // 篇幅长度：short/medium/long => 10-15页/20-30页/25-35页
  "scene": null, // 演示场景：通用场景、教学课件、工作总结、工作计划、项目汇报、解决方案、研究报告、会议材料、产品介绍、公司介绍、商业计划书、科普宣传、公众演讲 等任意场景类型。
  "audience": null, // 受众：大众、学生、老师、上级领导、下属、面试官、同事 等任意受众类型。
  "lang": null, // 语言: zh/zh-Hant/en/ja/ko/ar/de/fr/it/pt/es/ru
  "prompt": null // 用户要求（小于50字）
}

特别提醒

参数prompt只会在 创建的任务类型为 1 (智能生成), 2 (上传文件生成), 5 (通过网页链接生成), 6 (粘贴文本内容生成) 这些类型时生效，其他类型会忽略该字段

流式响应 event-stream

{ "text": "#", "status": 3 }

{ "text": " ", "status": 3 }

{ "text": "主题", "status": 3 }

...

{
	"text": "",
	"status": 4,
	"result": { // 最终markdown结构树
		"level": 1,
		"name": "主题",
		"children": [
			{
				"level": 2,
				"name": "章节",
				"children": [
					{
						"level": 3,
						"name": "页面标题",
						"children": [
							{
								"level": 4,
								"name": "内容标题",
								"children": [
									{
										"level": 0,
										"name": "内容"
									}
								]
							}
						]
					}
				]
			}
		]
	}
}

非流式响应（application/json）：

{
  "code": 0,
  "data": {
    "text": "# 主题\n## 章节\n### 页面标题\n#### 内容标题\n- 内容", // markdown 文本
    "result": {
      // markdown 结构树
      "level": 1,
      "name": "主题",
      "children": [
        {
          "level": 2,
          "name": "章节",
          "children": [
            {
              "level": 3,
              "name": "页面标题",
              "children": [
                {
                  "level": 4,
                  "name": "内容标题",
                  "children": [
                    {
                      "level": 0,
                      "name": "内容"
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  },
  "message": "ok"
}

### 修改大纲内容
接口说明： 根据用户指令（question）修改大纲内容。

POST
http://data.oillink.com/api/shengli/Pptapi/updateContent


参数

{
  "id": "xxx", // 任务ID
  "stream": true, // 是否流式（默认 true）
  "markdown": "# 主题\n## 章节\n### 页面标题\n#### 内容标题\n- 内容", // 大纲内容markdown
  "question": null // 用户修改建议
}

响应 event-stream 或 application/json，结构同生成大纲内容

### 生成 PPT
接口说明： 根据 markdown 格式的 PPT 大纲与内容生成 PPT 作品。

POST
http://data.oillink.com/api/shengli/Pptapi/generatePptx


参数

{
  "id": "xxx", // 任务ID
  "templateId": "xxx", // 模板ID（调用模板接口获取）
  "markdown": "# 主题\n## 章节\n### 页面标题\n#### 内容标题\n- 内容" // 大纲内容markdown
}

响应

{
  "code": 0,
  "data": {
    "pptInfo": {
      // ppt信息
      "id": "xxx", // ppt id
      "subject": "xxx", // 主题
      "coverUrl": "https://xxx.png", // 封面
      "templateId": "xxx", // 模板ID
      "pptxProperty": "xxx", // PPT数据结构（json gzip base64）
      "userId": "xxx", // 用户ID
      "userName": "xxx", // 用户名称
      "companyId": 1000,
      "updateTime": null,
      "createTime": "2024-01-01 10:00:00"
    }
  },
  "message": "操作成功"
}
### 获取模板过滤选项
接口说明： 获取查询模版的过滤选项

GET
http://data.oillink.com/api/shengli/Pptapi/getTemplateOptions

响应

{
  "data": {
    "category": [
      // 类目筛选
      { "name": "全部", "value": "" },
      { "name": "年终总结", "value": "年终总结" },
      { "name": "教育培训", "value": "教育培训" },
      { "name": "医学医疗", "value": "医学医疗" },
      { "name": "商业计划书", "value": "商业计划书" },
      { "name": "企业介绍", "value": "企业介绍" },
      { "name": "毕业答辩", "value": "毕业答辩" },
      { "name": "营销推广", "value": "营销推广" },
      { "name": "晚会表彰", "value": "晚会表彰" },
      { "name": "个人简历", "value": "个人简历" }
    ],
    "style": [
      // 风格筛选
      { "name": "全部", "value": "" },
      { "name": "扁平简约", "value": "扁平简约" },
      { "name": "商务科技", "value": "商务科技" },
      { "name": "文艺清新", "value": "文艺清新" },
      { "name": "卡通手绘", "value": "卡通手绘" },
      { "name": "中国风", "value": "中国风" },
      { "name": "创意时尚", "value": "创意时尚" },
      { "name": "创意趣味", "value": "创意趣味" }
    ],
    "themeColor": [
      // 主题颜色筛选
      { "name": "全部", "value": "" },
      { "name": "橙色", "value": "#FA920A" },
      { "name": "蓝色", "value": "#589AFD" },
      { "name": "紫色", "value": "#7664FA" },
      { "name": "青色", "value": "#65E5EC" },
      { "name": "绿色", "value": "#61D328" },
      { "name": "黄色", "value": "#F5FD59" },
      { "name": "红色", "value": "#E05757" },
      { "name": "棕色", "value": "#8F5A0B" },
      { "name": "白色", "value": "#FFFFFF" },
      { "name": "黑色", "value": "#000000" }
    ]
  },
  "code": 0,
  "message": "ok"
}

### 分页查询 PPT 模板
接口说明： 分页查询 PPT 模版

POST
http://data.oillink.com/api/shengli/Pptapi/getTemplates


参数

{
  "page": 1,
  "size": 10,
  "filters": {
    "type": 1, // 模板类型（必传）：1系统模板、4用户自定义模板
    "category": null, // 类目筛选
    "style": null, // 风格筛选
    "themeColor": null // 主题颜色筛选
  }
}

响应

{
  "code": 0,
  "total": 1,
  "data": [
    {
      "id": "xxx", // 模板ID
      "type": 1, // 模板类型：1大纲完整PPT、4用户模板
      "coverUrl": "https://xxx.png", // 封面（需要拼接?token=${token}访问）
      "category": null, // 类目
      "style": null, // 风格
      "themeColor": null, // 主题颜色
      "subject": "", // 主题
      "num": 20, // 模板页数
      "createTime": "2024-01-01 10:00:00"
    }
  ],
  "message": "操作成功"
}


### 下载 PPT
接口说明： 下载 PPT 到本地

POST
http://data.oillink.com/api/shengli/Pptapi/downloadPptx


请求

{
  "id": "xxx",
  "refresh": false
}

响应

{
  "code": 0,
  "data": {
    "id": "xxx",
    "name": "xxx",
    "subject": "xxx",
    "fileUrl": "https://xxx" // 文件链接（有效期：2小时）
  },
  "message": "操作成功"
}

### 下载-智能动画 PPT
接口说明： 给 PPT 自动加上动画再下载到本地

GET
http://data.oillink.com/api/shengli/Pptapi/downloadWithAnimation?type=1&id=xxx


URL 请求

参数	类型	描述
type	number	动画类型，1 依次展示（默认）；2 单击展示
id	string	PPT ID
响应（application/octet-stream）
文件数据流

该接口会在原有的 PPT 元素对象上智能添加动画效果（元素入场动画 & 页面切场动画）

动画类型介绍：

1 依次展示，表示上一个元素动画结束后立马展示下一个元素动画

2 单击展示，表示在内容页，上一项内容展示完成后需要单击才会展示下一项内容，其他页面效果同依次展示。

### 操作 PPT
更换 PPT 模板
POST
http://data.oillink.com/api/shengli/Pptapi/updatePptTemplate


参数

{
  "pptId": "xxx", // ppt id
  "templateId": "xxx", // 模板ID
  "sync": false // 是否同步更新PPT文件（默认 false 异步更新，速度快）
}

响应

{
  "code": 0,
  "data": {
    "pptId": "xxx",
    "templateId": "xxx",
    "pptxProperty": {
      // 更换后的pptx结构数据（json）
      // ...
    }
  }
}
