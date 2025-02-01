# 22-5-team3-FastAPI

## 🗳️ 스누보트(SNUvote)는 어떤 서비스인가요?   
- 학내 자체적으로 전자 투표를 진행할 수 있는 시스템 구축을 제안하고자 합니다.
- 학생들이 자유롭게 의견을 나눌 수 있는 커뮤니티 기능도 포함합니다.


## 🧩 워크플로우 
사진

## 👨‍💻 프로젝트 참여자 

| <img width="300" alt="signup" src="https://github.com/user-attachments/assets/693d3964-7c98-4093-92c2-747b32f73cda"> | <img width="300" alt="signup" src="https://github.com/user-attachments/assets/78034d67-c4f2-4951-bbbf-36cc67be889c"> | <img width="300" alt="signup" src="https://github.com/user-attachments/assets/1ff80434-8fe5-4af9-9ff4-fbcccd60e714"> | <img width="300" alt="signup" src="https://github.com/user-attachments/assets/2d4226e1-9178-4f07-a5bd-c6483df43dd8"> | 
| --- | --- | --- | --- |
| <b> [김재민(odumag99)](https://github.com/odumag99) - 팀장</b> | <b>[김동규(morecleverer)](https://github.com/morecleverer)</b> | <b>[오정윤(nyunn2)](https://github.com/nyunn2) </b>| <b>[정희우(huiwoo1010)](https://github.com/huiwoo1010) </b>|
| <center>FastAPI</center> | <center>FastAPI</center> | <center>Android</center> | <center>Android</center> | 


- 김재민
  - 팀장 역할 수행 및 일정 관리
  - 데이터베이스 총 관리
  - 소셜 로그인 구현
  - 투표 참여 및 댓글 api 구현
- 김동규
  - 앱 디자인 설계
  - CI/CD 설계
  - 사용자 로그인, 투표 리스트 조회, 유저 페이지 api 구현
- 오정윤
  - 회원 가입 구현
  - 투표 리스트 조회 기능 구현
  - 투표 생성 및 참여, 회원 페이지 구현
  - 댓글 기능 구현
- 정희우
  - 사용자 로그인 페이지 및 자동 로그인 구현
  - 소셜 계정 연동 및 로그인, 로그아웃 구현
  - 투표 리스트 페이지네이션 구현
   
## 기술 스택
### 🖥️ 백엔드
### 💻 개발 언어
  - #### python
```js
fastapi = "^0.115.0"  // Python 기반 비동기 웹 프레임워크
uvicorn = "^0.30.6"  // ASGI 서버 (FastAPI 실행용)
sqlalchemy = "^2.0.35"  // ORM (Object Relational Mapper)
alembic = "^1.13.3"  // 데이터베이스 마이그레이션 도구
email-validator = "^2.2.0"  // 이메일 형식 검증 라이브러리
pydantic-settings = "^2.5.2"  // 환경 변수 및 설정 관리
cryptography = "^43.0.1"  // 암호화 및 보안 관련 기능 제공
python-jose = "^3.3.0"  // JWT 및 JOSE(JSON Object Signing and Encryption) 구현
python-multipart = "^0.0.17"  // 멀티파트 폼 데이터 처리 (파일 업로드 등)
social-auth-core = "^4.5.4"  // 소셜 로그인 및 인증 기능 제공
aiomysql = "^0.2.0"  // MySQL 비동기 드라이버
python-dotenv = "^1.0.1"  // .env 파일을 사용한 환경 변수 로드
boto3 = "^1.36.2"  // AWS SDK for Python (S3 등 AWS 서비스 연동)
bcrypt = "^4.2.1"  // 비밀번호 해싱 라이브러리
httpx = "^0.28.1"  // 비동기 HTTP 클라이언트 (Requests 대체)
```
<br>

### 📱 안드로이드
### 💻 개발 언어
  - #### Kotlin
### 프레임워크, 라이브러리
 - Android SDK & Jetpack
```js
`androidx.core:core-ktx` (`1.15.0`) // Kotlin 확장 기능 제공
`androidx.appcompat:appcompat` (`1.7.0`) // 구형 버전과의 호환성 유지
`androidx.swiperefreshlayout:swiperefreshlayout` (`1.1.0`) // 새로고침
```
- Jetpack 아키텍처 컴포넌트
```js
`androidx.lifecycle:lifecycle-livedata-ktx` (`2.6.1`) // LiveData를 통한 데이터 관리
`androidx.navigation:navigation-fragment-ktx` (`2.8.3`) // Jetpack Navigation (Fragment 간 이동)
`androidx.navigation:navigation-runtime-ktx` (`2.8.5`)
`androidx.navigation:navigation-ui-ktx` (`2.5.3`)
```
- 네트워크 통신
```js
`com.squareup.retrofit2:retrofit` (`2.11.0`) // REST API 요청 처리
`com.squareup.retrofit2:converter-gson` (`2.11.0`) // JSON 파싱 지원
`com.squareup.okhttp3:okhttp` (`4.10.0`) // HTTP 클라이언트
`com.squareup.okhttp3:logging-interceptor` (`4.10.0`) // HTTP 요청 로그 확인
```
- 의존성 주입 (Dependency Injection)
```js
`com.google.dagger:hilt-android` (`2.52`) // 구글 공식 DI 라이브러리
`com.google.dagger:hilt-android-compiler` (`2.52`) // Hilt 코드 생성
```
- 이미지 로딩
```js
`com.github.bumptech.glide:glide` (`4.16.0`) // 이미지 로딩
```
- 소셜 로그인
```js
`com.kakao.sdk:v2-user` (`2.18.0`) // 카카오 로그인
`com.navercorp.nid:oauth` (`5.4.0`) // 네이버 로그인
```

<br>   

## 프로젝트 뷰
### 1. 회원가입 페이지
<img width="200" alt="signup" src="https://github.com/user-attachments/assets/336bb886-571f-40e6-ab94-2a00935996bd" />

- 회원가입  

<br>

### 2. 로그인 페이지
<img width="200" alt="signup" src="https://github.com/user-attachments/assets/59039575-8705-4e0b-993a-0d36dc7ab80e">

- ID, PW로 로그인을 하거나 소셜계정으로 로그인합니다

<br>

### 3. 진행 중인 투표 페이지
<img width="200" alt="signup" src="https://github.com/user-attachments/assets/c8bcc9da-d3f9-4ea7-b1a7-1c1e07054ba3">

- 최신 순으로 진행 중인 투표 리스트를 확인할 수 있습니다.

<br>

### 4. HOT 투표 페이지
<img width="200" alt="signup" src="https://github.com/user-attachments/assets/fc81df9b-6706-4f9a-8359-ffdc67c98e40">

- 투표 참여자 수가 5명 이상인 투표 리스트를 확인할 수 있습니다.   
### 5. 종료된 투표 페이지
<img width="200" alt="signup" src="https://github.com/user-attachments/assets/7d4a3283-413d-4cae-b062-4e6897c82dbb">

- 마감된 투표 리스트를 확인 할 수 있습니다.

<br>

### 6. 투표 상세정보 페이지
| <img width="200" alt="signup" src="https://github.com/user-attachments/assets/4a3cbd26-bcda-4df6-9567-c5c6eb5d5663"> | <img width="200" alt="signup" src="https://github.com/user-attachments/assets/ef29d6de-93b6-4b05-8547-34957bead300"> |
| --- | --- |
| <center>진행 중인 투표</center> | <center>종료된 투표</center> |

- 투표 제목, 투표 설명, 투표 설정값을 확인할 수 있습니다.
- 댓글을 달 수 있습니다.
- 진행 중인 투표의 경우 투표 참여가 가능합니다. (참여코드가 필요할 수 있습니다)
- 종료된 투표의 경우 투표 결과를 확인할 수 있습니다.

<br>

### 7. 투표 생성 페이지
<img width="200" alt="signup" src="https://github.com/user-attachments/assets/ed703d48-a88b-4e17-ac63-790ef1471dcf">

- 사진, 제목, 설명, 투표 선택지, 투표 설정값, 마감 시간을 설정할 수 있습니다.

<br>

### 8. 회원 정보 페이지
| <img width="200" alt="signup" src="https://github.com/user-attachments/assets/7b057a87-d073-434e-ad58-3776624bf5cd"> | <img width="200" alt="signup" src="https://github.com/user-attachments/assets/c2a7e007-d2c0-41c4-b91d-c0f92f626e74"> | <img width="200" alt="signup" src="https://github.com/user-attachments/assets/9175ee40-96c1-4ad6-98b9-7b1abaf335d1"> | <img width="200" alt="signup" src="https://github.com/user-attachments/assets/4e855548-dcc9-468d-8e13-3baca20d0856"> |
| --- | --- | --- | --- |
| <center>회원 페이지</center> | <center>비밀번호 변경</center> | <center>내가 참여한 투표</center> | <center>내가 만든 투표</center> |

- 비밀번호 변경이 가능합니다.
- 내가 참여한 투표, 내가 만든 투표를 확인할 수 있습니다.
- 소셜 계정 연동이 가능합니다.
- 회원 탈퇴, 로그아웃이 가능합니다.

<br>   

## 추가
- docker + github action으로 CI/CD 구현
- 소수 정예로 똘똘 뭉친 기획팀
