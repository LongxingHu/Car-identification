from statistics import mode
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings
from django import forms
from predict.chatbot_graph import ChatBotGraph

import os


###图像分类所需的库
import csv
from PIL import Image
import torch
from torchvision import transforms  ##可方便指定各种transformer，直接传入DataLoader
from torch import nn, optim
from torch.nn import functional as F
import pandas as pd

### 加载本地与预训练权重文件
torch.cuda.empty_cache()
model = torch.load(os.path.join(settings.STATIC_ROOT, 'checkpoints', 'network_all_100.pt'))
model.cuda()

###设置超参
criterion = nn.CrossEntropyLoss()
criterion = criterion.cuda()


testTransform = transforms.Compose([  
            transforms.Resize(224),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

###将csv文件读进来进行名称银映射
data_info = pd.read_csv(os.path.join(settings.STATIC_ROOT, 'checkpoints', 'img_info.csv'))
class_list = list(data_info['class_num'])


File_path = ""


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()

def save_back_file(f):
    filename = f.name
    filename = 'show.jpg'
    # save_path = '%s\%s' % (settings.MEDIA_ROOT, filename)
    save_path = os.path.join(settings.STATIC_ROOT, 'img', filename)
    print(save_path)
    with open(save_path, 'wb') as file:
        for chunk in f.chunks():
            file.write(chunk)
    return save_path


def upload_file(request):
    global FILE_PATH
    print("hello upload!")
    predictings = []
    if 'input_file' in request.session:
        FILE_PATH = request.session['input_file']

    predict_filename = None
    messages.get_messages(request)
    if request.method == 'POST':
        if request.FILES.get('img') is not None:
            file = request.FILES.get('img')
            filename = file.name
            print(filename)
            FILE_PATH = save_back_file(file)
            print(FILE_PATH)
            request.session['input_file'] = FILE_PATH

            ###在这里预测----------
            predict(FILE_PATH)
            messages.add_message(request, messages.SUCCESS, "文件上传成功")
        else:
            messages.add_message(request, messages.WARNING, "文件上传失败")

    else:
        pass

    return render(request, 'upload_file.html',locals())

def index(request):
    global FILE_PATH
    print("hello index!")

    if 'input_file' in request.session:
        FILE_PATH = request.session['input_file']
    # else:
    #    FILE_PATH = None
    predict_filename = None
    messages.get_messages(request)
    if request.method == 'POST':
        if 'input_file' in request.POST:
            if request.FILES.get('img') is not None:
                file = request.FILES.get('img')
                filename = file.name
                print(filename)
                FILE_PATH = save_back_file(file)
                print(FILE_PATH)
                request.session['input_file'] = FILE_PATH
                messages.add_message(request, messages.SUCCESS, "文件上传成功")
            else:
                messages.add_message(request, messages.WARNING, "文件上传失败")

    else:
        pass




    return render(request, 'index.html', locals())


def predict(img_path):
    img = testTransform(Image.open(img_path).resize((224,224)).convert('RGB'))
    inputs=torch.unsqueeze(img.cuda(), dim=0)
    outputs = F.softmax(model(inputs))
    max_scores, max_labels = outputs.data.topk(5, dim=1)
    print((max_scores, max_labels))

    predict_class = "类别\n"
    predict_conf  = "置信度\n"
    car_series = ""
    f_class = open(os.path.join(settings.STATIC_ROOT, 'txt', 'predict_class.html').replace('\\', '/'), 'w', encoding='utf-8')
    f_conf  = open(os.path.join(settings.STATIC_ROOT, 'txt', 'predict_conf.html').replace('\\', '/'), 'w', encoding='utf-8')

    # for j in range(5):                    ###这种循环查找时间过长，舍弃。
    #     for i in range(data_info.shape[0]):
    #         if data_info.iloc[i, 2] == max_labels[0][j].item():
    #             predict_class += "{}\n".format(data_info.iloc[i, 1])  
    #             predict_conf  += "{:.3f}\n".format(max_scores[0][j].item(), 2)
    #             break

    for j in range(5):
        class_index = class_list.index(max_labels[0][j].item())
        predict_class += "{}\n".format(data_info.iloc[class_index, 1])
        predict_conf  += "{:.3f}\n".format(max_scores[0][j].item(), 2)

    # for i in range(data_info.shape[0]):
    #         if data_info.iloc[i, 2] == max_labels[0][0].item():
    #             car_series = data_info.iloc[i, 1]
    #             break

    car_series = data_info.iloc[class_list.index(max_labels[0][0].item()), 1]

    predict_class = "<!DOCTYPE html>\n<html><head><meta charset='UTF-8'><body><div style='color:white'>{}</div></body>".format(predict_class)
    predict_class = predict_class.replace('\n', '<br/>')
    predict_conf  = "<!DOCTYPE html>\n<html><head><meta charset='UTF-8'><body><div style='color:white'>{}</div></body>".format(predict_conf)
    predict_conf  = predict_conf.replace('\n', '<br/>')
    
    f_class.write(predict_class)
    f_class.close()

    f_conf.write(predict_conf)
    f_conf.close()


    # car_serise = 'Stelvio'      #默认展示车系
    car_ques   = car_series + "如何"  #默认问题
    print(car_ques)
    handler = ChatBotGraph()
    answer = handler.chat_main(car_ques)

    #将答案保存，刷新之后直接显示txt文件中的内容
    f = open(os.path.join(settings.STATIC_ROOT, 'txt', 'answer.html').replace('\\', '/'), 'w', encoding='utf-8')
    
    answer = "<!DOCTYPE html>\n<html><head><meta charset='UTF-8'><body><div style='color:white'>{}</div></body>".format(answer)
    answer = answer.replace('\n', '<br/>').replace("price/", "price/<br/>")
    f.write(answer)
    f.close()


    ### 将预测结果保留