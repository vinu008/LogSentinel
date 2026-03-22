import time
from collections import defaultdict, deque

WINDOW_SIZE = int(__import__('os').getenv("WINDOW_SIZE", "60"))   # seconds
ZSCORE_THRESHOLD = float(__import__('os').getenv("ZSCORE_THRESHOLD", "2.0"))
MIN_SAMPLES = 10  # don't flag until we have enough history

class AnomalyDetector:
    def __init__(self):
        # per service: deque of (timestamp, is_error) tuples
        self.windows = defaultdict(deque)

    def record(self, service: str, level: str) -> dict | None:
        now = time.time()
        window = self.windows[service]

        # add new event
        window.append((now, level == "ERROR" or level == "FATAL"))

        # evict events older than WINDOW_SIZE seconds
        while window and now - window[0][0] > WINDOW_SIZE:
            window.popleft()

        if len(window) < MIN_SAMPLES:
            return None

        # compute error rate over window
        total = len(window)
        errors = sum(1 for _, is_err in window if is_err)
        error_rate = errors / total

        # compute rolling mean and std using the last N snapshots
        # simplified: use current error_rate vs historical snapshots
        rates = self._historical_rates(service)
        if len(rates) < MIN_SAMPLES:
            return None

        mean = sum(rates) / len(rates)
        variance = sum((r - mean) ** 2 for r in rates) / len(rates)
        std = variance ** 0.5

        if std == 0:
            return None

        zscore = abs(error_rate - mean) / std
        if zscore > ZSCORE_THRESHOLD:
            return {
                "service": service,
                "zscore": round(zscore, 3),
                "error_rate": round(error_rate, 3),
                "mean": round(mean, 3),
                "window_size": total,
                "detected_at": now,
            }
        return None

    def _historical_rates(self, service: str):
        # bucket the window into 5-second chunks and return error rate per chunk
        window = self.windows[service]
        if not window:
            return []
        now = time.time()
        buckets = defaultdict(lambda: [0, 0])  # bucket_idx -> [total, errors]
        for ts, is_err in window:
            bucket = int((now - ts) // 5)
            buckets[bucket][0] += 1
            buckets[bucket][1] += int(is_err)
        return [e / t for t, e in buckets.values() if t > 0]
