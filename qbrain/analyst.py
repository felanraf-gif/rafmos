import json

class MemoryAnalyst:
    def __init__(self, path="ai_gridworld/memories.json"):
        self.path = path
        self.memories = []

        with open(self.path, "r") as f:
            self.memories = json.load(f)

    def success_rate(self):
        return len(self.memories)

    def best_runs(self, n=5):
        return sorted(self.memories, key=lambda m: m["steps"])[:n]

    def worst_runs(self, n=5):
        return sorted(self.memories, key=lambda m: m["steps"], reverse=True)[:n]

    def trend(self):
        steps = [m["steps"] for m in self.memories]
        if len(steps) < 2:
            return 0
        return steps[-1] - steps[0]
