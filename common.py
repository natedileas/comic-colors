import numpy as np
import requests
from bs4 import BeautifulSoup
import shutil
import os
import glob
import cv2
import pickle
import datetime


def cache_local_colors(inglob, outnamefunc, **kwargs):
    for i, fn in enumerate(glob.glob(inglob)):
        print(i)
        image = cv2.imread(fn)

        if image is not None:
            codes, counts, centroids = get_colors(image, **kwargs)
            
            with open(outnamefunc(fn), 'wb') as f:
                pickle.dump([codes, counts, centroids], f)


def get_images(url, get_image_url, get_next_link, get_save_loc):
    """ """
    i = 0

    while True:
        print(i, url)
        i += 1
        req = requests.get(url)
        if req.status_code != 200:
            continue

        soup = BeautifulSoup(req.text, 'html.parser')

        imageurl = get_image_url(soup, url)

        # find the comic image and save it
        r = requests.get(imageurl, stream=True)
        imagename = get_save_loc(url, imageurl)
        if r.status_code == 200:
            with open(imagename, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

        # find the next url to go to
        nexturl = get_next_link(soup, url)
        if url == nexturl:
            break

        url = nexturl


def create_color_col_image(inglob='./doa_colors/*.pickle', labelfun=None, height=100, outname='out.png'):

    columns = []
    labels = []
    for pickle_name in glob.glob(inglob):

        try:
            with open(pickle_name, 'rb') as f:
                codes, counts, centroids = pickle.load(f)
        except FileNotFoundError:
            continue
        
        columns.append(get_col_from_colors(codes, counts, centroids, height=height))
        labels.append(labelfun(pickle_name))
        

    # sort by labels
    # columns = [x for _,x in sorted(zip(labels, columns))]

    # pad columns
    padded_cols = []
    max_len = max(c.shape[0] for c in columns)
    for column in columns:
        padded_cols.append(np.pad(column, ((max_len - column.shape[0], 0), (0,0), (0,0)), 'constant'))


    cv2.imwrite(outname, np.hstack(padded_cols))


def norm_image(image):
    """ Take a gray, 3-channel, or 4-channel image and return a 3-channel bgr im. """
    if len(image.shape) == 3:
        return image[:,:,:3]
    elif len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)


def get_colors(image, n_colors=10, kind='kmeans'):
    """ from an image return a column where the colors are sorted and sized by rate of occurence

    inspired by: http://mkweb.bcgsc.ca/color-summarizer/?faq
    """
    im_lab = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)

    from scipy.cluster.vq import kmeans, kmeans2, whiten, vq
    features = im_lab.reshape(-1, 3)
    whitened = whiten(features)
    
    if kind == 'kmeans':
        centroids, distortion = kmeans(whitened, n_colors)
    elif kind == 'kmeans2':
        centroids, labels = kmeans2(whitened, n_colors, minit='points')

    # centroids = np.sort(centroids, axis=0)
    dewhiten = np.std(features, axis=0)
    dewhiten[dewhiten == 0] = 1
    centroids *= dewhiten   # un-whiten
    codes, dist = vq(features, centroids)   # categorize each observation

    codes, counts = np.unique(codes, return_counts=True)

    return codes, counts, centroids


def get_col_from_colors(codes, counts, centroids, height=100):
    s = np.argsort(counts)
    col = np.vstack([np.repeat(centroids[codes[s][i]][np.newaxis,:], np.round(height * counts[s][i] / counts.sum()), axis=0) for i in range(len(codes))])
    col = np.sort(col, axis=0)[:, np.newaxis,:]
    # print(col.shape)
    # col = np.repeat(centroids[:, np.newaxis, :], 100, axis=0)

    return cv2.cvtColor(col.astype(np.uint8), cv2.COLOR_Lab2BGR)


def grab_center_col(image):
    return image[:,int(image.shape[1] // 2)][np.newaxis, :, :]

