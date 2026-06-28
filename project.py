import os
import webbrowser
import threading
import wave
import numpy as np
import soundfile as sf  
import gradio as gr
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import winsound 


recognizer = sr.Recognizer()


languages = {
    "Telugu (తెలుగు)": "te",
    "English (English)": "en",
    "Hindi (हिंदी)": "hi",
    "Spanish (Español)": "es",
    "French (Français)": "fr",
    "German (Deutsch)": "de",
    "Tamil (தமிழ்)": "ta",
    "Kannada (కನ್ನಡ)": "kn"
}

def voice_text_pipeline(input_mode, audio_mic, audio_file, typed_text, source_lang_name, target_lang_name):
    detected_text = ""
    translated_text = ""
    source_lang_code = languages.get(source_lang_name, "te")
    target_lang_code = languages.get(target_lang_name, "en")
    
    try:
        if input_mode in ["🎙️ Live Record (లైవ్ రికార్డ్)", "📁 Upload Audio (ఫైల్ అప్‌లోడ్)"]:
            winsound.Beep(2000, 250)

        temp_wav_path = "input_processed.wav"

        if input_mode == "🎙️ Live Record (లైవ్ రికార్డ్)":
            if audio_mic is None:
                return "No live recording detected. Please record your voice first.", "", None, None, None
            
            sr_rate, y = audio_mic
            if np.issubdtype(y.dtype, np.floating):
                y = (y * 32767).astype(np.int16)
            else:
                y = y.astype(np.int16)
                
            with wave.open(temp_wav_path, "wb") as wav_file:
                channels = 1 if len(y.shape) == 1 else y.shape[1]
                wav_file.setnchannels(channels)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sr_rate)
                wav_file.writeframes(y.tobytes())
            
            with sr.AudioFile(temp_wav_path) as source:
                audio_recorded = recognizer.record(source)
                detected_text = recognizer.recognize_google(audio_recorded, language=source_lang_code)

        elif input_mode == "📁 Upload Audio (ఫైల్ అప్‌లోడ్)":
            if audio_file is None:
                return "No audio file uploaded. Please upload a file first.", "", None, None, None
            
            try:
                data, samplerate = sf.read(audio_file)
                sf.write(temp_wav_path, data, samplerate, subtype='PCM_16')
                
                with sr.AudioFile(temp_wav_path) as source:
                    audio_recorded = recognizer.record(source)
                    detected_text = recognizer.recognize_google(audio_recorded, language=source_lang_code)
            except Exception as conversion_error:
                return f"Error reading audio file: {str(conversion_error)}.", "", None, None, None

        else:
            if not typed_text.strip():
                return "Please enter some text before processing.", "", None, None, None
            detected_text = typed_text

        translator = GoogleTranslator(source='auto', target=target_lang_code)
        translated_text = translator.translate(detected_text)

        try:
            tts = gTTS(text=translated_text, lang=target_lang_code)
        except Exception:
            tts = gTTS(text=translated_text, lang='en')

        audio_output_path = "voice_response.mp3"
        text_output_path = "interaction_summary.txt"
        
        tts.save(audio_output_path)
        
        with open(text_output_path, "w", encoding="utf-8") as f:
            f.write("=== TRANSLATION LOG ===\n")
            f.write(f"Input Mode: {input_mode}\n\n")
            f.write(f"Original Text:\n{detected_text}\n\n")
            f.write(f"Translated Text:\n{translated_text}\n")
            f.write("=============================\n")

        return detected_text, translated_text, audio_output_path, audio_output_path, text_output_path

    except sr.UnknownValueError:
        return "Could not understand the audio. Please speak clearly.", "", None, None, None
    except Exception as e:
        return f"Error: {str(e)}", "", None, None, None

def toggle_inputs(mode):
    if mode == "🎙️ Live Record (లైవ్ రికార్డ్)":
        return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
    elif mode == "📁 Upload Audio (ఫైల్ అప్‌లోడ్)":
        return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)
    else:
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)


