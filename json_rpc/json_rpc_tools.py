import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from json_rpc.json_rpc import call_json_rpc, make_json_rpc_error

__author__ = 'pl'


def remote_call(address, path, request_obj):
    connection = http.client.HTTPConnection(address)
    args_json = json.dumps(request_obj)
    connection.request('POST', '/' + path, args_json)
    response = connection.getresponse()
    status_code = response.status
    ret_json = response.read().decode('utf-8', errors='ignore')
    ret = json.loads(ret_json)
    if status_code != 200:
        raise ChildProcessError(ret)
    if ret.get('error') is not None:
        print(ret)
    return ret


class JsonRpcServer(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def do_POST(self):
        """Serve a POST request."""
        try:
            data_str = self.rfile.read(int(self.headers['Content-Length']))
            data_str = data_str.decode(encoding='utf-8')
            methods = self.server.json_rpc_methods
            result = call_json_rpc(methods, data_str)
        except ValueError:
            result = make_json_rpc_error(-32603)

        return self.send_reply(result)

    def send_reply(self, content):
        content_json = json.dumps(content).encode('utf-8', errors='ignore')

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content_json)))
        self.end_headers()
        self.wfile.write(content_json)


def run_json_rpc_server(bind, port, methods):
    server_address = (bind, port)
    httpd = HTTPServer(server_address=server_address, RequestHandlerClass=JsonRpcServer)
    httpd.json_rpc_methods = methods

    sa = httpd.socket.getsockname()
    print("Serving HTTP on", sa[0], "port", sa[1], "...")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
        httpd.server_close()
        raise
