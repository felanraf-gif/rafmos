import numpy as np


class ReflectionEngine:
    def __init__(self, threshold=5):
        self.threshold = threshold
        self.reflection_count = 0


    def reflect(self, brain, memory, env):
        self.reflection_count += 1
        
        world_type = env.world_type
        runs = memory.by_world(world_type)
        
        if len(runs) < self.threshold:
            return False

        best = memory.best(world_type)
        worst = memory.worst(world_type)

        if best and worst:
            brain.bias_towards(best["path"])
            brain.penalize(worst["path"])
            return True
        
        return False


    def get_insight(self, memory, env):
        world_type = env.world_type
        stats = memory.stats(world_type)
        best = memory.best(world_type)
        worst = memory.worst(world_type)
        
        return {
            "world_type": world_type,
            "total_runs": stats.get("count", 0),
            "avg_efficiency": stats.get("avg_efficiency", 0),
            "best_steps": best["steps"] if best else None,
            "worst_steps": worst["steps"] if worst else None,
        }
