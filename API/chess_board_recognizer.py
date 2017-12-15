import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
import numpy as np

import PIL.Image
from io import BytesIO
from IPython.display import clear_output, Image, display
import scipy.ndimage as nd
import scipy.signal


def display_array(a, format='jpeg', rng=[0, 1]):
    a = (a - rng[0]) / float(rng[1] - rng[0]) * 255
    a = np.uint8(np.clip(a, 0, 255))
    file = BytesIO()
    PIL.Image.fromarray(a).save(file, format)
    display(Image(data=file.getvalue()))

def ImageName(str):
    img_file = str

def make_kernel(a):
    """Transform a 2D array into a convolution kernel"""
    a = np.asarray(a)
    a = a.reshape(list(a.shape) + [1, 1])
    return tf.constant(a, dtype=1)


def simple_conv(x, k):
    """A simplified 2D convolution operation"""
    x = tf.expand_dims(tf.expand_dims(x, 0), -1)
    y = tf.nn.depthwise_conv2d(x, k, [1, 1, 1, 1], padding='SAME')
    return y[0, :, :, 0]


def gradientx(x):
    """Compute the x gradient of an array"""
    gradient_x = make_kernel([[-1., 0., 1.],
                              [-1., 0., 1.],
                              [-1., 0., 1.]])
    return simple_conv(x, gradient_x)


def gradienty(x):
    """Compute the x gradient of an array"""
    gradient_y = make_kernel([[-1., -1, -1], [0., 0, 0], [1., 1, 1]])
    return simple_conv(x, gradient_y)


def corners(x):
    """Find chess square corners in an array"""
    chess_corner = make_kernel([[-1., 0, 1], [0., 0., 0.], [1., 0, -1]])
    return simple_conv(x, chess_corner)


def dilate(x, size=3):
    """Dilate"""
    kernel = make_kernel(np.ones([size, size], dtype=np.float32))
    return tf.clip_by_value(simple_conv(x, kernel),
                            np.float32(1),
                            np.float32(2)) - np.float32(1)


def erode(x, size=3):
    """Erode"""
    kernel = make_kernel(np.ones([size, size]))
    return tf.clip_by_value(simple_conv(x, kernel),
                            np.float32(size * size - 1),
                            np.float32(size * size)) - np.float32(size * size - 1)


def opening(x, size=3):
    return dilate(erode(x, size), size)


def closing(x, size=3):
    return erode(dilate(x, size), size)


def skeleton(x, size=3):
    """Skeletonize"""
    return tf.clip_by_value(erode(x) - opening(erode(x)),
                            0.,
                            1.)

def checkMatch(lineset):
    """Checks whether there exists 7 lines of consistent increasing order in set of lines"""
    linediff = np.diff(lineset)
    x = 0
    cnt = 0
    for line in linediff:
        if np.abs(line - x) < 5:
            cnt += 1
        else:
            cnt = 0
            x = line
    return cnt == 5


def pruneLines(lineset):
    """Prunes a set of lines to 7 in consistent increasing order (chessboard)"""
    linediff = np.diff(lineset)
    x = 0
    cnt = 0
    start_pos = 0
    for i, line in enumerate(linediff):
        if np.abs(line - x) < 5:
            cnt += 1
            if cnt == 5:
                end_pos = i + 2
                return lineset[start_pos:end_pos]
        else:
            cnt = 0
            x = line
            print (i, x)
            start_pos = i
    return lineset


def skeletonize_1d(arr):
    """return skeletonized 1d array (thin to single value, favor to the right)"""
    _arr = arr.copy()
    for i in range(_arr.size - 1):
        if arr[i] <= _arr[i + 1]:
            _arr[i] = 0
    for i in np.arange(_arr.size - 1, 0, -1):
        if _arr[i - 1] > _arr[i]:
            _arr[i] = 0
    return _arr


def getChessLines(hdx, hdy, hdx_thresh, hdy_thresh):
    """Returns pixel indices for the 7 internal chess lines in x and y axes"""

    gausswin = scipy.signal.gaussian(21, 4)
    gausswin /= np.sum(gausswin)

    blur_x = np.convolve(hdx > hdx_thresh, gausswin, mode='same')
    blur_y = np.convolve(hdy > hdy_thresh, gausswin, mode='same')

    skel_x = skeletonize_1d(blur_x)
    skel_y = skeletonize_1d(blur_y)

    lines_x = np.where(skel_x)[0]
    lines_y = np.where(skel_y)[0]

    lines_x = pruneLines(lines_x)
    lines_y = pruneLines(lines_y)

    is_match = len(lines_x) == 7 and len(
        lines_y) == 7 and checkMatch(lines_x) and checkMatch(lines_y)

    return lines_x, lines_y, is_match




