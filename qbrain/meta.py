import numpy as np
import json
import os


class MetaBrain:
    def __init__(self, window=10):
        self.window = window
        self.history = []
        self.ema = None
        self.world_stats = {}
        self.consecutive_same = 0
        self.last_decision = None
        
        self.thresholds = {
            "solved_mean": 0.85,
            "solved_stability": 0.05,
            "impossible_mean": 0.15,
            "stuck_mean": 0.25,
            "stuck_trend": 0.1,
            "degradation_trend": -0.15,
        }


    def record(self, efficiency, world_type=None):
        self.history.append(efficiency)
        if len(self.history) > self.window:
            self.history.pop(0)
        
        if world_type:
            if world_type not in self.world_stats:
                self.world_stats[world_type] = []
            self.world_stats[world_type].append(efficiency)
            if len(self.world_stats[world_type]) > self.window:
                self.world_stats[world_type].pop(0)
        
        if self.ema is None:
            self.ema = efficiency
        else:
            self.ema = 0.3 * efficiency + 0.7 * self.ema


    def stats(self):
        if len(self.history) < 2:
            return None

        arr = np.array(self.history)
        mean = float(np.mean(arr))
        std = float(np.std(arr))
        trend = self.history[-1] - self.history[0]
        
        return {
            "mean": mean,
            "std": std,
            "trend": trend,
            "ema": self.ema,
        }


    def world_stats_for(self, world_type):
        if world_type not in self.world_stats or len(self.world_stats[world_type]) < 2:
            return None
        
        arr = np.array(self.world_stats[world_type])
        return {
            "mean": float(np.mean(arr)),
            "trend": arr[-1] - arr[0],
            "count": len(arr),
        }


    def decide(self, world_has_solution=True, world_type=None):
        s = self.stats()
        if s is None:
            return "CONTINUE"
        
        mean = s["mean"]
        trend = s["trend"]
        
        if self.last_decision == self._decide(mean, trend, world_has_solution):
            self.consecutive_same += 1
        else:
            self.consecutive_same = 0
        
        decision = self._decide(mean, trend, world_has_solution)
        self.last_decision = decision
        
        if self.consecutive_same > 5 and decision in ["CONTINUE", "CHANGE_WORLD"]:
            return "ADAPT_STRATEGY"
        
        return decision


    def _decide(self, mean, trend, world_has_solution):
        t = self.thresholds
        
        if mean > t["solved_mean"] and abs(trend) < t["solved_stability"]:
            return "SOLVED"
        
        if not world_has_solution:
            return "IMPOSSIBLE"
        
        if world_has_solution and mean < t["stuck_mean"] and abs(trend) < t["stuck_trend"]:
            return "CHANGE_WORLD"
        
        if trend < t["degradation_trend"]:
            return "CHANGE_WORLD"
        
        if mean > 0.7 and trend > 0.1:
            return "INCREASE_DIFFICULTY"
        
        return "CONTINUE"


    def adapt_thresholds(self, performance_over_time):
        if performance_over_time > 0:
            self.thresholds["solved_mean"] = min(0.95, self.thresholds["solved_mean"] + 0.02)
        else:
            self.thresholds["solved_mean"] = max(0.7, self.thresholds["solved_mean"] - 0.02)


    def get_thresholds(self):
        return self.thresholds.copy()


    def save(self, path=None):
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "meta.json")
        
        data = {
            "history": self.history,
            "ema": self.ema,
            "world_stats": {k: v for k, v in self.world_stats.items()},
            "thresholds": self.thresholds,
        }
        with open(path, "w") as f:
            json.dump(data, f)


    def load(self, path=None):
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "meta.json")
        
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                self.history = data.get("history", [])
                self.ema = data.get("ema")
                self.world_stats = data.get("world_stats", {})
                self.thresholds = data.get("thresholds", self.thresholds)
