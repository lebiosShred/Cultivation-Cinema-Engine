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
out_dir = os.path.join(project_dir, "full_option_b_destatic_master")
os.makedirs(out_dir, exist_ok=True)

# 1. Clean & De-Static the Reference Audio
raw_ref_path = os.path.join(project_dir, "chattts_male_seeds", "Male_Seed_1_(Seed_4567_117Hz).wav")
clean_ref_path = os.path.join(out_dir, "Male_Seed_1_Pristine_Clean.wav")

ref_data, ref_sr = sf.read(raw_ref_path)
denoised_ref = nr.reduce_noise(
    y=ref_data,
    sr=ref_sr,
    stationary=True,
    prop_decrease=0.95,
    time_mask_smooth_ms=64
)
sos_hp = signal.butter(4, 80, 'hp', fs=ref_sr, output='sos')
denoised_ref = signal.sosfilt(sos_hp, denoised_ref)
max_r = np.max(np.abs(denoised_ref))
if max_r > 0:
    denoised_ref = (denoised_ref / max_r) * 0.90
sf.write(clean_ref_path, denoised_ref, ref_sr)

print("1. Initializing Fish Speech Engine...")
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

print(f"🎙️ Using Pristine Clean Voice Reference: Option B (117 Hz - Denoised)")
print(f"   Reference Transcript: \"{ref_txt}\"")

# 7 Sections of Episode 189 Breakdown
FULL_SCRIPT_SECTIONS = [
    {
        "id": "sec1_cold_open",
        "title": "Act 1: Cold Open & The Jolt",
        "text": "Yo, what is good fellow Daoists?! Welcome back to Cultivation Cinema! Episode one hundred eighty-nine just dropped, and bro, Hahn Lee is actually built different."
    },
    {
        "id": "sec2_soul_barrier",
        "title": "Act 1 Part 2: Trapped in Soul Barrier",
        "text": "When trapped inside an ancient living soul corrosion barrier that instantly melts ordinary cultivators, Hahn Lee does not even flinch."
    },
    {
        "id": "sec3_novel_context",
        "title": "Act 2: What the Donghua Cut from the Novel",
        "text": "Here is what the animation skipped from the original web novel. Before Hahn Lee even stepped into the chamber, his Great Development Technique had already detected seven hidden spiritual traps."
    },
    {
        "id": "sec4_hiding_bamboo_swords",
        "title": "Act 2 Part 2: Tactical Concealment",
        "text": "In the novel, Hahn Lee knew that revealing his seventy-two Azure Bamboo Cloudswarm swords would draw unwanted attention from greedy Core Formation and Nascent Soul ancestors. So instead of wasting his Divine Devil Lightning, he chose an even nastier counter."
    },
    {
        "id": "sec5_tihun_unleashed",
        "title": "Act 3: Unleashing the Weeping Soul Beast",
        "text": "He casually drops his secret creature, Tee-hoon, the Weeping Soul Spirit! For anyone new to the lore, Tee-hoon is literally the apex predator of all ghostly and Yin spirits."
    },
    {
        "id": "sec6_devoured_seconds",
        "title": "Act 3 Part 2: Devouring Century-Old Souls",
        "text": "In literally three seconds, a century of evil Yin cultivation gets vacuumed up like a light afternoon snack."
    },
    {
        "id": "sec7_power_scaling_outro",
        "title": "Act 4: Power Scaling & Call to Action",
        "text": "This is the classic Hahn Lee formula: stay low key, calculate every single risk, and leave zero room for your enemy's survival! Episode one hundred ninety is going to be pure fire, so smash that subscribe button, drop a like, and cultivate well, fellow Daoists!"
    }
]

print(f"\n🚀 Rendering 7 Sections with Zero-Static De-Noising Pipeline...")
rendered_clips = []
sample_rate = 44100

