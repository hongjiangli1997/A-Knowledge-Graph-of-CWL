def process_data(html,id_start):
    """
    html：json
    id_start: length
    传入每一页的json格式的内容, 总的字典长度
    提取爬虫获取的html页的信息，获取每个label和url
    """
    content = {}
    for item in html['content']:
        content[id] = {'label':item['label'], 
                       'url': item['retrievedFrom'].get('url')}
        id += 1
    return  content

out_content = {}
id_start = len(out_content)
add_content = process_data(jsondata,id_start)
out_content.update(add_content)




#------------------------------------------------------------------------
import requests
import time
import os
import json



BASE_URL = 'https://view.commonwl.org'
WORKFLOW_PATH = '/workflows/workflow.cwl'
WORKFLOW_URL = 'https://view.commonwl.org/workflows'

TRAVIS_COMMIT = os.getenv('TRAVIS_COMMIT')
TRAVIS_REPO_SLUG = os.getenv('TRAVIS_REPO_SLUG')


# Whole workflow URL on github
workflowURL = 'https://github.com/'  + '/blob/'  + WORKFLOW_PATH



# Headers
HEADERS = {
    'user-agent': 'my-app/0.0.1',
    'accept': 'application/json'
}

# 页面大小
PAGE_SIZE = 100

# 页面数据
TOTAL_ELEMENT = 1
TOTAL_PAGES = 1


def format_json(filePath):
    # 格式化json文件
    with open(filePath,'r+') as f:
        data = json.loads(f.read())
        form_data = json.dumps(data, indent=4, separators=(',', ':'))
        f.seek(0)
        f.truncate()
        f.write(form_data)



def get_page(url,params = None):
    #获取url 转换成json
    r = requests.get(url,
                    headers=HEADERS,
                    params=params)
    html = r.text
    jsondata = json.loads(html)
    return jsondata



def process_data(html,id):
    """
    html：json
    id: length
    传入每一页的json格式的内容, 总的字典长度
    提取爬虫获取的html页的信息，获取每个label和url
    """
    content = {}
    for item in html['content']:
        content[id] = {'label':item['label'], 
                       'url': item['retrievedFrom'].get('url')}
        id += 1
    return  content

page_info = {'size': PAGE_SIZE}
data = get_page(WORKFLOW_URL,params=page_info)
TOTAL_ELEMENT = data.get('totalElements')
TOTAL_PAGES = data.get('totalPages')

page_list = []
out_content = {}
for i in range(TOTAL_PAGES):
    print("---------NOW processing page {}---------------".format(i))
    page_info = {'page': i, 'size': PAGE_SIZE}
    page = get_page(WORKFLOW_URL,params = page_info)
    
    
    id_start = len(out_content)
    add_content = process_data(page,id_start)
    out_content.update(add_content)

out_json = json.dumps(out_content)

with open('data.json', 'w+') as f:
    f.write(out_json)

format_json('data1.json')








    


