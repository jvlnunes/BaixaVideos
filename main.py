from functions import *

urls = [
        # 'https://www.youtube.com/watch?v=M-h2KwQ2o4Q&ab_channel=distress',
        # 'https://www.youtube.com/watch?v=UMl2sMpzs-E&ab_channel=NovaMTG',
        'https://www.youtube.com/watch?v=fVK6nkRyZ-E&ab_channel=Revibes'
             
    ]

path_pasta_download = 'C://Users//jv//Music//Baixadas//Novos'

# verifica_arquivo(file_path)

for url in urls:
    file_path, title = download_audio(url, path_pasta_download)
    # convert_to_wav(file_path, path_pasta_download + '/WAV/' + title + '.wav')

