class WorldMemory:
    def __init__(self):
        self.solved = {}
        self.failed = set()

    # ------------------------------
    # When world is solved
    # ------------------------------
    def mark_solved(self, world_type, score):
        self.solved[world_type] = score

    # ------------------------------
    # When world is impossible
    # ------------------------------
    def mark_failed(self, world_type):
        self.failed.add(world_type)

    # ------------------------------
    # Can we use this world?
    # ------------------------------
    def is_allowed(self, world_type):
        return world_type not in self.failed

    # ------------------------------
    # Pick next world
    # ------------------------------
    def choose_next(self, candidates):
        allowed = [w for w in candidates if w not in self.failed]
        if not allowed:
            return None
        return allowed[0]

    # ------------------------------
    # For LLM prompt
    # ------------------------------
    def summary(self):
        return f"SOLVED={self.solved}, FAILED={list(self.failed)}"
