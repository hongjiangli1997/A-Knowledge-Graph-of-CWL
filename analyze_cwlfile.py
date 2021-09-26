import yaml
import os
import json

""" filepath = 'raw_cwl/22846/wf_bacterial_annot_pass3.cwl'
with open(filepath, 'r') as f:
    cwl = f.read()

cwl_json = yaml.load(cwl,Loader= yaml.FullLoader)
print(cwl_json) """
# 收集所有的input，output，step
# 向data中加入信息 run信息
# 分析 各input output step的字符频率, 看看出现最高的是什么实体
# 加入format分析， 看看对应的名称


# deep walk 进行节点相似度计算
# 有多少使用了edam

# 错误类型：无法解析的 是空文档  有的是用json模式写的 yaml无法解析


def get_purelist(path):
    with open(path,'r') as f:
        id_list = f.read().split(',')
    id_list = list(filter(None, id_list))
    return id_list



def process_steps(original_dict):
    step_dict = {}
    if isinstance(original_dict,list):
        for item in original_dict:
            sub_dict = process_steps(item)
            step_dict.update({item.get('id'):sub_dict})
    
    elif isinstance(original_dict,dict):
        for key, value in original_dict.items():
            if key == 'in' or key == 'out':
                # 忽略 in 和 out 在 run里面的
                continue
            elif key == 'run':
                # 可能是文件 也可能是小的工作流
                if isinstance(value,str):
                    step_dict['run'] = {'IsFile':True,'Filename':value.split('/')[-1]}  
                else:
                    step_dict['run'] = {'IsFile':False, 'SubWorkflow':process_cwl(value)}

            elif isinstance(value,dict):
                sub_dict = process_steps(value)
                step_dict.update({key:sub_dict})            
                

    return step_dict

def process_cwl(cwl_json):
    cwl_dict = {}
    cwl_dict['inputs'] = cwl_json.get('inputs')
    cwl_dict['outputs'] = cwl_json.get('outputs')
    cwl_dict['class'] = cwl_json.get('class')
    cwl_dict['steps'] = process_steps(cwl_json.get('steps'))
    return cwl_dict



def gather_cwl_information(filepath):
    cwl_dict= {}
    error = False

    id = filepath.split('/')[-2]

    with open(filepath, 'r') as f:
        cwl = f.read()

    try:
        cwl_json = yaml.load(cwl,Loader = yaml.FullLoader)
    except:
        print('process {} failed...'.format(filepath))
        error = True
        return error,cwl_dict
        
    if not isinstance(cwl_json,dict):
        print('{} has no cwl content/ can not parse...'.format(filepath))
        error = True
        return error,cwl_dict
 
    cwl_dict['inputs'] = cwl_json.get('inputs')
    cwl_dict['outputs'] = cwl_json.get('outputs')
    cwl_dict['class'] = cwl_json.get('class')

    if cwl_dict['inputs'] == None and cwl_dict['outputs'] == None:
        print('process {} failed... Input is Null'.format(filepath))
        return True, cwl_dict
    else:
        cwl_dict['steps'] = process_steps(cwl_json.get('steps'))
        return error, cwl_dict

    


def get_cwl_info(id_list):
    cwlfiles_dict = {}
    error_list = []
    base_path = 'raw_cwl/'
    for num, id in enumerate(id_list):
        file_dict = {} #单个文件的字典
        dir_path = base_path + id + '/'
        files = os.listdir(dir_path)
        # 判断是否存在文件
        if len(files)>0:
            #遍历文件
            for file in files:
                #寻找 cwl文件
                if file.endswith('.html'):
                    continue
                elif file.endswith('.cwl'):
                    real_path = os.path.join(dir_path,file)
                    if id == '3':
                        print('3')
                    error, cwl_dict = gather_cwl_information(real_path)
                    if error:
                        error_list.append(id)
                    else:
                        cwlfiles_dict[id] = cwl_dict
                else:
                    print('ID {} Can not find CWL file, end with .cwl'.format(id))
                    error_list.append(id)
                #计数
        if (num+1) % 10 == 0:
            print('process...{}'.format(num+1))


    # save lines data
    line_data_path = 'data/purelist3_cwl_lines.json'
    save_data_path = 'data/purelist3_cwl.json'

    with open(line_data_path,'w+') as f:
        for key, value in cwlfiles_dict.items():
            dict = {}
            dict['_id'] = key
            dict.update(value)
            content = json.dumps(dict)
            f.writelines(content+'\n')
    
    # save format data
    with open(save_data_path,'w') as f:
        content = json.dumps(cwlfiles_dict,indent=4)
        f.write(content)


