import urllib.parse
import os
import datetime

from doa_slit import cache_local_colors, create_doa_image, get_images


if __name__ == '__main__':
    def get_im_url(soup, url):
        div = soup.find(id="webcomic-image")
        p = urllib.parse.urlparse(url)
        p = p._replace(path=div.img['src'])
        return p.geturl()

    def get_next_url(soup, url):
        a = soup.find(class_="next-webcomic-link")
        p = urllib.parse.urlparse(url)
        p = p._replace(path=a['href'])
        return p.geturl()

    def get_save_loc(url, imageurl):
        return os.path.join('btf', '_'.join(imageurl.split('/')[-3:]))

    # get_images('https://betweenfailures.com/comics1/every-story-has-to-start-somewhere',
    #          get_im_url,
    #          get_next_url,
    #          get_save_loc)

    outnamef = lambda fn: os.path.join('btf_colors', os.path.basename(fn) + '.pickle')
    # cache_local_colors('./btf/*', outnamef, kind='kmeans2', n_colors=10)

    def label(fn):
        try:
            return int(fn.split('_')[-1].split('-')[-2][3:])
        except:
            print(fn)
            return -1

    name = f'btf_slit_{datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")}.png'
    create_doa_image(inglob='./btf_colors/*.pickle', outname=name, labelfun=label, height=500)
