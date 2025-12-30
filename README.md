This Pharmacy AI Agent uses OpenAI Responses API, it's a stateless phaarmacy assistant that is able to handle workflows such as prescription management, inventory control, and customer service.
there are 3 main files to this package:
1) agent.py - The driver of the Response API, implementing the two-phase model. Tool --> model flow
-the user inputs a string, and the agent's string is output.
2) tools.py - the code that reads/writes the local SQLite database. It has helper functions that interacts with the db and then provides the medication and prescription related operations that the agent uses to respond.
3) tool_schemas.py - a list of tool definitions compatible with OpenAI Responses API

List of tools:
get_medication_by_name - retrieves medication and its factual info
check_medication_stock - checks if medication is in stock and how much
check_user_prescription - checks if a user has a prescription for specified medication

The Pharmacy Agent only provides factual information about medications.
The Pharmacy Agent does not provide medical advice.
The Pharmacy Agent does not encourage any purchases.
The Pharmacy Agent does not diagnose anyone.
