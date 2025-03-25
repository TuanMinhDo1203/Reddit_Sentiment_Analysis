import streamlit as st
import pandas as pd
from fuzzywuzzy import process
import time 
from pathlib import Path
import streamlit.components.v1 as components
import google.generativeai as genai

# Cấu hình API
API_KEY = "AIzaSyCPaztwbDpbUlayehCkr0qZkVKFJXinAeU"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")
# Load dữ liệu
# path_df=Path("Reddit_Sentiment_Analysis/dataframe/source_dashboard/nonan_goodformat_comment_data.csv")
# match_comments = pd.read_csv(path_df)
# df = match_comments


# keywords = ["goal", "penalty", "red card", "yellow card", "free kick", "VAR", "offside"]

# def extract_important_events(df, comments):
#     """Nhận diện sự kiện từ danh sách bình luận."""
#     filtered_comments = [c for c in comments if any(word in c.lower() for word in keywords)]
    
#     if not filtered_comments:
#         return "Không có sự kiện quan trọng nào được ghi nhận."

#     text = " ".join(filtered_comments)[:2000]  # Giới hạn độ dài đầu vào
#     prompt = f"Tóm tắt các sự kiện quan trọng từ các bình luận bóng đá sau:\n{text}"
    
#     response = model.generate_content(prompt)
#     return response.text

# # Lọc comment theo trận đấu và thời gian
# def extract_match_events(df, home_team, away_team, start_min, end_min):
#     match_comments = df[
#         (df["home_team"] == home_team) &
#         (df["away_team"] == away_team) &
#         (df["minute_in_match"].between(start_min, end_min))
#     ]["comment_text"].tolist()
    
#     return extract_important_events(df, match_comments)


def extract_player_summary(df, player_name):
    # Lọc bình luận liên quan đến cầu thủ
    player_data = df[
        df["comment_text"].str.contains(player_name, case=False, na=False)
    ]

    if player_data.empty:
        return f"Không có dữ liệu cho {player_name}."

    # Gộp tất cả bình luận thành một đoạn văn bản duy nhất
    combined_text = " ".join(player_data["comment_text"].tolist())[:800]  # Giới hạn 4000 ký tự

    # Tạo prompt tổng quát thay vì theo từng vòng
    prompt = f"Tóm tắt phong độ tổng quát của {player_name} trong mùa giải dựa trên các bình luận: {combined_text}"
    response = model.generate_content(prompt)

    return response.text

def compare_players(df, player1, player2):
    summary1 = extract_player_summary(df, player1)
    summary2 = extract_player_summary(df, player2)

    # Thống kê số lượng bình luận theo cảm xúc
    def get_sentiment_stats(df, player_name):
        player_data = df[
            df["comment_text"].str.contains(player_name, case=False, na=False)
        ]
        sentiment_counts = player_data["Sentiment"].value_counts(normalize=True) * 100
        return f"Tích cực: {sentiment_counts.get('Positive', 0):.1f}%, Trung lập: {sentiment_counts.get('Neutral', 0):.1f}%, Tiêu cực: {sentiment_counts.get('Negative', 0):.1f}%"

    stats1 = get_sentiment_stats(df, player1)
    stats2 = get_sentiment_stats(df, player2)

    prompt = f"""So sánh phong độ của {player1} và {player2} dựa trên nhận xét của fan:
    
    {player1}:
    - Tóm tắt: {summary1}
    - Thống kê cảm xúc: {stats1}
    
    {player2}:
    - Tóm tắt: {summary2}
    - Thống kê cảm xúc: {stats2}
    
    Đưa ra nhận xét tổng quan và đánh giá cầu thủ nào đang có phong độ tốt hơn dựa trên dữ liệu trên."""
    
    response = model.generate_content(prompt)
    
    return response.text

def analyze_team_sentiment(df, team_name):
    team_data = df[
        df["comment_text"].str.contains(team_name, case=False, na=False)
    ]

    if team_data.empty:
        return f"Không có dữ liệu về {team_name}."

    sentiment_counts = team_data["Sentiment"].value_counts(normalize=True) * 100
    stats = f"Tích cực: {sentiment_counts.get('Positive', 0):.1f}%, Trung lập: {sentiment_counts.get('Neutral', 0):.1f}%, Tiêu cực: {sentiment_counts.get('Negative', 0):.1f}%"
    
    prompt = f"Fan nói gì về {team_name} dựa trên dữ liệu bình luận?\n{stats}"
    response = model.generate_content(prompt)
    
    return response.text

