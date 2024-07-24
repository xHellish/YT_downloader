# ================================================================================== #
# Librerías
# -------------------------------------------------------------------------------- #
import yt_dlp                                   # Descargar videos yt
import pywhatkit as kit                         # Utilidad / búsqueda
import os                                       # Llamadas al sistema
import wikipedia                                # Obtener info
import requests                                 # Descargar
import wx                                       # Interfaz gráfica

from bs4 import BeautifulSoup                                   # Obtener link de páginas web
from youtubesearchpython import VideosSearch                    # Buscar videos por python
from moviepy.editor import VideoFileClip, AudioFileClip         # Editar videos y audio

# ================================================================================== #
# -------------------------------------------------------------------------------- #
# Variables 
running = True
# -------------------------------------------------------------------------------- #
# ================================================================================== #
# Auxiliares
# ================================================================================== #
# -------------------------------------------------------------------------------- #
# Traductores
# -------------------------------------------------------------------------------- #
def traducir_esp_to_eng(string):
    translator = Translator()
    traduccion = translator.translate(string, src='es', dest='en')
    return traduccion.text
# -------------------------------------------------------------------------------- #
def traducir_eng_to_esp(string):
    translator = Translator()
    traduccion = translator.translate(string, src='en', dest='es')
    return traduccion.text

# ================================================================================== #
# -------------------------------------------------------------------------------- #
# Une un video y un audio de una ruta especificada con ajustes de compresión
def unir_video_audio(video_path, audio_path, output_path):
    try:
        # Cargar el archivo de video y audio
        video_clip = VideoFileClip(video_path)
        audio_clip = AudioFileClip(audio_path)
        
        # Ajustar la duración del audio al del video
        audio_clip = audio_clip.set_duration(video_clip.duration)
        
        # Unir el audio al video y escribir el archivo resultante
        final_clip = video_clip.set_audio(audio_clip)
        
        # Ajustar el bitrate y la calidad de codificación
        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', threads=8, preset='veryfast', bitrate='3000k')
        
        print("Fusión de video y audio completada exitosamente.")
    except Exception as e:
        print(f"Error al unir video y audio: {e}")
# -------------------------------------------------------------------------------- #
# Función que recibe un link de video en YouTube y descarga el video en elo directorio actual
def descargar_video_youtube(link):
    # Opcion para descargar por separado y unir después
    confirm = input("¿Desea máxima calidad de video (puede durar varios minutos)? (y/n): ")

    if confirm == "y":
        # Configuración para descargar video y audio por separado
        ydl_opts_video = {
            'format': 'bestvideo',
            'outtmpl': '%(title)s_video.%(ext)s',  # Guarda el video con el título y "_video" como nombre de archivo
        }
        ydl_opts_audio = {
            'format': 'bestaudio',
            'outtmpl': '%(title)s_audio.%(ext)s',  # Guarda el audio con el título y "_audio" como nombre de archivo
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            'geo_bypass': True,
            'geo_bypass_country': 'US',
        }
        # -------------------------------------------------------------------------------- #
        # Descargar el video
        video_path = ""
        try:
            with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
                result = ydl.extract_info(link, download=True)
                video_path = ydl.prepare_filename(result)
            print("Video descargado con éxito.")
        except Exception as e:
            print(f"Error al descargar el video: {e}")
        # -------------------------------------------------------------------------------- #
        # Descargar el audio
        audio_path = ""
        try:
            with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
                result = ydl.extract_info(link, download=True)
                audio_path = ydl.prepare_filename(result)
            print("Audio descargado con éxito.")
        except Exception as e:
            print(f"Error al descargar el audio: {e}")
        # -------------------------------------------------------------------------------- #
        # Fusionar video y audio si ambos se descargaron correctamente
        if video_path and audio_path:
            output_path = video_path.replace("_video", "")
            unir_video_audio(video_path, audio_path, output_path)

            # Eliminar el audio y el video separados
            os.remove(video_path)
            os.remove(audio_path)

            print("")

        return  
    else:
        ydl_opts = {
            'format': 'best',
            'outtmpl': '%(title)s.%(ext)s',
        }

    # -------------------------------------------------------------------------------- #
    # En caso de no descargar por separado
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        print("Video descargado con éxito.")
    except Exception as e:
        print(f"Error al descargar el video: {e}")

    print("")
    return
# -------------------------------------------------------------------------------- #
# Opción 1
def opcion1_descargar_video_yt():
    link = input("Ingrese link de YouTube: ")
    print("")
    descargar_video_youtube(link)

# ================================================================================== #
def buscar_videos_youtube(query, max_results=5):

    # Realizar la búsqueda en YouTube desde la consola
    videos_search = VideosSearch(query, limit=max_results)
    resultados = videos_search.result()['result']

    links_strings = []

    # Extraer y mostrar la información relevante de los resultados (link, nombre)
    for idx, video in enumerate(resultados):

        video = [video['link'], video['title']]

        # print(f"{idx + 1}. {video['title']}")
        # print(f"   Descripción: {video['descriptionSnippet']}")
        # print(f"   Link: {video['link']}\n")

        links_strings.append(video)

    return links_strings

# -------------------------------------------------------------------------------- #
# Opción 2
def opcion2_buscar_videos_yt():
    # Búsqueda en YouTube
    query = input("Buscar: ")
    print("")

    try:

        buscar_videos_youtube(query, max_results=5)
    except Exception as e:
        print(f"Error en opción 2: {e}")

# ================================================================================== #
# Opción 3
def opcion3_buscar_video_yt(query):
    # Búsqueda en YouTube para abrir navegador
    kit.playonyt(query)

