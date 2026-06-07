import os
import subprocess
import time


def main():
    fps = 90
    duration = 120  # seconds
    display = os.environ.get("DISPLAY", ":0")
    output_path = os.path.join("videos", f"recording_{int(time.time())}.mp4")

    # Capture region: set size to one monitor's resolution and offset to its
    # top-left corner. For the left monitor use offset 0,0; for the right
    # monitor use offset 1920,0 (or whatever your left monitor's width is).
    capture_size = "1920x1080"
    capture_offset = "1920,0"  # change to "1920,0" to record the right monitor

    # Use ffmpeg x11grab to capture the X11 display directly at true 60fps.
    # This bypasses the Selenium screenshot bottleneck entirely.
    ffmpeg_proc = subprocess.Popen([
        "ffmpeg", "-y",
        "-f", "x11grab",
        "-framerate", str(fps),
        "-video_size", capture_size,
        "-i", f"{display}+{capture_offset}",
        "-r", str(fps),
        "-c:v", "libx264",
        "-crf", "15",       # quality: 0=lossless, 51=worst; default 23
        "-preset", "fast",  # encoding speed vs compression; fast is safe for real-time
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_path,
    ], stdin=subprocess.PIPE)

    time.sleep(duration)

    # Send 'q' to stdin — the proper ffmpeg quit signal that finalizes the file
    ffmpeg_proc.communicate(input=b"q")
    ffmpeg_proc.wait()

    print(f"Recording saved to {output_path}")


if __name__ == "__main__":
    main()