def merge_files(filepath1, filepath2):
    merge_info = {}
    with open(filepath1,'r') as f1, open(filepath2,'r') as f2:
        cwl_str = f1.readline()
        data_str = f2.readline()
        while(cwl_str and data_str):
            cwl = json.loads(cwl_str)
            data = json.loads(data_str)
            while(cwl['_id']>data ['_id']):
                data = json.loads(f2.readline())
            while(cwl['_id']<data ['_id']):
                cwl = json.loads(f1.readline())
            if(cwl['_id'] == data ['_id']):
                _id = int(cwl['_id'])
                cwl_info = simplify_cwl(cwl)
                data.update(cwl_info)
                merge_info[_id] = data
                # 继续读取
                cwl_str = f1.readline()
                data_str = f2.readline()
    
    # save lines data
    line_data_path = 'data/purelist3_merge_lines.json'
    save_data_path = 'data/purelist3_merge.json'

    with open(line_data_path,'w+') as f:
        for key, value in merge_info.items():
            dict = {}
            dict['_id'] = key
            dict.update(value)
            content = json.dumps(dict)
            f.writelines(content+'\n')
    
    # save format data
    with open(save_data_path,'w') as f:
        content = json.dumps(merge_info,indent=4)
        f.write(content)



def simplify_cwl(cwl):
    cwl_info = {}
    # input
    if(cwl.get('inputs')):
        cwl_info['inputs'] = process_in_out(cwl['inputs'])
    else:
        print('no input')
    
    #output
    if(cwl.get('outputs')):
        cwl_info['outputs'] = process_in_out(cwl['outputs'])
    else:
        print('no output')

    #steps
    if(cwl.get('steps')):
        cwl_info['runs'] = process_run_info(cwl['steps'])
    else:
        print('no steps')
    
    #class
    cwl_info['_class'] = cwl['class']
    return cwl_info

def process_in_out(in_out_puts):
    # 还没完成 list type下的多种类
    # TODO :format
    inputs = {}
    
    if(isinstance(in_out_puts, list)):
        for item in in_out_puts:
            name = item['id']
            type = process_single_type_item(item['type'])
            inputs[name] = {'type':type}

    elif(isinstance(in_out_puts, dict)):
        for key, value in in_out_puts.items():
            type = process_single_type_item(value)
            inputs[key] = {'type':type}

    return inputs

def process_single_type_item(single_type):
    #处理单个类型的type，根据类别处理
    type = []
    if(isinstance(single_type,str)):
        type.append(single_type)

    elif(isinstance(single_type,list)):
        for _type in single_type:
            if(isinstance(_type, str)):
                type.append(_type)
            elif(isinstance(_type,dict)):
                type.append(_type["type"])
            else:
                print('list in type process')    

    elif(isinstance(single_type,dict)):
        if(isinstance(single_type['type'],list)):
            type = process_single_type_item(single_type['type'])
        else:
            type.append(single_type['type'])


    else:
        print('type process error...')
    return type


def  process_run_info(steps):
    #处理步骤信息
    runs = []
    if(isinstance(steps,dict)):
        for name,value in steps.items():
            step_info = {}
            if(value['run']['IsFile']):
                step_info['StepName'] = name
                step_info['file_name'] = value['run']['Filename']
                runs.append(step_info)
            else:
                #TODO:subworkflow
                pass
    else:
        print("step process error")
    return runs
                    


#path = 'statistic_data/purelist_3.txt'
#id_list = get_purelist(path)
#get_cwl_info(id_list)

merge_files('data/purelist3_cwl_lines.json','data/purelist3_data_lines.json')
