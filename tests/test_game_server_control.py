from discordgsm.protocols.gameservercontrol import GameServerControl
from discordgsm.server import Server
from discordgsm.styles import Styles


def sample_payload():
    return {
        "host": "GAME-SERVER",
        "checkedAt": "2026-07-25T23:00:00Z",
        "games": [
            {
                "gameId": "windrose",
                "displayName": "Windrose",
                "running": True,
                "healthy": True,
                "reachable": True,
                "gameState": "Online",
                "playerCount": 0,
                "maxPlayers": 0,
                "uptimeSeconds": 90061,
                "connection": "",
            },
            {
                "gameId": "satisfactory",
                "displayName": "Satisfactory",
                "running": True,
                "healthy": True,
                "reachable": True,
                "gameState": "Playing",
                "playerCount": 2,
                "maxPlayers": 4,
                "uptimeSeconds": 3661,
                "connection": "satisfactory.voidroute.net:7777",
            },
        ],
    }


def test_control_payload_becomes_safe_aggregate_result(monkeypatch):
    monkeypatch.setenv("GAME_SERVER_CONTROL_BRAND", "Voidroute Game Servers")
    result = GameServerControl.result_from_payload(sample_payload(), 12)

    assert result["name"] == "Voidroute Game Servers"
    assert result["numplayers"] == 2
    assert result["maxplayers"] == 4
    assert result["ping"] == 12
    assert result["raw"]["games"][0]["connection"] == ""


def test_control_style_lists_games_and_public_join_address():
    result = GameServerControl.result_from_payload(sample_payload(), 12)
    server = Server.new(
        guild_id=1,
        channel_id=2,
        game_id="gameservercontrol",
        address="192.168.8.225",
        query_port=8790,
        query_extra={},
        result=result,
    )
    style = Styles.get(server)
    embed = style.embed().to_dict()

    assert style.standalone is True
    assert embed["title"] == "Voidroute Game Servers"
    assert "2 of 2 hosted games online" in embed["description"]
    assert embed["fields"][0]["name"] == "🟢 Windrose"
    assert "satisfactory.voidroute.net:7777" in embed["fields"][1]["value"]
    assert "invite" not in str(embed).lower()


def test_control_style_reports_host_offline():
    result = GameServerControl.result_from_payload(sample_payload(), 12)
    server = Server.new(1, 2, "gameservercontrol", "192.168.8.225", 8790, {}, result)
    server.status = False

    embed = Styles.get(server).embed().to_dict()
    assert "unreachable" in embed["description"]
    assert embed.get("fields") is None
