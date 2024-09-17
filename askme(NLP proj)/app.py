import config
from utils import authenticate , upload_to_drive
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

def main():
    #setting page config
    st.set_page_config(page_title = "AskMe" , layput = "wide" , initial_sidebar_state = "collapsed")
    st.title("AskMe")
    st.subheader("what about any document")
    
    #collapse side menu
    st.markdown(
    f"""<style>
        [data-testid="collapsedControl"] {{display:none}}
    </style>""",
    unsafe_allow_html=True,
    )

    #upload button
    upload_container = st.container()
    upload_container.markdown(
        """
        <style>
        div[data-testid="stFileUploader"] div:first-child {
            max-width: 300px;
            width: 100%;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    uploaded_file = upload_container.file_uploader("Upload a PDF file" , type = ["pdf" , "txt" , "docs"])

    if uploaded_file:
        st.session_state['file_name'] = uploaded_file.name
        st.session_state['folder_id'] = config.FOLDER_ID
        st.session_state['file_id'] = None
        drive_service = authenticate()
        if drive_service:
            st.session_state['file_id'] = upload_to_drive(drive_service , uploaded_file.name , uploaded_file.getvalue(),config.FOLDER_ID)
        else:
            st.write("storage service authentication failed")

    if uploaded_file and st.session_state['file_id'] and st.button("chat"):
        switch_page("chat")
if __name__ == "main":
    main()


