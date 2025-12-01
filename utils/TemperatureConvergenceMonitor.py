# temperature_monitor.py
import time

class TemperatureConvergenceMonitor:
    """
    Monitors an instrument temperature for convergence around a setpoint.
    
    Logic:
      - You set a target temperature (setpoint)
      - If current temperature is within `tolerance` degrees of setpoint,
        a timer starts.
      - If it stays within that band continuously for `convergence_time`
        seconds, update() returns True and stays True thereafter.
    
    Call update(current_temp) repeatedly.
    """

    def __init__(self,
                 setpoint,
                 tolerance=2.0,
                 convergence_time=5 * 60):
        """
        Args:
            setpoint (float): target temperature in °C
            tolerance (float): allowed deviation (±) from setpoint in °C
            convergence_time (float): required time in seconds within tolerance
        """
        self.setpoint = setpoint
        self.tolerance = tolerance
        self.convergence_time = convergence_time

        # Internal state
        self.converged_start = None
        self._done = False

    def _in_band(self, temp):
        """Return True if temp is within tolerance of setpoint."""
        return abs(temp - self.setpoint) <= self.tolerance

    def update(self, temp):
        """
        Call this once per temperature reading.

        Args:
            temp (float): current temperature in °C

        Returns:
            True  -> temperature has been in band for convergence_time
            False -> still waiting
        """

        # If we have already converged, keep returning True
        if self._done:
            return True

        now = time.time()

        if self._in_band(temp):
            # First time entering the convergence band
            if self.converged_start is None:
                self.converged_start = now
            else:
                # Check how long we've stayed in band
                if now - self.converged_start >= self.convergence_time:
                    self._done = True
                    return True
        else:
            # Left the band → reset timer
            self.converged_start = None

        return False
