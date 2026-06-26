import json
import time
import random

def load_behavioral_profile():
    try:
        with open("behavioral_profile.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: Could not find 'behavioral_profile.json'. Run 'analyze_behavior.py' first.")
        return None

def simulate_typing_delay(incoming_message, ai_reply, profile):
    # --- 1. Calculate Reading Time ---
    # Average adult reading speed is roughly 200 words per minute (3.3 words per second)
    words_in_incoming = len(incoming_message.split())
    reading_speed_words_per_sec = 3.3
    reading_time = words_in_incoming / reading_speed_words_per_sec
    
    # --- 2. Calculate Thinking Time (Baseline Latency) ---
    base_thinking_delay = profile["median_delay_seconds"]
    # Keep the thinking delay realistic for active chat (usually between 2 and 10 seconds)
    thinking_time = random.uniform(2.0, min(10.0, max(2.5, base_thinking_delay * 0.1)))
    
    # --- 3. Calculate Physical Typing Speed & Time ---
    # First, load your calculated typing speed from the profile
    typing_speed_cps = profile["chars_per_second"]
    
    # Enforce a realistic smartphone typing speed boundary (between 3.5 and 7.0 chars/sec)
    # This prevents the simulator from typing too slowly due to long away-delays in your chat logs.
    if typing_speed_cps < 3.5 or typing_speed_cps > 7.0:
        typing_speed_cps = random.uniform(4.0, 5.5)
        
    reply_char_length = len(ai_reply)
    typing_time = reply_char_length / typing_speed_cps
    
    # Total delay before message appears
    total_latency = reading_time + thinking_time + typing_time
    
    # --- 4. EXECUTE SIMULATION ---
    print(f"\nIncoming Message: '{incoming_message}'")
    print(f"Reading & Thinking pause... ({reading_time + thinking_time:.2f} seconds)")
    time.sleep(reading_time + thinking_time)
    
    print(f"\n[Mahesh is typing...] (Typing for {typing_time:.2f} seconds at {typing_speed_cps:.1f} chars/sec)")
    # Simulate the visual typing indicator dots
    steps = int(typing_time) if int(typing_time) > 0 else 1
    for _ in range(steps):
        print(".", end="", flush=True)
        time.sleep(typing_time / steps)
    print("\n")
    
    print(f"🚨 Sent Message: '{ai_reply}'")
    print(f"Total simulated latency: {total_latency:.2f} seconds\n")

# --- TEST RUN ---
profile = load_behavioral_profile()

if profile:
    incoming = "Dei yengge update is ready or not?"
    mock_reply = "dei hold on still running some testing on vs code"
    
    simulate_typing_delay(incoming, mock_reply, profile)