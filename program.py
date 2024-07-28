# ================================================================================== #
# Librerías
# -------------------------------------------------------------------------------- #
import yt_dlp                                   # Descargar videos yt
import pywhatkit as kit                         # Utilidad / búsqueda
import os                                       # Llamadas al sistema
import wikipedia                                # Obtener info
import requests                                 # Descargar
import wx                                       # Interfaz gráfica
import fitz                                     # PyMuPDF
import wx.html2

# Ver video de youtube en un panel
import wx.html2 as webview
import re
import time

from urllib.parse import urlparse                               # Nombre de archivos
from pdf2image import convert_from_bytes                        # Obtener miniatura de pdf
from io import BytesIO                                          # Conversor de formato
from PIL import Image                                           # Miniaturas yt
from bs4 import BeautifulSoup                                   # Obtener link de páginas web
from youtubesearchpython import VideosSearch                    # Buscar videos por python
from moviepy.editor import VideoFileClip, AudioFileClip         # Editar videos y audio

# ================================================================================== #
# -------------------------------------------------------------------------------- #
# Variables 
running = True
global panel_secundario, text_box_buscar, progress_bar
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
# Descargar audio YouTube
def descargar_audio_youtube(link):
    progress_bar = wx.Gauge(panel_secundario, range=100, pos=(20, 550), size=(1000, 25))
    progress_bar.Raise()

    ydl_opts_audio = {
        'format': 'bestaudio',
        'outtmpl': '%(title)s_audio.%(ext)s',  # Guarda el audio con el título y "_audio" como nombre de archivo
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        },
        'geo_bypass': True,
        'geo_bypass_country': 'US',
        'progress_hooks': [lambda d: progress_bar_audio(d, progress_bar)],
    }

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
# Función que recibe un link de video en YouTube y descarga el video en el directorio actual
def descargar_video_youtube(link):
    # Descarga por separado y unir después
    progress_bar = wx.Gauge(panel_secundario, range=100, pos=(20, 550), size=(1000, 25))
    progress_bar.Raise()

    actualizar_progreso(progress_bar, 0, 1)

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

    actualizar_progreso(progress_bar, 1, 10)
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

    actualizar_progreso(progress_bar, 10, 40)
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

    actualizar_progreso(progress_bar, 40, 60)
    # -------------------------------------------------------------------------------- #
    # Fusionar video y audio si ambos se descargaron correctamente
    if video_path and audio_path:
        output_path = video_path.replace("_video", "")
        unir_video_audio(video_path, audio_path, output_path)

        # Eliminar el audio y el video separados
        os.remove(video_path)
        os.remove(audio_path)

    actualizar_progreso(progress_bar, 60, 100)
    progress_bar.Destroy()
    return 

# ================================================================================== #
def buscar_videos_youtube(query, max_results=5):

    # Realizar la búsqueda en YouTube desde la consola
    videos_search = VideosSearch(query, limit=max_results)
    resultados = videos_search.result()['result']
    links_strings = []

    # Extraer y mostrar la información relevante de los resultados (link, nombre)
    for idx, video in enumerate(resultados):
        video = [video['link'], video['title'], video["thumbnails"][0]["url"]]
        links_strings.append(video)

    return links_strings

# ================================================================================== #
def obtener_wiki_info_es(query):
    try:
        wikipedia.set_lang("es")
        page = wikipedia.page(query)
        summary = wikipedia.summary(query, sentences=2)
        return summary

    except wikipedia.exceptions.WikipediaException as e:
        return f"No se encontró información para '{query}' en Wikipedia."

# ================================================================================== #
def descargar_pdf(pdf_url):

    try:
        # Enviar una solicitud GET al enlace del PDF
        response = requests.get(pdf_url, stream=True)
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            # Obtener el nombre del archivo desde el enlace
            parsed_url = urlparse(pdf_url)
            nombre_archivo = os.path.basename(parsed_url.path)
            
            # Guardar el contenido del PDF en un archivo
            with open(nombre_archivo, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"PDF descargado con éxito como {nombre_archivo}.")
        else:
            print(f"Error al descargar el PDF: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar el PDF: {e}")

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
def ver_pdf_ventana(link):
    pass

