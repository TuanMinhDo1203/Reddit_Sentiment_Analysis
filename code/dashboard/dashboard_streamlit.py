import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
import match_page
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from matplotlib.patches import Rectangle
import base64
import os


# Load real data (similar to match_page.py)
@st.cache_data
def load_sentiment_data():
    df_sentiment = pd.read_csv("nonan_goodformat_comment_data.csv")
    df_sentiment["match_time"] = pd.to_datetime(df_sentiment["match_time"])
    return df_sentiment

@st.cache_data
def load_match_data():
    df_match = pd.read_csv("nonan_goodformat_match_data.csv")
    df_match["Date"] = pd.to_datetime(df_match["Date"])
    return df_match

@st.cache_data
def load_data():
    df = pd.read_csv("full_comments_sentiment_updated.csv")
    df["match_time"] = pd.to_datetime(df["match_time"])
    return df

st.set_page_config(page_title="Football Sentiment Analysis", layout="wide")

# Load data
df = load_sentiment_data()
df_match = load_match_data()
dfs = load_data()

def add_snowfall_effect():
    # Check if the image exists
    image_path = 'Filled.png'
    if not os.path.exists(image_path):
        st.warning("Image not found. Snowfall effect will use a default image.")
        snowflake_image = "https://via.placeholder.com/30"  # Fallback image
    else:
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        snowflake_image = f"data:image/png;base64,{encoded}"

    # CSS-only snowfall effect (more reliable in Streamlit)
    st.markdown(
        f"""
        <style>
        .snowflake-container {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 9999;
        }}
        .snowflake {{
            position: absolute;
            width: 30px;
            height: 30px;
            background: url('{snowflake_image}') no-repeat center center;
            background-size: contain;
            opacity: 0.8;
            animation: fall linear infinite;
        }}
        .stApp {{
            background: #1E1E1E;  /* Dark background to match the theme */
            color: white;
        }}
        @keyframes fall {{
            0% {{ opacity: 0; transform: translateY(-20vh); }}
            20% {{ opacity: 1; }}
            100% {{ opacity: 0; transform: translateY(100vh); }}
        }}
        /* Define multiple snowflakes with different positions and delays */
        .snowflake:nth-child(1) {{ left: 5%; animation-duration: 10s; animation-delay: 0s; }}
        .snowflake:nth-child(2) {{ left: 15%; animation-duration: 12s; animation-delay: 1s; }}
        .snowflake:nth-child(3) {{ left: 25%; animation-duration: 8s; animation-delay: 2s; }}
        .snowflake:nth-child(4) {{ left: 35%; animation-duration: 11s; animation-delay: 0s; }}
        .snowflake:nth-child(5) {{ left: 45%; animation-duration: 9s; animation-delay: 3s; }}
        .snowflake:nth-child(6) {{ left: 55%; animation-duration: 10s; animation-delay: 1s; }}
        .snowflake:nth-child(7) {{ left: 65%; animation-duration: 13s; animation-delay: 2s; }}
        .snowflake:nth-child(8) {{ left: 75%; animation-duration: 7s; animation-delay: 0s; }}
        .snowflake:nth-child(9) {{ left: 85%; animation-duration: 10s; animation-delay: 3s; }}
        .snowflake:nth-child(10) {{ left: 95%; animation-duration: 12s; animation-delay: 1s; }}
        </style>
        <div class="snowflake-container">
            <div class="snowflake"></div>
            <div class="snowflake"></div>
            <div class="snowflake"></div>
            <div class="snowflake"></div>
            <div class="snowflake"></div>
            <div class="snowflake"></div>
            <div class="snowflake"></div>
            <div class="snowflake"></div>
            <div class="snowflake"></div>
            <div class="snowflake"></div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Apply the snowfall effect with error handling
try:
    add_snowfall_effect()
except Exception as e:
    st.warning(f"Failed to apply snowfall effect: {str(e)}. Continuing without the effect.")



# Merge match data with sentiment data to get matchday info
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
    sentiment_by_match = df.groupby(['match', 'Sentiment']).size().reset_index(name='count')
    fig = px.bar(sentiment_by_match, x='match', y='count', color='Sentiment', 
                 barmode='group', title="Sentiment Distribution Across Matches")
    st.plotly_chart(fig)

# Page 2: Sentiment Trận đấu
elif page == "Sentiment Trận đấu":
    match_page.display_match_sentiment()

# Page 3: Chi tiết Post & Comment
elif page == "Chi tiết Post & Comment":
    st.title("Chi tiết Bài Post & Comment")
    st.subheader("Danh sách Post và Comment")
    st.dataframe(df[['post_id', 'comment_id', 'comment', 'comment_author', 'Sentiment', 'Compound']])

# Page 4: Sentiment Đội Bóng (Nguồn 3)
elif page == "Sentiment Đội Bóng":
    st.title("Sentiment Đội Bóng")

    # Requirement 3: Ranking Đội theo Sentiment (At the top)
    st.subheader("Ranking Đội theo Sentiment")

    # Cache the computation of combined scores
    @st.cache_data
    def compute_combined_scores(df):
        home_scores = df.groupby('home_team')['Compound'].mean().reset_index()
        home_scores = home_scores.rename(columns={'home_team': 'team'})
        away_scores = df.groupby('away_team')['Compound'].mean().reset_index()
        away_scores = away_scores.rename(columns={'away_team': 'team'})
        combined_scores = pd.concat([home_scores, away_scores]).groupby('team')['Compound'].mean().reset_index()
        combined_scores = combined_scores.sort_values(by='Compound', ascending=False).reset_index(drop=True)
        combined_scores['Rank'] = combined_scores.index + 1
        return combined_scores

    combined_scores = compute_combined_scores(dfs)

    # Modern styling for the table
    def style_ranking_table(df):
        if df.empty:
            return "<p>No data available to display the ranking table.</p>"

        html = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
        .ranking-container {
            display: flex;
            align-items: stretch;
            gap: 20px;
        }
        .table-container {
            flex: 1;
            min-height: 400px;
        }
        .chart-container {
            flex: 2;
            min-height: 400px;
            overflow: hidden;
        }
        .modern-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            font-family: 'Poppins', Arial, sans-serif;
            background-color: #2A2A2A;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }
        .modern-table th, .modern-table td {
            padding: 15px;
            text-align: center;
            color: #FFFFFF;  /* Changed to white */
            border-bottom: 1px solid #3A3A3A;
            transition: background-color 0.3s ease;
        }
        .modern-table th {
            background: linear-gradient(135deg, #4B1248, #7D2463);
            color: #FF69B4;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .modern-table tr:last-child td {
            border-bottom: none;
        }
        .modern-table tr:nth-child(even) {
            background-color: #333333;
        }
        .modern-table tr:hover {
            background-color: #444444;
            cursor: pointer;
        }
        .modern-table .top1 {
            background: linear-gradient(135deg, #FFD700, #FFC107);
            color: #FFFFFF;  /* Changed to white */
            font-weight: 600;
        }
        .modern-table .top2 {
            background: linear-gradient(135deg, #C0C0C0, #B0B0B0);
            color: #FFFFFF;  /* Changed to white */
            font-weight: 600;
        }
        .modern-table .top3 {
            background: linear-gradient(135deg, #CD7F32, #B87333);
            color: #FFFFFF;  /* Changed to white */
            font-weight: 600;
        }
        </style>
        <div class="table-container">
        <table class='modern-table'>
        <tr>
            <th>RANK</th>
            <th>TEAM</th>
            <th>COMPOUND</th>
        </tr>
        """

        for idx, row in df.iterrows():
            rank = row['Rank']
            team = row['team']
            compound = f"{row['Compound']:.4f}"
            # Apply special styling for top 3
            row_class = "top1" if rank == 1 else "top2" if rank == 2 else "top3" if rank == 3 else ""
            html += f"<tr class='{row_class}'>"
            html += f"<td>{rank}</td>"
            html += f"<td>{team}</td>"
            html += f"<td>{compound}</td>"
            html += "</tr>"

        html += "</table></div>"
        return html

    # Use st.columns with a custom container to ensure proper layout
    st.markdown('<div class="ranking-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(style_ranking_table(combined_scores), unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        if not combined_scores.empty:
            fig_ranking = px.bar(combined_scores, x='Compound', y='team', orientation='h',
                                 title="Sentiment Score by Team",
                                 color='Compound',
                                 color_continuous_scale='Viridis')
            fig_ranking.update_layout(yaxis={'tickmode': 'linear'}, showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_ranking, use_container_width=True)
        else:
            st.write("No data available to display the ranking chart.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Interactive elements
    st.subheader("Chọn đội")
    teams = pd.concat([dfs['home_team'], dfs['away_team']]).unique()
    selected_teams = st.multiselect("Chọn các đội để so sánh:", teams, default=["Manchester United"])
    team_data = dfs[dfs['home_team'].isin(selected_teams) | dfs['away_team'].isin(selected_teams)]

    # Matchday slider (range selection)
    matchdays = sorted(dfs['matchday'].unique())
    if len(matchdays) > 1:
        matchday_range = st.slider("Chọn khoảng vòng đấu:", 
                                   min_value=int(min(matchdays)), 
                                   max_value=int(max(matchdays)), 
                                   value=(int(min(matchdays)), int(max(matchdays))))
        start_matchday, end_matchday = matchday_range
        team_data = team_data[(team_data['matchday'] >= start_matchday) & (team_data['matchday'] <= end_matchday)]
    else:
        st.write("Only one matchday available.")
        start_matchday, end_matchday = matchdays[0], matchdays[0]

    # Requirement 1: Tổng hợp Sentiment theo Đội (Using Matplotlib with solid colors for all bars)
    st.subheader("Tổng hợp Sentiment theo Đội")
    display_mode = st.radio("Hiển thị dưới dạng:", ("Số lượng", "Tỷ lệ phần trăm"))
    
    # Cache the team sentiment computation
    @st.cache_data
    def compute_team_sentiment(team_data, display_mode):
        team_sentiment = team_data.groupby(['home_team', 'Sentiment']).size().reset_index(name='count')
        if display_mode == "Tỷ lệ phần trăm":
            total_comments = team_sentiment.groupby('home_team')['count'].sum().reset_index(name='total')
            team_sentiment = team_sentiment.merge(total_comments, on='home_team')
            team_sentiment['percentage'] = (team_sentiment['count'] / team_sentiment['total']) * 100
            y_axis = 'percentage'
            y_title = "Percentage of Comments (%)"
        else:
            y_axis = 'count'
            y_title = "Number of Comments"
        return team_sentiment, y_axis, y_title

    team_sentiment, y_axis, y_title = compute_team_sentiment(team_data, display_mode)

    # Create a Matplotlib figure for each team
    for team in selected_teams:
        team_subset = team_sentiment[team_sentiment['home_team'] == team]
        sentiments = ['Negative', 'Neutral', 'Positive']
        values = [team_subset[team_subset['Sentiment'] == s][y_axis].iloc[0] if s in team_subset['Sentiment'].values else 0 for s in sentiments]

        # Create the bar chart
        fig, ax = plt.subplots(figsize=(8, 4))
        bar_width = 0.8
        x_positions = np.arange(len(sentiments))

        # Use solid colors for all bars
        for i, (sentiment, value) in enumerate(zip(sentiments, values)):
            color = '#EF553B' if sentiment == 'Negative' else '#636EFA' if sentiment == 'Neutral' else '#00CC96'
            ax.bar(i, value, bar_width, color=color)

        ax.set_xticks(x_positions)
        ax.set_xticklabels(sentiments)
        ax.set_title(f"Sentiment Distribution for {team}").set_color('#FFFFFF')
        ax.set_xlabel("Sentiment").set_color('#FF69B4')
        ax.set_ylabel(y_title)
        ax.set_facecolor('#1E1E1E')  # Match the dark theme
        fig.patch.set_facecolor('#1E1E1E')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        # Format y-axis to avoid scientific notation
        ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))
        st.pyplot(fig)
        plt.close(fig)

    # Requirement 2: Sentiment for the Selected Matchday Range
    st.subheader(f"Sentiment for Matchdays {start_matchday} to {end_matchday}")
    team_sentiment_by_matchday = team_data.groupby(['matchday', 'Sentiment', 'home_team']).size().reset_index(name='count')
    # Filter for the selected matchday range (already filtered in team_data, but ensuring clarity)
    team_sentiment_by_matchday = team_sentiment_by_matchday[
        (team_sentiment_by_matchday['matchday'] >= start_matchday) & 
        (team_sentiment_by_matchday['matchday'] <= end_matchday)
    ]
    
    if not team_sentiment_by_matchday.empty:
        fig_trend = px.bar(team_sentiment_by_matchday, x='count', y='home_team', color='Sentiment',
                           title=f"Sentiment Distribution for Matchdays {start_matchday} to {end_matchday}",
                           color_discrete_map={'Positive': '#00CC96', 'Negative': '#EF553B', 'Neutral': '#636EFA'})
        fig_trend.update_layout(xaxis_title="Number of Comments", yaxis_title="Team")
        st.plotly_chart(fig_trend)
    else:
        st.write("No data available for the selected matchday range and teams.")