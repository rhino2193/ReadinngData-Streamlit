import pandas as pd
import streamlit as st

st.title("Armando's Reading Tracker")
st.write("Books I finished in 2025-2026, and the books left in my backlog. "
         "Filter by year and rating, see my reading patterns, and get a "
         "random pick from my 67-book backlog.")

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

    st.subheader("Books finished per month")
    st.bar_chart(books["End_Date"].dt.strftime("%Y-%m").value_counts().sort_index())

    st.subheader("Books by rating")
    st.bar_chart(books["Rating"].value_counts().sort_index())

    st.subheader("Book list")
    st.dataframe(books[["Title", "Author", "Year", "End_Date", "Rating"]])

    st.subheader("Currently reading")
    st.dataframe(reading_now[["Title", "Author", "Year", "Start_Date"]])

with tab2:
    st.header("Backlog: what's next?")
    st.write("All 67 backlog books are already owned, so there is nothing to buy.")

    backlog_books = backlog[backlog["Format"].isin(formats)]
    st.write(f"Showing {len(backlog_books)} backlog books, "
             f"{int(backlog_books['Pages'].sum()):,} pages in total.")

    st.subheader("Backlog by format")
    st.bar_chart(backlog_books["Format"].value_counts())

    if st.button("Pick a random book from the backlog"):
        pick = backlog_books.sample(1).iloc[0]
        st.write(f"Your next book is **{pick['Title']}** by {pick['Author']} "
                 f"- {int(pick['Pages'])} pages, {pick['Format']}.")

    st.subheader("Backlog list")
    st.dataframe(backlog_books[["Title", "Author", "Pages", "Format", "Ownership"]])