# ================================================================================== # 
# Crear gráfico de la aplicación
# -------------------------------------------------------------------------------- #
# Progress bar
def actualizar_progreso(progress_bar, progreso_barra_actual, progreso_nuevo):

    for i in range(progreso_barra_actual, progreso_nuevo, 1):
        progress_bar.SetValue(progreso_barra_actual + i)
        wx.GetApp().Yield()
        time.sleep(0.05)
    return

def progress_bar_audio(d, progress_bar):
    if d['status'] == 'downloading':
        percent = d['downloaded_bytes'] / d['total_bytes'] * 100
        wx.CallAfter(progress_bar.SetValue, int(percent))

# -------------------------------------------------------------------------------- #
# Llamada del botón ver video
def on_button_ver_click_window(link):

    # Ver video en panel
    def obtener_video_id(url):
        """ Extrae el ID del video de YouTube de la URL. """
        video_id_match = re.search(r'v=([a-zA-Z0-9_-]+)', url)
        if video_id_match:
            return video_id_match.group(1)
        return ''

    def on_button_ver_click(link):
        video_id = obtener_video_id(link)
        if video_id:
            video_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1"
            webview_window.LoadURL(video_url)
            # Usar un temporizador para iniciar la reproducción después de cargar
            wx.CallLater(2000, play_video)
        else:
            wx.MessageBox("ID de video no encontrado.", "Error", wx.OK | wx.ICON_ERROR)

    def play_video():
        # Intentar ejecutar un script en la página para iniciar la reproducción
        script = "document.querySelector('video').play();"
        webview_window.RunScript(script)

    # -------------------------------------------------------------------------------- #
    # Ventana secundaria para reproducir video
    app2 = wx.App(False)
    frame = wx.Frame(None, title="Reproductor de Video de YouTube", size=(800, 600))

    panel_video1 = wx.Panel(frame)
    sizer = wx.BoxSizer(wx.VERTICAL)

    # Crear WebView
    webview_window = webview.WebView.New(panel_video1)
    sizer.Add(webview_window, 1, wx.EXPAND)

    panel_video1.SetSizer(sizer)

    frame.Centre()
    frame.Show()

    # Llamar a la reproducción del video en la ventana
    on_button_ver_click(link)

    app2.MainLoop()

# -------------------------------------------------------------------------------- #
# Obtener imagen de la miniatura con la url
def obtener_miniatura(url): 
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    return image

# Convertir imagen a un formato que wx admita
def pil_image_to_wx_bitmap(pil_image):
    with BytesIO() as bio:
        pil_image.save(bio, format="PNG")
        bio.seek(0)
        wx_image = wx.Image(bio)
        if not wx_image.IsOk():
            raise ValueError("No se pudo convertir la imagen a wx.Image")
        bitmap = wx_image.ConvertToBitmap()
    return bitmap

def redimensionar_imagen(pil_image, size=(150, 90)):
    return pil_image.resize(size, Image.LANCZOS)

# -------------------------------------------------------------------------------- #
# Miniatura de PDF
def obtener_miniatura_pdf(url_pdf, tamano_miniatura=(200, 200)):
    response = requests.get(url_pdf)
    contenido_pdf = response.content

    # Cargar el PDF en PyMuPDF
    documento = fitz.open("pdf", contenido_pdf)
    pagina = documento.load_page(0)  # Obtener la primera página

    # Obtener una imagen de la primera página
    pix = pagina.get_pixmap()
    imagen = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # Redimensionar la imagen a la miniatura
    imagen.thumbnail(tamano_miniatura)

    # Guardar la miniatura en un objeto BytesIO
    miniatura_io = BytesIO()
    imagen.save(miniatura_io, format='PNG')
    miniatura_io.seek(0)

    return miniatura_io
# -------------------------------------------------------------------------------- #

