import sounddevice as sd
import numpy as np

# Microphone device selected from your device list.
DEVICE_ID = 1

# Record 5 seconds at the microphone's native sample rate.
device_info = sd.query_devices(DEVICE_ID)
sample_rate = int(device_info["default_samplerate"])

print(f"Microphone: {device_info['name']}")
print(f"Sample rate: {sample_rate} Hz")
print("Speak normally for 5 seconds...")

audio = sd.rec(
    int(5 * sample_rate),
    samplerate=sample_rate,
    channels=1,
    dtype="float32",
    device=DEVICE_ID
)

sd.wait()

# Measure the recorded signal to verify that audio was captured.
peak = float(np.max(np.abs(audio)))
rms = float(np.sqrt(np.mean(np.square(audio))))

print(f"Recording complete. Peak level: {peak:.4f}")
print(f"RMS level: {rms:.4f}")

if peak > 0.01:
    print("Microphone is capturing audio.")
else:
    print("Audio level is very low. Check the microphone and permissions.")
