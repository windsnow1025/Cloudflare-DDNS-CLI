from request import send_request

IP_SERVICES = {
    "international": {
        "A": "https://ipv4.icanhazip.com/",
        "AAAA": "https://ipv6.icanhazip.com/"
    },
    "china": {
        "A": "https://ip.3322.net/",
        "AAAA": "https://speed.neu6.edu.cn/getIP.php"
    }
}


async def fetch_current_ip(ip_service, dns_record_type) -> str:
    url = IP_SERVICES[ip_service][dns_record_type]
    try:
        response: str = await send_request("GET", url)
        return response.strip()
    except Exception as e:
        raise Exception(f"Failed to get IP address: {e}")
