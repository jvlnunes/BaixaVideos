from functions import *

urls = [
        'https://www.youtube.com/watch?v=gd2nlpGr9u4&ab_channel=PMM'  ,
        'https://www.youtube.com/watch?v=ODPqIix0tU0&ab_channel=PMM'  ,
        'https://www.youtube.com/watch?v=8jTXr2mwiWQ&ab_channel=Leod' ,
        'https://www.youtube.com/watch?v=GMnV6jsDwlQ&ab_channel=Leod' ,
        'https://www.youtube.com/watch?v=yHbR-KtJC9I&ab_channel=Leod' ,
        'https://www.youtube.com/watch?v=n--UDPEG_Xc&ab_channel=Leod' ,
        'https://www.youtube.com/watch?v=9NqWHAacMBQ&ab_channel=Leod' ,
        'https://www.youtube.com/watch?v=vV196a3vaaY&ab_channel=Leod' ,
        'https://www.youtube.com/watch?v=jfSRqd9De8A&ab_channel=Leod'
    ]

path_pasta_download = 'C:/Users/jv/Music'

for url in urls:
    download_audio(url, path_pasta_download)
    