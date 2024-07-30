import os
import sys
from utils import get_config
from cloudflare import Cloudflare
from cloudflare.types.dns import ARecord


def get_client_from_env():

    if not os.environ.get("CLOUDFLARE_EMAIL"):
        print("set CLOUDFLARE_EMAIL in env")
        sys.exit(1)

    if not os.environ.get("CLOUDFLARE_API_KEY"):
        print("set CLOUDFLARE_API_KEY in env")
        sys.exit(1)

    client = Cloudflare(
        # This is the default and can be omitted
        api_email=os.environ.get("CLOUDFLARE_EMAIL"),
        # This is the default and can be omitted
        api_key=os.environ.get("CLOUDFLARE_API_KEY"),
    )
    return client


# update ip
def update_cf_ip(client: Cloudflare, ip_address: str):

    if not os.environ.get("CLOUDFLARE_DNS_RECORD_IDS"):
        print("set dns_record_ids in env")
        sys.exit(1)

    if not os.environ.get("CLOUDFLARE_ZONE_ID"):
        print("set zone_id in env")
        sys.exit(1)

    dns_record_ids = os.environ.get("CLOUDFLARE_DNS_RECORD_IDS").split(",")
    for dns_record_id in dns_record_ids:
        dns_record = client.dns.records.get(
            dns_record_id,
            zone_id=os.environ.get("CLOUDFLARE_ZONE_ID"),
        )
        # if dns record is ARecord
        if dns_record and dns_record.type == "A":
            if dns_record.content == ip_address:
                print(f"dns record {dns_record.name} already be {ip_address}")
                continue
            print(f"updating {dns_record.name} to {ip_address}")
            client.dns.records.update(
                dns_record_id,
                zone_id=os.environ.get("CLOUDFLARE_ZONE_ID"),
                type=dns_record.type,
                name=dns_record.name,
                content=ip_address,
                comment=dns_record.comment,
                proxied=dns_record.proxied,
                ttl=dns_record.ttl,
                tags=dns_record.tags,
            )
        else:
            print(f"dns record {dns_record.id} is not ARecord")


if __name__ == "__main__":
    get_config()
    client = get_client_from_env()
    # get ip from arg
    if len(sys.argv) < 2:
        print("usage: python cf_dns_api.py <ip_address>")
        sys.exit(1)
    ip_address = sys.argv[1]
    update_cf_ip(client, ip_address)
