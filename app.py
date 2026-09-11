import json
import streamlit as st

from agent import process_email


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Email-to-Action Agent",
    page_icon="📧",
    layout="wide"
)


# --------------------------------------------------
# LOAD EMAILS
# --------------------------------------------------

with open("emails.json", "r", encoding="utf-8") as file:
    emails = json.load(file)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("📧 Email-to-Action Agent")
st.write(
    "AI-powered email classification and automated action system"
)

st.divider()


# --------------------------------------------------
# EMAIL SELECTION
# --------------------------------------------------

st.subheader("📨 Select an Email")

email_options = {
    f"{email['id']} - {email['subject']}": email
    for email in emails
}

selected_label = st.selectbox(
    "Choose an email to process:",
    list(email_options.keys())
)

selected_email = email_options[selected_label]


# --------------------------------------------------
# DISPLAY EMAIL
# --------------------------------------------------

st.subheader("Email Details")

col1, col2 = st.columns(2)

with col1:
    st.write("**Email ID:**", selected_email["id"])
    st.write("**Sender:**", selected_email["sender"])
    st.write("**Subject:**", selected_email["subject"])

with col2:
    st.write("**Body:**")
    st.info(selected_email["body"])


# --------------------------------------------------
# PROCESS EMAIL
# --------------------------------------------------

if st.button(
    "🚀 Process Email",
    type="primary",
    use_container_width=True
):

    with st.spinner("AI is analyzing the email..."):

        result = process_email(selected_email)

    classification = result["classification"]
    action = result["action"]


    # --------------------------------------------------
    # CLASSIFICATION RESULTS
    # --------------------------------------------------

    st.divider()

    st.subheader("🤖 AI Classification")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Intent",
            classification["intent"]
        )

    with col2:
        st.metric(
            "Confidence",
            f"{classification['confidence']}%"
        )

    with col3:
        st.metric(
            "Action",
            action["action"]
        )


    # --------------------------------------------------
    # REASON
    # --------------------------------------------------

    st.subheader("🔍 Classification Reason")

    st.write(
        classification["reason"]
    )


    # --------------------------------------------------
    # ACTION DETAILS
    # --------------------------------------------------

    st.subheader("⚡ Action Details")

    if action["action"] == "Human Review":

        st.warning(
            "👤 Human review is required for this email."
        )

    elif action["action"] == "Mark as Spam":

        st.error(
            "🚫 This email has been classified as spam."
        )

    elif action["action"] == "Invoice Logged":

        st.success(
            "✅ Invoice successfully logged for processing."
        )

    elif action["action"] == "Draft Reply":

        st.info(
            "✉️ A payment-status reply has been prepared "
            "for human review."
        )

    elif action["action"] == "Create Follow-up Task":

        st.warning(
            "📌 A follow-up task has been created for "
            "the finance team."
        )

    st.write(action["action_details"])


    # --------------------------------------------------
    # AUDIT INFORMATION
    # --------------------------------------------------

    st.divider()

    st.subheader("📝 Audit Log")

    audit = result["audit"]

    st.json(audit)