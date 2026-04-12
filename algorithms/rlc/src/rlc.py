# ALGO-META
# name: rlc
# version: 1.0.0
# category: signal-processing / analogue filters
# math: 2nd-order RLC filter transfer function H(s) + bilinear-transform IIR
# inputs: signal samples (list[float]), R, L, C, fs
# outputs: filtered signal (list[float])
# variants: low-pass, high-pass, band-pass
"""
RLC Analogue Filter — Low-Pass, High-Pass, Band-Pass.
Discrete equivalents via the Bilinear Transform (Tustin's method).

Version: 1.0.0

Analogue transfer functions
---------------------------

Series RLC circuit, output across:

  Capacitor (Low-Pass):
      H_LP(s) = (1/LC) / [s² + (R/L)s + 1/LC]

  Inductor (High-Pass):
      H_HP(s) = s² / [s² + (R/L)s + 1/LC]

  Resistor (Band-Pass):
      H_BP(s) = (R/L)s / [s² + (R/L)s + 1/LC]

Standard 2nd-order prototype:
    ω₀ = 1/√(LC)   (natural/resonant frequency, rad/s)
    Q  = ω₀ L / R  (quality factor)
    BW = R/L        (bandwidth, rad/s)

Bilinear Transform: s ← (2/Ts)(z-1)/(z+1)

Resulting IIR difference equation (Direct Form II):
    w[n] = x[n] - a1·w[n-1] - a2·w[n-2]
    y[n] = b0·w[n] + b1·w[n-1] + b2·w[n-2]
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Sequence


class FilterType(str, Enum):
    LOW_PASS = "low_pass"
    HIGH_PASS = "high_pass"
    BAND_PASS = "band_pass"


class RLCFilter:
    """Discrete 2nd-order RLC filter via the Bilinear Transform.

    Parameters
    ----------
    R:           Resistance [Ω].
    L:           Inductance [H].
    C:           Capacitance [F].
    fs:          Sampling frequency [Hz].
    filter_type: One of FilterType.LOW_PASS, HIGH_PASS, BAND_PASS.
    """

    def __init__(
        self,
        R: float,
        L: float,
        C: float,
        fs: float,
        filter_type: FilterType = FilterType.LOW_PASS,
    ) -> None:
        if R <= 0 or L <= 0 or C <= 0:
            raise ValueError("R, L, and C must all be positive.")
        if fs <= 0:
            raise ValueError("Sampling frequency fs must be positive.")

        self.R = R
        self.L = L
        self.C = C
        self.fs = fs
        self.filter_type = FilterType(filter_type)

        # Analogue prototype parameters
        self.omega0 = 1.0 / math.sqrt(L * C)   # rad/s
        self.Q = self.omega0 * L / R
        self.bw = R / L  # bandwidth rad/s

        # Compute IIR coefficients via bilinear transform
        self._b, self._a = self._design_coefficients()

        # Filter state (Direct Form II transposed)
        self._w1: float = 0.0
        self._w2: float = 0.0

    # ------------------------------------------------------------------
    def reset(self) -> None:
        """Reset filter state (zero initial conditions)."""
        self._w1 = 0.0
        self._w2 = 0.0

    # ------------------------------------------------------------------
    def process(self, signal: Sequence[float]) -> list[float]:
        """Filter *signal* sample by sample.

        Parameters
        ----------
        signal: Input samples.

        Returns
        -------
        list[float]: Filtered output samples.
        """
        b0, b1, b2 = self._b
        a1, a2 = self._a
        output: list[float] = []
        w1, w2 = self._w1, self._w2
        for x in signal:
            w0 = x - a1 * w1 - a2 * w2
            y = b0 * w0 + b1 * w1 + b2 * w2
            w2, w1 = w1, w0
            output.append(y)
        self._w1, self._w2 = w1, w2
        return output

    # ------------------------------------------------------------------
    @property
    def resonant_frequency_hz(self) -> float:
        """Resonant frequency f₀ = ω₀ / (2π) in Hz."""
        return self.omega0 / (2 * math.pi)

    # ------------------------------------------------------------------
    def _design_coefficients(self) -> tuple[tuple[float, float, float], tuple[float, float]]:
        """Derive (b0, b1, b2), (a1, a2) via bilinear transform of H(s)."""
        ts = 1.0 / self.fs
        k = 2.0 / ts  # pre-warp factor (k = 2*fs)

        # Analogue coefficients: H(s) = (num2 s² + num1 s + num0) / (s² + α s + β)
        alpha = self.R / self.L    # = ω₀ / Q = BW
        beta = self.omega0 ** 2   # = 1 / (LC)

        ft = self.filter_type
        if ft == FilterType.LOW_PASS:
            num2, num1, num0 = 0.0, 0.0, beta
        elif ft == FilterType.HIGH_PASS:
            num2, num1, num0 = 1.0, 0.0, 0.0
        elif ft == FilterType.BAND_PASS:
            num2, num1, num0 = 0.0, alpha, 0.0
        else:
            raise ValueError(f"Unknown filter type: {ft}")

        # Bilinear substitution s → k(z-1)/(z+1):
        # Denominator polynomial in z after substitution and normalization
        d0 = k**2 + alpha * k + beta
        d1 = -2 * k**2 + 2 * beta
        d2 = k**2 - alpha * k + beta

        n0 = num2 * k**2 + num1 * k + num0
        n1 = -2 * num2 * k**2 + 2 * num0
        n2 = num2 * k**2 - num1 * k + num0

        b = (n0 / d0, n1 / d0, n2 / d0)
        a = (d1 / d0, d2 / d0)
        return b, a


# ---------------------------------------------------------------------------
# Convenience constructors
# ---------------------------------------------------------------------------

def rlc_lowpass(R: float, L: float, C: float, fs: float) -> RLCFilter:
    """Return a low-pass RLC filter."""
    return RLCFilter(R, L, C, fs, FilterType.LOW_PASS)


def rlc_highpass(R: float, L: float, C: float, fs: float) -> RLCFilter:
    """Return a high-pass RLC filter."""
    return RLCFilter(R, L, C, fs, FilterType.HIGH_PASS)


def rlc_bandpass(R: float, L: float, C: float, fs: float) -> RLCFilter:
    """Return a band-pass RLC filter."""
    return RLCFilter(R, L, C, fs, FilterType.BAND_PASS)
