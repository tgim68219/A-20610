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
tab1, tab2, tab3 = st.tabs(["일별 관객수 추이", "개별 누적 관객수", "TOP 5 비교(20일 이상)"])


# [첫 번째 그래프: 선그래프]
with tab1:
    st.subheader(f"📈 {selected_movie} - 일자별 관객수 변화")

    fig1 = px.line(
        filtered_df,
        x="기준일자",
        y="해당일관객수",
        title=f"'{selected_movie}' 일자별 관객수 추이",
        labels={"기준일자": "날짜", "해당일관객수": "관객수(명)"},
        markers=True,
    )

    st.plotly_chart(fig1, use_container_width=True)
    st.caption("💡 이 그래프로 알 수 있는 것: 개봉 일자별 관객수 추이 및 흥행 유지 기간을 확인할 수 있습니다.")


# [두 번째 그래프: 영역차트]
with tab2:
    st.subheader(f"📊 {selected_movie} - 누적 관객수 변화")

    fig2 = px.area(
        filtered_df,
        x="기준일자",
        y="누적관객수",
        title=f"'{selected_movie}' 누적 관객수 추이",
        labels={"기준일자": "날짜", "누적관객수": "누적 관객수(명)"},
    )

    st.plotly_chart(fig2, use_container_width=True)
    st.caption("💡 이 그래프로 알 수 있는 것: 시간이 지남에 따라 관객수가 누적되는 속도와 총 누적 관객수의 증가 곡선을 한눈에 확인할 수 있습니다.")


# [세 번째 그래프: 다중 선그래프 (조건부 TOP 5 비교)]
with tab3:
    st.subheader("🏆 장기 흥행(20일 이상) TOP 5 영화 비교")

    # 1. 영화별 등장 일수(행 개수)를 계산합니다.
    movie_counts = df["영화명"].value_counts()

    # 2. 등장 일수가 20일 이상인 영화만 필터링합니다.
    over_20days_movies = movie_counts[movie_counts >= 20].index

    # 3. 20일 이상 등장한 영화 중 누적관객수 상위 5개를 순서대로 추출합니다.
    filtered_movie_order = [m for m in movie_order if m in over_20days_movies]
    top5_long_run_movies = filtered_movie_order[:5]

    # 4. 해당 5개 영화의 데이터만 필터링합니다.
    top5_df = df[df["영화명"].isin(top5_long_run_movies)]

    # 5. 다중 선 그래프 생성
    fig3 = px.line(
        top5_df,
        x="기준일자",
        y="누적관객수",
        color="영화명",
        title="20일 이상 차트인한 TOP 5 영화의 누적관객수 변화 비교",
        labels={"기준일자": "날짜", "누적관객수": "누적 관객수(명)", "영화명": "영화 제목"},
    )

    st.plotly_chart(fig3, use_container_width=True)
    st.caption("💡 이 그래프로 알 수 있는 것: 최소 20일 이상 박스오피스 상위권을 유지한 대표 장기 흥행작 TOP 5의 누적관객수 추이를 비교할 수 있습니다.")
