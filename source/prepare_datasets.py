import numpy as np
import torch
from torchvision import datasets

from _data_utils import MNISTSlice, default_transform


trainset_original = datasets.MNIST(
    '../data', train=True, download=True, transform=default_transform)

train_label_index = []
valid_label_index = []
for i in range(10):
    train_label_list = trainset_original.train_labels.numpy()
    label_index = np.where(train_label_list == i)[0]
    label_subindex = list(label_index[:300])
    valid_subindex = list(label_index[300: 1000 + 300])
    train_label_index += label_subindex
    valid_label_index += valid_subindex

trainset_np = trainset_original.train_data.numpy()
trainset_label_np = trainset_original.train_labels.numpy()
train_data_sub = torch.from_numpy(trainset_np[train_label_index])
train_labels_sub = torch.from_numpy(trainset_label_np[train_label_index])

trainset_new = MNISTSlice(
    root='./../data', data=train_data_sub, labels=train_labels_sub, train=True)
# trainset_new.train_data = train_data_sub.clone()
# trainset_new.train_labels = train_labels_sub.clone()

trainset_new.dump("./../data/train_labeled.p")
#pickle.dump(trainset_new, open("./../data/train_labeled.p", "wb"))

validset_np = trainset_original.train_data.numpy()
validset_label_np = trainset_original.train_labels.numpy()
valid_data_sub = torch.from_numpy(validset_np[valid_label_index])
valid_labels_sub = torch.from_numpy(validset_label_np[valid_label_index])

validset = MNISTSlice(
    root='./../data', data=valid_data_sub, labels=valid_labels_sub, train=False)
# validset.test_data = valid_data_sub.clone()
# validset.test_labels = valid_labels_sub.clone()

validset.dump("./../data/validation.p")
# pickle.dump(validset, open("./../data/validation.p", "wb"))

train_unlabel_index = []
for i in range(60000):
    if i in train_label_index or i in valid_label_index:
        pass
    else:
        train_unlabel_index.append(i)

trainset_np = trainset_original.train_data.numpy()
trainset_label_np = trainset_original.train_labels.numpy()
train_data_sub_unl = torch.from_numpy(trainset_np[train_unlabel_index])
#train_labels_sub_unl = torch.from_numpy(trainset_label_np[train_unlabel_index])
train_labels_sub_unl = torch.from_numpy(np.array([-1] * len(train_unlabel_index)))
trainset_new_unl = MNISTSlice(
    root='./../data', data=train_data_sub_unl, labels=train_labels_sub_unl, train=True)
# trainset_new_unl.train_data = train_data_sub_unl.clone()
# trainset_new_unl.train_labels = None      # Unlabeled

trainset_new_unl.dump("./../data/train_unlabeled.p")

#pickle.dump(trainset_new_unl, open("./../data/train_unlabeled.p", "wb"))
