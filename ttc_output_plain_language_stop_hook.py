import re
import threading

# Define a lock for thread safety
lock = threading.Lock()

def strip_code_blocks(text):
    """
    Strips code blocks from the given text.
    
    Args:
    text (str): The input text containing code blocks.
    
    Returns:
    str: The text with code blocks removed.
    """
    # Define patterns for code blocks
    code_patterns = [
        re.compile(r'"""(.*?)"""', re.DOTALL),
        re.compile(r"'''(.*?)'''", re.DOTALL),
        re.compile(r'def\s+[\w\s]+\s*\(', re.MULTILINE),
        re.compile(r'class\s+[\w\s]+\s*\(', re.MULTILINE),
        re.compile(r'if\s+[\w\s]+\s*:', re.MULTILINE),
    ]
    
    # Use a lock to ensure thread safety
    with lock:
        original_text = text
        for pattern in code_patterns:
            text = pattern.sub('', text)
    
    return text

# Example usage
if __name__ == '__main__':
    input_text = """
    This is a sample text with some code blocks.
    def example_function():
        print("Hello, World!")
    
    class ExampleClass:
        def __init__(self):
            pass
    
    if __name__ == '__main__':
        example_function()
    """
    cleaned_text = strip_code_blocks(input_text)
    print(cleaned_text)