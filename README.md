# idea-log

## 소개

이 앱은 간단한 메모 앱입니다. 사용자는 Google 계정 또는 guest 계정으로 로그인해 간단한 메모를 남길 수 있습니다.

## 서버 설치 방법

### flask 서버의 경우

```bash
bin/command/one-time-setup
```

위 커맨드를 실행하여 이 레포지토리를 위한 커맨드가 담긴 디렉토리를 환경변수에 추가합니다.

```bash
flask-server-setup
```

위 커맨드를 실행하여, Google 계정을 통한 로그인을 지원하기 위한 Client ID, Client Secret을 입력합니다.

```bash
sudo docker-compose up --build
```

위 커맨드를 실행하여 서버를 실행합니다.

### 새 GCP 프로젝트에 Cloud Functions/App Engine으로 배포하는 경우

1. 새로운 GCP 프로젝트 생성 및 설정

```bash
./bin/setup-new-gcp-project.sh <FLASK_SECRET_KEY>
```

2. 그 GCP 프로젝트의 사용자 인증 정보에서 OAuth 클라이언트 ID 생성 후, 그 비밀번호를 JSON 파일로 다운받아 루트 디렉토리로 이동

3. 현재 디렉토리 내 파일들을 현재 GCP 프로젝트로 배포

- Cloud Functions

```bash
gcloud builds submit --config cloudbuild-gcf.yaml .
```

- App Engine

```bash
gcloud builds submit --config cloudbuild-gae.yaml .
```


## 기술상의 특징

1. 플랫폼 독립성: Docker Compose를 이용해 시스템 환경에 구애받지 않고 웹 서비스를 실행할 수 있습니다. 사용자는 단 한 번의 쉘 스크립트 커맨드로 서비스를 간편하게 설치 및 실행할 수 있습니다.

2. 안정적인 웹 서비스 스택: Flask를 웹 애플리케이션 프레임워크로, Gunicorn을 WSGI 서버로, 그리고 Nginx를 웹 서버로 사용하였습니다. 이러한 조합은 웹 서비스의 안정성을 높이며, HTTPS를 통해 보안상의 이점을 확보하였습니다.

3. 데이터베이스 관리: SQLAlchemy ORM을 사용하였고 DAO 패턴으로 구현하여, 데이터베이스와 효율적으로 상호 작용 하도록 했고 데이터베이스 접근 코드를 내부 로직으로부터 분리해 코드의 가독성을 높였습니다.

4. 코드 품질 관리: YAPF, shfmt, pylint, mypy와 같은 도구들을 활용하여, 코드 포맷팅 및 타입 힌트의 적절성을 지속적으로 체크하는 CI/CD 파이프라인을 구축하였습니다.
