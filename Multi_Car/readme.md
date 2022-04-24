运行顺序

1. gen_csv.py  生成图片索引文件以制作Dataloader，如下所示：

![image-20220418111550906](https://s2.loli.net/2022/04/18/4A7dfIGwoBRSmnj.png)



2. handle.py 查看是否有错误图片，注意看代码注释
3. EfficientNet.py 开始训练 训练的模型保存在fine-tune文件夹下
4. model_test.py 测试模型acc