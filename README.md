# TeraFast

Telegram to TeraBox uploader bot.

Features in this release:

- Resumable batches with duplicate-target protection.
- Disk-safe downloads with stale-file cleanup and minimum free-space reserve.
- Unique temporary download names and pause-on-disk-full behavior.
- Telegram user-session fallback for private channels.
- Parallel Telegram download and TeraBox upload tuning.
- `/parallel` and `/pr` runtime controls for max queue workers 1-4.

Setup:

```text
cp .env.example .env
pip install -r requirements.txt
python bot.py
```

Never commit `.env`, Telegram sessions, the encryption key, SQLite data, downloads, or runtime logs.
