from functions import *

urls = [
        'https://www.youtube.com/watch?v=PTtxF46h1Ig&ab_channel=Revibes-Topic'          
    ]

path_pasta_download = 'C://Users//jv//Music//Baixadas//Novos'
# verifica_arquivo(file_path)

for url in urls:
    file_path, title = download_audio(url, path_pasta_download)
    convert_to_wav(file_path, path_pasta_download + '/WAV/' + title + '.wav')

