import requests


class SpaceTrackFetcher:
    BASE_URL = "https://www.space-track.org/api/query"

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

    def fetch_tle(self, norad_cat_id):
        url = f"{self.BASE_URL}/class/tle_latest"
        params = {"NORAD_CAT_ID": norad_cat_id, "orderby": "ORDINAL asc"}
        try:
            res = self.session.get(url, params=params, timeout=10)
            if res.status_code != 200:
                raise Exception(f"Failed to fetch TLE: {res.text}")

            return res.json
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch TLE: {e}")

    def fetch_active_satellites(self):
        url = f"{self.BASE_URL}/class/satcat"
        params = {"DECAY": "null-val", "orderby": "NORAD_CAT_ID asc"}
        try:
            res = self.session.get(url, params=params, timeout=10)
            if res.status_code != 200:
                raise Exception(f"Failed to fetch active satellites: {res.text}")

            return res.json
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch active satellites: {e}")

    def sync_TLEs(self):
        satellites = self.fetch_active_satellites()
        for satellite in satellites:
            norad_cat_id = satellite["NORAD_CAT_ID"]
            tle = self.fetch_tle(norad_cat_id)
            # TODO: Save TLE to database
