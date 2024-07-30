# Oracle VPS 服务自动更新 IP

## 功能

1. 自动判断丢包率并更换新的 Oracle VPS 公网地址（使用 [CLI](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/cliconcepts.htm) 或 [SDK](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/pythonsdk.htm)）
2. 新 IP 地址同步到 Cloudflare DNS

## 用法

```bash
# 查看帮助
python change_ip.py -h
# 获取当前 public ip 并测试丢包率
python change_ip.py
 # 仅获取 public ip
python change_ip.py -s
# 获取当前 public ip 并测试丢包率，如果丢包率大于30%，更换ip，失败重试 5 次
python change_ip.py -c -l 30 -r 5
```

## 依赖

1. [oci-python-sdk](https://github.com/oracle/oci-python-sdk) [文档](https://docs.oracle.com/en-us/iaas/tools/python/2.130.0/api/core/client/oci.core.VirtualNetworkClient.html)
2. [cloudflare-python](https://github.com/cloudflare/cloudflare-python) [文档](https://github.com/cloudflare/cloudflare-python/blob/main/api.md#dns)

## 参考

1. [OCI RESET APIs 文档](https://docs.oracle.com/en-us/iaas/api/#/en/iaas/20160918/PublicIp/)
