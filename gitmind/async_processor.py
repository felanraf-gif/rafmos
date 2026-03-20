import logging
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any, Optional, Dict
from threading import Lock

logger = logging.getLogger(__name__)


class AsyncProcessor:
    def __init__(self, max_workers: int = 2):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.futures: Dict[str, Future] = {}
        self.lock = Lock()
    
    def submit(self, task_id: str, func: Callable, *args, **kwargs) -> Future:
        future = self.executor.submit(func, *args, **kwargs)
        
        with self.lock:
            self.futures[task_id] = future
        
        logger.info(f"Task {task_id} submitted for background processing")
        return future
    
    def get_result(self, task_id: str, timeout: float = None) -> Optional[Any]:
        with self.lock:
            future = self.futures.get(task_id)
        
        if future is None:
            return None
        
        try:
            result = future.result(timeout=timeout)
            return result
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            return {"error": str(e)}
        finally:
            with self.lock:
                if task_id in self.futures:
                    del self.futures[task_id]
    
    def cancel(self, task_id: str) -> bool:
        with self.lock:
            future = self.futures.get(task_id)
        
        if future:
            return future.cancel()
        return False
    
    def get_status(self, task_id: str) -> str:
        with self.lock:
            future = self.futures.get(task_id)
        
        if future is None:
            return "not_found"
        
        if future.done():
            if future.cancelled():
                return "cancelled"
            try:
                future.result()
                return "completed"
            except Exception:
                return "failed"
        return "running"
    
    def get_pending_count(self) -> int:
        with self.lock:
            return sum(1 for f in self.futures.values() if not f.done())
    
    def shutdown(self, wait: bool = True):
        self.executor.shutdown(wait=wait)


async_processor = AsyncProcessor(max_workers=2)


def submit_review(project_id: str, mr_iid: int, handler_func: Callable) -> str:
    task_id = f"review_{project_id}_{mr_iid}"
    async_processor.submit(task_id, handler_func, project_id, mr_iid)
    return task_id


def get_review_status(task_id: str) -> Dict:
    return {
        "task_id": task_id,
        "status": async_processor.get_status(task_id)
    }
