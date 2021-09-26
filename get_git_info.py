import requests
import time
import os
import json
from bs4 import BeautifulSoup
import urllib

import re as regular

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import selenium 


HEADERS = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7'
}
header_1 = {
    'Accept': 'text/html, */*; q=0.01',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'
}

GIT_URL = "https://github.com/EOSC-LOFAR/presto-cwl/blob/master/presto.cwl"
usr_url = "https://github.com/tmooney"





# br = webdriver.Firefox(executable_path='D:/Program Files (x86)/geckodriver.exe')

def save_html(start = 0, one = False):
    # 遍历文件遍历所有url 下载html
    # one 代表只下载一个文件
    
    filepath = 'data1.json'
    with open(filepath, 'r') as f:
        data = json.loads(f.read())
        num = 0
        for id, content in data.items():
            if int(id) in range(int(start)):
                continue 
            url = content['url']
            download_html(id,url)
            if one == True:
                break
            num += 1


def download_html(id,url, one  = False):
    #下载一个 html
    # one 代表只下载一次
    base_path = 'raw_cwl/'
    save_path = base_path + str(id) + '/' + 'soure_{}.html'.format(id)
    try:
        br.get(url)
    except : 
        print ("Timeout Error:{}".format(id))  
        if one == False:
            for i in range(20):
                download_html(id,url, one = True)
        if one == True:
            return
            
    time.sleep(1)
    html_2 = br.page_source
    with open(save_path, 'w+', encoding="utf-8-sig") as f:
        print(url)
        print('------{}----------------'.format(id))
        f.write(html_2)



# save_html()


def check_page(file_path):
    #检查html文件是否存在或者404
    #错误返回文件id 正常返回-1
    id = file_path.split('/')[-2]
    if not os.path.exists(file_path):
        print("lack file {}".format(id))
        return int(id)
    with open(file_path,'r', encoding='utf-8') as f:
        html_text = f.read()
        html = BeautifulSoup(html_text,"html.parser")
        error_404 = html.find_all('img', alt="404 “This is not the web page you are looking for”")
        if len(error_404) > 0:
            print("file {} 404".format(id))
            return int(id)
        else:
            return -1


file_path = 'Page not found GitHub.html'
file_path = 'raw_cwl/0/soure_0.html'
# check_page(file_path)


def check_all_page():
    # 遍历文件夹 检查所有文件
    base_path = 'raw_cwl/'
    files= os.listdir(base_path) 
    error_list = []
    num = 0
    total = 0
    for file in files:
        file_path = base_path + file + '/' + 'soure_' + file + '.html'
        re = check_page(file_path)
        if re != -1:
            error_list.append(re)
            save_html(re,one = True)
        num += 1
        if num == 1000:
            total += num
            print("process  {}".format(total) )
            num = 0
    print(error_list)


# check_all_page()

def generate_pure_list():
    # 生成一个没有404的列表
    base_path = 'raw_cwl/'
    statistical_path = 'statistic_data/'
    with open(statistical_path+'error_list.txt','r') as f:
        txt = f.read()
        error_list = regular.split('[, \n]',txt)
        error_list = list(filter(None, error_list))
    files= os.listdir(base_path) 
    pure_list = [n for n in files if n not in error_list]


    with open(statistical_path+'purelist.txt','w+') as f:
        print('finish...')
        results = sorted(list(map(int, pure_list)))
        for i in results:
            f.write(str(i)+',')

generate_pure_list()















session = requests.session()
r = session.get(GIT_URL,headers=header_1)

html_str = r.text
html = BeautifulSoup(html_2,"html.parser")
#print(html.prettify())
author = html.find_all('a', rel='contributor')
#print(author)
print(author[0].attrs['href'])