# 2
#遍历所有干净的html
#寻找作者字段获取作者的用户名
#根据作者用户名获取作者 Name Company Location Bio
#把信息保存到json文档， 每个作者有一个单独的作者名单，每个项目有单独的项目名单
#一个文件有所属项目，作者，创建时间
import os
from bs4 import BeautifulSoup
import json


def pure_list2():
    #因为有些error发生在读取作者，因此生成porelist2、
    #读取原来的purelist
    pure_list_path = 'statistic_data\purelist.txt'
    with open(pure_list_path,'r') as f:
        pure_list = f.read().split(',')
    #读取获取作者信息的错误的list
    error_path = 'statistic_data\get_author_errorlist.txt'
    error_list = []
    with open(error_path,'r') as f:
        errors = f.read()
    errors = errors.split('\n')
    #在原来的purelist删除出现错误的id
    for error in errors:
        error = error.split('error...')[-1]
        pure_list.remove(error)
    #保存新的list 作为purelist2
    with open('statistic_data\purelist_2.txt','w+') as f:
        results = sorted(list(map(int, pure_list)))
        for i in results:
            f.write(str(i)+',')

# pure_list2()


def check_author_exist(author):
#检查作者是否还存在
    if len(author) > 0:
        return True
    else:
        return False


def get_author_uid():
    #生成 文件json列表
    data_dict = {}
    error_list = []

    # pure_list = 'statistic_data/purelist_2.txt'
    # pure_list = 'statistic_data/test_list.txt'
    pure_list = 'statistic_data/purelist_3.txt'
    with open(pure_list,'r') as f:
        id_list = f.read().split(',')
    id_list = list(filter(None, id_list))

    base_path = 'raw_cwl/'
    for num, id in enumerate(id_list):
        file_dict = {} #单个文件的字典
        html_path = base_path + id + '/' + 'soure_' + id + '.html'
        
        with open(html_path,'r', encoding='utf-8') as f:
            html_text = f.read()
            html = BeautifulSoup(html_text,"html.parser")

        #寻找作者账户是否存在
        author = html.find_all('a', class_='text-bold Link--primary')
        file_dict['author_exist'] = check_author_exist(author)


        # 寻找用户名
        try:
            usr_name = html.find(class_="text-bold Link--primary").text
        except:
            print('usr_name...error...{}'.format(id))
            error_list.append(id)
            continue
        file_dict['usr_name'] = usr_name


        #寻找文件名字
        try:
            file_name = html.find(class_="final-path").text 
        except:
            print('file_name...error...{}'.format(id))
            error_list.append(id)
            continue
        file_dict['file_name'] = file_name


        #文件创建日期
        latest_date = html.find_all('relative-time')
        if len(latest_date) == 1:
            latest_date = latest_date[0].get('datetime')
        else:
            error_list.append(id)
            print('latest_date...error...{}'.format(id))
        file_dict['latest_date'] = latest_date.split('T')[0]


        #寻找项目名字
        project_name = html.find_all('a',attrs={"data-pjax":"#js-repo-pjax-container"})
        if len(project_name) == 1:
            project_name = project_name[0].text
        else:
            error_list.append(id)
            print('project_name...error...{}'.format(id))
        file_dict['project_name'] = project_name


        #寻找项目所属作者和type
        project_author = html.find_all('a',class_='url fn')
        if len(project_author) == 1:
            project_author = project_author[0]
        else:
            print('project_author...error...{}'.format(id))
            error_list.append(id)
        project_author_type = project_author.get('data-hovercard-type')
        file_dict['project_author'] = project_author.text
        file_dict['project_author_type'] = project_author_type


        #贡献者用户名
        contributors = html.find_all(class_="avatar mr-2 avatar-user") 
        if len(contributors) != 0 :
            contributors_list = []
            for contributor in contributors:
                usr_name = contributor.get('alt')[1:]
                contributors_list.append(usr_name)
            file_dict['contributors'] = contributors_list

        data_dict[id] = file_dict


        #计数
        if (num+1) % 10 == 0:
            print('process...{}'.format(num+1))


    with open('data/purelist3_data_lines.json','w+') as f:
        for key, value in data_dict.items():
            dict = {}
            dict['_id'] = key
            dict.update(value)
            content = json.dumps(dict)
            f.writelines(content+'\n')
    
    with open('data/purelist3_data.json','w') as f:
        content = json.dumps(data_dict,indent=4)
        f.write(content)
    
    

get_author_uid()





