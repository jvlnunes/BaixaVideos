from pytubefix import YouTube

def download_video(url):
    try:
        YouTube(url).streams.first().download()
    except: 
        print("Não foi possível baixar o vídeo")
         
def download_audio(url, output_path):
    try:
        video_audio = YouTube(url).streams.filter(only_audio=True).first()
        title = video_audio.title
        filename = title + ".mp3"
        
        video_audio.download(output_path=output_path, filename=filename)
        
        print(f"Download concluído -> {filename}")
        
    except:
        print("Não foi possível baixar o vídeo com esse link -> " + url)