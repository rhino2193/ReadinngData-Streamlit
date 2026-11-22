import altair as alt
import pandas as pd
import streamlit as st

st.title("Armando's Reading Tracker")

# Load the data
finished = pd.read_csv("books_finished.csv")
backlog = pd.read_csv("books_backlog.csv")
finished["End_Date"] = pd.to_datetime(finished["End_Date"])
finished_only = finished[finished["Status"] == "Finished"]
reading_now = finished[finished["Status"] == "Currently Reading"]

# Sidebar: each widget is just a variable
year = st.sidebar.selectbox("Year finished", ["All years", "2025", "2026"])
min_rating = st.sidebar.slider("Minimum rating (stars)", 1, 5, 1)
search = st.sidebar.text_input("Search by title or author")
formats = st.sidebar.multiselect("Backlog formats", ["Ebook", "Hardcover", "Paperback"],
                                 ["Ebook", "Hardcover", "Paperback"])

# Top numbers
col1, col2, col3, col4 = st.columns(4)
col1.metric("Books finished", len(finished_only))
col2.metric("Average rating", f"{finished_only['Rating'].mean():.2f} / 5")
col3.metric("5-star books", int((finished_only["Rating"] == 5).sum()))
col4.metric("Backlog books", len(backlog))

# Filter the finished books with the sidebar choices
books = finished_only.copy()
if year != "All years":
    books = books[books["Year"] == int(year)]
books = books[books["Rating"] >= min_rating]
if search:
    books = books[books["Title"].str.contains(search, case=False, na=False) |
                  books["Author"].str.contains(search, case=False, na=False)]

# Two tabs: finished books, and what is next
tab1, tab2 = st.tabs(["Finished books", "Backlog: what's next?"])

with tab1:
    st.header("Finished books")
    st.write(f"Showing {len(books)} of {len(finished_only)} finished books.")

    st.subheader("Books finished per month in 2026")
    books_2026 = books[books["Year"] == 2026]
    # st.bar_chart sorts month names A-Z and turns the labels sideways,
    # and it has no setting to change that. So use Altair directly
    # (the chart tool Streamlit uses underneath) for these charts.
    # sort= keeps Jan first, labelAngle=0 keeps the labels upright.
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly = books_2026["End_Date"].dt.strftime("%b").value_counts()
    monthly = monthly.reindex(months).dropna().reset_index()
    monthly.columns = ["Month", "Books"]
    monthly_chart = alt.Chart(monthly).mark_bar().encode(
        x=alt.X("Month", sort=months, axis=alt.Axis(labelAngle=0)),
        y="Books",
    )
    st.altair_chart(monthly_chart, use_container_width=True)

    st.subheader("Books by rating")
    rating_chart = books["Rating"].value_counts().sort_index().reset_index()
    rating_chart.columns = ["Rating", "Books"]
    rating_chart["Rating"] = rating_chart["Rating"].astype(int).astype(str)
    rating_chart = alt.Chart(rating_chart).mark_bar().encode(
        x=alt.X("Rating", sort=["1", "2", "3", "4", "5"],
                axis=alt.Axis(labelAngle=0)),
        y="Books",
    )
    st.altair_chart(rating_chart, use_container_width=True)

    st.subheader("Book list")
    st.dataframe(books[["Title", "Author", "Year", "End_Date", "Rating"]])

    st.subheader("Currently reading")
    st.dataframe(reading_now[["Title", "Author", "Year", "Start_Date"]])

with tab2:
    st.header("Backlog: what's next?")

    backlog_books = backlog[backlog["Format"].isin(formats)]
    st.write(f"Showing {len(backlog_books)} backlog books, "
             f"{int(backlog_books['Pages'].sum()):,} pages in total.")

    st.subheader("Backlog by format")
    format_chart = backlog_books["Format"].value_counts().reset_index()
    format_chart.columns = ["Format", "Books"]
    format_chart = alt.Chart(format_chart).mark_bar().encode(
        x=alt.X("Format", sort=["Ebook", "Hardcover", "Paperback"],
                axis=alt.Axis(labelAngle=0)),
        y="Books",
    )
    st.altair_chart(format_chart, use_container_width=True)

    if st.button("Pick a random book from the backlog"):
        pick = backlog_books.sample(1).iloc[0]
        st.write(f"Your next book is **{pick['Title']}** by {pick['Author']} "
                 f"- {int(pick['Pages'])} pages, {pick['Format']}.")

    st.subheader("Backlog list")
    st.dataframe(backlog_books[["Title", "Author", "Pages", "Format", "Ownership"]])

