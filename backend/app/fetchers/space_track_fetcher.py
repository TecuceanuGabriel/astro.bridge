import logging

import requests
from datetime import datetime

from app.core.schemas import Satellite, TLE


class SpaceTrackFetcher:
    BASE_URL = "https://www.space-track.org/basicspacedata/query"

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self._authenticate()

    def _authenticate(self):
        login_url = "https://www.space-track.org/ajaxauth/login"
        try:
            res = self.session.post(
                login_url,
                data={"identity": self.username, "password": self.password},
                timeout=10,
            )
            if res.status_code != 200:
                raise Exception(f"Failed to authenticate: {res.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to authenticate: {e}")

    def fetch_active_satellites(self, limit=20):
        url = f"{self.BASE_URL}/class/satcat/DECAY/null-val/orderby/INTLDES%20asc/format/json"
        try:
            res = self.session.get(url)
            if res.status_code != 200:
                raise Exception(f"Failed to fetch active satellites: {res.text}")

            return res.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch active satellites: {e}")

    def fetch_tles(self, limit=20):
        url = f"{self.BASE_URL}/class/tle_latest/ORDINAL/1/orderby/ORDINAL%20asc/format/json"
        try:
            res = self.session.get(url)
            if res.status_code != 200:
                raise Exception(f"Failed to fetch TLE: {res.text}")

            return res.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch TLE: {e}")