def most_dramatic_match(df):
    dramatic_matches = df.groupby(["matchday", "home_team", "away_team"])["Sentiment"].apply(
        lambda x: (x == "Positive").sum() + (x == "Negative").sum()
    )

    top_match = dramatic_matches.idxmax()
    matchday, home_team, away_team = top_match
    return f"Trận đấu có nhiều drama nhất là {home_team} vs {away_team} (vòng {matchday}) với {dramatic_matches[top_match]} bình luận cảm xúc mạnh."




def football_chatbot(df):
    st.sidebar.title("⚽ Chatbot bóng đá")
    st.sidebar.write("Nhập câu hỏi về trận đấu, cầu thủ, hoặc đội bóng.")

    # Lưu trạng thái hội thoại
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "query" not in st.session_state:
        st.session_state["query"] = None
    if "pending_action" not in st.session_state:
        st.session_state["pending_action"] = None
    if "response" not in st.session_state:
        st.session_state["response"] = None

    # Hiển thị lịch sử chat trong sidebar
    with st.sidebar:
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # Nhập câu hỏi mới
    query = st.sidebar.text_input("Nhập câu hỏi...", key=f"query_{len(st.session_state['messages'])}")

    if st.sidebar.button("OK") and query:
        st.session_state["messages"].append({"role": "user", "content": query})
        st.session_state["query"] = query  
        st.session_state["response"] = None  

    # Nếu có query nhưng chưa xác định hành động, xử lý câu hỏi
    if st.session_state["query"] and not st.session_state["pending_action"]:
        process_question(df, st.session_state["query"])
        st.session_state["query"] = None  

    # Nếu cần thông tin bổ sung (cầu thủ/đội), yêu cầu nhập tiếp
    if st.session_state["pending_action"]:
        handle_pending_action(df)

    # Nếu chatbot đã có câu trả lời, rerun để nhập câu tiếp theo
    if st.session_state.get("response"):
        st.session_state["messages"].append({"role": "assistant", "content": st.session_state["response"]})
        st.session_state["response"] = None  
        time.sleep(1)

        # Giữ trạng thái messages khi rerun
        st.session_state["prev_messages"] = st.session_state["messages"].copy()
        # st.rerun()


def process_question(df, query):
    """Xác định loại câu hỏi và lưu vào pending_action nếu cần thêm thông tin."""
    questions = {
        "đánh giá cầu thủ": "extract_player_summary",
        "phong độ cầu thủ": "extract_player_summary",
        "so sánh cầu thủ": "compare_players",
        "tổng quan đội bóng": "analyze_team_sentiment",
        "drama trận đấu": "most_dramatic_match",
        "trận kịch tính": "most_dramatic_match"
    }

    best_match, score = process.extractOne(query, questions.keys())
    action = questions[best_match] if score > 60 else None

    if action:
        if action in ["extract_player_summary", "compare_players", "analyze_team_sentiment"]:
            st.session_state["pending_action"] = action  
        else:
            with st.sidebar:
                with st.spinner("⏳ Đang xử lý..."):
                    time.sleep(1)  
                    st.session_state["response"] = most_dramatic_match(df)  
    else:
        with st.sidebar:
            with st.spinner("🔍 Đang hỏi Gemini..."):
                  
                response = model.generate_content(query) 
                st.session_state["response"] = response.text if response else "Xin lỗi, tôi chưa có câu trả lời phù hợp!"

def handle_pending_action(df):
    """Yêu cầu người dùng nhập thêm thông tin nếu cần."""
    action = st.session_state["pending_action"]

    with st.sidebar:  # Đảm bảo tất cả phần này nằm trong sidebar
        if action == 'extract_player_summary':
            player_name = st.text_input("Nhập tên cầu thủ:")
            if st.button("Tóm tắt") and player_name:
                with st.spinner("⏳ Đang xử lý..."):
                    time.sleep(1)
                    st.session_state["response"] = extract_player_summary(df, player_name)
                st.session_state["pending_action"] = None  

        elif action == 'compare_players':
            player1 = st.text_input("Nhập cầu thủ 1:")
            player2 = st.text_input("Nhập cầu thủ 2:")
            if st.button("So sánh") and player1 and player2:
                with st.spinner("⏳ Đang xử lý..."):
                    time.sleep(1)
                    st.session_state["response"] = compare_players(df, player1, player2)
                st.session_state["pending_action"] = None  

        elif action == 'analyze_team_sentiment':
            team_name = st.text_input("Nhập tên đội bóng:")
            if st.button("Phân tích") and team_name:
                with st.spinner("⏳ Đang xử lý..."):
                    time.sleep(1)
                    st.session_state["response"] = analyze_team_sentiment(df, team_name)
                st.session_state["pending_action"] = None  