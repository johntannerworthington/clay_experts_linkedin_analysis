import pandas as pd

# Load the CSV file
df = pd.read_csv("clayanalysis.csv")

# Combine first and last names into Full Name (safe for NaNs)
df["Full Name"] = df["name 1"].fillna("").str.strip() + " " + df["name 2"].fillna("").str.strip()

# Normalize values for consistency
df["ReferencingClay?"] = df["ReferencingClay?"].astype(str).str.strip().str.lower()
df["CriticalOfClay?"] = df["CriticalOfClay?"].astype(str).str.strip().str.lower()
df["PromotingSalesTool?"] = df["PromotingSalesTool?"].astype(str).str.strip().str.lower()

# Group and aggregate
summary = df.groupby("Full Name").agg(
    TotalPosts=("content", "count"),
    MentionsClay=("ReferencingClay?", lambda x: (x == "yes").sum()),
    CriticalOfClay=("CriticalOfClay?", lambda x: (x == "yes").sum()),
    PromotesSalesTool=("PromotingSalesTool?", lambda x: (x == "yes").sum())
).reset_index()

# Save output
summary.to_csv("clay_summary.csv", index=False)
print("✅ clay_summary.csv generated successfully.")
