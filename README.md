# Discord Game Server Monitor

## Voidroute GAME-SERVER integration

This fork adds a read-only `gameservercontrol` source for David's Windows
`GAME-SERVER`. It produces one automatically refreshed Discord card containing
every game registered in Game Server Control, including games such as Windrose
that do not provide a standard public query protocol.

The integration:

- reads only `https://192.168.8.225:8790/api/monitor/status`;
- authenticates with a dedicated monitor token, not the dashboard administrator
  password;
- validates GAME-SERVER's private certificate;
- exposes Windrose's current invite code to the configured member-facing
  Discord status channel, but never exposes configuration, logs, credentials,
  or control actions;
- shows each direct-connect game's public connection address when available;
- shows player counts even when a game has an unlimited or unspecified
  maximum; and
- keeps the bot independent on `brutalapps`, allowing it to report when
  GAME-SERVER is unreachable.

The provided Compose deployment uses SQLite, publishes no ports, runs without
Linux capabilities, and persists state under `./data`.

## Minecraft Bedrock self-service allowlist

The Voidroute deployment can maintain one persistent access post in the
configured Minecraft Discord channel. Members select **Submit gamertag**, enter
the exact Microsoft/Xbox gamertag from Minecraft, and receive a private result.

This workflow uses a second, narrowly scoped credential and the dedicated
`/api/integrations/minecraft/allowlist` endpoint. It cannot read configuration,
control a game, restart a service, or use the dashboard administrator session.
GAME-SERVER validates the gamertag again, rate-limits submissions, and records
the Discord user ID and submitted gamertag in its local whitelist audit log.

Set `MINECRAFT_WHITELIST_CHANNEL_ID`,
`GAME_SERVER_CONTROL_ALLOWLIST_URL`, and
`GAME_SERVER_CONTROL_ALLOWLIST_TOKEN` in the private deployment environment.
The message ID is retained under the existing writable `./data` volume so bot
restarts update the original post instead of creating duplicates.

Required `.env` values are documented in `.env.example`. Keep the real `.env`
and monitor certificate under `/opt/discordgsm`; neither belongs in Git.

After inviting the bot and choosing the Discord status channel, an administrator
adds the aggregate card with:

```text
/addserver gameservercontrol
Host: 192.168.8.225
Query port: 8790
```

