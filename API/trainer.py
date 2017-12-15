import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
import time
from datetime import timedelta
import data_helper
import numpy as np
%matplotlib inline
import matplotlib.pyplot as plt
import random

# Convolutional layer 1
filter_size_1 = 3
num_filters_1 = 32

# Convolutional layer 2
filter_size_2 = 3
num_filters_2 = 64

# Convolutional layer 3
filter_size_3 = 3
num_filters_3 = 64

# Fully connected layer
fc_size = 128   # Number of neurons in fully connected layer

# Number of color channels in an image
num_channels = 3    #RGB

# Image dimensions
img_size = 32

# Size of image after flattening to a single dimension
img_size_flat = img_size * img_size * num_channels

# Tuple with height and width of images used to reshape arrays.
img_shape = (img_size, img_size)

# Class info
classes = ['black_bishop', 'black_king', 'black_knight', 'black_pawn', 'black_queen', 'black_rook', 'blank', \
'white_bishop', 'white_king', 'white_knight', 'white_pawn', 'white_queen', 'white_rook']
num_classes = len(classes)

# Batch size
batch_size = 4

# Validation split
validation_size = .2

# How long to wait after validation loss stops improving before terminating training
early_stopping = None  # using None because I don't want to implement early stoping

train_path = 'train_data'
test_path = 'test_data'

data = data_helper.read_training_sets(train_path, img_size, classes, validation_size = validation_size)
test_images, test_ids = data_helper.read_testing_set(test_path, img_size, classes)

print("Size of:")
print("- Training-set:\t\t{}".format(len(data.train.labels)))
print("- Test-set:\t\t{}".format(len(test_images)))
print("- Validation-set:\t{}".format(len(data.valid.labels)))


def new_weights(shape):
    return tf.Variable(tf.truncated_normal(shape, stddev = 0.05)) # Standard Deviation = 0.05

def new_biases(length):
    return tf.Variable(tf.constant(0.05, shape = [length]))


def new_conv_layer(input,              # The previous layer
               num_input_channels,     # Number of channels in previous layer
               filter_size,            # Width and height of each filter
               num_filters,            # Number of filters
               use_pooling = True):    # Use 2x2 max-pooling

    shape = [filter_size, filter_size, num_input_channels, num_filters]
    weights = new_weights(shape = shape)
    biases = new_biases(length = num_filters)
    layer = tf.nn.conv2d(input = input, filter = weights, strides=[1, 1, 1, 1], padding = 'SAME')
    layer += biases

    if use_pooling:
        layer = tf.nn.max_pool(value = layer,
                               ksize = [1, 2, 2, 1],       # Size of max-pooling window (2x2)
                               strides = [1, 2, 2, 1],     # stride on a single image (2x2)
                               padding = 'SAME')

    layer = tf.nn.relu(layer)
    return layer, weights


def flatten_layer(layer):

    layer_shape = layer.get_shape()
    num_features = layer_shape[1:4].num_elements()
    layer_flat = tf.reshape(layer, [-1, num_features])
    return layer_flat, num_features

def new_fc_layer(input,             # The previous layer
                 num_inputs,        # Number of inputs from previous layer
                 num_outputs,       # Number of outputs
                 use_relu = True):  # Use Rectified Linear Unit (ReLU)?

    weights = new_weights(shape = [num_inputs, num_outputs])
    biases = new_biases(length = num_outputs)

    layer = tf.matmul(input, weights) + biases

    if use_relu:
        layer = tf.nn.relu(layer)

    return layer

session = tf.Session()

x = tf.placeholder(tf.float32, shape = [None, img_size_flat], name = 'x')
x_image = tf.reshape(x, [-1, img_size, img_size, num_channels])

y_true = tf.placeholder(tf.float32, shape = [None, num_classes], name = 'y_true')
y_true_cls = tf.argmax(y_true, dimension = 1) # Returns the index with the largest value across axis of a tensor


layer_conv1, weights_conv1 = \
new_conv_layer(input = x_image,
               num_input_channels = num_channels,
               filter_size = filter_size_1,
               num_filters = num_filters_1,
               use_pooling = True)

layer_conv2, weights_conv2 = \
new_conv_layer(input = layer_conv1,
               num_input_channels = num_filters_1,
               filter_size = filter_size_2,
               num_filters = num_filters_2,
               use_pooling = True)

layer_conv3, weights_conv3 = \
new_conv_layer(input = layer_conv2,
               num_input_channels = num_filters_2,
               filter_size = filter_size_3,
               num_filters = num_filters_3,
               use_pooling = True)

layer_flat, num_features = flatten_layer(layer_conv3)

layer_fc1 = new_fc_layer(input = layer_flat,
                         num_inputs = num_features,
                         num_outputs = fc_size,
                         use_relu = True)

layer_fc2 = new_fc_layer(input = layer_fc1,
                         num_inputs = fc_size,
                         num_outputs = num_classes,
                         use_relu = False)

