import json
import logging
import os
import time
from ddns import DDNS, IP_SERVICES


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


def update_dns_records(ddns_objects):
    for ddns in ddns_objects:
        try:
            record_content = ddns.get_record_content()
            current_ip = ddns.fetch_current_ip()
            if current_ip != record_content and current_ip is not None:
                logging.info(
                    f"{ddns.dns_record_name} - Current IP {current_ip} is different from DNS record {record_content}. Updating..."
                )
                ddns.update_dns_record(current_ip)
            else:
                logging.info(f"{ddns.dns_record_name} - IP address unchanged.")
        except Exception as e:
            logging.error(f"Error updating DNS record: {e}")


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    ip_service, configs = load_config()
    logging.info(f"Using IP service: {ip_service} ({IP_SERVICES[ip_service]})")

    ddns_objects = [
        DDNS(config["email"], config["global_api_key"], config["dns_record_name"], ip_service)
        for config in configs
    ]
    logging.info("DNS records initialized successfully.")

    while True:
        update_dns_records(ddns_objects)
        time.sleep(60)


if __name__ == '__main__':
    main()