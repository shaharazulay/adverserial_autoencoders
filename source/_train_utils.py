import torch
from torch.autograd import Variable
import numpy as np

cuda = torch.cuda.is_available()


def predict_labels(Q, X):
    Q.eval()

    latent_y = Q(X)[0]
    pred_labels = torch.argmax(latent_y, dim=1)
    return pred_labels

def sample_categorical(batch_size, n_classes=10):
    '''
     Sample from a categorical distribution
     of size batch_size and # of classes n_classes
     return: torch.autograd.Variable with the sample
    '''
    cat = np.random.randint(0, 10, batch_size)
    cat = np.eye(n_classes)[cat].astype('float32')
    cat = torch.from_numpy(cat)
    return Variable(cat)

def report_loss(epoch, D_loss_cat, D_loss_gauss, G_loss, recon_loss):
    '''
    Print loss
    '''
    print('Epoch-{}; D_loss_cat: {:.4}; D_loss_gauss: '
          '{:.4}; G_loss: {:.4}; recon_loss: {:.4}'.format(
            epoch,
            D_loss_cat.item(),
            D_loss_gauss.item(),
            G_loss.item(),
            recon_loss.item()))

def classification_accuracy(Q, data_loader):
    correct = 0
    N = len(data_loader.dataset)

    for batch_idx, (X, target) in enumerate(data_loader):

        X.resize_(data_loader.batch_size, Q.input_size)
        X, target = Variable(X), Variable(target)
        if cuda:
            X, target = X.cuda(), target.cuda()

        # encoding phase
        pred = predict_labels(Q, X)
        correct += pred.eq(target.data).cpu().sum()

    return 100. * correct / N


def zero_grad_all(*models):
    [m.zero_grad() for m in models]

def train_all(*models):
    [m.train() for m in models]

def eval_all(*models):
    [m.eval() for m in models]

# def create_latent(Q, X):
#     '''
#     Creates the latent representation for the samples in loader
#     return:
#         z_values: numpy array with the latent representations
#         labels: the labels corresponding to the latent representations
#     '''
#     Q.eval()
#     labels = []
#
#         X, target = Variable(X), Variable(target)
#         labels.extend(target.data.tolist())
#         if cuda:
#             X, target = X.cuda(), target.cuda()
#         # Reconstruction phase
#         z_sample = Q(X)
#         if batch_idx > 0:
#             z_values = np.concatenate((z_values, np.array(z_sample.data.tolist())))
#         else:
#             z_values = np.array(z_sample.data.tolist())
#     labels = np.array(labels)
#
#     return z_values, labels

# def get_categorical(labels, n_classes=10):
#     cat = np.array(labels.data.tolist())
#     cat = np.eye(n_classes)[cat].astype('float32')
#     cat = torch.from_numpy(cat)

#     return Variable(cat)