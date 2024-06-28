import requests

VERSION = 'v0.0.0'

LATEST_RELEASE_URL = 'https://api.github.com/repos/richiehowelll/cat-lock/releases/latest'


def is_update_available() -> bool:
    response = requests.get(LATEST_RELEASE_URL)

    # Check if the request was successful
    if response.status_code == 200:
        release_data = response.json()
        if release_data.get("name") != VERSION:
            return True

    return False
