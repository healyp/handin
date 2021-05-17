from const import *
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
import logging
from handin_file_server import *

class AlertMacAddress(AbstractCommand):
    COMMAND = FileServerCommands.ALERT_MAC_ADDRESS

    def __init__(self):
        super().__init__()

    def handleRequest(self, request: Request):
        if (authenticate_lecturer(request, "ALERT_MAC_ADDRESS", False)):
            params = request.args
            mac = None
            if "mac" in params:
                mac = params['mac']

            if mac is None:
                request_bad("ALERT_MAC_ADDRESS", "Required mac value not provided")
                respond(request, False, "You need to provide a mac in an ALERT_MAC_ADDRESS request")
                return

            lecturer = params['lecturer']

            response_data = {}
            filepath = ROOTDIR + "/users/" + lecturer + "/mac_addresses.txt"
            logging.debug(f"Reading file {filepath}")
            alert = False
            line_found = False
            if(os.path.exists(filepath)):
                with open(filepath, 'r+') as f:
                    lines = f.readlines()

                    if(lines[0].startswith(mac)): #first mac address they used
                        line_found = True
                        for i, line in enumerate(lines):
                            data = line.split()
                            temp = data[1]
                            if(temp == "true"):
                                alert = True
                                alertMacAddress = data[0]
                                response_data['alertMacAddress'] = alertMacAddress
                    else:
                        for i, line in enumerate(lines):
                            if(line.startswith(mac)):
                                line_found = True
                    if(not line_found):
                        newMac = mac + " true\n"
                        lines.append(newMac)
                    f.seek(0)
                    for line in lines:
                        f.write(line)
            else:
                with open(filepath, 'a') as f:
                    line = mac + " false\n"
                    f.write(line)

            response_data['alert'] = alert

            request_ok("ALERT_MAC_ADDRESS")
            respond(request, True, "ALERT_MAC_ADDRESS Successful", response_data)
        else:
            request_unauthorized("ALERT_MAC_ADDRESS")
            send_unauthorized_lecturer_response(request)
