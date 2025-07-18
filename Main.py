from customtkinter import * # GUI
from PIL import Image # GUI
import webbrowser  # Link do Twitter
from yt_dlp import YoutubeDL # Download do Video
from CTkMessagebox import CTkMessagebox # GUI
import os # Diretório do Computador
import threading # Processos em Segundo Plano
import requests # Baixar dados
from io import BytesIO # Criar Arquivo

base_path = os.path.dirname(os.path.abspath(__file__))

Titulo_video = None
Thumb_video = None
#Funções
def centralizar(janela, largura, altura):
    largura_janela = largura
    altura_janela = altura
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    pos_x = int((largura_tela/2) - (largura_janela/2))
    pos_y = int((altura_tela/2) - (altura_janela/2))
    janela.geometry(f'{largura_janela}x{altura_janela}+{pos_x}+{pos_y}')
def telaajuda():
    CTkMessagebox(title='Ajuda', message='1-Coloque o link do vídeo ou da playlist, e em seguida aperte na lupa ao lado\n''\n'
                                         '2-Escolha o formato do arquivo\n''\n'
                                         '3-Clique no ícone de download.\n''\n'
                                         'Todo conteúdo baixado estará na pasta YoutubeDownloader que é criada automaticamente na pasta Downloads.'
                  , icon='question', option_1='Ok')

def abrirtwitter():
    url = 'https://linktr.ee/rafssunny'
    navegador = webbrowser.get()
    navegador.open(url)

def pegarvideo():
    url = LinkVideo.get()
    def conseguirtitulo():
        global Titulo_video, Thumb_video
        if Titulo_video:
            Titulo_video.destroy()
        if Thumb_video:
            Thumb_video.destroy()
        barraprogresso = CTkProgressBar(janela, width=100, progress_color='#ADD8E6')
        barraprogresso.place(x=350, y=220)
        barraprogresso.start()
        try:
            opcoes = {
                'quiet':True,
                'skip_download':True
            }
            with YoutubeDL(opcoes) as ydl:
                info = ydl.extract_info(url, download=False)
        except:
            CTkMessagebox(janela, message='Vídeo não encontrado. Cheque se a URL está correta.', icon='cancel', title='ERRO')
        else:
            Titulo_video = CTkLabel(janela, width=200, height=10, text=info['title'], font=('comic sans ms', 12), wraplength=300)
            Titulo_video.place(x=15, y=340)
            request_thumb = requests.get(info['thumbnail'])
            Thumbnail = Image.open(BytesIO(request_thumb.content))
            thumb_ctk = CTkImage(dark_image=Thumbnail, size=(220, 140))
            Thumb_video = CTkLabel(janela, image=thumb_ctk, width=200, height=100, text='')
            Thumb_video.place(x=15, y=200)
        barraprogresso.destroy()
    segundoplano = threading.Thread(target=conseguirtitulo)
    segundoplano.start()
def baixarvideo():
    formato = formato_arquivo.get()
    url = LinkVideo.get()
    if not url.strip():
        CTkMessagebox(janela, message='Nenhum link foi inserido.', icon='cancel', option_1='Ok', title='ERRO')
        return
    try:
        with YoutubeDL({'quiet':True, 'skip_download':True}) as ydl:
            info = ydl.extract_info(url, download=False)
    except:
        CTkMessagebox(janela, message='Não é possível fazer download. Cheque se a URL está correta.', icon='cancel', option_1='Ok', title='ERRO')
    else:
        segundoplano = threading.Thread(target=executardownload, args=(url, formato))
        segundoplano.start()
