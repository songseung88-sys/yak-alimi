# 약 알리미 — Play App Signing 및 사이드로드 전환 계획

기준: 2026-09-28

## 1. 현재 키 상태

### 과거 사이드로드 APK
V3.0.1 / V3.0.2 등 기존 직접 설치 APK의 서명 인증서 SHA-256:

`97:DB:85:3E:68:33:86:3A:C4:1B:C9:C1:AD:E9:3D:85:A9:DA:74:B1:82:5D:78:6F:8E:40:47:3F:14:0E:4A:E4`

### 현재 Google Play 업로드 키
Play Console에 AAB를 업로드하기 위해 새로 만든 upload key 인증서 SHA-256:

`E2:F4:61:A7:1A:34:24:D3:D4:78:3E:F2:45:69:9A:4F:72:91:12:8A:C8:58:33:65:B5:97:50:BE:16:33:52:AA`

현재 `yak-alimi-v3.0.3-play-signed.aab`는 이 upload key로 서명되어 있으며 JAR 서명 검증을 통과한다.

---

## 2. 권장 Play App Signing 전략

이 앱은 아직 Google Play 프로덕션에 배포된 적이 없는 신규 앱이므로 다음 구조로 진행한다.

1. Google Play Console에서 **Play App Signing 사용**
2. **Google이 앱 서명키(app signing key)를 생성·관리**하도록 선택
3. 개발자는 현재 준비된 **upload key**로 AAB를 서명해 업로드
4. Google Play는 실제 사용자에게 배포할 APK를 Google의 app signing key로 다시 서명

즉, upload key와 사용자 기기에 설치되는 최종 앱의 app signing key는 서로 다른 키다.

---

## 3. 기존 사이드로드 APK와의 관계

Android는 동일 패키지명의 앱을 업데이트할 때 서명 인증서 연속성을 확인한다.

따라서 과거 `97:DB:...` 인증서로 설치된 사이드로드 APK 위에, 향후 Google Play의 새로운 app signing key로 서명된 앱을 그대로 업데이트 설치할 수는 없다.

### 전환 방법
Google Play 내부/비공개 테스트를 처음 시작하는 시점에 개발용 사이드로드 앱을 제거한 뒤 Play Store에서 테스트 버전을 새로 설치한다.

주의: 약 알리미의 복용 기록·재고는 로컬 저장이므로 앱을 삭제하면 기존 테스트 데이터가 사라질 수 있다. Play 전환 직전에는 실제 중요한 데이터가 아니라 테스트용 데이터만 남겨두는 것을 권장한다.

---

## 4. 왜 지금은 이 전략이 합리적인가

- 아직 일반 사용자에게 Google Play 버전을 배포하지 않았음
- 기존 사이드로드 설치는 개발·검증 단계에 해당함
- Google Play 정식 배포가 시작된 뒤에는 Google의 app signing key가 계속 유지되므로 이후 Play 업데이트는 정상적으로 이어짐
- upload key를 분실하더라도 Google Play의 절차를 통해 upload key 재설정을 요청할 수 있음

---

## 5. 예외 — 기존 사이드로드 서명을 반드시 유지하고 싶은 경우

기존 `97:DB:...` 인증서의 **개인키가 들어 있는 원본 keystore**를 복구할 수 있다면, 첫 Play App Signing 설정 단계에서 기존 키를 app signing key로 사용하는 방안을 검토할 수 있다.

하지만 인증서 파일이나 APK만으로는 기존 개인키를 복원할 수 없다. 원본 keystore가 없다면 과거 사이드로드 서명과 완전한 연속성을 만드는 것은 불가능하다.

현재 출시 계획에서는 **Google 생성 app signing key + 별도 upload key** 전략을 기본안으로 사용한다.

---

## 6. 키 보안 원칙

- upload keystore는 GitHub 공개 저장소에 절대 커밋하지 않는다.
- keystore 비밀번호도 저장소, 문서, 이슈에 기록하지 않는다.
- keystore와 비밀번호는 서로 분리해 최소 2곳에 안전하게 백업한다.
- 공개 저장소에는 인증서 PEM 또는 SHA-256 fingerprint 같은 공개 정보만 올릴 수 있다.

---

## 7. Play 테스트 전환 체크리스트

- [ ] Play Console에서 앱 생성
- [ ] Play App Signing 활성화
- [ ] Google 생성 app signing key 선택
- [ ] upload certificate 등록/확인
- [ ] V3.0.3 signed AAB 업로드
- [ ] 내부 또는 비공개 테스트 릴리스 생성
- [ ] 기존 사이드로드 APK의 테스트 데이터가 삭제되어도 되는지 확인
- [ ] 기존 사이드로드 앱 제거
- [ ] Play Store 테스트 링크에서 앱 설치
- [ ] Play 설치본에서 알림/전체화면 권한/프리미엄/광고 재검증
- [ ] 이후 모든 테스트와 출시 검증은 가능하면 Play 설치본 기준으로 진행
