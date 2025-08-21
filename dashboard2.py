import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np

# ==========================
# 페이지 설정
# ==========================
st.set_page_config(
    page_title="뀨군뀨양 가계부",
    page_icon="🐧",
    layout="wide"
)

st.title("🐧 뀨군뀨양 가계부 대시보드")
st.markdown("---")

# ==========================
# 샘플 데이터 함수
# ==========================
def sample_data():
    np.random.seed(42)
    categories = ['식비', '외식비', '생활용품', '건강', '문화생활']
    items = ['라면', '커피', '휴지', '약', '영화티켓', '점심', '저녁', '간식', '음료', '책']
    data = []
    for i in range(50):
        date = datetime.now().replace(day=np.random.randint(1,28))
        cat = np.random.choice(categories)
        item = np.random.choice(items)
        amount = np.random.randint(1000,50000)
        io = np.random.choice(['수입','지출'], p=[0.2,0.8])
        data.append([date, cat, item, amount, io, ''])
    df = pd.DataFrame(data, columns=['날짜','분류','항목','금액','수입/지출','비고'])
    return df

# ==========================
# 파일 업로드
# ==========================
with st.sidebar:
    st.header("📁 가계부 파일 업로드")
    uploaded_file = st.file_uploader(
        "엑셀 파일 업로드 (.xlsx)",
        type=["xlsx"],
        help="월별 가계부 시트가 포함된 파일을 업로드하세요"
    )

# ==========================
# 선택한 시트 데이터 로드
# ==========================
def load_sheet(file_bytes, sheet_name):
    # 데이터 시작 행 지정 (7번째 행)
    df = pd.read_excel(file_bytes, sheet_name=sheet_name, header=6)
    # 컬럼 공백 제거
    df.columns = df.columns.str.strip().str.replace('\n','').str.replace('\r','')
    # 날짜, 금액 없는 행 제거
    df = df.dropna(subset=['날짜','금액'])
    # 금액 숫자로 변환
    df['금액'] = df['금액'].astype(str).str.replace(',', '', regex=False)
    df['금액'] = pd.to_numeric(df['금액'], errors='coerce')
    df = df.dropna(subset=['금액'])
    # 날짜 타입 변환
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
    return df

if uploaded_file:
    try:
        # 업로드 파일 열기
        xls = pd.ExcelFile(uploaded_file)
        sheet = st.selectbox("📅 시트 선택", xls.sheet_names)

        # 선택한 시트 읽기
        df = load_sheet(uploaded_file, sheet)

        # 필수 컬럼 체크
        required_cols = ['날짜','분류','항목','금액','수입/지출','비고']
        if not all(col in df.columns for col in required_cols):
            st.warning("❌ 필수 컬럼 누락, 샘플 데이터 표시")
            df = sample_data()

    except Exception as e:
        st.error(f"❌ 파일 로드 실패: {e}")
        df = sample_data()
else:
    st.info("⬆️ 엑셀 파일 업로드 필요, 샘플 데이터 표시")
    df = sample_data()

# ==========================
# 월 예산 설정
# ==========================
monthly_budget = 400_000
total_expense = df[df['수입/지출']=='지출']['금액'].sum()
remain = monthly_budget - total_expense

# ==========================
# 상단 요약
# ==========================
col1, col2, col3 = st.columns(3)
col1.metric("이번 달 예산", f"{monthly_budget:,.0f} 원")
col2.metric("총 지출", f"{total_expense:,.0f} 원")
col3.metric("남은 금액", f"{remain:,.0f} 원")
st.markdown("---")

# ==========================
# 분류별 지출
# ==========================
cat_exp = df[df['수입/지출']=='지출'].groupby('분류')['금액'].sum().reset_index()
fig1 = px.pie(cat_exp, names='분류', values='금액', title="📂 분류별 지출 비중")
st.plotly_chart(fig1, use_container_width=True)

# ==========================
# 항목별 TOP 10
# ==========================
item_exp = df[df['수입/지출']=='지출'].groupby('항목')['금액'].sum().reset_index().sort_values('금액', ascending=False).head(10)
fig2 = px.bar(item_exp, x='금액', y='항목', orientation='h', title="🏆 항목별 지출 TOP 10", color='금액', color_continuous_scale='Blues')
st.plotly_chart(fig2, use_container_width=True)

# ==========================
# 날짜별 지출 추이
# ==========================
daily_exp = df[df['수입/지출']=='지출'].groupby('날짜')['금액'].sum().reset_index()
fig3 = px.line(daily_exp, x='날짜', y='금액', title="📅 날짜별 지출 추이")
st.plotly_chart(fig3, use_container_width=True)

# ==========================
# 세부 내역
# ==========================
with st.expander("📋 세부 내역 보기"):
    st.dataframe(df)

# ==========================
# 데이터 다운로드
# ==========================
st.markdown("---")
st.header("📁 데이터 내보내기")
csv = df.to_csv(index=False, encoding='utf-8-sig')
st.download_button(
    label="CSV 파일 다운로드",
    data=csv,
    file_name=f"뀨군뀨양_가계부_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)


# python -m streamlit run dashboard2.
