import requests
from PIL import Image
import io
import logging
import cv2
import numpy as np
import datetime
import time
import pickle


def norm_image(image):
	""" Take a gray, 3-channel, or 4-channel image and return a 3-channel bgr im. """
	if len(image.shape) == 3:
		return image[:,:,:3]
	elif len(image.shape) == 2:
		return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)


def get_colors(image, n_colors=10):
	""" from an image return a column where the colors are sorted and sized by rate of occurence

	inspired by: http://mkweb.bcgsc.ca/color-summarizer/?faq
	"""
	im_lab = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)

	from scipy.cluster.vq import kmeans, kmeans2, whiten, vq
	features = im_lab.reshape(-1, 3)
	whitened = whiten(features)
	# centroids, distortion = kmeans(whitened, n_colors)
	centroids, labels = kmeans2(whitened, n_colors, minit='points')

	# centroids = np.sort(centroids, axis=0)
	centroids *= np.std(features, axis=0)   # un-whiten
	# print(centroids.shape, centroids)
	codes, dist = vq(features, centroids)   # categorize each observation

	codes, counts = np.unique(codes, return_counts=True)

	return codes, counts, centroids

def _get_col_from_colors(codes, counts, centroids, height=100):
	s = np.argsort(counts)
	col = np.vstack([np.repeat(centroids[codes[s][i]][np.newaxis,:], np.round(height * counts[s][i] / counts.sum()), axis=0) for i in range(len(codes))])
	col = np.sort(col, axis=0)[:, np.newaxis,:]
	# print(col.shape)
	# col = np.repeat(centroids[:, np.newaxis, :], 100, axis=0)

	return cv2.cvtColor(col.astype(np.uint8), cv2.COLOR_Lab2BGR)


def grab_center_col(image):
	return image[:,int(image.shape[1] // 2)][np.newaxis, :, :]

def get_images():
	for i in range(1, 50):
	# for i in range(1, 100):
	# for i in range(1, 4220):
		print('\r', i, end='')
		try:
			r = requests.get(f'https://www.questionablecontent.net/comics/{i}.png')
			imgdata = r.content
			image = np.asarray(Image.open(io.BytesIO(imgdata)))

			image = norm_image(image)
			cv2.imwrite(f'./qc/{i}.png', image)
			time.sleep(1)

		except KeyboardInterrupt:
			break
		except:
			logging.error('Failed on %s', i, exc_info=True)


def cache_local_colors():
	for i in range(2000, 4220):
		print('\r', i, end='')
		image = cv2.imread(f'./qc/{i}.png')
		if image is not None:
			codes, counts, centroids = get_colors(image, n_colors=10)
			debug_name=f'./qc/{i}.pickle'
			with open(debug_name, 'wb') as f:
				pickle.dump([codes, counts, centroids], f)

def create_web_slit_scan(start, end, height=100, format_str='{}.png', outname='out.png'):

	columns = []
	for i in range(start, end):
		print('\r', i, end='')
		pickle_name = format_str.format(i)
		
		try:
			with open(pickle_name, 'rb') as f:
				codes, counts, centroids = pickle.load(f)
		except FileNotFoundError:
			continue
		
		columns.append(_get_col_from_colors(codes, counts, centroids, height=height))

	# pad columns
	padded_cols = []
	max_len = max(c.shape[0] for c in columns)
	for column in columns:
		padded_cols.append(np.pad(column, ((max_len - column.shape[0], 0), (0,0), (0,0)), 'constant'))


	cv2.imwrite(outname, np.hstack(padded_cols))


if __name__ == '__main__':
	# cache_local_colors()
	# create_web_slit_scan(1, 2050, './qc/{}.pickle', height=1000, outname=f'qc_slit_{datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")}.png')
	create_web_slit_scan(1, 4220, height=2000, format_str='./qc/{}.pickle', outname=f'qc_slit_{datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")}.png')
	
'''
# PowerShell: seems to be working where python isn't
for ($i=90; $i -le 101; $i++){ wget "https://www.questionablecontent.net/comics/$i.png" -outFile "./qc/$i.png"}
for ($i=100; $i -le 1000; $i++){ wget "https://www.questionablecontent.net/comics/$i.png" -outFile "./qc/$i.png"}
for ($i=2170; $i -le 4220; $i++){ wget "https://www.questionablecontent.net/comics/$i.png" -outFile "./qc/$i.png"}
'''