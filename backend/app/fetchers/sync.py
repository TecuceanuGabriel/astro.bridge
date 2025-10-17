import os
import logging
from datetime import datetime
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from requests.models import LocationParseError
from sqlalchemy.orm.session import Session

from app.fetchers.satnogs_fetcher import SatNOGSFetcher
from app.fetchers.space_track_fetcher import SpaceTrackFetcher
from app.core.schemas import Satellite, TLE, RF


class Syncer:
    space_track_username = os.environ.get("SPACE_TRACK_USERNAME")
    space_track_password = os.environ.get("SPACE_TRACK_PASSWORD")
    satnogs_api_key = os.environ.get("SATNOGS_API_KEY")

    def __init__(self, db: Session):
        self.db = db

        self.satnogs_fetcher = SatNOGSFetcher(self.satnogs_api_key)
        self.space_track_fetcher = SpaceTrackFetcher(
            self.space_track_username, self.space_track_password
        )

    def sync(self):
        self.sync_satellites()

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(self.sync_TLEs): "TLEs",
                executor.submit(self.sync_RF): "RFs",
            }

            for future in as_completed(futures):
                name = futures[future]
                try:
                    future.result()
                    logging.info(f"{name} sync completed successfully.")
                except Exception as e:
                    logging.error(f"Error syncing {name}: {e}")

        self.db.close()

    def sync_satellites(self):
        try:
            satellites = self.space_track_fetcher.fetch_active_satellites()

            for sat in satellites:
                satellite_obj = (
                    self.db.query(Satellite)
                    .filter_by(norad_cat_id=sat.get("NORAD_CAT_ID"))
                    .first()
                )

                if satellite_obj:
                    continue

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
                self.db.add(satellite_obj)

            self.db.commit()

        except Exception as e:
            logging.info(f"Error syncing satellite data: {e}")
            self.db.rollback()
            self.db.close()

    def sync_TLEs(self):
        try:
            tles = self.space_track_fetcher.fetch_tles()

            tle_groups = defaultdict(list)
            for tle in tles:
                tle_groups[int(tle["NORAD_CAT_ID"])].append(tle)

            for norad_cat_id, tles in tle_groups.items():
                satellite = (
                    self.db.query(Satellite)
                    .filter_by(norad_cat_id=norad_cat_id)
                    .first()
                )

                if not satellite:
                    continue

                for tle in tles:
                    old_tle = (
                        self.db.query(TLE)
                        .filter_by(satellite_id=satellite.id, epoch=tle.get("EPOCH"))
                        .first()
                    )

                    if old_tle:
                        continue

                    tle_obj = TLE(
                        satellite_id=satellite.id,
                        comment=tle.get("COMMENT"),
                        originator=tle.get("ORIGINATOR"),
                        norad_cat_id=tle.get("NORAD_CAT_ID"),
                        object_name=tle.get("OBJECT_NAME"),
                        object_type=tle.get("OBJECT_TYPE"),
                        classification_type=tle.get("CLASSIFICATION_TYPE"),
                        intldes=tle.get("INTLDES"),
                        epoch=datetime.strptime(tle.get("EPOCH"), "%Y-%m-%d %H:%M:%S"),
                        epoch_microseconds=tle.get("EPOCH_MICROSECONDS"),
                        mean_motion=tle.get("MEAN_MOTION"),
                        eccentricity=tle.get("ECCENTRICITY"),
                        inclination=tle.get("INCLINATION"),
                        ra_of_asc_node=tle.get("RA_OF_ASC_NODE"),
                        arg_of_pericenter=tle.get("ARG_OF_PERICENTER"),
                        mean_anomaly=tle.get("MEAN_ANOMALY"),
                        ephemeris_type=tle.get("EPHEMERIS_TYPE"),
                        element_set_no=tle.get("ELEMENT_SET_NO"),
                        rev_at_epoch=tle.get("REV_AT_EPOCH"),
                        bstar=tle.get("BSTAR"),
                        mean_motion_dot=tle.get("MEAN_MOTION_DOT"),
                        mean_motion_ddot=tle.get("MEAN_MOTION_DDOT"),
                        file=tle.get("FILE"),
                        tle_line0=tle.get("TLE_LINE0"),
                        tle_line1=tle.get("TLE_LINE1"),
                        tle_line2=tle.get("TLE_LINE2"),
                        object_id=tle.get("OBJECT_ID"),
                        object_number=tle.get("OBJECT_NUMBER"),
                        semimajor_axis=tle.get("SEMIMAJOR_AXIS"),
                        period=tle.get("PERIOD"),
                        apogee=tle.get("APOGEE"),
                        perigee=tle.get("PERIGEE"),
                        decayed=tle.get("DECAYED"),
                    )

                    self.db.add(tle_obj)

            self.db.commit()

        except Exception as e:
            logging.error(f"Failed to sync data: {e}")
            self.db.rollback()

    def sync_RF(self):
        try:
            rf_data = self.satnogs_fetcher.fetch_rfs()

            rf_groups = defaultdict(list)
            for rf in rf_data:
                rf_groups[int(rf["norad_cat_id"])].append(rf)

            for norad_cat_id, rfs in rf_groups.items():
                satellite = (
                    self.db.query(Satellite)
                    .filter_by(norad_cat_id=norad_cat_id)
                    .first()
                )

                if not satellite:
                    continue

                for rf in rfs:
                    old_rf = self.db.query(RF).filter_by(uuid=rf["uuid"]).first()

                    if old_rf:
                        continue

                    updated = None
                    if rf.get("updated"):
                        try:
                            updated = datetime.fromisoformat(
                                rf["updated"].replace("Z", "+00:00")
                            )
                        except ValueError:
                            raise ValueError(
                                f"Invalid datetime format for updated: {rf['updated']}"
                            )

                    rf_obj = RF(
                        satellite_id=satellite.id,
                        uuid=rf.get("uuid"),
                        description=rf.get("description"),
                        alive=rf.get("alive"),
                        type=rf.get("type"),
                        uplink_low=rf.get("uplink_low"),
                        uplink_high=rf.get("uplink_high"),
                        uplink_drift=rf.get("uplink_drift"),
                        downlink_low=rf.get("downlink_low"),
                        downlink_high=rf.get("downlink_high"),
                        downlink_drift=rf.get("downlink_drift"),
                        mode=rf.get("mode"),
                        mode_id=rf.get("mode_id"),
                        uplink_mode=rf.get("uplink_mode"),
                        invert=rf.get("invert"),
                        baud=rf.get("baud"),
                        norad_cat_id=rf.get("norad_cat_id"),
                        sat_id=rf.get("sat_id"),
                        norad_follow_id=rf.get("norad_follow_id"),
                        status=rf.get("status"),
                        updated=updated,
                        citation=rf.get("citation"),
                        service=rf.get("service"),
                        iaru_coordination=rf.get("iaru_coordination"),
                        iaru_coordination_url=rf.get("iaru_coordination_url"),
                        frequency_violation=rf.get("frequency_violation"),
                        unconfirmed=rf.get("unconfirmed"),
                    )

                    self.db.add(rf_obj)

            self.db.commit()

        except Exception as e:
            logging.error(f"Failed to sync RF data: {e}")
            self.db.rollback()
