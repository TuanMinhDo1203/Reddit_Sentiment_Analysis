import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd
import base64
from io import BytesIO
from wordcloud import WordCloud
import re
import google.generativeai as genai
import time
API_KEY = "ben"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# ---------------------- Lọc & Tóm tắt bình luận ----------------------
# Danh sách từ khóa liên quan đến sự kiện quan trọng
keywords = ["goal", "penalty", "red card", "yellow card", "free kick", "VAR", "offside"]

def extract_important_events(comments):
    """Nhận diện sự kiện từ danh sách bình luận."""
    filtered_comments = [c for c in comments if any(word in c.lower() for word in keywords)]
    
    if not filtered_comments:
        return "Không có sự kiện quan trọng nào được ghi nhận."

    text = " ".join(filtered_comments)[:4000]  # Giới hạn độ dài đầu vào
    prompt = f"Tóm tắt các sự kiện quan trọng từ các bình luận bóng đá sau:\n{text} ngắn gọn và súc tích."
    
    response = model.generate_content(prompt)
    return response.text

# Lọc comment theo trận đấu và thời gian
def get_match_events(match_comments_df, start_min, end_min):
    match_comments = match_comments_df[
        (match_comments_df["minute_in_match"].between(start_min, end_min))
    ]["comment_text"].tolist()
    
    return extract_important_events(match_comments)



#-----------------------------------------------------------------------------------

def display_sentiment_charts(match_comments, selected_match):
    """Hiển thị Pie Chart, Stacked Bar Chart và Word Cloud."""
    
    # ---------------------- Pie Chart & Stacked Bar Chart ----------------------
    col1, col2 = st.columns([1, 2])  

    with col1:
        st.subheader("Tỷ lệ Sentiment Toàn Trận")  

    with col2:
        st.subheader("Diễn Biến Sentiment")  

    col1, col2 = st.columns([1, 2])  

    with col1:  
        sentiment_counts = match_comments["Sentiment"].value_counts().reset_index()
        sentiment_counts.columns = ["Sentiment", "Count"]

        pie_chart = px.pie(sentiment_counts, values="Count", names="Sentiment", 
                            color_discrete_sequence=['#28a745', '#6c757d', '#dc3545'],
                            hole=0.3, width=350, height=350)
        st.plotly_chart(pie_chart, use_container_width=True)

    with col2:  
        if "minute_in_match" in match_comments.columns:
            match_comments["minute_in_match"] = pd.to_numeric(match_comments["minute_in_match"], errors="coerce")

            if match_comments["minute_in_match"].notna().any():  
                max_minute = match_comments["minute_in_match"].max()
            else:
                max_minute = 90  

            match_comments["minute_bin"] = pd.cut(match_comments["minute_in_match"], 
                                                bins=np.arange(0, max_minute + 5, 5), 
                                                right=False)

            sentiment_bar_data = match_comments.groupby(["minute_bin", "Sentiment"]).size().reset_index(name="Count")

            sentiment_bar_data["minute_bin"] = sentiment_bar_data["minute_bin"].apply(
                lambda x: f"{int(x.left)}-{int(x.right)}" if pd.notna(x) else "Unknown"
            )

            bar_chart = px.bar(sentiment_bar_data, 
                            x="minute_bin", 
                            y="Count", 
                            color="Sentiment",
                            color_discrete_map={"Positive": "#28a745", "Neutral": "#6c757d", "Negative": "#dc3545"},
                            barmode="stack", 
                            width=650, 
                            height=350,
                            labels={"minute_bin": "Thời gian (phút)", "Count": "Số lượng comment"})  

            st.plotly_chart(bar_chart, use_container_width=True)
        else:
            st.warning("Dữ liệu không có thông tin thời gian.")


