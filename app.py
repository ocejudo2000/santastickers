import streamlit as st
from TTS.api import TTS
from pydub import AudioSegment
from ftplib import FTP
import os
import uuid

# Configuración de la conexión SFTP
FTP_HOST = 'http://www.nitrodata.com.mx'
FTP_PORT = 21  # Puerto por defecto para SFTP
FTP_USER = 'ocejudo@nitrodata.com.mx'
FTP_PASS = 'OrionPaola2%$'
FTP_DIR = '/home/nitrodat/domains/nitrodata.com.mx'  # Directorio en el servidor donde se guardará el archivo

# Inicializa TTS con un modelo preentrenado en español
tts = TTS(model_name="tts_models/es/mai/tacotron2-DDC", progress_bar=False, gpu=False)

# Título de la aplicación
st.title('Conversor de Texto a Voz con Música de Fondo')

# Entrada de texto del usuario
texto = st.text_area('Ingresa el texto en español que deseas convertir a voz:')

# Selección del género de la voz
genero = st.selectbox('Selecciona el género de la voz:', ['Femenina', 'Masculina'])

# Selección de la música de fondo
musica = st.selectbox('Selecciona la música de fondo:', ['Navidad 1', 'Navidad 2', 'Navidad 3', 'Navidad 4', 'Navidad 5'])

# Mapeo de música a archivos locales
# Mapeo de música a archivos locales
musica_map = {
    'Navidad 1': 'https://github.com/ocejudo2000/santa/blob/main/HillTopTrio-SilentNight.mp3',
    'Navidad 2': 'https://github.com/ocejudo2000/santa/blob/main/Kashido-DeckTheAisles.mp3',
    'Navidad 3': 'https://github.com/ocejudo2000/santa/blob/main/Semo-ItsXmasAgain.mp3',
    'Navidad 4': 'musica/navidad4.mp3',
    'Navidad 5': 'musica/navidad5.mp3'
}

# Control deslizante para ajustar la atenuación de la música de fondo
atenuacion = st.slider('Ajusta el volumen de la música de fondo (dB):', min_value=0, max_value=30, value=20)

if st.button('Generar Audio'):
    if texto:
        # Genera un UUID para el nombre del archivo
        unique_id = uuid.uuid4()
        audio_filename = f"resultado_{unique_id}.mp3"

        # Genera la voz sintetizada
        tts.tts_to_file(text=texto, speaker=genero, file_path="voz.wav")

        # Carga la música de fondo seleccionada
        musica_fondo = AudioSegment.from_mp3(musica_map[musica])

        # Carga la voz sintetizada
        voz = AudioSegment.from_wav("voz.wav")

        # Ajusta la duración de la música de fondo para que coincida con la duración de la voz
        if len(musica_fondo) < len(voz):
            # Repite la música de fondo si es más corta que la voz
            repeticiones = len(voz) // len(musica_fondo) + 1
            musica_fondo = musica_fondo * repeticiones
        musica_fondo = musica_fondo[:len(voz)]

        # Aplica la atenuación seleccionada a la música de fondo
        musica_fondo = musica_fondo - atenuacion  # Reduce el volumen según la selección del usuario

        # Combina la voz con la música de fondo
        combinado = voz.overlay(musica_fondo)

        # Exporta el audio combinado a un archivo
        combinado.export(audio_filename, format="mp3")

        # Subida del archivo al servidor FTP
        try:
            # Establece la conexión FTP
            with FTP() as ftp:
                ftp.connect(FTP_HOST, FTP_PORT)
                ftp.login(FTP_USER, FTP_PASS)
                ftp.cwd(FTP_DIR)

                # Sube el archivo
                with open(audio_filename, 'rb') as file:
                    ftp.storbinary(f'STOR {audio_filename}', file)
                st.success(f'Archivo subido exitosamente a {FTP_DIR}{audio_filename}')

        except Exception as e:
            st.error(f'Error al subir el archivo: {e}')
    else:
        st.warning('Por favor, ingresa un texto.')