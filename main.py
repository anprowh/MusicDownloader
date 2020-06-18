from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
from pytube import YouTube
from ffmpeg.video import separate_audio
import os
import patch

patch.apply_patches()


def download_music(search_request,download_path,nvids=1,max_zero_results=10,max_download_attempts=5,convert_to_mp3=False,verbose=True):

    base_search = 'https://www.youtube.com/results?search_query='
    base = 'https://www.youtube.com'

    vids = []

    pos = 0
    cur_zero_results = 0

    if verbose:
        print('Searching...   ',end='')

    while len(vids)==0:

        search = requests.get(base_search+search_request.replace(' ','+')).text                # getting search results
        soup = BeautifulSoup(search,features='html.parser').findAll('a')

        vids = []
        for link in soup:                                                    # appropriate results
            if 'href' in link.attrs:
                if str(link['href'])[:7] == '/watch?':
                    vids.append([link['href'],link.text])

        if len(vids)==0:                                                     # if no results then try again
            cur_zero_results += 1
            if verbose==2:
                print('Failed\nSearching again...   ',end='')
            if cur_zero_results == max_zero_results:
                if verbose:
                    print('Failed')
                return False

            continue

        if verbose:
            print()

        vids = [x for x in vids if x[1][0]!='\n']                            # getting rid of duplicates

        
        i=0
        if nvids == 1:                                                       # choosing prefered video
            link = vids[i][0]
        else:
            for pair in vids[:nvids]:
                print(i,pair[1])
                i+=1
            i = int(input('Choose Audio to download: '))
            link = vids[i][0]

        filename = vids[i][1].replace(' ','_')


        done = False

        if verbose:
            print('Downloading',vids[i][1])

        for j in range(max_download_attempts):
            stream = YouTube(base+link).streams.filter(only_audio=True).first()
            try:
                stream.download(download_path,filename=filename)   # downloading audio
                done = True
                break
            except:
                if verbose==2:
                    print('Trying again...')
                continue
        if not done:
            if verbose:
                print('Failed')
            
            return False

        if convert_to_mp3:
            if verbose:
                print('Converting')
            separate_audio(os.path.join(download_path,filename+'.mp4'),os.path.join(download_path,filename+'.mp3'))
            os.remove(os.path.join(download_path,filename+'.mp4'))

        if verbose:
            print('Done downloading',vids[i][1])
        return True
    return False

    
if __name__=='__main__':
    
    vids=[]

    download_path = os.path.join(os.path.curdir,'Music')

    nvids=5
    max_zero_results = 10
    max_download_attempts = 5

    convert = False

    titles_file = open('titles.txt','r')
    titles = [x.replace('\n','') for x in titles_file.readlines()]

    for search_request in titles:

        if search_request[0] == '-':
            continue
        
        print(search_request,'...',sep='')
        download_music(search_request,download_path,nvids=2)
        print('-'*50)
        