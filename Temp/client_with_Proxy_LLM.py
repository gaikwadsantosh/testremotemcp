import requests
import json
import google.generativeai as genai

# 1️⃣ Configure Gemini
genai.configure(api_key="")
model = genai.GenerativeModel("gemini-1.5-flash")

# 2️⃣ Set your proxy URL
PROXY_URL = "http://127.0.0.1:6277"  # default FastMCP proxy port

headers = {
    "Content-Type": "application/json",
}

# 3️⃣ Get list of tools from MCP server via proxy
payload = {
    "method": "tools/list",
    "params": {}
}

resp = requests.post(PROXY_URL, headers=headers, json=payload)
resp.raise_for_status()
tools = resp.json()["tools"]

print("✅ Tools available:")
print(json.dumps(tools, indent=2))

exit()

# 4️⃣ Natural language query
user_query = "list expenses for October"

# 5️⃣ Ask Gemini which tool + arguments to call
system_prompt = f"""
You are an intelligent client for a Model Context Protocol (MCP) server.
Available tools (JSON):
{json.dumps(tools, indent=2)}

Given a natural language query, decide which tool to call and what arguments to pass.
Return *only JSON* in this format:
{{
  "method": "tools/call",
  "params": {{
     "name": "<tool_name>",
     "arguments": {{ ... }}
  }}
}}
"""

response = model.generate_content([
    {"role": "system", "parts": system_prompt},
    {"role": "user", "parts": user_query}
])

structured = response.text.strip()
print("\n🤖 Gemini output:\n", structured)
parsed = json.loads(structured)

# 6️⃣ Call the tool via proxy
call_payload = {
    "method": "tools/call",
    "params": parsed["params"]
}

call_resp = requests.post(PROXY_URL, headers=headers, json=call_payload)
call_resp.raise_for_status()
print("\n✅ Server Response:")
print(json.dumps(call_resp.json(), indent=2))
