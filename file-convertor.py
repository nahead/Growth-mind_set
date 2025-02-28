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

def process_dataframe(file, ext):
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
        mime = "text/csv" if format_choice == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        new_name = file.name.replace(ext, format_choice)
        
        if format_choice == "csv":
            df.to_csv(output, index=False)
        else:
            df.to_excel(output, index=False, engine="openpyxl")
        
        output.seek(0)
        st.download_button(label=f"Download {new_name}", data=output, file_name=new_name, mime=mime)

def process_pdf(file):
    st.subheader(f"{file.name} - PDF Preview")
    pdf_reader = PyPDF2.PdfReader(file)
    text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    st.text_area("Extracted Text", text, height=300)
    
    output = BytesIO(file.getvalue())
    st.download_button(label=f"Download {file.name}", data=output, file_name=file.name, mime="application/pdf")

def process_image(file, ext):
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
        os.remove(temp_img_path)  # Delete temp file after use
        
        pdf_output = BytesIO()
        pdf.output(pdf_output, dest="F")
        pdf_output.seek(0)
        
        st.download_button(label=f"Download {file.name}.pdf", 
                           data=pdf_output, 
                           file_name=file.name.replace(ext, "pdf"), 
                           mime="application/pdf")

if files:
    for file in files:
        ext = file.name.split(".")[-1].lower()
        file.seek(0)  # Reset file pointer
        
        if ext in ["csv", "xlsx"]:
            process_dataframe(file, ext)
        elif ext == "pdf":
            process_pdf(file)
        elif ext in ["jpg", "png"]:
            process_image(file, ext)
    
    st.success("Progress Complete ✅")
