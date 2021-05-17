from const import *
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
import logging
from handin_file_server import *

class TrustMacAddress(AbstractCommand):
    COMMAND = FileServerCommands.TRUST_MAC_ADDRESS

    def __init__(self):
        super().__init__()

    def handleRequest(self, request: Request):
        if (authenticate_lecturer(request, "TRUST_MAC_ADDRESS", False)):
            params = request.args
            mac = None

            if "mac" in params:
                mac = params['mac']

            if mac is None:
                request_bad("TRUST_MAC_ADDRESS", "Required mac value not provided")
                respond(request, False, "You need to provide a mac in an TRUST_MAC_ADDRESS request")
                return

            trust = "false"

            if "trust" in params:
                trust = params['trust']
            else:
                logging.warning("trust value not provided in TRUST_MAC_ADDRESS request, defaulting to \"false\"")

            lecturer = params['lecturer']

            response_data = {}
            filepath = ROOTDIR + "/users/" + lecturer + "/mac_addresses.txt"
            logging.debug(f"Reading file {filepath}")
            with open(filepath, 'r+') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if line.startswith(mac):
                        if(trust == "true"):
                            data = line.split()
                            lines[i] = data[0] + " false\n"
                f.seek(0)
                if(trust == "false"):
                    for line in lines:
                        if(not line.startswith(mac)):
                            f.write(line)
                else:
                    for line in lines:
                        f.write(line)
                f.truncate()

            request_ok("TRUST_MAC_ADDRESS")
            respond(request, True, "TRUST_MAC_ADDRESS successful")
        else:
            request_unauthorized("TRUST_MAC_ADDRESS")
            send_unauthorized_lecturer_response(request)
