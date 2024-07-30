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
        self.client = get_client_from_env()

    def get_public_ip_by_private_ip_id(self):
        sucess, result = get_public_ip_by_private_ip_id(self.client, self.private_ip_id)
        if sucess:
            self.compartment_id = result["compartment-id"]
        return sucess, result

    def delete_public_ip(self):
        if not self.public_ip_id:
            print("Public ip id not set, use get_public_ip_by_private_ip_id first")
            return False, None
        return delete_public_ip(self.client, self.public_ip_id)

    def create_public_ip(self):
        if not self.compartment_id:
            print("Compartment id not set, use get_public_ip_by_private_ip_id first")
            return False, None
        return create_public_ip(self.client, self.private_ip_id, self.compartment_id)


def get_client_from_env():
    config = oci.config.from_file(file_location="~/.oci/config", profile_name="DEFAULT")
    # to mock oci cli, add the client type: Oracle-PythonCLI/version, version come from oci-cli version `oci -v`
    config["additional_user_agent"] = "Oracle-PythonCLI/{}".format("3.2.0")
    if get_debug_mode():
        print(config)

    # Initialize service client with default config file
    core_client = VirtualNetworkClient(config)
    return core_client


def get_public_ip_by_private_ip_id(core_client: VirtualNetworkClient, private_ip_id):

    if not private_ip_id:
        print("private_ip_id is required")
        return None
    try:
        response: Response = core_client.get_public_ip_by_private_ip_id(
            oci.core.models.GetPublicIpByPrivateIpIdDetails(private_ip_id=private_ip_id)
        )
        if get_debug_mode():
            print(response.data)
        return True, replace_underscore_with_dash(json.loads(str(response.data)))
    except ServiceError as e:
        print(f"ServiceError: {e}")
        return False, None


def delete_public_ip(core_client: VirtualNetworkClient, public_ip_id):
    try:
        response = core_client.delete_public_ip(public_ip_id)
        if get_debug_mode():
            print(response.headers)
        return True, None
    except ServiceError as e:
        print(f"ServiceError: {e}")
        return False, None


def create_public_ip(core_client: VirtualNetworkClient, compartment_id, private_ip_id):
    try:
        response = core_client.create_public_ip(
            oci.core.models.CreatePublicIpDetails(compartment_id=compartment_id, private_ip_id=private_ip_id)
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
