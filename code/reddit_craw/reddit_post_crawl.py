import praw
import pandas as pd
from datetime import datetime

def init_reddit():                 #### Hàm khởi tạo Reddit API
    return praw.Reddit(
        client_id="3Lk6D3zzN-6VJ91Qw8-WUQ",
        client_secret="TsHTQgd2Pic6bT6qzippkLmqrPKZYw",
        user_agent="Ok-Bill-8363",
        request_timeout=90
    )

def load_dataframe(filename):       #### Hàm load dữ liệu từ file csv
    df = pd.read_csv(filename)
    df["DateTime"] = pd.to_datetime(df["utc_date"], format="%Y-%m-%d %H:%M:%S")
    return df

def clean_team_name(team_name):   #### Hàm xử lý tên đội bóng
    return team_name.replace("FC", "").strip()

def search_match_threads(reddit, df_matches, max_matchday=19):  #### Hàm tìm các bài post trên Reddit có giới hạn ngày
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

def match_searcher(reddit, home_team, away_team, match_date, sort="relevance", time_filter="year"):  #### Hàm tìm các bài post trên Reddit có thêm thông số linh hoạt hơn
    posts = []
    
    home_team_cleaned = clean_team_name(home_team)
    away_team_cleaned = clean_team_name(away_team)

    search_query = f"(Author:MatchThreadder {home_team_cleaned} vs {away_team_cleaned}) OR ({home_team_cleaned} v {away_team_cleaned})"
    
    for submission in reddit.subreddit("soccer").search(search_query, sort=sort, time_filter=time_filter):
        post_date = datetime.utcfromtimestamp(submission.created_utc)
        time_diff = (post_date - match_date).total_seconds() / 3600  # time difference in hours
        
        if "Match Thread" in submission.title:
            posts.append({
                "home_team": home_team_cleaned,
                "away_team": away_team_cleaned,
                "match_date": match_date.strftime('%Y-%m-%d %H:%M'),
                "post_date": post_date.strftime('%Y-%m-%d %H:%M'),
                "time_diff_hours": time_diff,
                "title": submission.title,
                "url": submission.url,
                "upvotes": submission.score,
                "comments": submission.num_comments,
                "submission_id": submission.id
            })
    
    return pd.DataFrame(posts)

def find_missing_matches(df_original, df_posts):  #### Hàm tìm các trận đấu chưa có bài post
    """
    Tìm các trận đấu trong df_original nhưng không có trong df_posts.
    
    Parameters:
        df_original (pd.DataFrame): DataFrame gốc.
        df_posts (pd.DataFrame): DataFrame chứa danh sách các trận đã có bài đăng trên Reddit.
    
    Returns:
        pd.DataFrame: DataFrame chứa các trận chưa có bài đăng.
    """
    def clean_team_name(team_name):
        return team_name.replace("FC", "").strip()

    # Tạo tập hợp các trận đã có bài post
    collected_matches = set(zip(df_posts["home_team"], df_posts["away_team"]))

    # Tạo tập hợp tất cả trận đấu từ file gốc
    all_matches = set(zip(
        df_original["home_team"].apply(clean_team_name), 
        df_original["away_team"].apply(clean_team_name), 
        df_original["matchday"], 
        df_original["utc_date"]
    ))

    # Tìm các trận chưa có bài post
    missing_matches = [match for match in all_matches if (match[0], match[1]) not in collected_matches]

    # Chuyển danh sách trận chưa có post thành DataFrame
    df_missing = pd.DataFrame(missing_matches, columns=["home_team", "away_team", "matchday", "utc_date"])

    # Sắp xếp theo matchday và lọc các trận trong vòng 19 vòng đầu
    # return df_missing.sort_values(by="matchday").loc[df_missing["matchday"] <= 19] 
    return df_missing.sort_values(by="matchday")



def unique_matches(df_matches):  #### Hàm đếm số cặp trận unique

    num_unique_matches = df_matches[['home_team', 'away_team']].drop_duplicates().shape[0]
    print(f"Số cặp trận unique: {num_unique_matches}")

    return num_unique_matches


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
