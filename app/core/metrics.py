import time
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class MetricsTracker:
    total_tokens: int = 0
    start_time: float = field(default_factory=time.time)
    last_time: float = field(default_factory=time.time) 
    step_times: List[Dict[str, Any]] = field(default_factory=list)

    def log_step(self, step_name: str, tokens: int = 0):
        """Logs the timing and token count of a specific workflow step."""
        current = time.time()
        step_duration = current - self.last_time
        self.last_time = current
        self.total_tokens += tokens
        
        self.step_times.append({
            "step": step_name, 
            "duration": round(step_duration, 2),
            "tokens": tokens,
            "cumulative": round(current - self.start_time, 2)
        })

    def get_stats(self):
        return {
            "tokens": self.total_tokens,
            "duration": round(time.time() - self.start_time, 2),
            "steps": self.step_times
        }