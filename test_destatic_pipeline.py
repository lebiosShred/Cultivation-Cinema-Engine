import os
import sys
import time
import torch
import soundfile as sf
import numpy as np
import scipy.signal as signal
import noisereduce as nr
import whisper

fish_dir = r"C:\Users\SkyDr\.gemini\antigravity\scratch\fish-speech"
sys.path.insert(0, fish_dir)

import pyrootutils
pyrootutils.setup_root(fish_dir, indicator=".project-root", pythonpath=True)

from tools.inference_engine import TTSInferenceEngine
from tools.llama.generate import launch_thread_safe_queue
from tools.vqgan.inference import load_model as load_decoder_model
from tools.schema import ServeTTSRequest, ServeReferenceAudio

project_dir = r"C:\Users\SkyDr\OneDrive\Desktop\PROJECTS\Youtube Videos\RMJI"
test_dir = os.path.join(project_dir, "destatic_eval")
os.makedirs(test_dir, exist_ok=True)

# 1. Clean the Reference Audio File
raw_ref_path = os.path.join(project_dir, "chattts_male_seeds", "Male_Seed_1_(Seed_4567_117Hz).wav")
clean_ref_path = os.path.join(test_dir, "Male_Seed_1_Pristine_Clean.wav")

ref_data, ref_sr = sf.read(raw_ref_path)

# Apply stationary noise reduction to reference audio
denoised_ref = nr.reduce_noise(
    y=ref_data,
    sr=ref_sr,
    stationary=True,
    prop_decrease=0.95,
    time_mask_smooth_ms=64
)

# Apply gentle 80Hz high-pass filter to remove subsonic rumble
sos_hp = signal.butter(4, 80, 'hp', fs=ref_sr, output='sos')
denoised_ref = signal.sosfilt(sos_hp, denoised_ref)

# Peak normalize reference to -1 dB
max_r = np.max(np.abs(denoised_ref))
if max_r > 0:
    denoised_ref = (denoised_ref / max_r) * 0.90
sf.write(clean_ref_path, denoised_ref, ref_sr)

print(f"✅ Pristine Reference Audio Created: {clean_ref_path}")

# Initialize Fish Speech Engine
ckpt_dir = os.path.join(fish_dir, "checkpoints", "fish-speech-1.5")
llama_ckpt = ckpt_dir
decoder_ckpt = os.path.join(ckpt_dir, "firefly-gan-vq-fsq-8x1024-21hz-generator.pth")

device = "cuda"
precision = torch.half

llama_queue = launch_thread_safe_queue(
    checkpoint_path=llama_ckpt,
    device=device,
    precision=precision,
    compile=False
)
decoder_model = load_decoder_model(
    config_name="firefly_gan_vq",
    checkpoint_path=decoder_ckpt,
    device=device
)
engine = TTSInferenceEngine(
    llama_queue=llama_queue,
    decoder_model=decoder_model,
    precision=precision,
    compile=False
)

whisper_model = whisper.load_model('base')
ref_txt = whisper_model.transcribe(clean_ref_path)['text'].strip()

with open(clean_ref_path, 'rb') as f:
    clean_ref_bytes = f.read()
clean_ref_obj = ServeReferenceAudio(audio=clean_ref_bytes, text=ref_txt)

test_text = "Yo, what is good fellow Daoists?! Welcome back to Cultivation Cinema! Episode one hundred eighty-nine just dropped, and bro, Hahn Lee is actually built different."

# Test 3 Parameter configurations:
# 1. Clean Ref + Temp 0.25 (Ultra-clean deterministic)
# 2. Clean Ref + Temp 0.35 (Balanced warmth & clarity)
# 3. Clean Ref + Temp 0.35 + Post-Vocoder Denoise

configs = [
    {"name": "destatic_temp_0_25", "temp": 0.25, "top_p": 0.50, "post_denoise": False},
    {"name": "destatic_temp_0_35", "temp": 0.35, "top_p": 0.60, "post_denoise": False},
    {"name": "destatic_temp_0_35_postpolish", "temp": 0.35, "top_p": 0.60, "post_denoise": True}
]

for cfg in configs:
    c_name = cfg["name"]
    temp = cfg["temp"]
    top_p = cfg["top_p"]
    post_dn = cfg["post_denoise"]
    
    out_file = os.path.join(test_dir, f"{c_name}.wav")
    
    req = ServeTTSRequest(
        text=test_text,
        references=[clean_ref_obj],
        reference_id=None,
        max_new_tokens=1024,
        chunk_length=200,
        top_p=top_p,
        repetition_penalty=1.2,
        temperature=temp,
        streaming=False
    )
    
    results = list(engine.inference(req))
    final_result = [r for r in results if r.code == "final"]
    if final_result and final_result[0].audio is not None:
        sr, audio_data = final_result[0].audio
        
        if post_dn:
            # Gentle post-vocoder noise reduction
            cleaned_audio = nr.reduce_noise(
                y=audio_data,
                sr=sr,
                stationary=True,
                prop_decrease=0.80,
                time_mask_smooth_ms=32
            )
            # High-pass filter 70Hz
            sos_hp_out = signal.butter(4, 70, 'hp', fs=sr, output='sos')
            cleaned_audio = signal.sosfilt(sos_hp_out, cleaned_audio)
            
            # Peak normalize
            max_val = np.max(np.abs(cleaned_audio))
            if max_val > 0:
                cleaned_audio = (cleaned_audio / max_val) * 0.89
            sf.write(out_file, cleaned_audio, sr)
        else:
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = (audio_data / max_val) * 0.89
            sf.write(out_file, audio_data, sr)
            
        dur = len(audio_data) / sr
        asr = whisper_model.transcribe(out_file)['text'].strip()
        print(f"\n🎉 [{c_name}] (Temp={temp}, Top-P={top_p}, Post-Denoise={post_dn}):")
        print(f"   Duration: {dur:.2f}s")
        print(f"   ASR: \"{asr}\"")
        print(f"   File: {out_file}")

print("\n" + "=" * 70)
print("DE-STATIC EVALUATION COMPLETE!")
print("=" * 70)
