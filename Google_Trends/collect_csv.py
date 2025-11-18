from pytrends.request import TrendReq
import pandas as pd
import time
from pytrends.request import TrendReq
import pandas as pd
import time
import os
import re

OUTPUT_DIR = r"C:\Users\Kenneth\Desktop\Kenneth\Hashtags-For-Change\Google_Trends"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SEARCH_TERMS = [
    # Country-Specific Hashtags (34)
    "#FreePalestine",
    "#Gaza",
    "#GazaCeasefire",
    "#FreeGaza",
    "#UkraineWar",
    "#StandWithUkraine",
    "#SlavaUkraine",
    "#RussiaUkraineWar",
    "#StopPutin",
    "#SyriaWar",
    "#SaveSyria",
    "#TurkishWomenNeedHelp",
    "#FreeMamoglu",
    "#WeNeedToTalkAboutYemen",
    "#PeaceInYemen",
    "#WhatsHappeningInMyanmar",
    "#MilkTeaAlliance",
    "#POSCO_StopSupportingSAC",
    "#AfghanistanWar",
    "#Taliban",
    "#IraqWar",
    "#StopIraq",
    "#Somaliland",
    "#SomaliaHumanRights",
    "#IndiaPakistan",
    "#SaveIndia",
    "#PakistanArmy",
    "#PakistanZindabad",
    "#StopGunViolence",
    "#BlackLivesMatter",
    "#StandWithMexico",
    "#PeaceForMexico",
    "#SaveBrazil",
    "#RioCrisis",

    # Thematic Hashtags (47)
    "#NeverAgain",
    "#FightForDemocracy",
    "#FreedomOfSpeech",
    "#HumanRights",
    "#FreePress",
    "#YouthForDemocracy",
    "#Protest",
    "#DemoncracyForAll",
    "#NeverForget",
    "#CivilRights",
    "#Justice",
    "#FightForFreedom",
    "#Activism",
    "#FridaysForFuture",
    "#PeopleNotProfit",
    "#MeToo",
    "#StopFundingHate",
    "#WomensMarch",
    "#TimesUp",
    "#GenerationEquality",
    "#MyBodyMyChoice",
    "#ProChoice",
    "#LoveIsLove",
    "#TransRigths",
    "#EqualityForAll",
    "#TransRightsAreHumanRights",
    "#EndSexualViolence",
    "#WomensRights",
    "#LGBTQ+",
    "#GayRights",
    "#ImmigrantRights",
    "#WarCrimes",
    "#PeceNotWar",
    "#AntiWar",
    "#StopWar",
    "#StopTheWar",
    "#HummanatarianCrisis",
    "#RefugeeRelief",
    "#PeaceForAll",
    "#Solidarity",
    "#Ceasefire",
    "#CeasefireNOW",
    "#StopGenocide",
    "#HummanatarianAid",
    "#StandWithPeace",
    "#StandWithhummanity",
    "#EndTheViolence",

    # Regional Hashtags (11)
    "#MiddleEastCrisis",
    "#MENA",
    "#PeaceInMiddleEast",
    "#EuropeanSolidarity",
    "#RejoinEU",
    "#SouthAsiaPeace",
    "#SouthAsiaUnity",
    "#LatinAmericaSolidarity",
    "#LatinAmericaUnited",
    "#NorthAmericaUnited",
    "#FreedomConvoy2022",
]

TIMEFRAME = "2020-01-01 2025-10-18"
GEO = ""

pytrends = TrendReq(hl="en-US", tz=0)


def slugify(term: str) -> str:
    term = term.strip().lower()
    term = term.replace('"', "")
    term = re.sub(r"\s+", "_", term)
    term = re.sub(r"[^a-z0-9_]+", "", term)
    if not term:
        term = "term"
    return term


def fetch_term(term: str, max_retries: int = 5):
    slug = slugify(term)
    out_path = os.path.join(OUTPUT_DIR, f"google_trends_{slug}.csv")

    if os.path.exists(out_path):
        print(f"[SKIP] {term} -> {out_path} (already exists)")
        return

    delay = 10

    for attempt in range(1, max_retries + 1):
        print(f"[RUN ] {term} (attempt {attempt})")

        try:
            pytrends.build_payload(
                kw_list=[term],
                timeframe=TIMEFRAME,
                geo=GEO,
            )
            df = pytrends.interest_over_time()

            if df.empty:
                print(f"[WARN] No data returned for: {term}")
                return

            if "isPartial" in df.columns:
                df = df.drop(columns=["isPartial"])

            df.to_csv(out_path)
            print(f"[OK  ] Saved: {out_path}")

            time.sleep(20)
            return

        except Exception as e:
            print(f"[FAIL] {term}: {type(e).__name__}: {e}")
            if attempt == max_retries:
                print(f"[GIVE] Giving up on {term} after {max_retries} attempts")
                return
            time.sleep(delay)
            delay *= 2


for term in SEARCH_TERMS:
    fetch_term(term)

print("Done.")
