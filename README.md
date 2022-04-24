# 车辆识别

## 仓库结构
本仓库三个文件夹分别包含Django网页搭建代码、模型训练代码、数据爬取和知识图谱构建代码

### 爬虫和汽车知识图谱
对应数据爬取以及知识图谱的创建，锚点网站是汽车之家，读者可以在我代码之上对目标网站进行更加灵活的数据收集，也可以直接使用我已经爬取的数据集。
整个汽车数据集清洗后包含 155 种汽车品牌，900 种车系，共计55945 张车辆图像。对于文本数据，共收集了 284 种品牌的车辆信息，共计2058种车系信息。
图像数据集链接：https://pan.baidu.com/s/19GranwVhkFazVChGA0aPhA?pwd=6666 
文本数据集链接：https://pan.baidu.com/s/1HmIZccWgZz69SbnuQDMhZQ?pwd=6666

准备好数据集后，使用文本数据集构建汽车知识图谱以及搭建一个简单的汽车问答系统。在KgCars文件夹中运行Build_Graph.py文件创建知识图谱。你需要预先准备好neo4j环境并在该文件修改自己的neo4j平台账号和密码。之后直接运行chatbot_grapg.py便可！

### Multi_Car
该文件夹对应模型的训练，本次实验使用EfficientNetB8对汽车图像数据集进行迁移学习。经过100个epoch的训练。模型Top1识别准确率为94.33737%, Top5识别准确率为99.3033%，模型较为优秀。训练好的模型放在fine_tune文件夹下。读者可以尝试在其它数据集例如ImageNet上训练模型，不过这样的话你需要另外制作DataLoader惹！
该文件夹的执行顺序为：
1. gen_csv.py用来生成图像在主机上的路径以及标签等其它信息。生成的csv为img_info.csv。
2. 为了保证所有的图像数据在传输过程中都没有损坏，运行handle.py，如果显示出路径，则表明文件损坏，需要在指定路径下删除文件，然后再使用gen_csv.py重新生成csv。
3. 仅在第一次训练模型之前运行，test.py可以根据img_info.csv将数据集分割为训练数据和测试数据。
4. 运行EfficientNet.py便可开始训练模型，读者可以自己设置一些超参。

注意：本文提供训练好的模型，在RTX-2080显卡上训练100个epoch需要运行约50小时。模型链接：https://pan.baidu.com/s/1GF42Bt7rPbI8olXCZqc_3A?pwd=6666。需要将下载好的模型放在CarReco-->CarReco-->predict-->views.py上修改模型路径，这样网页可以正常预加载训练好的模型。另外model_test.py能够测试Top1和top5的识别准确率。

top1_acc:
![image](https://github.com/Fanzweig/Car-identification/blob/main/images/top1.png)
top1_acc:
![image](https://github.com/Fanzweig/Car-identification/blob/main/images/top5.png)
### CarReco
该文件夹代码实现了一个使用Django搭建的算法网页展示。
业务逻辑：用户在前端html页面上传一张图像，后台会接收该文件并保存在项目目录结构中predict--->static--->img--->show.jpg上，然后使用训练好的模型对其进行预测，网页左侧返回Top5的预测结果。知识图谱在在其中扮演什么角色？答：丰富返回信息。利用预测的Top1结果，在知识图谱中自动生成Cypher语句(默认是查询车系的综合信息：包括品牌、价格、引擎类型、用户评分等)，然后结果返回网页右侧。

运行步骤：在CarReco根目录下运行:

```python
python manage.py runserver
```

网页展示如下：
![image](https://github.com/Fanzweig/Car-identification/blob/main/images/web_show1.jpg)
![image](https://github.com/Fanzweig/Car-identification/blob/main/images/web_show2.jpg)



