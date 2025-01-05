from functions import *

urls = [
        'https://www.youtube.com/watch?v=o6O3sgnyY9g&ab_channel=S%CE%94%E2%80%A0IERF',
        'https://www.youtube.com/watch?v=-lxZulr2Ak8&ab_channel=GabrielMzero',
        'https://www.youtube.com/watch?v=5VkqPqr45U4&ab_channel=GabrielMzero',
        'https://www.youtube.com/watch?v=GMYMhrS00fY&ab_channel=GabrielMzero',
        'https://www.youtube.com/watch?v=lWUBUrNNfPM&ab_channel=GabrielMzero',      
    ]

path_pasta_download = 'C:/Users/jv/Music/Baixadas'

for url in urls:
    download_audio(url, path_pasta_download, 'wav')
    