import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import plotly.express as px
import matplotlib.pyplot as plt
from pathlib import Path
# Hàm tải dữ liệu với caching
@st.cache_data
def load_match_data():
    path = Path("Reddit_Sentiment_Analysis/dataframe/source_dashboard/nonan_goodformat_match_data.csv")
    df_match = pd.read_csv(path)
    df_match["Date"] = pd.to_datetime(df_match["Date"])
    return df_match

@st.cache_data
def load_sentiment_data():
    path = Path("Reddit_Sentiment_Analysis/dataframe/source_dashboard/nonan_goodformat_comment_data.csv")
    df_sentiment = pd.read_csv(path)
    df_sentiment["match_time"] = pd.to_datetime(df_sentiment["match_time"])
    return df_sentiment

# Hàm vẽ biểu đồ phân phối sentiment tổng thể
def plot_sentiment_distribution(df_sentiment):
    sentiment_counts = df_sentiment['Sentiment'].value_counts()
    fig = px.pie(sentiment_counts, 
                 values=sentiment_counts.values, 
                 names=sentiment_counts.index, 
                 title='Phân phối Sentiment Tổng thể',
                 height=400)
    fig.update_layout(template='plotly_dark')
    return fig

# Các hàm vẽ biểu đồ theo chế độ xem khác nhau
@st.cache_data
def plot_comments_by_matchday(df):
    df['match'] = df['home_team'] + " vs " + df['away_team']
    comments_by_matchday = df.groupby('matchday').agg({'comment_id': 'count'}).reset_index()
    
    fig = px.bar(
        comments_by_matchday, 
        x='matchday', 
        y='comment_id', 
        title='Số lượng Bình luận Theo Matchday',
        labels={'matchday': 'Matchday', 'comment_id': 'Số lượng Bình luận'},
        height=400
    )
    fig.update_layout(template='plotly_dark')
    return fig

@st.cache_data
def plot_comments_by_weekday(df):
    df['weekday'] = df['match_time'].dt.day_name()
    comments_by_weekday = df.groupby('weekday')['comment_id'].count().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    ).reset_index()
    
    fig = px.bar(comments_by_weekday, 
                 x='weekday', 
                 y='comment_id', 
                 title='Số lượng Bình luận Theo Thứ Trong Tuần',
                 labels={'weekday': 'Thứ Trong Tuần', 'comment_id': 'Số lượng Bình luận'},
                 height=400)
    fig.update_layout(template='plotly_dark')
    return fig

@st.cache_data
def plot_comments_by_hour(df):
    df['hour'] = df['match_time'].dt.hour
    comments_by_hour = df.groupby('hour')['comment_id'].count().reset_index()
    all_hours = pd.DataFrame({'hour': list(range(24))})
    comments_by_hour = all_hours.merge(comments_by_hour, on='hour', how='left').fillna(0)
    
    fig = px.bar(comments_by_hour, 
                 x='hour', 
                 y='comment_id', 
                 title='Số lượng Bình luận Theo Giờ Trong Ngày',
                 labels={'hour': 'Giờ Trong Ngày', 'comment_id': 'Số lượng Bình luận'},
                 height=400)
    fig.update_xaxes(dtick=1, tickvals=list(range(24)), tickformat='%H')
    fig.update_layout(template='plotly_dark')
    return fig

@st.cache_data
def plot_comments_by_minute_in_the_match(df):
    comments_by_minute = df.groupby('minute_in_match')['comment_id'].count().reset_index()
    fig = px.line(comments_by_minute, 
                  x='minute_in_match', 
                  y='comment_id', 
                  title="Số lượng Bình luận Theo Phút Trong Trận",
                  labels={'minute_in_match': 'Phút trong Trận', 'comment_id': 'Số lượng Bình luận'})
    fig.update_layout(template='plotly_dark')
    return fig

# Biểu đồ của các trận đấu có lượng comment nhiều nhất
@st.cache_data
def plot_team_sentiment(df):
    df['match_name'] = df['home_team'] + ' vs ' + df['away_team']
    match_comment_counts = df['match_name'].value_counts().nlargest(10).reset_index()
    match_comment_counts.columns = ['match_name', 'comment_count']
    
    fig = px.bar(match_comment_counts, 
                 x='comment_count', 
                 y='match_name', 
                 orientation='h', 
                 title='Top 10 Trận đấu Nhận được Nhiều Bình luận Nhất',
                 height=600)
    fig.update_layout(template='plotly_dark', yaxis=dict(autorange="reversed"))
    return fig

# Hàm vẽ word cloud
def plot_wordcloud(df):
    text = " ".join(comment for comment in df['comment_text'].dropna())
    wordcloud = WordCloud(width=800, height=400, background_color='black', colormap='viridis').generate(text)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    plt.title("Word Cloud of Comments", fontsize=16)
    st.pyplot(fig)

