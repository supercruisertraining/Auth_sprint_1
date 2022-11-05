from urllib.parse import urljoin

import requests

from tests.functional.settings import test_config

while True:
    try:
        res = requests.get(urljoin(test_config.API_BASE_URL, test_config.API_HEALTH_CHECK_PATH))
        if res.ok:
            break
    except Exception:
        pass
