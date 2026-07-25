import os
import ssl
import time
from typing import TYPE_CHECKING

import aiohttp

from discordgsm.protocols.protocol import Protocol

if TYPE_CHECKING:
    from discordgsm.gamedig import GamedigResult


class GameServerControl(Protocol):
    """Read-only aggregate status from GAME-SERVER."""

    name = "gameservercontrol"

    async def query(self):
        host = str(self.kv["host"])
        port = int(str(self.kv["port"]))
        token = os.getenv("GAME_SERVER_CONTROL_TOKEN", "").strip()
        ca_path = os.getenv("GAME_SERVER_CONTROL_CA", "").strip()
        endpoint = os.getenv(
            "GAME_SERVER_CONTROL_URL",
            f"https://{host}:{port}/api/monitor/status",
        ).strip()
        if not token:
            raise RuntimeError("GAME_SERVER_CONTROL_TOKEN is required")
        if not ca_path:
            raise RuntimeError("GAME_SERVER_CONTROL_CA is required")

        ssl_context = ssl.create_default_context(cafile=ca_path)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        start = time.monotonic()
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                endpoint,
                headers={"Authorization": f"Bearer {token}"},
                ssl=ssl_context,
            ) as response:
                if response.status != 200:
                    raise RuntimeError(
                        f"Game Server Control returned HTTP {response.status}"
                    )
                payload = await response.json()

        return self.result_from_payload(
            payload, int((time.monotonic() - start) * 1000)
        )

    @staticmethod
    def result_from_payload(payload: dict, ping: int):
        games = payload.get("games")
        if not isinstance(games, list):
            raise ValueError("Game Server Control payload has no games list")

        safe_games = []
        for game in games:
            if not isinstance(game, dict):
                continue
            safe_games.append(
                {
                    "gameId": str(game.get("gameId", "")),
                    "displayName": str(game.get("displayName", "")),
                    "running": bool(game.get("running", False)),
                    "healthy": bool(game.get("healthy", False)),
                    "reachable": bool(game.get("reachable", False)),
                    "gameState": str(game.get("gameState", "")),
                    "playerCount": int(game.get("playerCount", 0) or 0),
                    "maxPlayers": int(game.get("maxPlayers", 0) or 0),
                    "uptimeSeconds": int(game.get("uptimeSeconds", 0) or 0),
                    "connection": str(game.get("connection", "")),
                }
            )

        players = sum(
            game["playerCount"] for game in safe_games if game["running"]
        )
        max_players = sum(
            game["maxPlayers"]
            for game in safe_games
            if game["running"] and game["maxPlayers"] > 0
        )

        result: "GamedigResult" = {
            "name": os.getenv("GAME_SERVER_CONTROL_BRAND", "Voidroute Game Servers"),
            "map": "",
            "password": False,
            "numplayers": players,
            "numbots": 0,
            "maxplayers": max_players,
            "players": None,
            "bots": None,
            "connect": "",
            "ping": ping,
            "raw": {
                "game_server_control": True,
                "host": str(payload.get("host", "GAME-SERVER")),
                "checkedAt": str(payload.get("checkedAt", "")),
                "games": safe_games,
            },
        }
        return result
