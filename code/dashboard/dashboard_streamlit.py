import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
# Load dummy data (thay bằng dữ liệu thực)
df = pd.DataFrame({
    'match': ['Match 1', 'Match 1', 'Match 2', 'Match 2'],
    'team': ['Team A', 'Team B', 'Team A', 'Team B'],
    'sentiment': ['Positive', 'Negative', 'Neutral', 'Positive'],
    'count': [120, 80, 50, 140]
})

df_info = pd.DataFrame({
    'match': ['Match 1', 'Match 2'],
    'date': ['2024-03-10', '2024-03-15'],
    'location': ['Stadium A', 'Stadium B'],
    'total_comments': [500, 420]
})



st.set_page_config(page_title="Football Sentiment Analysis", layout="wide")

# Tạo thanh menu ngang
page = option_menu(
    menu_title=None,  # Không cần tiêu đề
    options=["Tổng quan", "Sentiment Trận đấu", "Chi tiết Post & Comment"],
    icons=["house", "bar-chart", "chat-dots"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"background-color": "#4b1248"},
        "nav-link": {"font-size": "16px", "text-align": "center", "color": "white"},
        "nav-link-selected": {"background-color": "#7d2463"},
    }
)



# Trang 1: Tổng quan sentiment
if page == "Tổng quan":
    st.title("Tổng quan Sentiment")
    fig = px.bar(df, x='match', y='count', color='sentiment', barmode='group')
    st.plotly_chart(fig)

# Trang 2: Sentiment theo trận
elif page == "Sentiment Trận đấu":
    st.title("Sentiment theo Trận")

    selected_match = st.selectbox("Chọn trận đấu:", df['match'].unique())

    match_data = df_info[df_info['match'] == selected_match].iloc[0]
    st.write(f"📅 **Ngày diễn ra:** {match_data['date']}")
    st.write(f"📍 **Địa điểm:** {match_data['location']}")
    st.write(f"💬 **Tổng số bình luận:** {match_data['total_comments']}")

    filtered_df = df[df['match'] == selected_match]
    fig = px.bar(filtered_df, x='team', y='count', color='sentiment', barmode='group',
                 title=f'Sentiment for {selected_match}')
    st.plotly_chart(fig)

# Trang 3: Chi tiết post & comment
elif page == "Chi tiết Post & Comment":
    st.title("Chi tiết Bài Post & Comment")
    fig = px.histogram(df, x='sentiment', y='count', color='team', barmode='group')
    st.plotly_chart(fig)
