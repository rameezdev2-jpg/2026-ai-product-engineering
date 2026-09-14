import asyncio
import os
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters, stdio_client


def test_real_stdio_tool_discovery_and_permissions(tmp_path):
    async def scenario():
        env={**os.environ,'DATABASE_PATH':str(tmp_path/'mcp.sqlite3'),'MCP_TENANT':'demo','MCP_ROLE':'analyst'}
        server=StdioServerParameters(command=sys.executable,args=[str(Path(__file__).resolve().parents[1]/'mcp_server.py')],env=env)
        async with stdio_client(server) as (read,write):
            async with ClientSession(read,write) as client:
                await client.initialize()
                tools=await client.list_tools()
                assert {t.name for t in tools.tools}=={'plan_task','execute_plan','business_report'}
                result=await client.call_tool('business_report',{})
                assert not result.is_error
                assert 'task_count' in str(result)
                result=await client.call_tool('execute_plan',{'plan_id':99999})
                assert result.is_error
    asyncio.run(scenario())