custom_css = """
body { 
    background: linear-gradient(-45deg, #020617, #0f172a, #0b1329, #020617) !important;
    background-size: 400% 400% !important;
    animation: premiumScroll 18s ease infinite !important;
    color: #ffffff !important;
}
@keyframes premiumScroll {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.gradio-container {
    background: transparent !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    padding: 40px 20px !important;
}
.glowing-title {
    text-align: center;
    background: linear-gradient(90deg, #ffe082 0%, #e2b857 50%, #f59e0b 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 3.1rem;
    letter-spacing: -0.02em;
    margin-bottom: 5px;
    text-transform: uppercase;
    text-shadow: 0 2px 20px rgba(226, 184, 87, 0.15);
}
.custom-card {
    background: rgba(15, 23, 42, 0.9) !important; 
    border: 1px solid rgba(226, 184, 87, 0.25) !important; 
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6) !important;
    border-radius: 16px !important;
    padding: 30px !important;
    backdrop-filter: blur(8px);
}
.action-btn {
    background: linear-gradient(90deg, #e2b857, #f59e0b) !important; 
    color: #000000 !important; 
    font-weight: 800 !important;
    font-size: 1.1rem !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 16px 32px !important;
    box-shadow: 0 5px 20px rgba(245, 158, 11, 0.2) !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    text-transform: uppercase;
}
.action-btn:hover {
    background: linear-gradient(90deg, #ffe082, #e2b857) !important;
    box-shadow: 0 8px 25px rgba(245, 158, 11, 0.35) !important;
    transform: translateY(-1px);
}
.copy-btn {
    background: transparent !important;
    color: #e2b857 !important;
    border: 1px solid #e2b857 !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
    padding: 8px 16px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    margin-top: 10px;
}
.copy-btn:hover {
    background: rgba(226, 184, 87, 0.1) !important;
}
.section-header {
    font-size: 1.2rem;
    font-weight: 700;
    text-transform: uppercase;
    color: #e2b857; 
    margin-bottom: 20px;
    border-left: 4px solid #e2b857;
    padding-left: 10px;
}
input, textarea, select, .tabs button {
    background: #1e293b !important; 
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 8px !important;
    color: #ffffff !important; 
    font-size: 1.05rem !important;
}
input:focus, textarea:focus, select:focus {
    border-color: #e2b857 !important; 
}
.block label span {
    color: #cbd5e1 !important; 
    font-weight: 600 !important;
}
"""

with gr.Blocks(theme=gr.themes.Default(primary_hue="amber", font=[gr.themes.GoogleFont("Plus Jakarta Sans")]), css=custom_css) as demo:
    gr.HTML("<h1 class='glowing-title'>Multilanguage Text & Voice Assistant</h1>")
    gr.Markdown("<p style='text-align:center; color:#94a3b8; font-size:1.1rem; letter-spacing: 0.05em;'>REALTIME MULTILINGUAL SYNTAX & AUDIO TRANSLATOR</p>")
    
    with gr.Row(equal_height=True):
        with gr.Column(scale=5, elem_classes=["custom-card"]):
            gr.HTML("<div class='section-header'>Input Terminal</div>")
            
            input_mode = gr.Radio(
                choices=["🎙️ Live Record (లైవ్ రికార్డ్)", "📁 Upload Audio (ఫైల్ అప్‌లోడ్)", "✍️ Text Input (టెక్స్ట్)"],
                value="✍️ Text Input (టెక్స్ట్)",
                label="Execution Mode"
            )
            
            with gr.Group():
                voice_mic_area = gr.Audio(sources=["microphone"], type="numpy", label="Capture Microphone", visible=False)
                voice_file_area = gr.Audio(sources=["upload"], type="filepath", label="Ingest Audio File", visible=False)
                text_area = gr.Textbox(placeholder="ఇక్కడ టెక్స్ట్ ఎంటర్ చేయండి...", label="Raw Text Field", lines=6, visible=True)
            
            with gr.Row():
                src_lang = gr.Dropdown(choices=list(languages.keys()), value="Telugu (తెలుగు)", label="Source Language")
                tgt_lang = gr.Dropdown(choices=list(languages.keys()), value="English (English)", label="Target Language")
            
            submit_btn = gr.Button("Process & Translate", elem_classes=["action-btn"])
            
        with gr.Column(scale=6, elem_classes=["custom-card"]):
            gr.HTML("<div class='section-header'>Realtime Output</div>")
            
            # Error fixed here: Removed show_copy_button parameter
            stt_log = gr.Textbox(label="1. Transcribed Content", interactive=False, lines=4)
            trans_log = gr.Textbox(label="2. Translated Content", interactive=False, lines=5, elem_id="trans_log")
            
            copy_btn = gr.Button("📋 Copy Translated Text", elem_classes=["copy-btn"])

            gr.HTML("<div style='height: 1px; background: rgba(255,255,255,0.1); margin: 20px 0;'></div>")
            tts_player = gr.Audio(label="Acoustic Voice Output", type="filepath", interactive=False, autoplay=True)
            
            with gr.Row():
                download_audio = gr.File(label="Export Audio")
                download_text = gr.File(label="Export Manifest")

    input_mode.change(
        fn=toggle_inputs,
        inputs=input_mode,
        outputs=[voice_mic_area, voice_file_area, text_area]
    )

    submit_btn.click(
        fn=voice_text_pipeline,
        inputs=[input_mode, voice_mic_area, voice_file_area, text_area, src_lang, tgt_lang],
        outputs=[stt_log, trans_log, tts_player, download_audio, download_text]
    )

    copy_btn.click(
        None, 
        None, 
        None, 
        js="""() => {
            const text = document.querySelector('#trans_log textarea').value;
            if (text && text.trim() !== '') {
                navigator.clipboard.writeText(text);
                alert('టెక్స్ట్ కాపీ అయింది! / Text copied successfully!');
            } else {
                alert('కాపీ చేయడానికి అక్కడ టెక్స్ట్ ఏమీ లేదు! / No text to copy!');
            }
        }"""
    )

def open_browser():
    webbrowser.open("http://127.0.0.1:7866")

if __name__ == "__main__":
    threading.Timer(1.5, open_browser).start()
    demo.launch(server_port=7866, share=False)