No `voidroute.net` DNS record is required for the bot itself.
[![Python Package](https://github.com/DiscordGSM/GameServerMonitor/actions/workflows/python-package.yml/badge.svg)](https://github.com/DiscordGSM/GameServerMonitor/actions/workflows/python-package.yml)
[![Docker Image](https://github.com/DiscordGSM/GameServerMonitor/actions/workflows/docker-image.yml/badge.svg)](https://github.com/DiscordGSM/GameServerMonitor/actions/workflows/docker-image.yml)
[![Discord Shield](https://discordapp.com/api/guilds/680159496584429582/widget.png?style=shield)](https://discordgsm.com/discord)
[![Docker Pulls](https://img.shields.io/docker/pulls/discordgsm/discord-game-server-monitor.svg)](https://hub.docker.com/r/discordgsm/discord-game-server-monitor)
[![GitHub release](https://img.shields.io/github/release/DiscordGSM/GameServerMonitor)](https://github.com/DiscordGSM/GameServerMonitor/releases/)
[![GitHub license](https://img.shields.io/github/license/DiscordGSM/GameServerMonitor)](https://github.com/DiscordGSM/GameServerMonitor/blob/main/LICENSE)

📺 A discord bot that monitors your game server and tracks the live data of your game servers.

![DiscordGSM Thumbnail](https://discordgsm.com/thumbnail.jpg)

🚨 Get alerted when your server is down! Learn more: https://discordgsm.com

![DiscordGSM Alert](https://discordgsm.com/game-server-monitor-alert.jpg?v=2)

## Installation
We provide a public discord bot service which allows to monitor 10 servers per discord guild.

[![DiscordGSM Thumbnail](https://discordgsm.com/add-to-server.png)](https://discordgsm.com/invite)

For self hosting, please check https://discordgsm.com/guide#installation.

## Commands
Learn more: https://discordgsm.com/guide/commands

![DiscordGSM Commands](https://discordgsm.com/game-server-monitor-commands.jpg)

## Supported Games
Learn more: https://discordgsm.com/guide/supported-games

![Supported Games](https://discordgsm.com/images/guide/supported-games/thumbnail.jpg)

## Languages
Feel free to contribute! Learn more: [Contributor's Guide: Adding Translations](https://github.com/DiscordGSM/GameServerMonitor/issues/1)

<details>
<summary>All translations</summary>
  
| Language Name | Native Name | Supported | Locale File | Contributors |
| ------------- | ----------- | --------- | ----------- | ------------ |
| <img src="https://discordgsm.com/images/flags/da.png" width=20 /> Danish | Dansk | ✔️ | [da.json](/discordgsm/translations/da.json) | [@XiqZo](https://github.com/XiqZo) |
| <img src="https://discordgsm.com/images/flags/de.png" width=20 /> German | Deutsch | ✔️ | [de.json](/discordgsm/translations/de.json) | [@rohere58](https://github.com/rohere58) |
| <img src="https://discordgsm.com/images/flags/en-GB.png" width=20 /> English, UK | English, UK | ✔️ | [en-GB.json](/discordgsm/translations/en-GB.json) | [@BattlefieldDuck](https://github.com/BattlefieldDuck) |
| <img src="https://discordgsm.com/images/flags/en-US.png" width=20 /> English, US | English, US | ✔️ | [en-US.json](/discordgsm/translations/en-US.json) | [@BattlefieldDuck](https://github.com/BattlefieldDuck) |
| <img src="https://discordgsm.com/images/flags/es-ES.png" width=20 /> Spanish | Español | ✔️ | [es-ES.json](/discordgsm/translations/es-ES.json) | [@Akagioni](https://github.com/Akagioni) |
| <img src="https://discordgsm.com/images/flags/fr.png" width=20 /> French | Français | ✔️ | [fr.json](/discordgsm/translations/fr.json) | [@Sami6053](https://github.com/Sami6053) |
| <img src="https://discordgsm.com/images/flags/hr.png" width=20 /> Croatian | Hrvatski | ❌ | [hr.json](/discordgsm/translations/hr.json) |  |
| <img src="https://discordgsm.com/images/flags/it.png" width=20 /> Italian | Italiano | ✔️ | [it.json](/discordgsm/translations/it.json) | [@ricardoguimaraes2021](https://github.com/ricardoguimaraes2021) |
| <img src="https://discordgsm.com/images/flags/lt.png" width=20 /> Lithuanian | Lietuviškai | ✔️ | [lt.json](/discordgsm/translations/lt.json) | [@Kodashas](https://github.com/Kodashas) |
| <img src="https://discordgsm.com/images/flags/hu.png" width=20 /> Hungarian | Magyar | ✔️ | [hu.json](/discordgsm/translations/hu.json) | [@w4sb0y](https://github.com/w4sb0y)  |
| <img src="https://discordgsm.com/images/flags/nl.png" width=20 /> Dutch | Nederlands | ✔️ | [nl.json](/discordgsm/translations/nl.json) | [@CounterForce](https://github.com/CounterForce) |
| <img src="https://discordgsm.com/images/flags/no.png" width=20 /> Norwegian | Norsk | ❌ | [no.json](/discordgsm/translations/no.json) |  |
| <img src="https://discordgsm.com/images/flags/pl.png" width=20 /> Polish | Polski | ✔️ | [pl.json](/discordgsm/translations/pl.json) | [@StarterX4](https://github.com/StarterX4) |
| <img src="https://discordgsm.com/images/flags/pt-BR.png" width=20 /> Portuguese, Brazilian | Português do Brasil | ✔️ | [pt-BR.json](/discordgsm/translations/pt-BR.json) | [@ricardoguimaraes2021](https://github.com/ricardoguimaraes2021) |
| <img src="https://discordgsm.com/images/flags/ro.png" width=20 /> Romanian, Romania	| Română | ❌ | [ro.json](/discordgsm/translations/ro.json) |  |
| <img src="https://discordgsm.com/images/flags/fi.png" width=20 /> Finnish | Suomi | ✔️ | [fi.json](/discordgsm/translations/fi.json) | [@sestain](https://github.com/sestain) |
| <img src="https://discordgsm.com/images/flags/sv-SE.png" width=20 /> Swedish | Svenska | ❌ | [sv-SE.json](/discordgsm/translations/sv-SE.json) |  |
| <img src="https://discordgsm.com/images/flags/vi.png" width=20 /> Vietnamese | Tiếng Việt | ✔️ | [vi.json](/discordgsm/translations/vi.json) |  [@hoangvu12](https://github.com/hoangvu12) |
| <img src="https://discordgsm.com/images/flags/tr.png" width=20 /> Turkish | Türkçe | ✔️ | [tr.json](/discordgsm/translations/tr.json) |  [@RedBuls81](https://github.com/RedBuls81) |
| <img src="https://discordgsm.com/images/flags/cs.png" width=20 /> Czech | Čeština | ❌ | [cs.json](/discordgsm/translations/cs.json) |  |
| <img src="https://discordgsm.com/images/flags/el.png" width=20 /> Greek | Ελληνικά | ❌ | [el.json](/discordgsm/translations/el.json) |  |
| <img src="https://discordgsm.com/images/flags/bg.png" width=20 /> Bulgarian | български | ❌ | [bg.json](/discordgsm/translations/bg.json) |  |
| <img src="https://discordgsm.com/images/flags/ru.png" width=20 /> Russian | Pусский | ✔️ | [ru.json](/discordgsm/translations/ru.json) | [@K-Faktor](https://github.com/K-Faktor), [@Satton2](https://github.com/Satton2) |
| <img src="https://discordgsm.com/images/flags/uk.png" width=20 /> Ukrainian | Українська | ✔️ | [uk.json](/discordgsm/translations/uk.json) | [@only1avetrill](https://github.com/only1avetrill) |
| <img src="https://discordgsm.com/images/flags/hi.png" width=20 /> Hindi, India | हिन्दी, भारत | ✔️ | [hi.json](/discordgsm/translations/hi.json) | [@shankypedia](https://github.com/shankypedia) |
| Malayalam | മലയാളം | ✔️ | [ml.json](/discordgsm/translations/ml.json) | [@DarkwixZz](https://github.com/DarkwixZz) |
| <img src="https://discordgsm.com/images/flags/th.png" width=20 /> Thai | ไทย | ❌ | [th.json](/discordgsm/translations/th.json) |  |
| <img src="https://discordgsm.com/images/flags/zh-CN.png" width=20 /> Chinese, China | 中文 | ✔️ | [zh-CN.json](/discordgsm/translations/zh-CN.json) | [@BattlefieldDuck](https://github.com/BattlefieldDuck) |
| <img src="https://discordgsm.com/images/flags/ja.png" width=20 /> Japanese | 日本語 | ✔️ | [ja.json](/discordgsm/translations/ja.json) | [@koimoee](https://github.com/koimoee) |
| <img src="https://discordgsm.com/images/flags/zh-TW.png" width=20 /> Chinese, Taiwan | 繁體中文 | ✔️ | [zh-TW.json](/discordgsm/translations/zh-TW.json) | [@BattlefieldDuck](https://github.com/BattlefieldDuck) |
| <img src="https://discordgsm.com/images/flags/ko.png" width=20 /> Korean | 한국어 | ✔️ | [ko.json](/discordgsm/translations/ko.json) | [@koimoee](https://github.com/koimoee), [@angrystar170](https://github.com/angrystar170) |
</details>

## Contributing
Contributions are welcome! Please feel free to submit pull requests or open issues.

![https://github.com/DiscordGSM/GameServerMonitor/graphs/contributors](https://contrib.rocks/image?repo=DiscordGSM/GameServerMonitor)

## Support Server
Got any questions or feedback? Join our Discord Server: https://discordgsm.com/discord

## Stargazers over time
[![Stargazers over time](https://starchart.cc/DiscordGSM/GameServerMonitor.svg?variant=adaptive)](https://starchart.cc/DiscordGSM/GameServerMonitor)
