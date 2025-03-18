import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Load dummy data (thay bằng dữ liệu thực)
df = pd.DataFrame({
    'match': ['Match 1', 'Match 1', 'Match 2', 'Match 2'],
    'team': ['Team A', 'Team B', 'Team A', 'Team B'],
    'sentiment': ['Positive', 'Negative', 'Neutral', 'Positive'],
    'count': [120, 80, 50, 140]
})

# Thêm thông tin trận đấu
df_info = pd.DataFrame({
    'match': ['Match 1', 'Match 2'],
    'date': ['2024-03-10', '2024-03-15'],
    'location': ['Stadium A', 'Stadium B'],
    'total_comments': [500, 420]
})

app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    
    # Navigation Bar
    html.Div([
        dcc.Link('🏠 Tổng quan | ', href='/', className='nav-link'),
        dcc.Link('📊 Sentiment Trận đấu | ', href='/match', className='nav-link'),
        dcc.Link('💬 Chi tiết Post & Comment', href='/comments', className='nav-link')
    ], className='navbar'),
    
    html.Div(id='page-content', className='content')
])

# Trang 1: Tổng quan sentiment
overview_layout = html.Div([
    html.H1("Tổng quan Sentiment", className='title'),
    dcc.Graph(id='overview-chart',
              figure=px.bar(df, x='match', y='count', color='sentiment', barmode='group'))
])

# Trang 2: Sentiment theo trận
detail_layout = html.Div([
    html.H1("Sentiment theo Trận", className='title'),
    dcc.Dropdown(
        id='match-dropdown',
        options=[{'label': m, 'value': m} for m in df['match'].unique()],
        value=df['match'].unique()[0],
        clearable=False,
        className='dropdown'
    ),
    html.Div(id='match-info', className='match-info'),
    dcc.Graph(id='sentiment-bar-chart')
], className='chart-container')

@app.callback(
    Output('match-info', 'children'),
    Input('match-dropdown', 'value')
)
def update_match_info(selected_match):
    match_data = df_info[df_info['match'] == selected_match].iloc[0]
    return html.Div([
        html.P(f"📅 Ngày diễn ra: {match_data['date']}"),
        html.P(f"📍 Địa điểm: {match_data['location']}"),
        html.P(f"💬 Tổng số bình luận: {match_data['total_comments']}")
    ])

@app.callback(
    Output('sentiment-bar-chart', 'figure'),
    Input('match-dropdown', 'value')
)
def update_chart(selected_match):
    filtered_df = df[df['match'] == selected_match]
    fig = px.bar(filtered_df, x='team', y='count', color='sentiment', barmode='group',
                 title=f'Sentiment for {selected_match}')
    return fig

# Trang 3: Chi tiết post & comment
comments_layout = html.Div([
    html.H1("Chi tiết Bài Post & Comment", className='title'),
    dcc.Graph(id='comments-chart',
              figure=px.histogram(df, x='sentiment', y='count', color='team', barmode='group'))
], className='chart-container')

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/match':
        return detail_layout
    elif pathname == '/comments':
        return comments_layout
    return overview_layout

# CSS Styling
app.css.append_css({"external_url": "https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css"})

if __name__ == '__main__':
    app.run_server(debug=True)
