import os
import sys
from utils import get_config
from cloudflare import Cloudflare
from cloudflare.types.dns import ARecord

from cf_dns_api import get_client_from_env


if __name__ == "__main__":
    get_config()
    client = get_client_from_env()
    if len(sys.argv) < 3:
        print("usage: python cf_dns_api.py <old_ip_address> <new_ip_address>")
        sys.exit(1)
    old_ip_address = sys.argv[1]
    new_ip_address = sys.argv[2]
    zones = client.zones.list()
    for zone in zones:
        records = client.dns.records.list(zone_id=zone.id, extra_query={"content.contains": old_ip_address, "type": "A"})
        # records = client.dns.records.get(zone_id=zone.id, extra_query={"content.contains": old_ip_address})
        if records.success > 0 and len(records.result) > 0:
            for dns_record in records.result:
                if dns_record and dns_record.type == "A" and dns_record.content == old_ip_address:
                    print(f"Updating {dns_record.name} to {new_ip_address}")
                    dns_record.content = new_ip_address
                    # result = client.dns.records.update(zone_id=zone.id, record_id=dns_record.id, record=dns_record)
                    result = client.dns.records.update(
                        dns_record.id,
                        zone_id=zone.id,
                        type=dns_record.type,
                        name=dns_record.name,
                        content=new_ip_address,
                        comment=dns_record.comment,
                        proxied=dns_record.proxied,
                        ttl=dns_record.ttl,
                        tags=dns_record.tags,
                    )
                    if result:
                        print(f"Updated {dns_record.name} to {new_ip_address}")
                    else:
                        print(f"Failed to update {dns_record.name} to {new_ip_address}")

        # else:

            # print(records)
    # records = client.dns.records.get(
    #         zone_id=os.environ.get("CLOUDFLARE_ZONE_ID"),
    #     )