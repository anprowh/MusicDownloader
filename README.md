# MusicDownloader
Downloads Audio from YouTube

### How to use

  1. Open titles.txt file.
  2. Type line by line all the titles you want to download. These will be YouTube search requests and filenames. Don't use symbols prohibited in filenames (like ':').
  3. Run main.py by typing in comand line either "python main.py" or "python3 main.py" (without quatation marks).
  4. Wait till program finishes.
  5. Find your audio in Music folder.

### Notes: 
  1. after finding link on relevant YouTube video for all unprocessed titles it will add all the links to titles.txt. If there is such link search will not be proceeded. 
  * You can remove this link and special symbol (" -> ") to proceed seach again.
  2. after processing all the titles it will add '-' symbol in front of each title in titles.txt which means that this title is deactivated and will not be processed again. 
  * You can remove this mark to process this title again.
