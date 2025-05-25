def application(env, start_response):
    start_response('200 OK', [('Content-Typeу', 'text/html')])
    return [b"Hello World"]