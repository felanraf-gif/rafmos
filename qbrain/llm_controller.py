import json
import os
from openai import OpenAI

client = OpenAI()

class LLMController:
    def decide(self, report):
        prompt = f"""
You are the strategic brain of an autonomous RL agent.

Here is the current situation:
{json.dumps(report, indent=2)}

Decide what the agent should do next.

You must output JSON only, in this format:
{{
  "action": "CONTINUE | CHANGE_WORLD | BLACKLIST | SOLVED",
  "suggested_world": "corridor | maze | harder | trap | random",
  "new_epsilon": 0.0-1.0,
  "reason": "short explanation"
}}
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role":"user","content":prompt}],
            temperature=0.2
        )

        text = response.choices[0].message.content.strip()
        return json.loads(text)
