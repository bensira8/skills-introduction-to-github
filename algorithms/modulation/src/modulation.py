# ALGO-META
# name: modulation
# version: 1.0.0
# category: signal-processing / communications
# math: AM (DSB-LC, DSB-SC) and FM modulation + envelope/FM demodulation
# inputs: message signal m(t), carrier frequency fc, sampling frequency fs
# outputs: modulated/demodulated signal (list[float])
"""
Amplitude Modulation (AM) and Frequency Modulation (FM).

Version: 1.0.0

Mathematical definitions
------------------------

AM — Double-Sideband Large-Carrier (DSB-LC):
    s(t) = A_c [1 + k_a · m(t)] · cos(2π f_c t)

AM — Double-Sideband Suppressed-Carrier (DSB-SC):
    s(t) = m(t) · cos(2π f_c t)

AM Demodulation (envelope detector, discrete):
    envelope[n] = |analytic_signal[n]|   (Hilbert approach, approximated here
                                           with a simple full-wave rectifier +
                                           first-order IIR low-pass filter)

FM:
    s(t) = A_c · cos[2π f_c t + 2π k_f · ∫ m(τ) dτ]

    In discrete time with sampling period T_s = 1/f_s:
        phase[n] = 2π f_c n T_s + 2π k_f T_s · cumsum(m[n])
        s[n]     = A_c · cos(phase[n])

FM Demodulation (discriminator — discrete derivative of instantaneous phase):
    φ̂[n] ≈ angle(s_a[n] · conj(s_a[n-1])) / (2π T_s)   (instantaneous freq)
    m̂[n] = (φ̂[n] - f_c) / k_f
"""

from __future__ import annotations

import math
from typing import Sequence


# ---------------------------------------------------------------------------
# AM Modulation
# ---------------------------------------------------------------------------

def am_modulate_dsbsc(
    message: Sequence[float],
    fc: float,
    fs: float,
) -> list[float]:
    """AM DSB-SC modulation: s[n] = m[n] · cos(2π f_c n / f_s).

    Parameters
    ----------
    message: Baseband message samples.
    fc:      Carrier frequency [Hz].
    fs:      Sampling frequency [Hz].

    Returns
    -------
    list[float]: Modulated signal samples.
    """
    _validate_freqs(fc, fs)
    ts = 1.0 / fs
    return [m * math.cos(2 * math.pi * fc * n * ts) for n, m in enumerate(message)]


def am_modulate_dsblc(
    message: Sequence[float],
    fc: float,
    fs: float,
    carrier_amplitude: float = 1.0,
    modulation_index: float = 1.0,
) -> list[float]:
    """AM DSB-LC modulation: s[n] = A_c [1 + k_a m[n]] cos(2π f_c n / f_s).

    Parameters
    ----------
    message:           Baseband message samples (should be normalised to [-1, 1]).
    fc:                Carrier frequency [Hz].
    fs:                Sampling frequency [Hz].
    carrier_amplitude: A_c — peak carrier amplitude.
    modulation_index:  k_a — modulation index (0 < k_a ≤ 1 for no over-modulation).

    Returns
    -------
    list[float]: Modulated signal samples.
    """
    _validate_freqs(fc, fs)
    ts = 1.0 / fs
    return [
        carrier_amplitude * (1.0 + modulation_index * m) * math.cos(2 * math.pi * fc * n * ts)
        for n, m in enumerate(message)
    ]


def am_demodulate(
    signal: Sequence[float],
    fc: float,
    fs: float,
    lp_cutoff: float | None = None,
) -> list[float]:
    """AM envelope demodulation (full-wave rectifier + 1st-order IIR LPF).

    Parameters
    ----------
    signal:    Received AM signal.
    fc:        Carrier frequency [Hz] (used to set default LP cutoff).
    fs:        Sampling frequency [Hz].
    lp_cutoff: Low-pass filter cutoff [Hz].  Defaults to fc / 10.

    Returns
    -------
    list[float]: Recovered envelope (≈ message).
    """
    _validate_freqs(fc, fs)
    cutoff = lp_cutoff if lp_cutoff is not None else fc / 10.0
    alpha = _iir_alpha(cutoff, fs)

    rectified = [abs(s) for s in signal]
    return _iir_lowpass(rectified, alpha)


