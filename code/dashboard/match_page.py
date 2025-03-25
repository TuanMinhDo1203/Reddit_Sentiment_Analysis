import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import os
import random
import seaborn as sns
from wordcloud import WordCloud
import altair as alt
import base64
from io import BytesIO
from PIL import Image
import re
import numpy as np
import json
import ast
from pathlib import Path
from sentiment_charts import display_sentiment_charts

@st.cache_data
def load_match_data():
    path = Path("Reddit_Sentiment_Analysis/dataframe/source_dashboard/nonan_goodformat_match_data.csv")
    df_match = pd.read_csv(path)
    df_match["Date"] = pd.to_datetime(df_match["Date"])
    return df_match

@st.cache_data
def load_sentiment_data():
    df_sentiment = pd.read_csv(Path("Reddit_Sentiment_Analysis/dataframe/source_dashboard/nonan_goodformat_comment_data.csv"))
    df_sentiment["match_time"] = pd.to_datetime(df_sentiment["match_time"])
    return df_sentiment

@st.cache_data
def load_event_data():
    df_match = pd.read_csv(Path("Reddit_Sentiment_Analysis/dataframe/source_dashboard/full_events.csv"))
    df_match["Date"] = pd.to_datetime(df_match["Date"])
    return df_match

# Định nghĩa hàm lấy đường dẫn logo
def get_team_logo(team_name, image_folder=Path("Reddit_Sentiment_Analysis/code/dashboard/logo")):
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

