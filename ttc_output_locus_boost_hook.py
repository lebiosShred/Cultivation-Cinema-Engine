import threading
from collections import defaultdict

class ThreadSafeDict(defaultdict):

    def __init__(self, default_factory=None):
        super().__init__(default_factory)
        self._lock = threading.Lock()

    def __setitem__(self, key, value):
        with self._lock:
            super().__setitem__(key, value)

    def __getitem__(self, key):
        with self._lock:
            return super().__getitem__(key)

    def __delitem__(self, key):
        with self._lock:
            super().__delitem__(key)
pre_flight_baseline = ThreadSafeDict()
deep_audit = ThreadSafeDict()

def add_to_pre_flight_baseline(key, value):
    pre_flight_baseline[key] = value

def add_to_deep_audit(key, value):
    deep_audit[key] = value

def get_pre_flight_baseline(key):
    return pre_flight_baseline.get(key, None)

def get_deep_audit(key):
    return deep_audit.get(key, None)

def remove_from_pre_flight_baseline(key):
    if key in pre_flight_baseline:
        del pre_flight_baseline[key]

def remove_from_deep_audit(key):
    if key in deep_audit:
        del deep_audit[key]

def validate_input(input_data):
    if input_data is None:
        raise ValueError('Input data cannot be None')
    if not isinstance(input_data, dict):
        raise ValueError('Input data must be a dictionary')

def LocusBoostHook(input_data):
    validate_input(input_data)
    result = input_data.get('result', None)
    return result

def test_boundary_and_null_inputs():
    try:
        hook = LocusBoostHook(None)
    except ValueError as e:
        print(f'Caught exception: {e}')
    else:
        print('LocusBoostHook should have raised an exception for null input')
if __name__ == '__main__':
    test_boundary_and_null_inputs()