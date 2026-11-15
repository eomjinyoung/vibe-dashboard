import io

import pandas as pd
import streamlit as st


# Streamlit은 화면을 조작할 때마다 이 파일을 처음부터 다시 실행한다.
# @st.cache_data를 붙이면 같은 파일 내용은 한 번만 읽고, 다음부터는 저장해 둔 결과를 쓴다.
# 올린 파일의 내용(바이트)을 받아서, 내용이 같으면 다시 읽지 않는다.
@st.cache_data
def load_data(file_bytes):
    df = pd.read_excel(io.BytesIO(file_bytes))
    # 날짜에서 '연-월'(예: 2026-01)만 뽑아 둔다. 기간 필터와 월별 차트에 쓴다.
    df["월"] = df["날짜"].dt.strftime("%Y-%m")
    return df


# '2026-03' 같은 값을 화면에는 '3월'로 보여 준다
def month_label(month):
    return f"{int(month[5:])}월"


# 페이지 제목
st.title("📊 판매 대시보드")

# 엑셀 파일 올리기 버튼 (.xlsx 파일만 받는다)
uploaded_file = st.file_uploader("판매 데이터 엑셀 파일을 올려 주세요", type=["xlsx"])

# 아직 파일을 올리지 않았으면 안내 문구만 보여 주고 여기서 멈춘다
if uploaded_file is None:
    st.info("엑셀 파일을 올리면 대시보드가 나타납니다")
    st.stop()

# 올린 파일 읽기
df = load_data(uploaded_file.getvalue())

# ---------------- 왼쪽 사이드바: 필터 ----------------
all_regions = sorted(df["지역"].unique())  # 데이터에 있는 지역 목록
all_months = sorted(df["월"].unique())  # 데이터에 있는 월 목록

with st.sidebar:
    st.header("필터")

    # 지역: 여러 개를 고를 수 있고, 처음에는 모든 지역이 선택되어 있다
    selected_regions = st.pills(
        "지역",
        all_regions,
        selection_mode="multi",
        default=all_regions,
    )

    # 기간: 시작 월과 끝 월을 고르는 슬라이더. 처음에는 첫 달~마지막 달 전체다
    start_month, end_month = st.select_slider(
        "기간",
        options=all_months,
        value=(all_months[0], all_months[-1]),
        format_func=month_label,
    )

# 고른 지역에 속하고, 시작 월~끝 월 사이에 있는 판매 건만 남긴다
filtered = df[
    df["지역"].isin(selected_regions)
    & (df["월"] >= start_month)
    & (df["월"] <= end_month)
]

# 남은 데이터가 없으면(예: 지역을 하나도 고르지 않음) 안내만 보여 주고 멈춘다
if filtered.empty:
    st.warning("고른 조건에 맞는 판매 데이터가 없습니다. 왼쪽 필터에서 지역을 하나 이상 골라 주세요.")
    st.stop()

# 지금 적용된 조건을 한 줄로 보여 준다
st.caption(
    f"조건: {', '.join(selected_regions)} · "
    f"{month_label(start_month)}~{month_label(end_month)}"
)

# ---------------- 핵심 지표 ----------------
total_sales = int(filtered["매출"].sum())  # 총 매출: 모든 판매 건의 매출을 더한 값
order_count = len(filtered)  # 판매 건수: 표의 행(줄) 수
average_sales = round(total_sales / order_count)  # 건당 평균 매출: 총 매출 ÷ 판매 건수 (원 단위 반올림)

# 핵심 지표 세 개를 가로로 나란히 보여 준다 (숫자에는 천 단위 쉼표를 넣는다)
with st.container(horizontal=True):
    st.metric("총 매출", f"{total_sales:,}원", border=True)
    st.metric("판매 건수", f"{order_count:,}건", border=True)
    st.metric("건당 평균 매출", f"{average_sales:,}원", border=True)

# ---------------- 차트용 데이터 만들기 ----------------
# 차트에 쓰는 매출은 모두 각 판매 건의 매출(수량 × 단가)을 더한 값이다.
# 월별 매출: 같은 달끼리 묶어서 더한다
monthly_sales = filtered.groupby("월")["매출"].sum()

# 지역별 매출: 같은 지역끼리 묶어서 더한다
region_sales = filtered.groupby("지역", as_index=False)["매출"].sum()

# 상품별 매출을 더한 뒤, 큰 순서로 10개만 남긴다
top_products = (
    filtered.groupby("상품", as_index=False)["매출"].sum().nlargest(10, "매출")
)

# ---------------- 첫째 줄: 월별 매출 + 지역별 매출 ----------------
# 화면을 두 칸으로 나눠 차트 두 개를 나란히 놓는다 (border=True: 칸마다 테두리)
left, right = st.columns(2, border=True)

with left:
    st.subheader("월별 매출")
    st.line_chart(
        monthly_sales,
        x_label="월",
        y_label="매출(원)",
        alt="월별 매출 합계 추이",  # 화면 낭독기(시각 장애인용 프로그램)가 읽어 주는 이름
    )

with right:
    st.subheader("지역별 매출")
    st.bar_chart(
        region_sales,
        x="지역",
        y="매출",
        sort="매출",  # 매출이 작은 지역부터 왼쪽에 놓는다 (앞에 '-'를 붙이면 큰 순서)
        x_label="지역",
        y_label="매출(원)",
        alt="지역별 매출 합계 비교",
    )

# ---------------- 둘째 줄: 매출 상위 10개 상품 ----------------
with st.container(border=True):
    st.subheader("매출 상위 10개 상품")
    st.bar_chart(
        top_products,
        x="상품",
        y="매출",
        horizontal=True,  # 가로 막대 (상품 이름이 길어도 읽기 쉽다)
        sort="-매출",  # 매출이 큰 상품부터 위에 놓는다
        x_label="상품",
        y_label="매출(원)",
        alt="매출 상위 10개 상품 비교",
    )

# ---------------- 맨 아래: 데이터 표 (접어 두기) ----------------
# 처음에는 접혀 있고, "데이터 보기"를 누르면 펼쳐진다
with st.expander("데이터 보기"):
    st.dataframe(
        filtered.drop(columns="월"),  # 필터용으로 만든 '월' 열은 표에서 뺀다
        hide_index=True,
        alt="고른 조건에 맞는 판매 데이터",
        column_config={
            # 날짜는 시간 없이 연-월-일만 보여 준다
            "날짜": st.column_config.DateColumn(format="YYYY-MM-DD"),
            # 금액에는 천 단위 쉼표를 넣는다
            "단가": st.column_config.NumberColumn(format="localized"),
            "매출": st.column_config.NumberColumn(format="localized"),
        },
    )
    st.caption(f"전체 {len(df):,}건 중 {len(filtered):,}건")