def display_match_info(match_info, events):
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

    # CSS
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
                object-fit: contain;
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
                background: linear-gradient(to right, #FFD700, #FF8C00);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                display: flex;
                justify-content: center;
                align-items: center;
                width: 100%;
            }
        </style>
    """, unsafe_allow_html=True)

    # Hiển thị logo và tỷ số
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
    # Kiểm tra nếu events là chuỗi JSON, chuyển thành danh sách
    if isinstance(events, str):
        try:
            events = json.loads(events)
        except json.JSONDecodeError as e:
            st.error(f"❌ Lỗi khi parse events: {e}")
            st.text(f"📌 Dữ liệu lỗi: {events}")
            events = []

    if not isinstance(events, list):
        st.error(f"❌ Events không phải danh sách, giá trị thực: {type(events)}")
        events = []

    # Lọc chỉ lấy sự kiện bàn thắng và thẻ đỏ
    filtered_events = [
        e for e in events if "Goal" in e.get("event_name", "") 
        or e.get("event_name") in ["Red Card", "Second Yellow Card"]
    ]

    # Sắp xếp theo thời gian (minute), xử lý nếu không có giá trị hợp lệ
    def parse_time(time_str):
        """Chuyển đổi thời gian từ dạng '45+1' thành số nguyên để sắp xếp."""
        match = re.match(r"(\d+)(?:\+(\d+))?", str(time_str))
        if match:
            base_time = int(match.group(1))  # Thời gian chính
            extra_time = int(match.group(2)) if match.group(2) else 0  # Thời gian bù giờ
            return base_time + extra_time * 0.1  # Ưu tiên thời gian bù giờ nhỏ hơn
        return float('inf')  # Tránh lỗi nếu không parse được

    # Sắp xếp sự kiện theo thời gian
    filtered_events.sort(key=lambda x: parse_time(x.get("time", "9999")))

    # Hiển thị sự kiện ngay dưới bảng tỷ số
    if filtered_events:
        st.markdown("<br><br>", unsafe_allow_html=True)  # Tạo khoảng trống mà không cần gạch ngang

        for event in filtered_events:
            if "Goal" in event["event_name"]:
                emoji = "⚽"
            elif event["event_name"] == "Red Card":
                emoji = "🟥"
            elif event["event_name"] == "Second Yellow Card":
                emoji = "🟨🟥"
            else:
                emoji = "❓"

            time = event.get("time", "N/A")
            player = event.get("player", "Unknown")

            team_side = "flex-start" if event.get("team") == "home" else "flex-end"

            st.markdown(
                f"""
                <div style="display: flex; justify-content: {team_side}; margin-top: 5px;">
                    <span style="font-weight: bold;">{time}' - {emoji} {event['event_name']}</span> | {player}
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("---")

    # Thông tin chi tiết
    info_html = f"""
        <style>
            .info-container {{
                display: flex;
                justify-content: center;
                gap: 50px;
                flex-wrap: wrap;
            }}
            .info-box {{
                background-color: #222;
                padding: 15px 30px;
                border-radius: 12px;
                text-align: center;
                color: white;
                font-size: 20px;
                min-width: 180px;
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

    

    st.markdown("---")
    



    



def get_random_team_image(team_name, image_folder=Path("Reddit_Sentiment_Analysis/code/dashboard/Team")):
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
    """ Hiển thị bảng thống kê trận đấu với thanh progress đẹp """
    if match_info.empty:
        return

    home_team = match_info["home_team"].values[0]
    away_team = match_info["away_team"].values[0]
    
    stats_columns = ["Possession", "Shots_on_Target", "Touches", "Tackles", "Corners", "Yellow_Cards", "Fouls"]
    
    # Lấy ảnh logo
    home_logo = get_random_team_image(home_team)
    away_logo = get_random_team_image(away_team)
    
    if not home_logo or not away_logo:
        st.error("Không tải được logo đội bóng!")
    
    # Tạo DataFrame
    df_stats = pd.DataFrame({
        "Statistic": stats_columns,
        home_team: [float(match_info[f"{stat}_Home"].values[0]) for stat in stats_columns],
        away_team: [float(match_info[f"{stat}_Away"].values[0]) for stat in stats_columns]
    })
    df_stats.loc[df_stats["Statistic"] == "Shots_on_Target", "Statistic"] = "Shots_on_Target (%)"
    # Chuẩn bị HTML hiển thị
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
                
                width : 400px;
                height: auto;
            }}
            .stats-container {{
                background: #1e1e1e;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0px 4px 15px rgba(255, 255, 255, 0.2);
                font-family: Arial, sans-serif;
                color: white;
                text-align: center;
                width: 450px;
            }}
            .stats-header {{
                display: flex;
                justify-content: space-between;
                font-size: 20px;
                font-weight: bold;
                padding-bottom: 10px;
                border-bottom: 2px solid #444;
            }}
            .stats-row {{
                justify-content: center;
                align-items: center;
                text-align: center;
                padding: 10px 0;
            }}
            .progress-bar-container {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                width: 100%;
                gap: 10px;
            }}
            .progress-bar {{
                height: 8px;
                border-radius: 5px;
                background: #ddd;
                overflow: hidden;
                flex-grow: 1;
                position: relative;
            }}
            .bar-home {{
                background: #007bff;
                height: 100%;
                position: absolute;
                left: 0;
            }}
            .bar-away {{
                background: #dc3545;
                height: 100%;
                position: absolute;
                right: 0;
            }}
            .stat-label {{
                font-size: 14px;
                font-weight: bold;
            }}
        </style>

        <div class="match-container">
            <div class="team-logo">
                <img src="data:image/png;base64,{home_logo}" alt="{home_team}">
            </div>
            <div class="stats-container">
                <div class="stats-header">
                    <span>{home_team}</span>
                    <span>{away_team}</span>
                </div>
    """
    
    for _, row in df_stats.iterrows():
        stat = row["Statistic"]
        home_value = row[home_team]
        away_value = row[away_team]
        home_percent = (home_value / (home_value + away_value)) * 100 if home_value + away_value > 0 else 50
        away_percent = 100 - home_percent
        
        html_code += f"""
        <div class="stats-row">
            <div class="stat-label">{stat}</div>
            <div class="progress-bar-container">
                <span>{home_value}</span>
                <div class="progress-bar">
                    <div class="bar-home" style="width: {home_percent}%"></div>
                    <div class="bar-away" style="width: {away_percent}%"></div>
                </div>
                <span>{away_value}</span>
            </div>
        </div>
        """
    
    html_code += f"""
            </div>
            <div class="team-logo">
                <img src="data:image/png;base64,{away_logo}" alt="{away_team}">
            </div>
        </div>
    """
    
    # st.markdown(html_code, unsafe_allow_html=True)
    st.components.v1.html(html_code, height=600)




