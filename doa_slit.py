from common import create_color_col_image, cache_local_colors


if __name__ == '__main__':
    import os
    import datetime

    def get_image_url(soup, url):
        return soup.find(id='comic-1').img['src']

    def get_next_url(soup, url):
        try:
            return soup.find(id='comic-1').a['href']
        except:
            return url

    def get_outname(url, imageurl):
        return './doa/' + '_'.join(url.split('/')[-4:]) + os.path.basename(imageurl)
    
    # get_images('https://www.dumbingofage.com/2010/comic/book-1/01-move-in-day/home/',
    #          get_image_url,
    #          get_next_url,
    #          get_outname)
    
    outname_f = lambda fn: os.path.join('doa_colors_2', os.path.basename(fn) + '.pickle')
    cache_local_colors('./doa/*', outname_f, kind='kmeans2', n_colors=10)

    label = lambda fn: datetime.datetime.strptime(fn.split('_')[-1][:10], '%Y-%m-%d')
    name = f'doa_slit_{datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")}.png'
    create_color_col_image(inglob='./doa_colors_2/*.pickle', outname=name, labelfun=label, height=1500)
