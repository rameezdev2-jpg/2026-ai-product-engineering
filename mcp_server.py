"""Local stdio MCP server. Identity and role come from its trusted launch environment."""
import os
from mcp.server.mcpserver import MCPServer
from automation import plan,execute
server=MCPServer('Rameez Business Tools')
@server.tool()
def plan_task(title:str) -> dict:
    """Prepare a task; a human must approve it through the separate API before execution."""
    return {'plan_id':plan(os.environ.get('MCP_TENANT','demo'),'create_task',{'title':title})}
@server.tool()
def execute_plan(plan_id:int) -> dict:
    """Execute an allowed, approved plan exactly once. Agents cannot approve plans."""
    return execute(os.environ.get('MCP_TENANT','demo'),plan_id,os.environ.get('MCP_ROLE','analyst'))
@server.tool()
def business_report() -> dict:
    """Read the task count in this server's workspace."""
    tenant=os.environ.get('MCP_TENANT','demo')
    return execute(tenant,plan(tenant,'report',{}),os.environ.get('MCP_ROLE','analyst'))
if __name__=='__main__': server.run(transport='stdio')
