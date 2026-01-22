import pandas as pd
from chatbot.user_chat_entry import chat_with_dataset


df = pd.DataFrame({
    "startup": ["A", "B", "C"],
    "annual_revenue_usd": [10, 20, 5],
    "funding_usd": [100, 200, 80],
    "employees": [10, 20, 8],
    "internal_notes": ["x", "y", "z"],
})

df.to_csv("test_projection.csv", index=False)

response = chat_with_dataset(
    user_query="Which startups perform best?",
    dataset_path="test_projection.csv",
    drop_columns=["internal_notes", "employees"],
)

print(response)
