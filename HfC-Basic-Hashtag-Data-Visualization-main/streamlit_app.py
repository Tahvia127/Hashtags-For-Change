import streamlit as st
import pandas as pd
import altair as alt



# Page configuration
st.set_page_config(
    page_title="Hashtags for Change",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Sidebar navigation
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Kenneth's Data", "TikTok Data", "Google Trends Data"]
)

metric_options = {
        "Likes": "likes",
        "Views": "views",
        "Shares": "shares",
        "Comments": "comments"
    } 


if page == "Home":
    st.header("Project Overview")
    st.write("""
        This applet looks at data from three sources: TikTok data via Kenneth, alternate TikTok data, and Google Trends data,
        allowing the user to select from data sources, hashtag names, and specific types of data (likes, shares, etc), to see
        graphs of activity over time in the chosen hashtag and form of activity.
                 
        Notes:
        - Provide graphs of data sorted by hashtag type and data metric (likes, shares, etc)
        - Shows lines from data frame corresponding to the hashtag, date of post, and data metric
        - In-app dataframe can be sorted by either column by user
        - Comment out the line: “filtered = filtered.reset_index(drop=True)” within a page and you can see the line in the original csv that the data in the in-app data frame corresponds to

        Limitations:
        - Only provides a data frame with the specific data metric data (code can be changed to show all data corresponding to post)
        - Only shows the data from one csv at a time
        - Does not compare data of search interest to specific events

        Issues:
        - Kenneth’s data seems to be from TikTok, but is different from the csv in the TikTok data folder, so unsure how to interact with it - temporarily just treated it as its own data source
        - For some posts, there is a random data point from 1970 with 0 in all columns (potential bug?)
        - standwithhummanity under google trends tier 3 hashtags uses two “m”s in hu*mm*anity
        - Unclear on what the value associated with Google Trends actually measures
        """)


# Kenneth's Data
elif page == "Kenneth's Data":
    st.title("Kenneth's TikTok Data")

    # Load dataframe
    @st.cache_data
    def load_data():
        url = "https://raw.githubusercontent.com/Tahvia127/Hashtags-For-Change/main/Kenneth_Task/hydrated_results.csv"
        df = pd.read_csv(url)

        # Ensure video_date is actually a datetime
        df["video_date"] = pd.to_datetime(df["video_date"], errors="coerce")

        return df

    df = load_data()

    # ---------------------------------------
    # Dropdowns
    # ---------------------------------------

    st.header("Filters")

    # Choose hashtag
    selected_hashtag = st.selectbox(
        "Choose a hashtag:",
        sorted(df["hashtag"].unique())
    )

    # Choose metric (stat to graph)
    metrics = ["likes", "views", "shares", "comments"]
    selected_metric_display = st.selectbox(
        "Choose a metric:",
        list(metric_options.keys())
    )
    selected_metric = metric_options[selected_metric_display]

    # ---------------------------------------
    # Filter data based on the chosen hashtag
    # ---------------------------------------

    filtered = df[df["hashtag"] == selected_hashtag].sort_values("video_date")
    filtered = filtered.reset_index(drop=True)
    # ---------------------------------------
    # Chart
    # ---------------------------------------

    st.subheader(f"{selected_metric.capitalize()} over time for #{selected_hashtag}")

    chart = (
        alt.Chart(filtered)
        .mark_line(point=True)
        .encode(
            x=alt.X("video_date:T", title="Date"),
            y=alt.Y(f"{selected_metric}:Q", title=selected_metric.capitalize()),
            tooltip=["video_date", selected_metric]
        )
    )

    st.altair_chart(chart, use_container_width=True)

    # ---------------------------------------
    # Show the filtered table
    # ---------------------------------------

    st.write("Filtered data:")
    st.dataframe(filtered[["video_date", selected_metric]])


#TikTok Data
elif page == "TikTok Data":
    st.title("TikTok Data")

    # Load dataframe
    @st.cache_data
    def load_data():
        url = "https://raw.githubusercontent.com/Tahvia127/Hashtags-For-Change/main/TikTok_Data/hydrated_results.csv"
        df = pd.read_csv(url)

        # Ensure video_date is actually a datetime
        df["video_date"] = pd.to_datetime(df["video_date"], errors="coerce")

        return df

    df = load_data()

    # ---------------------------------------
    # Dropdowns
    # ---------------------------------------

    st.header("Filters")

    # Choose hashtag
    selected_hashtag = st.selectbox(
        "Choose a hashtag:",
        sorted(df["hashtag"].unique())
    )

    # Choose metric (stat to graph)
    metrics = ["likes", "views", "shares", "comments"]
    selected_metric_display = st.selectbox(
        "Choose a metric:",
        list(metric_options.keys())
    )
    selected_metric = metric_options[selected_metric_display]

    # ---------------------------------------
    # Filter data based on the chosen hashtag
    # ---------------------------------------

    filtered = df[df["hashtag"] == selected_hashtag].sort_values("video_date")
    filtered = filtered.reset_index(drop=True)
    # ---------------------------------------
    # Chart
    # ---------------------------------------

    st.subheader(f"{selected_metric.capitalize()} over time for #{selected_hashtag}")

    chart = (
        alt.Chart(filtered)
        .mark_line(point=True)
        .encode(
            x=alt.X("video_date:T", title="Date"),
            y=alt.Y(f"{selected_metric}:Q", title=selected_metric.capitalize()),
            tooltip=["video_date", selected_metric]
        )
    )

    st.altair_chart(chart, use_container_width=True)

    # ---------------------------------------
    # Show the filtered table
    # ---------------------------------------

    st.write("Filtered data:")
    st.dataframe(filtered[["video_date", selected_metric]])

