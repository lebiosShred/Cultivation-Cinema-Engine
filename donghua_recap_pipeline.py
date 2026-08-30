import argparse
import json
import os
import subprocess
import sys
import time

try:
    from youtube_uploader import get_authenticated_service, upload_video
except ImportError:
    get_authenticated_service = None
    upload_video = None

def extract_keyframes(video_path, output_dir, timestamps=[60, 180, 360, 540]):
    """
    Extracts high-resolution 4K keyframe snapshots from the video for thumbnail creation.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_frames = []
    
    print(f"\n🖼️ Extracting 4K keyframes from {os.path.basename(video_path)}...")
    for ts in timestamps:
        out_file = os.path.join(output_dir, f"thumbnail_frame_{ts:04d}s.jpg")
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(ts),
            "-i", video_path,
            "-vframes", "1",
            "-q:v", "2",
            out_file
        ]
        res = subprocess.run(cmd, capture_output=True)
        if res.returncode == 0 and os.path.exists(out_file):
            generated_frames.append(out_file)
            print(f"  ✅ Extracted: {os.path.basename(out_file)} ({os.path.getsize(out_file)//1024} KB)")

    return generated_frames

def generate_highlight_teaser(video_path, output_path, start_time="00:03:00", duration="00:01:00"):
    """
    Cuts a crisp 60-second 4K highlight teaser clip using lossless FFmpeg cutting.
    """
    print(f"\n🎬 Compiling 60s 4K Highlight Teaser...")
    cmd = [
        "ffmpeg", "-y",
        "-ss", start_time,
        "-i", video_path,
        "-t", duration,
        "-c", "copy",
        output_path
    ]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode == 0 and os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"✅ 4K Teaser ready: {output_path} ({size_mb:.2f} MB)")
        return output_path
    else:
        print(f"❌ Teaser extraction error: {res.stderr.decode('utf-8', errors='ignore')}")
        return None

def build_metadata(episode_num=189, series_title="A Record of a Mortal's Journey to Immortality"):
    """
    Generates high-CTR, SEO-optimized title, description with chapters, and tags for Cultivation Cinema.
    """
    channel_name = "Cultivation Cinema"
    title = f"{series_title} Episode {episode_num} Breakdown & Highlights [4K UHD 60FPS] | 凡人修仙传"
    
    description = f"""🔥 Welcome to Cultivation Cinema — Experience Chinese Animation & Xianxia in Native 4K UHD!

In this episode of A Record of a Mortal's Journey to Immortality (凡人修仙传) Episode {episode_num}, Han Li faces escalating spiritual clashes in the Mortal Realm. 

⏱️ CHAPTER TIMESTAMPS:
00:00 - Episode {episode_num} Opening Recap
01:30 - Han Li's Tactical Cultivation Assessment
04:15 - Spiritual Battle Climax & Artifact Clash
07:45 - Nascent Soul Power Level Breakdown
12:00 - Final Analysis & Next Episode Preview

🎬 ABOUT CULTIVATION CINEMA:
We deliver theater-grade 4K 60FPS Donghua breakdowns, cultivation realm lore explanations, power scaling guides, and cinematic fight highlights.

🔔 Subscribe to Cultivation Cinema for weekly 4K Donghua releases and deep-dive lore!

#CultivationCinema #RMJI #Donghua #HanLi #ARecordOfAMortalsJourneyToImmortality #Cultivation #Xianxia #Anime4K #凡人修仙传
"""
    tags = [
        "Cultivation Cinema",
        "A Record of a Mortal's Journey to Immortality",
        f"RMJI Episode {episode_num}",
        "Han Li",
        "Donghua 4K",
        "Chinese Anime 4K 60FPS",
        "Cultivation Anime",
        "Xianxia",
        "RMJI 189",
        "凡人修仙传",
        "Battle Through The Heavens",
        "Perfect World Donghua",
        "Renegade Immortal",
        "Shrouding the Heavens",
        "Cultivation Cinema 4K"
    ]
    
    return title, description, tags

def main():
    parser = argparse.ArgumentParser(description="Donghua 4K Content Automation Pipeline")
    parser.add_argument("--video", default="a_record_of_a_mortal_s_journey_to_immortality_ep189_4k.mp4", help="Path to input 4K video")
    parser.add_argument("--episode", type=int, default=189, help="Episode number")
    parser.add_argument("--auto-upload", action="store_true", help="Automatically trigger YouTube Data API upload")
    parser.add_argument("--privacy", default="unlisted", choices=["public", "unlisted", "private"], help="YouTube privacy status")

    args = parser.parse_args()

    work_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(work_dir, args.video) if not os.path.isabs(args.video) else args.video

    if not os.path.exists(video_path):
        print(f"❌ Target video not found: {video_path}")
        sys.exit(1)

    print("=================================================================")
    print(f"🚀 Launching Donghua 4K Content Pipeline for Episode {args.episode}")
    print("=================================================================")

    # 1. Keyframe Extraction
    thumb_dir = os.path.join(work_dir, "thumbnails")
    frames = extract_keyframes(video_path, thumb_dir, timestamps=[90, 240, 420, 600])
    selected_thumb = frames[1] if len(frames) > 1 else (frames[0] if frames else None)

    # 2. Teaser Generation
    teaser_path = os.path.join(work_dir, f"rmji_ep{args.episode}_teaser_4k.mp4")
    generate_highlight_teaser(video_path, teaser_path, start_time="00:04:00", duration="00:01:00")

    # 3. SEO Metadata Generation
    title, description, tags = build_metadata(args.episode)

    print("\n📝 Generated YouTube Metadata:")
    print(f"📌 Title:\n  {title}")
    print(f"🏷️ Tags:\n  {', '.join(tags)}")
    print(f"🖼️ Thumbnail Asset: {selected_thumb}")

    # 4. Save metadata to JSON
    meta_json_path = os.path.join(work_dir, f"metadata_ep{args.episode}.json")
    with open(meta_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "title": title,
            "description": description,
            "tags": tags,
            "thumbnail": selected_thumb,
            "video": video_path,
            "teaser": teaser_path
        }, f, indent=2)
    print(f"\n💾 Metadata exported to: {meta_json_path}")

    # 5. Optional Direct YouTube Upload
    if args.auto_upload:
        if not get_authenticated_service:
            print("❌ Error: youtube_uploader module not found.")
            return

        print("\n🌐 Triggering YouTube API Auto-Upload...")
        try:
            yt = get_authenticated_service()
            upload_video(
                youtube=yt,
                file_path=video_path,
                title=title,
                description=description,
                tags=tags,
                category_id="1",
                privacy_status=args.privacy,
                thumbnail_path=selected_thumb
            )
        except Exception as ue:
            print(f"⚠️ Auto-upload error: {ue}")

if __name__ == "__main__":
    main()
