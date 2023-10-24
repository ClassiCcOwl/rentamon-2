import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

file = "rentamon.csv"


df = pd.read_csv(file)

m = df[['rooms', 'rate']]

z = m.groupby(['rooms']).mean()

plt.pie(z['rate'], labels=z.index)
# plt.show()

st.scatter_chart(z)
st.line_chart(z)

st.pyplot(plt)
