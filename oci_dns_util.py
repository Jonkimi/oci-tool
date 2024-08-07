from abc import abstractmethod


class OciPublicIpUtil:

    @abstractmethod
    def get_private_ip_by_id(self) -> tuple[bool, dict]:
        pass

    @abstractmethod
    def get_public_ip_by_private_ip_id(self) -> tuple[bool, dict]:
        pass

    @abstractmethod
    def delete_public_ip(self) -> tuple[bool, dict]:
        pass

    @abstractmethod
    def create_public_ip(self) -> tuple[bool, dict]:
        pass


class OciPublicIpDryRunUtil:
    def get_public_ip_by_private_ip_id(self):
        print("get public ip by private ip id")

        return True, {
            "id": "id",
            "compartment-id": "compartment-id",
            "ip-address": "ip-address",
            "display-name": "display-name",
        }

    def delete_public_ip(self):
        print("delete public ip")

        return True, None

    def create_public_ip(self):
        print("create public ip")

        return True, {
            "id": "id",
            "compartment-id": "compartment-id",
            "ip-address": "new-ip-address",
            "display-name": "new-display-name",
        }
