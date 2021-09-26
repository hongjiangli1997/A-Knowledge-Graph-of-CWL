import os
import json
from py2neo import Graph,Node


class WorkFlowGraph:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        self.data_path = os.path.join(cur_dir, 'data/purelist3_merge_lines.json')
        self.g = Graph("http://localhost:7474", auth=("neo4j", "neo4j"))
    
    
    '''读取文件'''
    def read_nodes(self):

        # 共n类节点
        workflows = []
        organizations = []
        usrs = []
        projects = []
        locations = []

        workflow_infos = []
        usr_infos = []

        # 构建节点实体关系
        rels_IsAuthorOf = [] # a 是 workflow b 的作者
        rels_Contribute = [] # a 是 workflow b 贡献者
        rels_ContainWorkFlow = [] # 项目 a 包含 workflow b
        rels_ContainProject_Org = []  # 用户或者组织 a 包含 项目 b
        rels_ContainProject_Usr = []  # 用户或者组织 a 包含 项目 b

        # ----------------------
        inputs = []
        outputs = []

        rels_HasInput = []
        rels_HasOutput = []
        rels_RunFile = []

        count = 0

        for data in open(self.data_path):
            workflow_dict = {}
            

            count += 1
            print(count)

            data_json = json.loads(data)
            
            workflow_name = data_json['file_name']
            workflow_dict['file_name'] = workflow_name
            workflow_dict['_class'] = data_json['_class']
            workflows.append(workflow_name)

            if 'latest_date'  in data_json:
                workflow_dict['latest_date'] = data_json['latest_date']
            
            if 'project_name' in data_json:
                projects.append(data_json['project_name'])
                _project = data_json['project_name']
                rels_ContainWorkFlow.append([_project, workflow_name])

            if 'usr_name' in data_json:
                _usr_name = data_json['usr_name']
                rels_IsAuthorOf.append([_usr_name, workflow_name])
                usr_dict = {}
                usr_dict['_login'] = _usr_name
                usr_dict['exist'] = data_json['author_exist']
                usr_infos.append(usr_dict)
                usrs.append(_usr_name)

            if 'contributors' in data_json:
                for usr_name in data_json['contributors']:
                    rels_Contribute.append([usr_name, workflow_name])
                    usr_dict = {'_login':usr_name,'exist':''}
                    usr_infos.append(usr_dict)
                    usrs.append(usr_name)
            
            if 'project_author' in data_json:
                _author = data_json['project_author']
                if data_json['project_author_type'] == 'organization':
                    organizations.append(_author) 
                    rels_ContainProject_Org.append([_author, _project])
                elif data_json['project_author_type'] == 'user':
                    usr_dict = {'_login':_author,'exist':''}
                    usr_infos.append(usr_dict)
                    usrs.append(_author)
                    rels_ContainProject_Usr.append([_author, _project])
            
            if 'inputs' in data_json:
                for key, value in data_json['inputs'].items():
                    inputs.append(key)
                    rels_HasInput.append([workflow_name,key])
            
            if 'outputs' in data_json:
                for key, value in data_json['outputs'].items():
                    outputs.append(key)
                    rels_HasOutput.append([workflow_name,key])
            
            if 'runs' in data_json:
                for step in data_json['runs']:
                    rels_RunFile.append([workflow_name, step['file_name']])

            workflow_infos.append(workflow_dict)

        #作者字典去重和workflow去重
        return set(workflows), set(organizations), set(usrs), set(projects), set(inputs), set(outputs), workflow_infos, usr_infos,\
               rels_IsAuthorOf, rels_Contribute, rels_ContainWorkFlow, rels_ContainProject_Org, rels_ContainProject_Usr, \
               rels_HasInput, rels_HasOutput, rels_RunFile
               



    '''创建知识图谱实体节点类型schema'''
    def create_graphnodes(self):
        Workflows, Organizations, Usrs, Projects, Inputs, Outputs, workflow_infos, usr_infos, rels_IsAuthorOf, rels_Contribute, rels_ContainWorkFlow, rels_ContainProject_Org, rels_ContainProject_Usr, rels_HasInput, rels_HasOutput, rels_RunFile = self.read_nodes()
        self.create_workflows_nodes(workflow_infos)
        self.create_node('User', Usrs)
        # self.create_usrs_nodes(usr_infos)

        self.create_node('Organization', Organizations)
        print(len(Organizations))

        self.create_node('Project', Projects)
        print(len(Projects))

        self.create_node('Input', Inputs)
        print(len(Inputs))

        self.create_node('Output', Outputs)
        print(len(Outputs))
        return
    

    '''建立节点'''
    def create_node(self, label, nodes):
        count = 0
        for node_name in nodes:
            node = Node(label, name=node_name)
            self.g.create(node)
            count += 1
            print(count, len(nodes))
        return


    '''创建知识图谱中心疾病的节点'''
    def create_workflows_nodes(self, workflow_infos):
        count = 0
        for workflow_dict in workflow_infos:
            node = Node("Workflow", name=workflow_dict['file_name'], latest_date=workflow_dict['latest_date'], _class = workflow_dict['_class'])
            self.g.create(node)
            count += 1
            print(count)
        return
    

    '''创建知识图谱中心疾病的节点'''
    def create_usrs_nodes(self, usr_infos):
        count = 0
        for usr_dict in usr_infos:
            node = Node("User", name=usr_dict['_login'], exist=usr_dict['exist'])
            self.g.create(node)
            count += 1
            print(count)
        return



    '''创建实体关系边'''
    def create_graphrels(self):
        Workflows, Organizations, Usrs, Projects, Inputs, Outputs, workflow_infos, usr_infos, rels_IsAuthorOf, rels_Contribute, rels_ContainWorkFlow, rels_ContainProject_Org, rels_ContainProject_Usr, rels_HasInput, rels_HasOutput, rels_RunFile = self.read_nodes()
        self.create_relationship('User', 'Workflow', rels_IsAuthorOf, 'IsAuthorOf', 'The author of workflow')
        self.create_relationship('User', 'Workflow', rels_Contribute, 'IsContributorOf', 'The contributor of workflow')
        self.create_relationship('Project', 'Workflow', rels_ContainWorkFlow, 'contain_workflow', 'The project contain workflow')
        self.create_relationship('Organization', 'Project', rels_ContainProject_Org, 'contain_project', 'The org contain workflow')
        self.create_relationship('User', 'Project', rels_ContainProject_Usr, 'contain_project', 'The org contain workflow')
        self.create_relationship('Workflow', 'Input', rels_HasInput, 'has_input', 'a workflow has input')
        self.create_relationship('Workflow', 'Output', rels_HasOutput, 'has_output', 'a workflow has output')
        self.create_relationship('Workflow', 'Workflow', rels_RunFile, 'run', 'a workflow run another workflow')



    '''创建实体关联边'''
    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        count = 0
        # 去重处理
        set_edges = []
        for edge in edges:
            set_edges.append('###'.join(edge))
        all = len(set(set_edges))
        for edge in set(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            try:
                self.g.run(query)
                count += 1
                print(rel_type, count, all)
            except Exception as e:
                print(e)
        return


    def deleteDuplicate(self, dict):
        pass


if __name__ == '__main__':
    handler = WorkFlowGraph()
    #handler.export_data()
    handler.create_graphnodes()
    handler.create_graphrels()


