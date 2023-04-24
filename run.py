import streamlit as st

from core.data_cleaner import cleaner
from core.bio_cleaner import bio_cleaner
from core.column_selector import select_cols


# ----------------------------------------------------------------
class MultiApp:
    """Framework for combining multiple streamlit applications."""

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({"title": title, "function": func})

    def run(self):
        app = st.sidebar.selectbox("Navigation", self.apps,
                                   format_func=lambda app: app["title"])

        app["function"]()

# ----------------------------------------------------------------


application = MultiApp()

application.add_app("Column Selector", select_cols)
application.add_app("Dataset Cleaner", cleaner)
application.add_app("Dataset Bio-Cleaner", bio_cleaner)

application.run()
