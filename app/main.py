import asyncio
import json
import logging
import os

from cloudflare import fetch_dns_records, update_dns_record
from ddns import DDNS
from ip import IP_SERVICES, fetch_current_ip


def load_config():
    if not os.path.exists('config.json'):
        print("Select IP service provider:")
        print("1. International (icanhazip.com)")
        print("2. China Mainland (3322.net / neu6.edu.cn)")
        while True:
            choice = input("Enter your choice (1/2): ").strip()
            if choice == "1":
                ip_service = "international"
                break
            elif choice == "2":
                ip_service = "china"
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")

        configs = []
        while True:
            config = {
                "email": input("Enter your email: "),
                "global_api_key": input("Enter your global API key: "),
                "dns_record_name": input("Enter your DNS record name (e.g., sub.domain.com): ")
            }
            configs.append(config)

            another = input("Do you want to add another record? (y/n): ")
            if another.lower().startswith('n'):
                break

        data = {
            "ip_service": ip_service,
            "records": configs
        }
        with open('config.json', 'w') as f:
            json.dump(data, f, indent=2)
    else:
        with open('config.json') as f:
            data = json.load(f)

    return data["ip_service"], data["records"]


async def update_dns_records(ddns_objects: list[DDNS], ip_service: str):
    ip_cache: dict[str, str] = {}

    for ddns in ddns_objects:
        for record_type, dns_record in ddns.dns_records.items():
            try:
                if record_type not in ip_cache:
                    try:
                        ip_cache[record_type] = await fetch_current_ip(ip_service, record_type)
                    except Exception as e:
                        raise Exception(f"Failed to get {record_type} IP: {e}")
                current_ip = ip_cache[record_type]

                current_records = await fetch_dns_records(
                    ddns.headers, ddns.domain_id, ddns.dns_record_name
                )
                record_content = current_records[record_type].content

                if current_ip != record_content:
                    logging.info(
                        f"{ddns.dns_record_name} ({record_type}) - "
                        f"Current IP {current_ip} differs from DNS record {record_content}. Updating..."
                    )
                    response = await update_dns_record(
                        ddns.headers,
                        ddns.dns_record_name,
                        ddns.domain_id,
                        dns_record.id,
                        record_type,
                        current_ip
                    )
                    logging.info(f"{ddns.dns_record_name} ({record_type}) - Updated successfully: {response}")
                else:
                    logging.info(f"{ddns.dns_record_name} ({record_type}) - IP address unchanged.")

            except Exception as e:
                logging.error(f"Error updating {ddns.dns_record_name} ({record_type}): {e}")


async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    ip_service, configs = load_config()
    logging.info(f"Using IP service: {ip_service} ({IP_SERVICES[ip_service]})")

    ddns_objects = []
    for config in configs:
        ddns = DDNS(config["email"], config["global_api_key"], config["dns_record_name"])
        try:
            await ddns.init_dns_record()
            logging.info(
                f"Initialized {config['dns_record_name']} with record types: {ddns.record_types}"
            )
        except Exception as e:
            raise Exception(f"Failed to initialize {config['dns_record_name']}: {e}")
        ddns_objects.append(ddns)
    logging.info("All DNS records initialized successfully.")

    while True:
        await update_dns_records(ddns_objects, ip_service)
        await asyncio.sleep(60)


if __name__ == '__main__':
    asyncio.run(main())
