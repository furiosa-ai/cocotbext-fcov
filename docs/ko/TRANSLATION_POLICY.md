# 한국어 문서 번역 정책

> 본 문서는 `docs/ko/` 하위 모든 한국어 문서의 번역 규약을 정의한다.
> 본 정책은 veriosa-py의 `docs/ko/TRANSLATION_POLICY.md`를 cocotbext-fcov
> 컨텍스트에 맞게 축약 / 채택한 것이다.

## §0. 말투 / 시점

- **평서체 사용**: `~한다`, `~된다`, `~이다`. 경어체 (`~합니다`, `~하세요`) 금지.
- **독자 관점**: "사용자에게 권유"가 아닌 "문서를 읽는 주체에게 시스템 동작 / 사용법을 설명"하는 declarative 톤.

## §1. 영어 그대로 유지

다음은 한국어로 번역하지 않는다.

- **Verification / coverage 용어**: `coverage`, `covergroup`, `coverpoint`, `cross`, `bin`, `sample`, `assertion`, `constraint`, `transition`.
- **Protocol / interface 이름**: 모든 bus / interface 이름은 영어.
- **약어 / 일반 기술 용어**: `DUT`, `SV`, `RTL`, `pytest`, `cocotb`, `Python`, `Enum`, `IntEnum`, `range`, `class`.
- **프로젝트 고유명사 / 클래스명 / 파일 경로**: 모든 `BinXxx`, `CoverXxx`, `cocotbext.fcov.*`, `tests/pytest/*`.

## §2. 한국어로 번역

자주 쓰이는 한국어 외래어 (`인터페이스`, `클래스`, `모델`, `시뮬레이터`, `라이브러리`, `프레임워크`, `모듈`, `패키지`, `옵션`, `플래그`) 는 한국어 그대로.

## §3. Section heading 번역 매핑

| 영문 | 한국어 |
|------|--------|
| Overview | 개요 |
| Quick example | Quick example (원문 유지) |
| Usage patterns | Usage patterns (원문 유지) |
| When to use | 사용 시점 |
| Goal | 목표 |
| API summary | API summary (원문 유지) |
| See also | 관련 문서 |

## §4. 코드 블록

Python / SystemVerilog / bash 코드 블록은 **영문 원본 유지**. 주석 (`# ...`) 역시 영어.

## §5. Frontmatter

```yaml
---
source: ../<path>.md
source_hash: <영문 body의 해시 또는 "bootstrap">
title: <한국어 타이틀>
---
```

`source_hash`는 영문 body 해시이며 drift 추적용. 초기 부트스트랩 시점에는 `bootstrap` 문자열 placeholder를 사용한다.

---

*본 문서는 docs 유지관리용 정책이며 실제 cocotbext-fcov 사용자 가이드가 아니다.*
