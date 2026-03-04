# 专利检索API接口文档

## 接口地址

`/api/shengli/patentsearch/index`

## 请求方式

GET

## 请求参数

| 参数名       | 类型   | 是否必填 | 说明         | 示例值 | 最大值/长度 |
|--------------|--------|----------|--------------|--------|-------------|
| query        | string | 是       | 检索关键词   | "人工智能" |             |
| page         | number | 否       | 页码，从0开始 | 0      |             |
| size         | number | 否       | 每页条数     | 20     |             |

## 返回数据结构（JSON格式）

| 字段         | 类型    | 说明         |
|--------------|---------|--------------|
| code         | int     | 状态码       |
| msg          | string  | 提示信息     |
| data         | array   | 结果数据     |

### data字段说明 (数组中的每个元素代表一个专利详情)

| 字段         | 类型    | 说明         |
|--------------|---------|--------------|
| id           | string  | 专利ID       |
| title        | string  | 专利标题     |
| abstract     | string  | 专利摘要     |
| year         | number  | 专利年份     |
| authors      | array   | 作者列表     |
| assignees    | array   | 受让人列表   |
| country      | string  | 国家         |
| publication_date | string | 发布日期     |

## 返回示例

```json
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "id": "patent123",
      "title": "一种基于深度学习的图像识别方法",
      "abstract": "本发明公开了一种基于深度学习的图像识别方法，通过构建多层神经网络模型，实现对图像的高效识别和分类。",
      "year": 2023,
      "authors": ["张三", "李四"],
      "assignees": ["某科技公司"],
      "country": "CN",
      "publication_date": "2023-01-15"
    },
    {
      "id": "patent456",
      "title": "人工智能在医疗诊断中的应用",
      "abstract": "本研究探讨了人工智能技术在医疗诊断领域的应用，旨在提高疾病诊断的准确性和效率。",
      "year": 2022,
      "authors": ["王五"],
      "assignees": ["某医疗机构"],
      "country": "CN",
      "publication_date": "2022-07-20"
    }
  ]
}
```

## 请求示例

`curl -X GET "http://data.oillink.com/api/shengli/patentsearch/index?query=%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&page=0&size=10"`

