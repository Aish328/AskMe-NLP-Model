import streamlit as st
import io
import PyPDF2
import google.generativeai as genai
import config
from utils import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txtfile

genai.configure(api_key=config.api_key)

def extract_text_from_pdf(pdf_content):

    try:
        pdf_file = io.BytesIO(pdf_content)
        reader = PyPDF2.PdfReader(pdf_file)
        text_content = ""
        for page_num in range(len(reader.pages)):
            text_content += reader.pages[page_num].extract_text() or ""
        return text_content
    except Exception as e:
        st.write("Error extracting text from document:", e)
        return None

def ask_gemini(question):
    """Uses the Gemini API to answer a question."""
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(question)
    return response.text if response else "No response from Gemini."

def main():
    st.title("Talk to your doc using AskMe ")

    pdf_file = st.file_uploader("Upload your file", type=["pdf"])
    
    if pdf_file is not None:
        pdf_content = pdf_file.read()
        extracted_text = extract_text_from_pdf(pdf_content)

        if extracted_text:
            
            user_query = st.text_input("Ask a question about the PDF:")
            
            if st.button("Get Answer"):
                if user_query.strip():
                    # Combine extracted text with user query for context
                    full_query = f"{extracted_text}\n\nQuestion: {user_query}"
                    answer = ask_gemini(full_query)
                    st.write("Answer from Askme:")
                    st.write(answer)
                else:
                    st.write("Please enter a question.")

if __name__ == "__main__":
    main()