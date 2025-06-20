import streamlit as st

# --- Streamlit App Configuration ---
st.set_page_config(
    page_title="Google Login & Domain Check",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Configuration for allowed domain ---
ALLOWED_DOMAIN = "ghs.edu.hk" # The specific domain you want to allow

# --- Function to check authentication and domain ---
def check_authentication():
    """
    Checks if a user is logged in via Streamlit Cloud's Google Auth
    and if their email domain is authorized.
    """
    user = st.user # Get user object from Streamlit Cloud environment

    if user:
        user_email = user.email
        if user_email and user_email.endswith(f"@{ALLOWED_DOMAIN}"):
            st.session_state.authenticated = True
            st.session_state.user_email = user_email
            return True
        else:
            st.session_state.authenticated = False
            st.session_state.user_email = user_email # Store unauthorized email for display
            return False
    else:
        st.session_state.authenticated = False
        st.session_state.user_email = None
        return False

# --- Logout Function ---
def logout():
    """
    Simulates a logout by clearing authentication state.
    Note: On Streamlit Cloud, the user might still be logged into Google,
    but this clears the app's internal recognition.
    """
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.experimental_rerun() # Rerun the app to reflect the logged out state

# --- Main App Logic ---
st.title("Google Login with Domain Restriction")

# Check authentication status on each rerun
# This needs to be called after st.session_state initialization if states are used within it
check_authentication()

if st.session_state.authenticated:
    st.success(f"Hello World, you are logged in as {st.session_state.user_email}!")
    st.markdown("This content is only visible to authorized users.")

    # Logout button
    if st.button("Logout"):
        logout()
else:
    # --- Login Page Section ---
    st.header("Login Page")
    st.markdown("Please log in to access the application.")

    if st.session_state.user_email:
        # User is logged into Google, but domain is not authorized
        st.error("Access Denied")
        st.warning(f"Your email ({st.session_state.user_email}) is not authorized. Please log in with an email ending in @{ALLOWED_DOMAIN}.")
    else:
        # User is not logged into Google at all (or session expired)
        st.info("To proceed, please use the Google authentication prompt provided by Streamlit.")
        st.markdown(
            "**(On Streamlit Community Cloud, a 'Continue with Google' button "
            "should appear automatically above or below, or you may need to "
            "refresh the page. This application requires a Google account "
            "from the authorized domain.)**"
        )
    
    st.markdown("---")
    st.markdown("If you believe this is an error, please contact support.")
