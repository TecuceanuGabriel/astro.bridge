import dis
from re import I
from sqlalchemy import (
    Column,
    String,
    Enum,
    Double,
    Boolean,
    DateTime,
    Date,
    ForeignKey,
    UniqueConstraint,
)

from sqlalchemy.dialects.mysql import (
    INTEGER,
    DECIMAL,
    FLOAT,
    BIGINT,
    SMALLINT,
)

from datetime import datetime

from app.core.db import Base


class Satellite(Base):
    __tablename__ = "satellites"

    id = Column(INTEGER(unsigned=True), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- SATCAT fields ---
    intldes = Column(String(12), nullable=False)
    norad_cat_id = Column(
        INTEGER(unsigned=True), unique=True, index=True, nullable=True
    )
    object_type = Column(String(12))
    satname = Column(String(25), nullable=False, index=True)
    country = Column(String(6), nullable=False)
    launch = Column(Date)
    site = Column(String(5))
    decay = Column(Date)

    period = Column(DECIMAL(12, 2))
    inclination = Column(DECIMAL(12, 2))
    apogee = Column(BIGINT(unsigned=True))
    perigee = Column(BIGINT(unsigned=True))

    comment = Column(String(32))
    commentcode = Column(SMALLINT(display_width=3, unsigned=True))

    rcsvalue = Column(INTEGER, default=0, nullable=False)
    rcs_size = Column(String(6))

    file = Column(SMALLINT(display_width=5, unsigned=True), default=0, nullable=False)

    launch_year = Column(
        SMALLINT(display_width=5, unsigned=True), default=0, nullable=False
    )
    launch_num = Column(
        SMALLINT(display_width=5, unsigned=True), default=0, nullable=False
    )
    launch_piece = Column(String(3), nullable=False)

    current = Column(Enum("Y", "N", name="current_status"), default="N", nullable=False)

    object_name = Column(String(25), nullable=False)
    object_id = Column(String(12), nullable=False)
    object_number = Column(INTEGER(unsigned=True))


class TLE(Base):
    __tablename__ = "tle_history"

    id = Column(INTEGER(unsigned=True), primary_key=True)
    fetched_at = Column(DateTime, default=datetime.utcnow, index=True)

    # --- Relationship to Satellite ---
    satellite_id = Column(
        INTEGER(unsigned=True),
        ForeignKey("satellites.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # --- TLE standard fields ---
    comment = Column(String(32), nullable=False)
    originator = Column(String(7), nullable=False)
    norad_cat_id = Column(INTEGER(unsigned=True), index=True)
    object_name = Column(String(25), nullable=False)
    object_type = Column(String(12))
    classification_type = Column(String(1), nullable=False)
    intldes = Column(String(8))

    epoch = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)
    epoch_microseconds = Column(INTEGER(unsigned=True), nullable=False, default=0)

    mean_motion = Column(Double, nullable=False, default=0)
    eccentricity = Column(Double, nullable=False, default=0)
    inclination = Column(Double, nullable=False, default=0)
    ra_of_asc_node = Column(Double, nullable=False, default=0)
    arg_of_pericenter = Column(Double, nullable=False, default=0)
    mean_anomaly = Column(Double, nullable=False, default=0)

    ephemeris_type = Column(
        SMALLINT(display_width=3, unsigned=True), nullable=False, default=0
    )
    element_set_no = Column(
        SMALLINT(display_width=5, unsigned=True), nullable=False, default=0
    )

    rev_at_epoch = Column(FLOAT, nullable=False, default=0)
    bstar = Column(Double, nullable=False, default=0)

    mean_motion_dot = Column(Double, nullable=False, default=0)
    mean_motion_ddot = Column(Double, nullable=False, default=0)

    file = Column(INTEGER(unsigned=True), nullable=False, default=0)

    tle_line0 = Column(String(27), nullable=False)
    tle_line1 = Column(String(71), nullable=False)
    tle_line2 = Column(String(71), nullable=False)

    object_id = Column(String(11))
    object_number = Column(INTEGER(unsigned=True))

    semimajor_axis = Column(DECIMAL(20, 3), nullable=False, default=0.000)

    period = Column(DECIMAL(20, 3))
    apogee = Column(DECIMAL(20, 3), nullable=False, default=0.000)
    perigee = Column(DECIMAL(20, 3), nullable=False, default=0.000)

    decayed = Column(SMALLINT(unsigned=True), default=0)

    # --- Constraints ---
    __table_args__ = (
        UniqueConstraint("satellite_id", "epoch", name="idx_tle_unique_per_satellite"),
    )


class RF(Base):
    __tablename__ = "rf"

    id = Column(INTEGER(unsigned=True), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Foreign key to satellite
    satellite_id = Column(
        INTEGER(unsigned=True), ForeignKey("satellites.id"), nullable=False
    )

    # SatNOGS Transmitter API fields
    uuid = Column(String(36), nullable=False, unique=True)  # UUID string
    description = Column(String(255), nullable=False)
    alive = Column(Boolean, nullable=False)
    type = Column(Enum("Transmitter", "Transceiver", "Transponder"), nullable=True)

    uplink_low = Column(BIGINT, nullable=True)
    uplink_high = Column(BIGINT, nullable=True)
    uplink_drift = Column(INTEGER, nullable=True)
    downlink_low = Column(BIGINT, nullable=True)
    downlink_high = Column(BIGINT, nullable=True)
    downlink_drift = Column(INTEGER, nullable=True)

    mode = Column(INTEGER, nullable=True)
    mode_id = Column(INTEGER, nullable=True)
    uplink_mode = Column(INTEGER, nullable=True)
    invert = Column(Boolean, default=False)
    baud = Column(FLOAT, nullable=True)

    norad_cat_id = Column(BIGINT, nullable=False, index=True)
    sat_id = Column(String(50), nullable=True)
    norad_follow_id = Column(BIGINT, nullable=True)

    status = Column(Enum("active", "inactive", "invalid"), nullable=True)

    updated = Column(DateTime, nullable=True)
    citation = Column(String(512), nullable=True)
    service = Column(String(100), nullable=True)

    iaru_coordination = Column(
        Enum("IARU Coordinated", "IARU Declined", "IARU Uncoordinated", "N/A"),
        nullable=True,
    )
    iaru_coordination_url = Column(String(200), nullable=True)

    frequency_violation = Column(Boolean, default=False)
    unconfirmed = Column(Boolean, default=False)

    # constraints
    __table_args__ = (
        UniqueConstraint("satellite_id", name="idx_rf_unique_per_satellite"),
    )
