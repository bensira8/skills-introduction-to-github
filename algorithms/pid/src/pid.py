# ALGO-META
# name: pid
# version: 1.0.0
# category: control
# math: discrete position-form PID
# inputs: setpoint (float), measurement (float), dt (float)
# outputs: control_output (float)
# state: integral_accumulator, previous_error
"""
Discrete PID Controller — position form.

Version: 1.0.0

Mathematical definition
-----------------------
Given error  e[k] = setpoint - measurement,

    u[k] = Kp * e[k]
         + Ki * dt * sum_{i=0}^{k} e[i]          (integral, trapezoidal)
         + Kd / dt * (e[k] - e[k-1])              (derivative, backward diff)

with optional symmetric output clamp [out_min, out_max] and
anti-windup: integral accumulation is frozen when the output is saturated.
"""

from __future__ import annotations


class PIDController:
    """Discrete PID controller (position form, anti-windup, output clamp).

    Parameters
    ----------
    kp:      Proportional gain.
    ki:      Integral gain.
    kd:      Derivative gain.
    dt:      Sampling period [s].
    out_min: Lower saturation limit (default -inf).
    out_max: Upper saturation limit (default +inf).
    """

    def __init__(
        self,
        kp: float,
        ki: float,
        kd: float,
        dt: float,
        out_min: float = float("-inf"),
        out_max: float = float("inf"),
    ) -> None:
        if dt <= 0:
            raise ValueError("Sampling period dt must be positive.")
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.dt = dt
        self.out_min = out_min
        self.out_max = out_max
        self._integral: float = 0.0
        self._prev_error: float = 0.0

    # ------------------------------------------------------------------
    def reset(self) -> None:
        """Reset internal state (integral and previous error)."""
        self._integral = 0.0
        self._prev_error = 0.0

    # ------------------------------------------------------------------
    def update(self, setpoint: float, measurement: float) -> float:
        """Compute the next control output.

        Parameters
        ----------
        setpoint:    Desired target value.
        measurement: Current process variable.

        Returns
        -------
        float: Control output, clamped to [out_min, out_max].
        """
        error = setpoint - measurement

        proportional = self.kp * error
        derivative = self.kd * (error - self._prev_error) / self.dt
        self._prev_error = error

        # Anti-windup (clamping): only accumulate the integral if doing so would
        # NOT push the output further into saturation.
        new_integral = self._integral + error * self.dt
        prospective_raw = proportional + self.ki * new_integral + derivative
        at_upper = prospective_raw > self.out_max and error > 0
        at_lower = prospective_raw < self.out_min and error < 0
        if not (at_upper or at_lower):
            self._integral = new_integral

        raw = proportional + self.ki * self._integral + derivative
        return max(self.out_min, min(self.out_max, raw))
