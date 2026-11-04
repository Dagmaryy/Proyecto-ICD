import os
from faster_whisper import WhisperModel

carpeta_audios = 'data/raw/interviews/usuarios/'
carpeta_salida = 'data/raw/interviews/transcripciones/'
os.makedirs(carpeta_salida, exist_ok=True)

print("Cargando modelo 'medium' (La primera vez descargará 1.5 GB)...")
model = WhisperModel("medium", device="cpu", compute_type="int8")

# Buscar específicamente del 17 al 25
audios_a_transcribir = []
for i in range(17, 26):
    # Buscamos el archivo que contenga el número (por si hay variaciones en el nombre)
    for f in os.listdir(carpeta_audios):
        if str(i) in f and f.lower().endswith(('.aac', '.m4a', '.mp3', '.wav')):
            audios_a_transcribir.append(f)
            break

print(f"Se encontraron {len(audios_a_transcribir)} audios para transcribir (del 17 al 25).\n")

for i, nombre_audio in enumerate(audios_a_transcribir, 1):
    ruta_audio = os.path.join(carpeta_audios, nombre_audio)
    print(f"[{i}/{len(audios_a_transcribir)}] 🎙️ Transcribiendo: {nombre_audio}...")

    segments, info = model.transcribe(ruta_audio, beam_size=5, language="es")
    texto_completo = " ".join([segment.text for segment in segments])

    nombre_salida = os.path.splitext(nombre_audio)[0] + '.md'
    ruta_salida = os.path.join(carpeta_salida, nombre_salida)

    with open(ruta_salida, 'w', encoding='utf-8') as f:
        f.write(f"# Transcripción: {nombre_audio}\n\n")
        f.write(texto_completo)

    print(f"   ✅ Guardado en: {nombre_salida}")

print("\n🎉 ¡Transcripciones terminadas!")
