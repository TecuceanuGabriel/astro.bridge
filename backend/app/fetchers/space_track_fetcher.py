import logging

import requests
from datetime import datetime

from app.core.db import get_db
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

    def fetch_tle(self, norad_cat_id):
        url = f"{self.BASE_URL}/class/tle_latest/NORAD_CAT_ID/{norad_cat_id}/orderby/ORDINAL%20asc/format/json"
        try:
            res = self.session.get(url, timeout=10)
            if res.status_code != 200:
                raise Exception(f"Failed to fetch TLE: {res.text}")

            data = res.json()
            if not data:
                return None

            return res.json()[0]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch TLE: {e}")

    def fetch_active_satellites(self, limit=20):
        url = f"{self.BASE_URL}/class/satcat/DECAY/null-val/orderby/INTLDES%20asc/limit/{limit}/format/json"
        try:
            res = self.session.get(url, timeout=10)
            if res.status_code != 200:
                raise Exception(f"Failed to fetch active satellites: {res.text}")

            return res.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch active satellites: {e}")

    def sync_TLEs(self, db):
        try:
            satellites = self.fetch_active_satellites()

            logging.info(len(satellites))

            for sat in satellites:
                satellite_obj = (
                    db.query(Satellite)
                    .filter_by(norad_cat_id=sat.get("NORAD_CAT_ID"))
                    .first()
                )

                if not satellite_obj:
                    satellite_obj = Satellite(
                        intldes=sat.get("INTLDES"),
                        norad_cat_id=sat.get("NORAD_CAT_ID"),
                        object_type=sat.get("OBJECT_TYPE"),
                        satname=sat.get("SATNAME"),
                        country=sat.get("COUNTRY"),
                        launch=sat.get("LAUNCH"),
                        site=sat.get("SITE"),
                        decay=sat.get("DECAY"),
                        period=sat.get("PERIOD"),
                        inclination=sat.get("INCLINATION"),
                        apogee=sat.get("APOGEE"),
                        perigee=sat.get("PERIGEE"),
                        comment=sat.get("COMMENT"),
                        commentcode=sat.get("COMMENTCODE"),
                        rcsvalue=sat.get("RCSVALUE"),
                        rcs_size=sat.get("RCS_SIZE"),
                        file=sat.get("FILE"),
                        launch_year=sat.get("LAUNCH_YEAR"),
                        launch_num=sat.get("LAUNCH_NUM"),
                        launch_piece=sat.get("LAUNCH_PIECE"),
                        current=sat.get("CURRENT"),
                        object_name=sat.get("OBJECT_NAME"),
                        object_id=sat.get("OBJECT_ID"),
                        object_number=sat.get("OBJECT_NUMBER"),
                    )
                    db.add(satellite_obj)
                    db.flush()  # get ID before committing

                # Fetch and store latest TLE
                tle_data = self.fetch_tle(satellite_obj.norad_cat_id)
                if tle_data:
                    existing_tle = (
                        db.query(TLE).filter_by(norad_cat_id=tle_data.get("NORAD_CAT_ID")).first()
                    )
                    if existing_tle:
                        continue

                    tle_obj = TLE(
                        satellite_id=satellite_obj.id,
                        comment=tle_data.get("COMMENT"),
                        originator=tle_data.get("ORIGINATOR"),
                        norad_cat_id=tle_data.get("NORAD_CAT_ID"),
                        object_name=tle_data.get("OBJECT_NAME"),
                        object_type=tle_data.get("OBJECT_TYPE"),
                        classification_type=tle_data.get("CLASSIFICATION_TYPE"),
                        intldes=tle_data.get("INTLDES"),
                        epoch=datetime.strptime(
                            tle_data.get("EPOCH"), "%Y-%m-%d %H:%M:%S"
                        ),
                        epoch_microseconds=tle_data.get("EPOCH_MICROSECONDS"),
                        mean_motion=tle_data.get("MEAN_MOTION"),
                        eccentricity=tle_data.get("ECCENTRICITY"),
                        inclination=tle_data.get("INCLINATION"),
                        ra_of_asc_node=tle_data.get("RA_OF_ASC_NODE"),
                        arg_of_pericenter=tle_data.get("ARG_OF_PERICENTER"),
                        mean_anomaly=tle_data.get("MEAN_ANOMALY"),
                        ephemeris_type=tle_data.get("EPHEMERIS_TYPE"),
                        element_set_no=tle_data.get("ELEMENT_SET_NO"),
                        rev_at_epoch=tle_data.get("REV_AT_EPOCH"),
                        bstar=tle_data.get("BSTAR"),
                        mean_motion_dot=tle_data.get("MEAN_MOTION_DOT"),
                        mean_motion_ddot=tle_data.get("MEAN_MOTION_DDOT"),
                        file=tle_data.get("FILE"),
                        tle_line0=tle_data.get("TLE_LINE0"),
                        tle_line1=tle_data.get("TLE_LINE1"),
                        tle_line2=tle_data.get("TLE_LINE2"),
                        object_id=tle_data.get("OBJECT_ID"),
                        object_number=tle_data.get("OBJECT_NUMBER"),
                        semimajor_axis=tle_data.get("SEMIMAJOR_AXIS"),
                        period=tle_data.get("PERIOD"),
                        apogee=tle_data.get("APOGEE"),
                        perigee=tle_data.get("PERIGEE"),
                        decayed=tle_data.get("DECAYED"),
                    )
                    db.add(tle_obj)

            db.commit()

        except Exception as e:
            logging.error(f"Failed to add TLE to database: {e}")
            db.rollback()
        finally:
            db.close()