# ================================================================================== #
def obtener_wiki_info_es(query):
    try:
        wikipedia.set_lang("es")
        page = wikipedia.page(query)
        summary = wikipedia.summary(query, sentences=2)
        return summary

    except wikipedia.exceptions.WikipediaException as e:
        return f"No se encontró información para '{query}' en Wikipedia."

# -------------------------------------------------------------------------------- #
# Opción 4
def opcion4_buscar_info_wikipedia():
    # Obtener información de Wikipedia
    query = input("Buscar: ")
    print("")
    print(obtener_wiki_info_es(query))
    print("")

# ================================================================================== #
def descargar_pdf(url, output_folder='./'):
    response = requests.get(url)
    if response.status_code == 200:
        file_name = url.split('/')[-1]
        file_path = os.path.join(output_folder, file_name)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"PDF descargado exitosamente: {file_path}")
    else:
        print(f"Error al descargar el PDF: {response.status_code}")
# -------------------------------------------------------------------------------- #        
def buscar_pdfs_duckduckgo(query, max_results=5):
    search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}+filetype:pdf"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extraer los enlaces de los resultados de búsqueda
    links = []
    for item in soup.find_all('a', class_='result__a'):
        href = item.get('href')
        if href and '.pdf' in href:
            links.append(href)
            if len(links) >= max_results:
                break

    return links
# -------------------------------------------------------------------------------- #
# Opción 5
def opcion5_buscar_y_descargar_pdf():
    query = input("Buscar PDF: ")
    print("")

    try:
        enlaces_pdf = buscar_pdfs_duckduckgo(query, max_results=5)
        for idx, link in enumerate(enlaces_pdf):
            print(f"{idx + 1}. {link} \n")

        opcion = int(input("Digite número de PDF a descargar (0 para cancelar): "))
        print("")

        if opcion in range(1, len(enlaces_pdf) + 1):
            descargar_pdf(enlaces_pdf[opcion - 1])
        elif opcion == 0:
            return
        else:
            print("Opción incorrecta")
    except Exception as e:
        print(f"Error en opción 5: {e}")

# ================================================================================== # 
# Crear una clase para la aplicación
# -------------------------------------------------------------------------------- #

def on_button_buscar_click(event):
    texto_busqueda_usuario = text_box_buscar.GetValue()
    opcion_actual = combo_box_opciones.GetValue()

    print(texto_busqueda_usuario)
    print("")
    print(opcion_actual)

    if opcion_actual == "YouTube":
        lista_links_videos = buscar_videos_youtube(texto_busqueda_usuario, max_results=5)


        coordenada_y_videos = 100
        for video in lista_links_videos:
            label = wx.StaticText(panel_principal, label=f"{video[1]} | link: {video[0]}", pos=(20, coordenada_y_videos))
            coordenada_y_videos = coordenada_y_videos + 100

# Crear la aplicación
app = wx.App(False)
frame1 = wx.Frame(None, title="Stuff Downloader", size=(1280, 720))

# Crear un panel para contener los widgets
panel_principal = wx.Panel(frame1)

# -------------------------------------------------------------------------------- #
# Botones
buscar_button = wx.Button(panel_principal, label="Iniciar búsqueda", pos=(430, 20), size=(150, 30))
buscar_button.Bind(wx.EVT_BUTTON, on_button_buscar_click)

# -------------------------------------------------------------------------------- #
# Crear un ComboBox y agregar opciones
combo_box_opciones = wx.ComboBox(panel_principal, choices=['YouTube', 'PDF', 'Wikipedia'], style=wx.CB_READONLY)

# Enlazar el evento de selección del ComboBox a la función correspondiente
combo_box_opciones.SetPosition((590, 21))
combo_box_opciones.SetSize((100, 28))

# -------------------------------------------------------------------------------- #
# Crear un Label
label_formato_combobox = wx.StaticText(panel_principal, label="Formato", pos=(595, 23))
label_formato_combobox.SetBackgroundColour(wx.Colour(255, 255, 0))  # Amarillo
# -------------------------------------------------------------------------------- #
# Text input del usuario
text_box_buscar = wx.TextCtrl(panel_principal, pos=(20, 20), size=(400, 30))

font_textbox = wx.Font(16, wx.SWISS, wx.NORMAL, wx.BOLD)
text_box_buscar.SetFont(font_textbox)

# Mostrar la ventana
frame1.Show()

# Ejecutar el bucle principal de eventos
app.MainLoop()

# ================================================================================== #
# Running
while running:
    print("-----============== < MENU > ==============-----")
    print("1. Descargar video de YT")
    print("2. Buscar video en YT")
    print("3. Buscar video en YT (abrir navegador)")
    print("4. Info - wikipedia")
    print("5. Buscar PDF")
    print("0. Salir")
    # ------------------------------------------------------------- #
    
    try:
        opcion = int(input("Opción: "))

        if opcion in [0, 1, 2, 3, 4, 5]:
            if opcion == 0:
                print("Saliendo...")
                running = False

            if opcion == 1:
                opcion1_descargar_video_yt()

            if opcion == 2:
                opcion2_buscar_videos_yt()
                
            if opcion == 3:
                opcion3_buscar_video_yt()

            if opcion == 4:
                opcion4_buscar_info_wikipedia()

            if opcion == 5:
                opcion5_buscar_y_descargar_pdf()

        else:
            print("Opción Incorrecta")

    except:
        print("Error innesperado, intenta nuevamente...")
    # ------------------------------------------------------------- #

# ================================================================================== #
# End of code
