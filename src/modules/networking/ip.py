import requests, json


def get_public_ipv4() -> str:
    response = requests.get("https://icanhazip.com")
    ipv4 = response.text.strip()
    return ipv4


def main():
    get_public_ipv4()


if __name__ == "__main__":
    main()