y_pred = tf.nn.softmax(layer_fc2, name = 'y_pred')
y_pred_cls = tf.argmax(y_pred, dimension = 1)

cross_entropy = tf.nn.softmax_cross_entropy_with_logits(logits = layer_fc2, labels = y_true)
cost = tf.reduce_mean(cross_entropy)

optimizer = tf.train.AdamOptimizer(learning_rate = 1e-4).minimize(cost)
correct_prediction = tf.equal(y_pred_cls, y_true_cls)
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

session = tf.Session()
session.run(tf.global_variables_initializer())

train_batch_size = batch_size

def print_progress(epoch, feed_dict_train, feed_dict_validate, val_loss):
    acc = session.run(accuracy, feed_dict = feed_dict_train)
    val_acc = session.run(accuracy, feed_dict = feed_dict_validate)
    msg = "Epoch {0} --- Training Accuracy: {1:>6.1%}, Validation Accuracy: {2:>6.1%}, Validation Loss: {3:.3f}"
    print(msg.format(epoch + 1, acc, val_acc, val_loss))

# Counter for total number of iterations performed so far.
total_iterations = 0

def optimize(num_iterations):

    global total_iterations
    start_time = time.time()

    best_val_loss = float("inf")
    patience = 0

    for i in range(total_iterations,
                   total_iterations + num_iterations):

        x_batch, y_true_batch, _, cls_batch = data.train.next_batch(train_batch_size)
        x_valid_batch, y_valid_batch, _, valid_cls_batch = data.valid.next_batch(train_batch_size)
        x_batch = x_batch.reshape(train_batch_size, img_size_flat)
        x_valid_batch = x_valid_batch.reshape(train_batch_size, img_size_flat)
        feed_dict_train = {x: x_batch, y_true: y_true_batch}
        feed_dict_validate = {x: x_valid_batch, y_true: y_valid_batch}
        session.run(optimizer, feed_dict = feed_dict_train)
        if i % int(data.train.num_examples/batch_size) == 0:
            val_loss = session.run(cost, feed_dict = feed_dict_validate)
            epoch = int(i / int(data.train.num_examples / batch_size))
            print_progress(epoch, feed_dict_train, feed_dict_validate, val_loss)

            if early_stopping:
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    patience = 0
                else:
                    patience += 1

                if patience == early_stopping:
                    break

    saver = tf.train.Saver()
    if not os.path.exists("trained_model"):
        os.makedirs("trained_model")
    saver.save(session, 'trained_model/trained_model',global_step = 15000)

    total_iterations += num_iterations
    end_time = time.time()
    time_dif = end_time - start_time
    print("Time elapsed: " + str(timedelta(seconds=int(round(time_dif)))))


def plot_images(images, cls_true, cls_pred = None):

    if len(images) == 0:
        print("no images to show")
        return
    else:
        random_indices = random.sample(range(len(images)), min(len(images), 9))

    images, cls_true  = zip(*[(images[i], cls_true[i]) for i in random_indices])
    fig, axes = plt.subplots(3, 3)
    fig.subplots_adjust(hspace=5, wspace=5)

    for i, ax in enumerate(axes.flat):
        ax.imshow(images[i].reshape(img_size, img_size, num_channels))
        if cls_pred is None:
            xlabel = "True: {0}".format(cls_true[i])
        else:
            xlabel = "True: {0}, Pred: {1}".format(cls_true[i], cls_pred[i])
        ax.set_xlabel(xlabel)
        ax.set_xticks([])
        ax.set_yticks([])
    plt.show()


def plot_example_errors(cls_pred, correct):
    incorrect = (correct == False)
    images = data.valid.images[incorrect]
    cls_pred = cls_pred[incorrect]
    cls_true = data.valid.cls[incorrect]
    plot_images(images = images[0:4],
                cls_true = cls_true[0:4],
                cls_pred = cls_pred[0:4])

def print_validation_accuracy(show_example_errors = False):

    num_test = len(data.valid.images)
    cls_pred = np.zeros(shape = num_test, dtype = np.int)
    i = 0

    while i < num_test:
        j = min(i + batch_size, num_test)
        images = data.valid.images[i:j, :].reshape(batch_size, img_size_flat)
        labels = data.valid.labels[i:j, :]
        feed_dict = {x: images, y_true: labels}
        cls_pred[i:j] = session.run(y_pred_cls, feed_dict = feed_dict)
        i = j

    cls_true = np.array(data.valid.cls)
    cls_pred = np.array([classes[x] for x in cls_pred])
    correct = (cls_true == cls_pred)
    correct_sum = correct.sum()
    acc = float(correct_sum) / num_test
    msg = "Accuracy on Test-Set: {0:.1%} ({1} / {2})"
    print(msg.format(acc, correct_sum, num_test))
    if show_example_errors:
        print("Example errors:")
        plot_example_errors(cls_pred = cls_pred, correct = correct)



optimize(num_iterations = 15000)
print_validation_accuracy(show_example_errors = False)
