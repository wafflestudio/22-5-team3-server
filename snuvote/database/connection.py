from typing import Any, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from snuvote.database.settings import DB_SETTINGS


class DatabaseManager:
    def __init__(self):
        # TODO pool 이 뭘까요?
        # pool_recycle 은 뭐고 왜 28000으로 설정해두었을까요?
        self.engine = create_engine(
            DB_SETTINGS.url,
            pool_recycle=28000,
            pool_pre_ping=True,
        )
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)


# TODO 아래 함수를 이용해서 Session 종속성을 주입받을 수 있습니다.
# 이렇게 했을 때의 장점은 무엇일까요? 다른 방법은 없을까요?
# 한 번 생각해보세요.
def get_db_session() -> Generator[Session, Any, None]:
    session = DatabaseManager().session_factory()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
