from py2neo import Graph, Node

import pandas as pd

class CarGraph:
    def __init__(self):
        self.datapath = 'all_cars.csv'
        self.g = Graph("http://localhost:7474", auth=("neo4j", "hulongxing"))    #连接
    
    def read_nodes(self):
        data = pd.read_csv(self.datapath)   #读取数据

        brand_names = []
        serise_names = []
        scores = []
        levels = []
        structs = []
        EngineORbatterys = []
        SpeedchunkORcharges = []
        types = []
        prices = []
        status = []
        urls =  []

        cars_info = []

        #构建关系
        rel_brand2serise = []   #品牌与车系关系(1:n)
        rel_brand2price = []    #品牌与价格关系(1:n)
        rel_brand2type = []     #品牌与类型关系(1:n)
        rel_brand2urls = []     #品牌与链接关系(1:n)

        rel_name2scores = []    #车系评分关系(1:1)
        rel_serise2levels = []  #车系与车型(轿车、SUV等)关系(1:1)
        rel_serise2struct = []  #车系与车架关系(1:1)
        rel_serise2Engine = []  #车系与引擎关系(OR续航时间)(1:1)
        rel_serise2Chunk = []   #车系与变速器(OR充电时间)关系(1:1)
        rel_serise2type = []    #车系与类型关系(是否为新能源汽车)(1:1)
        rel_serise2price = []   #车系与价格(1:1)
        rel_serise2status = []  #车系与销售状态关系(1:1)
        rel_serise2url = []     #车系链接(1:1)

        current_serise_names = []
        current_prices = []
        current_types = []
        current_urls = []

        current_serise_name = []
        current_price = []
        current_type = []
        current_url = []

        current_brand = data.iloc[0, :]['brand_name']
        for i in range(data.shape[0]):
            car_dict = {}

            car_dict['brand_name'] = data.iloc[i, :]['brand_name']
            car_dict['serise_name'] = data.iloc[i, :]['serise_name']
            car_dict['score'] = data.iloc[i, :]['score']
            car_dict['level'] = data.iloc[i, :]['level']
            car_dict['struct'] = data.iloc[i, :]['struct']
            car_dict['EngineORbattery'] = data.iloc[i, :]['EngineORbattery']
            car_dict['SpeedchunkORcharge'] = data.iloc[i, :]['SpeedchunkORcharge']
            car_dict['type'] = data.iloc[i, :]['type']
            car_dict['price'] = data.iloc[i, :]['price']
            car_dict['status'] = data.iloc[i, :]['status']
            car_dict['url'] = data.iloc[i, :]['url']


            brand_names.append(car_dict['brand_name'])
            serise_names.append(car_dict['serise_name'])
            scores.append(car_dict['score'])
            levels.append(car_dict['level'])
            structs.append(car_dict['struct'])
            EngineORbatterys.append(car_dict['EngineORbattery'])
            SpeedchunkORcharges.append(car_dict['SpeedchunkORcharge'])
            types.append(car_dict['type'])
            prices.append(car_dict['price'])
            status.append(car_dict['status'])
            urls.append(car_dict['url'])

            

            if current_brand == car_dict['brand_name']:
                #如果之前已经记录了品牌，则
                current_serise_name.append(car_dict['serise_name'])
                current_price.append(car_dict['price'])
                current_type.append(car_dict['type'])
                current_url.append(car_dict['url'])
                
            else:
                current_serise_names.append(current_serise_name)
                current_prices.append(current_price)
                current_types.append(current_type)
                current_urls.append(current_url)
                current_serise_name, current_price, current_type, current_url = [], [], [], []  #清空操作，为下次做准备
                #如果之前已经记录了品牌，则
                current_serise_name.append(car_dict['serise_name'])
                current_price.append(car_dict['price'])
                current_type.append(car_dict['type'])
                current_url.append(car_dict['url'])
                current_brand = car_dict['brand_name']


            if i == data.shape[0]-1:
                current_serise_names.append(current_serise_name)
                current_prices.append(current_price)
                current_types.append(current_type)
                current_urls.append(current_url)

            rel_name2scores.append([car_dict['serise_name'], car_dict['score']])#车系评分关系(1:1)
            rel_serise2levels.append([car_dict['serise_name'], car_dict['level']])#车系与车型(轿车、SUV等)关系(1:1)
            rel_serise2struct.append([car_dict['serise_name'], car_dict['struct']]) #车系与车架关系(1:1)
            rel_serise2Engine.append([car_dict['serise_name'], car_dict['EngineORbattery']])  #车系与引擎关系(OR续航时间)(1:1)
            rel_serise2Chunk.append([car_dict['serise_name'], car_dict['SpeedchunkORcharge']])  #车系与变速器(OR充电时间)关系(1:1)
            rel_serise2type.append([car_dict['serise_name'], car_dict['type']])  #车系与类型关系(是否为新能源汽车)(1:1)
            rel_serise2price.append([car_dict['serise_name'], car_dict['price']])  #车系与价格(1:1)
            rel_serise2status.append([car_dict['serise_name'], car_dict['status']]) #车系与销售状态关系(1:1)
            rel_serise2url.append([car_dict['serise_name'], car_dict['url']])     #车系链接(1:1)

            cars_info.append(car_dict)
        #添加关系
        convert = list(set(brand_names))
        convert.sort(key=brand_names.index)

        rel_brand2serise = list(zip(convert, current_serise_names))
        
        rel_brand2price  = list(zip(convert, current_prices))
        rel_brand2type   = list(zip(convert, current_types))
        rel_brand2urls   = list(zip(convert, current_urls))

        return set(brand_names),serise_names,set(scores),set(levels),set(structs) ,set(EngineORbatterys),set(SpeedchunkORcharges),set(types),\
        set(prices),set(status),urls,rel_brand2serise, rel_brand2price, rel_brand2type, rel_brand2urls, rel_name2scores,\
        rel_serise2levels, rel_serise2struct, rel_serise2Engine, rel_serise2Chunk,\
        rel_serise2type, rel_serise2price, rel_serise2status, rel_serise2url, cars_info

        #额外处理一对多的列表

    def create_node(self, label, nodes):
        count = 0
        for node_name in nodes:
            node = Node(label, name=node_name)  #py2neo方法，node_name就是一类节点中的某一个，要建立对象
            self.g.create(node)
            count += 1
            print(count, len(nodes))
        return

    def create_car_nodes(self, cars_info):
        count = 0
        for car_dict in cars_info:
            node = Node("Car", name=car_dict['serise_name'], brand_name=car_dict['brand_name'],
                        score=car_dict['score'] ,level=car_dict['level'],
                        struct=car_dict['struct'],EngineORbattery=car_dict['EngineORbattery'],
                        SpeedchunkORcharge=car_dict['SpeedchunkORcharge'],
                        type=car_dict['type'] , price=car_dict['price'],
                        status=car_dict['status'], url=car_dict['url']
                        )
            self.g.create(node)
            count += 1
            print(count)        #打印每一个品牌的
        return

    '''创建知识图谱实体节点类型schema'''
    def create_graphnodes(self):
        brand_names,serise_names,scores,levels,structs ,EngineORbatterys,SpeedchunkORcharges,types,\
        prices,status,urls,rel_brand2serise, rel_brand2price, rel_brand2type, rel_brand2urls, rel_name2scores,\
        rel_serise2levels, rel_serise2struct, rel_serise2Engine, rel_serise2Chunk,\
        rel_serise2type, rel_serise2price, rel_serise2status, rel_serise2url, cars_info = self.read_nodes()

        self.create_car_nodes(cars_info)
        self.create_node('brand_names', brand_names)
        print(len(brand_names))
        self.create_node('serise_names', serise_names)
        print(len(serise_names))
        self.create_node('scores', scores)
        print(len(scores))
        self.create_node('levels', levels)
        print(len(levels))
        self.create_node('structs', structs)
        print(len(structs))
        self.create_node('EngineORbatterys', EngineORbatterys)
        print(len(EngineORbatterys))
        self.create_node('SpeedchunkORcharges', SpeedchunkORcharges)
        print(len(SpeedchunkORcharges))
        self.create_node('types', types)
        print(len(types))
        self.create_node('prices', prices)
        print(len(prices))
        self.create_node('status', status)
        print(len(status))
        self.create_node('urls', urls)
        print(len(urls))
        return

    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        count = 0
        #                                 # 去重处理  传进来的edges是列表，列表的元素还是列表
        # set_edges = []
        # for edge in edges:              #遍历每一个元素，把###加入进去，之后再分割
        #     set_edges.append('###'.join(edge))
        # all = len(set(set_edges))
        #先判断edge类型，如果是列表，则for循环，如果是字符串则
        for edge in edges:
            p  = edge[0]
            qs = edge[1]
            print(str(type(qs)))

            if str(type(qs)) == "<class 'str'>":
                query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, qs, rel_type, rel_name) #关键代码关键代码关键代码！！！创建指定两点之间指定的关系
                try:
                    self.g.run(query)   #pyneo方法
                    print("{}---{}---->{}".format(p, rel_type, qs))
                    count += 1
                    print(rel_type, count, all)
                except Exception as e:
                    print(e)
            else:
                for q in qs:
                    query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                    start_node, end_node, p, q, rel_type, rel_name) #关键代码关键代码关键代码！！！创建指定两点之间指定的关系

                    try:
                        self.g.run(query)   #pyneo方法
                        print("{}---{}---->{}".format(p, rel_type, q))
                        count += 1
                        print(rel_type, count, all)
                    except Exception as e:
                        print(e)

        # for edge in set(set_edges):     #去重主要是使用了set，set中的元素各不相同。
        #     edge = edge.split('###')    #还原
        #     p = edge[0]                 #p是起始点，如百日咳
        #     q = edge[1]                 #q是终点，  如清蒸鸡蛋羹
        #     query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
        #         start_node, end_node, p, q, rel_type, rel_name) #关键代码关键代码关键代码！！！创建指定两点之间指定的关系

        #     try:
        #         self.g.run(query)   #pyneo方法
        #         count += 1
        #         print(rel_type, count, all)
        #     except Exception as e:
        #         print(e)
        return
    
    def create_graphrels(self):
        brand_names,serise_names,scores,levels,structs ,EngineORbatterys,SpeedchunkORcharges,types,\
        prices,status,urls,rel_brand2serise, rel_brand2price, rel_brand2type, rel_brand2urls, rel_name2scores,\
        rel_serise2levels, rel_serise2struct, rel_serise2Engine, rel_serise2Chunk,\
        rel_serise2type, rel_serise2price, rel_serise2status, rel_serise2url, cars_info = self.read_nodes()

        self.create_relationship('brand_names', 'Car', rel_brand2serise, 'has_serises', '拥有车系')
        # self.create_relationship('brand_names', 'prices', rel_brand2price, 'brand_price', '汽车价格')
        # self.create_relationship('brand_names', 'types', rel_brand2type, 'brand_types', '类型')
        # self.create_relationship('brand_names', 'urls', rel_brand2urls, 'brand_url', '链接')


        self.create_relationship('Car', 'scores', rel_name2scores, 'serise_score', '评分')
        self.create_relationship('Car', 'levels', rel_serise2levels, 'serise_level', '级别')
        self.create_relationship('Car', 'structs', rel_serise2struct, 'serise_struct', '架构')
        self.create_relationship('Car', 'EngineORbatterys', rel_serise2Engine, 'serise_engine', '引擎OR续航')
        self.create_relationship('Car', 'SpeedchunkORcharges', rel_serise2Chunk, 'serise_chunk', '变速箱OR充电')
        self.create_relationship('Car', 'types', rel_serise2type, 'serise_type', '类型')
        self.create_relationship('Car', 'status', rel_serise2status, 'serise_status', '销售状态')
        self.create_relationship('Car', 'urls', rel_serise2url, 'serise_urls', '链接')
        


    def export_data(self):
        brand_names,serise_names,scores,levels,structs ,EngineORbatterys,SpeedchunkORcharges,types,\
        prices,status,urls,rel_brand2serise, rel_brand2price, rel_brand2type, rel_brand2urls, rel_name2scores,\
        rel_serise2levels, rel_serise2struct, rel_serise2Engine, rel_serise2Chunk,\
        rel_serise2type, rel_serise2price, rel_serise2status, rel_serise2url, cars_info = self.read_nodes()

        f_brand_names           = open('brand_names.txt', 'w+', encoding='utf-8')
        f_serise_names          = open('serise_names.txt', 'w+', encoding='utf-8')
        f_scores                = open('scores.txt', 'w+', encoding='utf-8')
        f_levels                = open('levels.txt', 'w+', encoding='utf-8')
        f_structs               = open('structs.txt', 'w+', encoding='utf-8')
        f_EngineORbatterys      = open('EngineORbatterys.txt', 'w+', encoding='utf-8')
        f_SpeedchunkORcharges   = open('SpeedchunkORcharges.txt', 'w+', encoding='utf-8')
        f_types                 = open('types.txt', 'w+', encoding='utf-8')
        f_prices                = open('prices.txt', 'w+', encoding='utf-8')
        f_status                = open('status.txt', 'w+', encoding='utf-8')
        f_urls                  = open('urls.txt', 'w+', encoding='utf-8')

        
        f_brand_names.write('\n'.join(list(brand_names)))
        f_serise_names.write('\n'.join(list(serise_names)))
        f_scores.write('\n'.join(list(scores)))
        f_levels.write('\n'.join(list(levels)))
        print(structs)
        f_structs.write('\n'.join(list(structs)))
        f_EngineORbatterys.write('\n'.join(list(EngineORbatterys)))
        f_SpeedchunkORcharges.write('\n'.join(list(EngineORbatterys)))
        f_types.write('\n'.join(list(types)))
        f_prices.write('\n'.join(list(prices)))
        f_status.write('\n'.join(list(status)))
        f_urls.write('\n'.join(list(urls)))

        f_brand_names.close()
        f_serise_names.close()
        f_scores.close()
        f_levels.close()
        f_structs.close()
        f_EngineORbatterys.close()
        f_types.close()
        f_prices.close()
        f_status.close()
        f_urls.close()
        return


if __name__ == '__main__':
    handler = CarGraph()
    handler.export_data()
    handler.create_graphnodes()
    handler.create_graphrels()   