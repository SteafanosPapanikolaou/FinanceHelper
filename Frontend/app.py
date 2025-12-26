import streamlit as st
import requests

st.set_page_config(page_title="Chatbot", layout="wide")

st.title("📄 Chatbot with PDF Upload")

# ---- Cache uploaded files ----
@st.cache_data(show_spinner=False)
def cache_files(files):
    return files

# ---- File upload (drag & drop) ----
uploaded_files = st.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    cached_files = cache_files(uploaded_files)
    st.success(f"{len(cached_files)} file(s) cached")

# ---- Chat input ----
user_query = st.text_input("Ask a question")

if st.button("Send"):
    if not user_query:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Sending to backend..."):
            files = []
            if uploaded_files:
                for f in uploaded_files:
                    files.append(
                        ("files", (f.name, f.getvalue(), "application/pdf"))
                    )

            response = requests.post(
                "http://localhost:5000/chat",
                data={"query": user_query},
                files=files
            )

            if response.status_code == 200:
                st.markdown("### 🤖 Answer")
                st.write(response.json()["answer"])
            else:
                st.error("Backend error")
