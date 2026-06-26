import re
import json
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
# Set to your exact WhatsApp sender name
TARGET_USER = "Mahesh"  

def parse_whatsapp_file(file_path):
    # A robust regex pattern that captures Date, Time, Sender, and Message
    # regardless of AM/PM formatting or narrow unicode spaces.
    pattern = r'^\[?([^,]+),\s*([^\]]+)\]\s*(?:-\s*)?([^:]+):\s*(.*)$'
    parsed_data = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(pattern, line)
            if match:
                date_str, time_str, sender, message = match.groups()
                
                # Clean up weird narrow non-breaking spaces (\u202f) commonly used by iOS/macOS before PM/AM
                time_str = time_str.replace('\u202f', ' ').strip()
                timestamp_str = f"{date_str} {time_str}"
                
                # List of possible date formats to try (handles 12-hour and 24-hour clocks)
                date_formats = [
                    "%d/%m/%Y %I:%M:%S %p",  # 12-hour, 4-digit year (e.g., 01/03/2025 4:32:56 PM)
                    "%d/%m/%y %I:%M:%S %p",  # 12-hour, 2-digit year (e.g., 01/03/25 4:32:56 PM)
                    "%d/%m/%Y %H:%M:%S",     # 24-hour, 4-digit year
                    "%d/%m/%y %H:%M:%S"      # 24-hour, 2-digit year
                ]
                
                timestamp = None
                for fmt in date_formats:
                    try:
                        timestamp = datetime.strptime(timestamp_str, fmt)
                        break  # Success
                    except ValueError:
                        continue
                
                if timestamp is None:
                    continue  # Skip if we can't parse the timestamp
                
                parsed_data.append({
                    "timestamp": timestamp,
                    "sender": sender.strip(),
                    "message": message.strip()
                })
                
    return pd.DataFrame(parsed_data)

def generate_training_pairs(df, target_user):
    training_pairs = []
    for i in range(1, len(df)):
        current_row = df.iloc[i]
        prev_row = df.iloc[i-1]
        
        # Check if the other person spoke first, and the Target User (Mahesh) replied
        if current_row['sender'] == target_user and prev_row['sender'] != target_user:
            time_difference = (current_row['timestamp'] - prev_row['timestamp']).total_seconds()
            
            # Only keep replies that happened within 1 hour (3600 seconds)
            if time_difference < 3600:
                training_pairs.append({
                    "instruction": f"Respond as {target_user}",
                    "input": prev_row['message'],
                    "output": current_row['message'],
                    "delay_seconds": time_difference
                })
    return training_pairs

# --- EXECUTION ---
raw_chat_file = "whatsapp_chat.txt" 

try:
    print("Reading and parsing chat file...")
    df_chat = parse_whatsapp_file(raw_chat_file)
    print(f"Successfully parsed {len(df_chat)} total messages.")
    
    dataset = generate_training_pairs(df_chat, TARGET_USER)
    print(f"Generated {len(dataset)} training pairs.")
    
    # Save the output as a JSONL file
    output_file = "whatsapp_dataset.jsonl"
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in dataset:
            f.write(json.dumps(entry) + '\n')
            
    print(f"Dataset successfully saved to {output_file}!")

except FileNotFoundError:
    print(f"Error: Could not find '{raw_chat_file}' in your folder. Make sure the name matches exactly.")