import pretty_midi
import time
import keyboard
import re
import threading

#midi upload
midi = pretty_midi.PrettyMIDI(r'C:\Users\pc\Desktop\piano\[YOUR .MID FILE HERE]')
midi_notes = []


for inst in midi.instruments:
    if not inst.is_drum:
        for n in inst.notes:
            midi_notes.append({
                "start": n.start,
                "end": n.end,
                "pitch": n.pitch,
                "used": False
            })

midi_notes.sort(key=lambda x: x["start"])

#read notes
with open(r'C:\Users\pc\Desktop\piano\[YOUR .TXT FILE HERE]]', "r", encoding="utf-8") as f:
    text = f.read().replace('i', 'ı')

tokens = re.findall(r'\[[^\[\]]+\]|\S', text)


#find pattern

def match_pattern(tokens, pattern):
    pattern_str = [t.lower() for t in pattern]
    for i in range(len(tokens) - len(pattern_str) + 1):
        if [tokens[j].lower() for j in range(i, i + len(pattern_str))] == pattern_str:
            return i
    return -1

event_timings = []
last_event_time = 0.0

for token in tokens:
    letters = list(token[1:-1]) if token.startswith('[') else [token]
    used_notes = []

    for letter in letters:
        for note in midi_notes:
            if not note["used"]:
                note["used"] = True
                used_notes.append((letter, note["start"], note["end"]))
                break
        else:
            raise RuntimeError(f"'{letter}' için nota yok nigga")
        
    event_start = min(n[1] for n in used_notes)
    delay = event_start - last_event_time
    last_event_time = event_start

    event_timings.append({
        "keys": [n[0] for n in used_notes],
        "delay": delay,
        "event_start": event_start
    })

#timing
for i in range(len(event_timings)):
    if i < len(event_timings) - 1:
        delay_to_next = event_timings[i + 1]["event_start"] - event_timings[i]["event_start"]
        duration = max(0.05, min(delay_to_next, 1.0))
    else:
        duration = 0.3
    event_timings[i]["duration"] = duration
    del event_timings[i]["event_start"]

#play

print("Starting in 5 seconds... (Press escape to stop)")
time.sleep(5)

for i, event in enumerate(event_timings):
    if keyboard.is_pressed("esc"):
        print("Stopped")
        exit()

    time.sleep(event["delay"])

    
    for key in event["keys"]:
        keyboard.press(key)
        threading.Timer(event["duration"], keyboard.release, args=(key,)).start()

print("Fin.")
