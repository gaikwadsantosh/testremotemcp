import requests
import json
import uuid
import google.generativeai as genai

# 1️⃣ Configure Gemini
genai.configure(api_key="")

model = genai.GenerativeModel("gemini-1.5-flash")

# 2️⃣ MCP endpoint
MCP_URL = "http://127.0.0.1:8000/mcp"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}


# 3️⃣ JSON-RPC helper
def json_rpc_call(method: str, params: dict):
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": method,
        "params": params or {}
    }
    resp = requests.post(MCP_URL, headers=HEADERS, json=payload)
    resp.raise_for_status()
    data = resp.json()

    if "error" in data:
        raise RuntimeError(f"MCP error: {data['error']}")
    return data["result"]


# 4️⃣ Get list of available tools
result = json_rpc_call("tools/list", {})
tools = result["tools"]

print("✅ Available tools:")
print(json.dumps(tools, indent=2))

exit()

# 5️⃣ Ask Gemini to map user query → tool + arguments
user_query = "list all expenses for October"

system_prompt = f"""
You are an assistant that maps user queries to MCP tool calls.
Available tools (JSON):
{json.dumps(tools, indent=2)}

Return only JSON in this format:
{{
  "tool_name": "...",
  "arguments": {{ ... }}
}}
"""

response = model.generate_content([
    {"role": "system", "parts": system_prompt},
    {"role": "user", "parts": user_query}
])

structured = response.text.strip()
print("\n🤖 Gemini output:\n", structured)
parsed = json.loads(structured)

# 6️⃣ Call tool through MCP JSON-RPC
call_result = json_rpc_call("tools/call", {
    "name": parsed["tool_name"],
    "arguments": parsed["arguments"]
})

print("\n✅ Tool call result:")
print(json.dumps(call_result, indent=2))
