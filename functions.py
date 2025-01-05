# from pytube import YouTube
from pytubefix import YouTube
import unicodedata
import os
import re

import wave
import contextlib

import subprocess

def clean_filename(filename):
    filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode('ASCII')
    return re.sub(r'[<>:"/\\|?*]', '', filename)

# def clean_filename(filename):
#     # Remove any non-ASCII characters
#     filename = re.sub(r'[^\x00-\x7F]+', '', filename)
#     # Remove any special characters
#     filename = re.sub(r'[^a-zA-Z0-9\s.-]+', '', filename)
#     # Replace any spaces with underscores
#     filename = filename.replace(' ', '_')
#     return filename

def verifica_arquivo(file_path):
    with contextlib.closing(wave.open(file_path, 'r')) as f:
        params = f.getparams()
        print(f"Parâmetros do WAV: {params}")

def get_files_paths(folder_path):
    paths = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        # print(file_path)
        paths.append(file_path)
        
    return paths

def download_video(url):
    try:
        YouTube(url).streams.first().download()
        
    except Exception as e: 
        print("Não foi possível baixar o vídeo:"+ e)

def download_audio(url, output_path, format='.mp3'):
    try:
        video = YouTube(url).streams.filter(only_audio=True).first()
        title = clean_filename(video.title)

        temp_file = video.download(output_path=output_path, filename=title+".mp4")

        novo_nome = os.path.join(output_path, title + f".{format}")
        os.rename(temp_file, novo_nome)

        print(f"Download concluído -> {novo_nome}")
        return novo_nome, title

    except Exception as e:
        print("download_audio: Não foi possível baixar o vídeo com esse link -> " + url + ": " + str(e))
        
def convert_file_to_wav(directory_path):
        
    files_paths = get_files_paths(directory_path)

    for file_path in files_paths: 
        if file_path.endswith('.wav'):  
            title = os.path.basename(file_path)

            input_path = os.path.join(directory_path, title)
            output_path = os.path.join(directory_path, 'Novos', 'WAV', title)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if not os.path.exists(input_path):
                print(f"Erro: O arquivo {input_path} não foi encontrado.")
                continue

            print(f"Arquivo de entrada: {input_path}")
            print(f"Arquivo de saída: {output_path}\n")
            
            # Converter para WAV
            convert_to_wav(input_path, output_path)

    
def convert_to_wav(input_file_payh, output_file_path):
    try:
        if not os.path.exists(input_file_payh):
            print(f"Erro: O arquivo {input_file_payh} não foi encontrado.")
            return None

        input_file_payh  = input_file_payh.replace("\\", "/")
        output_file_path = output_file_path.replace("\\", "/")

        command = [
            "ffmpeg",
            "-i", input_file_payh,          
            "-ar", "44100",           
            "-ac", "2",               
            "-b:a", "1411k",          
            "-f", "wav",              
            output_file_path               
        ]

        result = subprocess.run(command, check=True, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Erro no FFmpeg: {result.stderr}")
            return None

        print(f"Conversão concluída: {output_file_path}")
        return output_file_path

    except Exception as e:
        print(f"Erro ao converter o arquivo: {e}")
        return None
