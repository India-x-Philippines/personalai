"""
Friday MCP Server — Entry Point
Run with: python server.py
"""

import os
from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse
from livekit import api

from friday.tools import register_all_tools
from friday.prompts import register_all_prompts
from friday.resources import register_all_resources
from friday.config import config

# Create the MCP server instance
mcp = FastMCP(
    name=config.SERVER_NAME,
    instructions=(
        "You are Friday, a Tony Stark-style AI assistant. "
        "You have access to a set of tools to help the user. "
        "Be concise, accurate, and a little witty."
    ),
)

# Register tools, prompts, and resources
register_all_tools(mcp)
register_all_prompts(mcp)
register_all_resources(mcp)

# Custom HTTP Routes
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint for startup verification."""
    return JSONResponse({
        "status": "ok",
        "server": config.SERVER_NAME,
        "mcp": True
    })

@mcp.custom_route("/api/token", methods=["GET"])
async def get_livekit_token(request):
    """
    Generates a short-lived LiveKit access token for the browser client.
    Never exposes LIVEKIT_API_SECRET to the browser.
    """
    api_key = config.LIVEKIT_API_KEY or os.getenv("LIVEKIT_API_KEY", "")
    api_secret = config.LIVEKIT_API_SECRET or os.getenv("LIVEKIT_API_SECRET", "")
    url = config.LIVEKIT_URL or os.getenv("LIVEKIT_URL", "")

    if not api_key or not api_secret or "your-" in api_key:
        return JSONResponse(
            {"error": "LiveKit credentials not configured in .env"},
            status_code=500
        )

    room_name = request.query_params.get("room", "friday-room")
    identity = request.query_params.get("identity", "user-browser")

    try:
        token = (
            api.AccessToken(api_key, api_secret)
            .with_identity(identity)
            .with_name("User Browser")
            .with_grants(api.VideoGrants(room_join=True, room=room_name))
            .to_jwt()
        )
        return JSONResponse({
            "token": token,
            "url": url,
            "room": room_name,
            "identity": identity
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

def main():
    mcp.run(transport='sse')

if __name__ == "__main__":
    main()