import os
import sys
sys.path.insert(0, r'c:\Users\p20on\Documents\Vsproyects\Chatbot')
from portal_plugin import portal_handler

os.environ['UNIVERSITY_PORTAL_URL'] = 'https://www.udem.edu.co'
print('Running portal_plugin test...')
res = portal_handler('¿Qué programas ofrece la universidad?')
print('Has result:', bool(res))
if res:
    print(res[:800])
else:
    print('No snippet found or portal not accessible.')
