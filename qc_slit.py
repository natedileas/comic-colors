from common import cache_local_colors, create_color_col_image

# def get_images():
#   for i in range(1, 50):
#   # for i in range(1, 100):
#   # for i in range(1, 4220):
#       print('\r', i, end='')
#       try:
#           r = requests.get(f'https://www.questionablecontent.net/comics/{i}.png')
#           imgdata = r.content
#           image = np.asarray(Image.open(io.BytesIO(imgdata)))

#           image = norm_image(image)
#           cv2.imwrite(f'./qc/{i}.png', image)
#           time.sleep(1)

#       except KeyboardInterrupt:
#           break
#       except:
#           logging.error('Failed on %s', i, exc_info=True)

if __name__ == '__main__':
    import os
    import datetime

    outnamef = lambda fn: os.path.join('qc_colors', os.path.basename(fn) + '.pickle')
    cache_local_colors('./qc/*.png', outnamef, kind='kmeans2', n_colors=10)

    label = lambda fn: int(os.path.splitext(os.path.basename(fn))[0])
    create_color_col_image(inglob='./qc_colors/*.pickle', labelfun=label, height=2000, outname=f'qc_slit_{datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")}.png')
    
