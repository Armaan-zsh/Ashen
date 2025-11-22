"""Concurrency utilities for Digital Forensic Surgeon."""

from __future__ import annotations

import os
import time
import signal
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed, Future
from typing import Any, Callable, Dict, List, Optional, TypeVar, Iterator, Tuple
from functools import wraps
from dataclasses import dataclass

T = TypeVar('T')
R = TypeVar('R')


@dataclass
class TaskResult:
    """Container for task execution results."""
    task_id: str
    result: Any
    exception: Optional[Exception] = None
    execution_time: float = 0.0
    success: bool = True


def create_thread_pool(max_workers: Optional[int] = None, 
                      thread_name_prefix: str = "forensic") -> ThreadPoolExecutor:
    """Create a configured thread pool executor."""
    if max_workers is None:
        max_workers = min(32, (os.cpu_count() or 1) + 4)
    
    return ThreadPoolExecutor(
        max_workers=max_workers,
        thread_name_prefix=thread_name_prefix,
        initializer=_setup_thread_context
    )


def create_process_pool(max_workers: Optional[int] = None) -> ProcessPoolExecutor:
    """Create a configured process pool executor."""
    if max_workers is None:
        max_workers = os.cpu_count() or 1
    
    return ProcessPoolExecutor(max_workers=max_workers)


def _setup_thread_context():
    """Setup thread-local context."""
    # Can be used to set thread-local variables
    pass


def run_parallel_tasks(tasks: List[Callable[[], R]], 
                      max_workers: Optional[int] = None,
                      timeout: Optional[float] = None,
                      return_exceptions: bool = True) -> List[TaskResult]:
    """Run tasks in parallel with optional timeout."""
    results = []
    
    with create_thread_pool(max_workers) as executor:
        # Submit all tasks
        future_to_task = {
            executor.submit(task): f"task_{i}" 
            for i, task in enumerate(tasks)
        }
        
        # Collect results
        for future in as_completed(future_to_task, timeout=timeout):
            task_id = future_to_task[future]
            
            try:
                start_time = time.time()
                result = future.result()
                execution_time = time.time() - start_time
                
                results.append(TaskResult(
                    task_id=task_id,
                    result=result,
                    execution_time=execution_time,
                    success=True
                ))
                
            except Exception as e:
                results.append(TaskResult(
                    task_id=task_id,
                    result=None,
                    exception=e,
                    success=False
                ))
    
    return results


def run_with_timeout(func: Callable[[], R], 
                    timeout: float,
                    default_result: Optional[R] = None) -> R:
    """Run function with timeout, returning default if timeout occurs."""
    
    def timeout_handler():
        raise TimeoutError(f"Function timed out after {timeout} seconds")
    
    timer = threading.Timer(timeout, timeout_handler)
    timer.start()
    
    try:
        result = func()
        timer.cancel()
        return result
    except TimeoutError:
        timer.cancel()
        return default_result
    except Exception as e:
        timer.cancel()
        raise e


def chunk_iterable(iterable: Iterator[T], chunk_size: int) -> Iterator[List[T]]:
    """Split iterable into chunks of specified size."""
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []
    
    if chunk:
        yield chunk


class ParallelFileScanner:
    """Parallel file scanning utility."""
    
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.executor = None
    
    def __enter__(self):
        self.executor = create_thread_pool(self.max_workers)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.executor:
            self.executor.shutdown(wait=True)
    
    def scan_files(self, file_paths: List[str], 
                  scan_function: Callable[[str], Any]) -> Iterator[Tuple[str, Any]]:
        """Scan files in parallel."""
        if not self.executor:
            raise RuntimeError("Scanner not initialized. Use as context manager.")
        
        # Submit all scan tasks
        future_to_path = {
            self.executor.submit(scan_function, file_path): file_path
            for file_path in file_paths
        }
        
        # Collect results
        for future in as_completed(future_to_path):
            file_path = future_to_path[future]
            
            try:
                result = future.result()
                yield file_path, result
            except Exception as e:
                yield file_path, {"error": str(e)}


