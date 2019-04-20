import os
import numpy as np
from collections import Counter
import torch
from torch.autograd import Variable
import torch.nn.functional as F

import matplotlib
from matplotlib import gridspec
import matplotlib.pyplot as plt

from ._train_utils import predict_labels

cuda = torch.cuda.is_available()


def show_samples_of_classes_and_reconstructions(Q, P, valid_loader, n_classes, z_dim, output_dir):
    batch_size = valid_loader.batch_size
    n = len(valid_loader)
    selected_batch_id = np.random.randint(0, n - 1)
    
    labels = []

    for batch_id, (X, y) in enumerate(valid_loader):
        if batch_id == selected_batch_id:
            X.resize_(batch_size, Q.input_size)

            X, y = Variable(X), Variable(y)
            if cuda:
                X, y = X.cuda(), y.cuda()

            show_sample_from_each_class(Q, P, X, n_classes, z_dim, output_dir)
            show_reconstruction(Q, P, X, output_dir)
            return


def show_reconstruction(Q, P, X, output_dir):
    Q.eval()
    P.eval()

    latent_y, latent_z = Q(X)

    latent_vec = torch.cat((latent_y, latent_z), 1)
    X_rec = P(latent_vec)

    img_orig = np.array(X[0].data.tolist()).reshape(28, 28)
    img_rec = np.array(X_rec[0].data.tolist()).reshape(28, 28)
    
    plt.figure()
    plt.subplot(1, 2, 1)
    plt.imshow(img_orig, cmap='gray')
    plt.subplot(1, 2, 2)
    plt.imshow(img_rec, cmap='gray')
    plt.title('predicted label: %s' % torch.argmax(latent_y, dim=1)[0])
    plt.savefig(os.path.join(output_dir, 'reconstruction_example.png'))

def show_sample_from_each_class(Q, P, X, n_classes, z_dim, output_dir):

    Q.eval()

    latent_y, latent_z = Q(X)
    y_class = torch.argmax(latent_y, dim=1).cpu().numpy()

    fig, ax = plt.subplots(nrows=n_classes, ncols=9)

    X_samples = {}
    for label in range(n_classes):
        label_indices = np.where(y_class == label)
        try:
            X_samples[label] = X[label_indices][:8, :]  # take first 8 images
        except:
            X_samples[label] = None

    for label in range(n_classes):
        latent_y = np.eye(n_classes)[label].astype('float32')
        latent_y = torch.from_numpy(latent_y)
        latent_y = Variable(latent_y).reshape(1, n_classes)

        latent_z = Variable(torch.zeros(1, z_dim))


    for i, row in zip(range(n_classes), ax):
        for j, col in zip(range(9), row):
            if j == 0:  # first column shows the "mode" of the labels generated by the latent space
                latent_y = np.eye(n_classes)[i].astype('float32')
                latent_y = torch.from_numpy(latent_y)
                latent_y = Variable(latent_y).reshape(1, n_classes)

                latent_z = Variable(torch.zeros(1, z_dim))

                latent_vec = torch.cat((latent_y, latent_z), 1)
                X_mode_rec = P(latent_vec)

                mode_img = np.array(X_mode_rec.data.tolist()).reshape(28, 28)
                col.axis('off')
                col.imshow(mode_img, cmap='gray')

            else:  # show actual images predicted to be part of the current label
                col.axis('off')
                try:
                    img = X_samples[i][j]
                    img = np.array(img.data.tolist()).reshape(28, 28)
                    col.imshow(img, cmap='gray')
                except:
                    col.imshow(np.zeros((28, 28)), cmap='gray')

    plt.suptitle('Representative mode & samples from each possible label')
    plt.savefig(os.path.join(output_dir, 'modes_and_samples_from_each_label.png'))


def plot_latent_distribution(Q, valid_loader, output_dir):
    batch_size = valid_loader.batch_size
    labels = []

    _, (X, y) = next(enumerate(valid_loader))  # take first batch
    X.resize_(batch_size, Q.input_size)

    X, y = Variable(X), Variable(y)
    if cuda:
        X, y = X.cuda(), y.cuda()

    latent_y, latent_z = Q(X)

    y_highest_prob = []
    for latent_y_vec in latent_y:
        sorted_p = latent_y_vec.sort(descending=True)[0].detach().cpu().numpy()
        y_highest_prob.append(sorted_p[0])

    plt.figure()
    plt.hist(y_highest_prob, bins=15)
    plt.title('distribution of highest "probability" given by the latent y vector')
    plt.savefig(os.path.join(output_dir, 'y_distribution.png'))

    plt.figure()
    plt.hist(latent_z.detach().cpu().numpy()[:, 0])
    plt.title('distribution of the first element of the latent z vector')
    plt.savefig(os.path.join(output_dir, 'z_distribution.png'))


