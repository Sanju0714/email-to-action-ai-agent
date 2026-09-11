import json
import os
from datetime import datetime

from dotenv import load_dotenv
from groq import Groq


# Load API key from .env
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# --------------------------------------------------
# 1. CLASSIFY EMAIL
# --------------------------------------------------

def classify_email(email):
    """
    Classifies an email into exactly one supported intent.
    """

    prompt = f"""
You are an email classification agent for a fictional business.

Classify the email into exactly ONE of these categories:

1. Invoice Submission
2. Payment Query
3. Dispute
4. Spam
5. Ambiguous

Rules:

- Invoice Submission:
  The sender is submitting or asking to process an invoice.

- Payment Query:
  The sender is asking about payment status, payment timing,
  or when money will be received.

- Dispute:
  The sender clearly states that they disagree with,
  challenge, reject, or dispute an amount, transaction,
  charge, or invoice.

  Examples:
  "The amount charged is incorrect."
  "We dispute this invoice."
  "This transaction is incorrect."
  "The invoice amount is wrong."

- Spam:
  Promotional, fraudulent, irrelevant, or suspicious email.

- Ambiguous:
  The email is vague or does not clearly match one of
  the four main categories.

  Examples:
  "There seems to be an issue with our transaction."
  "Please check this."
  "Something looks wrong."
  "There is a problem with the recent transaction."

Important:
If an email only says there is an issue, problem, or concern
without clearly stating what is wrong or explicitly disputing
a charge, transaction, or invoice, classify it as Ambiguous.

Confidence must be a number between 0 and 100.

If confidence is below 70, classify the email as Ambiguous.

If the email is vague or does not clearly match one of the
four main categories, classify it as Ambiguous.

Return ONLY valid JSON.

Use exactly this format:

{{
    "intent": "Invoice Submission",
    "confidence": 95,
    "reason": "The email contains an invoice submission request."
}}

EMAIL:
Sender: {email["sender"]}
Subject: {email["subject"]}
Body: {email["body"]}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    result = json.loads(
        response.choices[0].message.content
    )

    # Extra safety check
    allowed_intents = {
        "Invoice Submission",
        "Payment Query",
        "Dispute",
        "Spam",
        "Ambiguous"
    }

    if result["intent"] not in allowed_intents:
        result["intent"] = "Ambiguous"
        result["confidence"] = 0
        result["reason"] = "The intent could not be classified safely."

    # Enforce the confidence rule
    if result["confidence"] < 70:
        result["intent"] = "Ambiguous"

    return result


# --------------------------------------------------
# 2. PERFORM ACTION
# --------------------------------------------------

def perform_action(email, classification):
    """
    Performs an action based on the detected intent.
    """

    intent = classification["intent"]

    if intent == "Invoice Submission":

        action = "Invoice Logged"

        action_details = (
            f"Invoice from {email['sender']} has been "
            "logged for processing."
        )

    elif intent == "Payment Query":

        action = "Draft Reply"

        action_details = (
            "A payment-status reply has been prepared "
            "for human review."
        )

    elif intent == "Dispute":

        action = "Create Follow-up Task"

        action_details = (
            "A follow-up task has been created for the "
            "finance team to review the dispute."
        )

    elif intent == "Spam":

        action = "Mark as Spam"

        action_details = (
            "The email has been marked as spam and "
            "requires no further processing."
        )

    else:

        action = "Human Review"

        action_details = (
            "The email requires human review because "
            "the intent could not be determined confidently."
        )

    return {
        "action": action,
        "action_details": action_details
    }


# --------------------------------------------------
# 3. SAVE AUDIT LOG
# --------------------------------------------------

def save_audit_log(email, classification, action_result):
    """
    Stores processing history in audit_log.json.
    """

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "email_id": email["id"],
        "sender": email["sender"],
        "subject": email["subject"],
        "intent": classification["intent"],
        "confidence": classification["confidence"],
        "reason": classification["reason"],
        "action": action_result["action"],
        "action_details": action_result["action_details"]
    }

    try:
        with open(
            "audit_log.json",
            "r",
            encoding="utf-8"
        ) as file:

            audit_log = json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):

        audit_log = []

    audit_log.append(log_entry)

    with open(
        "audit_log.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            audit_log,
            file,
            indent=4
        )

    return log_entry


# --------------------------------------------------
# 4. PROCESS EMAIL
# --------------------------------------------------

def process_email(email):
    """
    Complete email-to-action workflow.
    """

    classification = classify_email(email)

    action_result = perform_action(
        email,
        classification
    )

    audit_entry = save_audit_log(
        email,
        classification,
        action_result
    )

    return {
        "email": email,
        "classification": classification,
        "action": action_result,
        "audit": audit_entry
    }


# --------------------------------------------------
# 5. TEST THE AGENT
# --------------------------------------------------

if __name__ == "__main__":

    with open(
        "emails.json",
        "r",
        encoding="utf-8"
    ) as file:

        emails = json.load(file)

    for email in emails:

        print("\n" + "=" * 60)

        print("EMAIL ID:", email["id"])

        print("SUBJECT:", email["subject"])

        print("=" * 60)

        result = process_email(email)

        print("\nINTENT:")
        print(result["classification"]["intent"])

        print("CONFIDENCE:")
        print(result["classification"]["confidence"])

        print("REASON:")
        print(result["classification"]["reason"])

        print("\nACTION:")
        print(result["action"]["action"])

        print("ACTION DETAILS:")
        print(result["action"]["action_details"])