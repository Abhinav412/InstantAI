import pandas as pd
from chatbot.user_chat_entry import chat_with_dataset

df = pd.DataFrame({
    "startup_name": ["AlphaAI", "BetaTech", "GammaLabs"],
    "annual_revenue_usd": [1_200_000, 2_500_000, 800_000],
    "funding_usd": [5_000_000, 12_000_000, 3_000_000],
    "employees": [25, 60, 15],
})

df.to_csv("startups_clean.csv", index=False)

response = chat_with_dataset(
    user_query="Which startups are performing best?",
    dataset_path="startups_clean.csv",
)

print(response)
