import ctypes
import json
import numpy as np
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

def parse_path(path):
    result = urlparse(path)
    return {
        'path': result[2],
        'query': dict((key, vals[0]) for key, vals in parse_qs(result[4]).items())
    }

def run(server_class=HTTPServer, handler_class=None, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Now the http server is serving.')
    httpd.serve_forever()


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class DiagnosisServer(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server, user_diagnosis_classifier):
        self.user_diagnosis_classifier = user_diagnosis_classifier
        super().__init__(request, client_address, server)

    def _send_headers(self, state_code):
        self.send_response(state_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def _respond(self, state_code, msg, data):
        self._send_headers(state_code)
        self.wfile.write(bytes(json.dumps({
            'message': msg,
            'data': data
        }), 'UTF-8'))

    def do_POST(self):
        params = parse_path(self.path)
        try:
            if params['path'] == '/classification':
                self.do_classification()
        except Exception as err:
            self._respond(400, 'Error occurs: ' + str(err), None)

    def do_classification(self):
        ctype = self.headers.get('content-type')
        if ctype == 'application/json':
            length = int(self.headers.get('content-length', 0))
            try:
                data = json.loads(self.rfile.read(length))
                age = data["age"]
                gender = data["gender"]
                questions = data["questions"]
                sequences = data["sequences"]
                results = []
                for sequence in sequences:
                    results.append(run_one_sequence(sequence["data"], sequence["painful"], age, gender, questions))




            except(ValueError, KeyError, TypeError):
                print("JSON format error")


        result = json.dumps(average_result(results))
        self._respond(200, 'do_classification successfully', result)


def run_one_sequence(sequence, painful, age, gender, questions):
    # todo
    return [1, 0.3, 1, 0.44, 1, 0.2, 1, 0.1, 0.44, 1]  # 12個答案


def average_result(results):
    r = np.array(results)
    result = np.mean(r, axis=0).tolist()
    print(result)
    return result


if __name__ == "__main__":
    import sys
    from sys import argv

    # if the script is not run in the administrator privilege, pop up the UAC dialog to seek to elevate
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
		
    user_diagnosis_classifier = None
    port = int(argv[1]) if len(argv) == 2 else 5000

    run(port=port, handler_class=lambda request, client_address, server: DiagnosisServer(request, client_address, server, user_diagnosis_classifier))