class QuestionPaser:

    '''构建实体节点'''
    def build_entitydict(self, args):
        entity_dict = {}
        for arg, types in args.items():
            for type in types:
                if type not in entity_dict:
                    entity_dict[type] = [arg]
                else:
                    entity_dict[type].append(arg)

        return entity_dict

    '''解析主函数'''
    def parser_main(self, res_classify):
        args = res_classify['args']
        entity_dict = self.build_entitydict(args)
        question_types = res_classify['question_types'] #列表
        sqls = []   #最终要返回的cql语句
        for question_type in question_types:
            sql_ = {}
            sql_['question_type'] = question_type
            sql = []
            if question_type == 'evaluation':
                sql = self.sql_transfer(question_type, entity_dict.get('serise'))

            elif question_type == 'link':
                sql = self.sql_transfer(question_type, entity_dict.get('serise'))

            elif question_type == 'price':
                sql = self.sql_transfer(question_type, entity_dict.get('serise'))

            elif question_type == 'find_serise':
                sql = self.sql_transfer(question_type, entity_dict.get('brand'))

            elif question_type == 'find_type':
                sql = self.sql_transfer(question_type, entity_dict.get('serise'))

            elif question_type == 'find_battery':
                sql = self.sql_transfer(question_type, entity_dict.get('serise'))

            if sql:
                sql_['sql'] = sql

                sqls.append(sql_)

        return sqls

    '''针对不同的问题，分开进行处理'''
    def sql_transfer(self, question_type, entities):
        if not entities:
            return []

        # 查询语句
        sql = []
        # 查询综合评估(总体信息)
        if question_type == 'evaluation':
            sql = ["MATCH (m:Car) where m.name = '{0}' return  m.name, m.brand_name, m.score, m.level, m.struct,\
                  m.EngineORbattery, m.SpeedchunkORcharge, m.type, m.price, m.status, m.url".format(i) for i in entities]

        # 查找链接
        elif question_type == 'link':
            sql = ["MATCH (m:Car) where m.name = '{0}' return m.name, m.url".format(i) for i in entities]

        # 查询车系的价格
        elif question_type == 'price':
            sql = ["MATCH (m:Car) where m.name = '{0}' return m.name, m.price".format(i) for i in entities]

        # 查询车系
        elif question_type == 'find_serise':
            sql = ["MATCH (m:brand_names)-[r:has_serises]->(n:Car) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

        #查询车系的类型(新能源OR燃油汽车)
        elif question_type == 'find_type':
            sql = ["MATCH (m:Car) where m.name = '{0}' return m.name, m.type".format(i) for i in entities]
        
        #查询车系的引擎或电池
        elif question_type == 'find_battery':
            sql = ["MATCH (m:Car) where m.name = '{0}' return m.name, m.EngineORbattery, m.SpeedchunkORcharge".format(i) for i in entities]
            
        return sql


if __name__ == '__main__':
    handler = QuestionPaser()
