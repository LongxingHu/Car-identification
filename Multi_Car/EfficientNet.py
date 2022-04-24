import csv
from turtle import color
import pandas as pd

from torch.utils.data import Dataset, DataLoader
from torchvision import transforms  ##可方便指定各种transformer，直接传入DataLoader
from PIL import Image
from tqdm import tqdm
from efficientnet_pytorch import EfficientNet
from torch.autograd import Variable
import torch
from torch import nn, optim
from torchvision import models
from matplotlib import pyplot as plt
import pickle

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True



class MyDataset(Dataset):
    def __init__(self, record_path, is_train=True):
        # self.data = []
        self.is_train = is_train

        self.record = pd.read_csv(record_path)
        ## transforms.Normalize：对R G B三通道数据做均值方差归一化，因此给出下方三个均值和方差
        # normMean = [0.49139968, 0.48215827, 0.44653124]
        # normStd = [0.24703233, 0.24348505, 0.26158768]
        # normTransform = transforms.Normalize(normMean, normStd)

        self.trainTransform = transforms.Compose([       ## train训练集处理
            transforms.Resize(224),
            transforms.CenterCrop(224),
            transforms.RandomAffine(degrees=0, translate=(0.05, 0.05)),
            transforms.RandomHorizontalFlip(),           ## 以50%概率水平翻转
            transforms.ToTensor(),                       ## 转为Tensor形式
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])                                               
        ])

        ## 测试集的transforms数据处理
        self.testTransform = transforms.Compose([  
            transforms.Resize(224),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

     # 获取单条数据
    def __getitem__(self, index):
        img = self.trainTransform(Image.open(self.record.iloc[index, 0]).resize((224,224)).convert('RGB'))
        if not self.is_train:
            img = self.testTransform(Image.open(self.record.iloc[index, 0]).resize((224, 224)).convert('RGB'))
        label = self.record.iloc[index, 2]
        return img, label

    # 数据集长度
    def __len__(self):
        return self.record.shape[0]



def train_model(network, criterion, optimizer, trainLoader, valLoader, n_epochs = 200):
    network = network.cuda()
    criterion = criterion.cuda()
    accuracy_all_train = []
    accuracy_all_test  = []    
    for epoch in range(0, n_epochs):
        correct = 0.0
        cum_loss = 0.0
        counter = 0

        # Make a pass over the training data.
        t = tqdm(trainLoader, desc = 'Training epoch %d' % epoch)
        network.train()  # This is important to call before training!
        accuracy_current_train = []
        accuracy_current_test  = []
        for (i, (inputs, labels)) in enumerate(t):

            # Wrap inputs, and targets into torch.autograd.Variable types.
            inputs = Variable(inputs)
            labels = Variable(labels)
            
            inputs = inputs.cuda()
            labels = labels.cuda()

            # Forward pass:
            outputs = network(inputs)
            loss = criterion(outputs, labels)

            # Backward pass:
            optimizer.zero_grad()
            # Loss is a variable, and calling backward on a Variable will
            # compute all the gradients that lead to that Variable taking on its
            # current value.
            loss.backward() 

            # Weight and bias updates.
            optimizer.step()

            # logging information.
            cum_loss += loss.data.item()
            max_scores, max_labels = outputs.data.topk(5, dim=1)
            for j in range(5):
                correct += (max_labels[:,j] == labels.data).sum()
            counter += inputs.size(0)
            accuracy_current_train.append(100 * correct / counter)
            t.set_postfix(loss = cum_loss / (1 + i), accuracy = 100 * correct / counter)
            
            del inputs, labels

        accuracy_all_train.append(accuracy_current_train[-1])

        # Make a pass over the validation data.
        correct = 0.0
        cum_loss = 0.0
        counter = 0
        t = tqdm(valLoader, desc = 'Validation epoch %d' % epoch)
        network.eval()  # This is important to call before evaluating!
        with torch.no_grad():
            for (i, (inputs, labels)) in enumerate(t):

                # Wrap inputs, and targets into torch.autograd.Variable types.
                inputs = Variable(inputs)
                labels = Variable(labels)
            
                inputs = inputs.cuda()
                labels = labels.cuda()

                # Forward pass:
                outputs = network(inputs)
                loss = criterion(outputs, labels)

                # logging information.
                cum_loss += loss.data.item()
                max_scores, max_labels = outputs.data.topk(5, dim=1)
                for j in range(5):
                    correct += (max_labels[:,j] == labels.data).sum()
                counter += inputs.size(0)
                accuracy_current_test.append(100 * correct / counter)
                t.set_postfix(loss = cum_loss / (1 + i), accuracy = 100 * correct / counter)
            

                del inputs, labels
            if (epoch+1) % 100 == 0 and epoch != 0:     #每100个epoch保存一下
                torch.save(network, 'fine_tune/network_all_{}.pt'.format(epoch+1))        
            accuracy_all_test.append(accuracy_current_test[-1])

    
    ### plot
    plt.xlabel("epochs")
    plt.ylabel("accuracy")
    plt.plot(range(1, n_epochs+1), accuracy_all_train, color='red')
    plt.show()

    plt.xlabel("epochs")
    plt.ylabel("accuracy")
    plt.plot(range(1, n_epochs+1), accuracy_all_test, color='blue')
    plt.show()


def main():
    train_data = MyDataset("./train.csv")
    test_data = MyDataset("./test.csv", is_train=False)
    trainLoader = DataLoader(dataset=train_data,batch_size=8,shuffle=True)
    testLoader = DataLoader(dataset=test_data,batch_size=8,shuffle=False)

    trainset = trainLoader.dataset
    valset =testLoader.dataset
    print('%d training samples' % len(trainset))
    print('%d validation samples' % len(valset))

    data_info = pd.read_csv('train.csv')
    num_class = len(set(data_info['class_num']))


    # vgg16 = models.vgg16(pretrained = True)
    # for param in vgg16.parameters():
    #     param.requires_grad = False     #特征层中参数都固定住，不会发生梯度的更新
        
    # vgg16.classifier = nn.Sequential(   #重写vgg16的全连接分类层
    #     nn.Linear(25088, 4096), 
    #     nn.ReLU(), 
    #     nn.Dropout(0.5),
    #     nn.Linear(4096, 4096),
    #     nn.ReLU(), 
    #     nn.Dropout(0.5),
    #     nn.Linear(4096, num_class)
    # )

    model = EfficientNet.from_pretrained('efficientnet-b8', advprop=True)
    in_feature = model._fc.in_features
    #model._fc =  nn.Sequential(   #重写efficientNet-b8的全连接分类层
    #        nn.Linear(in_feature, 4096), 
    #        nn.ReLU(), 
    #        nn.Dropout(0.5),
    #        nn.Linear(4096, 4096),
    #        nn.ReLU(), 
    #        nn.Dropout(0.5),
    #        nn.Linear(4096, num_class)
    #)
    model._fc = nn.Linear(in_feature, num_class)
    
    optimizer = optim.SGD(model.parameters(), lr = 0.0001, momentum = 0.9, weight_decay=0.0004)
    criterion = nn.CrossEntropyLoss()

    print('finished initializing network')

    train_model(model, criterion, optimizer, trainLoader, testLoader, n_epochs=200)
    # torch.save(network, 'fine_tune/network20.pt')


if __name__ == '__main__': main()
