"""Tests for the discrete PID controller (v1.0.0)."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from pid import PIDController


def test_proportional_only():
    """Pure P: output == Kp * error."""
    pid = PIDController(kp=2.0, ki=0.0, kd=0.0, dt=0.1)
    out = pid.update(setpoint=10.0, measurement=7.0)
    assert out == pytest.approx(6.0)


def test_integral_accumulation():
    """I term accumulates over multiple steps."""
    pid = PIDController(kp=0.0, ki=1.0, kd=0.0, dt=0.1)
    pid.update(setpoint=1.0, measurement=0.0)  # integral = 0.1
    out = pid.update(setpoint=1.0, measurement=0.0)  # integral = 0.2
    assert out == pytest.approx(0.2)


def test_derivative_kick():
    """D term reacts to error change."""
    pid = PIDController(kp=0.0, ki=0.0, kd=1.0, dt=0.1)
    pid.update(setpoint=1.0, measurement=0.0)  # prev_error = 1
    out = pid.update(setpoint=1.0, measurement=0.5)  # error = 0.5, de = -0.5
    assert out == pytest.approx(-0.5 / 0.1)


def test_output_clamping():
    """Output must not exceed [out_min, out_max]."""
    pid = PIDController(kp=100.0, ki=0.0, kd=0.0, dt=0.1, out_min=-5.0, out_max=5.0)
    out = pid.update(setpoint=10.0, measurement=0.0)
    assert out == pytest.approx(5.0)


def test_anti_windup():
    """Integral must freeze when output is saturated."""
    pid = PIDController(kp=0.0, ki=1.0, kd=0.0, dt=1.0, out_min=-1.0, out_max=1.0)
    for _ in range(100):
        pid.update(setpoint=5.0, measurement=0.0)
    # Integral must be bounded, not grow to 500
    assert abs(pid._integral) <= 2.0


def test_reset():
    """reset() must clear integral and previous error."""
    pid = PIDController(kp=1.0, ki=1.0, kd=1.0, dt=0.1)
    pid.update(setpoint=5.0, measurement=0.0)
    pid.reset()
    assert pid._integral == 0.0
    assert pid._prev_error == 0.0


def test_invalid_dt():
    """Non-positive dt must raise ValueError."""
    with pytest.raises(ValueError):
        PIDController(kp=1.0, ki=0.0, kd=0.0, dt=0.0)


def test_convergence_step_response():
    """PI controller converges to setpoint on an integrating plant."""
    pid = PIDController(kp=1.0, ki=0.5, kd=0.0, dt=0.01, out_min=-10.0, out_max=10.0)
    plant = 0.0
    for _ in range(1000):
        u = pid.update(setpoint=1.0, measurement=plant)
        plant += u * 0.01  # first-order integrating plant: dy = u*dt
    assert abs(plant - 1.0) < 0.05
