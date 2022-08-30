#!/usr/bin/env bash
python3.10 scheduler.py
(cd MiguMusicApi && npm start & cd ../) &
(cd QQMusicApi && npm start & cd ../) &
(cd NeteaseCloudMusicApi && node app.js & cd ../) &
python3.10 core.py 1

