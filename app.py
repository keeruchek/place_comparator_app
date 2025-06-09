import streamlit as st

# ---- UI Header ----
st.title("📍 Compare Living in U.S. Cities")
st.subheader("Choose one or two places to compare housing, safety, commute, parks, and more.")

# ---- Option Selector ----
option = st.radio("What would you like to do?", ("Compare One Place", "Compare Two Places"))

# ---- Input Fields ----
place1 = st.text_input("Enter first place (e.g. South Boston, MA)")

place2 = None
if option == "Compare Two Places":
    place2 = st.text_input("Enter second place (e.g. Back Bay, MA)")

# ---- Mock Data Function ----
def get_mock_data(place):
    return {
        "Average Housing Cost": "$3,200",
        "Crime Rate": "Medium",
        "Schools Nearby": ["Lincoln High", "Jefferson Elementary", "Newton Prep"],
        "Commute Score": "75 (Train)",
        "Green Spaces": "12 parks nearby",
        "Walkability Score": "80",
        "Diversity Index": "0.73",
        "Gyms Nearby": ["Anytime Fitness", "Crunch", "Orangetheory", "Planet Fitness"],
        "Shopping Options": ["Target", "Trader Joe's", "Whole Foods"],
        "PET Score": "76"
    }

# ---- Display Results ----
if st.button("Compare Now"):
    if place1 and (option == "Compare One Place" or (option == "Compare Two Places" and place2)):
        data1 = get_mock_data(place1)
        data2 = get_mock_data(place2) if place2 else None

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### {place1}")
            for k, v in data1.items():
                st.write(f"**{k}:**", v)

        if data2:
            with col2:
                st.markdown(f"### {place2}")
                for k, v in data2.items():
                    st.write(f"**{k}:**", v)
    else:
        st.warning("Please enter both places to compare.")

