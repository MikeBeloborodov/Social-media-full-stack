from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.routers.logic.settings import settings
from backend.routers.logic.schemas import *


# check True if you want to test a test database
# check False if you want to test the real database
Test_environment = True


SQLALCHEMY_TEST_DATABASE_URL = (f"postgresql://"
                            f"{settings.database_username}:"
                            f"{settings.database_password}@"
                            f"{settings.database_hostname}/"
                            f"{settings.database_name}_test")


engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)


TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# overridden db test session for sqlalchemy
def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()