# Cultivation Cinema: Automated 4K Donghua Recap & Voiceover Engine

Production-grade, local neural voiceover and automated 4K 60FPS video publishing engine for **Cultivation Cinema** (@CultivationCinema), specializing in *A Record of a Mortal's Journey to Immortality* (RMJI / 凡人修仙传) and high-tier Xianxia donghua.

---

## 🎙️ Voiceover Engine: Fish Speech 1.5 (Option B: Crystal-Clear Streamer)

The voiceover pipeline runs locally on CUDA using **Fish Speech 1.5** (DualARTransformer + Firefly VQ-GAN vocoder) conditioned with a **Pristine Clean 117 Hz Streamer** acoustic profile to deliver clean, fast-paced, broadcast-grade YouTube commentary with zero vocal fry and zero background static.

### 🔑 Key Acoustic & De-Static Innovations

1. **Acoustic Reference Denoising**:
   * Pre-cleans the reference prompt with stationary spectral noise reduction and a \text{ Hz}$ high-pass filter, lowering reference noise floor from $-46.29\text{ dBFS}$ to $-85\text{ dBFS}$.
2. **Low-Entropy Deterministic Sampling**:
   * Uses 	emperature=0.30 and 	op_p=0.55 to eliminate codebook token jitter, acoustic fuzz, and high-frequency vocoder hash.
3. **Transparent Post-Vocoder Polish**:
   * Applies gentle spectral gating and \text{ Hz}$ subsonic rumble cut, achieving a **$-91.56\text{ dBFS}$ studio-black noise floor** and **.55\text{ dB}$ dynamic SNR**.
4. **Phonetic Text Normalization**:
   * Canonical Xianxia pronunciations (Han Li $\rightarrow$ Hahn Lee, Tihun $\rightarrow$ Tee-hoon, Episode 189 $\rightarrow$ Episode one hundred eighty-nine).

---

## 📂 Repository Structure

`
├── render_full_ep189_destatic_master.py  # Master Episode 189 zero-static production engine
├── test_destatic_pipeline.py             # De-static parameter & SNR evaluation suite
├── render_clear_throat_fishspeech.py     # Multi-seed acoustic audition script (117Hz / 144Hz / Studio)
├── tune_both_fish_and_cosyvoice.py       # Hyperparameter sweep & comparative tuning suite
├── daoist_ren_persona.json               # Channel host persona, pacing rules, and invariants
├── metadata_ep189.json                    # SEO-optimized title, description, chapter timestamps & tags
├── donghua_recap_pipeline.py             # 4K FFmpeg muxer, 60s teaser cutter & keyframe extractor
└── README.md                             # Documentation and usage guide
`

---

## 🚀 Quickstart & Usage

### 1. Run Crystal-Clear Voiceover Generation
`ash
python render_full_ep189_destatic_master.py
`
Outputs:
* Master Audio Track: ishspeech_option_b_destatic_master.wav (90.21s / -91.56 dBFS noise floor)
* 7 Individual Chapter Takes in ull_option_b_destatic_master/

### 2. Mux with 4K 60FPS Video & Cut Teaser
`ash
python donghua_recap_pipeline.py
`
Extracts 4K keyframe snapshots for thumbnails, compiles a lossless 60s highlight teaser, and exports YouTube-ready metadata.

---

## 📜 License
MIT License. Free and Open Source.
