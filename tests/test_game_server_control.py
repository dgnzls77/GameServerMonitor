import json
import logging

from discordgsm.protocols.gameservercontrol import GameServerControl
from discordgsm.server import Server
from discordgsm.styles import Styles

FAKE_JOIN_PASSWORD = "test-sotf-secret-9Qv7"


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
                "inviteCode": "WIND-ROSE",
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
                "connection": "games.voidroute.net:7777",
                "inviteCode": "",
            },
            {
                "gameId": "sonsoftheforest",
                "displayName": "Sons of the Forest",
                "running": True,
                "healthy": True,
                "reachable": True,
                "gameState": "Online",
                "playerCount": 0,
                "maxPlayers": 8,
                "uptimeSeconds": 934,
                "connection": "68.108.85.1:8766",
                "inviteCode": "",
            },
        ],
    }


def render(payload=None, game_filter=None):
    result = GameServerControl.result_from_payload(
        payload or sample_payload(), 12, game_filter=game_filter
    )
    server = Server.new(
        guild_id=1,
        channel_id=2,
        game_id="gameservercontrol",
        address="192.168.8.225",
        query_port=8790,
        query_extra={} if game_filter is None else {"game_filter": game_filter},
        result=result,
    )
    return result, Styles.get(server).embed().to_dict()


def test_control_payload_becomes_safe_aggregate_result(monkeypatch):
    monkeypatch.setenv("GAME_SERVER_CONTROL_BRAND", "Voidroute Game Servers")
    result = GameServerControl.result_from_payload(sample_payload(), 12)

    assert result["name"] == "Voidroute Game Servers"
    assert result["numplayers"] == 2
    assert result["maxplayers"] == 12
    assert len(result["raw"]["games"]) == 3
    assert result["ping"] == 12
    assert result["raw"]["games"][0]["connection"] == ""
    assert result["raw"]["games"][0]["inviteCode"] == "WIND-ROSE"


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
    assert "3 of 3 hosted games online" in embed["description"]
    assert embed["fields"][0]["name"] == "🟢 Windrose"
    assert "**Players:** 0" in embed["fields"][0]["value"]
    assert "**Invite code:** `WIND-ROSE`" in embed["fields"][0]["value"]
    assert "**Players:** 2/4" in embed["fields"][1]["value"]
    assert "games.voidroute.net:7777" in embed["fields"][1]["value"]


def test_join_password_is_absent_when_unset_or_empty(monkeypatch):
    monkeypatch.delenv("SONS_OF_THE_FOREST_JOIN_PASSWORD", raising=False)
    _, unset_embed = render()
    assert all("Password:" not in field["value"] for field in unset_embed["fields"])

    monkeypatch.setenv("SONS_OF_THE_FOREST_JOIN_PASSWORD", "   ")
    _, empty_embed = render()
    assert all("Password:" not in field["value"] for field in empty_embed["fields"])


def test_join_password_is_aggregate_sotf_only_and_secret_isolated(
    monkeypatch, capsys, caplog
):
    monkeypatch.setenv("SONS_OF_THE_FOREST_JOIN_PASSWORD", FAKE_JOIN_PASSWORD)
    caplog.set_level(logging.DEBUG)

    result, embed = render()
    values = {field["name"]: field["value"] for field in embed["fields"]}
    expected = f"**Password:** ||{FAKE_JOIN_PASSWORD}||"

    assert values["🟢 Sons of the Forest"].splitlines().count(expected) == 1
    assert FAKE_JOIN_PASSWORD not in values["🟢 Windrose"]
    assert FAKE_JOIN_PASSWORD not in values["🟢 Satisfactory"]
    assert FAKE_JOIN_PASSWORD not in json.dumps(result, sort_keys=True)

    captured = capsys.readouterr()
    assert FAKE_JOIN_PASSWORD not in captured.out
    assert FAKE_JOIN_PASSWORD not in captured.err
    assert FAKE_JOIN_PASSWORD not in caplog.text


def test_join_password_is_absent_from_filtered_sotf_card(monkeypatch):
    monkeypatch.setenv("SONS_OF_THE_FOREST_JOIN_PASSWORD", FAKE_JOIN_PASSWORD)
    result, embed = render(game_filter="SonsOfTheForest")

    assert len(result["raw"]["games"]) == 1
    assert FAKE_JOIN_PASSWORD not in embed["fields"][0]["value"]
    assert "Password:" not in embed["fields"][0]["value"]


def test_control_filter_selects_sons_of_the_forest_case_insensitively():
    result = GameServerControl.result_from_payload(
        sample_payload(), 12, game_filter="SonsOfTheForest"
    )
    server = Server.new(
        guild_id=1,
        channel_id=2,
        game_id="gameservercontrol",
        address="192.168.8.225",
        query_port=8790,
        query_extra={"game_filter": "sonsoftheforest"},
        result=result,
    )
    embed = Styles.get(server).embed().to_dict()

    assert result["numplayers"] == 0
    assert result["maxplayers"] == 8
    assert len(result["raw"]["games"]) == 1
    assert embed["description"] == "**1 of 1 hosted games online**"
    assert len(embed["fields"]) == 1
    assert embed["fields"][0]["name"] == "\U0001f7e2 Sons of the Forest"
    assert "**Players:** 0/8" in embed["fields"][0]["value"]
    assert "**Uptime:** 15m" in embed["fields"][0]["value"]
    assert "**Join:** `68.108.85.1:8766`" in embed["fields"][0]["value"]


def test_control_filter_rejects_unknown_game_id():
    try:
        GameServerControl.result_from_payload(
            sample_payload(), 12, game_filter="unknown-game"
        )
    except ValueError as error:
        assert "unknown-game" in str(error)
    else:
        raise AssertionError("unknown game filter should fail closed")


def test_control_style_reports_host_offline():
    result = GameServerControl.result_from_payload(sample_payload(), 12)
    server = Server.new(1, 2, "gameservercontrol", "192.168.8.225", 8790, {}, result)
    server.status = False

    embed = Styles.get(server).embed().to_dict()
    assert "unreachable" in embed["description"]
    assert embed.get("fields") is None
