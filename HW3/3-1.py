import json
import operator

class AperiodicTask:
    def __init__(self, id: int, release_time: int, computation_time: int):
        self.id = id
        self.release_time = release_time
        self.remaining_computation_time = computation_time

class PeriodicTask:
    def __init__(self, id: int, computation_time: int, interval: int):
        self.id = id
        self.interval = interval
        self.computation_time = computation_time
        self.remaining_computation_time = computation_time
    
    def utilization(self) -> float:
        return self.computation_time / self.interval

class PollingServer:
    def __init__(self, server_capacity: int, server_period: int, aperiodic_tasks: list[AperiodicTask], periodic_tasks: list[PeriodicTask]):
        self.server_capacity = server_capacity
        self.server_period = server_period
        self.remaining_server_capacity = server_capacity
        self.aperiodic_tasks = aperiodic_tasks
        self.periodic_tasks = periodic_tasks
    
    def is_schedulable(self) -> bool:
        return sum(map(lambda task: task.utilization(), self.periodic_tasks)) + self.server_capacity / self.server_period <= (len(self.periodic_tasks) + 1) * (pow(2, 1 / (len(self.periodic_tasks) + 1)) - 1)

def create_polling_server_from_json(filename: str) -> PollingServer:
    with open(filename, 'r') as file:
        loaded_json_file = json.load(file)
    aperiodic_tasks: list[AperiodicTask] = []
    for task in loaded_json_file["aperiodic_tasks"]:
        aperiodic_tasks.append(AperiodicTask(task["id"], task["release_time"], task["computation_time"]))
    aperiodic_tasks.sort(key=operator.attrgetter('release_time'))
    periodic_tasks: list[PeriodicTask] = []
    for task in loaded_json_file["periodic_tasks"]:
        periodic_tasks.append(PeriodicTask(task["id"], task["computation_time"], task["interval"]))
    periodic_tasks.sort(key=operator.attrgetter('interval'))
    return PollingServer(loaded_json_file["server_capacity"], loaded_json_file["server_period"], aperiodic_tasks, periodic_tasks)

def schedule_until(server: PollingServer, until_time: int):
    handling_aperiodic_tasks = False
    for current_time in range(until_time + 1):
        # Refresh periods / computation times
        for task in server.periodic_tasks:
            if current_time % task.interval == 0:
                task.remaining_computation_time = task.computation_time
        # Check polling server interval
        if current_time % server.server_period == 0:
            # Check if there is any task which can be run
            if any(map(lambda task: task.remaining_computation_time > 0 and current_time >= task.release_time, server.aperiodic_tasks)):
                handling_aperiodic_tasks = True
                server.remaining_server_capacity = server.server_capacity
                print(f"Starting to handle aperiodic tasks in T={current_time}")
            else:
                handling_aperiodic_tasks = False
        # Check periodic tasks
        did_periodic_task = False
        for task in server.periodic_tasks:
            if task.remaining_computation_time > 0 and task.interval < server.server_period:
                print(f"Did one unit of periodic task {task.id} in T={current_time}")
                did_periodic_task = True
                task.remaining_computation_time -= 1
                break
        if did_periodic_task:
            continue
        # Check aperiodic tasks
        did_aperiodic_task = False
        if handling_aperiodic_tasks:
            for task in server.aperiodic_tasks:
                if task.remaining_computation_time > 0 and task.release_time <= current_time:
                    task.remaining_computation_time -= 1
                    server.remaining_server_capacity -= 1
                    print(f"Did one unit of aperiodic task {task.id} in T={current_time}. Server has {server.remaining_server_capacity} units of capacity left")
                    if server.remaining_server_capacity == 0:
                        handling_aperiodic_tasks = False
                    did_aperiodic_task = True
                    break
        if did_aperiodic_task:
            continue
        else:
            handling_aperiodic_tasks = False
        # Check other tasks (periodic)
        for task in server.periodic_tasks:
            if task.remaining_computation_time > 0 and task.interval >= server.server_period:
                print(f"Did one unit of periodic task {task.id} in T={current_time}")
                task.remaining_computation_time -= 1
                break

server = create_polling_server_from_json(input("Enter the configuration filename: "))
if not server.is_schedulable():
    print("Not schedulable!")
    exit(0)
schedule_until(server, int(input("Schedule until when? ")))