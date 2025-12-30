"""
Stateless MCP Server for Todo Operations

CRITICAL: This server is stateless for horizontal scaling (Phase 3 requirement).
ALL state is stored in Neon PostgreSQL database.

Architecture:
- Uses FastMCP with stateless_http=True for load balancing
- Tools are registered via decorators in separate modules
- Each tool fetches/stores state from/to database
- No in-memory state or session storage
- Exports streamable_http_app() for ASGI deployment (Uvicorn/Hypercorn)

Deployment:
    uvicorn mcp_server.server:mcp_app --host 0.0.0.0 --port 8000
"""

from mcp.server.fastmcp import FastMCP

# Initialize the stateless MCP server
mcp = FastMCP("Todo AI Agent", stateless_http=True)

# Import all tool modules to register them with the mcp instance
# The @mcp.tool() decorators in these modules will auto-register the tools
from mcp_server.tools import add_task      # noqa: F401
from mcp_server.tools import list_tasks    # noqa: F401
from mcp_server.tools import complete_task # noqa: F401
from mcp_server.tools import delete_task   # noqa: F401
from mcp_server.tools import update_task   # noqa: F401

# Export the streamable HTTP app for ASGI deployment
# This enables horizontal scaling with load balancers
mcp_app = mcp.streamable_http_app()
