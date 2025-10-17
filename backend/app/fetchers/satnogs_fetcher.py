import logging

import requests
from datetime import datetime

from app.core.schemas import RF


class SatNOGSFetcher:
    BASE_URL = "https://db-dev.satnogs.org/api"

    def __init__(self, api_key):
        self.api_key = api_key

    def fetch_rf(self, norad_cat_id):
        url = f"{self.BASE_URL}/transmitters/satellite__norad_cat_id={norad_cat_id}"
        token = f"Bearer {self.api_key}"

        try:
            res = requests.get(url, headers={"Authorization": token})
            if res.status_code != 200:
                raise Exception(f"SatNOGS API returned status code {res.status_code}")

            data = res.json()
            if not data:
                return None

            return data[0]
        except Exception as e:
            raise Exception(f"Error fetching RF data from SatNOGS: {e}")
