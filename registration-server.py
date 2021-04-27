import cgi
import io
import os
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

            modCode = form['moduleCode'].value
            student_id = form['studentID'].value
            student_name = form['studentName'].value

            logging.info(f"{self.client_address[0]} - ({modCode}, {student_id}, {student_name})")

            modpath = os.path.join(const.ROOTDIR, modCode, "curr")
            clpath = os.path.join(modpath, "class-list")

            if not self.moduleExists(modCode):
                emsg = "Nothing known about module {}; please contact your instructor.".format(modCode)
                out.write(self.problemPage.format(msg=emsg))
                logging.info(f"{self.client_address[0]} - ({modCode}, {student_id}, unknown module)")
                out.detach()
            elif not self.classListExists(modCode):
                emsg = "No class list exists for module {}; please contact your instructor.".format(modCode)
                out.write(self.problemPage.format(msg=emsg))
                logging.info(f"{self.client_address[0]} - ({modCode}, {student_id}, no class list exists)")
                out.detach()
            elif const.findStudentId(student_id, clpath) == '':
                emsg = "Student ID {} is not on {} class list; please contact your instructor.".format(student_id, modCode)
                out.write(self.problemPage.format(msg=emsg))
                logging.info(f"{self.client_address[0]} - ({modCode}, {student_id}, not on class list)")
                out.detach()
            else:
                self.create_handin_file(modpath, modCode, student_id, student_name)
                spath = f"/.handin/{modCode}/curr/tmp/handin_{student_id}.txt"
                out.write(f'<h2>handin script download</h2><p>Click <a href="{spath}" download="handin.py">here</a> to download your personalised handin.py script')

                out.detach()
                logging.info(f"{self.client_address[0]} - ({modCode}, {student_id}, sending handin.py)")
                
        except Exception as e:
            self.handle_error(e)

    def moduleExists(self, mc):
        return os.path.exists(os.path.join(const.ROOTDIR, mc))

    def currentSemesterExists(self, mc):
        ay = const.whatAY()
        return os.path.exists(os.path.join(const.ROOTDIR, mc, ay))

    def classListExists(self, mc):
        return os.path.exists(os.path.join(const.ROOTDIR, mc, "curr", "class-list"))

    def create_handin_file(self, modpath, modcode, student_id, student_name):
        # create /temp/ file directory if not exists
        tmpdir = os.path.join(modpath, "tmp")
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
                        str(const.HOST),  # host
                        str(const.PORT),  # port
                        str(student_name),       # student name
                        str(student_id),         # student id
                        str(modcode),        # module code
                     ).encode('utf-8')
            f.write(content)

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
    serverAddr = const.ADDR
    server = HTTPServer(server_address=serverAddr, RequestHandlerClass=RequestHandler)
    print('Starting server ...')
    logging.basicConfig(filename=logFile, level=logging.INFO, format='%(asctime)s %(message)s')
    logging.info('Open http://{}:{}'.format(const.HOST, const.PORT))
    server.serve_forever()
