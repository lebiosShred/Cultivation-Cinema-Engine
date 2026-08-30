# Cultivation Cinema: Automated 4K Donghua Recap & Voiceover Engine

Production-grade, local neural voiceover and automated 4K 60FPS video publishing engine for **Cultivation Cinema** (@CultivationCinema), specializing in *A Record of a Mortal's Journey to Immortality* (RMJI / 凡人修仙传) and high-tier Xianxia donghua.

---

## 🎙️ Voiceover Engine: Fish Speech 1.5 (Option B: Smooth Streamer)

The voiceover pipeline runs locally on CUDA using **Fish Speech 1.5** (DualARTransformer + Firefly VQ-GAN vocoder) conditioned with a **117 Hz Smooth Streamer** acoustic reference to deliver clean, fast-paced, high-retention YouTube commentary with zero vocal fry or robotic artifacts.

### 🔑 Key Pipeline Innovations

1. **Phonetic Text Normalization**:
   * Eliminates pronunciation errors for complex Xianxia terminology:
     * Episode 189 $\rightarrow$ Episode one hundred eighty-nine
     * Han Li $\rightarrow$ Hahn Lee
     * Tihun $\rightarrow$ Tee-hoon
     * 72 Azure Bamboo swords $\rightarrow$ seventy-two Azure Bamboo Cloudswarm swords
2. **Acoustic Anti-Fry Conditioning**:
   * Selected a resonant 117 Hz streamer vocal seed (Male_Seed_1_117Hz) to eliminate glottal raspiness and vocal fatigue.
3. **Continuous Flow & Breath Gap Assembly**:
   * Synthesizes 7 core narrative thought-streams.
   * Assembles with 220ms natural breath pauses and 15ms $\cos^2$ micro-fades.
   * Peak normalized to $-1.0\text{ dBFS}$ for broadcast loudness.

---

## 📂 Repository Structure

`
├── render_full_ep189_option_b.py       # Master Fish Speech 1.5 Episode 189 synthesis script
├── render_clear_throat_fishspeech.py   # Multi-seed acoustic audition script (117Hz / 144Hz / Studio)
├── tune_both_fish_and_cosyvoice.py     # Hyperparameter sweep & comparative tuning suite
├── daoist_ren_persona.json             # Channel host persona, pacing rules, and invariants
├── metadata_ep189.json                  # SEO-optimized title, description, chapter timestamps & tags
├── donghua_recap_pipeline.py           # 4K FFmpeg muxer, 60s teaser cutter & keyframe extractor
└── README.md                           # Documentation and usage guide
`

---

## 🚀 Quickstart & Usage

### 1. Run Full Voiceover Generation
`ash
python render_full_ep189_option_b.py
`
Outputs:
* Master Audio Track: ishspeech_option_b_full_master.wav (82.54s)
* 7 Individual Chapter Takes in ull_option_b_production/

### 2. Mux with 4K 60FPS Video & Cut Teaser
`ash
python donghua_recap_pipeline.py
`
Extracts 4K keyframe snapshots for thumbnails, compiles a lossless 60s highlight teaser, and exports YouTube-ready metadata.

---

## 📜 License
MIT License. Free and Open Source.
