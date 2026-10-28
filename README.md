# Audio Separator

A Python desktop application for audio source separation and automatic polyphonic MIDI transcription.

The software combines Demucs for separating musical stems and Basic Pitch for converting audio to MIDI, controlled via a minimal Tkinter graphical user interface.

## Features

- Separates audio tracks into four isolated stems: vocals, drums, bass, and other instruments.
- Automatically transcribes each separated stem into MIDI format (.mid).
- Graphical user interface (GUI) to easily select local audio files (.wav, .mp3).
- Uses relative paths to ensure repository portability across different machines.

## Folder Structure

- `audio_files/`: directory for input audio files.
- `modello_convertitore_MIDI/`: directory containing the neural network model weights for MIDI transcription (TensorFlow SavedModel format in `nmp/`).
- `output/`: target directory for processed results.
  - `output/separated/`: separated audio tracks in WAV format.
  - `output/transcriptions/`: generated MIDI files organized into instrument subfolders.
- `audio_separator.py`: main script containing the GUI and processing pipeline.
- `requirements.txt`: list of required Python libraries and dependencies.

## Prerequisites

- Python 3.10
- CUDA-compatible GPU (optional, recommended for faster processing; CPU fallback is supported)
- FFmpeg installed and available in system PATH

## Installation

1. Clone the repository:
```bash
git clone https://github.com/<your-username>/Audio-separator.git
cd Audio-separator
```

2. Create a virtual environment:
```bash
python -m venv virtual
```

3. Activate the virtual environment:
- On Windows (PowerShell):
```powershell
.\virtual\Scripts\Activate.ps1
```
- On Linux / macOS:
```bash
source virtual/bin/activate
```

4. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application from your terminal with the virtual environment activated:
```bash
python audio_separator.py
```

2. In the graphical window:
- Click the "Sfoglia" (Browse) button to select an audio file.
- Click "Avvia Analisi" (Start Analysis) to begin stem separation and MIDI transcription.

3. Once processing is complete, check the results in the `output/` directory:
- `output/separated/` contains the individual audio stems (`vocals.wav`, `drums.wav`, `bass.wav`, `other.wav`).
- `output/transcriptions/` contains the corresponding MIDI files (`vocals.mid`, `drums.mid`, `bass.mid`, `other.mid`).



## License
This project is licensed under the PolyForm Noncommercial License 1.0.0. See the LICENSE file for details.