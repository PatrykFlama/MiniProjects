import requests
import re
from datetime import datetime, timedelta
import json
import sys

DEBUG = False
dprint = print if DEBUG else lambda *args, **kwargs: None

# OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_URL = "http://192.168.10.15:11434/api/generate"
MODEL = "llama3.2:3b"
# MODEL = "mwiewior/bielik"

INPUT_FILE = "wa_chat.txt"
N_BLOCKS = 25
MIN_GAP = 30
SUMM_STYLE = "oneblock_chain"
SEPARATE_BLOCKS = False

prompt_base = "Podsumuj szczegółowo i długo następującą rozmowę, podaj TYLKO podsumowanie"
summarize_all_prompt = "Podam wszystkie poprzednie podsumowania, zredaguj je odpowienio i szczegółowo. (tutaj możesz wypisać dużo informacji):\n"

# prompt_base = "Jest to fragment konwersacji z grupy na wyjazd, wyciągnij z niego szczegółowy plan podróży (tylko dla tego fragmentu, tak aby nie było w nim nic zbędnego)"
# summarize_all_prompt = "Podam wszystkie poprzednie podsumowania, wyciągnij z nich szczegółowy plan podróży. (tutaj możesz wypisać dużo informacji)"

def parse_timestamp(line):
    """Extracts and parses the timestamp from a chat message."""
    match = re.match(r"(\d{1,2})/(\d{1,2})/(\d{2}), (\d{2}):(\d{2}) - ", line)
    if match:
        month, day, year, hour, minute = match.groups()
        year = f"20{year}"
        date_str = f"{year}-{month}-{day} {hour}:{minute}"
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    return None


def split_chat(filename, n_blocks, min_gap):
    """Splits the chat into N blocks, ensuring a minimum time gap between them."""
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    messages = []

    for line in lines:
        timestamp = parse_timestamp(line)
        if timestamp:
            messages.append((timestamp, line.strip()))

    total_msgs = len(messages)
    if total_msgs == 0:
        return []

    interval = total_msgs // n_blocks
    blocks = []
    block = []
    last_split_time = messages[0][0]
    lines_in_block = 0

    for i, (timestamp, message) in enumerate(messages):
        if lines_in_block >= interval and (timestamp - last_split_time).total_seconds() / 60 >= min_gap:
            blocks.append("\n".join(block))
            block = []
            lines_in_block = 0

        lines_in_block += 1
        last_split_time = timestamp
        block.append(message)

    if block:
        blocks.append("\n".join(block))

    print("============SPLIT CHAT=============")
    print("Total messages:", total_msgs)
    print("Total blocks:", len(blocks))
    print("Target messages per block:", total_msgs / len(blocks))
    print("Real avg msg per block", sum(len(b.split("\n")) for b in blocks) / len(blocks))

    return blocks

def query_ollama(text, prev_summary=None, summary_style="simple_chain"):
    """Sends a request to the local Ollama server for summarization."""

    prompt = ""
    if summary_style == "oneblock_chain":
        prompt = prompt_base + "" + \
        (", uwzględnij poprzednią odpowiedź w tej odpowiedzi (dodaj ją do tej odpowiedzi)" if prev_summary and SEPARATE_BLOCKS else "") + ":\n\n"
    elif summary_style == "simple_chain" or summary_style:
        prompt = prompt_base + ":\n\n"
    elif summary_style == "summarize_all":
        prompt = summarize_all_prompt + ":\n\n"

    prompt += "\n===========================\n"

    if prev_summary:
        if SEPARATE_BLOCKS:
            prompt = f"{prompt}\n===== Odpowiedź do poprzedniego fragmentu: =====\n{prev_summary}\n\n===== Nowy fragment: ====\n{text}"
        else:
            prompt = f"{prompt}\n{prev_summary}\n\n{text}\n"
    else:
        prompt = f"{prompt}\n{text}\n"

    prompt += "\n######\n"

    dprint("----------------Prompt:----------------")
    dprint(prompt)

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL, 
        "prompt": prompt, 
        "options": {
            "reset": True,
            "temperature": 0.2,  # reduce randomness
            "stop": ["######"],  # helps prevent it from hallucinating extra content
        }, 
        "stream": True
    })

    summary = ""
    for line in response.iter_lines():
        if line:
            try:
                json_data = line.decode("utf-8")
                parsed = json.loads(json_data)
                summary += parsed.get("response", "")
            except json.JSONDecodeError:
                continue


    print("----------------Response:----------------")
    print(summary)

    return summary.strip()


def process_chat(chat_file, n_blocks, min_gap, output_file="summary.txt", summary_style="simple_chain"):
    """Processes the chat, summarizes it, and saves the final result."""
    blocks = split_chat(chat_file, n_blocks, min_gap)
    latest_summary = None
    summaries = []

    if summary_style == "double_layer":
        for block in blocks:
            latest_summary = query_ollama(block, summary_style="simple_chain")
            summaries.append(latest_summary)
        
        latest_summary = query_ollama("\n\n".join(summaries), summary_style="summarize_all")
        summaries.append(latest_summary)
    elif summary_style == "summarize_all":
        latest_summary = query_ollama("\n\n".join(blocks), summary_style="summarize_all")
        summaries.append(latest_summary)
    elif summary_style == "isolated_chain":
        for block in blocks:
            latest_summary = query_ollama(block, summary_style="simple_chain")
            summaries.append(latest_summary)
    elif summary_style == "isolated_double_layer":
        for block in blocks:
            latest_summary = query_ollama(block, summary_style="simple_chain")
            summaries.append(latest_summary)
        
        latest_summary = query_ollama("\n\n".join(summaries), summary_style="summarize_all")
        summaries.append(latest_summary)
    else:
        for block in blocks:
            latest_summary = query_ollama(block, prev_summary=latest_summary, summary_style=summary_style)
            summaries.append(latest_summary)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n\n---------BLOCK SUMMARY---------\n".join(summaries))

    with open(output_file, "a", encoding="utf-8") as f:
        f.write("\n=========FINAL SUMMARY=========\n")
        f.write(latest_summary)

    print("=======Final Summary:======\n", latest_summary)



if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["q", "-q"]:
        print("Enter your question:")
        question = input()

        question = "W kontekście podanych informacji odpowiedz na pytanie:\n" + question + "\n"

        temp = prompt_base
        prompt_base = question
        response = process_chat(INPUT_FILE, n_blocks=N_BLOCKS, min_gap=MIN_GAP, summary_style=SUMM_STYLE)
        prompt_base = temp

        print("Response:", response)
    else:
        process_chat(INPUT_FILE, n_blocks=N_BLOCKS, min_gap=MIN_GAP, summary_style=SUMM_STYLE)
