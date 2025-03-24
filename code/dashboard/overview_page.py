import streamlit as st
import pandas as pd
import plotly.express as px

# Hàm tải dữ liệu với caching
@st.cache_data
def load_match_data():
    df_match = pd.read_csv(r"C:\Users\DO TUAN MINH\Desktop\ben\Learn\Reddit_Sentiment_Analysis\dataframe\source_dashboard\nonan_goodformat_match_data.csv")
    df_match["Date"] = pd.to_datetime(df_match["Date"])
    return df_match

@st.cache_data
def load_sentiment_data():
    df_sentiment = pd.read_csv(r"C:\Users\DO TUAN MINH\Desktop\ben\Learn\Reddit_Sentiment_Analysis\dataframe\source_dashboard\nonan_goodformat_comment_data.csv")
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

# Hàm vẽ biểu đồ sentiment theo thời gian (theo matchday)
def plot_sentiment_over_time(df_merged):
    sentiment_by_matchday = df_merged.groupby('matchday')['Compound'].mean().reset_index()
    fig = px.line(sentiment_by_matchday, 
                  x='matchday', 
                  y='Compound', 
                  title='Sentiment Trung bình Theo Vòng đấu',
                  height=400)
    fig.update_layout(template='plotly_dark')
    return fig

# Hàm vẽ biểu đồ so sánh sentiment giữa các đội
def plot_team_sentiment(df_sentiment):
    df_home = df_sentiment[['home_team', 'Compound']].rename(columns={'home_team': 'team'})
    df_away = df_sentiment[['away_team', 'Compound']].rename(columns={'away_team': 'team'})
    df_team_sentiment = pd.concat([df_home, df_away])
    team_avg_sentiment = df_team_sentiment.groupby('team')['Compound'].mean().reset_index()
    team_avg_sentiment = team_avg_sentiment.sort_values('Compound', ascending=False)
    fig = px.bar(team_avg_sentiment, 
                 x='team', 
                 y='Compound', 
                 title='Sentiment Trung bình Theo Đội',
                 height=600)
    fig.update_layout(template='plotly_dark')
    return fig

# Hàm vẽ biểu đồ các trận đấu nổi bật theo sentiment
def plot_top_matches(df_sentiment):
    df_sentiment['match_name'] = df_sentiment['home_team'] + ' vs ' + df_sentiment['away_team']
    match_avg_sentiment = df_sentiment.groupby('match_name')['Compound'].mean().reset_index()
    top_positive = match_avg_sentiment.nlargest(5, 'Compound')
    top_negative = match_avg_sentiment.nsmallest(5, 'Compound')
    top_matches = pd.concat([top_positive, top_negative]).sort_values('Compound', ascending=False)
    fig = px.bar(top_matches, 
                 x='Compound', 
                 y='match_name', 
                 orientation='h', 
                 title='Các Trận đấu Nổi bật Theo Sentiment',
                 color='Compound', 
                 color_continuous_scale='RdYlGn',
                 height=500)
    fig.update_layout(template='plotly_dark')
    return fig

# Hàm chính để hiển thị trang tổng quan
def display_overview():
    # Tải dữ liệu
    df_match = load_match_data()
    df_sentiment = load_sentiment_data()
    
    # Gộp dữ liệu để lấy thông tin matchday
    df_merged = pd.merge(df_sentiment, 
                         df_match[['home_team', 'away_team', 'matchday']], 
                         on=['home_team', 'away_team'], 
                         how='left')
    
    # Tiêu đề trang
    st.title("📈 Tổng quan Sentiment")
    
    # Hiển thị các số liệu chính
    total_comments = len(df_sentiment)
    avg_compound = df_sentiment['Compound'].mean()
    num_matches = len(df_match)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tổng số Bình luận", total_comments)
    with col2:
        st.metric("Sentiment Trung bình", f"{avg_compound:.2f}")
    with col3:
        st.metric("Số Trận đấu", num_matches)
    
    # Phân phối sentiment tổng thể
    st.header("Phân phối Sentiment Tổng thể")
    fig_pie = plot_sentiment_distribution(df_sentiment)
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Sentiment theo thời gian
    st.header("Sentiment Theo Thời gian")
    fig_line = plot_sentiment_over_time(df_merged)
    st.plotly_chart(fig_line, use_container_width=True)
    
    # So sánh sentiment giữa các đội
    st.header("So sánh Sentiment Các Đội")
    fig_bar = plot_team_sentiment(df_sentiment)
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Các trận đấu nổi bật theo sentiment
    st.header("Các Trận đấu Nổi bật Theo Sentiment")
    fig_top_matches = plot_top_matches(df_sentiment)
    st.plotly_chart(fig_top_matches, use_container_width=True)

# Chạy hàm chính nếu file được chạy độc lập
if __name__ == "__main__":
    display_overview()