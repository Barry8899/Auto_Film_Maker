import subprocess
import os

def test_aliyun_generation():
    cmd = [
        "/home/admin/.openclaw/venvs/video-director/bin/python",
        "/home/admin/.openclaw/workspace/auto_film_maker/tools/aliyun_video_generation.py",
        "--prompt", "The man in the image smiles gently. Keep the background and lighting consistent. Natural subtle motion.",
        "--model", "wan2.6-i2v-us",
        "--seconds", "5",
        "--reference", "/home/admin/.openclaw/workspace/outputs/doctor_strange_front_real.jpg",
        "--output_path", "/home/admin/.openclaw/workspace/outputs/test_aliyun_smile.mp4",
        "--manifest_path", "/home/admin/.openclaw/workspace/auto_film_maker/repo/S6_Video_Generation/stark_and_dad/asset_manifest.json",
        "--shot_id", "Shot_06"
    ]
    
    print("Executing command:")
    print(" ".join(cmd))
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)
    
if __name__ == "__main__":
    test_aliyun_generation()