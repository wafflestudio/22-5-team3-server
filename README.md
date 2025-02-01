# 22-5-team3-FastAPI

## 🗳️ 스누보트(SNUvote)는 어떤 서비스인가요?   
- 학내 자체적으로 전자 투표를 진행할 수 있는 시스템 구축을 제안하고자 합니다.
- 학생들이 자유롭게 의견을 나눌 수 있는 커뮤니티 기능도 포함합니다.


## 🧩 워크플로우 
사진

## 👨‍💻 프로젝트 참여자 

| image/odumag99.png | image/morecleverer.jpg | image/nyunn2.png | image/huiwoo1010.png | 
| --- | --- | --- | --- |
| <b> [김재민(odumag99)](https://github.com/odumag99) - 팀장</b> | <b>[김동규(morecleverer)](https://github.com/morecleverer)</b> | <b>[오정윤(nyunn2)](https://github.com/nyunn2) </b>| <b>[정희우(huiwoo1010)](https://github.com/huiwoo1010) </b>|
| <center>FastAPI</center> | <center>FastAPI</center> | <center>Android</center> | <center>Android</center> | 
   
## 기술 스택
### 🖥️ 백엔드
```js
fastapi = "^0.115.0"  // Python 기반 비동기 웹 프레임워크
uvicorn = "^0.30.6"  // ASGI 서버 (FastAPI 실행용)
sqlalchemy = "^2.0.35"  // ORM (Object Relational Mapper)
pymysql = "^1.1.1"  // MySQL 데이터베이스 드라이버
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
image/1_signup.jpg
- 회원가입  
### 2. 로그인 페이지
image/2_login.jpg
- ID, PW로 로그인을 하거나 소셜계정으로 로그인합니다
### 3. 진행 중인 투표 페이지
image/3_ongoing.jpg
- 최신 순으로 진행 중인 투표 리스트를 확인할 수 있습니다.
### 4. HOT 투표 페이지
- 투표 참여자 수가 5명 이상인 투표 리스트를 확인할 수 있습니다.   
### 5. 종료된 투표 페이지
image/5_ended.jpg
- 마감된 투표 리스트를 확인 할 수 있습니다.
### 6. 투표 상세정보 페이지
| image/6_voteinfo.jpg | image/6_endedvoteinfo.jpg |
| --- | --- |
| 진행 중인 투표 | 종료된 투표 |

- 투표 제목, 투표 설명, 투표 설정값을 확인할 수 있습니다.
- 댓글을 달 수 있습니다.
- 진행 중인 투표의 경우 투표 참여가 가능합니다. (참여코드가 필요할 수 있습니다)
- 종료된 투표의 경우 투표 결과를 확인할 수 있습니다.
### 7. 투표 생성 페이지
image/7_createvote.jpg
- 사진, 제목, 설명, 투표 선택지, 투표 설정값, 마감 시간을 설정할 수 있습니다.
### 8. 회원 정보 페이지
image/8_userpage.png
- 비밀번호 변경이 가능합니다.
- 내가 참여한 투표, 내가 만든 투표를 확인할 수 있습니다.
- 소셜 계정 연동이 가능합니다.
- 회원 탈퇴, 로그아웃이 가능합니다.

<br>   

## 추가
- docker + github action으로 CI/CD 구현
- 소수 정예로 똘똘 뭉친 기획팀
