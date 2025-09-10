import time
import functools
from typing import Any, Callable


def timer(func: Callable) -> Callable:
    """Measure execution time of functions"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper


def cache_result(func: Callable) -> Callable:
    """Simple memoization decorator"""
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from args and kwargs
        key = str(args) + str(sorted(kwargs.items()))
        if key in cache:
            print(f"Cache hit for {func.__name__}")
            return cache[key]
        
        result = func(*args, **kwargs)
        cache[key] = result
        print(f"Cache miss for {func.__name__}, storing result")
        return result
    return wrapper


def validate_types(**expected_types):
    """Decorator to validate function argument types"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate types
            for param_name, expected_type in expected_types.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not isinstance(value, expected_type):
                        raise TypeError(f"{param_name} must be {expected_type.__name__}, got {type(value).__name__}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Practical usage examples
@timer
@cache_result
def expensive_calculation(n: int) -> int:
    """Simulate expensive computation"""
    time.sleep(0.1)  # Simulate work
    return sum(i * i for i in range(n))


@validate_types(data=list, multiplier=int)
def process_data(data: list, multiplier: int = 1) -> list:
    """Process list data with validation"""
    return [x * multiplier for x in data]


class RateLimiter:
    """Decorator class for rate limiting"""
    def __init__(self, max_calls: int, time_window: float):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old calls outside time window
            self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
            
            if len(self.calls) >= self.max_calls:
                raise Exception(f"Rate limit exceeded: {self.max_calls} calls per {self.time_window} seconds")
            
            self.calls.append(now)
            return func(*args, **kwargs)
        return wrapper


@RateLimiter(max_calls=3, time_window=1.0)
def api_call(endpoint: str) -> str:
    """Simulate API call with rate limiting"""
    return f"Called {endpoint}"


if __name__ == "__main__":
    # Test decorators
    print("=== Testing Decorators ===")
    
    # Test caching and timing
    result1 = expensive_calculation(100)
    result2 = expensive_calculation(100)  # Should hit cache
    
    # Test validation
    process_data([1, 2, 3], 2)
    
    # Test rate limiting
    for i in range(4):
        try:
            result = api_call('/users')
            print(f"API call {i + 1}: {result}")
        except Exception as e:
            print(f"API call {i + 1}: BLOCKED - {e}")
        time.sleep(0.3)