def on_button_buscar_click(event):
    texto_busqueda_usuario = text_box_buscar.GetValue()
    opcion_actual = combo_box_opciones.GetValue()

    # Eliminar todos los widgets del panel secundario
    for child in panel_secundario.GetChildren():
        child.Destroy()

    panel_secundario.Layout()

    if opcion_actual == "YouTube":
        lista_links_videos = buscar_videos_youtube(texto_busqueda_usuario, max_results=5)

        coordenada_y_videos = 20
        for video in lista_links_videos:
            link, titulo, miniatura_url = video
            miniatura_image = obtener_miniatura(miniatura_url)
            miniatura_image = redimensionar_imagen(miniatura_image)
            
            # Convertir la imagen de PIL a wx.Bitmap
            miniatura_bitmap = pil_image_to_wx_bitmap(miniatura_image)

            # Crear StaticBitmap para la miniatura
            miniatura_bitmap_ctrl = wx.StaticBitmap(panel_secundario, bitmap=miniatura_bitmap, pos=(20, coordenada_y_videos))

            # Crear StaticText para el título
            label_title = wx.StaticText(panel_secundario, label=f"{titulo}", pos=(180, coordenada_y_videos))
            label_link = wx.StaticText(panel_secundario, label=f"{link}", pos=(180, coordenada_y_videos + 20))

            # Cambiar el tamaño del texto del StaticText
            font_label_title = wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
            label_title.SetFont(font_label_title)

            font_label_link = wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
            label_link.SetFont(font_label_link)

            descargar_video_button = wx.Button(panel_secundario, label="Descargar Video", pos=(180, coordenada_y_videos + 40), size=(150, 30))
            descargar_video_button.Bind(wx.EVT_BUTTON, lambda event, link=link: descargar_video_youtube(link))

            descargar_audio_button = wx.Button(panel_secundario, label="Descargar m4a", pos=(335, coordenada_y_videos + 40), size=(150, 30))
            descargar_audio_button.Bind(wx.EVT_BUTTON, lambda event, link=link: descargar_audio_youtube(link))

            ver_video_button = wx.Button(panel_secundario, label="Ver", pos=(490, coordenada_y_videos + 40), size=(150, 30))
            ver_video_button.Bind(wx.EVT_BUTTON, lambda event, link=link: on_button_ver_click_window(link))
            
            coordenada_y_videos += 100

    if opcion_actual == "PDF":

        links_pdf = buscar_pdfs_duckduckgo(texto_busqueda_usuario, max_results=5)

        coordenada_y_pdfs = 20
        for pdf_url in links_pdf:

            try :
                # Miniatura de cada pdf
                miniatura_io = obtener_miniatura_pdf(pdf_url)
                miniatura_imagen = Image.open(miniatura_io)
                miniatura_imagen = redimensionar_imagen(miniatura_imagen, size=(90, 150))
                miniatura_bitmap = pil_image_to_wx_bitmap(miniatura_imagen)
                miniatura_bitmap_ctrl = wx.StaticBitmap(panel_secundario, bitmap=miniatura_bitmap, pos=(20, coordenada_y_pdfs))

                # Crear StaticText para el título
                label_title = wx.StaticText(panel_secundario, label=f"{pdf_url}", pos=(180, coordenada_y_pdfs))

                # Cambiar el tamaño del texto del StaticText
                font_label_title = wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
                label_title.SetFont(font_label_title)

                descargar_pdf_button = wx.Button(panel_secundario, label="Descargar PDF", pos=(180, coordenada_y_pdfs + 40), size=(150, 30))
                descargar_pdf_button.Bind(wx.EVT_BUTTON, lambda event, pdf_url=pdf_url: descargar_pdf(pdf_url))

                leer_pdf_button = wx.Button(panel_secundario, label="Leer PDF", pos=(335, coordenada_y_pdfs + 40), size=(150, 30))
                leer_pdf_button.Bind(wx.EVT_BUTTON, lambda event, pdf_url=pdf_url: descargar_pdf(pdf_url))
                
                coordenada_y_pdfs += 170

            except:
                # Crear StaticText para el título
                label_title = wx.StaticText(panel_secundario, label=f"{pdf_url}", pos=(180, coordenada_y_pdfs))

                # Cambiar el tamaño del texto del StaticText
                font_label_title = wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
                label_title.SetFont(font_label_title)

                descargar_pdf_button = wx.Button(panel_secundario, label="Descargar PDF", pos=(180, coordenada_y_pdfs + 40), size=(150, 30))
                descargar_pdf_button.Bind(wx.EVT_BUTTON, lambda event, pdf_url=pdf_url: descargar_pdf(pdf_url))

                leer_pdf_button = wx.Button(panel_secundario, label="Leer PDF", pos=(335, coordenada_y_pdfs + 40), size=(150, 30))
                leer_pdf_button.Bind(wx.EVT_BUTTON, lambda event, pdf_url=pdf_url: descargar_pdf(pdf_url))
                
                coordenada_y_pdfs += 170

    if opcion_actual == "Wikipedia":
        url_wikipedia = f"https://es.wikipedia.org/wiki/{texto_busqueda_usuario}"
        
        # Crear un WebView y cargar la página de Wikipedia
        webview = wx.html2.WebView.New(panel_secundario, pos=(10, 0), size=(1205, 620))
        webview.LoadURL(url_wikipedia)

    # Llamar al Layout del panel_secundario para actualizar la disposición
    panel_secundario.Layout()

# ================================================================================== # 
# Crear la aplicación
# -------------------------------------------------------------------------------- #
app = wx.App(False)
frame1 = wx.Frame(None, title="Stuff Downloader", size=(1280, 720), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))

# Crear un panel principal
panel_principal = wx.Panel(frame1)
panel_principal.SetBackgroundColour(wx.Colour(255, 255, 255))  # Fondo blanco para el panel principal

# Crear un panel de desplazamiento para el panel secundario
scrolled_window = wx.ScrolledWindow(panel_principal)
scrolled_window.SetScrollRate(20, 20)

# Crear un panel secundario dentro del panel de desplazamiento
panel_secundario = wx.Panel(scrolled_window)
panel_secundario.SetBackgroundColour(wx.Colour(200, 200, 200))  # Color de fondo gris

# Agregar el panel secundario al panel de desplazamiento
scrolled_window.SetScrollRate(20, 20)  # Opcional: Configura la tasa de desplazamiento
scrolled_window.SetVirtualSize((1230, 800))  # Tamaño virtual del panel de desplazamiento

# Crear un botón
buscar_button = wx.Button(panel_principal, label="Iniciar búsqueda", pos=(540, 20), size=(150, 30))
buscar_button.Bind(wx.EVT_BUTTON, on_button_buscar_click)

# Crear un ComboBox y agregar opciones
combo_box_opciones = wx.ComboBox(panel_principal, choices=['YouTube', 'PDF', 'Wikipedia'], style=wx.CB_READONLY)
combo_box_opciones.SetPosition((430, 21))
combo_box_opciones.SetSize((100, 28))

# Crear un Label
label_formato_combobox = wx.StaticText(panel_principal, label="Formato", pos=(435, 23))
label_formato_combobox.SetBackgroundColour(wx.Colour(255, 255, 0))  # Amarillo

# Text input del usuario
text_box_buscar = wx.TextCtrl(panel_principal, pos=(20, 20), size=(400, 30))
font_textbox = wx.Font(16, wx.SWISS, wx.NORMAL, wx.BOLD)
text_box_buscar.SetFont(font_textbox)

# Ajustar el tamaño del panel secundario y del ScrolledWindow
panel_secundario.SetSize((1230, 800))  # Ajustar el tamaño del panel secundario
scrolled_window.SetSize((1280, 720))    # Tamaño del panel de desplazamiento

# Posicionar el panel de desplazamiento en el panel principal
scrolled_window.SetPosition((20, 60))

# Mostrar la ventana
frame1.Show()

# Ejecutar el bucle principal de eventos
app.MainLoop()

# ================================================================================== #
# End of code
