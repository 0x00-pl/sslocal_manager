__author__ = 'pl'

import time
import socket
import subprocess
from json_rpc import json_rpc
from json_rpc import json_rpc_tools


def f_id(x):
    return x


def set_diff(a, b, af=None, bf=None, merge_ab=None):
    af = af or f_id
    bf = bf or f_id
    merge_ab = merge_ab or (lambda x, y: x)

    ap = sorted(a, key=af)
    bp = sorted(b, key=bf)

    only_a = []
    only_b = []
    both_ab = []
    while len(ap) != 0 or len(bp) != 0:
        if len(ap) == 0:
            only_b.extend(bp)
            break
        if len(bp) == 0:
            only_a.extend(ap)
            break

        ak = af(ap[0])
        bk = bf(bp[0])
        if ak == bk:
            both_ab.append(merge_ab(ap.pop(0), bp.pop(0)))
        elif ak < bk:
            only_a.append(ap.pop(0))
        else:
            only_b.append(bp.pop(0))

    return only_a, both_ab, only_b


def test_port(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind(("127.0.0.1", int(port)))
    except socket.error as e:
        if e.errno == 98:
            # print("Port is already in use")
            pass
        else:
            # something else raised the socket.error exception
            # print(e)
            pass
        return False
    s.close()
    return True


class SslocalObject():
    def __init__(self, server_info):
        self.server_info = server_info
        self.process_object = None
        self.open_sslocal(**server_info)

    def open_sslocal(self, address, password, local_port, server_port=8388):
        self.process_object = subprocess.Popen([
            'sslocal',
            '-s', address,
            '-k', password,
            '-l', str(local_port),
            '-p', str(server_port),
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def get_port_list():
    return list(range(1080, 1100))


def get_server_list():
    return [
        {'address': '10.8.0.6', 'password': '123456'},
    ]


class SslocalManager():
    def __init__(self, port_list=None):
        self.active_process_list = []
        self.port_list = port_list or list(range(1080, 1100))

    def get_state(self):
        return [i.server_info for i in self.active_process_list]

    def open_connection(self, server_info, local_port_list):
        local_port = server_info.get('local_port')
        local_port_list = [local_port] + local_port_list if local_port is not None else local_port_list
        for i in local_port_list:
            if test_port(i):
                server_info['local_port'] = i
                break

        self.active_process_list.append(SslocalObject(server_info))

    def close_connection(self, sslocal_object):
        idx = self.active_process_list.index(sslocal_object)
        self.active_process_list.pop(idx)
        sslocal_object.process_object.terminate()
        print("======stdout======", sslocal_object.process_object.stdout.read())
        print("======stderr======", sslocal_object.process_object.stderr.read())

    def remove_stoped_connection(self):
        stoped_process = [i for i in self.active_process_list if i.process_object.returncode is not None]
        for i in stoped_process:
            self.close_connection(i)

    def update(self, server_list=None, port_list=None):
        self.remove_stoped_connection()
        if server_list is None and port_list is None:
            return

        self.port_list = port_list or self.port_list

        if server_list is not None:
            up, hold, down = set_diff(server_list, self.active_process_list,
                                      af=lambda x: x['address'], bf=lambda x: x.server_info['address'])
            for i in down:
                self.close_connection(i)
            for i in up:
                self.open_connection(i, port_list)


def main():
    # json_rpc_tools.remote_call('127.0.0.1', 'api', json_rpc.make_json_rpc_request())
    # spawn_sslocal('10.8.0.6', '123456', 1081)
    sm = SslocalManager()
    sm.update(get_server_list(), get_port_list())
    sm.update(get_server_list(), get_port_list())

    print("state", sm.get_state())

    time.sleep(10)

    sm.update([], get_port_list())
    print("state", sm.get_state())


    while True:
        time.sleep(10)

if __name__ == '__main__':
    print(test_port(1083))
    main()
