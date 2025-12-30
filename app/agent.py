import os
import json
import inspect
from typing import Any, Dict, List, Optional

from openai import OpenAI
from app.tool_schemas import get_flattened_tool_schemas
from app.tools import get_medication_by_name, check_medication_stock, check_user_prescription

TOOL_SCHEMAS = get_flattened_tool_schemas()
SYSTEM_PROMPT = (
    "You are a pharmacy assistant. Provide factual information only. "
    "Never give medical advice, never diagnose, and never encourage users to purchase or order products. "
    "If asked for medical advice, diagnosis, dosing, or to buy a product, respond with a short refusal and suggest the user consult a licensed healthcare professional or pharmacist. "
    "Use tools only for factual lookups and return neutral, factual results. "
    "Specifically, when asked about availability or stock, call the function 'check_medication_stock' with the medication's med_id; "
    "when asked whether a user has a prescription, call the function 'check_user_prescription' with user_id and med_id."
)


def _enforce_nonmedical(text: str) -> str:
    """Return a safe refusal string if the assistant appears to be giving medical advice
    or encouraging purchases. This uses a small keyword heuristic and is intentionally
    conservative — it only triggers on clear recommendation/purchase phrasing.
    """
    if not text:
        return text
    low = text.lower()
    # Trigger only on explicit recommendation or purchase phrasing.
    triggers = [
        "you should",
        "i recommend",
        "i'd recommend",
        "you must",
        "should take",
        "order now",
        "prescribe",
    ]
    purchase_triggers = ["buy", "purchase", "order now"]
    for t in triggers:
        if t in low:
            return (
                "I can't provide medical advice, diagnoses, or purchasing recommendations. "
                "I can provide factual information about medications and recommend you consult a licensed healthcare professional or pharmacist for personalized advice."
            )
    # If the text explicitly urges purchasing (buy/purchase) in a recommendation context, block it.
    for p in purchase_triggers:
        if p in low and ("should" in low or "recommend" in low or "must" in low or "prescribe" in low):
            return (
                "I can't provide medical advice, diagnoses, or purchasing recommendations. "
                "I can provide factual information about medications and recommend you consult a licensed healthcare professional or pharmacist for personalized advice."
            )
    return text


def is_advice_request(user_message: str) -> bool:
    """Return True when the user's message appears to request medical advice,
    personalized dosing, or diagnosis. This is a small intent heuristic used to
    decide whether to enforce the non-medical refusal.
    """
    if not user_message:
        return False
    low = user_message.lower()
    patterns = [
        "should i",
        "can i",
        "is it safe",
        "what should i",
        "what dose",
        "how much should",
        "am i",
        "do i need",
        "do i have symptoms",
        "diagnos",
        "pregnant",
        "breastfeeding",
    ]
    for p in patterns:
        if p in low:
            return True
    return False

def _get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required")
    return OpenAI(api_key=api_key)

# _build_tools_for_sdk was a passthrough and is removed to simplify the module.

def _extract_output_text(resp: Any) -> Optional[str]:
    # 1) direct output_text (allow empty string)
    ot = getattr(resp, "output_text", None)
    if ot is not None:
        return ot
    # 2) iterate output[*].content[*].text
    out = getattr(resp, "output", None)
    if isinstance(out, list):
        for item in out:
            content = getattr(item, "content", None)
            if isinstance(content, list):
                for c in content:
                    txt = getattr(c, "text", None)
                    if txt is not None:
                        return txt
            # fallback for tool_call output_text
            tool_out = getattr(item, "output_text", None)
            if tool_out:
                return tool_out
    # 3) dict fallback (last resort)
    if isinstance(resp, dict):
        if "output_text" in resp:
            return resp["output_text"]
        if "text" in resp:
            return resp["text"]
    return None

