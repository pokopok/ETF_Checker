import pandas as pd
import streamlit as st
import yfinance as yf
import altair as alt
from PIL import Image

st.title('ETF Price Checker')

column1, column2, column3, column4, column5= st.columns(5)
img=Image.open('turnip.png')
column1.image(img, width=60)
column2.image(img, width=60)
column3.image(img, width=60)
column4.image(img, width=60)
column5.image(img, width=60)

tickers = ['VYM', 'SPYD', 'HDV', 'VOO', 'VTI']

st.write("""
左バーの表示設定から表示銘柄、年数、範囲を指定してください。
""")

st.sidebar.write("""
# 表示設定
"""
)

st.sidebar.write("""
## 銘柄選択
""")

brands = st.sidebar.multiselect(
    '表示する銘柄名を選択してください',
    tickers,
    ['VYM', 'SPYD', 'HDV']
)

if not brands:
    st.error('少なくとも一銘柄は選んでください')

st.sidebar.write("""
## 表示年数選択
"""
)

years = st.sidebar.slider('年数を指定してください', 1, 20, 5)

st.sidebar.write("""
## 株価の範囲指定
""")

ymin, ymax = st.sidebar.slider(
	'範囲を指定してください.',
	0, 500, (0, 150)
)


@st.cache
def get_data(years, tickers):
    df = pd.DataFrame()
    for brands in tickers:

        tkr = yf.Ticker(brands)

        hist = tkr.history(period= f'{years}y')
        hist = hist[['Close']]
        hist.columns = [brands]
        hist = hist.T
        hist.index.name = 'Name'

        df = pd.concat([df, hist])
    return df



df = get_data(years, tickers).T
df2 = df.reset_index()

df2 = df2.groupby([df2['Date'].dt.year, df2['Date'].dt.month]).head(1).set_index('Date')
df2.index = df2.index.strftime('%d %B %Y')
df2 = df2.T

data = df2.loc[brands]
st.write(f"""### 過去{years}年の株価（USD）""",data.sort_index())
data = data.T.reset_index()
data = pd.melt(data, id_vars=['Date']).rename(
columns={'value': 'Stock Prices(USD)'}
)
chart = (
    alt.Chart(data)
    .mark_line(opacity=0.8, clip=True) #clipはグラフ範囲外は削除
    .encode(
    x='Date:T',
    y=alt.Y('Stock Prices(USD):Q', stack=None, scale=alt.Scale(domain=[ymin, ymax])),
    color='Name:N'
    ) # scaleでy軸の範囲を設定
)

st.altair_chart(chart, use_container_width=True)