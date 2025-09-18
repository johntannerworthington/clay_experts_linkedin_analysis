import pandas as pd
import asyncio
import aiohttp
from tqdm import tqdm
import csv

API_KEY = "OPENAI_API_KEY"
API_URL = "https://api.openai.com/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

PROMPT_TEMPLATE = """
I am going to provide some content. This is raw text from a LinkedIn post from an influencer.

Your job is to return:
1. Whether the post is referencing a tool called Clay (Clay.com).
2. Whether the post is critical of Clay in any way (e.g., suggesting better, cheaper, or open source alternatives — not simply being neutral or describing its use).
3. Whether the post is promoting or endorsing **any** sales tool (e.g., but not limited to: Instantly.ai, Apollo, Clay, Lemlist, Icypeas, TryKitt, LeadMagic, Smartlead, etc).

Content: {content}

Answer in this JSON format:
{{"ReferencingClay?": "Yes" or "No", "CriticalOfClay?": "Yes" or "No", "PromotingSalesTool?": "Yes" or "No"}}
"""

SEMAPHORE_LIMIT = 100

async def analyze_row(session, semaphore, row, idx, pbar):
    content = row["content"]

    prompt = PROMPT_TEMPLATE.format(content=content)
    body = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }

    async with semaphore:
        async with session.post(API_URL, headers=HEADERS, json=body) as resp:
            data = await resp.json()
            pbar.update(1)
            try:
                result = data['choices'][0]['message']['content']
                json_like = eval(result)
                return {
                    "ReferencingClay?": json_like.get("ReferencingClay?", "No"),
                    "CriticalOfClay?": json_like.get("CriticalOfClay?", "No"),
                    "PromotingSalesTool?": json_like.get("PromotingSalesTool?", "No")
                }
            except Exception as e:
                return {
                    "ReferencingClay?": "Error",
                    "CriticalOfClay?": "Error",
                    "PromotingSalesTool?": "Error"
                }

async def main():
    df = pd.read_csv("output1.csv")
    semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)
    tasks = []

    async with aiohttp.ClientSession() as session:
        with tqdm(total=len(df), desc="Analyzing posts") as pbar:
            for idx, row in df.iterrows():
                task = analyze_row(session, semaphore, row, idx, pbar)
                tasks.append(task)

            results = await asyncio.gather(*tasks)

    # Add new columns to DataFrame
    df["ReferencingClay?"] = [res["ReferencingClay?"] for res in results]
    df["CriticalOfClay?"] = [res["CriticalOfClay?"] for res in results]
    df["PromotingSalesTool?"] = [res["PromotingSalesTool?"] for res in results]

    df.to_csv("clayanalysis.csv", index=False)
    print("✅ Analysis complete. Output saved to clayanalysis.csv")

if __name__ == "__main__":
    asyncio.run(main())