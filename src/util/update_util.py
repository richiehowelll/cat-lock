import logging

import requests

VERSION = 'v1.1.0'

LATEST_RELEASE_URL = 'https://api.github.com/repos/richiehowelll/cat-lock/releases/latest'


def is_update_available() -> bool:
    try:
        response = requests.get(LATEST_RELEASE_URL)

        if response.status_code == 200:
            release_data = response.json()
            if release_data.get("name") != VERSION:
                return True
    except requests.exceptions.ConnectionError as e:
        logging.info(f'Failed to check for updates: {str(e)}')
        pass
    except Exception as e:
        logging.exception(f'Failed to check for updates: {str(e)}')
    return False
