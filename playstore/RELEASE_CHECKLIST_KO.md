# 약 알리미 Google Play 출시 체크리스트

상태 기준: 2026-09-28

표시: `[x]` 준비 완료 / `[ ]` Play Console 또는 외부 서비스에서 아직 필요

## A. Google Play Console
- [ ] Google Play 개발자 계정 신원 확인 완료
- [ ] 앱 생성: 이름 `약 알리미`, 기본 언어 한국어, 앱, 무료
- [x] 패키지명 확인: `com.yakalimi.app`
- [ ] Play App Signing 사용 설정
- [x] 연락처/지원 이메일 확정: `songseung88@hanmail.net`
- [x] 개인정보처리방침 공개 페이지 준비
- [x] 한국어 및 6개 언어 스토어 등록 문구 준비
- [x] 512×512 앱 아이콘 준비
- [x] 1024×500 피처 그래픽 준비
- [ ] 실제 앱 화면 기반 스토어 스크린샷 최종 촬영 및 업로드

## B. 건강 앱 정책
- [x] 건강 앱 선언 입력안 작성
- [x] `Medication and Treatment Management / 약물 및 치료 관리` 선택 근거 확인
- [x] 앱이 의료기기가 아니라는 고지 문구 준비
- [x] 의학적 판단은 의사·약사 등 의료 전문가와 상의하도록 안내 반영
- [x] 약뿐 아니라 영양제 관리 가능성을 앱/스토어 문구에 반영
- [ ] Play Console > 앱 콘텐츠에서 건강 앱 선언 실제 제출

## C. Data safety
- [x] 약·영양제 이름, 복용 일정, 복용 기록, 재고가 개발자 서버로 전송되지 않음을 문서에 반영
- [x] Google Mobile Ads SDK 25.5.0 데이터 공개 문서 기준 초안 작성
- [x] IP 주소/사용자 상호작용/진단/기기·계정 식별자 고려사항 반영
- [x] Google Play Billing 관련 설명 반영
- [x] 개인정보처리방침과 Data safety 초안의 기본 방향 일치 확인
- [ ] 실제 프로덕션 AdMob/UMP 설정 확정 후 최종 답변 재검토
- [ ] Play Console Data safety 실제 제출

## D. AdMob
- [ ] AdMob 계정 준비 또는 현재 상태 확인
- [ ] Android 앱 `약 알리미` 등록
- [ ] 실제 AdMob App ID 발급
- [ ] 실제 Anchored Adaptive Banner 광고 단위 ID 발급
- [x] 개발/테스트 빌드는 Google 테스트 광고 ID 사용
- [ ] 프로덕션 빌드에 실제 광고 ID 반영
- [ ] UMP 메시지/동의 설정 최종 확인

## E. 프리미엄 일회성 구매
- [x] Product ID 확정: `premium_unlock`
- [x] 상품 유형 확정: 비소비성 1회 구매
- [x] 한국 기준 판매 가격 확정: `₩4,900`
- [x] 광고 제거 + 여러 약·영양제 등록 + 모든 기능 사용 문구 반영
- [x] 앱에서 Google Play Billing의 현지화 가격을 표시하도록 구현
- [x] `이전 구매 복구` 문구 및 기능 반영
- [ ] Play Console > 수익 창출에서 `premium_unlock` 실제 생성
- [ ] 라이선스 테스트 계정 추가
- [ ] Play 설치본에서 실제 구매/이전 구매 복구 검증

## F. 전체화면 알림
- [x] `USE_FULL_SCREEN_INTENT` 사용 목적 설명 준비
- [x] 사용자가 직접 설정한 약·영양제 복용 알림에만 사용한다는 설명 준비
- [x] Android 14+에서 `canUseFullScreenIntent()` 권한 상태 확인
- [x] 권한이 없을 때 일반 알림으로 동작하고 재허용 경로 제공
- [x] 업데이트 후 권한 해제 시 안내 문구 및 허용 버튼 구현/실기기 확인
- [ ] Play Console 전체화면 인텐트 선언 실제 제출 및 심사 결과 확인

## G. 배포 파일 및 서명
- [x] Play Store 업로드용 V3.0.3 AAB 생성
- [x] 업로드 키로 서명한 AAB 준비
- [x] 업로드 인증서 별도 추출
- [x] 업로드 키 백업 파일 준비
- [x] 개인키와 비밀번호를 GitHub 공개 저장소에 올리지 않음
- [ ] Play App Signing 초기 설정 시 기존 사이드로드 앱과의 서명 연속성 전략 최종 확인
- [ ] Play Console 비공개/내부 테스트 트랙에 AAB 업로드

## H. 앱 기능 QA
- [x] Android 시스템 뒤로가기 버튼이 앱 내부 이전 화면으로 이동하도록 수정
- [x] 앱 홈에서 뒤로가기를 연속 입력해야 종료되도록 수정
- [x] 약·영양제 등록/목록/재고/프리미엄 문구 반영
- [x] 6개 언어 기본 현지화 구성
- [ ] Play 설치본에서 무료 1개 제한 확인
- [ ] 실제 배너 광고 확인
- [ ] 프리미엄 구매 후 광고 제거 확인
- [ ] 구매 후 여러 약·영양제 등록 확인
- [ ] 삭제/재설치 후 이전 구매 복구 확인
- [ ] 복용 알림, 재알림, 잠금화면 전체화면 알림 확인
- [ ] 업데이트 후 기존 복용 기록/재고 유지 확인

## I. 새 개인 개발자 계정 비공개 테스트
- [x] 14일 QA 계획 준비
- [ ] 앱 설정 필수 항목 완료
- [ ] 비공개 테스트 트랙 생성
- [ ] 테스터 최소 12명 모집
- [ ] 12명 이상이 14일 연속 opt-in 상태 유지
- [ ] 테스트 피드백 및 수정 내역 기록
- [ ] 기준 충족 후 프로덕션 액세스 신청

## 지금 남아 있는 핵심 외부 의존사항
1. Google Play 개발자 신원 확인 완료
2. Play Console 앱 생성 및 Play App Signing 설정
3. AdMob 실제 App ID / 배너 광고 단위 ID
4. `premium_unlock` 실제 상품 생성
5. 실제 앱 화면 기반 스토어 스크린샷 촬영
6. 비공개 테스트 시작 및 12명 이상 테스터 14일 연속 참여

## 참고 문서
- `PLAY_CONSOLE_COPY_PASTE_KO.md`: 건강 앱, 전체화면 인텐트, Data safety, 광고, 프리미엄 등 Console 입력안
- `DATA_SAFETY_DRAFT_KO.md`: Data safety 상세 초안
- `STORE_LISTING_6LANG.md`: 6개 언어 스토어 문구
- `SCREENSHOT_CAPTURE_PLAN_KO.md`: 실제 앱 화면 촬영 계획
- `../docs/CLOSED_TEST_QA_KO.md`: 비공개 테스트 QA 계획
