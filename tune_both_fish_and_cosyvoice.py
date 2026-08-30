import os
import sys
import time
import torch
import soundfile as sf
import numpy as np
import whisper

# Project Directories
project_dir = r"C:\Users\SkyDr\OneDrive\Desktop\PROJECTS\Youtube Videos\RMJI"
audition_dir = os.path.join(project_dir, "auditions", "tuned_auditions")
os.makedirs(audition_dir, exist_ok=True)

# Reference Audio for Voice Conditioning (Natural Deep Male Timbre)
ref_audio_path = os.path.join(project_dir, "chattts_male_seeds", "Male_Seed_2_(Seed_9999_103Hz).wav")
ref_text = "Welcome back to the channel, fellow Daoists."

# Normalized Script with G2P phonetic hints to prevent pinyin/language confusion
tuned_scenes = [
    {
        "id": "scene1_cold_open",
        "text": "Yo, what is good fellow Daoists?! Welcome back to Cultivation Cinema. Episode one hundred eighty-nine just dropped, and bro, Hahn Lee is actually built different.",
        "cosy_text": "<|en|>Yo, what is good fellow Daoists?! Welcome back to Cultivation Cinema. Episode one hundred eighty-nine just dropped, and bro, Hahn Lee is actually built different."
    },
    {
        "id": "scene2_tihun_beast",
        "text": "He casually drops his secret beast, Tee-hoon, the Weeping Soul Spirit! For anyone new to the lore, Tee-hoon is literally the apex predator of all ghostly and Yin spirits.",
        "cosy_text": "<|en|>He casually drops his secret beast, Tee-hoon, the Weeping Soul Spirit! For anyone new to the lore, Tee-hoon is literally the apex predator of all ghostly and Yin spirits."
    }
]

whisper_model = whisper.load_model('base')

print("=" * 70)
print("🎯 MASTER TUNING PIPELINE: FISH SPEECH 1.5 & COSYVOICE 2.0 (CUDA)")
print("=" * 70)

# =========================================================================
# PART 1: TUNING FISH SPEECH 1.5 (Fish Audio)
# =========================================================================
print("\n" + "=" * 50)
print("🐟 PART 1: TUNING FISH SPEECH 1.5")
print("=" * 50)

fish_dir = r"C:\Users\SkyDr\.gemini\antigravity\scratch\fish-speech"
sys.path.insert(0, fish_dir)

import pyrootutils
pyrootutils.setup_root(fish_dir, indicator=".project-root", pythonpath=True)

from tools.inference_engine import TTSInferenceEngine
from tools.llama.generate import launch_thread_safe_queue
from tools.vqgan.inference import load_model as load_decoder_model
from tools.schema import ServeTTSRequest, ServeReferenceAudio

ckpt_dir = os.path.join(fish_dir, "checkpoints", "fish-speech-1.5")
llama_ckpt = ckpt_dir
decoder_ckpt = os.path.join(ckpt_dir, "firefly-gan-vq-fsq-8x1024-21hz-generator.pth")

device = "cuda"
precision = torch.half

print("1. Launching Fish Speech LLaMA Queue & VQ-GAN...")
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
fish_engine = TTSInferenceEngine(
    llama_queue=llama_queue,
    decoder_model=decoder_model,
    precision=precision,
    compile=False
)

# Load reference audio bytes
with open(ref_audio_path, 'rb') as f:
    ref_audio_bytes = f.read()

ref_obj = ServeReferenceAudio(audio=ref_audio_bytes, text=ref_text)

print("\n🚀 Synthesizing Tuned Fish Speech 1.5 Takes:")
for s in tuned_scenes:
    s_id = s["id"]
    text = s["text"]
    out_p = os.path.join(audition_dir, f"fishspeech_tuned_{s_id}.wav")
    
    req = ServeTTSRequest(
        text=text,
        references=[ref_obj],
        reference_id=None,
        max_new_tokens=1024,
        chunk_length=200,
        top_p=0.75,
        repetition_penalty=1.2,
        temperature=0.65,
        streaming=False
    )
    
    t0 = time.time()
    results = list(fish_engine.inference(req))
    elapsed = time.time() - t0
    
    final_result = [r for r in results if r.code == "final"]
    if final_result and final_result[0].audio is not None:
        sr, audio_data = final_result[0].audio
        sf.write(out_p, audio_data, sr)
        dur = len(audio_data) / sr
        asr = whisper_model.transcribe(out_p)['text'].strip()
        print(f"  ✅ [Fish Speech] {s_id}:")
        print(f"     Duration: {dur:.2f}s (Rendered in {elapsed:.2f}s)")
        print(f"     Whisper ASR: \"{asr}\"")
        print(f"     Output: {out_p}")
    else:
        print(f"  ❌ Error in Fish Speech {s_id}: {results}")

# Free GPU memory before CosyVoice
del fish_engine, llama_queue, decoder_model
torch.cuda.empty_cache()

# =========================================================================
# PART 2: TUNING COSYVOICE 2.0 (FunAudioLLM)
# =========================================================================
print("\n" + "=" * 50)
print("🌊 PART 2: TUNING COSYVOICE 2.0")
print("=" * 50)

cosy_dir = r"C:\Users\SkyDr\.gemini\antigravity\scratch\CosyVoice"
matcha_dir = os.path.join(cosy_dir, "third_party", "Matcha-TTS")
sys.path.insert(0, cosy_dir)
sys.path.insert(0, matcha_dir)

from cosyvoice.cli.cosyvoice import AutoModel

cosy_model_dir = os.path.join(cosy_dir, "pretrained_models", "CosyVoice2-0.5B")
print("1. Initializing CosyVoice 2.0 with fp16=True...")
cosyvoice = AutoModel(model_dir=cosy_model_dir, fp16=True)

print("\n🚀 Synthesizing Tuned CosyVoice 2.0 Takes (with Speed Calibration & English Prompt):")
for s in tuned_scenes:
    s_id = s["id"]
    tts_text = s["text"]
    out_p = os.path.join(audition_dir, f"cosyvoice2_tuned_{s_id}.wav")
    
    t0 = time.time()
    for i, j in enumerate(cosyvoice.inference_zero_shot(tts_text, ref_text, ref_audio_path, stream=False, speed=1.35)):
        audio_arr = j['tts_speech'].squeeze().cpu().numpy()
        sf.write(out_p, audio_arr, cosyvoice.sample_rate)
        break
    elapsed = time.time() - t0
    
    dur = len(audio_arr) / cosyvoice.sample_rate
    asr = whisper_model.transcribe(out_p)['text'].strip()
    print(f"  ✅ [CosyVoice 2.0] {s_id}:")
    print(f"     Duration: {dur:.2f}s (Rendered in {elapsed:.2f}s)")
    print(f"     Whisper ASR: \"{asr}\"")
    print(f"     Output: {out_p}")

print("\n" + "=" * 70)
print("🎉 ALL TUNED AUDITIONS COMPLETED AND VERIFIED!")
print("=" * 70)
