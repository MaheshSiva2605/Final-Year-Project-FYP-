import json
import numpy as np
import pandas as pd

def analyze_profile(jsonl_file):
    data = []
    
    # 1. Read the JSONL dataset we created in Step 1
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
            
    df = pd.DataFrame(data)
    
    if df.empty:
        print("Error: Dataset is empty.")
        return
    
    print("Analyzing your texting behavioral profile...")
    
    # --- 1. LATENCY & TYPING SPEED ANALYSIS ---
    # Filter out outliers (e.g., replies faster than 1 second or slower than 30 minutes)
    valid_replies = df[(df['delay_seconds'] > 1) & (df['delay_seconds'] < 1800)]
    
    avg_delay = valid_replies['delay_seconds'].mean()
    median_delay = valid_replies['delay_seconds'].median()
    
    # Apparent typing speed (characters per second)
    # Note: This includes reading time + thinking time + physical typing
    valid_replies = valid_replies.copy()
    valid_replies['char_count'] = valid_replies['output'].apply(len)
    valid_replies['chars_per_second'] = valid_replies['char_count'] / valid_replies['delay_seconds']
    
    avg_typing_speed = valid_replies['chars_per_second'].mean()

    # --- 2. STYLOMETRY (TEXT HABITS) ANALYSIS ---
    total_messages = len(df)
    
    # Capitalization: Does the first letter of messages tend to be uppercase?
    capitalized_count = sum(df['output'].apply(lambda x: x[0].isupper() if len(x) > 0 else False))
    cap_ratio = capitalized_count / total_messages
    
    # Punctuation analysis
    exclamation_count = sum(df['output'].apply(lambda x: '!' in x))
    question_count = sum(df['output'].apply(lambda x: '?' in x))
    period_count = sum(df['output'].apply(lambda x: x.endswith('.') if len(x) > 0 else False))
    
    # --- 3. DISPLAY RESULTS ---
    print("\n" + "="*50)
    print("      YOUR BEHAVIORAL STYLOMETRY PROFILE")
    print("="*50)
    print(f"Total Reply Pairs Analyzed: {total_messages}")
    print(f"Average Reply Delay: {avg_delay:.2f} seconds ({avg_delay/60:.2f} minutes)")
    print(f"Median Reply Delay: {median_delay:.2f} seconds")
    print(f"Estimated Apparent Typing Speed: {avg_typing_speed:.2f} characters/second")
    print("-" * 50)
    print(f"Capitalizes First Letter: {cap_ratio * 100:.1f}% of the time")
    print(f"Ends messages with a period (.): { (period_count/total_messages) * 100:.1f}% of the time")
    print(f"Uses Exclamation marks (!): { (exclamation_count/total_messages) * 100:.1f}% of the time")
    print(f"Uses Question marks (?): { (question_count/total_messages) * 100:.1f}% of the time")
    print("="*50)
    
    # 4. Save profile as JSON
    profile = {
        "avg_delay_seconds": float(avg_delay),
        "median_delay_seconds": float(median_delay),
        "chars_per_second": float(avg_typing_speed),
        "capitalization_ratio": float(cap_ratio),
        "period_ratio": float(period_count/total_messages)
    }
    
    with open("behavioral_profile.json", "w") as out:
        json.dump(profile, out, indent=4)
    print("\nSaved behavioral profile to 'behavioral_profile.json'")

# Run the analysis
analyze_profile("whatsapp_dataset.jsonl")