def getChessTiles(a, lines_x, lines_y):
    """Split up input grayscale array into 64 tiles stacked in a 3D matrix using the chess linesets"""

    stepx = np.int32(np.round(np.mean(np.diff(lines_x))))
    stepy = np.int32(np.round(np.mean(np.diff(lines_y))))

    padr_x = 0
    padl_x = 0
    padr_y = 0
    padl_y = 0

    if lines_x[0] - stepx < 0:
        padl_x = np.abs(lines_x[0] - stepx)
    if lines_x[-1] + stepx > a.shape[1] - 1:
        padr_x = np.abs(lines_x[-1] + stepx - a.shape[1])
    if lines_y[0] - stepy < 0:
        padl_y = np.abs(lines_y[0] - stepy)
    if lines_y[-1] + stepx > a.shape[0] - 1:
        padr_y = np.abs(lines_y[-1] + stepy - a.shape[0])

    a2 = np.pad(a, ((padl_y, padr_y), (padl_x, padr_x)), mode='edge')

    setsx = np.hstack([lines_x[0] - stepx, lines_x,
                       lines_x[-1] + stepx]) + padl_x
    setsy = np.hstack([lines_y[0] - stepy, lines_y,
                       lines_y[-1] + stepy]) + padl_y

    a2 = a2[setsy[0]:setsy[-1], setsx[0]:setsx[-1]]
    setsx -= setsx[0]
    setsy -= setsy[0]

    squares = np.zeros([np.round(stepy), np.round(stepx), 64], dtype=np.uint8)

    for i in range(0, 8):
        for j in range(0, 8):
            x1 = setsx[i]
            x2 = setsx[i + 1]
            padr_x = 0
            padl_x = 0
            padr_y = 0
            padl_y = 0

            if (x2 - x1) > stepx:
                if i == 7:
                    x1 = x2 - stepx
                else:
                    x2 = x1 + stepx
            elif (x2 - x1) < stepx:
                if i == 7:
                    padr_x = stepx - (x2 - x1)
                else:
                    padl_x = stepx - (x2 - x1)
            y1 = setsy[j]
            y2 = setsy[j + 1]

            if (y2 - y1) > stepy:
                if j == 7:
                    y1 = y2 - stepy
                else:
                    y2 = y1 + stepy
            elif (y2 - y1) < stepy:
                if j == 7:
                    padr_y = stepy - (y2 - y1)
                else:
                    padl_y = stepy - (y2 - y1)
            squares[:, :, (7 - j) * 8 + i] = np.pad(a2[y1:y2, x1:x2],
                                                    ((padl_y, padr_y), (padl_x, padr_x)), mode='edge')
    return squares



def generateTileset(str, folder_name, tiles_directory):

    np.set_printoptions(suppress=True)

    sess = tf.InteractiveSession()
    img_file = str
    folder = folder_name

    img = PIL.Image.open("%s/%s" % (folder, img_file))

    if img.size[0] > 2000 or img.size[1] > 2000:
        print ("Image too big (%d x %d)" % (img.size[0], img.size[1]))
        new_size = 500.0
        if img.size[0] > img.size[1]:
            ratio = new_size / img.size[0]
        else:
            ratio = new_size / img.size[1]
        img = img.resize(img.size * ratio, PIL.Image.ADAPTIVE)

    a = np.asarray(img.convert("L"), dtype=np.float32)
    A = tf.Variable(a)

    Dx = gradientx(A)
    Dy = gradienty(A)

    tf.global_variables_initializer().run()

    Dx_pos = tf.clip_by_value(Dx, 0., 255., name="dx_positive")
    Dx_neg = tf.clip_by_value(Dx, -255., 0., name='dx_negative')
    Dy_pos = tf.clip_by_value(Dy, 0., 255., name="dy_positive")
    Dy_neg = tf.clip_by_value(Dy, -255., 0., name='dy_negative')


    hough_Dx = tf.reduce_sum(Dx_pos, 0) * \
        tf.reduce_sum(-Dx_neg, 0) / (a.shape[0] * a.shape[0])
    hough_Dy = tf.reduce_sum(Dy_pos, 1) * \
        tf.reduce_sum(-Dy_neg, 1) / (a.shape[1] * a.shape[1])

    hough_Dx_thresh = tf.reduce_max(hough_Dx) * 3 / 5
    hough_Dy_thresh = tf.reduce_max(hough_Dy) * 3 / 5

    lines_x, lines_y, is_match = getChessLines(hough_Dx.eval().flatten(),
                                               hough_Dy.eval().flatten(),
                                               hough_Dx_thresh.eval(),
                                               hough_Dy_thresh.eval())

    lines_x, lines_y, is_match = getChessLines(hough_Dx.eval().flatten(),
                                               hough_Dy.eval().flatten(),
                                               hough_Dx_thresh.eval() * .9,
                                               hough_Dy_thresh.eval() * .9)
    if is_match:
        print ("Chessboard found")
    else:
        print ("Couldn't find Chessboard")

    if is_match:
        print ("7 horizontal and vertical lines found, slicing up squares")
        squares = getChessTiles(a, lines_x, lines_y)
    else:
        print ("Number of lines not equal to 7")

    letters = 'ABCDEFGH'

    if is_match:
        print ("Order is row-wise from top left of image going right and down, so a8,b8....a7,b7,c7...h1")
        print ("Showing 5 random squares...")
        for i in np.random.choice(np.arange(64), 5, replace=False):
            display_array(squares[:, :, i], rng=[0, 255])
    else:
        print ("Didn't have lines to slice image up.")

    img_save_dir = tiles_directory + "/squares_%s" % img_file[:-4]

    if not is_match:
        print ("No squares to save")
    else:
        if not os.path.exists(img_save_dir):
            os.makedirs(img_save_dir)
            print ("Created dir %s" % img_save_dir)

        for i in range(64):
            sqr_filename = "%s/%s_%s%d.png" % (img_save_dir,
                                               img_file[:-4], letters[i % 8], i / 8 + 1)
            if i % 8 == 0:
                print ("#%d: saving %s..." % (i, sqr_filename))

            PIL.Image.fromarray(squares[:, :, i]) \
                .resize([32, 32], PIL.Image.ADAPTIVE) \
                .save(sqr_filename)
