Multi-Step Flow 1: Asking About Medication Information
Goal: User wants factual information about a medication.
    User asks, "Tell me about amoxicillin"
Expected flow:
1) The agent asks: "how can I help you today?"
2) The user asks responds with a question about a medication using its name.
3) The agent calls the get_medication_by_name tool with the medication name.
4) The tool queries the SQLite db and returns medication details such as active ingredients, dosage form, prescription requirements.
5) The agent uses the tool response to generate a factual explanation of the medication.
6) The agent only provides factual information and avoids giving medical advice or diagnosis.

tool used: get_medication_by_name

agent response:
The agent provides factual information about the medication while clearly avoiding any medical advice.

Multi-Step Flow 2: Asking Inventory Stock Questions 