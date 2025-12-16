import ipywidgets as widgets
from IPython.display import display, clear_output, Audio, HTML
from pynq import Overlay, allocate
import scipy.io.wavfile as wav
import numpy as np
import time
import os
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 1. Configuration & Global State
# ---------------------------------------------------------
BITSTREAMS = {
    "Low Pass": "your_file_name1.bit",
    "Band Pass": "your_file_name2.bit",
    "High Pass": "your_file_name3.bit"
}

# State variables
current_overlay = None
current_bitstream_file = None
dma = None
audio_data = None
sample_rate = 44100
processed_audio = None

# ---------------------------------------------------------
# 2. Custom CSS (Dark Purple Theme)
# ---------------------------------------------------------
style_html = """
<style>
    /* Main Container with Dark Grey Background */
    .pynq-dark-container {
        background-color: #2b2b2b;
        border: 2px solid #8e44ad; /* Purple Border */
        border-radius: 10px;
        padding: 20px;
        color: #ecf0f1;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Header with Purple Glow Gradient */
    .pynq-dark-header {
        background: linear-gradient(90deg, #5b2c6f 0%, #9b59b6 100%);
        padding: 15px;
        border-radius: 8px 8px 0 0;
        text-align: center;
        color: white;
        text-shadow: 0px 0px 10px #e0b0ff;
        margin-bottom: 15px;
    }

    /* Input Fields */
    .pynq-input input {
        background-color: #444 !important;
        color: white !important;
        border: 1px solid #8e44ad !important;
    }

    /* Buttons */
    .pynq-purple-btn {
        background-color: #6c3483 !important; /* Deep Purple */
        color: white !important;
        font-weight: bold;
        font-size: 14px;
        border-radius: 5px;
        border: 1px solid #9b59b6;
        transition: 0.3s;
    }
    .pynq-purple-btn:hover {
        background-color: #9b59b6 !important; /* Lighter Purple on Hover */
        box-shadow: 0 0 10px #9b59b6;
    }

    /* Progress Bar */
    .widget-progress .progress-bar-success {
        background-color: #af7ac5 !important;
    }
    
    /* Text Color Override for standard widgets */
    .widget-label {
        color: #ecf0f1 !important;
    }
</style>
"""

# ---------------------------------------------------------
# 3. Processing Logic (Standard)
# ---------------------------------------------------------
def load_audio_file(filename):
    global audio_data, sample_rate
    if not os.path.exists(filename):
        return False, "File not found"
    try:
        sr, data = wav.read(filename)
        sample_rate = sr
        if len(data.shape) > 1: data = data[:, 0] # Mono
        audio_data = data.astype(np.int32)
        return True, f"Loaded {len(data)} samples @ {sr}Hz"
    except Exception as e:
        return False, str(e)

def process_on_fpga(bitstream_path, progress_bar):
    global current_overlay, dma, current_bitstream_file, processed_audio
    
    if audio_data is None: return None, "No Audio Loaded"
    
    progress_bar.value = 10
    
    try:
        # Load Overlay if changed
        if current_bitstream_file != bitstream_path:
            current_overlay = Overlay(bitstream_path)
            dma = current_overlay.axi_dma_0
            current_bitstream_file = bitstream_path
    except Exception as e:
        return None, f"Bitstream Error: {str(e)}"

    progress_bar.value = 30
    
    data_len = len(audio_data)
    in_buffer = allocate(shape=(data_len,), dtype=np.int32)
    out_buffer = allocate(shape=(data_len,), dtype=np.int32)
    
    progress_bar.value = 50
    np.copyto(in_buffer, audio_data)
    
    progress_bar.value = 70
    start = time.time()
    dma.sendchannel.transfer(in_buffer)
    dma.recvchannel.transfer(out_buffer)
    dma.sendchannel.wait()
    dma.recvchannel.wait()
    end = time.time()
    
    progress_bar.value = 90
    processed_audio = out_buffer.astype(np.int16)
    
    del in_buffer, out_buffer
    
    progress_bar.value = 100
    return processed_audio, end - start

# ---------------------------------------------------------
# 4. GUI Construction
# ---------------------------------------------------------

# Apply CSS
display(HTML(style_html))

# Header
header = widgets.HTML(value="<div class='pynq-dark-header'><h2>🔮 FPGA Audio Processor</h2></div>")

# Input Section
txt_filename = widgets.Text(value='sparks.wav', placeholder='filename.wav', layout=widgets.Layout(width='60%'))
txt_filename.add_class('pynq-input')

