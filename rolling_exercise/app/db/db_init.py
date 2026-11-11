from app.db.database import Base, engine
from app.models.air_quality import AirQuality
from app.models.alert import Alert


def db_init():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()