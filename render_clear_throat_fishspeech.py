import os
import sys
import time
import torch
import soundfile as sf
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
audition_dir = os.path.join(project_dir, "auditions", "fishspeech_smooth_auditions")
os.makedirs(audition_dir, exist_ok=True)

ckpt_dir = os.path.join(fish_dir, "checkpoints", "fish-speech-1.5")
llama_ckpt = ckpt_dir
decoder_ckpt = os.path.join(ckpt_dir, "firefly-gan-vq-fsq-8x1024-21hz-generator.pth")

device = "cuda"
precision = torch.half

print("1. Initializing Fish Speech Engine...")
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

# 3 Candidate Reference Voices (Clean, smooth vocal tract, no sore throat / vocal fry)
candidates = [
    {
        "name": "smooth_streamer_117hz",
        "wav": os.path.join(project_dir, "chattts_male_seeds", "Male_Seed_1_(Seed_4567_117Hz).wav"),
        "desc": "Crisp Clear Natural Male Streamer (117 Hz - No Vocal Fry)"
    },
    {
        "name": "bright_streamer_144hz",
        "wav": os.path.join(project_dir, "chattts_male_seeds", "Male_Seed_3_(Seed_42_144Hz).wav"),
        "desc": "Bright Energetic Resonant Male Host (144 Hz - Smooth & Clear)"
    },
    {
        "name": "studio_narrator_adam",
        "wav": os.path.join(project_dir, "auditions", "kokoro_streamer_auditions", "kokoro_am_adam_scene1_cold_open.wav"),
        "desc": "Pristine Broadcast Studio Male Narrator (Balanced Smooth Warmth)"
    }
]

# Normalized scene scripts
test_scenes = [
    (
        "scene1_cold_open",
        "Yo, what is good fellow Daoists?! Welcome back to Cultivation Cinema. Episode one hundred eighty-nine just dropped, and bro, Hahn Lee is actually built different."
    ),
    (
        "scene2_tihun_beast",
        "He casually drops his secret beast, Tee-hoon, the Weeping Soul Spirit! For anyone new to the lore, Tee-hoon is literally the apex predator of all ghostly and Yin spirits."
    )
]

print("\n🚀 Synthesizing Smooth, Healthy Voice Options in Fish Speech 1.5:")
results_summary = []

for cand in candidates:
    wav_path = cand["wav"]
    cand_name = cand["name"]
    desc = cand["desc"]
    
    if not os.path.exists(wav_path):
        print(f"⚠️ Warning: Reference {wav_path} not found, skipping.")
        continue
    
    # Transcribe reference wav to ensure exact transcript
    ref_txt = whisper_model.transcribe(wav_path)['text'].strip()
    with open(wav_path, 'rb') as f:
        ref_bytes = f.read()
    ref_obj = ServeReferenceAudio(audio=ref_bytes, text=ref_txt)
    
    print(f"\n🎙️ Testing Voice: [{cand_name}] - {desc}")
    print(f"   Reference transcript: \"{ref_txt}\"")
    
    for s_tag, s_text in test_scenes:
        out_p = os.path.join(audition_dir, f"fishspeech_{cand_name}_{s_tag}.wav")
        
        req = ServeTTSRequest(
            text=s_text,
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
        results = list(engine.inference(req))
        elapsed = time.time() - t0
        
        final_result = [r for r in results if r.code == "final"]
        if final_result and final_result[0].audio is not None:
            sr, audio_data = final_result[0].audio
            sf.write(out_p, audio_data, sr)
            dur = len(audio_data) / sr
            asr = whisper_model.transcribe(out_p)['text'].strip()
            print(f"   ✅ Take [{s_tag}]:")
            print(f"      Duration: {dur:.2f}s (Rendered in {elapsed:.2f}s)")
            print(f"      Whisper ASR: \"{asr}\"")
            print(f"      File: {out_p}")
            results_summary.append({
                "voice": cand_name,
                "desc": desc,
                "scene": s_tag,
                "file": out_p,
                "duration": dur,
                "asr": asr
            })
        else:
            print(f"   ❌ Error generating {s_tag}: {results}")

print("\n" + "=" * 70)
print("🎉 ALL SMOOTH FISH SPEECH AUDITIONS COMPLETED!")
print("=" * 70)
