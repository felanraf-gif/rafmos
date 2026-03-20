class ProjectWorld:
    def __init__(self):
        self.goals = {
            "llm_connected": True,     # już masz
            "agent_can_talk": False,
            "worlds_generated": False,
            "memory_persistent": False,
        }

        self.history = []
        self.failures = []

    def is_solved(self):
        return all(self.goals.values())

    def state_text(self):
        return "\n".join(f"{k} = {v}" for k, v in self.goals.items())

    def record_action(self, action, result):
        self.history.append((action, result))
        if not result:
            self.failures.append(action)
