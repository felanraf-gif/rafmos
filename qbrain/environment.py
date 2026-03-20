import random
from collections import deque

class GridWorldEnvironment:
    def __init__(self, world_type="corridor", size=7):
        self.size = size
        self.world_type = world_type
        self.has_solution = True
        self.walls = []
        self.generate_world()

    def generate_world(self):
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.walls = []

        self.start = (0, 0)
        self.goal = (self.size - 1, self.size - 1)

        if self.world_type == "corridor":
            for i in range(self.size):
                self.grid[i][0] = 0
            for j in range(self.size):
                self.grid[self.size - 1][j] = 0

        elif self.world_type == "maze":
            for i in range(self.size):
                for j in range(self.size):
                    if random.random() < 0.3:
                        self.grid[i][j] = 1
                        self.walls.append((i, j))

        elif self.world_type == "trap":
            for i in range(self.size):
                for j in range(self.size):
                    if random.random() < 0.4:
                        self.grid[i][j] = 1
                        self.walls.append((i, j))

        elif self.world_type == "open":
            pass

        self.grid[self.start[0]][self.start[1]] = 0
        self.grid[self.goal[0]][self.goal[1]] = 0

        # ensure at least one valid path
        self.ensure_path()

    def ensure_path(self):
        x, y = self.start
        while (x, y) != self.goal:
            if random.random() < 0.5:
                x = min(self.size - 1, x + 1)
            else:
                y = min(self.size - 1, y + 1)
            self.grid[x][y] = 0

    def reset(self):
        self.pos = self.start
        return self.pos

    def step(self, action):
        x, y = self.pos

        if action == 0: x -= 1
        if action == 1: x += 1
        if action == 2: y -= 1
        if action == 3: y += 1

        x = max(0, min(self.size - 1, x))
        y = max(0, min(self.size - 1, y))

        if self.grid[x][y] == 1:
            return self.pos, -1, False

        self.pos = (x, y)

        if self.pos == self.goal:
            return self.pos, 10, True

        return self.pos, -0.01, False

    # 🔥 THIS IS WHAT META BRAIN NEEDS
    def shortest_path_length(self):
        visited = set()
        q = deque()
        q.append((self.start, 0))
        visited.add(self.start)

        while q:
            (x, y), d = q.popleft()
            if (x, y) == self.goal:
                return d

            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    if self.grid[nx][ny] == 0 and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        q.append(((nx, ny), d + 1))

        return None