# ------------------- Tóm tắt sự kiện quan trọng -----------------------------
    title_css = """
        <style>
            .title {
                text-align: center;
                font-size: 22px;
                font-weight: bold;
                color: white;
                text-shadow: 3px 3px 6px #cc3333;
            }
        </style>
        <h3 class='title'>📢 Tóm tắt sự kiện quan trọng</h3>
    """
    st.markdown(title_css, unsafe_allow_html=True)




    # 🎨 CSS tùy chỉnh (Fix màu thanh trượt)

    
    # CSS để tùy chỉnh giao diện slider
    slider_css = """
        <style>
            div[data-baseweb="slider"] > div {
                background: linear-gradient(to right, #cc3333, #990000) !important;
                border-radius: 10px;
                height: 8px;
            }

            div[data-baseweb="slider"] > div > div {
                background: linear-gradient(to right, #ff6666, #cc3333) !important;
                height: 8px;
                border-radius: 10px;
            }

            div[data-baseweb="slider"] > div > div > div {
                background: white !important;
                border: 3px solid #cc3333;
                width: 16px !important;
                height: 16px !important;
                border-radius: 50%;
            }

            div[data-baseweb="slider"] span {
                color: white !important;
                font-weight: bold;
                font-size: 15px;
                text-shadow: 1px 1px 2px black;
            }
        </style>
    """
    st.markdown(slider_css, unsafe_allow_html=True)



    # ⏳ Thanh trượt chọn thời gian
    start_min, end_min = st.slider(
        "⏳ Chọn khoảng thời gian (phút)", 0, 120, (0, 120), step=5
    )

    st.write(f"⏳ **Khoảng thời gian đã chọn:** {start_min} - {end_min} phút")
            


    # 🎨 CSS căn giữa button
    button_css = """
        <style>
            div.stButton > button {
                display: block;
                margin: 0 auto;
                font-size: 18px;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 10px;
                background: #cc3333;
                color: white;
                border: 2px solid black;
                transition: 0.3s;
            }

            div.stButton > button:hover {
                background: #ff6666;
                transform: scale(1.05);
                box-shadow: 0px 0px 10px rgba(255, 102, 102, 0.8);
            }
        </style>
    """
    st.markdown(button_css, unsafe_allow_html=True)




    # 🔘 Hiển thị button ở giữa
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Lấy tóm tắt sự kiện"):
            with st.spinner("🔄 Đang xử lý... Vui lòng chờ!"):
                progress_bar = st.progress(0)

                for percent_complete in range(100):
                    time.sleep(0.02)  # Giả lập xử lý
                    progress_bar.progress(percent_complete + 1)

                summary = f"{get_match_events(match_comments, start_min, end_min)}"  # Thay bằng get_match_events(...)
                progress_bar.empty()  # Xóa thanh loading khi hoàn tất

            st.success("🎉 Tóm tắt hoàn tất!")  # Hiển thị thông báo thành công
            st.info(summary, icon="📌")  # Hiển thị kết quả




    # ---------------------- Word Cloud ----------------------
    st.subheader("Word Cloud Bình Luận")

    if "last_match" not in st.session_state or st.session_state.last_match != selected_match:
        st.session_state.pop("wordcloud_img", None)  
        st.session_state.last_match = selected_match  

    if "wordcloud_img" not in st.session_state:
        all_text = " ".join(match_comments["comment_text"].dropna())

        if all_text.strip():  
            wordcloud = WordCloud(width=1000, height=500, background_color='black',
                                colormap='coolwarm').generate(all_text)

            buf = BytesIO()
            wordcloud.to_image().save(buf, format="PNG")
            st.session_state.wordcloud_img = base64.b64encode(buf.getvalue()).decode()
        else:
            st.session_state.wordcloud_img = None  

    if st.session_state.wordcloud_img:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center;">
                <img src="data:image/png;base64,{st.session_state.wordcloud_img}" width="900">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning("Không có dữ liệu bình luận để tạo Word Cloud.")

    # Ô nhập từ khóa tìm kiếm trong bình luận
    clicked_word = st.text_input("🔍 Nhập từ bạn muốn tìm:", "")

    if clicked_word:
        filtered_comments = match_comments[
            match_comments["comment_text"].str.contains(rf"\b{re.escape(clicked_word)}\b", case=False, na=False)
        ][["comment_text", "Sentiment"]]

        total_comments = len(filtered_comments)
        pos_count = (filtered_comments["Sentiment"] == "Positive").sum()
        neg_count = (filtered_comments["Sentiment"] == "Negative").sum()
        neu_count = (filtered_comments["Sentiment"] == "Neutral").sum()

        if total_comments > 0:
            st.subheader(f"📜 Bình luận chứa từ '{clicked_word}' ({total_comments} bình luận)")

            # Hiển thị số lượng bình luận theo sentiment
            st.write(f"- **😊 Tích cực:** {pos_count} bình luận")
            st.write(f"- **😐 Trung tính:** {neu_count} bình luận")
            st.write(f"- **😡 Tiêu cực:** {neg_count} bình luận")

            # Chia danh sách bình luận theo sentiment
            pos_comments = filtered_comments[filtered_comments["Sentiment"] == "Positive"]["comment_text"].tolist()
            neg_comments = filtered_comments[filtered_comments["Sentiment"] == "Negative"]["comment_text"].tolist()
            neu_comments = filtered_comments[filtered_comments["Sentiment"] == "Neutral"]["comment_text"].tolist()

            # Đảm bảo số lượng dòng bằng nhau để hiển thị đẹp
            max_len = max(len(pos_comments), len(neu_comments), len(neg_comments))
            pos_comments += [""] * (max_len - len(pos_comments))
            neu_comments += [""] * (max_len - len(neu_comments))
            neg_comments += [""] * (max_len - len(neg_comments))

            df_sentiment = pd.DataFrame({
                "😊 Tích cực": pos_comments,
                "😐 Trung tính": neu_comments,
                "😡 Tiêu cực": neg_comments
            })

            st.dataframe(df_sentiment, height=400)
        else:
            st.warning(f"Không tìm thấy bình luận nào chứa từ '{clicked_word}'.")