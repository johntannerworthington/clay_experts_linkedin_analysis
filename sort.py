import pandas as pd
import asyncio
import aiohttp
from tqdm import tqdm
from datetime import datetime
import dateparser

INPUT_CSV = "input.csv"
WITHIN_12_MONTHS_CSV = "output1.csv"
OUTSIDE_12_MONTHS_CSV = "output2.csv"
TIME_FRAME_COL = "time frame"
API_KEY = "OPENAI_API_KEY"  # Your API key here

# === GPT PROMPT ===
def build_prompt(time_frame):
    return [
        {
            "role": "user",
            "content": f"""Today's date is {datetime.today().strftime('%B %d, %Y')}.
Is the following time frame within the past 12 months? Reply with only 'yes' or 'no'.

Time frame: {time_frame}
"""
        }
    ]

# === ASYNC GPT CALL ===
async def classify_timeframe(session, semaphore, time_frame):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4",
        "messages": build_prompt(time_frame),
        "temperature": 0
    }

    async with semaphore:
        try:
            async with session.post(url, json=payload, headers=headers, timeout=30) as resp:
                data = await resp.json()
                reply = data["choices"][0]["message"]["content"].strip().lower()
                is_within = "yes" in reply
                return time_frame, is_within, reply
        except Exception as e:
            print(f"⚠️ Error: {e} for time frame: {time_frame}")
            return time_frame, False, "error"

# === DRIVER FUNCTION ===
async def main():
    df = pd.read_csv(INPUT_CSV)
    unique_timeframes = df[TIME_FRAME_COL].dropna().unique()
    print(f"🔍 Loaded {len(df)} rows and {len(unique_timeframes)} unique time frames.\n")

    results = {}
    semaphore = asyncio.Semaphore(400)

    async with aiohttp.ClientSession() as session:
        tasks = [classify_timeframe(session, semaphore, tf) for tf in unique_timeframes]
        for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Classifying"):
            tf, is_within, reply = await f
            results[tf] = is_within
            label = "✅ WITHIN 12M" if is_within else "❌ OUTSIDE 12M"
            print(f"{label}: {tf} → GPT: '{reply}'")

    # Tag rows with classification
    df["is_within_12_months"] = df[TIME_FRAME_COL].map(results)
    within_df = df[df["is_within_12_months"] == True]
    outside_df = df[df["is_within_12_months"] == False]

    # Save results
    within_df.to_csv(WITHIN_12_MONTHS_CSV, index=False)
    outside_df.to_csv(OUTSIDE_12_MONTHS_CSV, index=False)

    print("\n✅ DONE")
    print(f"➡️ {len(within_df)} rows written to {WITHIN_12_MONTHS_CSV}")
    print(f"➡️ {len(outside_df)} rows written to {OUTSIDE_12_MONTHS_CSV}")

# === RUN ===
if __name__ == "__main__":
    asyncio.run(main())
