import os
from typing import Generator, Dict, Any


def batch_processor(data: list, batch_size: int) -> Generator[list, None, None]:
    """Process data in batches - memory efficient for large datasets"""
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]


def file_line_reader(filepath: str) -> Generator[str, None, None]:
    """Read file line by line without loading entire file into memory"""
    with open(filepath, 'r') as file:
        for line in file:
            yield line.strip()


def log_parser(log_lines: Generator[str, None, None]) -> Generator[Dict[str, Any], None, None]:
    """Parse log lines into structured data"""
    for line in log_lines:
        if line and not line.startswith('#'):
            parts = line.split(' - ')
            if len(parts) >= 3:
                yield {
                    'timestamp': parts[0],
                    'level': parts[1],
                    'message': ' - '.join(parts[2:])
                }


def fibonacci_sequence(limit: int) -> Generator[int, None, None]:
    """Generate Fibonacci numbers up to limit"""
    a, b = 0, 1
    while a < limit:
        yield a
        a, b = b, a + b


def data_pipeline(source_data: list) -> Generator[Dict[str, Any], None, None]:
    """Transform raw data through multiple steps"""
    for item in source_data:
        # Step 1: Filter out invalid data
        if isinstance(item, dict) and 'id' in item:
            # Step 2: Normalize and enrich
            processed = {
                'id': item['id'],
                'name': item.get('name', 'Unknown').title(),
                'score': item.get('score', 0) * 1.1,  # Apply bonus
                'category': item.get('category', 'general').lower()
            }
            
            # Step 3: Only yield items that meet criteria
            if processed['score'] > 50:
                yield processed


class NumberStream:
    """Generator class for producing number streams"""
    def __init__(self, start: int, step: int = 1):
        self.start = start
        self.step = step
    
    def __iter__(self):
        return self
    
    def __next__(self):
        current = self.start
        self.start += self.step
        return current
    
    def take(self, n: int) -> Generator[int, None, None]:
        """Take n numbers from the stream"""
        for _ in range(n):
            yield next(self)


def send_example() -> Generator[str, str, None]:
    """Generator that can receive values via send()"""
    received = None
    while True:
        if received:
            response = f"Processed: {received.upper()}"
        else:
            response = "Ready for input"
        
        received = yield response


if __name__ == "__main__":
    print("=== Testing Generators ===")
    
    # Test batch processing
    large_dataset = list(range(1000))
    batch_count = 0
    for batch in batch_processor(large_dataset, 100):
        batch_count += 1
    print(f"Processed {batch_count} batches of data")
    
    # Create a test log file
    with open('test.log', 'w') as f:
        f.write("2024-01-01 10:00:00 - INFO - Application started\n")
        f.write("2024-01-01 10:01:00 - ERROR - Database connection failed\n")
        f.write("2024-01-01 10:02:00 - INFO - Retrying connection\n")
    
    # Test file reading and log parsing
    log_entries = list(log_parser(file_line_reader('test.log')))
    print(f"Parsed {len(log_entries)} log entries")
    
    # Test Fibonacci generator
    fib_numbers = list(fibonacci_sequence(100))
    print(f"Fibonacci numbers under 100: {fib_numbers}")
    
    # Test data pipeline
    raw_data = [
        {'id': 1, 'name': 'john', 'score': 85, 'category': 'Premium'},
        {'id': 2, 'name': 'jane', 'score': 30, 'category': 'Basic'},
        {'id': 3, 'name': 'bob', 'score': 95, 'category': 'Premium'},
        {'invalid': 'data'},
    ]
    
    processed_data = list(data_pipeline(raw_data))
    print(f"Processed {len(processed_data)} valid records")
    
    # Test number stream
    stream = NumberStream(10, 5)
    numbers = list(stream.take(5))
    print(f"Generated numbers: {numbers}")
    
    # Test generator with send()
    processor = send_example()
    print(next(processor))  # Prime the generator
    print(processor.send("hello"))
    print(processor.send("world"))
    
    # Cleanup
    os.remove('test.log')