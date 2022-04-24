import os
import csv
import pandas as pd

### 制作DataLoader之前需要记录图片文件的位置和类别

#记录所有图片文件对应的类别

base_dir = '/home/yuxc/bishe/hlx/HomeCars2/'
brand_names = os.listdir(base_dir)
path_list, class_num_list, class_name_list = [], [], []
for j, brand_name in enumerate(brand_names):
    print("{}   /   {}".format(j, len(brand_names)))
    brand_path = os.path.join(base_dir, brand_name)
    serise_names = os.listdir(brand_path)
    for serise_name in serise_names:
        serise_path = os.path.join(brand_path, serise_name)
        img_names = os.listdir(serise_path)
        if len(img_names) >= 8:      #只保留图片数量大于8的类别，数据太小不好训练
            for img_name in img_names:
                img_path = os.path.join(serise_path, img_name)
                path_list.append(img_path)
                class_num_list.append(serise_name)
                class_name_list.append(serise_name)

#将根据列表创建DataFrame
df = pd.DataFrame({'path':path_list, 'class_name':class_name_list, 'class_num':class_num_list})

#需要对class_num这一列使用LabelEncoder，因为训练过程需要的是数字类别
from sklearn.preprocessing import LabelEncoder
labelencoder_X = LabelEncoder()
df['class_num'] = labelencoder_X.fit_transform(df['class_num'])

#保存文件
df.to_csv("img_info.csv",index=False, encoding='utf-8_sig') #直接使用utf-8输出的csv是不带BOM的，excel不支持(中文乱码)，但是Notepad++支持。使用utf-8_sig两者支持


### 分割数据集
#读取csv文件
data_info = pd.read_csv("img_info.csv")
# train = data_info.sample(frac=0.7)
# data_info   = data_info.reset_index()   #重置index，因为上面已经打乱了
# test = data_info[~data_info.index.isin(train.index)]

# #对每一类图像都要划分，而不是总体进行划分(这样有些类别可能只训练了或者只测试了)

# #先对DataFram使用GroupBy来分组，每个组都是一类图片的信息集合
groups = df.groupby(data_info.class_name)

train_pd = pd.DataFrame()
test_pd  = pd.DataFrame()

for group in groups:
    #group是一个tuple，第一个元素是分类依据也就是class_name，第二列是dataframe
    group = group[1]
    train_group = group.sample(frac=0.7)

    test_group  = group[~group.index.isin(train_group.index)]
    # print("train group: {}".format(train_group))
    # print("test  group: {}".format(test_group))
    train_pd = pd.concat([train_pd, train_group], axis=0)
    test_pd  = pd.concat([test_pd, test_group], axis=0)

train_pd = train_pd.reset_index(drop=True)
test_pd  = test_pd.reset_index(drop=True)

"""
(train_pd.shape, test_pd.shape, data_info.shape)

((39150, 3), (16795, 3), (55945, 3))

len(set(data_info['class_num']))
3877 也就是3877分类
"""

train_pd.to_csv("train.csv", index=False, encoding='utf-8_sig')
test_pd.to_csv("test.csv", index=False, encoding='utf-8_sig')


