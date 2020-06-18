import os

for a,b,files in os.walk('./Music'):
    for file in files:
        os.rename(os.path.join(a,file),os.path.join(a,os.path.splitext(file)[0]+'.mp3'))
