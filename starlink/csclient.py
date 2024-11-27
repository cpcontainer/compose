"""
NCOS communication module for Containerized SDK applications.

Copyright (c) 2022 Cradlepoint, Inc. <www.cradlepoint.com>.  All rights reserved.

This file contains confidential information of CradlePoint, Inc. and your use of
this file is subject to the CradlePoint Software License Agreement distributed with
this file. Unauthorized reproduction or distribution of this file is subject to civil and
criminal penalties.

Working Methods:

.get(path)
.decrypt(path)
.put(path, value)
.post(path, value)
.log(value)
.alert(value)
.patch(config) -- NCOS 7.22.20+

"""


import json
import os
import re
import select
import socket
import threading
import logging.handlers
import signal
import sys

try:
    import traceback
except ImportError:
    traceback = None


class SdkCSException(Exception):
    pass


class CSClient(object):
    """
    The CSClient class is the NCOS SDK mechanism for communication between apps and the router tree/config store.
    Instances of this class communicate with the router using either an explicit socket or with http method calls.

    Apps running locally on the router use a socket on the router to send commands from the app to the router tree
    and to receive data (JSON) from the router tree.

    Apps running remotely use the requests library to send HTTP method calls to the router and to receive data from
    the router tree. This allows one to use an IDE to run and debug the application on a the computer. Although,
    there are limitations with respect to the device hardware access (i.e. serial, USB, etc.).
    """
    END_OF_HEADER = b"\r\n\r\n"
    STATUS_HEADER_RE = re.compile(b"status: \w*")
    CONTENT_LENGTH_HEADER_RE = re.compile(b"content-length: \w*")
    MAX_PACKET_SIZE = 8192
    RECV_TIMEOUT = 2.0

    _instances = {}

    @classmethod
    def is_initialized(cls):
        return cls in cls._instances

    def __new__(cls, *na, **kwna):
        """ Singleton factory (with subclassing support) """
        if not cls.is_initialized():
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]

    def __init__(self, app_name, init=False):
        self.app_name = app_name
        self.ncos = '/var/mnt/sdk' in os.getcwd()  # Running in NCOS
        handlers = [logging.StreamHandler()]
        if self.ncos:
            handlers.append(logging.handlers.SysLogHandler(address='/dev/log'))
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s: %(message)s', datefmt='%b %d %H:%M:%S',
                            handlers=handlers)
        self.logger = logging.getLogger(app_name)
        if not init:
            return

    def get(self, base, query='', tree=0):
        """
        Constructs and sends a get request to retrieve specified data from a device.

        The behavior of this method is contextual:
            - If the app is installed on (and executed from) a device, it directly queries the router tree to retrieve the
              specified data.
            - If the app running remotely from a computer it calls the HTTP GET method to retrieve the specified data.

        Args:
            base: String representing a path to a resource on a router tree,
                  (i.e. '/config/system/logging/level').
            value: Not required.
            query: Not required.
            tree: Not required.

        Returns:
            A dictionary containing the response (i.e. {"success": True, "data:": {}}

        """
        cmd = "get\n{}\n{}\n{}\n".format(base, query, tree)
        return self._dispatch(cmd).get('data')

    def decrypt(self, base, query='', tree=0):
        """
        Constructs and sends a decrypt/get request to retrieve specified data from a device.

        The behavior of this method is contextual:
            - If the app is installed on (and executed from) a device, it directly queries the router tree to retrieve the
              specified data.
            - If the app running remotely from a computer it calls the HTTP GET method to retrieve the specified data.

        Args:
            base: String representing a path to a resource on a router tree,
                  (i.e. '/config/system/logging/level').
            value: Not required.
            query: Not required.
            tree: Not required.

        Returns:
            A dictionary containing the response (i.e. {"success": True, "data:": {}}

        """
        cmd = "decrypt\n{}\n{}\n{}\n".format(base, query, tree)
        return self._dispatch(cmd).get('data')

    def put(self, base, value='', query='', tree=0):
        """
        Constructs and sends a put request to update or add specified data to the device router tree.

        The behavior of this method is contextual:
            - If the app is installed on(and executed from) a device, it directly updates or adds the specified data to
              the router tree.
            - If the app running remotely from a computer it calls the HTTP PUT method to update or add the specified
              data.

        Args:
            base: String representing a path to a resource on a router tree,
                  (i.e. '/config/system/logging/level').
            value: Not required.
            query: Not required.
            tree: Not required.

        Returns:
            A dictionary containing the response (i.e. {"success": True, "data:": {}}
        """
        value = json.dumps(value)
        cmd = "put\n{}\n{}\n{}\n{}\n".format(base, query, tree, value)
        return self._dispatch(cmd)

    def post(self, base, value='', query=''):
        """
        Constructs and sends a post request to update or add specified data to the device router tree.

        The behavior of this method is contextual:
            - If the app is installed on(and executed from) a device, it directly updates or adds the specified data to
              the router tree.
            - If the app running remotely from a computer it calls the HTTP POST method to update or add the specified
              data.

        Args:
            base: String representing a path to a resource on a router tree,
                  (i.e. '/config/system/logging/level').
            value: Not required.
            query: Not required.

        Returns:
            A dictionary containing the response (i.e. {"success": True, "data:": {}}
        """
        value = json.dumps(value)
        cmd = f"post\n{base}\n{query}\n{value}\n"
        return self._dispatch(cmd)

    def patch(self, value):
        """
        Constructs and sends a patch request to update or add specified data to the device router tree.
        The behavior of this method is contextual:
            - If the app is installed on(and executed from) a device, it directly updates or adds the specified data to
              the router tree.
            - If the app running remotely from a computer it calls the HTTP PUT method to update or add the specified
              data.
        Args:
            value: list containing dict of add/changes, and list of removals:  [{add},[remove]]
        Returns:
            A dictionary containing the response (i.e. {"success": True, "data:": {}}
        """

        if 'linux' in sys.platform:
            if value[0].get("config"):
                adds = value[0]
            else:
                adds = {"config": value[0]}
            adds = json.dumps(adds)
            removals = json.dumps(value[1])
            cmd = f"patch\n{adds}\n{removals}\n"
            return self._dispatch(cmd)
        else:
            # Running in a computer so use http to send the put to the device.
            import requests
            device_ip, username, password = self._get_device_access_info()
            device_api = 'http://{}/api/'.format(device_ip)

            try:
                response = requests.patch(device_api,
                                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                                        auth=self._get_auth(device_ip, username, password),
                                        data={"data": '{}'.format(json.dumps(value))})
            except (requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError):
                print("Timeout: device at {} did not respond.".format(device_ip))
                return None

            return json.loads(response.text)

    def delete(self, base, query=''):
        """
        Constructs and sends a delete request to delete specified data to the device router tree.

        The behavior of this method is contextual:
            - If the app is installed on(and executed from) a device, it directly deletes the specified data to
              the router tree.
            - If the app running remotely from a computer it calls the HTTP DELETE method to update or add the specified
              data.


        Args:
            base: String representing a path to a resource on a router tree,
                  (i.e. '/config/system/logging/level').
            query: Not required.

        Returns:
            A dictionary containing the response (i.e. {"success": True, "data:": {}}
        """
        cmd = "delete\n{}\n{}\n".format(base, query)
        return self._dispatch(cmd)

    def log(self, value=''):
        """
        Adds an INFO log to the device SYSLOG.

        Args:
        value: String text for the log.

        Returns:
        None
        """
        if self.ncos:
            # Running in NCOS so write to the logger
            self.logger.info(value)
        elif 'linux' in sys.platform:
            # Running in Linux (container?) so write to stdout
            with open('/dev/stdout', 'w') as log:
                log.write(f'{self.app_name}: {value}\n')
        else:
            # Running in a computer so just use print for the log.
            print(value)
        
    def alert(self, value=''):
        """
        Constructs and sends a custom alert to NCM for the device. Apps calling this method must be running
        on the target device to send the alert. If invoked while running on a computer, then only a log is output.

        Args:

        app_name: String name of your application.
        value: String to displayed for the alert.

        Returns:
            Success: None
            Failure: An error
        """
        cmd = "alert\n{}\n{}\n".format(self.app_name, value)
        return self._dispatch(cmd)
        
    def _get_auth(self, device_ip, username, password):
        # This is only needed when the app is running in a computer.
        # Returns the proper HTTP Auth for the global username and password.
        # Digest Auth is used for NCOS 6.4 and below while Basic Auth is
        # used for NCOS 6.5 and up.
        import requests
        from http import HTTPStatus

        use_basic = False
        device_api = 'http://{}/api/status/product_info'.format(device_ip)

        try:
            response = requests.get(device_api, auth=requests.auth.HTTPBasicAuth(username, password))
            if response.status_code == HTTPStatus.OK:
                use_basic = True

        except:
            use_basic = False

        if use_basic:
            return requests.auth.HTTPBasicAuth(username, password)
        else:
            return requests.auth.HTTPDigestAuth(username, password)

    def _safe_dispatch(self, cmd):
        """Send the command and return the response."""
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect('/var/tmp/cs.sock')
            sock.sendall(bytes(cmd, 'ascii'))
            return self._receive(sock)

    def _dispatch(self, cmd):
        errmsg = None
        result = ""
        try:
            result = self._safe_dispatch(cmd)
        except Exception as err:
            # ignore the command error, continue on to next command
            errmsg = "dispatch failed with exception={} err={}".format(type(err), str(err))
        if errmsg is not None:
            self.log(errmsg)
            pass
        return result

    def _safe_receive(self, sock):
        sock.settimeout(self.RECV_TIMEOUT)
        data = b""
        eoh = -1
        while eoh < 0:
            # In the event that the config store times out in returning data, lib returns
            # an empty result. Then again, if the config store hangs for 2+ seconds,
            # the app's behavior is the least of our worries.
            try:
                buf = sock.recv(self.MAX_PACKET_SIZE)
            except socket.timeout:
                return {"status": "timeout", "data": None}
            if len(buf) == 0:
                break
            data += buf
            eoh = data.find(self.END_OF_HEADER)

        status_hdr = self.STATUS_HEADER_RE.search(data).group(0)[8:]
        content_len = self.CONTENT_LENGTH_HEADER_RE.search(data).group(0)[16:]
        remaining = int(content_len) - (len(data) - eoh - len(self.END_OF_HEADER))

        # body sent from csevent_xxx.sock will have id, action, path, & cfg
        while remaining > 0:
            buf = sock.recv(self.MAX_PACKET_SIZE)  # TODO: This will hang things as well.
            if len(buf) == 0:
                break
            data += buf
            remaining -= len(buf)
        body = data[eoh:].decode()
        try:
            result = json.loads(body)
        except json.JSONDecodeError as e:
            # config store receiver doesn't give back
            # proper json for 'put' ops, body
            # contains verbose error message
            # so putting the error msg in result
            result = body.strip()
        return {"status": status_hdr.decode(), "data": result}

    def _receive(self, sock):
        errmsg = None
        result = ""
        try:
            result = self._safe_receive(sock)
        except Exception as err:
            # ignore the command error, continue on to next command
            errmsg = "_receive failed with exception={} err={}".format(type(err), str(err))
        if errmsg is not None:
            self.log(errmsg)
        return result


def clean_up_reg(signal, frame):
    """
    When 'cppython remote_port_forward.py' gets a SIGTERM, config_store_receiver.py doesn't
    clean up registrations. Even if it did, the comm module can't rely on an external service
    to clean up.
    """
    EventingCSClient('CSClient').stop()
    sys.exit(0)


signal.signal(signal.SIGTERM, clean_up_reg)
