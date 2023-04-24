import streamlit as st

from core.code.streamlit_structure import Sidebar, Body, Misc

EXAMPLE = "./core/files/example_cleaner.csv"


str_1 = ("For biological activity:  **:red[ID]**, **:red[Smiles]**, "
         "**:red[Molecular Weight]**, **:red[Standard Value]**, "
         "**:red[Standard Units]**, **:red[Assay Organism]**")
str_2 = ("Others:  **:red[ID]**, **:red[Smiles]**, **:red[Labels]**, "
         "**:red[Train/Test set]**, **:red[Cluster]** (optional)")


def select_cols():
    uploaded_file = None
    uploaded_file = Sidebar.file_uploader("Upload data",
                                          "Upload CSV or SDF file",
                                          EXAMPLE)

    if uploaded_file:
        file_name = uploaded_file.name.split(".")[0]
        data = Misc.load_csv_sdf(uploaded_file)

        st.sidebar.markdown(str_1)
        st.sidebar.markdown(str_2)
        sel_col = Sidebar.multicolumn_selector(data, "Select columns")

        # Set displays placeholders
        title = st.empty()
        data_disp = st.empty()
        info_down = st.empty()

        # Display input data
        title.subheader("Data")
        data_disp.dataframe(data)
        info_down.info(f"Input shape: {data.shape}")

        if len(sel_col) > 0:
            output = data[sel_col]
            data_disp.dataframe(output)
            info_down.info(f"Output shape: {output.shape}")

            Misc.download_data(output, file_name,
                               disp_text="Download")
    else:
        Body.awating_upload()
