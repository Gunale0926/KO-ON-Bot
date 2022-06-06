# MusicBot for Kaiheila.cn

## Install

```bash
git clone git@github.com:CarterGunale/MusicBot.git
```

## Configure

Rename `config.tmp.json` to `config.json`

Open `config.json`

- Set `token` to your bot WebSocket Token.

- Set `channel` to the text channel where you want to send the command.

- Set `voiceid` to the voice channel where you want to place your bot.

- Set `skipper` to a role ID which you want to give them access to skip current music.

- Set `port` to a local port.

- (Optional) `n_cookie` to a NeteaseCloudMusic Cookie

- (Optional) `q_cookie` to a QQMusic Cookie

## Run

```bash
sh run.sh
```
