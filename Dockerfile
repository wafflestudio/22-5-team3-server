# syntax=docker/dockerfile:1
FROM python:3.11
# 작업 디렉토리 설정
WORKDIR /src
# Poetry 설치
RUN pip install poetry
# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt update && apt install -y \
    default-libmysqlclient-dev \
    git && \
    apt clean
# 프로젝트 의존성 파일 복사
COPY pyproject.toml poetry.lock ./
# Poetry를 사용하여 의존성 설치
RUN poetry install --no-dev
# 애플리케이션 코드 복사
COPY snuvote ./snuvote
# 애플리케이션 실행 명령
CMD ["poetry", "run", "uvicorn", "snuvote.main:app", "--host", "0.0.0.0", "--port", "8000"]