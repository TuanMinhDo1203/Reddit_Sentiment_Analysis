import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
from typing import Dict, Tuple

# Constants for consistent styling
COLOR_POSITIVE = '#00CC96'
COLOR_NEGATIVE = '#EF553B'
COLOR_NEUTRAL = '#636EFA'
COLOR_BACKGROUND = '#1E1E1E'
COLOR_SECONDARY = '#2A2A2A'
COLOR_ACCENT = '#FF69B4'

def setup_page() -> None:
    """Configure page settings and styles."""
    st.set_page_config(page_title="EPL Sentiment Dashboard", layout="wide")
    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: {COLOR_BACKGROUND}; color: white; }}
        .css-1aumxhk {{ background-color: {COLOR_BACKGROUND}; }}
        .metric-container {{ 
            background-color: {COLOR_SECONDARY}; 
            border-radius: 10px; 
            padding: 15px; 
            margin-bottom: 15px;
            border-left: 4px solid {COLOR_ACCENT};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def load_data() -> pd.DataFrame:
    """Load and preprocess the data."""
    dfs = pd.DataFrame({
        'matchday': np.random.randint(1, 20, 500),
        'home_team': np.random.choice(['Arsenal', 'Chelsea', 'Liverpool', 'Man Utd', 'Man City'], 500),
        'away_team': np.random.choice(['Tottenham', 'Everton', 'Leicester', 'West Ham', 'Wolves'], 500),
        'Sentiment': np.random.choice(['Positive', 'Neutral', 'Negative'], 500, p=[0.4, 0.3, 0.3]),
        'Compound': np.random.uniform(-1, 1, 500)
    })
    return dfs

def filter_data(dfs: pd.DataFrame, selected_teams: list, selected_sentiments: list, 
                start_matchday: int, end_matchday: int) -> pd.DataFrame:
    """Filter data based on user selections."""
    team_data = dfs[
        (dfs['home_team'].isin(selected_teams) | dfs['away_team'].isin(selected_teams)) &
        (dfs['Sentiment'].isin(selected_sentiments)) &
        (dfs['matchday'].between(start_matchday, end_matchday))
    ].copy()
    
    team_data['selected_team'] = np.where(
        team_data['home_team'].isin(selected_teams),
        team_data['home_team'],
        team_data['away_team']
    )
    
    return team_data

def create_ranking_table(df: pd.DataFrame) -> None:
    """Create and display a professional team ranking table with all teams."""
    st.subheader("🏆 Team Sentiment Ranking")
    
    # Calculate ranking metrics for all teams
    home_stats = df.groupby('home_team').agg({
        'Compound': ['mean', 'count'],
        'Sentiment': lambda x: (x == 'Positive').mean()
    }).reset_index()
    home_stats.columns = ['Team', 'Avg_Sentiment', 'Comment_Count', 'Positive_Rate']
    
    away_stats = df.groupby('away_team').agg({
        'Compound': ['mean', 'count'],
        'Sentiment': lambda x: (x == 'Positive').mean()
    }).reset_index()
    away_stats.columns = ['Team', 'Avg_Sentiment', 'Comment_Count', 'Positive_Rate']
    
    # Combine home and away stats
    combined_stats = pd.concat([home_stats, away_stats]).groupby('Team').mean().reset_index()
    combined_stats['Rank'] = combined_stats['Avg_Sentiment'].rank(ascending=False, method='min').astype(int)
    combined_stats = combined_stats.sort_values('Rank')
    
    # Format values
    combined_stats['Avg_Sentiment'] = combined_stats['Avg_Sentiment'].round(4)
    combined_stats['Positive_Rate'] = (combined_stats['Positive_Rate'] * 100).round(1)
    combined_stats['Comment_Count'] = combined_stats['Comment_Count'].astype(int)

    # Create a clean, modern styled DataFrame
    def color_sentiment(val):
        color = COLOR_POSITIVE if val > 0 else COLOR_NEGATIVE if val < 0 else COLOR_NEUTRAL
        return f'color: {color}; font-weight: bold'
    
    def highlight_row(row):
        if row['Rank'] == 1:
            return ['background-color: rgba(255, 215, 0, 0.15)'] * len(row)
        elif row['Rank'] == 2:
            return ['background-color: rgba(192, 192, 192, 0.15)'] * len(row)
        elif row['Rank'] == 3:
            return ['background-color: rgba(205, 127, 50, 0.15)'] * len(row)
        return [''] * len(row)
    
    # Display the table using st.dataframe with custom styling
    st.dataframe(
        combined_stats.style
        .apply(highlight_row, axis=1)
        .applymap(color_sentiment, subset=['Avg_Sentiment'])
        .format({
            'Avg_Sentiment': '{:.4f}',
            'Positive_Rate': '{:.1f}%',
            'Comment_Count': '{:,}'
        })
        .set_properties(**{
            'background-color': COLOR_SECONDARY,
            'color': 'white',
            'border': '1px solid #3A3A3A'
        })
        .set_table_styles([{
            'selector': 'th',
            'props': [('background-color', '#4B1248'), ('color', 'white'), ('font-weight', 'bold')]
        }, {
            'selector': 'tr:hover',
            'props': [('background-color', '#3A3A3A')]
        }]),
        column_config={
            "Rank": st.column_config.NumberColumn(
                "Rank",
                help="Team ranking based on sentiment",
                width="small"
            ),
            "Team": st.column_config.TextColumn(
                "Team",
                help="Team name",
                width="medium"
            ),
            "Avg_Sentiment": st.column_config.NumberColumn(
                "Avg Sentiment",
                help="Average sentiment score (-1 to 1)",
                format="%.4f",
                width="medium"
            ),
            "Positive_Rate": st.column_config.NumberColumn(
                "Positive %",
                help="Percentage of positive comments",
                format="%.1f%%",
                width="medium"
            ),
            "Comment_Count": st.column_config.NumberColumn(
                "Comments",
                help="Total number of comments",
                format="%d",
                width="medium"
            )
        },
        use_container_width=True,
        hide_index=True,
        height=(min(len(combined_stats), 35) + 3) * 35  # Dynamic height based on row count
    )
    
    st.markdown("---")

def create_sentiment_chart(data: pd.DataFrame, team: str, display_mode: str) -> px.bar:
    """Create a sentiment distribution bar chart."""
    sentiment_counts = data['Sentiment'].value_counts()
    
    if display_mode == "Tỷ lệ phần trăm":
        total = sentiment_counts.sum()
        sentiment_data = (sentiment_counts / total * 100).round(1)
        y_title = "Percentage (%)"
    else:
        sentiment_data = sentiment_counts
        y_title = "Count"
    
    viz_df = pd.DataFrame({
        'Sentiment': sentiment_data.index,
        'Value': sentiment_data.values
    })
    
    fig = px.bar(
        viz_df,
        x='Sentiment',
        y='Value',
        title=f"Sentiment Distribution for {team}",
        labels={'Value': y_title},
        color='Sentiment',
        color_discrete_map={
            'Positive': COLOR_POSITIVE,
            'Negative': COLOR_NEGATIVE,
            'Neutral': COLOR_NEUTRAL
        },
        text='Value'
    )
    
    fig.update_layout(
        plot_bgcolor=COLOR_BACKGROUND,
        paper_bgcolor=COLOR_BACKGROUND,
        font=dict(color='white'),
        height=400,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    fig.update_traces(
        texttemplate='%{text}' + ('%' if display_mode == "Tỷ lệ phần trăm" else ''),
        textposition='outside'
    )
    
    return fig

def display_sentiment_counts(data: pd.DataFrame, display_mode: str) -> None:
    """Display sentiment counts with styled formatting."""
    sentiment_counts = data['Sentiment'].value_counts()
    total = sentiment_counts.sum() if display_mode == "Tỷ lệ phần trăm" else None
    
    st.markdown("""
    <style>
    .sentiment-counts {
        font-size: 1.2em;
        padding: 15px;
        background-color: #2A2A2A;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .sentiment-counts strong {
        color: #FF69B4;
    }
    </style>
    <div class="sentiment-counts">
    <strong>Sentiment Counts:</strong><br>
    """, unsafe_allow_html=True)
    
    for sentiment in ['Positive', 'Neutral', 'Negative']:
        count = sentiment_counts.get(sentiment, 0)
        if display_mode == "Tỷ lệ phần trăm":
            percentage = (count / total * 100) if total and total > 0 else 0
            st.markdown(f"""
            <div style="margin: 5px 0;">
            {sentiment}: <span style="color: {'#00CC96' if sentiment == 'Positive' else '#EF553B' if sentiment == 'Negative' else '#636EFA'}">
            {percentage:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="margin: 5px 0;">
            {sentiment}: <span style="color: {'#00CC96' if sentiment == 'Positive' else '#EF553B' if sentiment == 'Negative' else '#636EFA'}">
            {count:,}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def create_pie_chart(data: pd.DataFrame, team: str) -> px.pie:
    """Create a sentiment pie chart."""
    fig = px.pie(
        data,
        names='Sentiment',
        title=f"Sentiment Breakdown for {team}",
        color='Sentiment',
        color_discrete_map={
            'Positive': COLOR_POSITIVE,
            'Negative': COLOR_NEGATIVE,
            'Neutral': COLOR_NEUTRAL
        },
        height=500,
        width=500
    )
    
    fig.update_layout(
        plot_bgcolor=COLOR_BACKGROUND,
        paper_bgcolor=COLOR_BACKGROUND,
        font=dict(color='white'),
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

def display_team_sentiment(dfs: pd.DataFrame) -> None:
    """Main function to display the team sentiment dashboard."""
    # Debug: Check available columns
    required_columns = ['matchday', 'home_team', 'away_team', 'Sentiment', 'Compound']
    missing_columns = [col for col in required_columns if col not in dfs.columns]
    if missing_columns:
        st.error(f"Error: Missing required columns: {missing_columns}")
        st.stop()

    st.title("EPL Team Sentiment Analysis")


    # Display mode selector
    display_mode = st.radio(
        "Display mode:", 
        ("Count", "Percentage"), 
        horizontal=True,
        key='display_mode'
    )
    display_mode = "Tỷ lệ phần trăm" if display_mode == "Percentage" else "Số lượng"

    # Create ranking table
    create_ranking_table(dfs)  # Using full dataset for ranking
    # Sidebar for Filters
    st.subheader("Team Performance Metrics")
    teams = pd.concat([dfs['home_team'], dfs['away_team']]).unique()
    selected_teams = st.multiselect(
        "Select teams:", 
        teams, 
        default=teams[:2] if len(teams) > 1 else teams[0:1],
        key='team_selector'
    )

    sentiments = ['Positive', 'Negative', 'Neutral']
    selected_sentiments = st.multiselect(
        "Select sentiments:", 
        sentiments, 
        default=sentiments,
        key='sentiment_selector'
    )

    matchdays = sorted(dfs['matchday'].unique())
    if len(matchdays) > 1:
        matchday_range = st.slider(
            "Select matchday range:", 
            min_value=int(min(matchdays)), 
            max_value=int(max(matchdays)), 
            value=(int(min(matchdays)), int(max(matchdays))),
            key='matchday_slider'
        )
        start_matchday, end_matchday = matchday_range
    else:
        st.write("Only one matchday available.")
        start_matchday, end_matchday = matchdays[0], matchdays[0]


    # Filter data
    team_data = filter_data(dfs, selected_teams, selected_sentiments, start_matchday, end_matchday)

    if not selected_teams:
        st.warning("Please select at least one team")
        return

    

    # Team performance metrics
    st.subheader("Team Performance Metrics")
    if not team_data.empty:
        # Calculate basic metrics
        metrics = team_data.groupby('selected_team').agg({
            'Compound': ['mean', 'count'],
        }).reset_index()
        metrics.columns = ['Team', 'Avg Sentiment', 'Comment Count']
        
        # Display metrics in columns
        cols = st.columns(len(selected_teams))
        for idx, team in enumerate(selected_teams):
            with cols[idx]:
                team_metrics = metrics[metrics['Team'] == team]
                if not team_metrics.empty:
                    st.markdown(f"""
                    <div class="metric-container">
                        <div style="font-size: 1.1em; margin-bottom: 10px;"><strong>{team}</strong></div>
                        <div>Avg Sentiment: {team_metrics['Avg Sentiment'].values[0]:.2f}</div>
                        <div>Total Comments: {team_metrics['Comment Count'].values[0]:,}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning(f"No data for {team}")

    # Team sentiment analysis
    st.subheader("Team Sentiment Analysis")
    for team in selected_teams:
        st.markdown(f"#### {team}")
        
        team_subset = team_data[team_data['selected_team'] == team]
        
        if not team_subset.empty:
            col1, col2 = st.columns([2, 1])
            with col1:
                fig_bar = create_sentiment_chart(team_subset, team, display_mode)
                st.plotly_chart(fig_bar, use_container_width=True)
                display_sentiment_counts(team_subset, display_mode)
                
            with col2:
                fig_pie = create_pie_chart(team_subset, team)
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.warning(f"No data available for {team}")

    # Matchday analysis
    st.subheader(f"Matchday Analysis ({start_matchday}-{end_matchday})")
    
    if not team_data.empty:
        # Sentiment by matchday
        fig_matchday = px.bar(
            team_data.groupby(['matchday', 'Sentiment']).size().reset_index(name='count'),
            x='matchday',
            y='count',
            color='Sentiment',
            title="Sentiment by Matchday",
            color_discrete_map={
                'Positive': COLOR_POSITIVE,
                'Negative': COLOR_NEGATIVE,
                'Neutral': COLOR_NEUTRAL
            },
            barmode='group'
        )
        fig_matchday.update_layout(
            plot_bgcolor=COLOR_BACKGROUND,
            paper_bgcolor=COLOR_BACKGROUND,
            font=dict(color='white'),
            height=500
        )
        st.plotly_chart(fig_matchday, use_container_width=True)
        
        # Sentiment trend over matchdays
        st.subheader("Sentiment Trend")
        fig_trend = px.line(
            team_data.groupby(['matchday', 'Sentiment']).size().reset_index(name='count'),
            x='matchday',
            y='count',
            color='Sentiment',
            title="Sentiment Trend Over Matchdays",
            color_discrete_map={
                'Positive': COLOR_POSITIVE,
                'Negative': COLOR_NEGATIVE,
                'Neutral': COLOR_NEUTRAL
            },
            markers=True
        )
        fig_trend.update_layout(
            plot_bgcolor=COLOR_BACKGROUND,
            paper_bgcolor=COLOR_BACKGROUND,
            font=dict(color='white')
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("No data available for the selected filters")

if __name__ == "__main__":
    setup_page()
    dfs = load_data()
    display_team_sentiment(dfs)