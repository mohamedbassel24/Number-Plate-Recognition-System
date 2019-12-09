import numpy as np
import cv2
import skimage.io as io
from skimage.color import rgb2gray
from scipy.signal import convolve2d
import matplotlib.pyplot as plt
from scipy import signal as sig
from scipy.ndimage import gaussian_filter

def show_images(images, titles=None):
    # This function is used to show image(s) with titles by sending an array of images and an array of associated titles.
    # images[0] will be drawn with the title titles[0] if exists
    # You aren't required to understand this function, use it as-is.
    n_ims = len(images)
    if titles is None:
        titles = ['(%d)' % i for i in range(1, n_ims + 1)]
    fig = plt.figure()
    n = 1
    for image, title in zip(images, titles):
        a = fig.add_subplot(1, n_ims, n)
        if image.ndim == 2:
            plt.gray()
        plt.imshow(image)
        a.set_title(title)
        plt.axis('off')
        n += 1
    fig.set_size_inches(np.array(fig.get_size_inches()) * n_ims)
    plt.show()


def Preprocess(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.blur(img, (3, 3))  # TODO: Write this Function
    # _, img = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY)# TODO: Write this Function
    return img


def SobelFilter(img):
    image = rgb2gray(img)
    sobelMaskXDir = np.array([[-1, 0, 1],
                              [-np.sqrt(2), 0, np.sqrt(2)],
                              [-1, 0, 1]])
    sobelMaskYDir = sobelMaskXDir.T
    Gx = convolve2d(image, sobelMaskXDir)
    Gy = convolve2d(image, sobelMaskYDir)
    G = np.sqrt(np.power(Gx, 2))
    return Gx


def MorhOperations(img):
    SE = cv2.getStructuringElement(cv2.MORPH_RECT, (16, 16))
    SE2 = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
    SE3 = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))

    x = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel=SE)

    x = cv2.morphologyEx(x, cv2.MORPH_OPEN, kernel=SE2, iterations=1)
    x = cv2.morphologyEx(x, cv2.MORPH_OPEN, kernel=SE3, iterations=1)
    return x


def extractImages(pathIn):
    count = 0
    vidcap = cv2.VideoCapture(pathIn)
    success, image = vidcap.read()
    success = True
    ListFrames = []
    while success:
        # save a frame for every second
        vidcap.set(cv2.CAP_PROP_POS_MSEC, (count * 1000))
        success, image = vidcap.read()
        #   print('Read a new frame: ', success)
        if success == 0:
            break
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

        #   cv2.imwrite("../03-Dataset/frames/"+"frame%d.jpg" %
        #          count, image)     # save frame as JPEG file
        ListFrames.append(image)
        count = count + 1
    return ListFrames


def GammaCorrection(image, c, gamma):
    #   image = rgb2gray(image)
    imageGamma = np.array(image)
    image = c * np.power(imageGamma, gamma)
    return image


