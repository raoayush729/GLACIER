import queue
import re
import time
from collections import deque

import numpy as np
import requests
import sounddevice as sd
import speech_recognition as sr

# ---------------- CONFIG ----------------
BACKEND_URL = "http://127.0.0.1:8000"
SAMPLE_RATE = 16000
FRAME_S = 0.03                         # 30 ms frames
FRAME_SIZE = int(SAMPLE_RATE * FRAME_S)
PRE_ROLL_FRAMES = 12                   # ~0.36 s kept from BEFORE speech starts
MIN_LEVEL = 150.0                      # raise if background noise triggers it, lower if it misses you
END_SILENCE = 0.5                      # silence that ends one phrase
COMMAND_START_TIMEOUT = 6.0            # wait this long for the command after the wake word
COMMAND_FOLLOWUP = 1.2                 # extra silence after the last phrase that ends the command
MAX_PHRASE = 15.0
RESUME_TIMEOUT = 300                   # max wait for GLACIER to finish thinking + speaking

WAKE_WORD_VARIANTS = {"glacier", "glaciers", "glasier", "glazier", "glaysher", "glacia", "glassier"}

recognizer = sr.Recognizer()
audio_q = queue.Queue()                # the mic NEVER stops: audio is queued while we transcribe
pre_roll = deque(maxlen=PRE_ROLL_FRAMES)
noise_floor = 100.0


# ---------------- BACKEND ----------------
def send(event_type, message="", mode=""):
    try:
        requests.post(f"{BACKEND_URL}/voice-event",
                      json={"type": event_type, "message": message, "mode": mode}, timeout=2)
    except requests.RequestException as error:
        print(f"Could not reach GLACIER backend: {error}")


def get_mode():
    try:
        return requests.get(f"{BACKEND_URL}/voice-state", timeout=2).json().get("mode")
    except requests.RequestException:
        return None


# ---------------- AUDIO ----------------
def on_audio(indata, frames, time_info, status):
    audio_q.put(indata[:, 0].copy())


def rms(frame):
    return float(np.sqrt(np.mean(frame.astype(np.float32) ** 2)))


def is_speech(frame):
    global noise_floor
    level = rms(frame)
    loud = level > max(MIN_LEVEL, noise_floor * 3)
    if not loud:
        noise_floor = 0.98 * noise_floor + 0.02 * level
    return loud


def collect_phrase(start_timeout=None):
    """Block until one phrase (speech followed by a short silence) is captured.
    Returns None if no speech starts within start_timeout seconds."""
    frames, silent, waited, started = [], 0.0, 0.0, False
    while True:
        frame = audio_q.get()
        pre_roll.append(frame)
        loud = is_speech(frame)
        if not started:
            if loud:
                started, frames = True, list(pre_roll)   # includes audio from just before speech
            else:
                waited += FRAME_S
                if start_timeout is not None and waited >= start_timeout:
                    return None
            continue
        frames.append(frame)
        silent = 0.0 if loud else silent + FRAME_S
        if silent >= END_SILENCE or len(frames) * FRAME_S >= MAX_PHRASE:
            return np.concatenate(frames)


def transcribe(audio):
    data = sr.AudioData(audio.astype(np.int16).tobytes(), SAMPLE_RATE, 2)
    try:
        return recognizer.recognize_google(data, language="en-US").strip()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as error:
        print(f"Speech service error: {error}")
        return ""


def split_wake(text):
    """Return (heard_wake_word, words_spoken_after_it)."""
    words = text.split()
    for i, word in enumerate(words):
        if re.sub(r"[^a-z]", "", word.lower()) in WAKE_WORD_VARIANTS:
            return True, " ".join(words[i + 1:])
    return False, ""


def drain_audio():
    while not audio_q.empty():
        audio_q.get_nowait()
    pre_roll.clear()


# ---------------- MODES ----------------
def wait_until_stable():
    """While GLACIER thinks and speaks, ignore the mic (so it can't hear itself)."""
    deadline = time.time() + RESUME_TIMEOUT
    while time.time() < deadline:
        drain_audio()
        if get_mode() in ("stable", None):
            break
        time.sleep(0.2)
    time.sleep(0.4)                    # let the speaker tail fade out
    drain_audio()


def run_command(first_words):
    send("mode", mode="listening")     # overlay glows now; audio keeps queueing meanwhile
    parts = [first_words] if first_words else []
    if parts:
        send("partial", " ".join(parts))

    while True:
        phrase = collect_phrase(COMMAND_FOLLOWUP if parts else COMMAND_START_TIMEOUT)
        if phrase is None:
            break
        text = transcribe(phrase)
        if text:
            parts.append(text)
            send("partial", " ".join(parts))   # live text in the chat box

    command = " ".join(parts).strip()
    if command:
        print(f"Command: {command}")
        send("command", command)        # backend switches to "executing"
        wait_until_stable()
    else:
        print("No command heard.")
        send("mode", mode="stable")


def main():
    print("=" * 50)
    print("  GLACIER VOICE  -  say 'Glacier' (Ctrl+C to stop)")
    print("=" * 50)
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16",
                        blocksize=FRAME_SIZE, callback=on_audio):
        global noise_floor
        noise_floor = float(np.median([rms(audio_q.get()) for _ in range(int(1 / FRAME_S))]))
        send("mode", mode="stable")

        while True:
            try:
                text = transcribe(collect_phrase())
                if text:
                    print(f"Heard: {text}")
                found, rest = split_wake(text)
                if found:
                    print("Wake word detected!")
                    run_command(rest)
                    print("Listening for 'Glacier'...")
            except KeyboardInterrupt:
                raise
            except Exception as error:
                print(f"Voice listener error: {error}")
                time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        send("mode", mode="stable")
        print("\nGLACIER voice listener stopped.")