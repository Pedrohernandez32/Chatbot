from ollama_plugin import ollama_handler, ollama_check

prompt = 'Haz un pequeño poema sobre programación en 3 versos'
print('OLLAMA check:', ollama_check())
res = ollama_handler(prompt)
print('Type of response:', type(res))

if hasattr(res, '__iter__') and not isinstance(res, (str, bytes)):
    print('Detected generator/streaming. Reading up to 10 chunks...')
    try:
        i = 0
        for chunk in res:
            print('CHUNK:', repr(chunk))
            i += 1
            if i >= 10:
                break
    except Exception as e:
        print('Generator error:', e)
else:
    print('Response (non-generator):', res)