# Main function to display the dashboard
def display_overview():
    df_match = load_match_data()
    df_sentiment = load_sentiment_data()

    df_merged = pd.merge(df_sentiment, df_match[['home_team', 'away_team']], 
                         on=['home_team', 'away_team'], how='left')

    st.title("📈 Sentiment Overview")

    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Comments", len(df_sentiment))
    with col2:
        st.metric("Average Sentiment", f"{df_sentiment['Compound'].mean():.2f}")
    with col3:
        st.metric("Number of Matches", len(df_match))
    with col4:
        avg_comment_length = df_sentiment['comment_length'].mean()
        st.metric("Avg Comment Length", f"{avg_comment_length:.2f}")

    # Overall sentiment distribution
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribution of Sentiments")
        st.plotly_chart(plot_sentiment_distribution(df_sentiment), use_container_width=True)

    with col2:
        st.subheader("Distribution of Comments by Time")

        # Lưu trạng thái của dropdown trong session_state
        if 'selected_view' not in st.session_state:
            st.session_state.selected_view = "By Matchday"

        # Dropdown chọn chế độ xem
        option = st.selectbox(
            "Choose view mode:",
            ["By Matchday", "By Day of the Week", "By Hour of the Day", "By Minute in Match"],
            index=["By Matchday", "By Day of the Week", "By Hour of the Day", "By Minute in Match"].index(st.session_state.selected_view)
        )

        # Cập nhật trạng thái view nếu thay đổi
        if option != st.session_state.selected_view:
            st.session_state.selected_view = option

        # Hiển thị biểu đồ tương ứng
        if option == "By Matchday":
            fig = plot_comments_by_matchday(df_merged)
        elif option == "By Day of the Week":
            fig = plot_comments_by_weekday(df_merged)
        elif option == "By Hour of the Day":
            fig = plot_comments_by_hour(df_merged)
        else:
            fig = plot_comments_by_minute_in_the_match(df_sentiment)

        st.plotly_chart(fig, use_container_width=True)

    # So sánh sentiment giữa các đội
    st.header("Team Sentiment Comparison")
    st.plotly_chart(plot_team_sentiment(df_sentiment), use_container_width=True)

    # Hiển thị word cloud
    st.header("Word Cloud of Comments")
    plot_wordcloud(df_sentiment)
    # Thêm ô tìm kiếm và chế độ lọc
    st.header("🔍 Tìm kiếm Comment")

    # Ô nhập từ khóa
    search_term = st.text_input("Nhập từ cần tìm trong comment:", "").strip().lower()

    # Chọn chế độ xếp hạng
    sort_mode = st.radio("Sắp xếp kết quả theo:", ["Compound Score", "Comment Score"])

    if search_term:
        # Lọc comment chứa từ khóa
        filtered_df = df_sentiment[df_sentiment['comment_text'].str.lower().str.contains(search_term, na=False)]

        if not filtered_df.empty:
            # Phân loại Positive (Compound > 0), Negative (Compound < 0), và Neutral (Compound == 0)
            positive_comments = filtered_df[filtered_df['Compound'] > 0]
            negative_comments = filtered_df[filtered_df['Compound'] < 0]
            neutral_comments = filtered_df[filtered_df['Compound'] == 0]

            # Chọn chế độ sắp xếp
            if sort_mode == "Compound Score":
                positive_comments = positive_comments.sort_values(by='Compound', ascending=False)
                negative_comments = negative_comments.sort_values(by='Compound', ascending=True)
                neutral_comments = neutral_comments.sort_values(by='Compound', ascending=False)
            else:
                positive_comments = positive_comments.sort_values(by='comment_score', ascending=False)
                negative_comments = negative_comments.sort_values(by='comment_score', ascending=False)
                neutral_comments = neutral_comments.sort_values(by='comment_score', ascending=False)

            # Hiển thị bảng kết quả
            col1, col2, col3 = st.columns(3)
            with col1:
                st.subheader("📈 Positive Comments")
                st.dataframe(positive_comments[['comment_text', 'Compound', 'comment_score']].reset_index(drop=True), height=300)

            with col2:
                st.subheader("📉 Negative Comments")
                st.dataframe(negative_comments[['comment_text', 'Compound', 'comment_score']].reset_index(drop=True), height=300)

            with col3:
                st.subheader("😐 Neutral Comments")
                st.dataframe(neutral_comments[['comment_text', 'Compound', 'comment_score']].reset_index(drop=True), height=300)
        else:
            st.warning("Không tìm thấy comment nào chứa từ khóa này.")



    
