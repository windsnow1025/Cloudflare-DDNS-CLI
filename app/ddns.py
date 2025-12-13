from cloudflare import fetch_domain_id, fetch_dns_record, Headers


def get_domain_name(dns_record_name: str):
    return ".".join(dns_record_name.split(".")[-2:])


class DDNS:
    def __init__(self, email: str, global_api_key: str, dns_record_name: str):
        self.headers: Headers = Headers(x_auth_email=email, x_auth_key=global_api_key)
        self.dns_record_name: str = dns_record_name
        self.domain_id: str | None = None
        self.dns_record_id: str | None = None
        self.dns_record_type: str | None = None

    async def init_dns_record(self):
        self.domain_id = await fetch_domain_id(
            self.headers,
            get_domain_name(self.dns_record_name)
        )
        dns_record = await fetch_dns_record(
            self.headers,
            self.domain_id,
            self.dns_record_name
        )
        self.dns_record_id = dns_record.id
        self.dns_record_type = dns_record.type
