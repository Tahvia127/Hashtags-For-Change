import asyncio
import json
import csv
from datetime import datetime
from TikTokApi import TikTokApi

INPUT = "ids_by_tag.json"
OUTPUT = "hydrated_results.csv"

async def fetch_video(api, vid):
    url = f"https://www.tiktok.com/@_/video/{vid}"
    v = api.video(url=url, session_index=0)
    try:
        data = await v.info(session_index=0)
        return data
    except Exception as e:
        print(f"  [ERR] {vid}: {type(e).__name__}: {e}")
        return None

async def main():
    with open(INPUT, "r", encoding="utf-8") as f:
        tag_map = json.load(f)

    rows = []

    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=1,
            headless=False,
            browser="chromium",
            sleep_after=3,
            enable_session_recovery=True
        )

        for hashtag, ids in tag_map.items():
            print(f"\nProcessing {hashtag} ({len(ids)} videos)")

            for vid in ids:  # LIMIT TO 5 FOR TEST RUN
                print(f"  Fetching {vid}...")
                data = await fetch_video(api, vid)
                if not data:
                    print(f"    [FAIL] {vid}")
                    continue

                stats = data.get("stats", {})
                ct = int(data.get("createTime", 0))
                video_date = datetime.utcfromtimestamp(ct).strftime("%Y-%m-%d")

                rows.append([
                    hashtag,
                    video_date,
                    stats.get("diggCount", 0),
                    stats.get("playCount", 0),
                    stats.get("shareCount", 0),
                    stats.get("commentCount", 0),
                ])

                print(f"    [OK] {vid}")

    with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["hashtag", "video_date", "likes", "views", "shares", "comments"])
        w.writerows(rows)

    print(f"\nDone. Wrote {len(rows)} rows to {OUTPUT}")

if __name__ == "__main__":
    asyncio.run(main())
