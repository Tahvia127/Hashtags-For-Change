# collect_ids_by_tag.py
import asyncio, os, random, json, time, re
from pathlib import Path
from typing import Dict, List, Set
from playwright.async_api import async_playwright, Page

UA = os.getenv("UA", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")
PROXY = os.getenv("PROXY")  # http://USER:PASS@HOST:PORT
# Per-tag cap. Adjust to control runtime and volume.
TARGET_PER = int(os.getenv("TARGET_PER", "500"))
# Hard stop per tag in seconds to prevent endless scrolling.
TIME_LIMIT_S = int(os.getenv("TIME_LIMIT_S", "1000"))
OUT = Path(os.getenv("OUT", "ids_by_tag.json"))
CTX_DIR = ".plw_tiktok_tags"
SCROLL_PAUSE = 1.6

RAW_TAGS = [
    "#HumanRights", "#RefugeesWelcome", "#MeToo", "#FreedomOfSpeech*",
    "#WomensRights", "#EndViolence", "#EqualityNow", "#StandWithUkraine",
    "#SudanCrisis", "#IranProtests", "#ClimateCrisis", "#FridaysForFuture",
    "#ActOnClimate",
]

def sanitize(tag: str) -> str:
    # Drop leading '#', keep letters and digits only, preserve case used by TikTok tags.
    core = re.sub(r"[^A-Za-z0-9]", "", tag.lstrip("#"))
    if not core:
        raise ValueError(f"Invalid tag after sanitize: {tag}")
    return core

def load_existing(path: Path) -> Dict[str, List[str]]:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
            # Normalize to lists of unique strings.
            norm = {}
            for k, v in obj.items():
                if isinstance(v, list):
                    norm[k] = list(dict.fromkeys(str(x) for x in v))
            return norm
    except Exception:
        return {}

async def accept_consent(page: Page):
    for label in ("Accept", "I agree", "Allow all", "Accept all"):
        try:
            await page.get_by_role("button", name=label, exact=False).click(timeout=1500)
        except Exception:
            pass

async def harvest_dom_ids(page: Page, seen: Set[str]) -> int:
    link_loc = page.locator('a[href*="/video/"]')
    hrefs = await link_loc.evaluate_all("els => els.map(a => a.href).filter(Boolean)")
    added = 0
    for href in hrefs:
        vid = href.split("video/")[-1].split("?")[0].split("/")[0]
        if vid.isdigit() and vid not in seen:
            seen.add(vid)
            added += 1
    return added

async def collect_for_tag(page: Page, tag: str, limit: int, time_limit_s: int) -> List[str]:
    url = f"https://www.tiktok.com/tag/{tag}"
    await page.goto(url, wait_until="domcontentloaded")
    await accept_consent(page)

    # Wait for grid to render or bail out later.
    try:
        await page.wait_for_selector('a[href*="/video/"]', timeout=60_000)
    except Exception:
        pass

    start = time.time()
    seen: Set[str] = set()
    last_growth = time.time()
    stagnation_iters = 60
    body = page.locator("body")
    link_loc = page.locator('a[href*="/video/"]')

    # Also try to pull IDs passing through network URLs.
    def _id_from_url(u: str):
        m = re.search(r"video/(\d+)", u)
        return m.group(1) if m else None

    async def on_response(resp):
        vid = _id_from_url(resp.url)
        if vid and len(seen) < limit:
            seen.add(vid)
    page.on("response", lambda r: asyncio.create_task(on_response(r)))

    # Main loop
    while len(seen) < limit and (time.time() - start) < time_limit_s:
        # Scroll grid to trigger lazy load
        try:
            await link_loc.last.scroll_into_view_if_needed(timeout=2000)
        except Exception:
            pass
        await body.evaluate("el => el.scrollBy(0, el.clientHeight * 0.95)")
        await asyncio.sleep(SCROLL_PAUSE + random.random() * 0.4)

        added = await harvest_dom_ids(page, seen)

        if added == 0:
            stagnation_iters += 1
        else:
            stagnation_iters = 0
            last_growth = time.time()

        # Stop if no growth for a while
        if stagnation_iters >= 25:
            break

        # Detect verify wall; pause until cleared or until time limit
        try:
            if await page.get_by_text("Verify", exact=False).count():
                for _ in range(180):
                    if not await page.get_by_text("Verify", exact=False).count():
                        break
                    await asyncio.sleep(1)
        except Exception:
            pass

        # Safety: if nothing grew for 45s, break
        if time.time() - last_growth > 45:
            break

    return list(seen)[:limit]

async def run():
    tags = [sanitize(t) for t in RAW_TAGS]
    data = load_existing(OUT)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
            proxy={"server": PROXY} if PROXY else None,
        )
        ctx = await browser.new_context(
            user_agent=UA,
            locale="en-US",
            viewport={"width": 1366, "height": 864},
            extra_http_headers={"accept-language": "en-US,en;q=0.9"},
            storage_state=CTX_DIR if Path(CTX_DIR).exists() else None,
        )
        page = await ctx.new_page()

        for tag in tags:
            if tag in data and len(data[tag]) >= TARGET_PER:
                continue
            print(f"Tag {tag}…")
            ids = await collect_for_tag(page, tag, TARGET_PER, TIME_LIMIT_S)
            # Merge and dedupe per tag
            merged = list(dict.fromkeys((data.get(tag) or []) + ids))
            data[tag] = merged
            # Save checkpoint after each tag
            with OUT.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"{tag}: {len(merged)} ids")

        # Persist session for fewer prompts later
        Path(CTX_DIR).write_text(json.dumps(await ctx.storage_state()), encoding="utf-8")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
