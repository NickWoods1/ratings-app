import streamlit as st

from utils.db import get_supabase

supabase = get_supabase()

st.markdown(
    "<h1 style='text-align: center;'>🏆 ELO Ratings Leaderboard</h1>",
    unsafe_allow_html=True,
)

# Load items and elo_battles from the database
items = supabase.table("items").select("*").execute().data
elo_battles = supabase.table("elo_battles").select("*").execute().data

# Initialize ratings and win-loss records
elo_ratings = {item["id"]: 1500 for item in items}
win_loss_record = {item["id"]: {"wins": 0, "losses": 0} for item in items}

# Calculate current ELO ratings and win-loss records from elo_battles history
for battle in sorted(elo_battles, key=lambda x: x["created_at"]):
    winner_id = battle["winner_item_id"]
    loser_id = battle["loser_item_id"]

    elo_ratings[winner_id] = battle["winner_new_rating"]
    elo_ratings[loser_id] = battle["loser_new_rating"]

    win_loss_record[winner_id]["wins"] += 1
    win_loss_record[loser_id]["losses"] += 1

# Construct leaderboard
leaderboard = []
for item in items:
    wins = win_loss_record[item["id"]]["wins"]
    losses = win_loss_record[item["id"]]["losses"]
    leaderboard.append(
        {
            "name": item["object_name"],
            "elo_rating": elo_ratings.get(item["id"], 1500),
            "image_url": item["image_url"],
            "wins": wins,
            "losses": losses,
        }
    )

# Sort leaderboard by ELO rating descending
leaderboard.sort(key=lambda x: x["elo_rating"], reverse=True)

# Display the leaderboard
for rank, entry in enumerate(leaderboard, start=1):
    st.markdown(
        f"### #{rank}: {entry['name']} — {entry['elo_rating']:.2f} ELO ({entry['wins']}W - {entry['losses']}L)"
    )
