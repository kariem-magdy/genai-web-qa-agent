import time
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class MetricsTracker:
    """
    Tracks 'Agent's Brain' metrics (Tokens & Time).
    """
    total_tokens: int = 0
    start_time: float = field(default_factory=time.time)
    # NEW: Tracks the completion time of the previous step to calculate deltas
    last_time: float = field(default_factory=time.time) 
    step_times: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        # Ensure last_time is synchronized with start_time upon creation
        self.last_time = self.start_time

    def add_tokens(self, count: int):
        """Updates total token consumption."""
        if count:
            self.total_tokens += count

    def log_step(self, step_name: str):
        """Logs the timing of a specific workflow step."""
        current = time.time()
        
        # Existing logic: Cumulative time from start
        cumulative = current - self.start_time
        
        # NEW LOGIC: Delta time (duration of just this specific step)
        step_duration = current - self.last_time
        self.last_time = current # Update last_time for the next step
        
        self.step_times.append({
            "step": step_name, 
            "timestamp": current,
            "cumulative_duration": round(cumulative, 2),
            "step_duration": round(step_duration, 2) # Saving the specific speed
        })

    def get_stats(self):
        """Returns formatted stats for the UI."""
        return {
            "tokens": self.total_tokens,
            "duration": round(time.time() - self.start_time, 2),
            "steps": self.step_times # Expose steps so UI can read them
        }