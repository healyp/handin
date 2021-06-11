import cgi
import io
import os
import py_compile
import subprocess
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

import const

logFile = os.path.join(const.ROOTDIR, "registration.log")

""" ###########################################
    Server for student to access and download handin.py file
"""

class BaseCase(object):
    @staticmethod
    def handle_file(handler, full_path):
        try:
            with open(full_path, 'rb') as f:
                content = f.read()
            handler.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(full_path, msg)
            handler.handle_error(msg)

    @staticmethod
    def index_path(handler):
        return os.path.join(handler.full_path, 'handin.html')

    def test(self, handler):
        raise NotImplementedError("Not implemented")

    def act(self, handler):
        raise NotImplementedError("Not implemented")


class CaseDirectoryIndexFile(BaseCase):
    def test(self, handler):
        return os.path.isdir(handler.full_path) \
               and os.path.isfile(self.index_path(handler))

    def act(self, handler):
        self.handle_file(handler, self.index_path(handler))


class CaseNoFile(BaseCase):
    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))


class CaseCgiFile(BaseCase):
    @staticmethod
    def run_cgi(handler):
        content = subprocess.check_output(["python", handler.full_path])
        handler.send_content(content)

    def test(self, handler):
        return os.path.isfile(handler.full_path) \
               and handler.full_path.endswith('.py')

    def act(self, handler):
        self.run_cgi(handler)


class CaseExistingFile(BaseCase):
    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        self.handle_file(handler, handler.full_path)


class CaseDefault(BaseCase):
    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException("Unknown object '{0}'".format(handler.path))

class RequestHandler(BaseHTTPRequestHandler):
    """Handle request and return page"""

    error_page = """\
    <html>
    <body>
    <h1>Error accessing {path}</h1>
    <p>{msg}</p>
    </body>
    </html>
    """

    problemPage = """\
    <html>
    <body>
    <h2>handin registration problem:</h2>
    <p style="color:#FFA500";>{msg}</p>
    </body>
    </html>
    """

    cases = [
        CaseNoFile(),
        CaseCgiFile(),
        CaseExistingFile(),
        CaseDirectoryIndexFile(),
        CaseDefault(),
    ]

    base_path = const.ROOTDIR

    def do_GET(self):
        try:
            self.full_path = os.getcwd() + self.path # rel to HANDINHOME
            for case in self.cases:
                if case.test(self):
                    case.act(self)
                    break
        except Exception as e:
            self.handle_error(e)

    def do_POST(self):
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': self.headers['Content-Type'],
                },
            )
            self.send_response(200)
            self.send_header('Content-Type', 'text/html;charset=utf-8')
            self.end_headers()
            out = io.TextIOWrapper(
                self.wfile,
                encoding='utf-8',
                line_buffering=False,
                write_through=True,
            )

            student_id = form['studentID'].value
            student_name = form['studentName'].value

            logging.info(f"{self.client_address[0]} - ({student_id}, {student_name})")

            self.create_handin_file(student_id, student_name)
            if not os.path.isdir(const.ROOTDIR + "/tmp"):
                os.makedirs(const.ROOTDIR + "/tmp")

            spath = f"/.handin/tmp/handin_{student_id}.txt"
            out.write(f'<h2>handin script download</h2><p>Click <a href="{spath}" download="handin.py">here</a> to download your personalised handin.py script')

            out.detach()
            logging.info(f"{self.client_address[0]} - ({student_id}, sending handin.py)")

        except Exception as e:
            self.handle_error(e)

    def create_handin_file(self, student_id, student_name):
        # create /temp/ file directory if not exists
        tmpdir = os.path.join(const.ROOTDIR, "tmp")
        if not os.path.isdir(tmpdir):
            logging.info("{} didn't exist after all; creating now...".format(tmpdir))
            os.mkdir(tmpdir)
        # the /temp/handin_xxx.txt must be in .txt format. It is downloaded as handin.py file
        filename = "handin_" + student_id + ".txt"
        fpath = os.path.join(tmpdir, filename)
        hstpath = os.path.join(const.SRCDIR, 'handin_student_template.py')
        with open(fpath, 'wb') as f:
            content_bytes: bytes = open(hstpath, 'rb').read()
            content = content_bytes.decode('utf-8').format(
                        hostname=str(const.HOST),  # host
                        server_port=str(const.PORT),  # port
                        student_name=str(student_name),       # student name
                        student_id=str(student_id)
                     )

            python_path = os.path.join(tmpdir, "handin_" + student_id + ".py")
            with open(python_path, 'w+') as file:
                file.write(content)

            py_compile.compile(file=python_path, cfile=fpath) # compile the python file to bytecode so the student cannot easily alter the file
            os.remove(python_path) # delete the python file as we no longer need it

    def handle_error(self, msg):
        content = self.error_page.format(path=self.path, msg=msg)
        self.send_content(bytes(content.encode('utf-8')), status=404)

    def send_content(self, content: bytes, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


class ServerException(Exception):
    """Server Exception"""
    pass


if __name__ == '__main__':
    if os.getcwd() != const.HANDINHOME:
        print(f"Must start server from {const.HANDINHOME}; exiting.")
        exit()
    serverAddr = const.REGISTRATION_ADDR
    server = HTTPServer(server_address=serverAddr, RequestHandlerClass=RequestHandler)
    print('Starting server ...')
    logging.basicConfig(filename=logFile, level=logging.INFO, format='%(asctime)s %(message)s')
    logging.info('Open http://{}:{}'.format(const.REGISTRATION_HOST, const.REGISTRATION_PORT))
    server.serve_forever()