class ProgressTracker:
    """Track progress of parallel operations."""
    
    def __init__(self, total_tasks: int):
        self.total_tasks = total_tasks
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.start_time = time.time()
        self.lock = threading.Lock()
    
    def increment(self, success: bool = True) -> None:
        """Increment completed task count."""
        with self.lock:
            if success:
                self.completed_tasks += 1
            else:
                self.failed_tasks += 1
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress information."""
        with self.lock:
            completed = self.completed_tasks
            failed = self.failed_tasks
            total_completed = completed + failed
        
        if self.total_tasks == 0:
            return {
                "progress_percent": 100.0,
                "completed": completed,
                "failed": failed,
                "total": self.total_tasks,
                "elapsed_time": time.time() - self.start_time,
                "estimated_remaining": 0.0,
                "tasks_per_second": 0.0
            }
        
        progress_percent = (total_completed / self.total_tasks) * 100
        elapsed_time = time.time() - self.start_time
        
        if total_completed > 0:
            tasks_per_second = total_completed / elapsed_time
            remaining_tasks = self.total_tasks - total_completed
            estimated_remaining = remaining_tasks / tasks_per_second if tasks_per_second > 0 else 0
        else:
            estimated_remaining = 0
            tasks_per_second = 0
        
        return {
            "progress_percent": progress_percent,
            "completed": completed,
            "failed": failed,
            "total": self.total_tasks,
            "elapsed_time": elapsed_time,
            "estimated_remaining": estimated_remaining,
            "tasks_per_second": tasks_per_second
        }


def parallel_map(func: Callable[[T], R], 
                items: List[T],
                max_workers: Optional[int] = None,
                chunksize: int = 1) -> List[R]:
    """Map function over items in parallel."""
    with create_thread_pool(max_workers) as executor:
        results = executor.map(func, items, chunksize=chunksize)
        return list(results)


def parallel_filter(predicate: Callable[[T], bool],
                   items: List[T],
                   max_workers: Optional[int] = None) -> List[T]:
    """Filter items in parallel."""
    with create_thread_pool(max_workers) as executor:
        # Submit all filter tasks
        futures = [executor.submit(predicate, item) for item in items]
        
        # Collect results
        filtered_items = []
        for future, item in zip(futures, items):
            try:
                if future.result():
                    filtered_items.append(item)
            except Exception:
                # Include item if predicate fails
                filtered_items.append(item)
        
        return filtered_items


def timeout_decorator(timeout_seconds: float):
    """Decorator to add timeout to function execution."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return run_with_timeout(
                lambda: func(*args, **kwargs),
                timeout_seconds,
                default_result=None
            )
        return wrapper
    return decorator


def retry_decorator(max_attempts: int = 3, 
                   delay: float = 1.0,
                   exceptions: Tuple[Exception, ...] = (Exception,)):
    """Decorator to retry function execution on failure."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
            
            # All attempts failed
            raise last_exception
        
        return wrapper
    return decorator


class TaskPool:
    """Pool for managing long-running tasks."""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = create_thread_pool(max_workers)
        self.tasks: Dict[str, Future] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}
    
    def submit_task(self, task_id: str, func: Callable, *args, **kwargs) -> None:
        """Submit a task to the pool."""
        if len(self.tasks) >= self.max_workers:
            raise RuntimeError("Task pool is full")
        
        future = self.executor.submit(func, *args, **kwargs)
        self.tasks[task_id] = future
    
    def get_result(self, task_id: str, timeout: Optional[float] = None) -> Optional[TaskResult]:
        """Get result of a task."""
        if task_id not in self.tasks:
            if task_id in self.completed_tasks:
                return self.completed_tasks[task_id]
            return None
        
        future = self.tasks[task_id]
        
        try:
            result = future.result(timeout=timeout)
            
            # Move to completed and remove from active tasks
            task_result = TaskResult(
                task_id=task_id,
                result=result,
                success=True
            )
            
            self.completed_tasks[task_id] = task_result
            del self.tasks[task_id]
            
            return task_result
            
        except Exception as e:
            task_result = TaskResult(
                task_id=task_id,
                result=None,
                exception=e,
                success=False
            )
            
            self.completed_tasks[task_id] = task_result
            del self.tasks[task_id]
            
            return task_result
    
    def wait_all(self, timeout: Optional[float] = None) -> List[TaskResult]:
        """Wait for all tasks to complete."""
        results = []
        
        # Get results from all current tasks
        task_ids = list(self.tasks.keys())
        for task_id in task_ids:
            result = self.get_result(task_id, timeout)
            if result:
                results.append(result)
        
        return results
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task."""
        if task_id in self.tasks:
            future = self.tasks[task_id]
            cancelled = future.cancel()
            if cancelled:
                del self.tasks[task_id]
                self.completed_tasks[task_id] = TaskResult(
                    task_id=task_id,
                    result=None,
                    exception=TimeoutError("Task cancelled"),
                    success=False
                )
            return cancelled
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current pool status."""
        return {
            "active_tasks": len(self.tasks),
            "completed_tasks": len(self.completed_tasks),
            "max_workers": self.max_workers
        }
    
    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the task pool."""
        self.executor.shutdown(wait=wait)


def create_cancellation_handler(cancel_event: threading.Event):
    """Create signal handler for graceful cancellation."""
    def handler(signum, frame):
        cancel_event.set()
    
    # Register signal handlers for Unix systems
    if hasattr(signal, 'SIGINT'):
        signal.signal(signal.SIGINT, handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, handler)