#Google Trends Data
elif page == "Google Trends Data":

    st.title("Google Trends Viewer")

    # -----------------------------
    # Lists of hashtags in each folder
    # -----------------------------
    tier1_hashtags = ["black_lives_matter", "brazil_conflict", "brazil_gangs", "brazil_violence", "capitol_riots", "gaza_ceasefire", "gaza_conflict", "houthi_yemen", "india_demonstrations", "india_protests", "india_riots", "india_strikes", "india_unrest", "israel_palestine", "january_6", "mexico_cartel", "mexico_crime", "mexico_drug_war", "mexico_violence", "myanmar_coup", "myanmar_military", "myanmar_violence", "pakistan_demonstrations", "pakistan_unrest", "pakistan_violence", "palestine_conflict", "protests_america", "russia_ukraine", "syria_bombing", "syria_conflict", "syria_military", "syria_war", "ukraine_conflict", "ukraine_crisis", "ukraine_invasion", "ukraine_military", "ukraine_war", "united_states_protests", "us_protests", "yemen_conflict", "yemen_violence", "yemen_war"] 
    tier2_hashtags = ["afghanistan_conflict", "afghanistan_military", "boko_haram", "colombia_conflict", "colombia_violence", "france_protests", "french_demonstrations", "iraq_conflict", "iraq_military", "iraq_war", "italian_demonstrations", "italy_protests", "korea_demonstrations", "lebanon_conflict", "lebanon_crisis", "lebanon_protests", "nigeria_insurgency", "nigeria_violence", "russia_conflict", "russia_military", "south_korea_protests", "taliban", "turkey_conflict", "turkey_conflict", "turkey_military", "turkey_violence"]
    tier3_hashtags = ["blacklivesmatter", "ceasefire", "ceasefirenow", "equalityforall", "europeansolidarity", "freedomconvoy2022", "freegaza", "freepalestine", "fridaysforfuture", "gayrights", "gaza", "gazaceasefire", "generationequality", "indiapakistan", "justice", "lgbtq", "loveislove", "metoo", "milkteaalliance", "neveragain", "neverforget", "pakistanarmy", "pakistanzindabad", "peaceinyemen", "prochoice", "protest", "refugeerelief", "riocrisis", "russiaukrainewar", "slavaukraine", "solidarity", "standwithhummanity", "standwithukraine", "stopgenocide", "stopputin", "stopthewar", "stopwar", "taliban", "timesup", "transrightsarehumanrights", "turkishwomenneedhelp", "ukrainewar", "weneedtotalkaboutyemen", "whatshappeninginmyanmar"]

    # Map each hashtag to its folder
    hashtag_to_folder = {h: "TIER1_COUNTRIES" for h in tier1_hashtags}
    hashtag_to_folder.update({h: "TIER2_COUNTRIES" for h in tier2_hashtags})
    hashtag_to_folder.update({h: "TIER3_HASHTAGS" for h in tier3_hashtags})

    # -----------------------------
    # Dropdown to select hashtag
    # -----------------------------
    selected_hashtag = st.selectbox(
        "Select a hashtag or country:",
        sorted(list(hashtag_to_folder.keys()))
    )

    # -----------------------------
    # Build raw URL to CSV
    # -----------------------------
    folder = hashtag_to_folder[selected_hashtag]
    filename = f"google_trends_{selected_hashtag}.csv"

    raw_url = f"https://raw.githubusercontent.com/Tahvia127/Hashtags-For-Change/main/Google_Trends/{folder}/{filename}"

    # -----------------------------
    # Load CSV
    # -----------------------------
    @st.cache_data
    def load_csv(url):
        df = pd.read_csv(url)
        # Assume first column is date, second column is the numeric value
        df.columns = ["date", "value"]
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return df

    df = load_csv(raw_url)



    # -----------------------------
    # Time-series chart
    # -----------------------------
    st.subheader(f"Trend of {selected_hashtag} search interest over time")
    chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("value:Q", title="Value"),
            tooltip=["date", "value"]
        )
    )

    st.altair_chart(chart, use_container_width=True)

    # -----------------------------
    # Display table
    # -----------------------------
    st.subheader(f"Data for {selected_hashtag}")
    st.dataframe(df.reset_index(drop=True))
