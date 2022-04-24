from predict.question_classifier import *
from predict.question_parser import *
from predict.answer_search import *

'''问答类'''
class ChatBotGraph:
    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionPaser()
        self.searcher = AnswerSearcher()

    def chat_main(self, sent):
        answer = '数据库找不到了...'
        res_classify = self.classifier.classify(sent)   #使用pyahocorasick在数上完成KMP模式串匹配，得到关键字所属的类别
        if not res_classify:
            return answer
        res_sql = self.parser.parser_main(res_classify)
        final_answers = self.searcher.search_main(res_sql)
        if not final_answers:
            return answer
        else:
            return '\n'.join(final_answers)

if __name__ == '__main__':
    handler = ChatBotGraph()
    while 1:
        question = input('咨询:')
        answer = handler.chat_main(question)
        print('魔法小星:', answer)

