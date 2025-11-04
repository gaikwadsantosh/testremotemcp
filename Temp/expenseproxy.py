from fastmcp import FastMCP
import os

mcp = FastMCP.as_proxy("http://127.0.0.1:8000/mcp", name="ExpenseTrackerProxy")

if __name__ == "__main__":
    mcp.run()