def display_match_sentiment():
    df_match = load_match_data()
    df_sentiment = load_sentiment_data()
    df_events = load_event_data()  # Load sự kiện trận đấu

    st.title("📊 Sentiment Trận đấu")

    # Chọn vòng đấu
    matchday_list = df_match["matchday"].unique()
    selected_matchday = st.selectbox("Chọn vòng đấu:", sorted(matchday_list))

    # Lọc danh sách trận đấu theo vòng đã chọn
    matches_in_round = df_match[df_match["matchday"] == selected_matchday]
    match_options = matches_in_round["home_team"] + " vs " + matches_in_round["away_team"]
    
    # Chọn trận đấu
    selected_match = st.selectbox("Chọn trận đấu:", match_options)

    # Lấy thông tin trận đấu
    home_team, away_team = selected_match.split(" vs ")
    match_info = matches_in_round[(matches_in_round["home_team"] == home_team) & (matches_in_round["away_team"] == away_team)]
    match_comments = df_sentiment[(df_sentiment["home_team"] == home_team) & (df_sentiment["away_team"] == away_team)]
    

        # 🔹 Chuyển từ string JSON thành list (nếu chưa ở dạng list)
    df_events["events"] = df_events["events"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    # 🔹 Xử lý ký tự đặc biệt và khoảng trắng
    df_events["events"] = df_events["events"].apply(lambda events: [
        {**e, "event_name": e["event_name"].replace("\xa0", " ").strip()} for e in events
    ])
    # 🔹 Lọc sự kiện của trận đấu từ df_events
    match_events = df_events[(df_events["home_team"] == home_team) & (df_events["away_team"] == away_team)]

    # 🔹 Chuyển về danh sách dictionary (nếu cần)
    events = match_events["events"].tolist()
    events = [e for sublist in events for e in sublist] if events else []  # Flatten nếu cần
    # Hiển thị thông tin trận đấu kèm sự kiện
    display_match_info(match_info, events)  # ✅ Truyền thêm events
    display_match_stats(match_info)
    display_sentiment_charts(match_comments, selected_match)

    
    
    
        
    #     # ---------------------- Pie Chart & Stacked Bar Chart (Hàng 1 - Căn thẳng hàng) ----------------------
    # col1, col2 = st.columns([1, 2])  # Chia layout

    # with col1:
    #     st.subheader("Tỷ lệ Sentiment Toàn Trận")  # Tiêu đề Pie Chart

    # with col2:
    #     st.subheader("Diễn Biến Sentiment")  # Tiêu đề Bar Chart

    # col1, col2 = st.columns([1, 2])  # Chia layout lại lần nữa để hiển thị biểu đồ

    # with col1:  # Pie Chart
    #     sentiment_counts = match_comments["Sentiment"].value_counts().reset_index()
    #     sentiment_counts.columns = ["Sentiment", "Count"]

    #     pie_chart = px.pie(sentiment_counts, values="Count", names="Sentiment", 
    #                         color_discrete_sequence=['#28a745', '#6c757d', '#dc3545'],
    #                         hole=0.3, width=350, height=350)
    #     st.plotly_chart(pie_chart, use_container_width=True)

    # with col2:  # Stacked Bar Chart - Sentiment theo 5 phút
    #     if "minute_in_match" in match_comments.columns:
    #         # Chuyển "minute_in_match" về số, xử lý NaN
    #         match_comments["minute_in_match"] = pd.to_numeric(match_comments["minute_in_match"], errors="coerce")

    #         if match_comments["minute_in_match"].notna().any():  # Kiểm tra nếu có giá trị hợp lệ
    #             max_minute = match_comments["minute_in_match"].max()
    #         else:
    #             max_minute = 90  # Giá trị mặc định nếu toàn bộ là NaN

    #         match_comments["minute_bin"] = pd.cut(match_comments["minute_in_match"], 
    #                                             bins=np.arange(0, max_minute + 5, 5), 
    #                                             right=False)

    #         sentiment_bar_data = match_comments.groupby(["minute_bin", "Sentiment"]).size().reset_index(name="Count")
    #         # sentiment_bar_data["minute_bin"] = sentiment_bar_data["minute_bin"].astype(str)  
    #         # Chuyển interval thành dạng chuỗi có dạng "start-end"
    #         sentiment_bar_data["minute_bin"] = sentiment_bar_data["minute_bin"].apply(
    #             lambda x: f"{int(x.left)}-{int(x.right)}" if pd.notna(x) else "Unknown"
    #         )



    #         bar_chart = px.bar(sentiment_bar_data, 
    #                         x="minute_bin", 
    #                         y="Count", 
    #                         color="Sentiment",
    #                         color_discrete_map={"Positive": "#28a745", "Neutral": "#6c757d", "Negative": "#dc3545"},
    #                         barmode="stack", 
    #                         width=650, 
    #                         height=350,
    #                         labels={"minute_bin": "Thời gian tính từ khi trận đấu bắt đầu (phút)", 
    #                                 "Count": "Số lượng comment"})  # Chỉnh tiêu đề trục X/Y

    #         st.plotly_chart(bar_chart, use_container_width=True)
    #     else:
    #         st.warning("Dữ liệu không có thông tin thời gian.")


    # # ---------------------- Word Cloud ----------------------
    # st.subheader("Word Cloud Bình Luận")

    # # Kiểm tra nếu trận đấu thay đổi => Xóa cache WordCloud
    # if "last_match" not in st.session_state or st.session_state.last_match != selected_match:
    #     st.session_state.pop("wordcloud_img", None)  # Xóa nếu tồn tại
    #     st.session_state.last_match = selected_match  # Cập nhật trận đấu mới

    # # Chỉ tạo lại WordCloud nếu chưa có trong session_state
    # if "wordcloud_img" not in st.session_state:
    #     all_text = " ".join(match_comments["comment_text"].dropna())

    #     if all_text.strip():  # Kiểm tra nếu có từ để tạo WordCloud
    #         wordcloud = WordCloud(width=1000, height=500, background_color='black',
    #                             colormap='coolwarm').generate(all_text)

    #         buf = BytesIO()
    #         wordcloud.to_image().save(buf, format="PNG")
    #         st.session_state.wordcloud_img = base64.b64encode(buf.getvalue()).decode()
    #     else:
    #         st.session_state.wordcloud_img = None  # Không có dữ liệu để hiển thị

    # # Hiển thị WordCloud nếu có dữ liệu
    # if st.session_state.wordcloud_img:
    #     st.markdown(
    #         f"""
    #         <div style="display: flex; justify-content: center;">
    #             <img src="data:image/png;base64,{st.session_state.wordcloud_img}" width="900">
    #         </div>
    #         """,
    #         unsafe_allow_html=True
    #     )
    # else:
    #     st.warning("Không có dữ liệu bình luận để tạo Word Cloud.")

    # # Ô nhập để tìm từ trong comment
    # clicked_word = st.text_input("🔍 Nhập từ bạn muốn tìm:", "")

    # # Lọc và hiển thị comment chứa từ đó
    # if clicked_word:
    #     filtered_comments = match_comments[
    #         match_comments["comment_text"].str.contains(rf"\b{re.escape(clicked_word)}\b", case=False, na=False)
    #     ][["comment_text"]]

    #     if not filtered_comments.empty:
    #         st.subheader(f"📜 Bình luận chứa từ '{clicked_word}':")
    #         st.dataframe(filtered_comments, height=300)
    #     else:
    #         st.warning(f"Không tìm thấy bình luận nào chứa từ '{clicked_word}'.")






