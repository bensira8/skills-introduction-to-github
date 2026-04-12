"""Tests for the RLC analogue filter (v1.0.0)."""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from rlc import RLCFilter, FilterType, rlc_lowpass, rlc_highpass, rlc_bandpass

# RLC component values: R=1Ω, L=1mH, C=1µF → f0 ≈ 5033 Hz
R, L, C = 1.0, 1e-3, 1e-6
FS = 96000.0  # Hz


def _sine(freq: float, n: int, fs: float = FS, amplitude: float = 1.0) -> list[float]:
    return [amplitude * math.sin(2 * math.pi * freq * k / fs) for k in range(n)]


def _rms(x: list[float]) -> float:
    return math.sqrt(sum(v**2 for v in x) / len(x))


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_resonant_frequency():
    f = RLCFilter(R, L, C, FS)
    expected_f0 = 1.0 / (2 * math.pi * math.sqrt(L * C))
    assert f.resonant_frequency_hz == pytest.approx(expected_f0, rel=1e-6)


def test_invalid_R_raises():
    with pytest.raises(ValueError):
        RLCFilter(0.0, L, C, FS)


def test_invalid_fs_raises():
    with pytest.raises(ValueError):
        RLCFilter(R, L, C, 0.0)


# ---------------------------------------------------------------------------
# Low-pass
# ---------------------------------------------------------------------------

def test_lp_passes_dc():
    """DC signal (freq=0) should pass through a low-pass filter."""
    filt = rlc_lowpass(R, L, C, FS)
    sig = [1.0] * 2000
    out = filt.process(sig)
    # After settling, output should be near 1.0
    assert abs(sum(out[-100:]) / 100 - 1.0) < 0.01


def test_lp_attenuates_high_freq():
    """Low-pass must attenuate signals well above f0."""
    f0 = 1.0 / (2 * math.pi * math.sqrt(L * C))
    filt = rlc_lowpass(R, L, C, FS)
    # Frequency 50x above f0
    high = _sine(min(f0 * 50, FS / 2 - 100), 4096)
    low_ref = _sine(f0 / 100, 4096)
    out_high = filt.process(high)
    filt.reset()
    out_low = filt.process(low_ref)
    assert _rms(out_high[1000:]) < _rms(out_low[1000:]) * 0.2


# ---------------------------------------------------------------------------
# High-pass
# ---------------------------------------------------------------------------

def test_hp_blocks_dc():
    """DC signal must be blocked by a high-pass filter (steady-state output → 0)."""
    filt = rlc_highpass(R, L, C, FS)
    sig = [1.0] * 4000
    out = filt.process(sig)
    assert abs(sum(out[-100:]) / 100) < 0.01


def test_hp_passes_high_freq():
    """Signal well above f0 should largely pass through a high-pass filter."""
    f0 = 1.0 / (2 * math.pi * math.sqrt(L * C))
    filt = rlc_highpass(R, L, C, FS)
    high = _sine(min(f0 * 20, FS / 2 - 100), 4096)
    out = filt.process(high)
    assert _rms(out[2000:]) > 0.1


# ---------------------------------------------------------------------------
# Band-pass
# ---------------------------------------------------------------------------

def test_bp_peak_near_resonance():
    """Band-pass output is maximised near f0."""
    f0 = 1.0 / (2 * math.pi * math.sqrt(L * C))
    N = 4096
    freqs = [f0 / 10, f0, f0 * 10]
    rms_values = []
    for freq in freqs:
        filt = rlc_bandpass(R, L, C, FS)
        out = filt.process(_sine(min(freq, FS / 2 - 100), N))
        rms_values.append(_rms(out[N // 2:]))
    # Peak should be at f0 (index 1)
    assert rms_values[1] == max(rms_values)


# ---------------------------------------------------------------------------
# Reset & state
# ---------------------------------------------------------------------------

def test_reset_clears_state():
    filt = rlc_lowpass(R, L, C, FS)
    filt.process(_sine(1000.0, 500))
    filt.reset()
    assert filt._w1 == 0.0
    assert filt._w2 == 0.0


def test_process_length_preserved():
    filt = rlc_lowpass(R, L, C, FS)
    sig = _sine(100.0, 123)
    assert len(filt.process(sig)) == 123


# ---------------------------------------------------------------------------
# Convenience constructors
# ---------------------------------------------------------------------------

def test_convenience_constructors():
    lp = rlc_lowpass(R, L, C, FS)
    hp = rlc_highpass(R, L, C, FS)
    bp = rlc_bandpass(R, L, C, FS)
    assert lp.filter_type == FilterType.LOW_PASS
    assert hp.filter_type == FilterType.HIGH_PASS
    assert bp.filter_type == FilterType.BAND_PASS
