import json
import os


class MemoryBank:
    def __init__(self, path=None):
        self.path = path or os.path.join(os.path.dirname(__file__), "memories.json")
        self.runs = []
        self.load()


    def store(self, env, steps, path, optimal):
        if optimal is None or steps <= 0:
            return

        self.runs.append({
            "world_type": env.world_type,
            "size": env.size,
            "steps": steps,
            "optimal": optimal,
            "efficiency": optimal / steps if steps > 0 else 0,
            "path": path[-20:] if len(path) > 20 else path,
        })
        
        self.save()


    def by_world(self, world_type):
        return [r for r in self.runs if r["world_type"] == world_type]


    def best(self, world_type=None, n=1):
        data = self.runs if world_type is None else self.by_world(world_type)
        if not data:
            return None
        sorted_data = sorted(data, key=lambda r: r["efficiency"], reverse=True)
        return sorted_data[:n] if n > 1 else sorted_data[0]


    def worst(self, world_type=None, n=1):
        data = self.runs if world_type is None else self.by_world(world_type)
        if not data:
            return None
        sorted_data = sorted(data, key=lambda r: r["efficiency"])
        return sorted_data[:n] if n > 1 else sorted_data[0]


    def stats(self, world_type=None):
        data = self.runs if world_type is None else self.by_world(world_type)
        if not data:
            return {"count": 0}
        
        efficiencies = [r["efficiency"] for r in data]
        return {
            "count": len(data),
            "avg_efficiency": sum(efficiencies) / len(efficiencies),
            "best_efficiency": max(efficiencies),
            "worst_efficiency": min(efficiencies),
        }


    def clear(self):
        self.runs.clear()
        self.save()


    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.runs, f)


    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                self.runs = json.load(f)
