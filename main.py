from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
from pytube import YouTube
from ffmpeg.video import separate_audio
import os
import patch

patch.apply_patches()

def get_yt_link(search_request,nvids=1,max_zero_results=10,verbose=1):

    base_search = 'https://www.youtube.com/results?search_query='
    args_search = '&sp=EgIQAQ%253D%253D'
    base = 'https://www.youtube.com'

    vids = []

    pos = 0
    cur_zero_results = 0

    if verbose:
        print('Searching...   ',end='')

    while len(vids)==0:

        search = requests.get(base_search+search_request.replace(' ','+')+args_search).text                # getting search results
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
                return None

            continue

        if verbose:
            print()
            print('Found')

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

        return base+link,vids[i][1]

def download_music(link,filename,download_path,max_download_attempts=5,convert_to_mp3=False,rename=True,verbose=1):

    done = False

    if verbose:
        print('Downloading ',filename,'...',sep='')

    for j in range(max_download_attempts):

        stream = YouTube(link).streams.filter(only_audio=True).first()

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
            print('Converting...')

        
        separate_audio(os.path.join(download_path,filename+'.mp4'),os.path.join(download_path,filename+'.mp3')) # converting using ffmpeg

        if os.path.exists(os.path.join(download_path,filename+'.mp3')):

            os.remove(os.path.join(download_path,filename+'.mp4'))
            print('Done Converting')

        else:
    
            if verbose:
                print('Failed Converting')
                convert_to_mp3 = False

            if rename and convert_to_mp3:
                if verbose==2:
                    print('No Rename Required')
    

    if rename and not convert_to_mp3:

        if verbose:
            print('Renaming...')

        if os.path.exists(os.path.join(download_path,filename+'.mp3')):

            # If there already is file with this name then delete it
            if verbose == 2:
                print('Deleting existing file for renaming...')

            os.remove(os.path.join(download_path,filename+'.mp3'))

        os.rename(os.path.join(download_path,filename+'.mp4'),os.path.join(download_path,filename+'.mp3'))


    if verbose:
        print('Done downloading',filename)

    return True

    
if __name__=='__main__':
    
    spec_symb = ' -> ' # name - link separator for titles.txt

    download_path = os.path.join(os.path.abspath(os.path.curdir),'Music')
    print('Will be downloaded to',download_path)

    nvids = 1     # Number of videos to choose from
    max_zero_results = 10   # Max number of searching tries
    max_download_attempts = 5

    convert = False     # Converting using ffmpeg
    rename = True   # File is originally downloaded with .mp4 extension. Setting to true leads to renameing .mp4 to .mp3
    chooseAgain = False     # If there is link in titles.txt and it is set to False then no search will be done

    titles_file = open('titles.txt','r')
    titles_full = [x.replace('\n','') for x in titles_file.readlines()]
    titles =  [x for x in titles_full if x[0]!='-']
    links = []
    titles_new = []     # List used for saving info to titles.txt
    disable_found = []  
    disable_downloaded = [] # Disable title if search and downloading is successful

    i = 1

    
    # -----------------------------------Getting links--------------------------------- #
    for search_request in titles_full:

        # Skipping disabled titles
        if search_request[0] == '-':    
            titles_new.append(search_request)
            disable_found.append(True)
            continue

        print(i,'/',len(titles),' - Choosing YouTube link for ',search_request.split(spec_symb),'...',sep='')

        if search_request.count(spec_symb)==1 and not chooseAgain:   # Skipping search where link is available

            title,link = search_request.split(spec_symb)

            print('Link already exists')
            
            disable_found.append(True)

        else:

            title = search_request
            try:
                link,name = get_yt_link(search_request)

                disable_found.append(True)

            except:
                
                print('Search Failed')
                link,name = None, search_request
                disable_found.append(False)
  
        if disable_found[-1]:
            links.append(link)  
            titles_new.append(title + spec_symb + link)
        
        else:
            links.append(None)
            titles_new.append(title)
        
        i += 1

    # ------------------------Updating titles.txt: adding links-------------------------- #
    titles_file.close()                     
    titles_file = open('titles.txt','w')

    for title in titles_new:
        titles_file.write(title + '\n')

    titles_file.close()


    print()

    i = 1
    # ---------------------------------Downloading files----------------------------------- #
    for search_request,link in zip(titles,links):   
        if not link is None:

            try:

                filename_base = search_request.split(spec_symb)[0]

                print(i,'/',len(titles),' - Downloading Audio ',filename_base,'...',sep='')

                download_music(link,filename_base.replace(' ','_'),download_path,convert_to_mp3=convert,rename=rename)

                disable_downloaded.append(True)

            except:

                disable_downloaded.append(False)

                print('Failed downloading')

        i += 1

    # ------------------------Updating titles.txt: disabling downloaded music--------------- #
    titles_file = open('titles.txt','w')    

    for i,title in enumerate(titles_new):

        if disable_found and disable_downloaded:
            titles_file.write(('-' + title if title[0] != '-' else title) + '\n')
        else:
            titles_file.write(title + '\n')
        
        