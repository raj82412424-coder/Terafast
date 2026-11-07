"""Polls auto-mode targets for new media and uploads it to TeraBox."""
from __future__ import annotations

import asyncio
import logging

from pyrogram import Client

import config
import db
from services.batch_engine import fetch_messages, latest_message_id
from services.pipeline import PipelineError, pick_media, process_message, resolve_client

log = logging.getLogger("auto")

_task: asyncio.Task | None = None
_locks: dict[int, asyncio.Lock] = {}


def start(app: Client) -> None:
    global _task
    if _task is not None and not _task.done():
        return
    _task = asyncio.create_task(_loop(app), name="auto-engine")
    log.info("Auto engine started (poll every %ss)", config.AUTO_POLL_SECONDS)


async def stop() -> None:
    global _task
    if _task is None:
        return
    _task.cancel()
    await asyncio.gather(_task, return_exceptions=True)
    _task = None


async def _loop(app: Client) -> None:
    while True:
        try:
            await poll_once(app)
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001 - the poller must survive one bad target
            log.exception("Auto poll failed")
        await asyncio.sleep(config.AUTO_POLL_SECONDS)


async def poll_once(app: Client) -> None:
    for target in db.list_auto_targets():
        try:
            await _process_target(app, target)
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001
            log.exception("Auto target %s failed", target["id"])


async def _process_target(app: Client, target: dict) -> None:
    lock = _locks.setdefault(int(target["id"]), asyncio.Lock())
    if lock.locked():
        return

    async with lock:
        user_id = int(target["user_id"])
        chat_id = int(target["chat_id"])
        client = await resolve_client(app, user_id, chat_id)
        latest = await latest_message_id(client, chat_id)

        last = int(target["last_seen_id"] or 0)
        if last <= 0:
            last = int(target["start_message_id"]) - 1
        if latest <= last:
            return

        cursor = last
        while cursor < latest:
            chunk_end = min(cursor + config.BATCH_CHUNK_SIZE, latest)
            messages = await fetch_messages(
                client, chat_id, list(range(cursor + 1, chunk_end + 1))
            )
            for message in messages:
                cursor = int(message.id)
                if getattr(message, "empty", False) or pick_media(message) is None:
                    continue
                try:
                    result = await process_message(
                        app, user_id, chat_id, message.id, target=target
                    )
                except PipelineError as exc:
                    db.bump_target(target["id"], failed=1)
                    log.warning(
                        "Auto upload failed for %s/%s: %s", chat_id, message.id, exc
                    )
                    continue
                except Exception:  # noqa: BLE001
                    db.bump_target(target["id"], failed=1)
                    log.exception("Auto upload crashed for %s/%s", chat_id, message.id)
                    continue

                if result.status == "uploaded":
                    await _notify(app, target, result)
            if cursor < chunk_end:
                cursor = chunk_end
            db.set_last_seen(target["id"], cursor)


async def _notify(app: Client, target: dict, result) -> None:
    text = (
        "🤖 **Auto upload complete**\n\n"
        f"📢 {target['title']}\n"
        f"📁 `{result.name}`\n"
        f"🔗 {result.link}\n"
        f"↳ source: {result.source_link}"
    )
    try:
        await app.send_message(int(target["user_id"]), text)
    except Exception as exc:  # noqa: BLE001
        log.warning("Auto notification failed: %r", exc)
