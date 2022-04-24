#coding==utf-8
import requests
from bs4 import BeautifulSoup
import os
import re
import json
import random
import time
import csv


def htmlparser(url):#解析网页的函数
    ua = "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)"
    user_agent = ua
    headers = {'User-agent': user_agent,
               'Referer': 'https://car.autohome.com.cn.html',}#加上header伪装成浏览器防止被封
    r = requests.get(url, headers=headers)#get请求
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    content = r.text
    return content

def get_all_urls(url):
    #汽车之家url中只是在售状态的汽车，而即将在售和停售状态的汽车是以此url为锚点的
    """
    example:  在售url:  https://car.autohome.com.cn/price/brand-33.html
        则即将在售url:  https://car.autohome.com.cn/price/brand-33-0-2-1.html
              停售url:  https://car.autohome.com.cn/price/brand-33-0-3-1.html
    """
    anchor = url.split('/')[-1].split('.')[0]  #brand-33
    to_be_sold_url = url.replace(anchor, anchor+'-0-2-1')
    stop_saling = url.replace(anchor, anchor+'-0-3-1')
    #返回在售，即将在售和停售的url
    return  stop_saling, url, to_be_sold_url

def get_brand(url):
    """
    获取车辆的品牌
    """
    contents = htmlparser(url)
    soup = BeautifulSoup(contents,"html.parser")
    car_brand = soup.find("h2",class_= "fn-left name")
    return car_brand.text


def get_serise_info(url):
    contents = htmlparser(url)
    soup = BeautifulSoup(contents,"html.parser")

    #获取车系名称
    serise_names = []
    car_names_soup = soup.find_all("div",class_= "main-title")
    for car_name in car_names_soup:
        serise_names.append(car_name.find('a').text)

    #获取不同车系的URL
    car_list_soup = soup.find_all("div",class_= "list-cont")
    serise_urls = []
    for car_list in car_list_soup:
        serise_urls.append('https://car.autohome.com.cn'+car_list.find('a')['href'])
    
    #获取不同车系的用户评分
    car_score_soup = soup.find_all("div",class_= "score-cont")
    serise_votes = []
    for car_score in car_score_soup:
        serise_votes.append(car_score.text.split('：')[-1])

    #获取不同车系的级别、车身结构、发动机 变速箱、类型(新能源OR传统)
    serise_levels, serise_structs, serise_engineORbattery, serise_speedchunkORcharge, car_types = [], [], [], [], []
    car_level_soup = soup.find_all("div",class_= "main-lever-left")
    for car_level in car_level_soup:
        all_info = car_level.find_all('li')
        serise_levels.append(all_info[0].text.split("：")[-1])
        serise_structs.append(all_info[1].text.split("：")[-1])
        serise_engineORbattery.append(all_info[2].text.split("：")[-1])
        serise_speedchunkORcharge.append(all_info[3].text.split("：")[-1])   
        # print(all_info[3].text.split("：")[0])
        if all_info[3].text.split("：")[0] == "充电时间":
            car_types.append("新能源")
        else:
            car_types.append("燃油汽车")
            
    #获取指导价
    serise_prices = []
    car_level_soup = soup.find_all("span",class_= "lever-price red")
    for car_level in car_level_soup:
        serise_prices.append(car_level.text)
    

    
    return serise_names, serise_urls, serise_votes, serise_levels, serise_structs, serise_engineORbattery, serise_speedchunkORcharge, serise_prices, car_types


def get_all(url_text):

    with open(url_text, "r") as f:
        url_list = f.readlines()
    
    url_list = [item.replace('\n', '') for item in url_list]
    cars_item = []
    for k, url in enumerate(url_list):
        print("{} / {}".format(k+1, len(url_list)))
        #得到三种销售状态的url页面
        urls = get_all_urls(url)
        status = ['停售', '在售', '即将销售']
        car_item = []
        
        for i, url in enumerate(urls):
            #查找车系信息，页面中有名称、链接、级别、车身结构、发动机 变速箱 指导价 类型
            serise_names, serise_urls, serise_votes, serise_levels, serise_structs, serise_engineORbattery, serise_speedchunkORcharge, serise_prices, car_types = get_serise_info(url)
            for j in range(len(serise_urls)):
                serise_info = {}
                serise_info['brand_name'] = get_brand(url)   #加上品牌名称
                serise_info['serise_name'] = serise_names[j]
                serise_info['score'] = serise_votes[j]
                serise_info['level'] = serise_levels[j]
                serise_info['struct'] = serise_structs[j]
                serise_info['EngineORbattery'] = serise_engineORbattery[j]
                serise_info['SpeedchunkORcharge'] = serise_speedchunkORcharge[j]
                serise_info['type'] = car_types[j]
                serise_info['price'] = serise_prices[j]
                serise_info['status'] = status[i]
                serise_info['url'] = serise_urls[j]
                #如果发现在售状态和停售状态冲突,只保留停售
                flag = 0
                for car in car_item:
                    if car['serise_name'] == serise_info['serise_name']:
                        flag = 1

                if flag == 0:
                    car_item.append(serise_info)
        cars_item.append(car_item)
    #cars_item:[[{}, {}, {}, ..., {}], [{}, {}, {}, ..., {}], [...], [...], [...], ..., [...]]
    return cars_item

def save_to_csv(cars_list):
    with open("all_cars.csv", 'w', newline='', encoding='utf-8')  as csvfile1:
        #级别、车身结构、发动机 变速箱、类型(新能源OR传统)
        header = ['brand_name','serise_name', 'score', 'level', 'struct', 'EngineORbattery', 'SpeedchunkORcharge', 'type', 'price', 'status', 'url']
        writer = csv.DictWriter(csvfile1,fieldnames=header) # 提前预览列名，当下面代码写入数据时，会将其一一对应。
        writer.writeheader()  # 写入列名
        for car in cars_list:
            writer.writerows(car) # 写入数据
    csvfile1.close()

cars_list = get_all("car_url.txt")
save_to_csv(cars_list)