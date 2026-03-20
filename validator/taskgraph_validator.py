def is_dag(tasks, dependencies):
    graph = {t["id"]: [] for t in tasks}
    indegree = {t["id"]: 0 for t in tasks}

    for a, b in dependencies:
        graph[a].append(b)
        indegree[b] += 1

    # Kahn's algorithm
    queue = [n for n in indegree if indegree[n] == 0]
    visited = 0

    while queue:
        n = queue.pop(0)
        visited += 1
        for m in graph[n]:
            indegree[m] -= 1
            if indegree[m] == 0:
                queue.append(m)

    return visited == len(tasks)


def validate_project_world(world):
    tasks = world["tasks"]
    deps = world.get("dependencies", [])

    if not tasks:
        return False, "No tasks"

    if not is_dag(tasks, deps):
        return False, "Cyclic or impossible dependency graph"

    return True, "OK"
