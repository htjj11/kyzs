# 论文检索API接口文档

## 接口地址

`/api/shengli/articlesearch/index`

## 请求方式

GET

## 请求参数

| 参数名    | 类型    | 是否必填 | 说明           | 示例值                         | 最大值/长度 |
|-----------|---------|----------|----------------|-------------------------------|-------------|
| page      | number  | 否       | 页码，从0开始   | 0                             |             |
| size      | number  | 否       | 每页条数        | 5                             |             |
| keywords  | string/array | 是   | 关键词数组或JSON字符串 | ["人工智能", "机器学习"] 或 "[\"人工智能\",\"机器学习\"]" |             |



## 返回数据结构（JSON格式）

| 字段         | 类型    | 说明         |
|--------------|---------|--------------|
| code         | int     | 状态码       |
| msg          | string  | 提示信息     |
| data         | object  | 结果数据     |

### data字段说明

| 字段         | 类型    | 说明         |
|--------------|---------|--------------|
| abstract     | string  | 摘要         |
| abstract_zh  | string  | 中文摘要     |
| doi          | string  | DOI          |
| id           | string  | 论文id       |
| keywords     | array   | 关键词       |
| keywords_zh  | array   | 中文关键词   |
| title        | string  | 标题         |
| title_zh     | string  | 中文标题     |
| total        | float   | 总数         |
| year         | float   | 年份         |

## 返回示例

```
{
  "code": 200,
  "msg": "success",
  "data": {
    "abstract": "This paper discusses...",
    "abstract_zh": "本文讨论了...",
    "doi": "10.1234/example.doi",
    "id": "paper123456",
    "keywords": ["AI", "Machine Learning"],
    "keywords_zh": ["人工智能", "机器学习"],
    "title": "Research on AI",
    "title_zh": "人工智能研究",
    "total": 100,
    "year": 2024
  }
}
```

## 请求示例

curl -X GET "http://data.oillink.com/api/shengli/articlesearch/index?keywords=%5B%22%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%22%2C%22%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%22%5D&page=0&size=5" 