import requests
import xml.etree.ElementTree as ET




def get_article_from_wanfang_api(start_year=None, end_year=None, Keywords=[], StartRecord=1, MaximumRecords=10):
    """
    从万方检索文献，并标记每篇文章是否已被当前用户收藏（is_collected）。
    用 DOI 作为唯一标识匹配 knowledgebase 表。
    """
    exps = list(Keywords)
    if start_year and end_year:
        exps.append(f'Date within "{start_year}-01-01 {end_year}-12-31"')
    elif start_year:
        exps.append(f'Date within "{start_year}-01-01 {start_year}-12-31"')
    elif end_year:
        exps.append(f'Date within "{end_year}-01-01 {end_year}-12-31"')
    exp = " and ".join(exps)
    # print(f"检索表达式：{exp}")

    def send_soap_request_paper(exp, startRecord=1, maximumRecords=10):
        url = "http://10.68.16.2/S/SRW/Paper.asmx"
        headers = {"Host": "10.68.16.2", "Content-Type": "text/xml; charset=utf-8", "SOAPAction": "searchRetrieve"}
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
            <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                        xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
                <searchRetrieveRequest xmlns="http://www.loc.gov/zing/srw/">
                    <version>1.2</version>
                    <query>{exp}</query>
                    <operation>searchretrieve</operation>
                    <startRecord>{startRecord}</startRecord>
                    <maximumRecords>{maximumRecords}</maximumRecords>
                </searchRetrieveRequest>
            </soap:Body>
            </soap:Envelope>"""
        try:
            response = requests.post(url, data=soap_body, headers=headers)
            return response.text
        except Exception as e:
            # print("万方论文检索错误:", e)
            return None

    response = send_soap_request_paper(exp, startRecord=StartRecord, maximumRecords=MaximumRecords)
    with open("raw_response.txt", "w") as f:
        f.write(f"{response}")

    def parse_academic_papers(soap_response):
        namespaces = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "srw": "http://www.loc.gov/zing/srw/",
            "dc": "info:srw/schema/1/dc-v1.1",
            "srw_dc": "info:srw/schema/1/dc-v1.1"
        }
        # print(soap_response)
        root = ET.fromstring(soap_response)
        number_element = root.find('.//srw:numberOfRecords', namespaces=namespaces)
        if number_element is not None:
            number_of_records = number_element.text
            print(f"共解析到论文数量: {number_of_records}")
        else:
            print("未找到numberOfRecords元素")
            number_of_records = "0"
        record_nodes = root.findall(
            ".//soap:Body/srw:searchRetrieveResponse/srw:records/srw:record", namespaces=namespaces
        )
        papers = []
        for record in record_nodes:
            dc_node = record.find("srw:recordData/srw_dc:dc", namespaces=namespaces)
            def _get(tag):
                el = dc_node.find(tag, namespaces)
                return el.text.strip() if el is not None and el.text else ""
            info = {
                "标题": _get("dc:title"), "关键词": _get("dc:Subject"),
                "摘要": _get("dc:Description"), "发表时间": _get("dc:Date"),
                "DOI": _get("dc:Identifier"),
            }
            info["发表时间"] = info["发表时间"].split("-")[0]
            papers.append(info)
        return (papers, number_of_records)

    return parse_academic_papers(response)


def wangfang_patent(start_year=None, end_year=None, patent_name=[], StartRecord=1, MaximumRecords=10):
    exps = list(patent_name)
    if start_year and end_year:
        exps.append(f'F_PublicationDate within "{start_year}-01-01 {end_year}-12-31"')
    elif start_year:
        exps.append(f'F_PublicationDate within "{start_year}-01-01 {start_year}-12-31"')
    elif end_year:
        exps.append(f'F_PublicationDate within "{end_year}-01-01 {end_year}-12-31"')
    exp = " and ".join(exps)
    # print(f"检索表达式：{exp}")  # 原版注释掉了，保持一致

    def send_soap_request_patent(exp, startRecord=1, maximumRecords=10):
        url = "http://10.68.16.2/S/SRW/Patent.asmx"
        headers = {"Host": "10.68.16.2", "Content-Type": "text/xml; charset=utf-8", "SOAPAction": "searchRetrieve"}
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
            <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                        xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
                <searchRetrieveRequest xmlns="http://www.loc.gov/zing/srw/">
                    <version>1.2</version>
                    <query>{exp}</query>
                    <operation>searchretrieve</operation>
                    <startRecord>{startRecord}</startRecord>
                    <maximumRecords>{maximumRecords}</maximumRecords>
                </searchRetrieveRequest>
            </soap:Body>
            </soap:Envelope>"""
        try:
            response = requests.post(url, data=soap_body, headers=headers)
            response.raise_for_status()
            print("Response Status Code:", response.status_code)
            return response.text
        except requests.exceptions.RequestException as e:
            print("Error sending SOAP request:", e)
            return None

    response = send_soap_request_patent(exp, startRecord=StartRecord, maximumRecords=MaximumRecords)

    def parse_patents(soap_response) -> tuple:
        namespaces = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "srw": "http://www.loc.gov/zing/srw/",
            "dc": "info:srw/schema/1/dc-v1.1",
            "srw_dc": "info:srw/schema/1/dc-v1.1"
        }
        # print(soap_response)  # 原版注释掉了，保持一致
        root = ET.fromstring(soap_response)
        number_element = root.find('.//srw:numberOfRecords', namespaces=namespaces)
        if number_element is not None:
            number_of_records = number_element.text
            print(f"共解析到论文数量: {number_of_records}")
        else:
            print("未找到numberOfRecords元素")
            number_of_records = "0"
        record_nodes = root.findall(
            ".//soap:Body/srw:searchRetrieveResponse/srw:records/srw:record", namespaces=namespaces
        )
        papers = []
        for record in record_nodes:
            dc_node = record.find("srw:recordData/srw_dc:dc", namespaces=namespaces)
            def _get(tag):
                el = dc_node.find(tag, namespaces)
                return el.text.strip() if el is not None and el.text else ""
            papers.append({
                "申请号": _get("dc:ApplicationNo"), "申请日": _get("dc:ApplicationDate"),
                "公开号": _get("dc:PublicationNo"), "公开日": _get("dc:PublicationDate"),
                "专利名称": _get("dc:PatentName"), "申请人": _get("dc:Applicant"),
                "发明人": _get("dc:Inventor"), "IPC分类号": _get("dc:ClassMain"),
                "摘要": _get("dc:Abstract"), "权利要求": _get("dc:SignoryItem"),
            })
        return (papers, number_of_records)

    return parse_patents(response)

