import pandas as pd
import streamlit as st
from rdkit.Chem.PandasTools import LoadSDF

DELIMITERS = {",": ",", ";": ";"}


class Misc:
    def load_csv_sdf(uploaded_file):
        """Load a CSV or SDF file

        Args:
            uploaded_file (_type_): Uploaded file

        Returns:
            DataFrame: File loaded as pd.DataFrame
        """
        if uploaded_file.type == "text/csv":
            file = pd.read_csv(uploaded_file, delimiter=None)

        elif uploaded_file.type == "application/octet-stream":
            file = LoadSDF(uploaded_file, smilesName="Smiles", molColName=None)

        return file

    def download_data(data, file_name: str, disp_text: str, sidebar=False):
        """Donload pd.DataFrame as CSV file

        Args:
            dataframe (pd.DataFrame): Dataframe to be downloaded
            file_name (str): File name
            disp_text (str): Button label
            sidebar (bool, optional): Enable sidebar. Defaults to False.
        """
        csv = data.to_csv(index=False, encoding="utf-8")

        if sidebar:
            st.sidebar.download_button(label=disp_text,
                                       data=csv,
                                       file_name=f"{file_name}.csv",
                                       mime="text/csv")
        else:
            st.download_button(label=disp_text,
                               data=csv,
                               file_name=f"{file_name}.csv",
                               mime="text/csv")


class Sidebar:
    def file_uploader(title: str = "Upload file",
                      file_description: str = "Description",
                      example_csv_path: str = None,
                      example_csv_name="example_csv",
                      example_csv_text="Download example CSV file"):
        """Create structure to upload data on sidebar

        Args:
            title (str, optional): Title.
            file_description (str, optional): Description text.
            example_csv_path (str, optional): Example CSV path.
            example_csv_name (str, optional): Example CSV file name.
            example_csv_text (str, optional): Example CSV button label.

        Returns:
            _type_: Uploaded file
        """
        with st.sidebar.header(title):
            uploaded_file = st.sidebar.file_uploader(file_description,
                                                     type=["csv", "sdf"])

            if example_csv_path:
                exemple_file = pd.read_csv(example_csv_path, delimiter=None)
                Misc.download_data(exemple_file, example_csv_name,
                                   example_csv_text)

        return uploaded_file

    def multicolumn_selector(dataframe, text="Select desired columns"):
        """Create structure to select multiple columns on sidebar

        Args:
            dataframe (pd.DataFrame): Dataframe

        Returns:
            _type_: _description_
        """
        columns_all = list(dataframe.columns)

        columns = st.sidebar.multiselect(f"**{text}**", columns_all)

        return columns

    def column_selector(dataframe, text="Select desired columns"):
        """Create structure to select a column on sidebar

        Args:
            dataframe (pd.DataFrame): Dataframe

        Returns:
            _type_: _description_
        """
        columns_all = list(dataframe.columns)

        column = st.sidebar.selectbox(f"**{text}**", columns_all)

        return column

    def strain_selector(dataframe, col, text="Select desired strain"):
        """Create structure to select multiple columns on sidebar

        Args:
            dataframe (pd.DataFrame): Dataframe
            default (list, optional): Default columns selection.

        Returns:
            _type_: _description_
        """
        strain_all = list(dataframe[col].unique())

        strain = st.sidebar.multiselect(f"**{text}**", strain_all)

        return strain

    def slice_data(dataframe):
        """Create structure to slice data on sidebar

        Args:
            dataframe (pd.DataFrame): Dataframe

        Returns:
            int: Slice number
        """
        number = st.sidebar.slider("# data",
                                   min_value=10,
                                   max_value=dataframe.shape[0],
                                   value=dataframe.shape[0], step=10)

        return number


class Body:
    def awating_upload(display=True):
        """Create structure to display while wait for upload
        """
        with st.container():
            st.markdown("""## Awaiting file to be uploaded""")
            st.markdown("""Please use the sidebar menu to upload.""")

    def data_selection_preview(dataframe, n_slice: int, columns: list):
        """_summary_

        Args:
            dataframe (pd.DataFrame): Dataframe
            n_slice (int): Slicing point to preview
            columns (list): Columns to display

        Returns:
            pd.DataFrame: Preview dataframe
        """
        try:
            df = dataframe.iloc[:n_slice, :]
            df_preview = df[columns]

            st.subheader("Data selected")
            st.write(df_preview)

            return df_preview

        except ValueError:
            st.error("""Plase check your data or column selection""")

            return pd.DataFrame()
