#有的图像是jpg格式，但是读取不了（下载时丢失了信息)，所以需要在训练之前都读取一遍，以防在训练时报错前功尽弃
from torchvision import transforms  ##可方便指定各种transformer，直接传入DataLoader
from PIL import Image
import pandas as pd

imgs_info = pd.read_csv("img_info.csv")
# index_max = max(list())
# Image.open(self.record.iloc[index, 0])
for index in range(0, imgs_info.shape[0]):
    try:
        img = Image.open(imgs_info.iloc[index, 0])
    except:
        print("{}".format(imgs_info.iloc[index, 0]))    #打印不能读取的图片路径，将其删除，再运行gen_csv重新生成索引文件

print("OVER!")
