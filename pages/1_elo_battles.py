import random

import streamlit as st

from utils.db import get_supabase

supabase = get_supabase()

st.markdown(
    "<h1 style='text-align: center;'>⚔️ ELO Rating Battles</h1>", unsafe_allow_html=True
)

# Load items and ELO battles from the database
items = supabase.table("items").select("*").execute().data
elo_battles = supabase.table("elo_battles").select("*").execute().data

# Calculate current ELO ratings
elo_ratings = {item["id"]: 1500 for item in items}

for battle in elo_battles:
    elo_ratings[battle["winner_item_id"]] = battle["winner_new_rating"]
    elo_ratings[battle["loser_item_id"]] = battle["loser_new_rating"]


def expected_score(rating1, rating2):
    return 1 / (1 + 10 ** ((rating2 - rating1) / 400))


def update_elo(winner_id, loser_id, voter_ip=None, k=32):
    winner_rating = elo_ratings[winner_id]
    loser_rating = elo_ratings[loser_id]
    expected_win = expected_score(winner_rating, loser_rating)

    winner_new_rating = winner_rating + k * (1 - expected_win)
    loser_new_rating = loser_rating + k * (0 - (1 - expected_win))

    elo_ratings[winner_id] = winner_new_rating
    elo_ratings[loser_id] = loser_new_rating

    supabase.table("elo_battles").insert(
        {
            "winner_item_id": winner_id,
            "loser_item_id": loser_id,
            "winner_prev_rating": winner_rating,
            "loser_prev_rating": loser_rating,
            "winner_new_rating": winner_new_rating,
            "loser_new_rating": loser_new_rating,
            "voter_ip": voter_ip,
        }
    ).execute()


if len(items) >= 2:
    left_item, right_item = random.sample(items, 2)

    col1, col2 = st.columns(2)

    with col1:
        st.image(
            left_item["image_url"],
            caption=f"{left_item['object_name']} ({elo_ratings[left_item['id']]:.2f})",
            use_container_width=True,
        )
        if st.button(f"Vote {left_item['object_name']}"):
            update_elo(left_item["id"], right_item["id"])
            st.success(f"You chose {left_item['object_name']}!")

    with col2:
        st.image(
            right_item["image_url"],
            caption=f"{right_item['object_name']} ({elo_ratings[right_item['id']]:.2f})",
            use_container_width=True,
        )
        if st.button(f"Vote {right_item['object_name']}"):
            update_elo(right_item["id"], left_item["id"])
            st.success(f"You chose {right_item['object_name']}!")
else:
    st.warning("Need at least two items for ELO battles.")
