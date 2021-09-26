# 3

import os
import json
from functools import reduce
import requests

def deleteDuplicate(dict):
    func = lambda x, y: x if y in x else x + [y]
    return reduce(func, [[], ] + dict)


def pure_list3():
    #去重，在pure_list2基础上，有些作者，工作流的名字是相同的，这些会在创建节点时产生误导，音系要去掉重复的
    cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
    data_path = os.path.join(cur_dir, 'data/purelist2_data_lines.json')

    workflows = {}

    for num,data in enumerate(open(data_path)):


        #加载文件信息
        data_json = json.loads(data)
        file_name = data_json['file_name']
        date = data_json['latest_date']  
        id = data_json['_id']
        project = data_json['project_name']

        #生成key
        cwl_key = file_name+'-###-'+project

        #判断是否更新字典
        if cwl_key not in workflows.keys():
            workflows.update({cwl_key:[id,date,1]})
        else:
            workflows.update({cwl_key:[id,workflows[cwl_key][1],workflows[cwl_key][2]+1]})
            if date > workflows[cwl_key][1]:
                workflows.update({cwl_key:[id,date,workflows[cwl_key][2]]})

        #计数
        if (num+1) % 10 == 0:
            print('process...{}'.format(num+1))
    

    purelist3 = [workflow[0] for workflow in workflows.values()]

    with open('statistic_data\purelist_version.txt','w+') as f:
        results = sorted(list(map(int, purelist3)))
        for i in results:
            f.write(str(i)+',')


pure_list3()


def get_page(url,params = None):
    HEADERS = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7'
    }
    #获取url 转换成json
    r = requests.get(url,
                    headers=HEADERS,
                    params=params)
    html = r.text
    jsondata = json.loads(html)
    return jsondata


def get_user_info(path):

    # usrs_list = get_usr_list(path)

    usrs_dict = {}

    for num,data in enumerate(open(path)):
        file_dict = {}
        data_json = json.loads(data)

        cwl_id = data_json['_id']
        usr_login = data_json['usr_name']
        url = 'https://api.github.com/users/' + usr_login
        usr_data = get_page(url)
        if len(usr_data) < 3 :
            continue

        file_dict['usr_name'] = usr_data['login']
        file_dict['name'] = usr_data['name']
        file_dict['company'] = usr_data['company']
        file_dict['location'] = usr_data['location']
        file_dict['email'] = usr_data['email']
        file_dict['bio'] = usr_data['bio']
        
        usrs_dict[cwl_id] = file_dict

        #计数
        if (num+1) % 10 == 0:
            print('process...{}'.format(num+1))
    
    
    with open('data/usr1_data_lines.json','w+') as f:
        for key, value in usrs_dict.items():
            dict = {}
            dict['cwl_id'] = key
            dict.update(value)
            content = json.dumps(dict)
            f.writelines(content+'\n')
    
    with open('data/usr1_data.json','w') as f:
        content = json.dumps(usrs_dict,indent=4)
        f.write(content)
        



def get_project_info():
    pass


def get_org_info():
    pass


cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
data_path = os.path.join(cur_dir, 'data/purelist3_data_lines.json')
get_user_info(data_path)
