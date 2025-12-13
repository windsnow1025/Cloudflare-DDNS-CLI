import logging

from util import send_request

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


class DDNS:
    def __init__(self, email: str, global_api_key: str, dns_record_name: str, ip_service: str):
        self.__headers = {
            "X-Auth-Email": email,
            "X-Auth-Key": global_api_key,
            "Content-Type": "application/json"
        }
        self.dns_record_name = dns_record_name
        self.ip_service = ip_service
        self.domain_id = None
        self.dns_record_id = None
        self.dns_record_type = None

    async def init_dns_record(self):
        self.domain_id = await self.__fetch_domain_id(
            self.__headers,
            self.__get_domain_name(self.dns_record_name)
        )
        self.dns_record_id, self.dns_record_type, _ = await self.__fetch_dns_record(
            self.__headers,
            self.domain_id,
            self.dns_record_name
        )

    async def update_dns_record(self, new_ip: str):
        url = f"https://api.cloudflare.com/client/v4/zones/{self.domain_id}/dns_records/{self.dns_record_id}"
        data = {
            "type": self.dns_record_type,
            "name": self.dns_record_name,
            "content": new_ip,
            "ttl": 1,
            "proxied": False
        }
        try:
            response = await send_request("PUT", url, headers=self.__headers, data=data)
            logging.info(f"DNS record updated successfully: {response}")
        except Exception as e:
            logging.error(f"Failed to update DNS record: {e}")

    async def get_record_content(self):
        _, _, record_content = await self.__fetch_dns_record(self.__headers, self.domain_id, self.dns_record_name)
        return record_content

    async def fetch_current_ip(self) -> str:
        url = IP_SERVICES[self.ip_service][self.dns_record_type]
        try:
            response: str = await send_request("GET", url)
            return response.strip()
        except Exception as e:
            raise Exception(f"Failed to get IP address: {e}")

    @staticmethod
    def __get_domain_name(dns_record_name: str):
        return ".".join(dns_record_name.split(".")[-2:])

    @staticmethod
    async def __fetch_domain_id(headers: dict[str, str], domain_name: str) -> str:
        url = "https://api.cloudflare.com/client/v4/zones"
        try:
            response = await send_request("GET", url, headers=headers)
        except Exception as e:
            raise Exception(f"Failed to retrieve domain ID: {e}")
        for domain in response["result"]:
            if domain["name"] == domain_name:
                return domain["id"]
        raise Exception(f"Domain {domain_name} not found.")

    @staticmethod
    async def __fetch_dns_record(
            headers: dict[str, str], domain_name_id: str, dns_record_name: str
    ) -> tuple[str, str, str]:
        url = f"https://api.cloudflare.com/client/v4/zones/{domain_name_id}/dns_records"
        try:
            response = await send_request("GET", url, headers=headers)
        except Exception as e:
            raise Exception(f"Failed to retrieve DNS record: {e}")
        for record in response["result"]:
            if record["name"] == dns_record_name:
                return record["id"], record["type"], record["content"]
        raise Exception(f"DNS record {dns_record_name} not found.")