# ---------------------------------------------------------------------------
# FM Modulation / Demodulation
# ---------------------------------------------------------------------------

def fm_modulate(
    message: Sequence[float],
    fc: float,
    fs: float,
    kf: float = 75e3,
    carrier_amplitude: float = 1.0,
) -> list[float]:
    """FM modulation using cumulative phase integration.

    Parameters
    ----------
    message:           Baseband message samples.
    fc:                Carrier frequency [Hz].
    fs:                Sampling frequency [Hz].
    kf:                Frequency deviation constant [Hz per unit of message].
    carrier_amplitude: A_c.

    Returns
    -------
    list[float]: FM modulated signal.
    """
    _validate_freqs(fc, fs)
    ts = 1.0 / fs
    phase = 0.0
    integral = 0.0
    result: list[float] = []
    for n, m in enumerate(message):
        integral += m * ts
        phase = 2 * math.pi * fc * n * ts + 2 * math.pi * kf * integral
        result.append(carrier_amplitude * math.cos(phase))
    return result


def fm_demodulate(
    signal: Sequence[float],
    fc: float,
    fs: float,
    kf: float = 75e3,
    lp_cutoff: float | None = None,
) -> list[float]:
    """FM demodulation via instantaneous frequency estimation (zero-crossing
    differentiator approximation).

    Uses the discrete differential: Δφ[n] ≈ arcsin(s[n]·c[n-1] − s[n-1]·c[n])
    where c[n] = cos(2π f_c n / f_s) is the local carrier reference.

    Parameters
    ----------
    signal:    Received FM signal.
    fc:        Carrier frequency [Hz].
    fs:        Sampling frequency [Hz].
    kf:        Frequency deviation constant [Hz per unit of message].
    lp_cutoff: Low-pass filter cutoff [Hz].  Defaults to fc / 20.

    Returns
    -------
    list[float]: Recovered message signal.
    """
    _validate_freqs(fc, fs)
    cutoff = lp_cutoff if lp_cutoff is not None else fc / 20.0
    alpha = _iir_alpha(cutoff, fs)
    ts = 1.0 / fs
    n = len(signal)
    demod: list[float] = [0.0]
    for i in range(1, n):
        c_prev = math.cos(2 * math.pi * fc * (i - 1) * ts)
        c_curr = math.cos(2 * math.pi * fc * i * ts)
        s_prev = math.sin(2 * math.pi * fc * (i - 1) * ts)
        s_curr = math.sin(2 * math.pi * fc * i * ts)
        cross = signal[i] * c_prev - signal[i - 1] * c_curr
        cross = max(-1.0, min(1.0, cross))  # clamp for asin domain
        delta_phase = math.asin(cross)
        inst_freq = delta_phase / (2 * math.pi * ts) - fc
        demod.append(inst_freq / kf)
    return _iir_lowpass(demod, alpha)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _validate_freqs(fc: float, fs: float) -> None:
    if fc <= 0 or fs <= 0:
        raise ValueError("Frequencies fc and fs must be positive.")
    if fc >= fs / 2:
        raise ValueError(f"Carrier frequency {fc} Hz violates Nyquist for fs={fs} Hz.")


def _iir_alpha(cutoff: float, fs: float) -> float:
    """Compute IIR first-order low-pass coefficient α = RC/(RC+Ts)."""
    rc = 1.0 / (2 * math.pi * cutoff)
    ts = 1.0 / fs
    return rc / (rc + ts)


def _iir_lowpass(x: list[float], alpha: float) -> list[float]:
    """Apply a first-order IIR low-pass filter: y[n] = α·y[n-1] + (1-α)·x[n]."""
    if not x:
        return []
    y = [0.0] * len(x)
    y[0] = (1 - alpha) * x[0]
    for n in range(1, len(x)):
        y[n] = alpha * y[n - 1] + (1 - alpha) * x[n]
    return y
