import asyncio
from fastmcp import Client
from google import genai
from google.genai import types
import json
import os
from datetime import date

# 🔑 CRITICAL FIX: Define the strictly compliant JSON Schema
TOOL_CALL_SCHEMA = {
    "type": "object",
    "properties": {
        "tool": {
            "type": "string",
            "description": "The exact name of the tool to be called (e.g., 'list_expenses'). If no tool is appropriate, set to 'None'."
        },
        "params": {
            "type": "object",
            "description": "A dictionary of parameters and their extracted values required for the tool.",
            "minProperties": 0, # Allows {}
        }
    },
    "required": ["tool", "params"]
}

async def interpret_with_gemini(user_message, tools, genai_client):
    # --- 2. Format Tool Definitions for the PROMPT --- (No change here)
    tool_context_list = []
    for tool in tools:
        # Assuming you implemented the fix to get correct type/description info
        params = tool.inputSchema.get('properties', {})
        param_desc = []
        for name, schema_dict in params.items():
            param_type = schema_dict.get('type', 'string')
            param_desc_text = schema_dict.get('description', '')
            desc_part = f" - {param_desc_text}" if param_desc_text else ""
            param_desc.append(f"'{name}' ({param_type}){desc_part}")
        
        params_line = "; ".join(param_desc) if param_desc else "None"
        
        tool_context_list.append(
            f"- Name: {tool.name}\n  Description: {tool.description}\n  Parameters: {params_line}"
        )
    
    tools_context = "\n".join(tool_context_list)
    
    # --- 3. Define the System Instruction (Persona & Rules) --- (No change here)
    today = date.today()
    system_instruction = (
        f"Assume the today is \n{str(today)}\n when interpreting date-related queries. "
        "If the user refers to a month only (e.g., 'October expenses'), use year from Today's date specified above unless otherwise specified."
        "You are a sophisticated AI financial assistant. Your sole task is to determine which "
        "tool to call based on the user's request and the list of available tools provided below. "
        "You MUST respond ONLY with a single JSON object that strictly adheres to the provided schema. "
        "Do not include any other text, explanation, or markdown formatting (e.g., ```json). "
        "If no tool is appropriate, set 'tool' to 'None' and 'params' to an empty dict ({}). "
        "Available Tools:\n"
        f"---BEGIN_TOOLS---\n{tools_context}\n---END_TOOLS---"
    )

    # --- 4. Prepare the Generation Config for Structured Output ---
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
        # 🔑 CRITICAL FIX: Use the manually defined schema dict
        response_json_schema=TOOL_CALL_SCHEMA,
        # REMOVE: response_schema=ToolCall,
    )

    # ... (rest of the function including the API call and JSON parsing remains the same)
    model_name = "gemini-2.5-flash"
    try:
        response = await genai_client.aio.models.generate_content(
            model=model_name,
            contents=user_message,
            config=config,
        )
        
        reply_text = response.text
        return json.loads(reply_text)
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return {"tool": None, "params": {}}


# The main function needs to be updated to pass the client
async def main():
    # Configure API key... (assuming it's done outside or globally)
    API_KEY = os.getenv("GOOGLE_API_KEY")
    if not API_KEY:
        raise ValueError("Set your GOOGLE_API_KEY environment variable")
    
    # Create GenAI client
    genai_client = genai.Client(api_key=API_KEY)
    
    client = Client("http://127.0.0.1:8000/mcp")
    async with client:
        # fastmcp tools are expected to be available here
        tools = await client.list_tools()
        print("Available tools:", tools)

        user_message = input("Enter your request: ")

        # Pass the genai_client to the function
        llm_result = await interpret_with_gemini(user_message, tools, genai_client)
        tool_name = llm_result.get("tool")
        params = llm_result.get("params", {})

        if tool_name and tool_name != "None":
            print(f"Calling tool: **{tool_name}** with params: **{params}**")
            # Note: client.call_tool is assumed to handle dynamic arguments (**params)
            result = await client.call_tool(tool_name, params)
            print("Tool result:", result)
        else:
            print("LLM did not select a tool or explicitly returned 'None'.")
            print("LLM's raw output:", llm_result)

asyncio.run(main())