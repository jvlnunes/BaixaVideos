# from pytube import YouTube
from pytubefix import YouTube
# from pydub import AudioSegment
# import ffmpeg
import os
import re

def clean_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def download_video(url):
    try:
        YouTube(url).streams.first().download()
        
    except Exception as e: 
        print("Não foi possível baixar o vídeo:"+ e)

def download_audio(url, output_path, format='wav'):
    try:
        video = YouTube(url).streams.filter(only_audio=True).first()
        title = clean_filename(video.title)

        temp_file = video.download(output_path=output_path, filename=title+".mp4")

        novo_nome = os.path.join(output_path, title + f".{format}")
        os.rename(temp_file, novo_nome)

        print(f"Download concluído -> {novo_nome}")

    except Exception as e:
        print("download_audio: Não foi possível baixar o vídeo com esse link -> " + url + ": " + str(e))
        
        
        