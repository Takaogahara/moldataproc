import os
import streamlit as st
from rdkit.Chem import PandasTools

from core.code.streamlit_structure import Sidebar, Body, Misc
from core.code.clean_process import BioCleaner

EXAMPLE = "./core/files/example_biocleaner.csv"
SDF_OUT = "./core/files/out_sdf.sdf"


def bio_cleaner():
    uploaded_file = None
    uploaded_file = Sidebar.file_uploader("Upload data",
                                          "Upload CSV or SDF file",
                                          EXAMPLE)

    if uploaded_file:
        # Delete SDF from lib folder
        if os.path.exists(SDF_OUT):
            os.remove(SDF_OUT)

        # Load data
        file_name = uploaded_file.name.split(".")[0]
        data = Misc.load_csv_sdf(uploaded_file)

        # UI
        col_smls = Sidebar.column_selector(data, "Select :red[Smiles] column")
        conv_text = ("Select :red[Molecular Weight], :red[Standard Relation],"
                     " :red[Standard Value], :red[Standard Units]"
                     " (IN THIS ORDER)")
        col_conv = Sidebar.multicolumn_selector(data, conv_text)
        col_strn = Sidebar.column_selector(data, "Select :red[Strain] column")
        strains = Sidebar.strain_selector(data, col_strn)
        thrd = st.sidebar.number_input("**Activity threshold value (nM)**",
                                       value=10000.0)

        # Set displays placeholders
        info_up = st.empty()
        title = st.empty()
        data_disp = st.empty()
        info_down = st.empty()

        # Display input data
        title.subheader("Input")
        data_disp.dataframe(data)
        info_down.info(f"Input shape: {data.shape}")

        if len(strains) > 0:
            if st.sidebar.button("Run"):
                with st.spinner("Please wait"):
                    # Run processing
                    dclean = BioCleaner(col_smls, col_strn, col_conv)
                    output = dclean.bio_clean(data, strains, thrd)

                # Display output data
                title.subheader("Output")
                data_disp.dataframe(output)
                info_up.info(f"Input shape: {data.shape}")
                info_down.info(f"Output shape: {output.shape}")

                Misc.download_data(output, file_name,
                                   disp_text="Download CSV")

                # Download SDF
                output_sdf = output.copy(deep=True)
                PandasTools.AddMoleculeColumnToFrame(output_sdf,
                                                     col_smls,
                                                     "ROMol")
                PandasTools.WriteSDF(output_sdf, SDF_OUT,
                                     molColName="ROMol",
                                     idName="RowID",
                                     properties=list(output_sdf.columns))
                with open(SDF_OUT, "rb") as sdf:
                    st.download_button("Download SDF", sdf,
                                       file_name=f"{file_name}.sdf")

    else:
        Body.awating_upload()
