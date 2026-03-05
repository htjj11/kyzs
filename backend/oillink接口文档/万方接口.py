
import requests
import xml.etree.ElementTree as ET

def parse_academic_papers(soap_response):
    """
    解析SOAP响应，提取学术论文信息并生成结构化列表
    
    参数:
        soap_response: SOAP响应的XML字符串（str类型）
    返回:
        list: 每篇论文为一个字典，包含核心学术字段
    """
    # 1. 定义所有必要的命名空间映射（关键！没有则无法定位节点）
    namespaces = {
        "soap": "http://schemas.xmlsoap.org/soap/envelope/",  # SOAP信封命名空间
        "srw": "http://www.loc.gov/zing/srw/",               # 搜索响应命名空间
        "dc": "info:srw/schema/1/dc-v1.1",                  # 论文元数据（DC标准）命名空间
        "srw_dc": "info:srw/schema/1/dc-v1.1"               # srw_dc前缀命名空间
    }

    # 2. 解析XML字符串，获取根节点
    root = ET.fromstring(soap_response)

    # 3. 定位所有<record>节点（XPath路径：逐层穿透到records下的record）
    # 注：XPath中需用"命名空间:节点名"格式，且传入namespaces参数
    record_nodes = root.findall(
        ".//soap:Body/srw:searchRetrieveResponse/srw:records/srw:record",
        namespaces=namespaces
    )

    # 4. 遍历每个record，提取论文信息
    papers = []
    for idx, record in enumerate(record_nodes, 1):
        # 定位当前record下的论文元数据节点（recordData → srw_dc:dc）
        dc_node = record.find("srw:recordData/srw_dc:dc", namespaces=namespaces)

        # 提取单篇论文的核心字段（用.find()定位dc前缀的节点，text获取值，None时用空字符串兜底）
        paper_info = {
            # "序号": idx,  # 手动添加序号，方便查看
            "标题": dc_node.find("dc:title", namespaces).text.strip() if dc_node.find("dc:title", namespaces) is not None else "",
            # "作者": dc_node.find("dc:Creator", namespaces).text.strip() if dc_node.find("dc:Creator", namespaces) is not None else "",
            "关键词": dc_node.find("dc:Subject", namespaces).text.strip() if dc_node.find("dc:Subject", namespaces) is not None else "",
            "摘要": dc_node.find("dc:Description", namespaces).text.strip() if dc_node.find("dc:Description", namespaces) is not None else "",
            # "贡献者": dc_node.find("dc:Contributor", namespaces).text.strip() if dc_node.find("dc:Contributor", namespaces) is not None else "",
            "发表时间": dc_node.find("dc:Date", namespaces).text.strip() if dc_node.find("dc:Date", namespaces) is not None else "",
            # "文献类型": dc_node.find("dc:Type", namespaces).text.strip() if dc_node.find("dc:Type", namespaces) is not None else "",
            # "文件格式": dc_node.find("dc:Format", namespaces).text.strip() if dc_node.find("dc:Format", namespaces) is not None else "",
            "DOI": dc_node.find("dc:Identifier", namespaces).text.strip() if dc_node.find("dc:Identifier", namespaces) is not None else "",
            # "语言": dc_node.find("dc:Language", namespaces).text.strip() if dc_node.find("dc:Language", namespaces) is not None else "",
            # "来源期刊": dc_node.find("dc:source", namespaces).text.strip() if dc_node.find("dc:source", namespaces) is not None else "",  # source首字母小写，与其他dc节点区分
            # "记录位置": record.find("srw:recordPosition", namespaces).text.strip() if record.find("srw:recordPosition", namespaces) is not None else ""
        }
        paper_info["发表时间"] = paper_info["发表时间"].split("-")[0]
        papers.append(paper_info)

    return papers

# 使用示例
def post_get(AfterDate = None, BeforeDate = None, Keywords = [], StartRecord = 1, MaximumRecords = 10):
    exps = []

    for keyword in Keywords:
        exps.append(f"{keyword}")

    if AfterDate:
        exps.append(f"Date >= {AfterDate}")
    # if BeforeDate:
    #     exps.append(f"Date <= {BeforeDate}")

    exp = " and ".join(exps)


    response = send_soap_request(exp, startRecord=StartRecord, maximumRecords=MaximumRecords)

    # 解析响应
    return parse_academic_papers(response)
    
   
    
def send_soap_request(exp, startRecord = 1, maximumRecords = 10):
    url = "http://10.68.16.2/S/SRW/Paper.asmx"
    headers = {
        "Host": "10.68.16.2",
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "searchRetrieve"
    }
    
    soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
                <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                            xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                            xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                <soap:Body>
                    <searchRetrieveRequest xmlns="http://www.loc.gov/zing/srw/">
                        <version>1.2</version>
                        <query>{exp}</query>
                        <startRecord>{startRecord}</startRecord>
                        <maximumRecords>{maximumRecords}</maximumRecords>
                    </searchRetrieveRequest>
                </soap:Body>
                </soap:Envelope>"""
    
    try:
        response = requests.post(url, data=soap_body, headers=headers)
        response.raise_for_status()
        print("Response Status Code:", response.status_code)
        # print("Response Content:")
        print(response.text)
        return response.text
    except requests.exceptions.RequestException as e:
        print("Error sending SOAP request:", e)
        return None

if __name__ == "__main__":
    records_list = post_get(AfterDate="2018-01-01", Keywords=["石油","钻井"], StartRecord = 1, MaximumRecords = 10)
     # 打印结果
    print(f"共解析到 {len(records_list)} 篇学术论文：\n")
    print(records_list)
    # for paper in records_list:
    #     print("=" * 80)
    #     for key, value in paper.items():
    #         print(f"{key:8}: {value}")  # 左对齐8个字符，字段名与值对齐
    # print("=" * 80)