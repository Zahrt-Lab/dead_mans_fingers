import time

class UVConvergenceMonitor:
    """
    Monitors a UV detector for:
      1. A spike (all wavelengths >= spike_level)
      2. Convergence (signal change < threshold for convergence_time seconds)
    Call update(values) repeatedly.
    Returns True ONLY when convergence is stable for required duration.
    """

    def __init__(self,
                 spike_level=0.2,
                 threshold=0.001,
                 convergence_time=5 * 60):
        self.spike_level = spike_level
        self.threshold = threshold
        self.convergence_time = convergence_time

        # Internal state
        self.previous = None
        self.spike_seen = False
        self.converged_start = None
        self._done = False

    def _spike_detected(self, values):
        return all(v >= self.spike_level for v in values)

    def _has_converged(self, current, previous):
        diffs = [abs(c - p) for c, p in zip(current, previous)]
        return max(diffs) < self.threshold

    def update(self, values):
        """
        Call this once per detector reading.
        `values` should be a list/array of absorbances (all wavelengths).
        
        Returns:
            True  -> convergence finished, safe to stop
            False -> still waiting
        """

        # If already finished, keep returning True
        if self._done:
            return True

        # First reading case
        if self.previous is None:
            self.previous = values
            return False

        # 1) Wait for spike
        if not self.spike_seen:
            if self._spike_detected(values):
                self.spike_seen = True
                self.converged_start = None  # reset timer
            self.previous = values
            return False

        # 2) After spike, check for convergence
        if self._has_converged(values, self.previous):
            if self.converged_start is None:
                self.converged_start = time.time()
            else:
                if time.time() - self.converged_start >= self.convergence_time:
                    # Fully converged for required duration
                    self._done = True
                    return True
        else:
            # Lost convergence stability → reset timer
            self.converged_start = None

        self.previous = values
        return False
