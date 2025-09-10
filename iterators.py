from typing import Any, Iterator, Optional


class CircularBuffer:
    """Fixed-size buffer that overwrites old data when full"""
    
    def __init__(self, size: int):
        self.size = size
        self.buffer = [None] * size
        self.index = 0
        self.count = 0
    
    def add(self, item: Any) -> None:
        """Add item to buffer"""
        self.buffer[self.index] = item
        self.index = (self.index + 1) % self.size
        self.count = min(self.count + 1, self.size)
    
    def __iter__(self) -> Iterator[Any]:
        """Iterate over buffer items in order of insertion"""
        if self.count == 0:
            return iter([])
        
        if self.count < self.size:
            # Buffer not full yet, return from start
            return iter(self.buffer[:self.count])
        else:
            # Buffer is full, return from current position
            return iter(self.buffer[self.index:] + self.buffer[:self.index])


class ConfigManager:
    """Configuration manager with nested key access"""
    
    def __init__(self, config_dict: dict):
        self.config = config_dict
    
    def __iter__(self) -> Iterator[tuple[str, Any]]:
        """Iterate over all config key-value pairs, flattening nested dicts"""
        return self._flatten_dict(self.config)
    
    def _flatten_dict(self, d: dict, parent_key: str = '') -> Iterator[tuple[str, Any]]:
        """Recursively flatten nested dictionary"""
        for key, value in d.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            
            if isinstance(value, dict):
                yield from self._flatten_dict(value, full_key)
            else:
                yield (full_key, value)


class DataValidator:
    """Validate data items with custom rules"""
    
    def __init__(self, data: list, validation_rules: dict):
        self.data = data
        self.rules = validation_rules
    
    def __iter__(self) -> Iterator[dict]:
        """Iterate over valid data items only"""
        for item in self.data:
            if self._validate_item(item):
                yield item
    
    def _validate_item(self, item: dict) -> bool:
        """Check if item passes all validation rules"""
        for field, rule in self.rules.items():
            if field not in item:
                return False
            
            value = item[field]
            
            # Type validation
            if 'type' in rule and not isinstance(value, rule['type']):
                return False
            
            # Range validation for numbers
            if 'min' in rule and value < rule['min']:
                return False
            if 'max' in rule and value > rule['max']:
                return False
            
            # Length validation for strings
            if 'min_length' in rule and len(value) < rule['min_length']:
                return False
            if 'max_length' in rule and len(value) > rule['max_length']:
                return False
        
        return True


class RangeQuery:
    """Iterator for range-based queries with step and filter"""
    
    def __init__(self, start: int, end: int, step: int = 1, condition=None):
        self.start = start
        self.end = end
        self.step = step
        self.condition = condition or (lambda x: True)
    
    def __iter__(self) -> Iterator[int]:
        current = self.start
        while current < self.end:
            if self.condition(current):
                yield current
            current += self.step


class ChainedIterator:
    """Chain multiple iterators together"""
    
    def __init__(self, *iterables):
        self.iterables = iterables
    
    def __iter__(self) -> Iterator[Any]:
        for iterable in self.iterables:
            yield from iterable


class WindowIterator:
    """Sliding window iterator over a sequence"""
    
    def __init__(self, sequence: list, window_size: int):
        self.sequence = sequence
        self.window_size = window_size
    
    def __iter__(self) -> Iterator[list]:
        if len(self.sequence) < self.window_size:
            return iter([])
        
        for i in range(len(self.sequence) - self.window_size + 1):
            yield self.sequence[i:i + self.window_size]


if __name__ == "__main__":
    print("=== Testing Custom Iterators ===")
    
    # Test CircularBuffer
    buffer = CircularBuffer(3)
    for i in range(6):
        buffer.add(f"item_{i}")
    
    print("Circular buffer contents:", list(buffer))
    
    # Test ConfigManager
    config = {
        'database': {
            'host': 'localhost',
            'port': 5432,
            'credentials': {
                'username': 'admin',
                'password': 'secret'
            }
        },
        'cache': {
            'ttl': 300,
            'size': 1000
        },
        'debug': True
    }
    
    config_manager = ConfigManager(config)
    print("\nFlattened config:")
    for key, value in config_manager:
        print(f"  {key}: {value}")
    
    # Test DataValidator
    user_data = [
        {'id': 1, 'name': 'Alice', 'age': 25, 'email': 'alice@example.com'},
        {'id': 2, 'name': 'Bob', 'age': 17, 'email': 'bob@example.com'},  # Invalid age
        {'id': 3, 'name': 'Charlie', 'age': 30, 'email': 'charlie'},  # Invalid email
        {'id': 4, 'name': 'Diana', 'age': 28, 'email': 'diana@example.com'},
    ]
    
    validation_rules = {
        'id': {'type': int, 'min': 1},
        'name': {'type': str, 'min_length': 2, 'max_length': 50},
        'age': {'type': int, 'min': 18, 'max': 120},
        'email': {'type': str, 'min_length': 5}
    }
    
    validator = DataValidator(user_data, validation_rules)
    valid_users = list(validator)
    print(f"\nValid users: {len(valid_users)} out of {len(user_data)}")
    
    # Test RangeQuery
    even_numbers = list(RangeQuery(0, 20, 2, lambda x: x % 2 == 0))
    print(f"Even numbers 0-20: {even_numbers}")
    
    # Test ChainedIterator
    list1 = [1, 2, 3]
    list2 = ['a', 'b', 'c']
    list3 = [True, False]
    
    chained = ChainedIterator(list1, list2, list3)
    print(f"Chained iterators: {list(chained)}")
    
    # Test WindowIterator
    sequence = [1, 2, 3, 4, 5, 6, 7, 8]
    windows = list(WindowIterator(sequence, 3))
    print(f"Sliding windows of size 3: {windows}")