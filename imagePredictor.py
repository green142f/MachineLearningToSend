import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision
from torchvision import datasets, transforms, utils
from dataset import datasetClass
from pathlib import Path
import numpy as np
import os
import os.path
import pickle
from settingReader import settingReader
import matplotlib.pyplot as plt


class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv_layer = nn.Sequential(
            # Conv Layer block 1
            nn.Conv2d(in_channels=1, out_channels=64, kernel_size=(4,4), padding=1), #used to be 4 by 4
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=(4,4), padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),

            # Conv Layer block 2
            nn.Conv2d(in_channels=128, out_channels=256, kernel_size=(4,4), padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.Conv2d(in_channels=256, out_channels=512, kernel_size=(4,4), padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout2d(p=0.05),

            # Conv Layer block 3
            nn.Conv2d(in_channels=512, out_channels=512, kernel_size=(4,4), padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(),
            nn.Conv2d(in_channels=512, out_channels=512, kernel_size=(4,4), padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        self.fc_layer = nn.Sequential(
            nn.Dropout(p=0.1),
            nn.Linear(2048, 1024), #used to be 18432, 3072
            nn.ReLU(),
            nn.Linear(1024, 512), #used to be 3072, 1024
            nn.ReLU(),
            nn.Linear(512, 256),  #used to be 1024, 512
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(256, 20),#usded to be 512,20
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(20, 5),#usded to be 512,20
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(5, 3)#usded to be 512,20
        )

    def forward(self, x):
        if torch.cuda.is_available():
           x = x.to(device="cuda")
        # conv layers
        x = self.conv_layer(x)
        # print(x.size(-4))
        # print(x.size(-3))
        # print(x.size(-2))
        # print(x.size(-1))
        # print(x.size(0))
        # print(x.size(1))
        # print(x.size(2))
        # print(x.size(3))
        # flatten
        x = x.view(x.size(0), -1)


        # fc layer
        x = self.fc_layer(x)

        return x
mod_path = Path(__file__).parent
path = (mod_path / "path.pth").resolve()


model = CNN()
model.load_state_dict(torch.load(path))
model.eval()
data = []
file_path = (mod_path / "Data" / "test.pickle")
with open(file_path, 'rb') as f:
    entry = pickle.load(f, encoding='latin1')
    data.append(entry['data'])
    # if 'labels' in entry:
    #     self.targets.extend(entry['labels'])
    # else:
    #     self.targets.extend(entry['fine_labels'])

data = np.vstack(data)
data = data.reshape(-1,1,32,32)
data = data.transpose((0,2,3,1))
test_batch_size = 1
numberOfPics = data.shape[0]

transform = transforms.Compose([transforms.ToTensor()])
images = datasetClass(root='./data', train=False,download=True, transform=transform, inputVersion = True)
val_loader = torch.utils.data.DataLoader(images, batch_size=test_batch_size, shuffle=False)
criterion = nn.CrossEntropyLoss()
classNames = settingReader().getItem("classNames")
def test(model, test_loader):
    model.eval()
    with torch.no_grad():
        count = 0
        for data, target in test_loader:
            count+=1
            if count > 16:
                break
            
            plt.imshow(data.squeeze(),cmap = "gray")
            plt.show()
            # print(target)
            output = model(data)
            _, pred = output.max(1)
            data = data.numpy().squeeze()
            # data = data.transpose((1,2,0))
            sp = plt.subplot(4, 4, count)
            sp.axis("Off")
            plt.imshow(data, cmap = "gray")
            print(pred[0])
            sp.set_title(classNames[pred[0]-1])
            plt.tight_layout()
            
        plt.show()
            
            
    
test(model,val_loader)