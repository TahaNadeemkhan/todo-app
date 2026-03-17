"""
MCP Tools Package

All tools follow the stateless FastMCP pattern:
- Decorated with @mcp.tool(name="...", description="...")
- Store ALL state in Neon PostgreSQL database
- No in-memory state or caching
- Support horizontal scaling

Available Tools:
- add_task: Create new tasks
- list_tasks: Retrieve task lists with filtering
- complete_task: Mark tasks as completed
- delete_task: Remove tasks from database
"""

# Tool modules are imported by server.py to trigger registration
# No need to re-export them here
