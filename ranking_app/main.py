from pipeline.orchestrator import run_pipeline

if __name__ == "__main__":
    rankings, explanation = run_pipeline(
        "Rank top startup incubators in India"
    )

    print("RANKINGS:")
    print(rankings)
    print("\nEXPLANATION:")
    print(explanation)