def handle_tool_call(tool_call: Any) -> Dict[str, Any]:
    name = getattr(tool_call, "name", None)
    args_raw = getattr(tool_call, "arguments", "{}")
    try:
        args = json.loads(args_raw) if isinstance(args_raw, str) else args_raw or {}
    except Exception:
        args = {}

    # Simple schema-driven sanitizer: keep only declared params and apply defaults
    schema_map: Dict[str, Dict[str, Any]] = {}
    for t in TOOL_SCHEMAS:
        tname = t.get("name")
        params = t.get("parameters") or {}
        props = params.get("properties", {}) if isinstance(params, dict) else {}
        schema_map[tname] = {"properties": props}

    def _coerce_value(val: Any, sch: Dict[str, Any]) -> Any:
        t = sch.get("type")
        if t == "integer":
            try:
                return int(val)
            except Exception:
                return val
        if t == "boolean":
            if isinstance(val, bool):
                return val
            if isinstance(val, str):
                v = val.strip().lower()
                if v in ("true", "1", "yes"):
                    return True
                if v in ("false", "0", "no"):
                    return False
            return bool(val)
        return val

    def validate_and_coerce(tool_name: str, raw_args: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name not in schema_map:
            return {}
        props = schema_map[tool_name]["properties"]
        out: Dict[str, Any] = {}
        for k, info in props.items():
            if k in raw_args:
                out[k] = _coerce_value(raw_args[k], info)
            else:
                if "default" in info:
                    out[k] = info.get("default")
        return out

    safe_args = validate_and_coerce(name, args or {})
    def _filter_for_callable(func, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        try:
            sig = inspect.signature(func)
        except Exception:
            return kwargs
        params = sig.parameters
        # if function accepts **kwargs, return as-is
        for p in params.values():
            if p.kind == inspect.Parameter.VAR_KEYWORD:
                return kwargs
        allowed = set(params.keys())
        return {k: v for k, v in (kwargs or {}).items() if k in allowed}

    if name == "get_medication_by_name":
        return get_medication_by_name(**_filter_for_callable(get_medication_by_name, safe_args))

    # If the model supplied a medication name instead of med_id, resolve it first
    if name == "check_medication_stock":
        # attempt to resolve name -> med_id
        if "med_id" not in safe_args and "name" in safe_args:
            med = get_medication_by_name(safe_args.get("name"))
            if med.get("error"):
                return {"error": "medication_not_found", "details": med.get("error")}
            safe_args["med_id"] = med.get("med_id")
        return check_medication_stock(**_filter_for_callable(check_medication_stock, safe_args))

    if name == "check_user_prescription":
        # if the model provided a name, resolve it to med_id
        if "med_id" not in safe_args and "name" in safe_args:
            med = get_medication_by_name(safe_args.get("name"))
            if med.get("error"):
                return {"error": "medication_not_found", "details": med.get("error")}
            safe_args["med_id"] = med.get("med_id")
        # require user_id — don't guess; return structured error so the model can ask for it
        if "user_id" not in safe_args or not safe_args.get("user_id"):
            return {"error": "user_id_required", "message": "Please provide a user_id (e.g., 'u1') to check prescriptions."}
        return check_user_prescription(**_filter_for_callable(check_user_prescription, safe_args))
    return {"error": f"unknown tool {name}"}

def chat(user_message: str, concise: bool = False, history: Optional[List[Dict[str, str]]] = None) -> str:

    # If no history provided, create a fresh conversation; otherwise append to the provided history
    if history is None:
        history = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]
        if concise:
            history.append({"role": "system", "content": "When possible, respond concisely in a short paragraph or bullets."})
        history.append({"role": "user", "content": user_message})
    else:
        # assume caller manages the history list; just append the new user turn
        history.append({"role": "user", "content": user_message})

    tools = TOOL_SCHEMAS

    try:
        client = _get_client()
    except RuntimeError:
        # Mock fallback if API key missing
        mock = {"error": "OPENAI_API_KEY not set; mock response"}
        if "amoxicillin" in user_message.lower():
            mock = {
                "med_id": "m1",
                "name": "Amoxicillin",
                "active_ingredient": "Amoxicillin",
                "dosage": "500mg every 8 hours",
                "prescription_required": True,
                "stock": 42,
            }
        out = f"(mock) I found: {json.dumps(mock)}"
        return _enforce_nonmedical(out) if is_advice_request(user_message) else out

    first = client.responses.create(model="gpt-5", input=history, tools=tools)
    first_text = _extract_output_text(first)
    tool_call = None
    out = getattr(first, "output", None)
    if isinstance(out, list):
        for item in out:
            itype = getattr(item, "type", None)
            if itype in ("tool_call", "function_call"):
                tool_call = item
                break

    if tool_call is not None:
        tool_result = handle_tool_call(tool_call)
        # append tool result to conversation (machine-readable)
        history.append({"role": "assistant", "content": f"Tool {getattr(tool_call, 'name', 'tool')} called."})
        history.append({"role": "assistant", "content": json.dumps(tool_result)})
        # final call to the model with tool result appended
        final = client.responses.create(model="gpt-5", input=history)
        final_text = _extract_output_text(final)
        if final_text is not None:
            return _enforce_nonmedical(final_text) if is_advice_request(user_message) else final_text

    if first_text is not None:
        return _enforce_nonmedical(first_text) if is_advice_request(user_message) else first_text

    return "I couldn't generate a response."

def repl():
    print("Pharmacy Agent REPL. Type 'exit' or 'quit' to stop.")
    # maintain persistent conversation history across turns
    history: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    # agent asks first to simulate a conversational assistant and make it part of history
    greeting = "How can I help you today?"
    print(f"Agent: {greeting}")
    history.append({"role": "assistant", "content": greeting})
    while True:
        try:
            user_input = input("User: ").strip()
        except (EOFError, KeyboardInterrupt):
            # graceful exit on Ctrl-D / Ctrl-C
            print()
            break
        if not user_input:
            # ignore empty input and continue
            continue
        if user_input.lower() in {"exit", "quit"}:
            break
        # pass the persistent history into chat so the model retains context
        response = chat(user_input, history=history)
        out = (response or "").strip() or "I couldn't generate a response."
        print(f"Agent: {out}")

if __name__ == "__main__":
    # start interactive REPL
    repl()
