class WorldTraumaMemory:
    def __init__(self):
        self.traumas = {}   # world_signature -> trauma_level

    def signature(self, env):
        # opis świata: wielkość + liczba ścian
        return f"{env.size}_{len(env.walls)}"

    def record_failure(self, env):
        sig = self.signature(env)
        self.traumas[sig] = self.traumas.get(sig, 0) + 1

    def is_traumatized(self, env, threshold=3):
        sig = self.signature(env)
        return self.traumas.get(sig, 0) >= threshold

    def filter_worlds(self, worlds, env_factory):
        # usuwa światy podobne do tych, które są traumatyczne
        safe = []
        for w in worlds:
            env = env_factory(w)
            if not self.is_traumatized(env):
                safe.append(w)
        return safe
