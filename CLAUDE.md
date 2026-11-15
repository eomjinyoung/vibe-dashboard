# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트

Streamlit, pandas, openpyxl로 만드는 매출 대시보드다. `uv init --no-package`로 만든 uv 프로젝트라서 빌드 단계나 설치 가능한 패키지가 없고, 프로젝트의 `.venv` 안에서 스크립트를 바로 실행한다. 파이썬 버전은 `.python-version`을 따른다(`pyproject.toml`은 3.13 이상을 요구한다).

아직 초기 뼈대 단계다. `main.py`는 uv가 만든 기본 예제 그대로이고, 테스트·린터·포매터는 아직 설정되어 있지 않다.

## 작업 규칙

- 사용자는 코딩 초보자다. 설명은 쉬운 한국어로 한다.
- 문서(CLAUDE.md, README 등)는 '~다' 문체로 쓴다. 사용자에게 하는 답변은 존댓말로 한다.
- 코드에는 한국어 주석을 단다.
- 계산 결과를 알려 줄 때는 어떤 기준으로 계산했는지 함께 설명한다.
- 금액은 천 단위 쉼표를 넣어 보여 준다(예: 1,234,500원). 대시보드 화면의 숫자도 같다.
- 커밋 메시지는 한국어로 쓴다.

## 명령어

파이썬은 항상 `uv run`으로 실행하고, 패키지는 항상 `uv add`로 설치한다. `python`, `pip`, `streamlit`을 직접 쓰지 않는다.

- 대시보드 실행: `uv run streamlit run app.py` (Streamlit 앱은 `uv run app.py`로 실행하면 동작하지 않는다)
  - **Claude는 Streamlit 앱을 직접 실행하지 않는다.** 사용자가 두 번째 터미널에서 이 명령으로 앱을 띄워 둔다. Streamlit은 파일이 저장되면 다시 불러오므로, 코드를 고친 뒤에는 브라우저에서 확인해 달라고 안내한다.
  - 코드가 맞는지 확인해야 하면 앱을 띄우지 말고 `uv run python -c "..."`로 데이터 처리 부분만 따로 실행해 본다.
- 일반 스크립트 실행: `uv run main.py`
- 패키지 추가: `uv add <패키지>` (`pyproject.toml`과 `uv.lock`이 함께 갱신되므로 이 파일들을 직접 고치지 않는다)
- 개발용 패키지 추가: `uv add --dev <패키지>`
- 변경 사항을 받은 뒤 환경 맞추기: `uv sync`

## Streamlit 스킬

- Streamlit 코드를 만들거나 고치기 전에 `.claude/skills/developing-with-streamlit`이 있는지 확인한다. 없으면 `uv run streamlit skills --yes`를 실행해 설치한 뒤 작업한다(`.venv`가 없으면 먼저 `uv sync`).
- 이 스킬은 `.venv` 안의 Streamlit 설치 폴더를 가리키는 바로가기라서, 컴퓨터마다 따로 만든다. `.gitignore`에 들어 있으므로 git에 추가하지 않는다.
- 스킬 내용은 `uv.lock`에 고정된 Streamlit 버전을 따른다. 스킬 파일을 프로젝트에 복사해 커밋하지 않는다(업그레이드해도 옛 내용이 남기 때문이다).

## 데이터

`app.py`는 파일을 직접 읽지 않고, 사용자가 화면의 `st.file_uploader`로 올린 엑셀 파일을 읽는다. 파일을 올리기 전에는 안내 문구만 보여 주고 `st.stop()`으로 멈춘다.

`data/sales_2026.xlsx`는 6장의 `../sales-report` 프로젝트에서 복사해 온 예시 파일이다. 화면에서 올려 보거나 코드를 확인할 때 쓴다.

- 시트는 `판매` 하나이고, 1,000행이다.
- 열: `날짜`(datetime, 2026년 중 180일), `지역`(5곳), `상품`(20종), `수량`, `단가`, `매출`(정수, 원 단위). `매출`은 `수량 × 단가`다.
- 열 이름이 한국어이므로 코드에서도 한국어 열 이름을 그대로 쓴다.
- Streamlit은 화면을 조작할 때마다 스크립트를 처음부터 다시 실행하므로, 데이터 읽기 함수에는 `@st.cache_data`를 붙인다. 올린 파일은 `uploaded_file.getvalue()`로 바이트를 꺼내 함수에 넘긴다(내용이 같으면 다시 읽지 않는다).
- 앱 화면 동작은 `st.testing.v1.AppTest`로 확인할 수 있다. 서버를 띄우지 않으므로 "앱을 직접 실행하지 않는다" 규칙에 어긋나지 않는다. 파일 올리기는 `at.file_uploader[0].upload("sales_2026.xlsx", 바이트).run()`으로 흉내 낸다.

## 폴더 규칙

- `data/`: 대시보드가 읽는 입력 파일을 둔다.
- `data/`의 원본 파일은 절대 수정하거나 덮어쓰지 않는다. 원본 데이터를 바꿔야 하면 `../sales-report`에서 다시 만든 뒤 복사한다.
