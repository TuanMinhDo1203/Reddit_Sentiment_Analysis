import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

def display_team_sentiment(dfs):
    # Debug: Check available columns
    required_columns = ['matchday', 'home_team', 'away_team', 'Sentiment', 'Compound']
    missing_columns = [col for col in required_columns if col not in dfs.columns]
    if missing_columns:
        st.error(f"Error: The following required columns are missing in the dataset: {missing_columns}. Available columns: {dfs.columns.tolist()}")
        st.stop()

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
            color: #FFFFFF;
            border-bottom: 1px solid #3A3A3A;
            transition: background-color 0.3s ease;
        }
        .modern-table th {
            background: linear-gradient(135deg, #4B1248, #7D2463);
            color: #FFFFFF;
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
            color: #FFFFFF;
            font-weight: 600;
        }
        .modern-table .top2 {
            background: linear-gradient(135deg, #C0C0C0, #B0B0B0);
            color: #FFFFFF;
            font-weight: 600;
        }
        .modern-table .top3 {
            background: linear-gradient(135deg, #CD7F32, #B87333);
            color: #FFFFFF;
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

    # Requirement 1: Tổng hợp Sentiment theo Đội (Using Matplotlib with image pattern for Positive bars)
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

    # Load the image for the Positive bar
    image_path = 'Filled.png'
    try:
        img = mpimg.imread(image_path)
        # Ensure the image is in RGBA format
        if img.shape[-1] != 4:
            img = np.dstack((img, np.ones(img.shape[:2]) * 255))  # Add alpha channel if needed
    except FileNotFoundError:
        st.warning("Image not found for Positive bars. Using default color instead.")
        img = None

    # Create a Matplotlib figure for each team
    for team in selected_teams:
        team_subset = team_sentiment[team_sentiment['home_team'] == team]
        sentiments = ['Negative', 'Neutral', 'Positive']
        values = [team_subset[team_subset['Sentiment'] == s][y_axis].iloc[0] if s in team_subset['Sentiment'].values else 0 for s in sentiments]

        # Create the bar chart
        fig, ax = plt.subplots(figsize=(8, 4))
        bar_width = 0.8
        x_positions = np.arange(len(sentiments))

        # Draw bars, using the image as a pattern for the Positive bar
        for i, (sentiment, value) in enumerate(zip(sentiments, values)):
            if sentiment == 'Positive' and img is not None:
                # Create a texture from the image
                bar = ax.bar(i, value, bar_width, color='white')  # Placeholder color
                bar_height = bar[0].get_height()
                bar_width_actual = bar[0].get_width()
                bar_x = bar[0].get_x()
                bar_y = bar[0].get_y()

                # Create an extent for the image to fill the entire bar
                extent = [bar_x, bar_x + bar_width_actual, 0, bar_height]
                ax.imshow(img, extent=extent, aspect='auto', zorder=bar[0].zorder + 1)
            else:
                color = '#EF553B' if sentiment == 'Negative' else '#636EFA' if sentiment == 'Neutral' else '#00CC96'
                ax.bar(i, value, bar_width, color=color)

        ax.set_xticks(x_positions)
        ax.set_xticklabels(sentiments)
        ax.set_title(f"Sentiment Distribution for {team}").set_color('#FF69B4')
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