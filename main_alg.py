from pytube import YouTube
from ffmpeg.video import separate_audio
import os
from youtubesearchpython import SearchVideos


class YTAudioDownloader:
    '''
        Class used for Music/Audio download from YouTube.
        It is able to search for Video in YouTube (get_yt_link),
        Download Audio from It (download_audio)

    '''

    def __init__(self, title: str, link=None, yt_name=None, filename=None, slugify=True):
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
        elif self.filename == 'yt' and self.yt_name is not None:
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
        self.filename = self.filename.replace(' ', '_')

        return self.filename

    def get_yt_link(self, n_videos=1, verbose=1):
        '''
            Searches YouTube to get link to the video with needed audio
            and updates link and yt_name.

            Args:
            n_videos (int):
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

        vids = []

        if verbose:
            print('Searching...   ', end='')

        search = SearchVideos(self.title, offset=1,
                              mode="json", max_results=n_videos)

        vids = eval(search.result())
        vids = [(x['link'], x['title']) for x in vids['search_result']]
        print(vids)

        # choosing prefered video
        i = 0
        if n_videos == 1:
            link = vids[i][0]
        else:
            for pair in vids[:n_videos]:
                print(i, pair[1])
                i += 1
            i = int(input('Choose Audio to download: '))
            link = vids[i][0]

        # Updating object info
        self.link = link
        self.yt_name = vids[i][1]

        if self.filename == 'yt':
            self.filename = self.yt_name
        if self.slugify:
            self.slugify_filename()
        return link, vids[i][1]

    def download_audio(self, download_path, max_download_attempts=5,
                       convert_to_mp3=False, rename=True, verbose=1):
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

        done = False

        if verbose:
            print('Downloading ', self.filename, '...', sep='')

        for j in range(max_download_attempts):
            stream = YouTube(self.link[:])
            stream = stream.streams.filter(only_audio=True).first()

            try:

                # downloading audio
                stream.download(download_path, filename=self.filename)
                done = True
                break

            except Exception:

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

            mp3_name = os.path.join(download_path, self.filename+'.mp3')
            mp4_name = os.path.join(download_path, self.filename+'.mp4')

            # converting using ffmpeg
            separate_audio(mp4_name, mp3_name)

            if os.path.exists(mp3_name):

                os.remove(mp4_name)
                print('Done Converting')

            else:

                if verbose:
                    print('Failed Converting')
                    convert_to_mp3 = False

                if rename and convert_to_mp3:
                    if verbose == 2:
                        print('No Rename Required')

        if rename and not convert_to_mp3:

            if verbose:
                print('Renaming...')

            mp3_name = os.path.join(download_path, self.filename+'.mp3')
            mp4_name = os.path.join(download_path, self.filename+'.mp4')

            if os.path.exists(mp3_name):

                # If there already is file with this name then delete it
                if verbose == 2:
                    print('Deleting existing file for renaming...')

                os.remove(os.path.join(mp3_name))

            os.rename(mp4_name, mp3_name)

        if verbose:
            print('Done downloading', self.filename)

        self.success = True

        return True


# ===================M====M========A========IIII=====NN====N================= #
# ===================MM==MM=======A=A========II======N=N===N================= #
# ===================M=MM=M======A===A=======II======N==N==N================= #
# ===================M====M=====AAAAAAA======II======N===N=N================= #
# ===================M====M=====A=====A=====IIII=====N====NN================= #

class MainProg:

    def __init__(
            self,
            spec_symb=' -> ',
            titles_filename='titles.txt',
            download_path=os.path.join(
                os.path.abspath(os.path.curdir), 'Music'),
            n_videos=1,
            max_download_attempts=5,
            convert=False,
            rename=True,
            choose_again=False,
            verbose=True):

        self.spec_symb = spec_symb  # name - link separator for titles.txt

        self.convert = convert     # Converting using ffmpeg
        # File is originally downloaded with .mp4 extension.
        # Setting to true leads to renameing .mp4 to .mp3
        self.rename = rename
        # If there is link in titles.txt and it is set to False
        # then no search will be done
        self.choose_again = choose_again
        self.verbose = verbose

        self.titles_filename = titles_filename
        self.download_path = download_path
        if self.verbose:
            print('Audio will be downloaded to', download_path)

        self.n_videos = n_videos     # Number of videos to choose from
        self.max_download_attempts = max_download_attempts
        self.downloaders = []

    def get_links(self):

        titles_file = open(os.path.join(
            self.download_path, self.titles_filename), 'r', encoding='utf-8')
        titles_full = [x.replace('\n', '')
                       for x in titles_file.readlines()]
        titles = [x for x in titles_full if x[0] != '-']

        i = 1
        n = 0

        for search_request in titles_full:

            # Skipping disabled titles
            if search_request[0] == '-':
                self.downloaders.append(search_request)
                continue

            if self.verbose:
                print(i, '/', len(titles), ' - Choosing YouTube link for ',
                      search_request.split(self.spec_symb)[0], '...', sep='')

            # Skipping search where link is available
            if search_request.count(self.spec_symb) == 1 and not self.choose_again:

                title, link = search_request.split(self.spec_symb)

                self.downloaders.append(YTAudioDownloader(title, link))

                n += 1
                if self.verbose:
                    print('Link already exists')

            else:
                # If choose again is true and link exists for this title
                # algorithm takes only title from titles.txt as a title
                # otherwice it will anyway return the title
                title = search_request.split(self.spec_symb)[0]


                self.downloaders.append(YTAudioDownloader(title))

                try:
                    self.downloaders[-1].get_yt_link(
                        n_videos=self.n_videos, verbose=self.verbose)
                    n += 1

                except Exception:
                    if self.verbose:
                        print('Search Failed')

            i += 1
        titles_file.close()

    def save(self):
        titles_file = open(os.path.join(
            self.download_path, self.titles_filename), 'w', encoding='utf-8')

        for unit in self.downloaders:
            if isinstance(unit, str):
                titles_file.write(unit + '\n')
            else:
                if unit.success:
                    titles_file.write(
                        '-'+unit.title+self.spec_symb+unit.link+'\n')
                else:
                    if unit.link is None:
                        titles_file.write(unit.title+'\n')
                    else:
                        titles_file.write(
                            unit.title+self.spec_symb+unit.link+'\n')

        titles_file.close()
        if self.verbose:
            print()

    def download(self):

        i = 1
        n = len([1 for x in self.downloaders if not isinstance(x, str)])

        for unit in self.downloaders:
            if isinstance(unit, str):
                continue

            try:
                if self.verbose:
                    print(i, '/', n, ' - Downloading Audio ',
                            unit.title, '...', sep='')
                unit.download_audio(
                    self.download_path, convert_to_mp3=self.convert, rename=self.rename)

            except Exception:

                if self.verbose:
                    print('Failed downloading')

            i += 1

    def run(self):

        self.get_links()
        self.save()
        self.download()
        self.save()


if __name__ == '__main__':
    base_path = os.path.abspath(os.path.dirname(__file__))
    config_file = open(os.path.join(base_path, 'folder.txt'), 'r')
    folder = config_file.read()
    path = os.path.join(base_path, folder)
    mainObj = MainProg(verbose=2, download_path=path,choose_again=True)
    mainObj.run()
