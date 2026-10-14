"""Utility to generate synthetic vs organic sample audio files for testing and demoing."""
import os
import numpy as np
import soundfile as sf

def generate_samples(output_dir: str = "samples"):
    os.makedirs(output_dir, exist_ok=True)
    sr = 16000
    duration = 3.0  # seconds
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)

    # 1. Simulated Synthetic / Cloned Voice Note:
    # Rigid harmonic pitch (180 Hz) without organic micro-jitter, plus digital silence boundaries
    f0 = 180.0
    synthetic = 0.5 * np.sin(2 * np.pi * f0 * t) + 0.25 * np.sin(2 * np.pi * 2 * f0 * t) + 0.12 * np.sin(2 * np.pi * 3 * f0 * t)
    # Add digital silence sections (common in TTS output)
    synthetic[: int(sr * 0.4)] = 0.0
    synthetic[-int(sr * 0.4):] = 0.0
    synth_path = os.path.join(output_dir, "synthetic_voice_sample.wav")
    sf.write(synth_path, synthetic.astype(np.float32), sr)
    print(f"Generated synthetic test audio: {synth_path}")

    # 2. Simulated Organic Voice Note:
    # Fluctuating pitch with micro-jitter, harmonic richness, breathing noise floor
    pitch_modulation = 150.0 + 30.0 * np.sin(2 * np.pi * 1.5 * t) + 8.0 * np.sin(2 * np.pi * 5.0 * t)
    phase = 2 * np.pi * np.cumsum(pitch_modulation) / sr
    organic = 0.4 * np.sin(phase) + 0.2 * np.sin(2 * phase) + 0.1 * np.sin(3 * phase)
    # Add ambient acoustic noise floor (fan/room-tone typical of WhatsApp audio)
    noise = 0.015 * np.random.normal(0, 1, len(t))
    organic = organic + noise
    organic_path = os.path.join(output_dir, "organic_voice_sample.wav")
    sf.write(organic_path, organic.astype(np.float32), sr)
    print(f"Generated organic test audio: {organic_path}")

if __name__ == "__main__":
    generate_samples()
