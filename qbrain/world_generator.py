    from validator.taskgraph_validator import validate_project_world

    def generate_world(self, context=None):
        prompt = self._build_prompt(context)

        try:
            result = subprocess.run(
                ["ollama", "run", self.model],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=90
            )

            if result.returncode != 0:
                raise RuntimeError(result.stderr)

            raw = result.stdout.strip()
            data = self._parse_llm_output(raw)

            ok, msg = validate_project_world(data)
            if not ok:
                raise ValueError(f"World rejected: {msg}")

            return data

        except Exception as e:
            print("⚠ World generation failed:", e)
            return self._fallback_world()