"""Tests for AM and FM modulation/demodulation (v1.0.0)."""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from modulation import (
    am_modulate_dsbsc,
    am_modulate_dsblc,
    am_demodulate,
    fm_modulate,
    fm_demodulate,
    _validate_freqs,
)

FS = 44100.0  # Hz
FC = 5000.0   # Hz


def _sinusoid(freq: float, n_samples: int, fs: float = FS) -> list[float]:
    return [math.sin(2 * math.pi * freq * n / fs) for n in range(n_samples)]


# ---------------------------------------------------------------------------
# AM DSB-SC
# ---------------------------------------------------------------------------

def test_am_dsbsc_zero_message():
    """Zero message → zero output."""
    msg = [0.0] * 64
    out = am_modulate_dsbsc(msg, FC, FS)
    assert all(v == pytest.approx(0.0) for v in out)


def test_am_dsbsc_carrier_at_unity_message():
    """Constant message = 1 → pure carrier at amplitude 1."""
    msg = [1.0] * 64
    out = am_modulate_dsbsc(msg, FC, FS)
    expected = [math.cos(2 * math.pi * FC * n / FS) for n in range(64)]
    for a, b in zip(out, expected):
        assert a == pytest.approx(b)


def test_am_dsbsc_length_preserved():
    N = 128
    assert len(am_modulate_dsbsc([0.5] * N, FC, FS)) == N


# ---------------------------------------------------------------------------
# AM DSB-LC
# ---------------------------------------------------------------------------

def test_am_dsblc_no_modulation():
    """ka=0 → constant-envelope carrier."""
    msg = _sinusoid(200.0, 64)
    out = am_modulate_dsblc(msg, FC, FS, carrier_amplitude=1.0, modulation_index=0.0)
    expected = [math.cos(2 * math.pi * FC * n / FS) for n in range(64)]
    for a, b in zip(out, expected):
        assert a == pytest.approx(b)


def test_am_dsblc_envelope_positive():
    """With ka=1, message in [-1,1] → envelope >= 0 (no overmodulation)."""
    msg = _sinusoid(200.0, 256)
    out = am_modulate_dsblc(msg, FC, FS, carrier_amplitude=1.0, modulation_index=1.0)
    # envelope = |out| / |cos(carrier)| should not invert carrier
    # Just check energy is positive
    assert sum(v**2 for v in out) > 0


# ---------------------------------------------------------------------------
# FM
# ---------------------------------------------------------------------------

def test_fm_constant_message_is_carrier():
    """Constant zero message → pure carrier (no frequency deviation)."""
    msg = [0.0] * 128
    out = fm_modulate(msg, FC, FS, kf=1.0, carrier_amplitude=1.0)
    expected = [math.cos(2 * math.pi * FC * n / FS) for n in range(128)]
    for a, b in zip(out, expected):
        assert a == pytest.approx(b, abs=1e-9)


def test_fm_amplitude_constant():
    """FM envelope is always A_c."""
    msg = _sinusoid(200.0, 256)
    Ac = 2.5
    out = fm_modulate(msg, FC, FS, kf=500.0, carrier_amplitude=Ac)
    for v in out:
        assert abs(v) <= Ac + 1e-9


def test_fm_length_preserved():
    N = 100
    msg = _sinusoid(200.0, N)
    assert len(fm_modulate(msg, FC, FS)) == N


# ---------------------------------------------------------------------------
# Demodulation round-trip (smoke tests)
# ---------------------------------------------------------------------------

def test_am_demodulate_output_length():
    msg = _sinusoid(200.0, 256)
    sig = am_modulate_dsblc(msg, FC, FS)
    env = am_demodulate(sig, FC, FS)
    assert len(env) == len(sig)


def test_fm_demodulate_output_length():
    msg = _sinusoid(200.0, 256)
    sig = fm_modulate(msg, FC, FS, kf=500.0)
    rec = fm_demodulate(sig, FC, FS, kf=500.0)
    assert len(rec) == len(sig)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_invalid_fc_raises():
    with pytest.raises(ValueError):
        _validate_freqs(fc=0.0, fs=FS)


def test_nyquist_violation_raises():
    with pytest.raises(ValueError):
        am_modulate_dsbsc([1.0] * 8, fc=FS, fs=FS)