def Harris(img):
    # imgg=GammaCorrection(img,1,2)
    # Preprocessing on frame=>
    image = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    sat = cv2.medianBlur(image, ksize=3)

    # sat=GammaCorrection(image,1,10)
    show_images([sat])
    # ----------------------------------------------------------------------------------------
    # print(imgg.shape)
    dst = cv2.cornerHarris(sat, 20, 5, 0.12)
    show_images([dst])
    # dst = cv2.dilate(dst, kernel=cv2.getStructuringElement(cv2.MORPH_RECT,(3,3)))
    dst = cv2.morphologyEx(dst, op=cv2.MORPH_CLOSE, kernel=cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)),
                           iterations=3)

    imag = np.copy(img)
    imag1 = np.copy(img)

    imag2 = np.copy(img)
    arr = ((dst > 0.1 * dst.max()) & (image > 150))

    max = -1
    maxi = [0, 0]
    wx = int(arr.shape[0] / 10.5)
    wy = int(arr.shape[1] / 3)
    ListPlates = []
    for i in range(arr.shape[0] - 1, 0, -int(wx / 3)):  # tool
        if (i < int(arr.shape[0] / 2)):
            break
        for j in range(arr.shape[1] - 1, 0 + wy, -int(wy / 3)):  # 3ard
            # print(np.sum(arr[i-wx:i,j-wy:j]))
            if (np.sum(arr[i - wx:i, j - wy:j])) > max:
                max = np.sum(arr[i - wx:i, j - wy:j])
                maxi[0] = i - wx
                maxi[1] = j - wy
                ListPlates.append([i - wx, j - wy, max])

    print(max, "weeeeeeeeee")
    if max == 0:
        return img, 0
    cv2.rectangle(imag, (maxi[1], maxi[0]), (maxi[1] + wy, maxi[0] + wx), (255, 0, 0), 2)

    ListPlates.reverse()
    cv2.rectangle(imag, (ListPlates[1][0], ListPlates[1][1]), (ListPlates[1][0] + wy, ListPlates[1][1] + wx),
                  (255, 0, 0), 2)
    ret = imag[maxi[0]:maxi[0] + wx, maxi[1]:maxi[1] + wy]
    show_images([ret, imag])
    return ret, imag
    imageret = cv2.cvtColor(ret, cv2.COLOR_RGB2GRAY)
    start, end = 1, 1
    # print(imageret.shape)
    starti, endi = 1, 1

    for i in range(imageret.shape[1] - 5):
        if np.average((imageret[int(0.2 * imageret.shape[0]):int(0.6 * imageret.shape[0]), i:i + 4])) > 100:
            start = i
            break
    for i in range(imageret.shape[1] - 6, 4, -1):
        if np.average((imageret[int(0.2 * imageret.shape[0]):int(0.6 * imageret.shape[0]), i:i + 4])) > 100:
            end = i
            break
    filtered = imageret[:, start:end]

    for i in range(filtered.shape[1] - 3):
        if np.average((filtered[i:i + 3, :])) > 120:
            starti = i
            break

    for i in range(filtered.shape[0] - 3, 0, -1):
        if np.average((filtered[i:i + 3, :])) > 120:
            endi = i
            break
    filtered = ret[starti:endi, start:end]
    print(starti, endi)
    #    show_images([img,filtered],["orginal","Suppose to be a plate ?"])
    return filtered, 0


# extractImages("../03-Dataset/car6.mp4")
# img = io.imread("lol.jpg")
# x1 = Harris(img)
# img = io.imread("lol2.jpg")
# x1 = Harris(img)
# img = io.imread("lol3.jpg")
# x1 = Harris(img)
# x= cv2.equalizeHist(x)
def my_cornerHarris(Orignal_img):
    img = rgb2gray(Orignal_img)
    # Sobel Algorithm =>
    fx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    fy = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])

    I_x = sig.convolve2d(img, fx, mode='same')
    I_y = sig.convolve2d(img, fy, mode='same')
    Ixx = gaussian_filter(I_x ** 2, sigma=2)
    Ixy = gaussian_filter(I_y * I_x, sigma=2)
    Iyy = gaussian_filter(I_y ** 2, sigma=2)
    k = 0.05
    detA = Ixx * Iyy - Ixy ** 2
    traceA = Ixx + Iyy
    harris_response = detA - k * traceA ** 2
    show_images([harris_response])
    offset=0
    height=3
    width=3


    for y in range(offset, height - offset):
        for x in range(offset, width - offset):
            Sxx = np.sum(Ixx[y - offset:y + 1 + offset, x - offset:x + 1 + offset])
            Syy = np.sum(Iyy[y - offset:y + 1 + offset, x - offset:x + 1 + offset])
            Sxy = np.sum(Ixy[y - offset:y + 1 + offset, x - offset:x + 1 + offset])
    det = (Sxx * Syy) - (Sxy ** 2)
    trace = Sxx + Syy
    r = det - k * (trace ** 2)
    img_copy_for_corners = np.copy(Orignal_img)
    img_copy_for_edges = np.copy(Orignal_img)
    for rowindex, response in enumerate(harris_response):
        for colindex, r in enumerate(response):
            if r > 0:
                # this is a corner
                img_copy_for_corners[rowindex, colindex] = [255, 0, 0]
            elif r < 0:
                # this is an edge
                img_copy_for_edges[rowindex, colindex] = [0, 255, 0]
#    corners = corner_peaks(harris_response)
    fig, ax = plt.subplots()
    ax.imshow(img_copy_for_corners, interpolation='nearest', cmap=plt.cm.gray)
    #ax.plot(corners[:, 1], corners[:, 0], '.r', markersize=3)
