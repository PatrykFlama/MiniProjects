import requests
import re
from datetime import datetime, timedelta
import json

DEBUG = False
dprint = print if DEBUG else lambda *args, **kwargs: None

# OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_URL = "http://192.168.10.15:11434/api/generate"
MODEL = "llama3.2:3b"
MODEL = "mwiewior/bielik"

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
        (", uwzględnij poprzednią odpowiedź w tej odpowiedzi" if prev_summary else "") + ":\n\n" + text
    elif summary_style == "simple_chain" or summary_style:
        prompt = prompt_base + ":\n\n" + text
    elif summary_style == "summarize_all":
        prompt = summarize_all_prompt + ":\n\n" + text

    if prev_summary:
        prompt = f"Odpowiedź do poprzedniego fragmentu: \n{prev_summary}\n\n{prompt}"


    dprint("----------------Prompt:----------------")
    dprint(prompt)

    response = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": prompt, "options": {"reset": True}, "stream": True})

    dprint("=====================RESPTXT=====================")

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



# n_blocks - number of blocks to divide chat into
# min_gap_min - minimum time gap between blocks in minutes (to not split in the middle of a conversation)
# summary style = 
    # summarize_all - summarize all blocks together
    # oneblock_chain - for each block create summary of block and previous summary
    # simple_chain - generate summary for each block separately only feeding previous summary
    # double_layer - first generate simple_chain, then summarize it
    # isolated_chain - generate summary for each block separately without feeding previous summary
    # isolated_double_layer - generate isolated_chain, then summarize it

process_chat("wa_chat.txt", n_blocks=30, min_gap=60, summary_style="oneblock_chain")
