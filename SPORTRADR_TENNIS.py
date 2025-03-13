import pandas as pd
import numpy as np
import sqlite3
import streamlit as st 

# Connect to SQLite database
conn = sqlite3.connect("tennis.db")
mycursor = conn.cursor()

#  **Tennis Sport Radar Dashboard**
st.title("TENNIS SPORT RADAR")
st.write("\n")

# **Competitor Table**
st.subheader("COMPETITOR TABLE")

# Fetch Competitor Data
mycursor.execute("SELECT * FROM Competitors")
data = mycursor.fetchall()
df = pd.DataFrame(data, columns=[desc[0] for desc in mycursor.description])


# Fetch Competitor Rankings
mycursor.execute("""
    SELECT Competitors.name, Competitor_Rankings.rank, Competitor_Rankings.points
    FROM Competitors
    INNER JOIN Competitor_Rankings ON Competitors.competitor_id = Competitor_Rankings.competitor_id
""")
D1 = mycursor.fetchall()
A1 = pd.DataFrame(D1, columns=[desc[0] for desc in mycursor.description])

# Sidebar Metrics  
st.sidebar.metric(label="TOTAL NO OF COMPETITORS", value=df["competitor_id"].count())
st.sidebar.metric(label="TOTAL COUNTRIES REPRESENTED", value=df["country"].nunique())


# Find Competitor with Highest Points  
mycursor.execute("""
    SELECT name, MAX(points) 
    FROM (
        SELECT Competitors.name, Competitor_Rankings.points
        FROM Competitors
        INNER JOIN Competitor_Rankings ON Competitors.competitor_id = Competitor_Rankings.competitor_id
    ) AS top_competitor;
""")
D1 = mycursor.fetchall()
A1 = pd.DataFrame(D1, columns=[desc[0] for desc in mycursor.description])
st.sidebar.subheader("HIGHEST POINTS COMPETITOR")
st.sidebar.dataframe(A1, hide_index=True)

# Fetch Full Competitor Data  
mycursor.execute("""
    SELECT Competitors.competitor_id, Competitors.name, Competitors.country,
           Competitors.country_code, Competitors.abbreviation,
           Competitor_Rankings.rank, Competitor_Rankings.points
    FROM Competitors
    INNER JOIN Competitor_Rankings ON Competitors.competitor_id = Competitor_Rankings.competitor_id
""")
C1 = mycursor.fetchall()
C2 = pd.DataFrame(C1, columns=[desc[0] for desc in mycursor.description])
st.dataframe(C2, hide_index=True)


# **Search for a Competitor**
search_name = st.text_input("Search for a competitor by name:")
filtered_df = C2[C2['name'].str.contains(search_name, case=False, na=False)] if search_name else C2
st.dataframe(filtered_df, hide_index=True)

# **Filter by Rank**
min_rank, max_rank = st.sidebar.slider("Select rank range", 1, 1000, (1, 100))
filtered_df = C2[(C2['rank'] >= min_rank) & (C2['rank'] <= max_rank)]
st.subheader("FILTER TABLE BY RANK")
st.dataframe(filtered_df, hide_index=True)


# **Filter by Country**
country = st.selectbox("Select country", C2['country'].unique())
filtered_df = C2[C2['country'] == country]
st.dataframe(filtered_df, hide_index=True)

# ** Top 3 Countries with Highest Points**
mycursor.execute("""
    SELECT country, SUM(points) AS Total_points
    FROM (
        SELECT Competitors.competitor_id, Competitors.name, Competitors.country, Competitor_Rankings.points
        FROM Competitors
        INNER JOIN Competitor_Rankings ON Competitors.competitor_id = Competitor_Rankings.competitor_id
    ) AS jointable
    GROUP BY country
    ORDER BY Total_points DESC
    LIMIT 3;
""")
top_countries = mycursor.fetchall()
df4 = pd.DataFrame(top_countries, columns=[desc[0] for desc in mycursor.description])
st.sidebar.subheader("TOP 3 COUNTRIES")
st.sidebar.dataframe(df4, hide_index=True)


# **🏆 Leaderboards**
st.header("Leaderboards")

# **Top 10 Ranked Competitors**
mycursor.execute("""
    SELECT Competitors.name, Competitors.country, Competitor_Rankings.rank, Competitor_Rankings.points
    FROM Competitors
    INNER JOIN Competitor_Rankings ON Competitors.competitor_id = Competitor_Rankings.competitor_id
    ORDER BY Competitor_Rankings.rank ASC
    LIMIT 10;
""")
top_ranked = mycursor.fetchall()
top_ranked_df = pd.DataFrame(top_ranked, columns=["Name", "Country", "Rank", "Points"])
st.subheader("Top-Ranked Competitors")
st.dataframe(top_ranked_df, hide_index=True)


# **Competitors with the Highest Points**
mycursor.execute("""
    SELECT Competitors.name, Competitors.country, Competitor_Rankings.rank, Competitor_Rankings.points
    FROM Competitors
    INNER JOIN Competitor_Rankings ON Competitors.competitor_id = Competitor_Rankings.competitor_id
    ORDER BY Competitor_Rankings.points DESC
    LIMIT 10;
""")
highest_points_competitors = mycursor.fetchall()
highest_points_df = pd.DataFrame(highest_points_competitors, columns=["Name", "Country", "Rank", "Points"])
st.subheader("Competitors with Highest Points")
st.dataframe(highest_points_df, hide_index=True)


# **📊 Analysis Summary**
st.subheader("Analysis of the Tennis Competition Rankings:")
st.write("""
The tennis competition features thousands of competitors from various countries, showcasing global participation.
The Czechia stands out as a top-performing country, accumulating significant points and demonstrating its dominance in tennis.
""")

# ** Complexes & Venues**
st.header("COMPLEXES AND VENUES")
st.sidebar.header("COMPLEX AND VENUE")


# Fetch Complex & Venue Data  
mycursor.execute("""
    SELECT Complexes.complex_id, Complexes.complex_name, Venues.venue_name, Venues.city_name,
           Venues.country_name, Venues.country_code, Venues.timezone
    FROM Venues
    INNER JOIN Complexes ON Venues.complex_id = Complexes.complex_id;
""")
data_1 = mycursor.fetchall()
df_1 = pd.DataFrame(data_1, columns=[desc[0] for desc in mycursor.description])

# **Total Complexes & Venues**
TOTAL_COMPLEX = df_1["complex_name"].nunique()
TOTAL_VENUE = df_1["venue_name"].nunique()
st.sidebar.metric(label="TOTAL COMPLEXES", value=TOTAL_COMPLEX)
st.sidebar.metric(label="TOTAL VENUES", value=TOTAL_VENUE)

# **Venues per Complex**
st.subheader("VENUES IN EACH COMPLEX")
mycursor.execute("""
    SELECT Complexes.complex_name, COUNT(Venues.venue_name) AS venue_count
    FROM Venues
    INNER JOIN Complexes ON Venues.complex_id = Complexes.complex_id
    GROUP BY Complexes.complex_name
    ORDER BY venue_count DESC;
""")
data_2 = mycursor.fetchall()
df_2 = pd.DataFrame(data_2, columns=[desc[0] for desc in mycursor.description])
st.dataframe(df_2, hide_index=True)


# ** Competition Analysis**
st.subheader("COMPETITION ANALYSIS")
st.write("""
Competitions cover a wide range of categories and genders, highlighting significant differences in participation across various groups.
""")

# **Close Connection**
conn.close()