def executardownload(url, formato):
    pasta_download = os.path.join(os.path.expanduser('~'), 'Downloads')
    pasta_programa = os.path.join(pasta_download, 'YoutubeDownloader')
    if not os.path.exists(pasta_programa):
        os.makedirs(pasta_programa)
    opcoes = {
        'outtmpl': os.path.join(pasta_programa, '%(title)s.%(ext)s'),
        'progress_hooks': [atualizarprogresso],
    }
    if formato == 'Webm':
        opcoes['format'] = 'bestaudio/best'
        opcoes['postprocessors'] = [{
            'key':'FFmpegExtractAudio',
            'preferredcodec':'mp3',
            'preferredquality':'192',
        }]
    if formato == 'Mp4':
        opcoes['format'] = 'best'

    with YoutubeDL(opcoes) as ydl:
        ydl.download([url])

def atualizarprogresso(d):
    Barraprogresso = CTkProgressBar(janela, width=100, progress_color='green')
    Barraprogresso.place(x=350, y=355)
    Barraprogresso.set(0)
    if d.get('status') == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded_bytes = d.get('downloaded_bytes')
        if total_bytes:
            progresso = downloaded_bytes/total_bytes
            Barraprogresso.set(progresso)
    elif d.get('status') == 'finished':
        Barraprogresso.set(1)
        CTkMessagebox(janela, message='Finalizado com sucesso!', icon='check', option_1='Ok', title='Finalizado')
        Barraprogresso.destroy()

#Janela Principal
janela = CTk()
try:
    caminho_icone = os.path.join(base_path, 'iconeprograma.ico')
    janela.wm_iconbitmap(caminho_icone)
except Exception as e:
    print('erro')
janela.title('YouTube Downloader')
centralizar(janela, 600, 400)
janela.resizable(width=False, height=False)
janela._set_appearance_mode('dark')


#Logo do Programa e Título
Imagem = CTkImage(dark_image=Image.open(os.path.join(base_path, 'logoyoutube.png')), size=(150, 150))
CTkLabel(janela, text='', image=Imagem).place(x=0,y=0)
Titulo = CTkLabel(janela, text=(f'Youtube Downloader'), font=('comic sans ms', 45)).place(x=160, y=40)
Subtitulo = CTkLabel(janela, text=('feito por rafssunny'), font=('comic sans ms', 20)).place(x=265, y=100)


#Botões
LinkVideo = CTkEntry(janela,width=300,placeholder_text='Insira o link do vídeo...')
LinkVideo.place(x=245, y=235)
LinkVideo.bind('<Return>', lambda  event : pegarvideo())

lupa_icone = CTkImage(dark_image=Image.open(os.path.join(base_path, 'lupa.png')), size=(21,21))
Botao_pequisar = CTkButton(janela, width=10, height=10, text='', image=lupa_icone, fg_color='transparent',hover_color='black',
                           bg_color='transparent', command=pegarvideo).place(x=545, y=234)

formato_arquivo = CTkOptionMenu(janela, values=['Mp4', 'Webm'], fg_color='gray', button_hover_color='black', button_color='gray',
                                dropdown_hover_color='black')
formato_arquivo.place(x=330, y=270)

Download_image = CTkImage(dark_image=Image.open(os.path.join(base_path, 'download.png')), size=(40,40))
Download = CTkButton(janela, fg_color='#2b2b2b', bg_color='transparent', image=Download_image, corner_radius=999, text='',
                     width=0, height=0, border_width=1, hover_color='green', border_color='green', command=baixarvideo)
Download.place(x=375, y=300)


#Thumb video
Thumb = CTkFrame(janela, width=200, height=150).place(x=15, y=200)


#Como usar e Twitter
Duvida = CTkButton(janela, width=50, text='?', text_color='white', font=('comic sans ms', 30), fg_color='gray'
                   , hover_color='black', command=telaajuda, border_color='white', border_width=1).place(x=550, y=350)
Img_twitter = CTkImage(dark_image=Image.open(os.path.join(base_path, 'twitter.png')), size=(40,40))
CTkButton(janela, image=Img_twitter, text='', width=0, height=0, corner_radius=20, fg_color='#1DA1F2', border_width=1, border_color=
          'white', command=abrirtwitter).place(x=500,y=350)

janela.mainloop()