btn_load = widgets.Button(description='Load WAV', layout=widgets.Layout(width='35%'))
btn_load.add_class('pynq-purple-btn')

lbl_status = widgets.HTML(value="<b>Status:</b> <span style='color:#bdc3c7'>Waiting for input...</span>")

# Filter Buttons
btn_lpf = widgets.Button(description=' Low Pass', icon='filter', layout=widgets.Layout(width='32%', height='60px'))
btn_bpf = widgets.Button(description=' Band Pass', icon='music', layout=widgets.Layout(width='32%', height='60px'))
btn_hpf = widgets.Button(description=' High Pass', icon='headphones', layout=widgets.Layout(width='32%', height='60px'))

for btn in [btn_lpf, btn_bpf, btn_hpf]:
    btn.add_class('pynq-purple-btn')

# Output Widgets
progress = widgets.IntProgress(value=0, min=0, max=100, layout=widgets.Layout(width='98%'))
out_plot = widgets.Output(layout=widgets.Layout(margin='10px 0'))
out_audio = widgets.Output()

# ---------------------------------------------------------
# 5. Event Handling
# ---------------------------------------------------------

def on_load_click(b):
    success, msg = load_audio_file(txt_filename.value)
    color = "#58d68d" if success else "#ec7063" # Soft Green or Red
    lbl_status.value = f"<b>Status:</b> <span style='color:{color}'>{msg}</span>"
    
    with out_plot:
        clear_output()
        if success:
            plt.style.use('dark_background') # Matplotlib Dark Mode
            fig, ax = plt.subplots(figsize=(10, 2))
            fig.patch.set_facecolor('#2b2b2b')
            ax.set_facecolor('#2b2b2b')
            ax.plot(audio_data[::100], color='#af7ac5', alpha=0.8) # Light Purple Line
            ax.set_title("Original Waveform", color='white')
            ax.axis('off')
            plt.show()

def run_filter(filter_name):
    progress.value = 0
    out_audio.clear_output()
    lbl_status.value = f"<b>Status:</b> Loading {filter_name}..."
    
    result, duration = process_on_fpga(BITSTREAMS[filter_name], progress)
    
    if result is None:
        lbl_status.value = f"<b>Status:</b> <span style='color:#ec7063'>Error: {duration}</span>"
    else:
        lbl_status.value = f"<b>Status:</b> <span style='color:#58d68d'>Success! ({duration:.4f}s)</span>"
        
        # Save file
        filename = f"out_{filter_name.replace(' ', '')}.wav"
        wav.write(filename, sample_rate, result)
        
        # Plot
        with out_plot:
            clear_output()
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(10, 3))
            fig.patch.set_facecolor('#2b2b2b')
            ax.set_facecolor('#2b2b2b')
            
            # Original (Faint Grey)
            ax.plot(audio_data[::100], color='gray', alpha=0.3, label="Original")
            
            # Filtered (Neon Colors)
            colors = {'Low Pass': '#3498db', 'Band Pass': '#f1c40f', 'High Pass': '#e74c3c'}
            ax.plot(result[::100], color=colors.get(filter_name, 'white'), alpha=0.9, label=filter_name)
            
            ax.legend()
            ax.set_title(f"{filter_name} Result", color='white')
            ax.axis('off')
            plt.show()
            
        with out_audio:
            display(HTML(f"<div style='color:white'><b>Result ({filter_name}):</b></div>"))
            display(Audio(filename))

# Link Events
btn_load.on_click(on_load_click)
btn_lpf.on_click(lambda b: run_filter("Low Pass"))
btn_bpf.on_click(lambda b: run_filter("Band Pass"))
btn_hpf.on_click(lambda b: run_filter("High Pass"))

# ---------------------------------------------------------
# 6. Layout Assembly
# ---------------------------------------------------------
ui_body = widgets.VBox([
    header,
    widgets.HTML("<br>"),
    widgets.Label("1. Select Audio File:", style={'font_weight':'bold'}),
    widgets.HBox([txt_filename, btn_load]),
    lbl_status,
    widgets.HTML("<hr style='border-color:#8e44ad'>"),
    widgets.Label("2. Apply Hardware Filter:", style={'font_weight':'bold'}),
    widgets.HBox([btn_lpf, btn_bpf, btn_hpf]),
    widgets.HTML("<br>"),
    progress,
    out_plot,
    out_audio
])

ui_body.add_class('pynq-dark-container')

# Render
display(ui_body)
