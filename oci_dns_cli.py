import json
import subprocess
import os
from utils import get_proxy, get_debug_mode

from oci_dns_util import OciPublicIpUtil


class OciPublicIpCliUtil(OciPublicIpUtil):

    def __init__(self, private_ip_id):
        self.private_ip_id = private_ip_id
        self.compartment_id = None
        self.public_ip_id = None

    def get_private_ip_by_id(self):
        sucess, result = OciPrivateIpGetCmd(self.private_ip_id).exec()
        if sucess:
            self.compartment_id = result["compartment-id"]
        return sucess, result

    def get_public_ip_by_private_ip_id(self):
        sucess, result = OciPublicIpGetCmd(self.private_ip_id).exec()
        if sucess:
            self.public_ip_id = result["id"]
        return sucess, result

    def delete_public_ip(self):
        if not self.public_ip_id:
            print("Public ip id not set, use get_public_ip_by_private_ip_id first")
            return False, None
        return OciPublicIpDeleteCmd(self.public_ip_id).exec()

    def create_public_ip(self):
        if not self.compartment_id:
            print("Compartment id not set, use get_public_ip_by_private_ip_id first")
            return False, None
        return OciPublicIpCreateCmd(
            self.compartment_id,
            self.private_ip_id,
        ).exec()


class Cmd:

    def __init__(self):

        self.cmd = None
        self.output = None

    def exec(self):
        return self.__exec_cmd()

    # exec shell command and return result string
    def __exec_cmd(self):
        print(self.cmd)
        PROXY = get_proxy()
        if PROXY:
            complete_process = subprocess.run(
                self.cmd, capture_output=True, shell=True, env={"https_proxy": PROXY}
            )
            result_str = complete_process.stdout.decode("utf-8")
        else:
            result_str = subprocess.getoutput(self.cmd)
        if get_debug_mode():
            print(result_str)
        return self.parse_result(result_str)

    def get_output(self, result):
        print("abstract method")

    # parse shell result

    def parse_result(self, result_str):
        if "ServiceError" not in result_str:
            # parse result as json
            try:
                result = json.loads(result_str)
                return True, self.get_output(result)
            except:
                print(f"json Error: {result}")
                return False, None
        else:
            print(f"ServiceError: {result}")
            return False, None


class OciPrivateIpGetCmd(Cmd):
    def __init__(self, private_ip_id):
        self.cmd = f"oci network private-ip get --private-ip-id {private_ip_id}"

    def get_output(self, result):
        # if data in result
        if "data" in result:
            return result["data"]
        else:
            return None


class OciPublicIpGetCmd(Cmd):
    def __init__(self, private_ip_id):
        self.cmd = f"oci network public-ip get --private-ip-id {private_ip_id}"

    def get_output(self, result):
        # if data in result
        if "data" in result:
            return result["data"]
        else:
            return None

    def parse_result(self, result_str):
        if "ServiceError" not in result_str:
            print(f"Success: {result_str}")
            # parse result as json
            return True, self.get_output(json.loads(result_str))
        else:
            print(f"ServiceError: {result_str}")
            if "404" in result_str:
                return True, None
            else:
                return False, None


class OciPublicIpDeleteCmd(Cmd):
    def __init__(self, public_ip_id):
        self.public_ip_id = public_ip_id
        self.cmd = (
            f"echo y | oci network public-ip delete --public-ip-id {public_ip_id}"
        )

    def parse_result(self, result_str):
        if "ServiceError" not in result_str:
            print(f"Success: {result_str}")
            # parse result as json
            return True, self.public_ip_id
        else:
            print(f"ServiceError: {result_str}")
            return False, self.public_ip_id


# create
class OciPublicIpCreateCmd(Cmd):
    def __init__(self, compartment_id, private_ip_id):
        self.cmd = f"oci network public-ip create -c {compartment_id} --private-ip-id {private_ip_id} --lifetime EPHEMERAL"

    def get_output(self, result):
        # if data in result
        if "data" in result:
            return True, result["data"]
        else:
            return False, None
