"""Tool schemas exported for the agent and for registration with an LLM.

Each entry is a single tool definition compatible with the OpenAI Responses API
`tools` parameter. Every entry contains these fields:
- type: must be "function"
- name: stable tool identifier (string)
- description: short description
- parameters: JSON Schema describing the arguments (type=object)

Do not add other top-level keys here; the agent will pass this list directly to
the Responses API as `tools`.
"""

# Responses API expects each tool entry to include top-level keys:
# - type: "function"
# - name
# - description
# - parameters (JSON Schema)
# We'll export TOOL_SCHEMAS in that flattened shape so it can be passed directly
# to client.responses.create(..., tools=TOOL_SCHEMAS)
TOOL_SCHEMAS = [
    {
        "type": "function",
        "name": "get_medication_by_name",
        "description": "Retrieve factual information about a medication by its name.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Exact or partial medication name to search for."},
                "limit": {"type": "integer", "description": "Maximum number of results to return", "default": 10}
            },
            "required": ["name"]
        }
    },
    {
        "type": "function",
        "name": "check_medication_stock",
        "description": "Check whether a medication is in stock and how many units are available.",
        "parameters": {
            "type": "object",
            "properties": {
                "med_id": {"type": "string", "description": "Medication identifier (med_id)."},
                "name": {"type": "string", "description": "Medication name (alternative to med_id)."}
            },
            "required": ["med_id"]
        }
    },
    {
        "type": "function",
        "name": "check_user_prescription",
        "description": "Check whether a user has a prescription for a medication.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "User identifier."},
                "med_id": {"type": "string", "description": "Medication identifier."},
                "name": {"type": "string", "description": "Medication name (alternative to med_id)."}
            },
            "required": ["user_id", "med_id"]
        }
    }
]


def get_flattened_tool_schemas():
    """Return TOOL_SCHEMAS in flattened shape (name/description/parameters at top level).

    This helper is kept for backward compatibility with modules that import it.
    """
    return TOOL_SCHEMAS

