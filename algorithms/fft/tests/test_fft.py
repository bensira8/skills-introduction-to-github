"""Tests for the Cooley-Tukey radix-2 DIT FFT (v1.0.0)."""

import sys
import os
import cmath
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from fft import fft, ifft, magnitude_spectrum


def _allclose(a: list, b: list, tol: float = 1e-9) -> bool:
    return all(abs(x - y) < tol for x, y in zip(a, b))


def test_single_element():
    assert fft([3 + 0j]) == [3 + 0j]


def test_dc_only():
    """Constant signal has energy only in bin 0."""
    N = 8
    x = [1.0 + 0j] * N
    X = fft(x)
    assert abs(X[0] - N) < 1e-9
    for k in range(1, N):
        assert abs(X[k]) < 1e-9


def test_single_frequency():
    """Pure sinusoid at frequency k0 has energy only in bins k0 and N-k0."""
    N = 8
    k0 = 2
    x = [cmath.exp(2j * math.pi * k0 * n / N) for n in range(N)]
    X = fft(x)
    assert abs(X[k0] - N) < 1e-9
    for k in range(N):
        if k != k0:
            assert abs(X[k]) < 1e-9


def test_linearity():
    """FFT must be linear: FFT(a*x + b*y) == a*FFT(x) + b*FFT(y)."""
    N = 4
    x = [1, 2, 3, 4]
    y = [4, 3, 2, 1]
    a, b = 2.0, 3.0
    combined = [a * xi + b * yi for xi, yi in zip(x, y)]
    lhs = fft(combined)
    rhs = [a * xi + b * yi for xi, yi in zip(fft(x), fft(y))]
    assert _allclose(lhs, rhs)


def test_parseval_theorem():
    """Sum of |x[n]|² == (1/N) * Sum of |X[k]|²."""
    x = [1, 2, 3, 4, 0, 0, 0, 0]
    X = fft(x)
    energy_time = sum(abs(v) ** 2 for v in x)
    energy_freq = sum(abs(v) ** 2 for v in X) / len(X)
    assert abs(energy_time - energy_freq) < 1e-9


def test_ifft_roundtrip():
    """IFFT(FFT(x)) must recover x."""
    x = [1 + 2j, 3 - 1j, -1 + 0j, 0 + 4j, 2 + 0j, 1 - 1j, 0 + 0j, -2 + 1j]
    recovered = ifft(fft(x))
    assert _allclose(x, recovered)


def test_non_power_of_two_raises():
    with pytest.raises(ValueError):
        fft([1, 2, 3])


def test_empty_raises():
    with pytest.raises(ValueError):
        fft([])


def test_magnitude_spectrum_length():
    N = 8
    x = [float(n) for n in range(N)]
    mag = magnitude_spectrum(x)
    assert len(mag) == N // 2 + 1
