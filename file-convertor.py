import streamlit as st
import pandas as pd
import PyPDF2
from io import BytesIO
from PIL import Image
from fpdf import FPDF
import tempfile
import os

st.set_page_config(page_title="File Converter", layout="wide", page_icon="📂")

st.title("File Converter")

st.write("Upload file")
st.sidebar.header("Choose a File Format")
files = st.file_uploader("Upload CSV, Excel, PDF, or Image files.", 
                         type=["csv", "xlsx", "pdf", "jpg", "png"], 
                         accept_multiple_files=True)

if files:
    for file in files:
        ext = file.name.split(".")[-1]
        file.seek(0)  # Ensure file pointer is at the beginning
        
        if ext in ["csv", "xlsx"]:
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

        elif ext == "pdf":
            st.subheader(f"{file.name} - PDF Preview")
            pdf_reader = PyPDF2.PdfReader(file)
            text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text() is not None])
            st.text_area("Extracted Text", text, height=300)

            output = BytesIO()
            output.write(file.getvalue())
            output.seek(0)
            st.download_button(label=f"Download {file.name}", data=output, file_name=file.name, mime="application/pdf")

        elif ext in ["jpg", "png"]:
            st.subheader(f"{file.name} - Image Preview")
            image = Image.open(file)
            st.image(image, caption=file.name, use_column_width=True)

            output = BytesIO()
            image.save(output, format=image.format)
            output.seek(0)
            st.download_button(label=f"Download {file.name}", data=output, file_name=file.name, mime=f"image/{ext}")

            if st.button(f"Convert {file.name} to PDF"):
                pdf = FPDF()
                pdf.add_page()
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as temp_img:
                    image.save(temp_img, format=image.format)
                    temp_img_path = temp_img.name
                
                pdf.image(temp_img_path, x=10, y=10, w=190)
                pdf_output = BytesIO()
                
                # ✅ Fix: Output PDF as a string and write to BytesIO
                pdf_bytes = pdf.output(dest="S").encode("latin1")
                pdf_output.write(pdf_bytes)
                pdf_output.seek(0)
                
                os.remove(temp_img_path)  # Delete temp file after use
                
                st.download_button(label=f"Download {file.name}.pdf", 
                                   data=pdf_output, 
                                   file_name=file.name.replace(ext, "pdf"), 
                                   mime="application/pdf")

    st.success("Progress Complete ✅")  # Success message moved outside the loop
