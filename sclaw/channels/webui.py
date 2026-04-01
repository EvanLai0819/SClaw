"""Web UI channel using aiohttp."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import aiohttp.web

from sclaw.core.logger import get_logger

if TYPE_CHECKING:
    from sclaw.channels.gateway import Gateway
    from sclaw.core.config import WebUIConfig

logger = get_logger(__name__)


class WebUIChannel:
    """
    Web UI chat interface using aiohttp.
    Provides a web-based chat interface for interacting with the agent.
    """

    def __init__(self, config: "WebUIConfig", gateway: "Gateway"):
        """
        Initialize WebUIChannel.

        Args:
            config: Web UI configuration
            gateway: Gateway for message routing
        """
        self.config = config
        self.gateway = gateway
        self.app = aiohttp.web.Application()
        self.runner: Any = None
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Set up HTTP routes."""
        self.app.router.add_get("/", self._serve_html)
        self.app.router.add_get("/api/status", self._api_status)
        self.app.router.add_post("/api/chat", self._api_chat)
        
        # Add static file route for js directory
        static_dir = Path(__file__).parent
        self.app.router.add_static('/js/', static_dir / 'js', name='js')

    async def start(self, port: int = 18791) -> None:
        """
        Start Web UI server.

        Args:
            port: Port to listen on
        """
        self.runner = aiohttp.web.AppRunner(self.app)
        await self.runner.setup()

        site = aiohttp.web.TCPSite(self.runner, "0.0.0.0", port)
        await site.start()

        logger.info(f"Web UI: http://0.0.0.0:{port}")

    async def _serve_html(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        """Serve the Web UI HTML page."""
        html_path = Path(__file__).parent / "webui.html"
        if html_path.exists():
            return aiohttp.web.FileResponse(html_path)
        return aiohttp.web.Response(
            text="Web UI not found", status=404
        )

    async def _api_status(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        """Return current status as JSON."""
        return aiohttp.web.json_response(
            {
                "status": "online",
            }
        )

    async def _api_chat(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        """Handle chat messages from Web UI."""
        try:
            data = await request.json()
        except Exception:
            return aiohttp.web.json_response(
                {"error": "Invalid JSON"}, status=400
            )

        message = data.get("message", "")
        session_id = data.get("session_id", "web_default")

        if not message:
            return aiohttp.web.json_response(
                {"error": "Message is required"}, status=400
            )

        try:
            response = await self.gateway.handle_incoming(
                channel_id="webui",
                user_id=session_id,
                message=message,
            )
            return aiohttp.web.json_response({"response": response})
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return aiohttp.web.json_response(
                {"error": f"Sorry, something went wrong: {e}"},
                status=500,
            )

    async def send_proactive(self, text: str) -> None:
        """
        Send a proactive message (from cron or background task).
        Note: Web UI doesn't support proactive messages like Telegram.
        """
        pass

    async def stop(self) -> None:
        """Graceful shutdown."""
        if self.runner:
            await self.runner.cleanup()
            logger.info("Web UI stopped")
