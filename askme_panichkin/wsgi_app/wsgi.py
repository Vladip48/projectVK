def application(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]

    get_params = environ.get('QUERY_STRING', '')
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0
    post_params = environ['wsgi.input'].read(request_body_size).decode('utf-8')

    response_body = [
        "GET parameters: " + get_params + "\n",
        "POST parameters: " + post_params + "\n"
    ]

    start_response(status, headers)
    return [body.encode('utf-8') for body in response_body]