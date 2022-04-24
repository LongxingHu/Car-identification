from py2neo import Graph

class AnswerSearcher:
    def __init__(self):
        self.g = Graph("http://localhost:7474", auth=("neo4j", "hulongxing223223"))
        self.num_limit = 20

    '''执行cypher查询，并返回相应结果'''
    def search_main(self, sqls):    #sqls是一个字典，有question_type，sql两个key,sql对应的value是一个列表，存的是一些问题
        final_answers = []
        for sql_ in sqls:
            question_type = sql_['question_type']
            queries = sql_['sql']
            answers = []
            for query in queries:
                ress = self.g.run(query).data()
                answers += ress
            final_answer = self.answer_prettify(question_type, answers) #answers是一个列表
            if final_answer:
                final_answers.append(final_answer)
        return final_answers    #返回列表

    '''根据对应的qustion_type，调用相应的回复模板'''
    def answer_prettify(self, question_type, answers):
        final_answer = []
        if not answers:
            return ''
        if question_type == 'evaluation':           ###需要调试
            desc = [[i['m.name'], i['m.brand_name'], i['m.score'], i['m.level'], i['m.struct'], i['m.EngineORbattery'],\
             i['m.SpeedchunkORcharge'], i['m.type'], i['m.price'], i['m.url']] for i in answers]
            subject = answers[0]['m.name']

            final_answer = '{0}的大致信息如下：\n车系：{1}\n品牌：{2}\n评分：{3}\n级别：{4}\n架构：{5}\n发动机OR续航：{6}\n变速箱OR充电时间：{7}\n新能源OR燃油：{8}\n价格：{9}\n链接{10}\n'.format(\
                subject, desc[0][0], desc[0][1], desc[0][2], desc[0][3], desc[0][4],\
                         desc[0][5], desc[0][6], desc[0][7], desc[0][8], desc[0][9])
        elif question_type == 'link':
            desc = [i['m.url'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的链接为：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'price':
            desc = [i['m.price'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的大致价格为{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'find_serise':
            final_answer = ''               #为了满足同时询问多个品牌的车系
            current_subject = ''
            for answer in answers:
                desc = answer['n.name']
                subject = answer['m.name']
                if subject != current_subject:
                    final_answer += '\n{}有如下车系：\n'.format(subject)
                    current_subject = subject
                final_answer += '{}；'.format(desc)
        
        elif question_type == 'find_type':
            desc = [i['m.type'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的类型为：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'find_battery':
            desc = [i['m.SpeedchunkORcharge'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}治疗可能持续的周期为：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        return final_answer


if __name__ == '__main__':
    searcher = AnswerSearcher()