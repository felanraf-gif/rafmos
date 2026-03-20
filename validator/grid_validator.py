from collections import deque

def shortest_path_exists(grid, start, goal):
    """
    grid: 2D list, 0 = free, 1 = wall
    start, goal: (x, y)
    """
    rows, cols = len(grid), len(grid[0])
    visited = set()
    queue = deque([start])

    while queue:
        x, y = queue.popleft()
        if (x, y) == goal:
            return True

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < rows and 0 <= ny < cols:
                if grid[nx][ny] == 0 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
    return False
