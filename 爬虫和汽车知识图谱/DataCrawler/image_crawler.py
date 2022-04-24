#爬取汽车之家网站的汽车图片

import requests
from bs4 import BeautifulSoup
import os
import re



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

def get_urls(url_text):
    #读取图片页面所属的网页链接，返回列表。
    #可以根据网页链接爬取里面的图片，每一个车系都有一个链接，里面展示了车辆图片
    with open(url_text, "r", encoding='utf-8') as f:
        url_list = f.readlines()
    url_list = [item.replace('price', 'pic') for item in url_list]
    url_list = [item.replace('\n', '') for item in url_list]
    return url_list

def get_names(name_text):
    with open(name_text, "r", encoding='utf-8') as f:
        name_list = f.readlines()
    name_list = [re.sub('\(.*\)', '', item) for item in name_list]
    name_list = [item.replace('\n', '') for item in name_list]
    return name_list


url_list = get_urls("car_url.txt")
name_list = get_names("car_url_name.txt")

#将各个品牌下的所有车系的图片链接都保存，然后在一个一个访问，这样可以动态建立文件夹
for i in range(0, len(url_list)):
    base_dir = 'F:/汽车之家图像数据集'                      #顶级目录
    pic_brand_name = name_list[i]
    #创建品牌文件夹
    brand_dir = os.path.join(base_dir, pic_brand_name).replace('\\', '/')
    # print(brand_dir)
    if os.path.exists(brand_dir):
        pass
    else:
        os.makedirs(brand_dir)
        
    print('{} / {}  {}'.format(i+1, len(url_list), pic_brand_name))
    pic_url = url_list[i]
    contents = htmlparser(pic_url)
    soup = BeautifulSoup(contents,"html.parser")
    all_links = soup.find_all('a', title=re.compile('[\s\S]'))
    all_links = ['https://car.autohome.com.cn' + item.attrs.get("href", None).split('#')[0] for item in all_links]
    for link in all_links:
        content = htmlparser(link)
        soup = BeautifulSoup(content,"html.parser")

        pic_serise_name = soup.find('h2', class_='fn-left cartab-title-name').text
        #如果名称中有非法字符，则将其替换为_
        pic_serise_name = pic_serise_name.replace(':', ' ')
        pic_serise_name = pic_serise_name.replace('\n', ' ')
        pic_serise_name = pic_serise_name.strip()
        #创建车系目录，里面存放车辆图像
        base_serise_dir = brand_dir
        pic_serise_dir  = os.path.join(base_serise_dir, pic_serise_name).replace('\\', '/')

        if os.path.exists(pic_serise_dir):
            pass 
        else:
            os.makedirs(pic_serise_dir)

        boxs = soup.find_all('div', attrs={"class" :"uibox"})   #直接class_='uibox'返回元素为空,所以用attrs。实验时attrs和class_可以交替尝试
        for box in boxs:                                        #找到含有车身外观的div
            if (str(type(box.find('a', text='车身外观'))) == "<class 'bs4.element.Tag'>"):

                anchor_cars_url = 'https://car.autohome.com.cn' + box.find('a', text='更多>>')['href']

                count_info = box.find('span', class_='uibox-title-font12').text

                img_counts = eval(count_info.split('(')[1].split('张')[0])

                pages = int(img_counts / 60) + 1

                anchor_cars_url = anchor_cars_url.split('#')[0].split(".html")[0]
                # print(anchor_cars_url)
                count = 1
                for i in range(0, pages):
                    cars_url = anchor_cars_url + '-p{}'.format(i+1) + ".html"

                    img_contents = htmlparser(cars_url)
                    img_soup = BeautifulSoup(img_contents,"html.parser")
                    box = img_soup.find('div',attrs={"class" :"uibox-con carpic-list03 border-b-solid"})
                    if str(type(box)) == "<class 'bs4.element.Tag'>":
                        cars_img_urls = box.find_all('img')
                        if len(cars_img_urls) > 3:                                 #如果图片数量为3张，有两种可能。1.无车辆图片的3个图片提示  2.有3张真实车辆图片
                            for car_img_url in cars_img_urls:
                                car_url = 'https:' + car_img_url['src']
                                car_img = requests.get(car_url)
                                fpath = os.path.join(pic_serise_dir,'{}.jpg'.format(count)).replace('\\', '/')
                                count += 1
                                with open(fpath, 'wb+') as f:
                                    f.write(car_img.content)
