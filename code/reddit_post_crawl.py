import praw
import pandas as pd
from datetime import datetime

def init_reddit():
    return praw.Reddit(
        client_id="3Lk6D3zzN-6VJ91Qw8-WUQ",
        client_secret="TsHTQgd2Pic6bT6qzippkLmqrPKZYw",
        user_agent="Ok-Bill-8363",
        request_timeout=90
    )

def load_dataframe(filename):
    df = pd.read_csv(filename)
    df["DateTime"] = pd.to_datetime(df["utc_date"], format="%Y-%m-%d %H:%M:%S")
    return df

def clean_team_name(team_name):
    return team_name.replace("FC", "").strip()

def search_match_threads(reddit, df_matches, max_matchday=19):
    posts = []
    
    for _, row in df_matches.iterrows():
        home_team = clean_team_name(row["home_team"])
        away_team = clean_team_name(row["away_team"])
        match_time = row["DateTime"]
        match_day = row["matchday"]

        search_query = f"(Author:MatchThreadder {home_team} vs {away_team}) OR ({home_team} v {away_team})"
        
        if match_day <= max_matchday:
            for submission in reddit.subreddit("soccer").search(search_query, sort="relevance", time_filter="year"):
                post_date = datetime.utcfromtimestamp(submission.created_utc)
                
                if abs((post_date - match_time).total_seconds()) <= 7200 and "Match Thread" in submission.title:
                    posts.append({
                        "home_team": home_team,
                        "away_team": away_team,
                        "match_time": match_time.strftime('%Y-%m-%d %H:%M'),
                        "post_date": post_date.strftime('%Y-%m-%d %H:%M'),
                        "title": submission.title,
                        "url": submission.url,
                        "upvotes": submission.score,
                        "comments": submission.num_comments,
                        "submission_id": submission.id
                    })
    
    return pd.DataFrame(posts)

def save_to_csv(df, filename):
    df.to_csv(filename, index=False)

def main():
    reddit = init_reddit()
    df_matches = load_dataframe("finished_matches.csv")
    df_posts = search_match_threads(reddit, df_matches)
    save_to_csv(df_posts, "match_threads_output.csv")
    print("Finished! Data saved to match_threads_output.csv")

if __name__ == "__main__":
    main()
