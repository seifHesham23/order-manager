import streamlit as st
def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔐 Login Required")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        login_button = st.button("Login")

        if login_button:
            if username == st.secrets.auth.username and password == st.secrets.auth.password:
                st.session_state.logged_in = True
                st.success("Login successful!")
            else:
                st.error("Invalid credentials")
        
        # STOP everything until login is successful
        return False  # App should not continue

    return True  # App can continue
