from datetime import datetime

import streamlit as st

from utils.db import get_supabase

supabase = get_supabase()

st.markdown(
    "<h1 style='text-align: center;'>Man Is the Measure of All Things</h1>",
    unsafe_allow_html=True,
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

                supabase.table("ratings").insert(
                    {
                        "object_name": object_name,
                        "object_descr": object_description,
                        "image_url": image_url,
                        "rating": 0,
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                    }
                ).execute()

                st.success("Uploaded successfully!")
            else:
                st.error("Name and image are required.")

st.markdown(
    "<h2 style='text-align: center;'>⭐ Things And Their Ratings</h2>",
    unsafe_allow_html=True,
)

# Fetch distinct items
items = (
    supabase.table("ratings")
    .select("object_name, object_descr, image_url")
    .execute()
    .data
)

# Remove duplicates by object_name (assuming name uniqueness)
unique_items = {item["object_name"]: item for item in items}.values()

for item in unique_items:
    st.markdown("<hr>", unsafe_allow_html=True)

    # Calculate avg rating dynamically
    rating_data = (
        supabase.table("ratings")
        .select("rating")
        .eq("object_name", item["object_name"])
        .gt("rating", 0)
        .execute()
        .data
    )

    ratings = [r["rating"] for r in rating_data]

    if ratings:
        avg_rating = sum(ratings) / len(ratings)
        rating_count = len(ratings)
        avg = f"🌟 {avg_rating:.2f}/10 ({rating_count} votes)"
    else:
        avg = "No ratings yet."

    st.markdown(
        f"<h3 style='text-align: center; color:#FFA500;'>{avg}</h3>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(item["image_url"], width=300, caption=item["object_name"])
        if item.get("object_descr"):
            st.markdown(
                f"<div style='text-align: center;'>{item['object_descr']}</div>",
                unsafe_allow_html=True,
            )

        selected_rating = st.radio(
            "Select your rating:",
            options=[f"{i} ⭐" for i in range(1, 11)],
            horizontal=True,
            key=f"rating_radio_{item['object_name']}",
        )

        if st.button(
            f"Submit rating for {item['object_name']}",
            key=f"submit_{item['object_name']}",
        ):
            rating_value = int(selected_rating.split()[0])

            supabase.table("ratings").insert(
                {
                    "object_name": item["object_name"],
                    "object_descr": item.get("object_descr"),
                    "image_url": item["image_url"],
                    "rating": rating_value,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                }
            ).execute()

            st.success(f"You rated {rating_value} ⭐!")
