import os
from utils import *
import oci_dns_cli
import oci_dns_api
import cf_dns_api
import oci_dns_util
import time


DEBUG = False
PROXY = None


def save_ip(ip_address, display_name, dry_run=False):
    if dry_run:
        return
    with open("ip.txt", "w") as f:
        f.write(f"{ip_address} {display_name}")


def recreate_public_ip(
    oci_dns_util: oci_dns_api.OciPublicIpUtil,
    loss_rate,
    retry_count,
    dry_run,
):
    cf_client = cf_dns_api.get_client_from_env()
    try_count = 0
    while try_count < retry_count:
        success, ip_address = oci_dns_util.delete_public_ip()
        if success:
            print(f"Delete public ip {ip_address} Success")
            time.sleep(30)
            # create public ip
            success, result = oci_dns_util.create_public_ip()
            if success:
                new_public_ip_id = result["id"]
                new_ip_address = result["ip-address"]
                new_display_name = result["display-name"]
                if new_ip_address != ip_address:
                    print(
                        f"Create new ip {new_ip_address} {new_display_name} {new_public_ip_id}"
                    )
                    # save "ip_address display_name" to file ip.txt
                    save_ip(new_ip_address, new_display_name, dry_run)

                    if is_good_ip(new_ip_address, loss_rate):
                        print(f"good ip {new_ip_address}, update to cloudflare")
                        cf_dns_api.update_cf_ip(cf_client, new_ip_address)
                        break
                    else:
                        print(f"bad new ip {new_ip_address}, try again")
                else:
                    print("new ip is same as old")

            else:
                print(f"Create new ip Failed")
        else:
            print(f"Delete new ip Failed")
        try_count += 1
        if try_count > 0 and try_count <= retry_count:
            print(f"try count: {try_count}")
            time.sleep(120)
        else:
            print("Max try count reached, exit")
            break


if __name__ == "__main__":
    get_config()

    DEBUG = get_debug_mode()
    RECREATE = get_recreate_mode()
    PROXY = get_proxy()
    FORCE = False

    if PROXY:
        print(f"using proxy: {PROXY}")

    # get args from command line
    # -s --skip-check  skip check
    # -d --debug  debug mode
    # -c --create  recreate public ip
    # -r --retry-count  recreate try count, default 5
    # -l --loss-rate package loss rate threshold, default 30
    # -f --force  force recreate
    # --dry-run  dry run mode

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--skip-check",
        action="store_true",
        dest="skip_check",
        help="enable skipping check ip is good or not at startup",
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", dest="debug", help="enable debug print"
    )
    parser.add_argument(
        "-c",
        "--create",
        action="store_true",
        dest="create",
        help="enable the process of recreating based on package loss rate of current public ip",
    )
    parser.add_argument(
        "-r",
        "--retry-count",
        type=int,
        default=5,
        dest="retry_count",
        metavar="<retry_count>",
        help="recreate try count, default value is 5 times",
    )
    parser.add_argument(
        "-l",
        "--loss-rate",
        type=int,
        default=30,
        metavar="<loss_rate>",
        dest="loss_rate",
        help="package loss rate threshold of ip ping test, default value is 30(%%)",
    )

    parser.add_argument(
        "-f", "--force", action="store_true", dest="force", help="force recreate"
    )

    parser.add_argument(
        "--dry-run", action="store_true", dest="dry_run", help="dry run"
    )

    args = parser.parse_args()

    skip_check = False

    if args.skip_check:
        skip_check = True

    # 命令行配置覆盖配置文件
    if args.debug:
        print("debug mode")
        os.environ["DEBUG"] = "True"
        DEBUG = True

    if args.create:
        os.environ["RECREATE"] = "True"
        RECREATE = True
        # if skip_check:
        #     print(f"-s/--skip-check is disabled by -c/--create")

    if args.force:
        os.environ["RECREATE"] = "True"
        RECREATE = True
        FORCE = True
        print("force recreate")

    retry_count = 5
    if args.retry_count:
        retry_count = args.retry_count

    loss_rate = 30
    if args.loss_rate:
        loss_rate = args.loss_rate

    private_ip_id = os.environ.get("OCI_PRIVATE_IP_ID")

    # oci_dns_util = oci_dns_cli.OciPublicIpCliUtil(private_ip_id)
    if args.dry_run:
        print("dry run mode")
        oci_dns_util = oci_dns_util.OciPublicIpDryRunUtil()
    else:
        oci_dns_util = oci_dns_api.OciPublicIpApiUtil(private_ip_id)

    oci_dns_util.get_private_ip_by_id()
    time.sleep(10)
    success, result = oci_dns_util.get_public_ip_by_private_ip_id()
    if success:
        if result:
            public_ip_id = result["id"]
            ip_address = result["ip-address"]
            display_name = result["display-name"]
            compartment_id = result["compartment-id"]
            print(f"current public ip: {ip_address} {display_name}")
            recreate_flag = False

            if RECREATE:
                if not skip_check and not is_good_ip(
                    ip_address, loss_rate, dry_run=args.dry_run
                ):
                    print(f"current ip {ip_address} is bad, try to recreate")
                    recreate_flag = True
                else:
                    if FORCE:
                        recreate_flag = True
                    else:
                        print(f"skip recreate good ip {ip_address}")

            else:
                if skip_check:
                    print(f"skip check ip {ip_address}")
                elif not skip_check and not is_good_ip(
                    ip_address, loss_rate, dry_run=args.dry_run
                ):
                    print(f"current ip {ip_address} is bad, but skipping recreate")

            if recreate_flag:

                recreate_public_ip(
                    oci_dns_util,
                    loss_rate,
                    retry_count,
                    args.dry_run,
                )

        else:
            print("no public ip")
            recreate_public_ip(
                oci_dns_util,
                loss_rate,
                retry_count,
                args.dry_run,
            )

    else:
        print("get public ip failed")

    print("Done")
