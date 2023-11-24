class Task:
    def __init__(self, id: int, deadline: int, computation: int, predecessors: list[int]) -> None:
        self.id = id
        self.deadline = deadline
        self.predecessors = predecessors
        self.computation = computation
        self.new_deadline = -1
        self.new_release_time = -1
    
    # Get the successors of current task
    def successors(self, tasks: dict) -> list[int]:
        result: list[int] = []
        for id, task in tasks.items():
            if self.id in task.predecessors:
                result.append(id)
        return result


# Create tasks of the system
tasks: dict[int, Task] = {}
tasks[1] = Task(1,   20,  3,  [])
tasks[2] = Task(2,   50,  18, [1])
tasks[3] = Task(3,   50,  12, [1])
tasks[4] = Task(4,   50,  9,  [1])
tasks[5] = Task(5,   50,  11, [1])
tasks[6] = Task(6,   50,  12, [1])
tasks[7] = Task(7,   70,  19, [3])
tasks[8] = Task(8,   70,  3,  [2, 4, 6])
tasks[9] = Task(9,   70,  8,  [2, 5])
tasks[10] = Task(10, 110, 1,  [7, 8, 9])

# Fix the release time of fathers
for task in tasks.values():
    if len(task.predecessors) == 0:
        print("Father", task.id)
        task.new_release_time = 0
# Fix all release times
while any(map(lambda t: t.new_release_time == -1 ,tasks.values())):
    for current_task in tasks.values():
        if current_task.new_release_time == -1 and all(map(lambda id: tasks[id].new_release_time != -1, current_task.predecessors)):
            current_task.new_release_time = max(map(lambda id: tasks[id].new_release_time + tasks[id].computation, current_task.predecessors))

# Fix deadlines of leaves
for task_id, task in tasks.items():
    if not any(map(lambda t: task_id in t.predecessors, tasks.values())):
        print("Leaf", task_id)
        task.new_deadline = task.deadline
# Fix all deadlines
while any(map(lambda t: t.new_deadline == -1 ,tasks.values())):
    for current_task in tasks.values():
        if current_task.new_deadline == -1 and all(map(lambda id: tasks[id].new_deadline != -1, current_task.successors(tasks))):
            current_task.new_deadline = min(current_task.deadline, min(map(lambda id: tasks[id].deadline - tasks[id].computation, current_task.successors(tasks))))

# Print new tasks
print("New tasks:")
for task_id in sorted(tasks.keys()):
    print(f"{task_id}\t{tasks[task_id].new_deadline}\t{tasks[task_id].new_release_time}")
