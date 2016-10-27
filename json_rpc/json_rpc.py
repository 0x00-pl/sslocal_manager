import json

__author__ = 'pl'


def make_json_rpc_object():
    return {"jsonrpc": "2.0"}


def make_json_rpc_request(method, params, request_id=None):
    request = make_json_rpc_object()
    request['method'] = method
    request['params'] = params
    request['id'] = request_id
    return request


json_rpc_errors = {
    '-32700': {'code': -32700, 'message': 'Parse error'},  # Errors occurred on the server while parsing the JSON text.
    '-32600': {'code': -32600, 'message': 'Invalid Request'},  # The JSON sent is not a valid Request object.
    '-32601': {'code': -32601, 'message': 'Method not found'},  # The method does not exist / is not available.
    '-32602': {'code': -32602, 'message': 'Invalid params'},  # Invalid method parameter(s).
    '-32603': {'code': -32602, 'message': 'Internal error'},  # Internal JSON-RPC error.
    # -32000 to -32099 	Server error 	Reserved for implementation-defined server-errors.
}


def make_json_rpc_error(error_no, object_id=None):
    ret = make_json_rpc_object()
    ret['error'] = json_rpc_errors[str(error_no)]
    ret['id'] = object_id
    return ret


def make_json_rpc_result(result, object_id):
    ret = make_json_rpc_object()
    ret['result'] = result
    ret['id'] = object_id
    return ret


def call_json_rpc(methods, request_json):
    try:
        request_object = json.loads(request_json)
    except:
        return make_json_rpc_error(-32700)

    try:
        assert (request_object['jsonrpc'] == '2.0')
        assert (type(request_object['method']) in (str,))
        request_object['params'] = request_object.get('params', None)
        request_object['id'] = request_object.get('id', None)
    except:
        return make_json_rpc_error(-32600)

    method = methods.get(request_object['method'], None)
    if method is None:
        return make_json_rpc_error(-32601, request_object['id'])

    try:
        result = method(request_object['params'])
        object_id = request_object['id']
        if object_id is None:
            return None
    except:
        return make_json_rpc_error(-32603, request_object['id'])

    return make_json_rpc_result(result, object_id)
