"""Telegram message link parsing and building."""
from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

_HOSTS = {
    "t.me",
    "www.t.me",
    "telegram.me",
    "www.telegram.me",
    "telegram.dog",
    "www.telegram.dog",
}
_LINK_RE = re.compile(
    r"(?:https?://)?(?:www\.)?(?:t\.me|telegram\.me|telegram\.dog)/[^\s<>\"']+",
    re.I,
)
_SCHEME_RE = re.compile(r"tg://resolve\?[^\s<>\"']+", re.I)
_TRAILING = ").,;:!?]}\"'"


@dataclass(frozen=True)
class TelegramLink:
    raw: str
    chat: str | int
    message_id: int
    username: str | None = None
    is_private: bool = False


def _clean(raw: str) -> str:
    return raw.strip().rstrip(_TRAILING)


def parse_telegram_link(text: str) -> TelegramLink | None:
    """Parse a public, private or tg:// message link. Returns None otherwise."""
    if not text:
        return None

    scheme = _SCHEME_RE.search(text)
    if scheme:
        raw = _clean(scheme.group(0))
        query = parse_qs(urlparse(raw).query)
        domain = (query.get("domain") or [""])[0]
        post = (query.get("post") or [""])[0]
        if domain and post.isdigit():
            return TelegramLink(raw, domain, int(post), domain, False)
        return None

    match = _LINK_RE.search(text)
    if not match:
        return None

    raw = _clean(match.group(0))
    if not raw.lower().startswith("http"):
        raw = "https://" + raw

    parsed = urlparse(raw)
    if parsed.netloc.lower() not in _HOSTS:
        return None
    parts = [part for part in parsed.path.split("/") if part]

Yˆ›İ\Î‚ˆ™]\›ˆ›Û™BˆYˆ\ÖÌHOHœÈ‚ˆ\ÈH\ÖÌWBˆYˆ›İ\Î‚ˆ™]\›ˆ›Û™BˆYˆ\ÖÌHOH˜È‚ˆYˆ[Š\ÊHÈÜˆ›İ\ÖÌWKš\ÙYÚ]

HÜˆ›İ\ÖÌ—Kš\ÙYÚ]

N‚ˆ™]\›ˆ›Û™Bˆ™]\›ˆ[YÜ˜[S[šÊ˜]Ë[
ˆ‹LLÜ\ÖÌW_HŠK[
\ÖÌ—JK›Û™KYJB‚ˆYˆ\ÖÌKœİ\İÚ]
ŠÈŠHÜˆ\ÖÌH[ˆÂˆš›Ú[˜Ú]‹ˆ˜YİXÚÙ\œÈ‹ˆœÚ\™H‹ˆœ›ŞH‹ˆœÛØÚÜÈ‹ˆN‚ˆ™]\›ˆ›Û™B‚ˆYˆ[Š\ÊHˆÜˆ›İ\ÖÌWKš\ÙYÚ]

N‚ˆ™]\›ˆ›Û™Bˆ\Ù\›˜[YHH\ÖÌBˆ™]\›ˆ[YÜ˜[S[šÊ˜]Ë\Ù\›˜[YK[
\ÖÌWJK\Ù\›˜[YK˜[ÙJB‚‚™YˆY\ÜØYÙWÛ[šÊÚ]ÚYˆ[Y\ÜØYÙWÚYˆ[\Ù\›˜[YNˆİˆ›Û™HH›Û™JHOˆİ‚ˆˆˆZ[HØ[›ÛšXØ[›YH[šÈ›ÜˆHİÜ™YY\ÜØYÙKˆˆˆ‚ˆYˆ\Ù\›˜[YN‚ˆ™]\›ˆˆšÎ‹Ëİ›YKŞİ\Ù\›˜[Y_KŞÛY\ÜØYÙWÚYH‚ˆ˜[YHH[
Ú]ÚY
BˆYˆ˜[YH‚ˆ[\›˜[HXœÊ˜[YJHHWÌÌÌÌˆYˆ[\›˜[ˆ‚ˆ™]\›ˆˆšÎ‹Ëİ›YKØËŞÚ[\›˜[KŞÛY\ÜØYÙWÚYH‚ˆ™]\›ˆˆšÎ‹Ëİ›YKØËŞØXœÊ˜[YJ_KŞÛY\ÜØYÙWÚYH‚