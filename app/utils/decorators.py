from functools import wraps
import logging
from typing import Callable, TypeVar, ParamSpec

logger = logging.getLogger(__name__)

P = ParamSpec('P')  # For function parameters
T = TypeVar('T')    # For return type

def handle_exceptions(error_message: str = None):
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                msg = error_message or f"Failed in {func.__name__}"
                logger.error(f"❌ {msg}: {str(e)}", exc_info=True)
                raise Exception(f"{msg}: {str(e)}")

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                msg = error_message or f"Failed in {func.__name__}"
                logger.error(f"❌ {msg}: {str(e)}", exc_info=True)
                raise Exception(f"{msg}: {str(e)}")

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator
