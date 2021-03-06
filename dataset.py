from PIL import Image
import os
import os.path
import numpy as np
import pickle
from torchvision.datasets import VisionDataset
from torchvision.datasets.utils import check_integrity, download_and_extract_archive
from pathlib import Path
#For Some reason the indexes always go up to 12 times the amount in the image bank

class datasetClass(VisionDataset):
    """
    Based on pytorch's cifar10 class
    """
    base_folder = 'Data'
    filename = "cifar-10-python.tar.gz"
    tgz_md5 = 'c58f30108f718f92721af3b95e74349a'

    shape = (32,32)



    # train_list = [['one.pickle','c99cafc152244af753f735de768cd75f']]
    train_list = [
        ['one.pickle', 'c99cafc152244af753f735de768cd75f']#,
        # ['two.pickle', 'd4bba439e000b95fd0a9bffe97cbabec'],
        # ['three.pickle', '54ebc095f3ab1f0389bbae665268c751'],
        # ['four.pickle', '634d18415352ddfa80567beed471001a'],
        # ['five.pickle', '482c414d41f54cd18b22e5b47cb7c3cb'],
    ]
    test_list = [
        ['test.pickle', '40351d587109b95175f43aff81a1287e'],
    ]
    meta = {
        'filename': 'batches.meta',
        'key': 'label_names',
        'md5': '5ff9c542aee3614f3951f8cda6e48888',
    }
   
    
    def __init__(self, root, train=True, transform=None, target_transform=None,
                 download=False,inputVersion = False):
        print("hello")
        super(datasetClass, self).__init__(root, transform=transform,
                                      target_transform=target_transform)

        self.train = train  # training set or test set

        if download:
            self.download()

        if not self._check_integrity():
            raise RuntimeError('Dataset not found or corrupted.' +
                               ' You can use download=True to download it')

        if self.train:
            downloaded_list = self.train_list
        else:
            downloaded_list = self.test_list

        self.data = []
        self.targets = []
        mod_path = Path(__file__).parent
        # now load the picked numpy arrays
        if inputVersion == True:
            #This setting only adds the test.pickle labels and data

            file_path = (mod_path / "Data/test.pickle").resolve()
            with open(file_path, 'rb') as f:
                entry = pickle.load(f, encoding='latin1')
                self.data.append(entry['image'])
                if 'ground' in entry:
                    self.targets.extend(entry['ground'])
                else:
                    self.targets.extend(entry['fine_labels'])

        else:
            for file_name, checksum in downloaded_list:
                file_path = (mod_path / "Data" / file_name).resolve()

                with open(file_path, 'rb') as f:
                    entry = pickle.load(f, encoding='latin1')
                    self.data.append(entry['image'])
                    if 'ground' in entry:
                        self.targets.extend(entry['ground'])
                    else:
                        self.targets.extend(entry['fine_labels'])

        #vstack changes the length
        self.data = np.vstack(self.data)
        #reshape changes the length
        self.data = self.data.reshape(-1, 1, datasetClass.shape[0], datasetClass.shape[1])
        # print("data shape")
        # print(self.data.shape)

        self.data = self.data.transpose((0, 2, 3, 1))  # convert to 
        # print(self.data.shape)




        self._load_meta()

    def _load_meta(self):
        path = os.path.join(self.root, self.base_folder, self.meta['filename'])
        if check_integrity(path, self.meta['md5']): #usually a "not" in between the if and check_integrity
            raise RuntimeError('Dataset metadata file not found or corrupted.' +
                               ' You can use download=True to download it')
        #possibly might need to add md5 verification :(
        # with open(path, 'rb') as infile:
        #     data = pickle.load(infile, encoding='latin1')
        #     self.classes = data[self.meta['key']]
        # self.class_to_idx = {_class: i for i, _class in enumerate(self.classes)}

    def __getitem__(self, index):
        # print("hello")

        img, target = self.data[index], self.targets[index]
        # print(img.shape)
        img = Image.fromarray(img.reshape(datasetClass.shape), 'L')

        if self.transform is not None:
            img = self.transform(img)

        if self.target_transform is not None:
            target = self.target_transform(target)

        return img, target
        # doing this so that it is consistent with all other datasets
        # to return a PIL Image
        """
        Args:
            index (int): Index
        Returns:
            tuple: (image, target) where target is index of the target class.
       """
    def __len__(self):
        return len(self.data)

    def _check_integrity(self):
        root = self.root
        for fentry in (self.train_list + self.test_list):
            filename, md5 = fentry[0], fentry[1]
            fpath = os.path.join(root, self.base_folder, filename)
            if not check_integrity(fpath, md5):
                #Add this later not really needed because I know the data is not malicious.
                return True # supposed to be false
        return True

    def download(self):
        if self._check_integrity():
            print('Files already downloaded and verified')
            return
        #figure this out late what exactly this does and if it is needed
        # download_and_extract_archive(self.url, self.root, filename=self.filename, md5=self.tgz_md5)

    def extra_repr(self):
        return "Split: {}".format("Train" if self.train is True else "Test")

