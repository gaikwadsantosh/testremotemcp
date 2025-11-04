
import asyncio
from fastmcp import Client

async def main():
    # Replace this URL with your MCP server endpoint
    client = Client("http://127.0.0.1:8000/mcp")

    async with client:
        # Ping the server
        await client.ping()

        # List available tools
        tools = await client.list_tools()
        print("Available tools:", tools)

        print("Adding Expense:")
        # Example to add an expense
        await client.call_tool("add_expense", {
            "date": "2025-10-31",
            "amount": 1000,
            "category": "Housing",
            "note": "rent"
        })

        print("Listing Expenses for October 2025:")
        result = await client.call_tool("list_expenses", {
            "start_date": "2025-10-01",
            "end_date": "2025-10-31"
        })
        print(result)

asyncio.run(main())
