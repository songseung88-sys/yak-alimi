# 약 알리미 최종 출시 전 체크리스트 — 2026-10-10

## 1. 현재 출시 후보
- [x] 앱 버전: 3.0.15
- [x] versionCode: 56
- [x] package: com.yakalimi.app
- [x] compileSdk / targetSdk: 36 / 36
- [x] Google Play Billing: 9.1.0
- [x] Google Mobile Ads SDK: 25.5.0
- [x] UMP: 4.0.0
- [x] 프로덕션 AdMob App ID / Banner ID 반영
- [x] 의견 보내기 Apps Script endpoint 반영
- [x] 업로드 키 서명 확인
- [x] 업로드 인증서 SHA-256: E2:F4:61:A7:1A:34:24:D3:D4:78:3E:F2:45:69:9A:4F:72:91:12:8A:C8:58:33:65:B5:97:50:BE:16:33:52:AA

## 2. Google Play 상품
### 프리미엄
- [x] Product ID: premium_unlock
- [x] 구매 옵션 ID: premium-lifetime
- [x] 한국 가격: ₩4,900
- [x] 구매 성공 테스트
- [x] 즉시 프리미엄 활성화 테스트
- [x] 재실행 후 유지 테스트
- [x] 재설치/구매 복원 테스트
- [x] 취소/거부 시 오활성화 없음 확인

### 개발자 응원 카드
- [x] 커피 Product ID: support_coffee_5000
- [x] 커피 구매 옵션 ID: support-coffee-5000
- [x] 커피 한국 가격: ₩5,000
- [x] 국밥 Product ID: support_meal_10000
- [x] 국밥 구매 옵션 ID: support-meal-10000
- [x] 국밥 한국 가격: ₩10,000으로 수정
- [x] 소비성 구매 및 재구매 구조 구현
- [x] 구매 후 로컬 응원 카드 증가 구현
- [ ] 국밥 가격 수정 반영 후 결제창에서 ₩10,000 최종 확인

## 3. 알림/권한
- [x] POST_NOTIFICATIONS
- [x] SCHEDULE_EXACT_ALARM
- [x] USE_FULL_SCREEN_INTENT
- [x] RECEIVE_BOOT_COMPLETED
- [x] 최초 알람 기준 반복 재알림
- [x] 약별 재알림 간격
- [x] 같은 시각 여러 약 그룹 알림
- [x] 각 약별 먹었어요/나중에 처리
- [x] 알림 소리·진동 2분 자동 정지
- [ ] 최종 Play 설치본에서 알림 종합 스모크 테스트
  - 최초 알림
  - 재알림
  - 2분 자동 정지
  - 두 약 동시 알림
  - 복용 완료 후 후속 알림 중단

## 4. 정책 / Play Console
- [x] 조직 계정 전환 및 D-U-N-S 연결
- [x] 사업자등록번호 및 통신판매업 신고정보 입력
- [x] 웹사이트 Search Console 소유권 확인
- [x] 공개 개인정보처리방침
- [x] 앱 내부 개인정보처리방침 링크
- [x] 개인정보처리방침에 프리미엄·응원 카드 Billing 반영
- [x] Data safety 작업본에 응원 카드 Billing 반영
- [ ] 조직 전환 후 72시간 경과 확인
- [ ] Play Console 건강 앱 선언 최종 상태 확인
- [ ] Play Console Data safety 최종 제출 상태 확인
- [ ] 광고 포함 여부 = 예 확인
- [ ] 전체화면 인텐트 선언 최종 제출/상태 확인
- [ ] 정확한 알람 관련 Play Console 질문이 표시되면 SCHEDULE_EXACT_ALARM 사용 사실과 사용자 허용 방식에 맞춰 답변
- [ ] 대상 연령/콘텐츠 등급 최종 상태 확인
- [ ] 앱 액세스: 로그인 불필요로 설정 확인

## 5. 스토어 등록정보
- [ ] 앱 이름/짧은 설명/전체 설명 최종 확인
- [ ] 앱 아이콘 최종 확인
- [ ] 피처 그래픽 최종 확인
- [ ] 실제 최신 UI 기반 휴대전화 스크린샷 최종 업로드
- [ ] 개발자 이메일/전화번호/웹사이트 공개 정보 확인
- [ ] 개인정보처리방침 URL 확인

## 6. 광고
- [x] 프로덕션 AdMob ID 포함
- [x] UMP 코드 포함
- [ ] 실제 무료 계정에서 프로덕션 배너 광고 표시 최종 확인
- [ ] 광고 개인정보 옵션 화면이 필요한 지역에서 진입 가능 확인
- [ ] AdMob 앱의 Play Store 연결은 공개 후 확인
- [ ] app-ads.txt 준비: 현재 GitHub Pages 프로젝트 경로는 루트 호스팅과 별도 검토 필요

## 7. 제출 직전
- [ ] 내부 테스트의 국밥 결제창이 ₩10,000으로 표시
- [ ] 최종 알림 스모크 테스트 통과
- [ ] Play Console 대시보드에 미완료/조치 필요 항목 없음
- [ ] 조직 전환 72시간 이후
- [ ] Production 트랙 접근 가능 여부 확인
- [ ] v3.0.15 versionCode 56 서명 AAB 업로드
- [ ] 릴리스 노트 입력
- [ ] 검토 후 프로덕션 제출
