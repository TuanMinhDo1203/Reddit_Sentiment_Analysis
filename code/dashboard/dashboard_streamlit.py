import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
import match_page
import team_sentiment_page
import base64
import os
from pathlib import Path
import overview_page
import chatbot
# Load the sentiment dataset with caching
@st.cache_data
def load_sentiment_data():
    file_path = Path("Reddit_Sentiment_Analysis/dataframe/source_dashboard/nonan_goodformat_comment_data.csv")
    df_sentiment = pd.read_csv(file_path)
    df_sentiment["match_time"] = pd.to_datetime(df_sentiment["match_time"])
    return df_sentiment
import os
print(os.getcwd())  # In ra thư mục hiện tại

# Load the match dataset with caching
@st.cache_data
def load_match_data():
    file_path = Path("Reddit_Sentiment_Analysis/dataframe/source_dashboard/nonan_goodformat_match_data.csv")
    df_match = pd.read_csv(file_path)
    df_match["Date"] = pd.to_datetime(df_match["Date"])
    return df_match

st.set_page_config(page_title="Football Sentiment Analysis", layout="wide")

# Load data
df = load_sentiment_data()
df_match = load_match_data()
dfs = load_sentiment_data()
chatbot.football_chatbot(df)
# Debug: Check if 'matchday' column exists
if 'matchday' not in dfs.columns:
    st.error("Error: 'matchday' column not found in the dataset. Available columns: " + str(dfs.columns.tolist()))
    st.stop()

# def add_snowfall_effect():
#     # Check if the image exists
    
    image_path = Path("Reddit_Sentiment_Analysis/code/dashboard/ball.png")
     
    if not os.path.exists(image_path):
        st.warning("Image not found. Snowfall effect will use a default image.")
        snowflake_image = "https://via.placeholder.com/30"  # Fallback image
    else:
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        snowflake_image = f"data:image/png;base64,{encoded}"

#     # CSS-only snowfall effect
#     st.markdown(
#         f"""
#         <style>
#         .snowflake-container {{
#             position: fixed;
#             top: 0;
#             left: 0;
#             width: 100%;
#             height: 100%;
#             pointer-events: none;
#             z-index: 9999;
#         }}
#         .snowflake {{
#             position: absolute;
#             width: 30px;
#             height: 30px;
#             background: url('{snowflake_image}') no-repeat center center;
#             background-size: contain;
#             opacity: 0.8;
#             animation: fall linear infinite;
#         }}
#         .stApp {{
#             background: #1E1E1E;  /* Dark background to match the theme */
#             color: white;
#         }}
#         @keyframes fall {{
#             0% {{ opacity: 0; transform: translateY(-20vh); }}
#             20% {{ opacity: 1; }}
#             100% {{ opacity: 0; transform: translateY(100vh); }}
#         }}
#         /* Define multiple snowflakes with different positions and delays */
#         .snowflake:nth-child(1) {{ left: 5%; animation-duration: 10s; animation-delay: 0s; }}
#         .snowflake:nth-child(2) {{ left: 15%; animation-duration: 12s; animation-delay: 1s; }}
#         .snowflake:nth-child(3) {{ left: 25%; animation-duration: 8s; animation-delay: 2s; }}
#         .snowflake:nth-child(4) {{ left: 35%; animation-duration: 11s; animation-delay: 0s; }}
#         .snowflake:nth-child(5) {{ left: 45%; animation-duration: 9s; animation-delay: 3s; }}
#         .snowflake:nth-child(6) {{ left: 55%; animation-duration: 10s; animation-delay: 1s; }}
#         .snowflake:nth-child(7) {{ left: 65%; animation-duration: 13s; animation-delay: 2s; }}
#         .snowflake:nth-child(8) {{ left: 75%; animation-duration: 7s; animation-delay: 0s; }}
#         .snowflake:nth-child(9) {{ left: 85%; animation-duration: 10s; animation-delay: 3s; }}
#         .snowflake:nth-child(10) {{ left: 95%; animation-duration: 12s; animation-delay: 1s; }}
#         </style>
#         <div class="snowflake-container">
#             <div class="snowflake"></div>
#             <div class="snowflake"></div>
#             <div class="snowflake"></div>
#             <div class="snowflake"></div>
#             <div class="snowflake"></div>
#             <div class="snowflake"></div>
#             <div class="snowflake"></div>
#             <div class="snowflake"></div>
#             <div class="snowflake"></div>
#             <div class="snowflake"></div>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

# Apply the snowfall effect with error handling
# try:
#     add_snowfall_effect()
# except Exception as e:
#     st.warning(f"Failed to apply snowfall effect: {str(e)}. Continuing without the effect.")

# Create navigation menu
page = option_menu(
    menu_title=None,
    options=["Tổng quan", "Sentiment Trận đấu", "Chi tiết Post & Comment", "Sentiment Đội Bóng"],
    icons=["house", "bar-chart", "chat-dots", "soccer"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"background-color": "#4b1248"},
        "nav-link": {"font-size": "16px", "text-align": "center", "color": "white"},
        "nav-link-selected": {"background-color": "#7d2463"},
    }
)

# Page 1: Tổng quan
if page == "Tổng quan":
    st.title("Tổng quan Sentiment")
    overview_page.display_overview()

# Page 2: Sentiment Trận đấu
elif page == "Sentiment Trận đấu":
    match_page.display_match_sentiment()

# Page 3: Chi tiết Post & Comment
elif page == "Chi tiết Post & Comment":
    st.title("Chi tiết Bài Post & Comment")
    st.subheader("Danh sách Post và Comment")
    # st.dataframe(df[['post_id', 'comment_id', 'comment', 'comment_author', 'Sentiment', 'Compound']])

# Page 4: Sentiment Đội Bóng
elif page == "Sentiment Đội Bóng":
    team_sentiment_page.display_team_sentiment(dfs)