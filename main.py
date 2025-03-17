import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

st.markdown(
    "<h1 style='text-align: center;'>📸 Rate Things</h1>", unsafe_allow_html=True
)

# Upload form
with st.expander("📤 Upload new thing"):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        object_name = st.text_input("Name")
        object_description = st.text_area("Description (optional)")
        uploaded_file = st.file_uploader("Image", type=["jpg", "jpeg", "png"])

        if st.button("Submit"):
            if uploaded_file and object_name:
                path = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_file.name}"
                supabase.storage.from_("images").upload(path, uploaded_file.getvalue())
                image_url = supabase.storage.from_("images").get_public_url(path)

                supabase.table("items").insert(
                    {
                        "object_name": object_name,
                        "object_description": object_description,
                        "image_url": image_url,
                    }
                ).execute()

                st.success("Uploaded successfully!")

        else:
            st.error("Name and image are required.")

st.markdown(
    "<h2 style='text-align: center;'>⭐ Things And Their Ratings</h2>",
    unsafe_allow_html=True,
)

# Load and display data
items = supabase.table("items").select("*").execute().data

for item in items:
    st.markdown("<hr>", unsafe_allow_html=True)

    # Display average rating prominently above the image
    if item.get("rating_count"):
        avg = item["rating_sum"] / item["rating_count"]
        st.markdown(
            f"<h3 style='text-align: center; color:#FFA500;'>🌟 {avg:.2f}/10 ({item['rating_count']} votes)</h3>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<h3 style='text-align: center; color:gray;'>No ratings yet.</h3>",
            unsafe_allow_html=True,
        )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(item["image_url"], width=300, caption=item["object_name"])
        if item.get("object_description"):
            st.markdown(
                f"<div style='text-align: center;'>{item['object_description']}</div>",
                unsafe_allow_html=True,
            )

        selected_rating = st.radio(
            "Select your rating:",
            options=[f"{i} ⭐" for i in range(1, 11)],
            horizontal=True,
            key=f"rating_radio_{item['id']}",
        )

        if st.button(
            f"Submit rating for {item['object_name']}", key=f"submit_{item['id']}"
        ):
            rating_value = int(selected_rating.split()[0])
            rating_sum = item.get("rating_sum") or 0
            rating_count = item.get("rating_count") or 0

            supabase.table("items").update(
                {
                    "rating_sum": rating_sum + rating_value,
                    "rating_count": rating_count + 1,
                    "updated_at": datetime.now().isoformat(),
                }
            ).eq("id", item["id"]).execute()

            st.success(f"You rated {rating_value} ⭐!")
