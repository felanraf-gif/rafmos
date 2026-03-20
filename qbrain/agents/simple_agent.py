```python
class SimpleAgent:
    def __init__(self, start):
        self.position = start

    def move(self, grid):
        next_positions = [(self.position[0] + dx, self.position[1] + dy) for (dx, dy) in [(-1, 0), (1, 0), (0, -1), (0, 1)] if 0 <= self.position[0] + dx < len(grid) and 0 <= self.position[1] + dy < len(grid[0]) and grid[self.position[0] + dx][self.position[1] + dy] != "#"]
        if next_positions:
            self.position = next_positions[0]
        else:
            print("No valid moves found.")
```