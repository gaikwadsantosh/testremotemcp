
Run Code for testing in MCP Inspector
---------------------------
uv run fastmcp dev server.py  -- this command will lanuch the MCP inspector, but you need to run another command to run server

--------------
Run Server (FASTMCP)
--------------
python server.py -- This command will run the actual server

--------------
Run Client 
--------------
1. Client Backend (FASTAPI) \client\backend
python -m uvicorn backend:app --reload --host 0.0.0.0 --port 9000

2. Client UI (STREAMLIT) \client\frontend
streamlit run frontend.py



------------------------
Other Options to Add tool to Claud Desktop
------------------------
Option 1 (with premium version of claud desktop) - deploy code to fastmcp cloud through github, copy the url and add connector in cluad desktop

Option 2 (through local proxy server):   
1. create expenseproxy.py file
2. test with mcp inspector uv run fastmcp dev expenseproxy.py (make sure server is running with python server.py)
2.1 connect in mcp insppector with stdio
3. to deploy in claud-desktop run uv run fastmcp install claude-desktop expenseproxy.py
3.1 go to claude desktop -> settings -> developers ->  edit config -> open claude-desktop-config.json -> add the full path of uv (you can find the path by command where uv)
3. connect this in claud desktop as stdio
