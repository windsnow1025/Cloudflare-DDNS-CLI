from cloudflare import fetch_domain_id, fetch_dns_records, Headers, DNSRecord


def get_domain_name(dns_record_name: str):
    return ".".join(dns_record_name.split(".")[-2:])


class DDNS:
    def __init__(self, email: str, global_api_key: str, dns_record_name: str):
        self.headers: Headers = Headers(x_auth_email=email, x_auth_key=global_api_key)
        self.dns_record_name: str = dns_record_name
        self.domain_id: str | None = None
        self.dns_records: dict[str, DNSRecord] = {}

    async def init_dns_record(self):
        self.domain_id = await fetch_domain_id(
            self.headers,
            get_domain_name(self.dns_record_name)
        )
        self.dns_records = await fetch_dns_records(
            self.headers,
            self.domain_id,
            self.dns_record_name
        )

    @property
    def record_types(self) -> list[str]:
        return list(self.dns_records.keys())