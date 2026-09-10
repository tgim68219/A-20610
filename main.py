import pandas as pd
import plotly.express as px
import streamlit as st


# [1. 데이터 불러오기]
# @st.cache_data 데코레이터를 사용하여 데이터를 캐싱(재사용)합니다.
# 앱이 실행될 때 매번 새로 다운로드하지 않아 속도가 빨라집니다.
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)

    # [2. 날짜 전처리]
    # 결측치(값이 없는 데이터)가 포함된 행을 삭제합니다.
    df = df.dropna()

    # '기준일자' 컬럼을 datetime(날짜) 형식으로 변환합니다.
    df["기준일자"] = pd.to_datetime(df["기준일자"])

    # 전체 데이터를 기준일자 오름차순으로 정렬합니다.
    df = df.sort_values(by="기준일자")

    return df


# 웹앱 제목 설정
st.title("🎬 영화 박스오피스 데이터 분석")

# 데이터 로드
df = load_data()

# [3. 영화 선택 기능]
# '영화명'별 '누적관객수'의 최댓값을 구해 내림차순 정렬합니다.
movie_order = (
    df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index.tolist()
)

# 사이드바에 영화 선택 드롭다운 생성 (기본값: 첫 번째 영화)
st.sidebar.header("🔍 옵션 선택")
selected_movie = st.sidebar.selectbox("영화를 선택하세요:", movie_order)

# 선택한 영화의 데이터만 필터링합니다.
filtered_df = df[df["영화명"] == selected_movie]


# [5. 기타 - 구역 나누기]
# 추후 다른 그래프들을 쉽게 추가할 수 있도록 탭(Tab) 구역을 나눕니다.
tab1, tab2 = st.tabs(["일별 관객수 추이", "추가 예정 구역"])


# [4. 선그래프 그리기]
with tab1:
    st.subheader(f"📈 {selected_movie} - 일자별 관객수 변화")

    # Plotly를 이용한 선 그래프 생성
    fig = px.line(
        filtered_df,
        x="기준일자",
        y="해당일관객수",
        title=f"'{selected_movie}' 일자별 관객수 추이",
        labels={"기준일자": "날짜", "해당일관객수": "관객수(명)"},
        markers=True,  # 데이터 포인트에 점 표시
    )

    # Streamlit 화면에 그래프 출력
    st.plotly_chart(fig, use_container_width=True)

    # [5. 기타 - 설명 문구]
    st.caption("💡 이 그래프로 알 수 있는 것: 개봉 일자별 관객수 추이 및 흥행 유지 기간을 확인할 수 있습니다.")


# 추후 추가할 그래프를 위한 예시 구역
with tab2:
    st.subheader("📌 준비 중인 영역")
    st.info("여기에 새로운 분석 그래프를 추가할 예정입니다.")
    # st.caption("💡 이 그래프로 알 수 있는 것: [설명 문구 추가 자리]")
