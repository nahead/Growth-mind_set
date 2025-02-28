import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="File Convertor", layout="wide", page_icon="📂")

st.title("File Convertor")

st.write("Upload file")
st.sidebar.header("Choose a File Format")
files = st.file_uploader("Upload CSV or Excel files.", type=["csv", "xlsx"], accept_multiple_files=True)

if files:
    for file in files:
        ext = file.name.split(".")[-1]
        df = pd.read_csv(file) if ext == "csv" else pd.read_excel(file, engine="openpyxl")

        st.subheader(f"{file.name} - Preview")
        st.dataframe(df.head())

        if st.checkbox(f"Remove Duplicates from {file.name}"):
            df = df.drop_duplicates()
            st.success(f"Removed duplicates from {file.name}")
            st.dataframe(df.head())

        if st.checkbox(f"Fill Missing Values in {file.name}"):
            df.fillna(df.select_dtypes(include=["number"]).mean(), inplace=True)
            st.success(f"Filled missing values in {file.name}")
            st.dataframe(df.head())

        selected_col = st.multiselect(f"Select columns to drop in {file.name}", df.columns)
        if selected_col:
            df = df.drop(columns=selected_col)
            st.success(f"Dropped selected columns from {file.name}")
            st.dataframe(df.head())

        if st.checkbox(f"Show Chart - {file.name}") and not df.select_dtypes(include=["number"]).empty:
            st.bar_chart(df.select_dtypes(include="number").iloc[:, :2])

        format_choice = st.radio(f"Convert {file.name} to", ["csv", "excel"], key=file.name)

        if st.button(f"Download {file.name} as {format_choice}"):
            output = BytesIO()
            if format_choice == "csv":
                df.to_csv(output, index=False)
                mime = "text/csv"
                new_name = file.name.replace(ext, "csv")
            else:
                df.to_excel(output, index=False, engine="openpyxl")
                mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                new_name = file.name.replace(ext, "xlsx")

            output.seek(0)
            st.download_button(label=f"Download {new_name}", data=output, file_name=new_name, mime=mime)

        st.success("Progress Complete")
