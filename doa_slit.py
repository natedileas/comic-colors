import numpy as np
import requests
from bs4 import BeautifulSoup
import shutil
import os
import glob
import cv2
import pickle
import datetime

from qc_slit import get_colors, _get_col_from_colors


def cache_local_colors(inglob, outnamefunc):
    for i, fn in enumerate(glob.glob(inglob)):
        print(i)
        image = cv2.imread(fn)

        if image is not None:
            codes, counts, centroids = get_colors(image, n_colors=10)
            
            with open(outnamefunc(fn), 'wb') as f:
                pickle.dump([codes, counts, centroids], f)


def get_images(url, get_image=None, get_next=None):
    # starting at this url
    #start_url = r'https://www.dumbingofage.com/2010/comic/book-1/01-move-in-day/home/'
    start_url = r'https://www.dumbingofage.com/2017/comic/book-7/04-the-do-list/chubby/'
    url = start_url
    i = 0

    while True:
        print(i, url)
        i += 1
        req = requests.get(url)
        if req.status_code != 200:
            continue

        soup = BeautifulSoup(req.text, 'html.parser')

        comicdiv = soup.find(id='comic-1')
        imageurl = comicdiv.img['src']

        # find the comic image and save it
        r = requests.get(imageurl, stream=True)

        imagename = './doa/' + '_'.join(url.split('/')[-4:]) + os.path.basename(imageurl)
        if r.status_code == 200:
            with open(imagename, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

        # find the next url to go to
        try:
            url = comicdiv.a['href']
        except KeyError:
            break


def create_doa_image(inglob='./doa_colors/*.pickle', labelfun=None, height=100, outname='out.png'):

    columns = []
    labels = []
    for pickle_name in glob.glob(inglob):

        try:
            with open(pickle_name, 'rb') as f:
                codes, counts, centroids = pickle.load(f)
        except FileNotFoundError:
            continue
        
        columns.append(_get_col_from_colors(codes, counts, centroids, height=height))
        labels.append(labelfun(pickle_name))

    # sort by labels
    columns = [x for _,x in sorted(zip(labels, columns))]

    # pad columns
    padded_cols = []
    max_len = max(c.shape[0] for c in columns)
    for column in columns:
        padded_cols.append(np.pad(column, ((max_len - column.shape[0], 0), (0,0), (0,0)), 'constant'))


    cv2.imwrite(outname, np.hstack(padded_cols))


if __name__ == '__main__':
    # get_images()
    
    outname_f = lambda fn: os.path.join('doa_colors_2', os.path.basename(fn) + '.pickle')
    cache_local_colors('./doa/*', outname_f)

    label = lambda fn: datetime.datetime.strptime(fn.split('_')[-1][:10], '%Y-%m-%d')
    name = f'doa_slit_{datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")}.png'
    create_doa_image(inglob='./doa_colors_2/*.pickle', outname=name, labelfun=label, height=1500)
