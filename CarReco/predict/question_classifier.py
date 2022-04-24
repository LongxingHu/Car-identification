import os
from re import S
import ahocorasick  
from django.conf import settings
class QuestionClassifier:
    def __init__(self):
        # cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        cur_dir = settings.STATIC_ROOT
        
        #　特征词路径
        self.brand_name_path = os.path.join(cur_dir, 'dict/brand_names.txt')
        self.serise_name_path = os.path.join(cur_dir, 'dict/serise_names.txt')
        self.scores_path = os.path.join(cur_dir, 'dict/scores.txt')
        self.levels_path = os.path.join(cur_dir, 'dict/levels.txt')
        self.structs_path = os.path.join(cur_dir, 'dict/structs.txt')
        self.EngineORbatterys_path = os.path.join(cur_dir, 'dict/EngineORbatterys.txt')
        self.SpeedchunkORcharges_path = os.path.join(cur_dir, 'dict/SpeedchunkORcharges.txt')
        self.types_path = os.path.join(cur_dir, 'dict/types.txt')
        self.prices_path = os.path.join(cur_dir, 'dict/prices.txt')
        self.status_path = os.path.join(cur_dir, 'dict/status.txt')
        self.urls_path = os.path.join(cur_dir, 'dict/urls.txt')
        # 加载特征词
        self.brand_name_wds= [i.strip() for i in open(self.brand_name_path,encoding="utf-8") if i.strip()]#encoding="utf-8"
        self.serise_name_wds= [i.strip() for i in open(self.serise_name_path,encoding="utf-8") if i.strip()]
        self.scores_wds= [i.strip() for i in open(self.scores_path,encoding="utf-8") if i.strip()]
        self.levels_wds= [i.strip() for i in open(self.levels_path,encoding="utf-8") if i.strip()]
        self.structs_wds= [i.strip() for i in open(self.structs_path,encoding="utf-8") if i.strip()]
        self.EngineORbatterys_wds= [i.strip() for i in open(self.EngineORbatterys_path,encoding="utf-8") if i.strip()]
        self.SpeedchunkORcharges_wds= [i.strip() for i in open(self.SpeedchunkORcharges_path,encoding="utf-8") if i.strip()]
        self.types_wds= [i.strip() for i in open(self.types_path,encoding="utf-8") if i.strip()]
        self.prices_wds= [i.strip() for i in open(self.prices_path,encoding="utf-8") if i.strip()]
        self.status_wds= [i.strip() for i in open(self.status_path,encoding="utf-8") if i.strip()]
        self.urls_wds= [i.strip() for i in open(self.urls_path,encoding="utf-8") if i.strip()]


        self.region_words = set(
                self.brand_name_wds + self.serise_name_wds + self.scores_wds + self.levels_wds + self.structs_wds + self.EngineORbatterys_wds +\
                self.SpeedchunkORcharges_wds + self.types_wds + self.prices_wds + self.status_wds + self.urls_wds
            )
        # 构造领域actree
        self.region_tree = self.build_actree(list(self.region_words))
        # 构建词典
        self.wdtype_dict = self.build_wdtype_dict()
        # 问句疑问词

        self.eval_qwds = ['怎么样', '如何', '好吗', '介绍', '性价比', '信息']
        self.link_qwds = ['链接', '网页', '网站']
        self.price_qwds = ['多少钱', '价格', '贵吗', '买']
        self.brand2serise_qwds = ['有哪些', '车系', '种类', '信息', '怎么样']
        self.type_qwds = ['电动', '新能源', '油', '燃油', '汽油', '烧油']
        self.battery_qwds = ['续航','电池', '充电', '电', '电量', '跑多久', '多久', '跑', '发动机', '引擎', '马力', '动力', ]   #要先进行汽车类型判断

        print('model init finished ......')

        return

    '''分类主函数'''
    def classify(self, question):
        data = {}
        car_dict = self.check_car(question)
        if not car_dict:
            return {}
        data['args'] = car_dict
        #收集问句当中所涉及到的实体类型
        types = []
        for type_ in car_dict.values():
            types += type_
        question_type = 'others'

        question_types = []
        # 评价奥迪A4L
        if self.check_words(self.eval_qwds, question) and ('serise' in types):
            question_type = 'evaluation'
            question_types.append(question_type)

        # 链接
        if self.check_words(self.link_qwds, question) and ('serise' in types):
            question_type = 'link'
            question_types.append(question_type)

        # 价格
        if self.check_words(self.price_qwds, question) and ('serise' in types):
            question_type = 'price'
            question_types.append(question_type)
            
        # 查找车系
        if self.check_words(self.brand2serise_qwds, question) and ('brand' in types):
            question_type = 'find_serise'
            question_types.append(question_type)

        # 查找类型
        if self.check_words(self.type_qwds, question) and 'serise' in types:
            question_type = 'find_type'
            question_types.append(question_type)

        #循环续航和充电时间
        if self.check_words(self.battery_qwds, question) and 'serise' in types:
            question_type = 'find_battery'
            question_types.append(question_type)

        # 将多个分类结果进行合并处理，组装成一个字典
        data['question_types'] = question_types

        return data

    '''构造词对应的类型'''
    def build_wdtype_dict(self):
        wd_dict = dict()
        for wd in self.region_words:
            wd_dict[wd] = []
            if wd in self.brand_name_wds:
                wd_dict[wd].append('brand')
            if wd in self.serise_name_wds:
                wd_dict[wd].append('serise')
            if wd in self.scores_wds:
                wd_dict[wd].append('scores')
            if wd in self.levels_wds:
                wd_dict[wd].append('level')
            if wd in self.structs_wds:
                wd_dict[wd].append('struct')   
            if wd in self.EngineORbatterys_wds:
                wd_dict[wd].append('EngineORbettery')
            if wd in self.SpeedchunkORcharges_wds:
                wd_dict[wd].append('ChunkORcharge')
            if wd in self.types_wds:
                wd_dict[wd].append('type')
            if wd in self.prices_wds:
                wd_dict[wd].append('price')
            if wd in self.status_wds:
                wd_dict[wd].append('status')
            if wd in self.urls_wds:
                wd_dict[wd].append('url')
        return wd_dict


    '''构造actree, 加速过滤'''
    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    '''问句过滤'''
    def check_car(self, question):
        region_wds = []
        for i in self.region_tree.iter(question):
            wd = i[1][1]
            region_wds.append(wd)
        stop_wds = []
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:
                    stop_wds.append(wd1)
        final_wds = [i for i in region_wds if i not in stop_wds]
        final_dict = {i:self.wdtype_dict.get(i) for i in final_wds}

        return final_dict

    '''基于特征词进行分类'''
    def check_words(self, wds, sent):
        """
        wds:待匹配的关键字
        sent:传进来的问句
        """
        for wd in wds:
            if wd in sent:
                return True
        return False


if __name__ == '__main__':
    handler = QuestionClassifier()
    while 1:
        question = input('input an question:')
        data = handler.classify(question)
        print(data)