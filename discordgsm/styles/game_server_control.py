import os
from datetime import datetime

from discord import Color, Embed

from discordgsm.styles.style import Style


class GameServerControlStyle(Style):
    """One member-facing card containing every hosted game."""

    @property
    def standalone(self) -> str:
        return True

    @property
    def display_name(self) -> str:
        return "Game Server Control"

    @property
    def description(self) -> str:
        return "Read-only status for every hosted game."

    @staticmethod
    def _uptime(seconds: int) -> str:
        if seconds <= 0:
            return "Just started"
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes = remainder // 60
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes or not parts:
            parts.append(f"{minutes}m")
        return " ".join(parts)

    def embed(self) -> Embed:
        raw = self.server.result.get("raw", {})
        brand = self.server.result.get("name", "Voidroute Game Servers")
        if not self.server.status:
            embed = Embed(
                title=brand,
                description="🔴 **GAME-SERVER is currently unreachable.**",
                color=Color.from_rgb(237, 66, 69),
            )
            self._set_footer(embed, raw)
            return embed

        games = raw.get("games", [])
        online = sum(
            1 for game in games if game.get("running") and game.get("healthy")
        )
        color = (
            Color.from_rgb(35, 165, 90)
            if online == len(games) and games
            else Color.from_rgb(250, 166, 26)
        )
        embed = Embed(
            title=brand,
            description=f"**{online} of {len(games)} hosted games online**",
            color=color,
        )
        sons_of_the_forest_password = os.getenv(
            "SONS_OF_THE_FOREST_JOIN_PASSWORD", ""
        ).strip()
        is_aggregate = len(games) > 1

        for game in games:
            running = bool(game.get("running"))
            healthy = bool(game.get("healthy"))
            indicator = "🟢" if running and healthy else "🟡" if running else "🔴"
            status = "Online" if running and healthy else "Unhealthy" if running else "Offline"
            lines = [f"**Status:** {status}"]
            player_count = int(game.get("playerCount", 0) or 0)
            max_players = int(game.get("maxPlayers", 0) or 0)
            if max_players > 0:
                lines.append(f"**Players:** {player_count}/{max_players}")
            else:
                lines.append(f"**Players:** {player_count}")
            if running:
                lines.append(
                    f"**Uptime:** {self._uptime(int(game.get('uptimeSeconds', 0) or 0))}"
                )
            connection = str(game.get("connection", "")).strip()
            if connection:
                lines.append(f"**Join:** `{connection}`")
            invite_code = str(game.get("inviteCode", "")).strip()
            if invite_code:
                lines.append(f"**Invite code:** `{invite_code}`")
            if (
                is_aggregate
                and str(game.get("gameId", "")).casefold() == "sonsoftheforest"
                and sons_of_the_forest_password
            ):
                lines.append(f"**Password:** ||{sons_of_the_forest_password}||")
            embed.add_field(
                name=f"{indicator} {game.get('displayName', 'Game')}",
                value="\n".join(lines),
                inline=False,
            )

        self._set_footer(embed, raw)
        return embed

    @staticmethod
    def _set_footer(embed: Embed, raw: dict):
        checked_at = str(raw.get("checkedAt", "")).strip()
        suffix = ""
        if checked_at:
            try:
                checked = datetime.fromisoformat(checked_at.replace("Z", "+00:00"))
                suffix = f" • Source updated {checked.astimezone().strftime('%I:%M:%S %p')}"
            except ValueError:
                pass
        embed.set_footer(text=f"GAME-SERVER • Read-only status{suffix}")
