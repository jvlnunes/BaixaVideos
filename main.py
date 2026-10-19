from functions import *

urls = [
        'https://www.youtube.com/watch?v=9vMh9f41pqE&list=RD9vMh9f41pqE&start_radio=1'
    ]

path_pasta_download = 'downloads'
# verifica_arquivo(file_path)

for url in urls:
    file_path, title = download_audio(url, path_pasta_download)
    convert_to_wav(file_path, path_pasta_download + '/WAV/' + title + '.wav')

