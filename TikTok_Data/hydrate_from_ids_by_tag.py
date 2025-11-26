import asyncio
import json
import csv
from datetime import datetime
from TikTokApi import TikTokApi

INPUT = "ids_by_tag_2.json"
OUTPUT = "hydrated_results_1.csv"

async def fetch_video(api, vid):
    url = f"https://www.tiktok.com/@_/video/{vid}"
    try:
        v = api.video(url=url, session_index=0)
        data = await v.info(session_index=0)
        return data
    except Exception as e:
        print(f"  [ERR] {vid}: {type(e).__name__}: {e}")
        return None

async def main():
    with open(INPUT, "r", encoding="utf-8") as f:
        tag_map = json.load(f)

    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=1,
            headless=False,
            browser="chromium",
            sleep_after=3,
            enable_session_recovery=True,
        )

        # open once, write incrementally
        with open(OUTPUT, "a", encoding="utf-8", newline="") as f:
            w = csv.writer(f)

            # if file is empty, write header
            if f.tell() == 0:
                w.writerow(["hashtag", "video_date", "likes", "views", "shares", "comments"])

            for hashtag, ids in tag_map.items():
                print(f"\nProcessing {hashtag} ({len(ids)} videos)")

                for vid in ids:
                    print(f"  Fetching {vid}...")
                    data = await fetch_video(api, vid)
                    if not data:
                        print(f"    [FAIL] {vid}")
                        continue

                    stats = data.get("stats", {})
                    ct = int(data.get("createTime", 0))
                    video_date = datetime.utcfromtimestamp(ct).strftime("%Y-%m-%d")

                    row = [
                        hashtag,
                        video_date,
                        stats.get("diggCount", 0),
                        stats.get("playCount", 0),
                        stats.get("shareCount", 0),
                        stats.get("commentCount", 0),
                    ]
                    w.writerow(row)
                    f.flush()
                    print(f"    [OK] {vid}")

    print("\nDone.")

if __name__ == "__main__":
    asyncio.run(main())
