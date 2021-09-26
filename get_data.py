# 1
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

HEADERS_GIT = {}
GIT_URL = "https://github.com/genome/analysis-workflows/blob/3a287b7cb6162cdea79865235d224fea45963d87/definitions/pipelines/alignment_exome.cwl"

#"https://raw.githubusercontent.com/genome/analysis-workflows/3a287b7cb6162cdea79865235d224fea45963d87/definitions/pipelines/alignment_exome.cwl"
r = requests.get(GIT_URL)
html = r.text
print(html)


### 获取github中的源文件


def download_raw(id, url):
    #根据json中的id，url获取CWL源文件
    url = url.split('/')
    base = 'raw.githubusercontent.com'
    raw_url = ''
    file_name = url[-1]
    #根据不同字段构造raw-url
    for i in range(len(url)):
        if i == 2:
            raw_url = raw_url + '/' + base
        elif i == 5:
            continue
        elif i == 0:
            raw_url = url[i]
        else:
            raw_url = raw_url + '/' + url[i]
    
    r = requests.get(raw_url)
    raw_file = r.text

    file_dir = 'raw_cwl/' + str(id) 
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)
    
    file_path = file_dir + '/' + file_name
    with open(file_path, 'w+' ) as f:
        f.write(raw_file)




def gather_file_info(id, url):
    r = requests.get(url)
    html = r.text
    print(html)
    


    
def download_cwl():
    #下载json文件中所有的raw文件
    filepath = 'data1.json'
    with open(filepath, 'r') as f:
        data = json.loads(f.read())
        for id, content in data.items():
            #if int(id) in range(7071):
                #continue
            print('-----------Now processing num.{}-----------'.format(id))
            url = content['url']
            # download_raw(id,url)
            gather_file_info(id, url)


download_cwl()



#----------------------------------------------------------------------

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





### 保存cwl viewer的json数据

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










    

