import pandas as pd
import os
### generate some train and test csv, every train csv includes 75 class 
car_infos = pd.read_csv("img_info.csv")
car_groups = car_infos.groupby('class_name')
car_infos_list = list(car_groups)

pds = [pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()]

off = 75
pds_2 = []
for i, pd_ in enumerate(pds):
    print(i)
    for j in range(off*i, 75+off*i):
        pd_ = pd.concat([pd_, car_infos_list[j][1]], axis=0)
    pds_2.append(pd_)

for i, pd_ in enumerate(pds_2):
    pd_.to_csv("img_info{}.csv".format(i+1),index=False, encoding='utf-8_sig')


for i in range(1, 13):
    data_info = pd.read_csv("img_info{}.csv".format(i))
    groups = data_info.groupby('class_name')

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
    train_pd.to_csv("train{}.csv".format(i), index=False, encoding='utf-8_sig')
    test_pd.to_csv("test{}.csv".format(i), index=False, encoding='utf-8_sig')
    
