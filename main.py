import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "일별 관객수 추이",
        "개별 누적 관객수",
        "TOP 5 비교",
        "전체 관객수 이동평균",
        "월별 총 관객수",
    ]
)


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

    movie_counts = df["영화명"].value_counts()
    over_20days_movies = movie_counts[movie_counts >= 20].index
    filtered_movie_order = [m for m in movie_order if m in over_20days_movies]
    top5_long_run_movies = filtered_movie_order[:5]

    top5_df = df[df["영화명"].isin(top5_long_run_movies)]

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


# [네 번째 그래프: 이동평균선 그래프]
with tab4:
    st.subheader("📉 전체 TOP 10 영화 일일 관객수 합계 및 7일 이동평균")

    # 기준일자별로 모든 TOP 10 영화의 '해당일관객수' 합계를 구합니다.
    daily_total = (
        df.groupby("기준일자")["해당일관객수"].sum().reset_index()
    )

    # 7일 이동평균(Rolling Mean)을 계산합니다.
    daily_total["7일_이동평균"] = (
        daily_total["해당일관객수"].rolling(window=7).mean()
    )

    fig4 = go.Figure()

    fig4.add_trace(
        go.Scatter(
            x=daily_total["기준일자"],
            y=daily_total["해당일관객수"],
            mode="lines",
            name="일일 관객수 합계",
            line=dict(color="rgba(150, 150, 150, 0.4)", width=1.5),
        )
    )

    fig4.add_trace(
        go.Scatter(
            x=daily_total["기준일자"],
            y=daily_total["7일_이동평균"],
            mode="lines",
            name="7일 이동평균",
            line=dict(color="#FF4B4B", width=3),
        )
    )

    fig4.update_layout(
        title="박스오피스 전체 일일 관객수 합계 및 7일 이동평균 추이",
        xaxis_title="날짜",
        yaxis_title="관객수(명)",
        hovermode="x unified",
    )

    st.plotly_chart(fig4, use_container_width=True)
    st.caption("💡 이 그래프로 알 수 있는 것: 주말/평일 노이즈(변동)를 줄인 7일 이동평균선을 통해 극장가 전체 관객 규모의 계절적·시기별 성수기/비수기 트렌드를 파악할 수 있습니다.")


# [다섯 번째 그래프: 월별 막대그래프]
with tab5:
    st.subheader("📊 월별 전체 관객수 합계")

    # 1. 네 번째 탭에서 구한 daily_total 데이터에 연-월(YYYY-MM) 컬럼을 추가합니다.
    daily_total["연월"] = daily_total["기준일자"].dt.strftime("%Y-%m")

    # 2. 연월 단위로 그룹화하여 월별 총 관객수를 합산합니다.
    monthly_total = (
        daily_total.groupby("연월")["해당일관객수"].sum().reset_index()
    )

    # 3. Plotly 막대그래프(Bar Chart) 생성
    fig5 = px.bar(
        monthly_total,
        x="연월",
        y="해당일관객수",
        title="월별 박스오피스 전체 관객수 합계",
        labels={"연월": "기준 월", "해당일관객수": "총 관객수(명)"},
        text_auto=".2s",  # 막대 위에 축약된 숫자로 관객수 표시
    )

    st.plotly_chart(fig5, use_container_width=True)
    st.caption("💡 이 그래프로 알 수 있는 것: 월별 총 관객수 비교를 통해 극장가의 월별 성수기(방학, 연휴 시즌 등)와 비수기를 한눈에 직관적으로 파악할 수 있습니다.")
