This evaluation plan verifies that the Pharmacy AI Agent works as intended, provides factual information, correctly uses tools, respects policy restrictions, and executes multi-step flows reliably.

Evaluation Steps

Multi-step flow coverage
Test each designed flow

Medication information

Stock inventory

Prescription verification
For each flow, run 2–3 example queries. Check that the agent executes the correct tool calls in order and produces valid responses.

Tool and API validation
Confirm that get_medication_by_name, check_medication_stock, and check_user_prescription return correct data from the database.
Test edge cases such as invalid medications, out-of-stock items, and users without prescriptions.

Policy adherence check
Ensure the agent never gives medical advice, diagnoses, or encourages purchases.
Test questions that attempt to get advice and verify the agent redirects to general information or a healthcare professional.

Language support
Verify the agent responds correctly in English and Hebrew for each flow.

Error handling and fallback
Run queries when the database is missing data or a tool call fails.
Verify the agent returns a meaningful fallback response without throwing exceptions.

Automation and screenshots
Optionally, run a script that executes all flows and prints whether outputs meet expectations.
Include screenshots of interactions as evidence.