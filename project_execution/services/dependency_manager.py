from typing import List
from project_execution.schemas.execution_models import ExecutionTask, TaskState

class DependencyManager:
    def detect_cycles(self, tasks: List[ExecutionTask]) -> List[List[str]]:
        task_map = {t.name: t for t in tasks}
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(task_name, path):
            visited.add(task_name)
            rec_stack.add(task_name)
            path.append(task_name)
            
            for dep in task_map[task_name].dependencies:
                if dep not in visited:
                    dfs(dep, path)
                elif dep in rec_stack:
                    cycle_start = path.index(dep)
                    cycles.append(path[cycle_start:] + [dep])
                    
            path.pop()
            rec_stack.remove(task_name)
            
        for t in tasks:
            if t.name not in visited:
                dfs(t.name, [])
                
        return cycles
        
    def get_ready_tasks(self, tasks: List[ExecutionTask]) -> List[ExecutionTask]:
        completed = {t.name for t in tasks if t.state == TaskState.COMPLETED}
        ready = []
        for t in tasks:
            if t.state == TaskState.PENDING:
                if all(dep in completed for dep in t.dependencies):
                    t.state = TaskState.READY
                    ready.append(t)
        return ready
