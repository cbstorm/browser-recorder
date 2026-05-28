from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import subprocess
import time


def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--kiosk")
    options.add_argument("--disable-features=FullscreenNotification")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    # webdriver-manager sometimes resolves to a non-executable file in the
    # extracted directory (e.g. THIRD_PARTY_NOTICES.chromedriver). Walk up to
    # the containing folder and pick the plain "chromedriver" binary instead.
    wdm_path = ChromeDriverManager().install()
    chromedriver_path = os.path.join(os.path.dirname(wdm_path), "chromedriver")
    if not os.path.isfile(chromedriver_path):
        chromedriver_path = wdm_path  # fallback to whatever wdm returned

    driver = webdriver.Chrome(
        service=Service(chromedriver_path),
        options=options,
    )

    driver.get("http://localhost:3000")

    # Give the page a moment to fully render before recording starts
    time.sleep(1)

    fps = 90
    duration = 4  # seconds
    display = os.environ.get("DISPLAY", ":0")
    output_path = os.path.join(os.path.expanduser("~"), "Downloads", "recording.mp4")

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
        "-crf", "12",       # quality: 0=lossless, 51=worst; default 23
        "-preset", "fast",  # encoding speed vs compression; fast is safe for real-time
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_path,
    ], stdin=subprocess.PIPE)

    time.sleep(duration)

    # Send 'q' to stdin — the proper ffmpeg quit signal that finalizes the file
    ffmpeg_proc.communicate(input=b"q")
    ffmpeg_proc.wait()

    driver.quit()

    print(f"Recording saved to {output_path}")


if __name__ == "__main__":
    main()
