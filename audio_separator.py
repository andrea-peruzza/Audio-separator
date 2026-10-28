import os
import tkinter as tk
from tkinter import filedialog, messagebox
from demucs.apply import apply_model
from demucs.pretrained import get_model
from demucs.audio import AudioFile
from basic_pitch.inference import predict

import soundfile as sf
import torch
import pretty_midi
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SEPARATION_DIR = os.path.join(OUTPUT_DIR, "separated")
TRANSCRIPTION_DIR = os.path.join(OUTPUT_DIR, "transcriptions")
MODEL_DIR = os.path.join(BASE_DIR, "modello_convertitore_MIDI", "nmp")
AUDIO_FILES_DIR = os.path.join(BASE_DIR, "audio_files")

os.makedirs(SEPARATION_DIR, exist_ok=True)
os.makedirs(TRANSCRIPTION_DIR, exist_ok=True)

def run_processing(audio_path):
    try:
        print("Aspetta 0.5 secondi...")
        #print(f"[DEBUG] Verifica esistenza file: {audio_path}")
        if not os.path.isfile(audio_path):
            raise FileNotFoundError(f"Il file {audio_path} non esiste.")

        # Debug: stampa il percorso del file
        #print(f"Percorso del file audio: {audio_path}")

        # === SEPARAZIONE ===
        #print("[DEBUG] Caricamento modello...")
        model = get_model(name="hdemucs_mmi")

        #print("[DEBUG] Caricamento WAV con soundfile...")
        audio_data, sr = sf.read(audio_path)

        #Converti a tensore float32 e gestisci il formato
        if audio_data.ndim == 1:  #Mono
            audio_tensor = torch.tensor(audio_data).unsqueeze(0)  #(1, N)
        else:
            audio_tensor = torch.tensor(audio_data).T  # (channels, N)
        
        audio_tensor = audio_tensor.float()

        #print("[DEBUG] Risample se necessario...")
        if sr != model.samplerate:
            #print(f"[DEBUG] Risampling da {sr} a {model.samplerate}")
            import torchaudio
            resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=model.samplerate)
            audio_tensor = resampler(audio_tensor)


        #print("[DEBUG] Creazione device...")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        #print(f"[DEBUG] Tipo audio_tensor: {audio_tensor.dtype}")
        #print(f"[DEBUG] Forma audio_tensor: {audio_tensor.shape}")
        #print("[DEBUG] Applicazione modello...")
        print("FINITO!")
        #model = model.to(device)
        audio_tensor = audio_tensor.unsqueeze(0)
        sources = apply_model(model, audio_tensor.to(device), device=device, split=True, overlap=0.25)
        print("..e invece no")
        #print(f"numero sources trovate: {len(sources)}")
        #print(f"sources: {sources}")
        #print(f"sources trovate: {model.sources}")

        #print("[DEBUG] Scrittura sorgenti separate...")
        instrument_names = model.sources  #(drums, bass, other, vocals)
        separated_paths = []
        for i in range(len(instrument_names)): #in range(0, 4)
            source = sources[0, i]
            #verifico la forma del tensor per ogni sorgente
            #print(f"Forma sorgente {i}: {source.shape}")
            '''if len(source.shape) > 2:
                print(f"[DEBUG] La sorgente {i} ha {len(source.shape)} dimensioni. Riduciamole...")
                source = source.view(source.size(0), -1)  #ridimensiono
            if len(source.shape) > 1:
                source = source.squeeze()
            print(f"forma sorgente dopo squeeze: {source.shape}")
            #scrittura delle sorgenti separate'''
            #print(f"Scrivo sorgente {i} su {instrument_names[i]}.wav")
            out_path = os.path.join(SEPARATION_DIR, f"{instrument_names[i]}.wav")
            #print(f"Scrivo sorgente {i} su {out_path}")
            #print(f"Forma sorgente dopo squeeze e dopo out-path: {source.shape}")
            #print(f"Forma finale da salvare: {source.cpu().numpy().T.shape}")
            sf.write(out_path, source.cpu().numpy().T, model.samplerate)
            separated_paths.append(out_path)

        #print(f"[DEBUG] separated_paths finali: {separated_paths}")
        # === TRASCRIZIONE + PIANOROLL ===

        #print("[DEBUG] Avvio trascrizione e pianoroll...")
        print("Lavorare, Lavorare...  *fischiettii affaticati*")
        for path in separated_paths:
            #print(f"[DEBUG] path = {path}")
            #print(f"[DEBUG] type(path): {type(path)}")
            name = os.path.splitext(os.path.basename(path))[0].strip()
            #print(f"[DEBUG] os.path.basename(path): {os.path.basename(path)}")
            #print(f"[DEBUG] name: {name}")
            output_path = os.path.join(TRANSCRIPTION_DIR, name)
            os.makedirs(output_path, exist_ok=True)
            #print(f"[DEBUG] output_path: {output_path}")
            _, midi_data, _ = predict(
                path,
                model_or_model_path=MODEL_DIR
            )
            """_, midi_data, _ = predict_and_save(
                    paths,
                    output_directory=output_path,
                    model_or_model_path=MODEL_DIR,
                    save_midi=True,
                    save_model_outputs=False,
                    save_notes=False,
                    sonify_midi=False
                )"""
           
            
            print("ERRORE!")
            midi_path = os.path.join(output_path, name + ".mid")
            midi_data.write(midi_path)
            
            #show_pianoroll(midi_path, name)

        messagebox.showinfo("Completato", "Separazione e trascrizione completate!")
    except FileNotFoundError as e:
        messagebox.showerror("Errore", f"File non trovato: {e}")
    except PermissionError as e:
        messagebox.showerror("Errore", f"Permesso negato: {e}")
    except IOError as e:
        messagebox.showerror("Errore", f"Errore di I/O: {e}")
    except Exception as e:
        messagebox.showerror("Errore", str(e))

# === GUI ===
def select_file():
    initial_dir = AUDIO_FILES_DIR if os.path.exists(AUDIO_FILES_DIR) else BASE_DIR
    file_path = filedialog.askopenfilename(
        initialdir=initial_dir,
        filetypes=[("Audio files", "*.wav *.mp3")]
    )
    if file_path:
        # Normalizza il percorso
        file_path = os.path.normpath(file_path)
        print(f"Audio selezionato: {file_path}")
        label_selected.config(text=os.path.basename(file_path))
        btn_process.config(state=tk.NORMAL)
        app.file_path = file_path

def start_process():
    print(f"Percorso del file audio in start_process: {app.file_path}")
    # Usa il percorso assoluto per sicurezza
    audio_path = os.path.abspath(app.file_path)
    run_processing(audio_path)

# === INTERFACCIA TKINTER ===
if __name__ == "__main__":
    app = tk.Tk()
    app.title("L'audio-separatore-diddio")
    app.geometry("400x200")

    label_title = tk.Label(app, text="Seleziona un file audio", font=("Arial", 14))
    label_title.pack(pady=10)

    btn_browse = tk.Button(app, text="Sfoglia", command=select_file)
    btn_browse.pack()

    label_selected = tk.Label(app, text="Nessun file selezionato", fg="gray")
    label_selected.pack(pady=5)

    btn_process = tk.Button(app, text="Avvia Analisi", command=start_process, state=tk.DISABLED)
    btn_process.pack(pady=10)

    app.mainloop()
