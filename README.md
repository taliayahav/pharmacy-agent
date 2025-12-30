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

Database scripts and data
-------------------------
- `data/init_db.py` - creates the local SQLite schema used by the project. It creates three tables: `users` (user_id, name), `medications` (med_id, name, active_ingredients, requires_prescription, dosage_info, stock) and `prescriptions` (user_id, med_id) with foreign keys enforced.
- `data/seed_db.py` - inserts example rows into those tables (users, medications, and a few prescriptions).

Data notes
----------
- The seeded data is synthetic and intentionally created for development and testing (example medication IDs like `m1`, `m2`, user IDs like `u1`). Do not treat it as real clinical or inventory data.
- Medication fields include basic factual fields that the agent queries: `name`, `active_ingredients`, `dosage_info`, whether a prescription is required, and `stock` levels.

How the DB supports the agent
----------------------------
- The agent's local tools (`app/tools.py`) read this database to answer factual queries. Typical flows:
	- The LLM requests a tool call (e.g., `get_medication_by_name`).
	- The agent runs the corresponding function, which queries `data/pharmacy.db` and returns a JSON-friendly dict with the requested info.
	- That result is appended to the conversation history and passed back to the model so the assistant can produce a final, informed reply.

These scripts are intentionally simple so you can re-run `data/init_db.py` and `data/seed_db.py` to recreate the local development DB at `data/pharmacy.db`.