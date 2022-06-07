# MusicBot for Kaiheila.cn

## Install

```bash
git clone git@github.com:CarterGunale/MusicBot.git
cd MusicBot
git clone git@github.com:Binaryify/NeteaseCloudMusicApi.git
```
Check the installation instruction of [NeteaseCloudMusicApi][https://github.com/Binaryify/NeteaseCloudMusicApi.git]

## Configure

Rename `config.tmp.json` to `config.json`

Open `config.json`

- Set `token` to your bot WebSocket Token.

- Set `channel` to the text channel where you want to send the command.

- Set `voiceid` to the voice channel where you want to place your bot.

- Set `skipper` to a role ID which you want to give them access to skip current music.

- Set `port` to a local port.

- (Optional) Set `n_cookie` to a NeteaseCloudMusic Cookie.

- (Optional) Set `q_cookie` to a QQMusic Cookie.

- (Optional) If you want to use QQMusic plugin, set `q_enable` to `1`.

## Plugins

```bash
git clone git@github.com:jsososo/QQMusicApi.git
```
Check the installation instruction of [QQMusicApi][https://github.com/jsososo/QQMusicApi.git]

Remove `#` which sit on the second line of `run.sh`

## Run

```bash
sh run.sh
```