for idx, sec in enumerate(FULL_SCRIPT_SECTIONS, 1):
    sec_id = sec["id"]
    sec_title = sec["title"]
    sec_text = sec["text"]
    out_file = os.path.join(out_dir, f"{idx:02d}_{sec_id}.wav")
    
    print(f"\n[{idx}/{len(FULL_SCRIPT_SECTIONS)}] Rendering {sec_title}...")
    
    # Low-entropy sampling to eliminate token fuzz/grit
    req = ServeTTSRequest(
        text=sec_text,
        references=[clean_ref_obj],
        reference_id=None,
        max_new_tokens=1024,
        chunk_length=200,
        top_p=0.55,
        repetition_penalty=1.2,
        temperature=0.30,
        streaming=False
    )
    
    t0 = time.time()
    results = list(engine.inference(req))
    elapsed = time.time() - t0
    
    final_result = [r for r in results if r.code == "final"]
    if final_result and final_result[0].audio is not None:
        sr, audio_data = final_result[0].audio
        sample_rate = sr
        
        # Transparent post-vocoder noise polishing
        cleaned_audio = nr.reduce_noise(
            y=audio_data,
            sr=sr,
            stationary=True,
            prop_decrease=0.85,
            time_mask_smooth_ms=32
        )
        sos_hp_out = signal.butter(4, 75, 'hp', fs=sr, output='sos')
        cleaned_audio = signal.sosfilt(sos_hp_out, cleaned_audio)
        
        max_val = np.max(np.abs(cleaned_audio))
        if max_val > 0:
            cleaned_audio = (cleaned_audio / max_val) * 0.89
            
        sf.write(out_file, cleaned_audio, sr)
        dur = len(cleaned_audio) / sr
        asr = whisper_model.transcribe(out_file)['text'].strip()
        
        print(f"   ✅ Done: {dur:.2f}s (Rendered in {elapsed:.2f}s)")
        print(f"   Whisper ASR: \"{asr}\"")
        rendered_clips.append(cleaned_audio)
    else:
        print(f"   ❌ Error: {results}")

# Assemble Complete Master Track with 220ms natural breath pause
print("\n🎛️ Assembling Complete De-Static Master Track...")
pause_samples = int(sample_rate * 0.220)
fade_len = int(sample_rate * 0.015)

master_track_segments = []
for i, clip in enumerate(rendered_clips):
    c = clip.copy().astype(np.float32)
    if len(c) > 2 * fade_len:
        fade_in = np.linspace(0, 1, fade_len)
        fade_out = np.linspace(1, 0, fade_len)
        c[:fade_len] *= fade_in
        c[-fade_len:] *= fade_out
    master_track_segments.append(c)
    if i < len(rendered_clips) - 1:
        master_track_segments.append(np.zeros(pause_samples, dtype=np.float32))

full_master_audio = np.concatenate(master_track_segments)
max_peak = np.max(np.abs(full_master_audio))
if max_peak > 0:
    full_master_audio = (full_master_audio / max_peak) * 0.89

master_out_path = os.path.join(out_dir, "fishspeech_option_b_destatic_master.wav")
sf.write(master_out_path, full_master_audio, sample_rate)

full_dur = len(full_master_audio) / sample_rate
full_asr = whisper_model.transcribe(master_out_path)['text'].strip()

# Measure final noise floor
frame_len = int(sample_rate * 0.05)
num_frames = len(full_master_audio) // frame_len
energies = [np.mean(full_master_audio[i*frame_len:(i+1)*frame_len]**2) for i in range(num_frames)]
energies.sort()
quiet_rms = np.sqrt(np.mean(energies[:max(1, int(num_frames*0.15))]))
quiet_db = 20 * np.log10(quiet_rms + 1e-10)
peak_db = 20 * np.log10(np.max(np.abs(full_master_audio)) + 1e-10)
final_snr = peak_db - quiet_db

print("\n" + "=" * 70)
print(f"🎉 DE-STATIC FULL MASTER PRODUCTION COMPLETE!")
print(f"   Total Duration: {full_dur:.2f} seconds ({full_dur/60:.2f} mins)")
print(f"   Noise Floor: {quiet_db:.2f} dBFS (Studio Black Silence)")
print(f"   Dynamic SNR: {final_snr:.2f} dB")
print(f"   Master File: {master_out_path}")
print(f"   Full Transcript ASR: \"{full_asr}\"")
print("=" * 70)
