from dataclasses import dataclass

from request import send_request


@dataclass
class DNSRecord:
    id: str
    type: str
    content: str


@dataclass
class Headers:
    x_auth_email: str
    x_auth_key: str


def convert_headers_to_dict(headers: Headers) -> dict[str, str]:
    return {
        "X-Auth-Email": headers.x_auth_email,
        "X-Auth-Key": headers.x_auth_key,
        "Content-Type": "application/json"
    }


async def fetch_domain_id(headers: Headers, domain_name: str) -> str:
    url = "https://api.cloudflare.com/client/v4/zones"
    try:
        response = await send_request("GET", url, headers=convert_headers_to_dict(headers))
    except Exception as e:
        raise Exception(f"Failed to retrieve domain ID: {e}")
    for domain in response["result"]:
        if domain["name"] == domain_name:
            return domain["id"]
    raise Exception(f"Domain {domain_name} not found.")


async def fetch_dns_records(
        headers: Headers, domain_name_id: str, dns_record_name: str
) -> dict[str, DNSRecord]:
    url = f"https://api.cloudflare.com/client/v4/zones/{domain_name_id}/dns_records?name={dns_record_name}"
    try:
        response = await send_request("GET", url, headers=convert_headers_to_dict(headers))
    except Exception as e:
        raise Exception(f"Failed to retrieve DNS records: {e}")
    records = response["result"]
    if not records:
        raise Exception(f"DNS record {dns_record_name} not found.")

    dns_records = {}
    for record in records:
        if record["type"] in ("A", "AAAA"):
            dns_records[record["type"]] = DNSRecord(
                id=record["id"],
                type=record["type"],
                content=record["content"]
            )

    if not dns_records:
        raise Exception(f"No A or AAAA records found for {dns_record_name}.")

    return dns_records


async def update_dns_record(
        headers: Headers,
        dns_record_name: str,
        domain_id: str,
        dns_record_id: str,
        dns_record_type: str,
        new_ip: str,
) -> dict:
    url = f"https://api.cloudflare.com/client/v4/zones/{domain_id}/dns_records/{dns_record_id}"
    data = {
        "type": dns_record_type,
        "name": dns_record_name,
        "content": new_ip,
        "ttl": 1,
        "proxied": False
    }
    return await send_request("PUT", url, headers=convert_headers_to_dict(headers), data=data)
