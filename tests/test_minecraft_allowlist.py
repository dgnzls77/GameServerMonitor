import pytest

from discordgsm.minecraft_allowlist import (
    MinecraftWhitelistView,
    normalize_gamertag,
    whitelist_embed,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (" Brutalelder ", "Brutalelder"),
        ("Player Two", "Player Two"),
        ("Player_3-Alt", "Player_3-Alt"),
    ],
)
def test_normalize_gamertag_accepts_bedrock_names(value, expected):
    assert normalize_gamertag(value) == expected


@pytest.mark.parametrize("value", ["", "bad!name", "x" * 33, "quoted\"name"])
def test_normalize_gamertag_rejects_unsafe_values(value):
    with pytest.raises(ValueError):
        normalize_gamertag(value)


def test_whitelist_post_has_persistent_submission_button():
    view = MinecraftWhitelistView()
    assert view.timeout is None
    assert view.children[0].custom_id == "dss:minecraft:submit-gamertag"
    assert view.children[0].label == "Submit gamertag"
    embed = whitelist_embed().to_dict()
    assert embed["title"] == "Minecraft Bedrock access"
    assert "games.voidroute.net" in embed["description"]
