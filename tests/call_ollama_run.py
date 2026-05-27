import sys
import os
# Ensure project root is on sys.path so imports work when running from tests/
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ollama_plugin import ollama_check, ollama_handler

print('ollama_check=', ollama_check())
r = ollama_handler('Cuenta un chiste corto sobre un programador')
print('type=', type(r))

if hasattr(r, '__iter__') and not isinstance(r, (str, bytes)):
    import time
    i = 0
    last = time.time()
    try:
        for ch in r:
            print('CHUNK:', repr(ch))
            i += 1
            last = time.time()
            # stop after 30 chunks or if idle for 6s
            if i >= 30:
                break
            if time.time() - last > 6:
                break
    except Exception as e:
        print('Generator error:', e)
else:
    print('RESPONSE:', r)
