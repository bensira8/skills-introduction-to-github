# ALGO-META
# name: fft
# version: 1.0.0
# category: signal-processing
# math: Cooley-Tukey radix-2 DIT FFT (recursive)
# inputs: x (sequence of complex/real numbers, length must be power of 2)
# outputs: X (complex spectrum, same length)
# complexity: O(N log N)
"""
Fast Fourier Transform — Cooley-Tukey radix-2 Decimation-In-Time (DIT).

Version: 1.0.0

Mathematical definition
-----------------------
The Discrete Fourier Transform (DFT) of a length-N sequence x[n] is:

    X[k] = sum_{n=0}^{N-1} x[n] * exp(-j * 2*pi * k * n / N),   k = 0..N-1

The Cooley-Tukey radix-2 DIT algorithm exploits the twiddle-factor symmetry to
reduce complexity from O(N²) to O(N log₂ N) by recursively splitting the DFT into
two half-length DFTs of the even and odd indexed samples:

    X[k]     = E[k] + W_N^k * O[k]
    X[k+N/2] = E[k] - W_N^k * O[k]

where W_N = exp(-j * 2*pi / N) and E, O are the DFTs of the even/odd sub-sequences.

Inverse FFT (IFFT) is implemented via conjugation:
    IFFT{X} = conj(FFT{conj(X)}) / N
"""

from __future__ import annotations

import cmath
import math
from typing import Sequence


def fft(x: Sequence[complex]) -> list[complex]:
    """Compute the FFT of *x* using the Cooley-Tukey radix-2 DIT algorithm.

    Parameters
    ----------
    x:
        Input sequence.  Length **must** be a power of two.

    Returns
    -------
    list[complex]:
        Complex spectrum X[k], k = 0 … N-1.

    Raises
    ------
    ValueError:
        If ``len(x)`` is not a power of two or is zero.
    """
    n = len(x)
    if n == 0:
        raise ValueError("Input sequence must not be empty.")
    if n & (n - 1):
        raise ValueError(f"Input length must be a power of 2, got {n}.")

    if n == 1:
        return [complex(x[0])]

    even = fft([x[k] for k in range(0, n, 2)])
    odd = fft([x[k] for k in range(1, n, 2)])

    half = n >> 1
    twiddle = [cmath.exp(-2j * math.pi * k / n) * odd[k] for k in range(half)]

    return [even[k] + twiddle[k] for k in range(half)] + [
        even[k] - twiddle[k] for k in range(half)
    ]


def ifft(X: Sequence[complex]) -> list[complex]:
    """Compute the Inverse FFT via the conjugation identity.

    Parameters
    ----------
    X:
        Complex spectrum.  Length **must** be a power of two.

    Returns
    -------
    list[complex]:
        Reconstructed time-domain sequence x[n].
    """
    n = len(X)
    conjugated = [c.conjugate() for c in X]
    forward = fft(conjugated)
    return [v.conjugate() / n for v in forward]


def magnitude_spectrum(x: Sequence[complex]) -> list[float]:
    """Return the single-sided magnitude spectrum (dB) of *x*.

    Only the first N/2 + 1 bins are returned (positive frequencies).
    """
    X = fft(list(x))
    n = len(X)
    half = n // 2 + 1
    return [abs(X[k]) for k in range(half)]
