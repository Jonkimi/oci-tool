import os
import re
import subprocess


def get_proxy():
    return os.environ.get("http_proxy")


def get_debug_mode():
    return os.environ.get("DEBUG", "False") == "True"


def get_recreate_mode():
    return os.environ.get("RECREATE", "False") == "True"


def get_config():
    # get config from .env file
    if os.path.exists(".env"):
        with open(".env") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                key, value = line.split("=")
                os.environ[key.strip()] = value.strip()


def ping_test(host, count=4, timeout=2):
    """
    使用 ping 命令测试网络连接，计算丢包率和平均延迟。

    Args:
        host (str): 目标主机 IP 地址或域名。
        count (int): 发送的 ping 包数量，默认值为 4。
        timeout (int): 每个 ping 包的超时时间，默认值为 2 秒。

    Returns:
        tuple: 包含丢包率和平均延迟的元组。
    TODO 此函数仅测试于 macOS 系统上，可能不兼容其他系统
    """

    DEBUG = os.environ.get("DEBUG", "False") == "True"

    # 执行 ping 命令
    command = ["ping", "-c", str(count), "-W", str(timeout), host]
    if DEBUG:
        print(" ".join(command))
    result = subprocess.run(command, capture_output=True, text=True)

    # 解析命令输出
    output = result.stdout

    if DEBUG:
        print(output)

    # 提取丢包率
    packet_loss_rate = float(re.search(r"(\d+\.\d+)% packet loss", output).group(1))

    # 提取平均往返时间
    average_rtt = float(re.search(r" = \d+\.\d+/(\d+\.\d+)/", output).group(1))

    return packet_loss_rate, average_rtt


def is_good_ip(ip_address, loss_rate_threshold=30, dry_run=False):
    """
    check ip address is good or not based on packet loss rate is less than 30%
    """

    if dry_run:
        print(f"{ip_address} package loss: 0%, avg rtt: 0ms")
        print(f"{ip_address} is good ip")
        return True
    packet_loss_rate, average_rtt = ping_test(ip_address, 20)

    print(f"{ip_address} package loss: {packet_loss_rate}%, avg rtt: {average_rtt}ms")

    if packet_loss_rate > loss_rate_threshold:
        print(f"{ip_address} is bad ip")
        return False
    return True


def replace_underscore_with_dash(input_dict):
    """
    replace underscore with dash, for example:
    input_dict = {"a_b": 1, "c_d": 2}
    output_dict = {"a-b": 1, "c-d": 2}
    ensure api data aligns with key names from cli output and web rest api
    """
    new_dict = {}
    for key, value in input_dict.items():
        new_key = key.replace("_", "-")
        new_dict[new_key] = value
    return new_dict
