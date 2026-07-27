from __future__ import annotations

import json
import os
import re
import ssl
from pathlib import Path

import aiohttp
import discord
from discord import Embed, Interaction
from discord.ui import Modal, TextInput, View

from discordgsm.logger import Logger


GAMERTAG_PATTERN = re.compile(r"^[A-Za-z0-9 _-]{1,32}$")
STATE_PATH = Path("/usr/src/app/data/minecraft-whitelist-message.json")


def normalize_gamertag(value: str) -> str:
    gamertag = value.strip()
    if not GAMERTAG_PATTERN.fullmatch(gamertag):
        raise ValueError(
            "Use the exact Microsoft/Xbox gamertag with letters, numbers, "
            "spaces, underscores, or hyphens."
        )
    return gamertag


def whitelist_embed() -> Embed:
    embed = Embed(
        title="Minecraft Bedrock access",
        description=(
            "This server uses an allowlist. Before joining, submit the exact "
            "Microsoft/Xbox gamertag shown in your Minecraft profile.\n\n"
            "Once it is added, connect to **games.voidroute.net** using "
            "Bedrock's default port **19132**."
        ),
        color=discord.Color.from_rgb(59, 165, 93),
    )
    embed.add_field(
        name="Important",
        value="Gamertags are spelling-sensitive. Discord display names do not work.",
        inline=False,
    )
    return embed


async def submit_gamertag(gamertag: str, discord_user_id: int) -> dict:
    token = os.getenv("GAME_SERVER_CONTROL_ALLOWLIST_TOKEN", "").strip()
    ca_path = os.getenv("GAME_SERVER_CONTROL_CA", "").strip()
    endpoint = os.getenv(
        "GAME_SERVER_CONTROL_ALLOWLIST_URL",
        "https://192.168.8.225:8790/api/integrations/minecraft/allowlist",
    ).strip()
    if not token or not ca_path:
        raise RuntimeError("Minecraft allowlist integration is not configured.")

    ssl_context = ssl.create_default_context(cafile=ca_path)
    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(
            endpoint,
            headers={"Authorization": f"Bearer {token}"},
            json={"gamertag": gamertag, "discordUserId": str(discord_user_id)},
            ssl=ssl_context,
        ) as response:
            try:
                payload = await response.json()
            except (aiohttp.ContentTypeError, json.JSONDecodeError):
                payload = {}
            if response.status != 200:
                message = str(payload.get("error", "")).strip()
                raise RuntimeError(
                    message or f"Whitelist service returned HTTP {response.status}."
                )
            return payload


class MinecraftGamertagModal(Modal):
    def __init__(self):
        super().__init__(title="Minecraft Bedrock allowlist")
        self.gamertag = TextInput(
            label="Microsoft/Xbox gamertag",
            placeholder="Enter the exact gamertag from Minecraft",
            min_length=1,
            max_length=32,
        )
        self.add_item(self.gamertag)

    async def on_submit(self, interaction: Interaction):
        try:
            gamertag = normalize_gamertag(str(self.gamertag))
        except ValueError as error:
            await interaction.response.send_message(str(error), ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            payload = await submit_gamertag(gamertag, interaction.user.id)
            message = str(payload.get("message", "")).strip()
            await interaction.followup.send(
                message
                or f"**{gamertag}** was added to the Minecraft Bedrock allowlist.",
                ephemeral=True,
            )
        except Exception as error:
            Logger.warning(
                f"Minecraft allowlist request failed for Discord user "
                f"{interaction.user.id}: {type(error).__name__}"
            )
            await interaction.followup.send(
                "I could not add that gamertag right now. Please try again shortly "
                "or contact an administrator.",
                ephemeral=True,
            )


class MinecraftWhitelistView(View):
    def __init__(self):
        super().__init__(timeout=None)
        button = discord.ui.Button(
            label="Submit gamertag",
            style=discord.ButtonStyle.success,
            custom_id="dss:minecraft:submit-gamertag",
            emoji="\N{WHITE HEAVY CHECK MARK}",
        )
        button.callback = self.open_modal
        self.add_item(button)

    async def open_modal(self, interaction: Interaction):
        await interaction.response.send_modal(MinecraftGamertagModal())


def register_minecraft_whitelist_view(client: discord.Client) -> None:
    channel_id = os.getenv("MINECRAFT_WHITELIST_CHANNEL_ID", "").strip()
    if not channel_id or getattr(client, "_minecraft_whitelist_view_added", False):
        return
    client.add_view(MinecraftWhitelistView())
    setattr(client, "_minecraft_whitelist_view_added", True)


async def ensure_minecraft_whitelist_post(client: discord.Client) -> None:
    channel_value = os.getenv("MINECRAFT_WHITELIST_CHANNEL_ID", "").strip()
    if not channel_value:
        return
    channel_id = int(channel_value)
    channel = client.get_channel(channel_id)
    if channel is None:
        channel = await client.fetch_channel(channel_id)

    message = None
    if STATE_PATH.exists():
        try:
            message_id = int(json.loads(STATE_PATH.read_text(encoding="utf-8"))["message_id"])
            message = await channel.fetch_message(message_id)
        except (KeyError, ValueError, json.JSONDecodeError, discord.NotFound):
            message = None

    view = MinecraftWhitelistView()
    if message is None:
        message = await channel.send(embed=whitelist_embed(), view=view)
        Logger.info(f"Created Minecraft allowlist post in channel {channel_id}.")
    else:
        await message.edit(embed=whitelist_embed(), view=view)
        Logger.info(f"Refreshed Minecraft allowlist post in channel {channel_id}.")

    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = STATE_PATH.with_suffix(".tmp")
    temporary.write_text(
        json.dumps({"channel_id": channel_id, "message_id": message.id}),
        encoding="utf-8",
    )
    temporary.replace(STATE_PATH)