def plot_predicted_label_distribution(Q, valid_loader, n_classes, output_dir):
    batch_size = valid_loader.batch_size
    labels = []

    for _, (X, y) in enumerate(valid_loader):

        X.resize_(batch_size, Q.input_size)

        X, y = Variable(X), Variable(y)
        if cuda:
            X, y = X.cuda(), y.cuda()

        y_pred = predict_labels(Q, X)
        latent_y, latent_z = Q(X)

        labels.extend(y_pred.cpu().numpy())

    plt.figure()
    plt.title('distribution of the predicted labels')
    plt.hist(labels, bins=n_classes)
    plt.savefig(os.path.join(output_dir, 'predicted_label_distribution.png'))

    return Counter(labels)


def show_learned_latent_features(P, n_classes, z_dim, output_dir):

    subplot_ind = 1
    plt.figure()
    
    for label in range(n_classes):
        latent_y = np.eye(n_classes)[label].astype('float32')
        latent_y = torch.from_numpy(latent_y)
        latent_y = Variable(latent_y).reshape(1, n_classes)

        for j, z0 in zip(range(10), torch.linspace(-1, 1, 10)):
            latent_z = Variable(torch.zeros(1, z_dim))
            # scan over z0 values in-order
            latent_z[0, 0] = z0

            latent_vec = torch.cat((latent_y, latent_z), 1)
            X_mode_rec = P(latent_vec)

            mode_img = np.array(X_mode_rec.data.tolist()).reshape(28, 28)
            plt.subplot(n_classes, 10, subplot_ind)
            plt.imshow(mode_img, cmap='gray')
            plt.axis('off')
            subplot_ind += 1

    plt.suptitle('latent feature impact of decoded image')
    plt.savefig(os.path.join(output_dir, 'learned_latent_features.png'))

def show_all_learned_modes(P_mode_decoder, n_classes, output_dir):

    for label in range(n_classes):
        latent_y = np.eye(n_classes)[label].astype('float32')
        latent_y = torch.from_numpy(latent_y)
        latent_y = Variable(latent_y)

        X_mode_rec = P_mode_decoder(latent_y)
        mode_img = np.array(X_mode_rec.data.tolist()).reshape(28, 28)
        plt.subplot(1, n_classes, label + 1)
        plt.imshow(mode_img, cmap='gray')
        plt.title(label)
        plt.axis('off')

    plt.suptitle('learned modes')
    plt.savefig(os.path.join(output_dir, 'learned_modes.png'))


def unsupervised_accuracy_score(Q, valid_loader, n_classes):
    batch_size = valid_loader.batch_size
    labels = []

    true_to_pred = {}
    pred_to_true = {}

    for _, (X, y) in enumerate(valid_loader):

        X.resize_(batch_size, Q.input_size)

        X, y = Variable(X), Variable(y)
        if cuda:
            X, y = X.cuda(), y.cuda()

        y_pred = predict_labels(Q, X)

        for y_true, y_hat in zip(y, y_pred):
            true_to_pred.setdefault(y_true.item(), {})
            true_to_pred[y_true.item()].setdefault(y_hat.item(), 0)
            true_to_pred[y_true.item()][y_hat.item()] += 1

            pred_to_true.setdefault(y_hat.item(), {})
            pred_to_true[y_hat.item()].setdefault(y_true.item(), 0)
            pred_to_true[y_hat.item()][y_true.item()] += 1

    for y_true in range(10):  # true classes are always 0-10
        n_samples = sum(true_to_pred[y_true].values())
        best_match_label = max(true_to_pred[y_true], key=true_to_pred[y_true].get)
        n_highest_match = true_to_pred[y_true][best_match_label]
        print("Label {}: {}%, Best matching label; {}".format(y_true, 100.0 * n_highest_match / n_samples, best_match_label))


    correct = 0
    wrong = 0
    label_mapping = {}
    for y_hat in range(n_classes):
        try:
            label_mapping[y_hat] = max(pred_to_true[y_hat], key=pred_to_true[y_hat].get)
            correct += pred_to_true[y_hat][label_mapping[y_hat]]
            wrong += sum([v for  k, v in pred_to_true[y_hat].items() if k != label_mapping[y_hat]])
        except Exception as e:
            print(e)
            print("label %s is never predicted" % y_hat)

    print("ACCURACY: %.2f%%" % (float(correct) / (wrong + correct)))

    print(label_mapping)
    print(pred_to_true)
    return true_to_pred

def highest_loss_digit(Q, P, valid_loader):
    batch_size = valid_loader.batch_size
    
    weights_per_label = {}
    for batch_num, (X, target) in enumerate(valid_loader):

        X.resize_(batch_size, Q.input_size)
        X, target = Variable(X), Variable(target)
        if cuda:
            X, target = X.cuda(), target.cuda()

        latent_vec = torch.cat(Q(X), 1)
        X_rec = P(latent_vec)
        
        for x, x_rec, y_true in zip(X, X_rec, target):
            # Reconstruction loss
            loss = F.binary_cross_entropy(x_rec, x)

            weights_per_label.setdefault(y_true.item(), 0)
            weights_per_label[y_true.item()] += loss.item()
            
    highest_weight_label = max(weights_per_label, key=weights_per_label.get)
    print("\nhighest label weights is the digit {}".format(highest_weight_label))
    print(weights_per_label)
