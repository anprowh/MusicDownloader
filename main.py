from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
from pytube import YouTube
from ffmpeg.video import separate_audio
import os
import patch


class YTAudioDownloader:
    '''
        Class used for Music/Audio download from YouTube.
        It is able to search for Video in YouTube (get_yt_link),
        Download Audio from It (download_audio)

    '''

    def __init__(self, title, link=None, yt_name=None, filename=None, slugify=True):
        '''
            Initializes Downloader

            Args:
            title (str):
                Title of music/audio to search for
            
            link (str):
                Optional. Link on YouTube video to download audio from. 
                Found during search

            yt_name (str):
                Optional. Name of YouTube video. Can be used for naming.

            filename (str):
                Optional. If set to 'yt' then is named with yt_name. 
                If None or 'title' then is named with title.

            slugify (bool):
                If True then filename is converted to valid filename

        '''

        self.title = title
        self.yt_name = yt_name
        self.slugify = slugify
        self.link = link
        self.success = False
        self.filename = filename

        if self.filename is None or self.filename == 'title':
            self.filename = self.title
        elif self.filename == 'yt' and not self.yt_name is None:
            self.filename = self.yt_name
        
        if self.slugify:
            self.slugify_filename()

    def slugify_filename(self):
        """
        Normalizes filename, removes non-alpha characters,
        and converts spaces to hyphens.

        Returns:
            str: new filename
        
        """
        # import unicodedata
        # import re
        # self.filename = str(unicodedata.normalize('NFKD', self.filename))
        # self.filename = re.sub('[^\w\s-]', '', self.filename).strip()
        # self.filename = re.sub('[-\s]+', '-', self.filename)
        self.filename = self.filename.replace(' ','_')
        
        return self.filename
        
    def get_yt_link(self,nvids=1,max_zero_results=10,verbose=1):
        '''
            Searches YouTube to get link to the video with needed audio
            and updates link and yt_name.

            Args:
            nvids (int): 
                Number of videos to choose from. 
                If set to 1 then video is chosen automatically.
            
            max_zero_results (int):
                Number of times programm tries to find appropriate links.

            verbose (int):
                If 0 then no info is printed.
                If 1 then prints only main progress information. No retries.
                If 2 then prints all progress information. With retries.

            Returns:
                (String,String)/None: link and YT name. None if Failed.
            

        '''

        base_search = 'https://www.youtube.com/results?search_query='
        args_search = '&sp=EgIQAQ%253D%253D'
        base = 'https://www.youtube.com'

        vids = []

        pos = 0
        cur_zero_results = 0

        if verbose:
            print('Searching...   ',end='')

        while len(vids)==0:
            # getting search results
            search = requests.get(
                base_search+self.title.replace(' ','+')+args_search
                ).text
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
        
        # getting rid of duplicates
        vids = [x for x in vids if x[1][0]!='\n']

        # choosing prefered video
        i=0
        if nvids == 1:
            link = vids[i][0]
        else:
            for pair in vids[:nvids]:
                print(i,pair[1])
                i+=1
            i = int(input('Choose Audio to download: '))
            link = vids[i][0]

        # Updating object info
        self.link = base + link
        self.yt_name = vids[i][1]

        if self.filename == 'yt':
            self.filename = self.yt_name
        if self.slugify:
            self.slugify_filename()

        return base+link,vids[i][1]

    def download_audio(self,download_path,max_download_attempts=5,convert_to_mp3=False,rename=True,verbose=1): 
        '''
            Downloads audio from YouTube

            Args:
            download_path (str):
                Path to folder for audio to download to.

            max_download_attempts (int):
                Number of times programm tries to download audio.

            convert_to_mp3 (bool):
                If True then file is converted using ffmpeg. 
                If failed then 'Failed converting' is printed

            rename (bool):
                If True then file extension is roughly changed to .mp3.
                Originally it is downloaded with .mp4 extension.
                Is ignored if convert_to_mp3 is True and is converted successfully.

            verbose (int):
                If 0 then no info is printed.
                If 1 then prints only main progress information. No retries.
                If 2 then prints all progress information. With retries.
        '''

        if self.link is None:
            if verbose:
                print('No Link\nFailed')
            return False

        patch.apply_patches()

        done = False

        if verbose:
            print('Downloading ',self.filename,'...',sep='')

        for j in range(max_download_attempts):

            stream = YouTube(self.link).streams.filter(only_audio=True).first()

            try:

                stream.download(download_path,filename=self.filename)   # downloading audio
                done = True
                break

            except:

                if verbose == 2:
                    print('Trying again...')
                continue

        if not done:
            if verbose:
                print('Failed')
            
            return False

        if convert_to_mp3:

            if verbose:
                print('Converting...')
                
            # converting using ffmpeg
            separate_audio(os.path.join(download_path,self.filename+'.mp4'),os.path.join(download_path,self.filename+'.mp3')) 

            if os.path.exists(os.path.join(download_path,self.filename+'.mp3')):

                os.remove(os.path.join(download_path,self.filename+'.mp4'))
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

            if os.path.exists(os.path.join(download_path,self.filename+'.mp3')):

                # If there already is file with this name then delete it
                if verbose == 2:
                    print('Deleting existing file for renaming...')

                os.remove(os.path.join(download_path,self.filename+'.mp3'))

            os.rename(os.path.join(download_path,self.filename+'.mp4'),os.path.join(download_path,self.filename+'.mp3'))


        if verbose:
            print('Done downloading',self.filename)
        
        self.success = True

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
    downloaders = []

    i = 1
    n = 0


    # -----------------------------------Getting links--------------------------------- #
    for search_request in titles_full:

        # Skipping disabled titles
        if search_request[0] == '-':    
            downloaders.append(search_request)
            continue

        

        print(i,'/',len(titles),' - Choosing YouTube link for ',search_request.split(spec_symb),'...',sep='')

        if search_request.count(spec_symb)==1 and not chooseAgain:   # Skipping search where link is available

            title,link = search_request.split(spec_symb)

            downloaders.append(YTAudioDownloader(title,link))

            n+=1

            print('Link already exists')

        else:

            title = search_request

            downloaders.append(YTAudioDownloader(title))
            
            try:
                downloaders[-1].get_yt_link()
                n += 1

            except:
                
                print('Search Failed')
        
        i += 1

    # ------------------------Updating titles.txt: adding links-------------------------- #
    titles_file.close()                     
    titles_file = open('titles.txt','w')

    for unit in downloaders:
        if isinstance(unit,str):
            titles_file.write(unit + '\n')
        else:
            titles_file.write(unit.title+spec_symb+unit.link+'\n')

    titles_file.close()


    print()

    i = 1
    # ---------------------------------Downloading files----------------------------------- #
    for unit in downloaders:
        if isinstance(unit,str):
            continue

        try:

            print(i,'/',n,' - Downloading Audio ',unit.title,'...',sep='')

            unit.download_audio(download_path,convert_to_mp3=convert,rename=rename)

        except:

            print('Failed downloading')

        i += 1

    # ------------------------Updating titles.txt: disabling downloaded music--------------- #
    titles_file = open('titles.txt','w')    

    for unit in downloaders:

        if isinstance(unit,str):
            titles_file.write(unit+'\n')
        else:
            if unit.success:
                titles_file.write('-'+unit.title+spec_symb+unit.link+'\n')
            else:
                if unit.link is None:
                    titles_file.write(unit.title+'\n')
                else: 
                    titles_file.write(unit.title+spec_symb+unit.link+'\n')

                
        
        