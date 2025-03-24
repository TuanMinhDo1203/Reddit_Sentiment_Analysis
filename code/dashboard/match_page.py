import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import os
import random

import base64
from io import BytesIO
from PIL import Image
@st.cache_data
def load_match_data():
    df_match = pd.read_csv("nonan_goodformat_match_data.csv")
    df_match["Date"] = pd.to_datetime(df_match["Date"])
    return df_match

@st.cache_data
def load_sentiment_data():
    df_sentiment = pd.read_csv("nonan_goodformat_match_data.csv")
    df_sentiment["match_time"] = pd.to_datetime(df_sentiment["match_time"])
    return df_sentiment

# Định nghĩa hàm lấy đường dẫn logo
def get_team_logo(team_name, image_folder=r"C:\Users\DO TUAN MINH\Desktop\ben\Learn\DAP391m\logo"):
    """ Lấy ảnh logo đầu tiên từ thư mục đội bóng và chuyển thành Base64 """
    team_path = os.path.join(image_folder, team_name)
    if os.path.exists(team_path) and os.path.isdir(team_path):
        images = [img for img in os.listdir(team_path) if img.endswith((".png", ".jpg", ".jpeg", ".webp"))]
        if images:  # Chỉ lấy ảnh đầu tiên trong danh sách
            img_path = os.path.join(team_path, images[0])
            with open(img_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode("utf-8")
    return None  # Trả về None nếu không có ảnh

def decode_base64_to_image(base64_string):
    """Giải mã chuỗi Base64 thành ảnh PIL"""
    if base64_string:
        image_bytes = base64.b64decode(base64_string)
        return Image.open(BytesIO(image_bytes))
    return None

def display_match_info(match_info):
    if match_info.empty:
        st.warning("Không tìm thấy dữ liệu cho trận đấu này!")
        return

    home_team = match_info['home_team'].values[0]
    away_team = match_info['away_team'].values[0]
    score = match_info['Score'].values[0]

    # Lấy logo đội bóng
    home_logo_base64 = get_team_logo(home_team)
    away_logo_base64 = get_team_logo(away_team)

    st.subheader(f"⚽ {home_team} vs {away_team}")

    # CSS để căn chỉnh logo và text đẹp hơn
    st.markdown("""
        <style>
            .team-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            .team-logo {
                height: 100px;
                object-fit: contain; /* Giữ tỉ lệ ảnh */
                display: block;
            }
            .team-name {
                font-size: 16px;
                font-weight: bold;
                margin-top: 5px;
            }
            .score {
                font-size: 40px;
                font-weight: bold;
                text-align: center;
                margin-top: 30px;

                background: linear-gradient(to right, #FFD700, #FF8C00); /* Vàng sáng → Cam đậm */
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;

                display: flex;
                justify-content: center;
                align-items: center;
                width: 100%;
            }


        </style>
    """, unsafe_allow_html=True)

    # Chia bố cục: Logo - Tỷ số - Logo
    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        st.markdown(
            f"""
            <div class="team-container">
                <img src="data:image/png;base64,{home_logo_base64}" class="team-logo"/>
                <div class="team-name">{home_team}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(f"<div class='score'>{score}</div>", unsafe_allow_html=True)

    with col3:
        st.markdown(
            f"""
            <div class="team-container">
                <img src="data:image/png;base64,{away_logo_base64}" class="team-logo"/>
                <div class="team-name">{away_team}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Hiển thị thông tin chi tiết
   
    st.markdown("---")  # Đường kẻ ngang ngăn cách

    # Dùng HTML + CSS để căn giữa và mở rộng hơn
    info_html = f"""
        <style>
            .info-container {{
                display: flex;
                justify-content: center;
                gap: 50px;  /* Tăng khoảng cách giữa các ô */
                flex-wrap: wrap;
            }}
            .info-box {{
                background-color: #222;
                padding: 15px 30px;  /* Tăng padding cho thoáng */
                border-radius: 12px;
                text-align: center;
                color: white;
                font-size: 20px;  /* Chữ to hơn */
                min-width: 180px;  /* Đảm bảo không bị bó hẹp */
                font-weight: bold;
            }}
            .info-box p {{
                margin: 8px 0;
            }}
        </style>
        <div class="info-container">
            <div class="info-box">
                <p>📅 <b>Ngày</b></p>
                <p>{pd.Timestamp(match_info["Date"].values[0]).strftime("%d-%m-%Y")}</p>
            </div>
            <div class="info-box">
                <p>⏰ <b>Giờ</b></p>
                <p>{match_info["Time"].values[0]}</p>
            </div>
            <div class="info-box">
                <p>🏟️ <b>Sân</b></p>
                <p>{match_info["Venue"].values[0]}</p>
            </div>
            <div class="info-box">
                <p>👥 <b>Khán giả</b></p>
                <p>{match_info["Attendance"].values[0]}</p>
            </div>
            <div class="info-box">
                <p>⚖️ <b>Trọng tài</b></p>
                <p>{match_info["referee"].values[0]}</p>
            </div>
        </div>
    """
    st.markdown(info_html, unsafe_allow_html=True)


    



def get_random_team_image(team_name, image_folder=r"C:\Users\DO TUAN MINH\Desktop\ben\Learn\DAP391m\Team"):
    """ Chọn một ảnh ngẫu nhiên từ thư mục đội bóng và chuyển thành Base64 """
    team_path = os.path.join(image_folder, team_name)
    if os.path.exists(team_path) and os.path.isdir(team_path):
        images = [img for img in os.listdir(team_path) if img.endswith((".png", ".jpg", ".jpeg", "webp"))]
        if images:
            img_path = os.path.join(team_path, random.choice(images))
            with open(img_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode("utf-8")
    return None

def display_match_stats(match_info):
    """ Hiển thị bảng thống kê trận đấu với logo hai bên """
    if match_info.empty:
        return

    home_team = match_info["home_team"].values[0]
    away_team = match_info["away_team"].values[0]

    stats_columns = ["Possession", "Shots_on_Target", "Touches", "Tackles", "Corners", "Yellow_Cards", "Fouls"]

    # Lấy ảnh logo (đảm bảo không lỗi)
    home_logo = get_random_team_image(home_team)
    away_logo = get_random_team_image(away_team)

    if not home_logo or not away_logo:
        st.error("Không tải được logo đội bóng!")

    # Tạo bảng dữ liệu
    data = {
        "Statistic": stats_columns,
        home_team: [match_info[f"{stat}_Home"].values[0] for stat in stats_columns],
        away_team: [match_info[f"{stat}_Away"].values[0] for stat in stats_columns]
    }

    df_stats = pd.DataFrame(data)

    # Thiết kế bảng với logo hai bên
    html_code = f"""
        <style>
            .match-container {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 50px;
                margin-top: 20px;
            }}
            .team-logo img {{
                width: 400px;
                height: auto;
            }}
            .stats-container {{
                background: #1e1e1e;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0px 4px 15px rgba(255, 255, 255, 0.2);
                font-family: Arial, sans-serif;
                color: white;
                text-align: center;
                width: 400px;
            }}
            .stats-header {{
                display: flex;
                justify-content: space-between;
                font-size: 22px;
                font-weight: bold;
                padding: 10px;
                border-bottom: 2px solid #444;
            }}
            .stats-row {{
                display: flex;
                justify-content: space-between;
                padding: 12px;
                font-size: 18px;
                border-top: 1px solid #444;
            }}
            .stats-row:nth-child(even) {{
                background: #2a2a2a;
            }}
            .bold {{
                font-weight: bold;
                color: white;
            }}
        </style>

        <div class="match-container">
            <div class="team-logo">
                <img src="data:image/png;base64,{home_logo}" alt="{home_team}">
              
            </div>
            <div class="stats-container">
                <div class="stats-header">
                    <span class="bold">{home_team}</span>
                    <span class="bold">{away_team}</span>
                </div>
    """

    for i in range(len(df_stats)):
        html_code += f"""
        <div class="stats-row">
            <span class="bold">{df_stats.iloc[i,1]}</span> 
            {df_stats.iloc[i,0]} 
            <span class="bold">{df_stats.iloc[i,2]}</span>
        </div>
        """

    html_code += f"""
            </div>
            <div class="team-logo">
                <img src="data:image/png;base64,{away_logo}" alt="{away_team}">
            </div>
        </div>
    """

    st.components.v1.html(html_code, height=600)




def display_match_sentiment():
    df_match = load_match_data()
    df_sentiment = load_sentiment_data()

    st.title("📊 Sentiment Trận đấu")
    
    # Requirement: Select matchday first
    matchdays = sorted(df_match["matchday"].unique())
    selected_matchday = st.selectbox("Chọn vòng đấu:", matchdays)
    
    # Filter matches by selected matchday
    matches_in_matchday = df_match[df_match["matchday"] == selected_matchday]
    match_options = matches_in_matchday["home_team"] + " vs " + matches_in_matchday["away_team"]
    selected_match = st.selectbox("Chọn trận đấu:", match_options)
    
    home_team, away_team = selected_match.split(" vs ")
    match_info = df_match[(df_match["home_team"] == home_team) & (df_match["away_team"] == away_team)]
    match_comments = df_sentiment[(df_sentiment["home_team"] == home_team) & (df_sentiment["away_team"] == away_team)]

    # Existing match info and stats display
    display_match_info(match_info)
    display_match_stats(match_info)

    # Requirement: Display sentiment for the match
    st.subheader("Sentiment của Trận đấu")
    sentiment_summary = match_comments.groupby('Sentiment').size().reset_index(name='count')
    fig = px.bar(sentiment_summary, x='Sentiment', y='count', 
                 title=f"Sentiment Distribution for {selected_match}")
    st.plotly_chart(fig)

    st.subheader("Bình luận về trận đấu:")
    st.dataframe(match_comments[["comment_text", "Sentiment", "Compound"]])
