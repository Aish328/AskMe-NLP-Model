from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import streamlit as st
import io
import config
import PyPDF2
import re
import zipfile

def authenticate():
    try:
        credentials  = service_account.Credentials.from_service_account_file(
            config.SERVICE_ACCOUNT_FILE,
            scopes = ['https://www.googleapis.com/auth/drive']

        )
        return build('drive' , 'v3' , credentials = credentials)
    except:
        return None
    

def upload_to_drive(drive_service , file_name , file_content , folder_id): 
    #looking if the document uploaded is of the type we can process
    try:
        file_metadata = {
            'name' : file_name,
            'parents' : [folder_id]
        }
        doctype = file_name.split(".")[-1]
        #MIME (Multipurpose Internet Mail Extensions) 
        mime_type = {
            'pdf' : 'application/pdf' , 
            'txt' : 'text/plain',
            'docx' : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        if doctype not in mime_type:
            raise st.write(f"""Document of {doctype} is not supported""")
        
        media = MediaIOBaseUpload(io.BytesIO(file_content) ,        #file_content is expected to be a bytes-like object (e.g., the content of a file read in binary mode).BytesIO allows you to treat this binary data as a file-like object,
                                  mimetype = mime_type[doctype],
                                  resumable = True)
        #file creation operation
        file = drive_service.files().create(
            body = file_metadata,
            media_body = media , 
            fields = 'id'
        ).execute()             #.execute() method sends the request to the Google Drive API and performs the file creation operation.
        '''This part of the code calls the create method of the files resource in the Google Drive API. The drive_service object is an instance of the Google Drive API client that has been authenticated and set up to interact with Google Drive.Metadata is defined as "data about data'''

        st.write(f"""your file "{file_name}" is uploaded successfully!""")
        return file.get('id')
    except:
        st.write("failed to upload ur file")
        return None
    
def fetch_from_drive(drive_service , file_id):


    #fetch doc as pdf and extract text and return as strinf
    try:
        file_metadata = drive_service.files().get(fileId = file_id).execute()
        function_switcher = { 'application/pdf' : extract_text_from_pdf,
                             'text/plain' : extract_txt_from_txtfile,
                             'application/vnd.openxmlformats-officedocument.wordprocessingml.document' : extract_text_from_docx
                              }
        if file_metadata['mimeType'] not in function_switcher:
            raise st.write(f"""File of the type {file_metadata['mimeType']} is not supported""")
        content = drive_service.files().get_media(fileID = file_id).execute()
        text_content = function_switcher[file_metadata['mimeType']](content)

        return text_content
    except:
        st.write("Failed to fetch the file!!")
        return None

def extract_text_from_pdf(pdf_content):
    try :
        pdf_file = io.BytesIO(pdf_content)
        reader = PyPDF2.pdfReader(pdf_file)
        text_content = ""
        for page_num in range(len(reader.pages)):
            text_content += reader.pages[page_num].extract_text()
        return text_content
    except:
        st.write("Error filr extracting text from document !!")
        return None
    
def extract_text_from_txtfile(content):
    return content.decode('utf-8')

def extract_text_from_docx(content):
    content_bytes = io.BytesIO(content)
    docx_text = ""
    with zipfile.ZipFile(content_bytes) as docx_zip:
        with docx_zip.open('word/document.xml') as docs_xml:
            docs_text = docs_xml.read().decode()

    cleaned_text = re.sub(r'<.*?>', '', docx_text)
    return cleaned_text

def delete_file_from_drive(file_id):
    drive_service = authenticate()
    if drive_service:
        drive_service.files().delete(fileId = file_id).execute()
    else:
        st.write("Failed to delete file from server")

def string_to_generator(input_string):
    for char in input_string:
        yield char