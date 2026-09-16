import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="영화 데이터 그래프 - 분포와 관계", layout="wide"
)

st.title("영화 데이터 그래프 - 분포와 관계")


# 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # 장르 열 전처리: 세로막대 기호(|)로 분리 후 첫 번째 장르만 써
    df["genre"] = df["genre"].astype(str).str.split("|").str[0]

    return df


df = load_data()

# ---------------------------------------------------------
# 첫 번째 그래프: 장르별 영화 편수 (도넛 그래프)
# ---------------------------------------------------------
st.subheader("1. 장르별 영화 편수 비율")

genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["장르", "편수"]

fig1 = px.pie(
    genre_counts,
    values="편수",
    names="장르",
    hole=0.4,
    title="장르별 영화 분포",
)

# 조각에 마우스를 올리면 편수와 비율이 보이게.
fig1.update_traces(
    hovertemplate="<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}"
)

st.plotly_chart(fig1, use_container_width=True)

# 그래프 설명 구역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "박스오피스 상위권 영화 중 특정 장르가 차지하는 비중을 한눈에 파악할 수 있습니다."
)

st.divider()

# ---------------------------------------------------------
# 두 번째 그래프: 장르 및 영화별 총 관객 수 (트리맵)
# ---------------------------------------------------------
st.subheader("2. 장르 및 개별 영화별 총 관객 수")

# 칸의 크기는 total_audi(총 관객)로.
fig2 = px.treemap(
    df,
    path=[px.Constant("전체"), "genre", "movieNm"],
    values="total_audi",
    title="장르 및 영화별 총 관객 수 분포",
    color="genre",
)

# 칸에 마우스를 올리면 영화명과 총 관객이 보이게.
fig2.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객 수: %{value:,.0f}명<extra></extra>"
)

st.plotly_chart(fig2, use_container_width=True)

# 그래프 설명 구역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "어떤 장르가 가장 많은 관객을 끌어모았는지뿐만 아니라, 특정 대형 히트작이 해당 장르 전체 관객 수에 미친 영향력까지 확인할 수 있습니다."
)

st.divider()

# ---------------------------------------------------------
# 세 번째 그래프: 총 관객 수 분포 (히스토그램)
# ---------------------------------------------------------
st.subheader("3. 총 관객 수 분포")

# 히스토그램 생성
fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    title="총 관객 수 히스토그램",
    labels={"total_audi": "총 관객 수"},
)

fig3.update_traces(
    hovertemplate="관객 수 구간: %{x}<br>영화 수: %{y}편<extra></extra>"
)

st.plotly_chart(fig3, use_container_width=True)

# 가장 관객이 많은 영화 이름 추출
top_movie_idx = df["total_audi"].idxmax()
top_movie_name = df.loc[top_movie_idx, "movieNm"]
top_movie_audi = df.loc[top_movie_idx, "total_audi"]

# 그래프 설명 구역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "대부분의 영화가 하위 관객 수 구간에 집중되어 있는 오른쪽으로 긴 꼬리 분포를 보이며, "
    f"가장 많은 관객을 동원한 영화는 **'{top_movie_name}'**(총 {top_movie_audi:,.0f}명)입니다."
)

st.divider()

# ---------------------------------------------------------
# 네 번째 그래프: 개봉일 스크린 수 vs 총 관객 수 (산점도)
# ---------------------------------------------------------
st.subheader("4. 개봉일 스크린 수와 총 관객 수의 관계 (산점도)")

# 장르별로 점 색을 다르게 해.
fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    # 점에 마우스를 올리면 영화명이 보이게 하고,
    hover_name="movieNm",
    title="개봉일 스크린 수 vs 총 관객 수 산점도",
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객 수",
        "genre": "장르",
    },
)

st.plotly_chart(fig4, use_container_width=True)

# 그래프 설명 구역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "초기 확보한 스크린 수가 많을수록 최종 총 관객 수가 증가하는 양의 상관관계를 보이지만, 스크린 수가 적어도 입소문을 통해 높은 관객 수를 기록한 예외적인 성과작도 함께 확인할 수 있습니다."
)

st.divider()

# ---------------------------------------------------------
# 다섯 번째 그래프: 주요 장르별 총 관객 수 (박스플롯)
# ---------------------------------------------------------
st.subheader("5. 주요 장르별 총 관객 수 분포 (10편 이상 장르)")

# 영화가 10편 이상인 장르만 골라,
genre_counts_series = df["genre"].value_counts()
major_genres = genre_counts_series[genre_counts_series >= 10].index
df_major = df[df["genre"].isin(major_genres)]

# 상자 밖으로 튀는 점에 마우스를 올리면 영화명이 보이게.
fig5 = px.box(
    df_major,
    x="genre",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    points="outliers",
    title="영화 10편 이상 주요 장르의 총 관객 수 상자 그림",
    labels={"genre": "장르", "total_audi": "총 관객 수"},
)

fig5.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>관객 수: %{y:,.0f}명<extra></extra>"
)

st.plotly_chart(fig5, use_container_width=True)

# 그래프 설명 구역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "장르별 관객 수의 중앙값과 범위를 비교할 수 있으며, 이상치 점들을 통해 장르 내에서 이례적인 대형 흥행 기록을 세운 대표작들을 식별할 수 있습니다."
)

st.divider()

# ---------------------------------------------------------
# 여섯 번째 그래프: 스크린 수, 총 관객 수, 첫 주 관객 수의 관계 (버블 그래프)
# ---------------------------------------------------------
st.subheader("6. 개봉 초기 규모와 최종 흥행의 관계 (버블 그래프)")

# 네 번째 산점도를 버블 그래프로 변경
# 점 크기를 first_week_audi(첫 주 관객)로 넣어.
fig6 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    title="개봉일 스크린 수, 총 관객 수, 첫 주 관객 수의 관계",
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객 수",
        "first_week_audi": "개봉 첫 주 관객 수",
        "genre": "장르",
    },
    # 버블 크기 조절 (너무 작거나 크지 않게)
    size_max=60,
)

# 툴팁 형식 지정: 버블 크기인 첫 주 관객 수도 표시
fig6.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>"
    "개봉일 스크린 수: %{x:,}개<br>"
    "총 관객 수: %{y:,.0f}명<br>"
    "첫 주 관객 수: %{marker.size:,.0f}명<extra></extra>"
)

st.plotly_chart(fig6, use_container_width=True)

# 그래프 설명 구역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "앞선 산점도에 '첫 주 관객 수'라는 정보를 버블 크기로 추가했습니다. 개봉 초기 많은 스크린을 확보(x축)하고 첫 주에 폭발적인 관객을 동원(버블 크기)한 영화가 결국 높은 총 관객 수(y축)로 이어지는 '기획형 대작'의 흥행 패턴을 명확히 보여줍니다."
)
