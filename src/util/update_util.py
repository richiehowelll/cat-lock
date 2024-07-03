import requests

VERSION = 'v1.0.1'

LATEST_RELEASE_URL = 'https://api.github.com/repos/richiehowelll/cat-lock/releases/latest'


def is_update_available() -> bool:
    response = requests.get(LATEST_RELEASE_URL)

    if response.status_code == 200:
        release_data = response.json()
        if release_data.get("name") != VERSION:
            return True

    return False
