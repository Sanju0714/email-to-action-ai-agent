# Email-to-Action AI Agent

An LLM-powered email processing agent that automatically classifies incoming emails, determines the appropriate action, and maintains an audit trail for every decision.

## Overview

The Email-to-Action AI Agent converts unstructured emails into actionable workflows using an LLM.

The system:

1. Receives an email
2. Classifies it into a predefined intent
3. Assigns a confidence score
4. Routes low-confidence emails to human review
5. Performs an intent-specific action
6. Records the decision and action in an audit log

## Key Features

- **LLM-based Email Classification**
  - Invoice Submission
  - Payment Query
  - Dispute
  - Spam
  - Ambiguous

- **Confidence-Based Decision Making**
  - Generates a confidence score from 0–100
  - Uses a 70% confidence threshold
  - Routes low-confidence emails to human review

- **Automated Actions**
  - Invoice Logged
  - Draft Reply
  - Create Follow-up Task
  - Mark as Spam
  - Human Review

- **Safety Checks**
  - Validates the predicted intent before performing an action
  - Prevents unsupported actions from being executed

- **Audit Logging**
  - Email ID
  - Sender
  - Subject
  - Intent
  - Confidence
  - Reason
  - Action
  - Timestamp

## Architecture

```text
                 Incoming Email
                       |
                       v
              +------------------+
              |   LLM Classifier |
              +------------------+
                       |
                       v
              Intent + Confidence
                       |
              +--------+--------+
              |                 |
        Confidence >= 70%   Confidence < 70%
              |                 |
              v                 v
       Intent Validation    Human Review
              |
              v
      +-------------------+
      | Action Dispatcher |
      +-------------------+
              |
       +------+------+------+------+
       |      |      |      |
    Invoice Payment Dispute Spam
     Log    Reply    Task   Mark
              |
              v
        Audit Log (JSON)
