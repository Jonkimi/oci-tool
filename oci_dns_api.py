import oci
import sys
import os
import json
from utils import get_config, get_debug_mode, replace_underscore_with_dash

from oci.core import VirtualNetworkClient
from oci.response import Response
from oci.exceptions import ServiceError

from oci_dns_util import OciPublicIpUtil


class OciPublicIpApiUtil(OciPublicIpUtil):

    def __init__(self, private_ip_id):
        self.private_ip_id = private_ip_id
        self.compartment_id = None
        self.public_ip_id = None
        self.no_public_ip = False
        self.client = get_client_from_env()

    def get_private_ip_by_id(self):
        sucess, result = get_private_ip_by_id(self.client, self.private_ip_id)
        if sucess:
            self.compartment_id = result["compartment-id"]
        return sucess, result

    def get_public_ip_by_private_ip_id(self):
        sucess, result = get_public_ip_by_private_ip_id(self.client, self.private_ip_id)
        if sucess:
            if result:
                self.public_ip_id = result["id"]
            else:
                self.no_public_ip = True
        return sucess, result

    def delete_public_ip(self):
        if self.no_public_ip:
            print("No public ip found, nothing to delete")
            return True, None
        if not self.public_ip_id:
            print("Public ip id not set, use get_public_ip_by_private_ip_id first")
            return False, None
        success, result = delete_public_ip(self.client, self.public_ip_id)
        if success:
            self.public_ip_id = None
            self.no_public_ip = True
        return success, result

    def create_public_ip(self):
        if not self.compartment_id:
            print("Compartment id not set, use get_private_ip_by_id first")
            return False, None
        sucess, result = create_public_ip(
            self.client, self.compartment_id, self.private_ip_id
        )
        if sucess:
            print(f"create_public_ip {self.compartment_id} {self.private_ip_id}")
            self.public_ip_id = result["id"]
            self.no_public_ip = False
        return sucess, result


def get_client_from_env():
    config = oci.config.from_file(file_location="~/.oci/config", profile_name="DEFAULT")
    # to mock oci cli, add the client type: Oracle-PythonCLI/version, version come from oci-cli version `oci -v`
    config["additional_user_agent"] = "Oracle-PythonCLI/{}".format("3.2.0")
    if get_debug_mode():
        print(config)

    # Initialize service client with default config file
    core_client = VirtualNetworkClient(config)
    return core_client


def get_private_ip_by_id(core_client: VirtualNetworkClient, private_ip_id):
    if not private_ip_id:
        print("private_ip_id is required")
        return False, None
    try:
        response = core_client.get_private_ip(private_ip_id)
        if get_debug_mode():
            print(response.data)
        return True, replace_underscore_with_dash(json.loads(str(response.data)))
    except ServiceError as e:
        print(f"ServiceError: {e}")
        # exception_data = json.loads(str(e))
        if e.status == 404:
            return True, None
        return False, None


def get_public_ip_by_private_ip_id(core_client: VirtualNetworkClient, private_ip_id):

    if not private_ip_id:
        print("private_ip_id is required")
        return False, None
    try:
        response: Response = core_client.get_public_ip_by_private_ip_id(
            oci.core.models.GetPublicIpByPrivateIpIdDetails(private_ip_id=private_ip_id)
        )
        if get_debug_mode():
            print(response.data)
        return True, replace_underscore_with_dash(json.loads(str(response.data)))
    except ServiceError as e:
        print(f"ServiceError: {e}")
        # exception_data = json.loads(str(e))
        if e.status == 404:
            return True, None
        return False, None


def delete_public_ip(core_client: VirtualNetworkClient, public_ip_id):
    try:
        response = core_client.delete_public_ip(public_ip_id)
        if get_debug_mode():
            print(response.headers)
        return True, public_ip_id
    except ServiceError as e:
        print(f"ServiceError: {e}")
        return False, public_ip_id


def create_public_ip(core_client: VirtualNetworkClient, compartment_id, private_ip_id):
    try:
        print(f"create_public_ip {compartment_id} {private_ip_id}")
        response = core_client.create_public_ip(
            oci.core.models.CreatePublicIpDetails(
                compartment_id=compartment_id,
                private_ip_id=private_ip_id,
                lifetime="EPHEMERAL",
            )
        )
        if get_debug_mode():
            print(response.data)
        return True, replace_underscore_with_dash(json.loads(str(response.data)))
    except ServiceError as e:
        print(f"ServiceError: {e}")
        return False, None


if __name__ == "__main__":
    get_config()
    client = get_client_from_env()

    private_ip_id = os.getenv("OCI_PRIVATE_IP_ID")
    _, public_ip = get_public_ip_by_private_ip_id(client, private_ip_id)
    print(public_ip["id"])
