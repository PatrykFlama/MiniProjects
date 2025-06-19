import re
import requests
import json
import os
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
from tqdm import tqdm
import matplotlib.dates as mdates
import csv
import random

EUR_TO_PLN = 4.30  # <-- update with real-time rate if needed
CACHE_FILE = "game_tags_cache.out"
EXPORT_FILE = "purchase_history.csv"


# ================== PARSING FUNCTIONS ==================
def split_transactions(lines):
    """
    Splits the input lines into a list of lists, each containing the lines for a single transaction.
    A new transaction starts at a line matching the date pattern.
    """
    transactions = []
    current = []
    date_pattern = re.compile(r'\d{1,2} \w{3}, \d{4}(?:\t[^\t]+)?')

    for line in lines:
        if date_pattern.match(line):
            if current:
                transactions.append(current)
                current = []
        current.append(line)
    if current:
        transactions.append(current)
    return transactions

def parse_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    if lines[0].startswith("Date"):
        lines = lines[2:]

    transaction_blocks = split_transactions(lines)
    transactions = []

    for block in transaction_blocks:
        i = 0
        line = block[i]
        date_match = re.match(r'(\d{1,2} \w{3}, \d{4})(?:\t([^\t]+))?', line)
        if date_match:
            date = datetime.strptime(date_match.group(1), '%d %b, %Y')
            # special_transaction = date_match.group(2) if date_match.group(2) else ""
            i += 1

            transaction_type = ""
            items = []
            while i < len(block) and not re.match(r'\d{1,2} \w{3}, \d{4}(?:\t([^\t]+))?', block[i]):
                if re.match(r'(Purchase|Refund)', block[i]) and transaction_type == "":
                    transaction_type = block[i]
                    i += 1
                    break
                if re.match(r'.*Market Transactions?', block[i]) and transaction_type == "":
                    transaction_type = "Market Transaction"
                    i += 1
                    break
                if 'zł' in block[i] or '€' in block[i]:
                    break

                items.append(block[i])
                i += 1

            
            payment_line = block[i:] if i < len(block) else ""

            wallet_used = any(re.search(r'.*Wallet.*', line) is not None for line in payment_line)

            if wallet_used:
                payment_line = payment_line[:-1]  # Remove last line if it contains 'Wallet' info
            i += 1
            # Default values
            wallet_change = 0.0
            balance = None
            spent = 0.0
            payment_method = None

            # Find all lines that look like amounts (e.g. '34,99zł', '1,45zł Wallet', '4,99zł\t-1,45zł\t0,00zł')
            # Handle simple purchase: last line is the spent amount
            if block and re.match(r'^\d+,\d+\w+', block[-1]):
                amt_match = re.match(r'^([-+−]?\d+,\d+)(zł|€)', block[-1])
                if amt_match:
                    spent = float(amt_match.group(1).replace(',', '.'))
                    if amt_match.group(2) == '€':
                        spent *= EUR_TO_PLN

            # Handle split payment (wallet + card), e.g. ['1,45zł Wallet', '46,55zł MasterCard', '48,00zł\t-1,45zł\t0,00zł']
            elif block and '\t' in block[-1]:
                parts = block[-1].split('\t')
                # First part: total spent, second: wallet change, third: balance (sometimes 0,00zł)
                if len(parts) >= 2:
                    spent_match = re.match(r'^([-+−]?\d+,\d+)(zł|€)', parts[0])
                    if spent_match:
                        spent = float(spent_match.group(1).replace(',', '.'))
                        if spent_match.group(2) == '€':
                            spent *= EUR_TO_PLN
                if len(parts) >= 3:
                    wallet_match = re.match(r'^([-+−]?\d+,\d+)(zł|€)', parts[1])
                    if wallet_match:
                        wallet_change = float(wallet_match.group(1).replace(',', '.').replace('−', '-'))
                        if wallet_match.group(2) == '€':
                            wallet_change *= EUR_TO_PLN
                    balance_match = re.match(r'^([-+−]?\d+,\d+)(zł|€)', parts[2])
                    if balance_match:
                        balance = float(balance_match.group(1).replace(',', '.'))
                        if balance_match.group(2) == '€':
                            balance *= EUR_TO_PLN

            # Handle market transactions: look for '+0,54zł\t1,45zł' or similar
            elif block and any('Credit' in l for l in block):
                for l in block:
                    if '\t' in l:
                        parts = l.split('\t')
                        # First part: wallet change, second: balance
                        if len(parts) >= 2:
                            wc_match = re.match(r'^([-+−+]?\d+,\d+)(zł|€)', parts[0])
                            if wc_match:
                                wallet_change = float(wc_match.group(1).replace(',', '.').replace('−', '-').replace('+', ''))
                                if wc_match.group(2) == '€':
                                    wallet_change *= EUR_TO_PLN
                            bal_match = re.match(r'^([-+−]?\d+,\d+)(zł|€)', parts[1])
                            if bal_match:
                                balance = float(bal_match.group(1).replace(',', '.'))
                                if bal_match.group(2) == '€':
                                    balance *= EUR_TO_PLN

            # Fallback: try to find any amount in the block
            else:
                for l in block:
                    amt_match = re.match(r'^([-+−]?\d+,\d+)(zł|€)', l)
                    if amt_match:
                        spent = float(amt_match.group(1).replace(',', '.'))
                        if amt_match.group(2) == '€':
                            spent *= EUR_TO_PLN


            # Handle special cases for wallet transactions
            if wallet_used:
                spent_str, wallet_change_str, balance_str = ("", "", "")

                if transaction_type == "Market Transaction":
                    wallet_change_str, balance_str = block[-1].split()
                else:
                    try:
                        spent_str, wallet_change_str, balance_str = block[-1].split()

                        mult = 1
                        if '€' in spent_str:
                            mult = EUR_TO_PLN
                        spent = mult * float(spent_str.replace(',', '.').replace('zł', '').replace('€', ''))
                    
                    except ValueError:
                        spent_str = block[-1]

                        mult = 1
                        if '€' in spent_str:
                            mult = EUR_TO_PLN
                        spent = mult * float(spent_str.replace(',', '.').replace('zł', '').replace('€', ''))

                

                wallet_change_str = wallet_change_str.replace(',', '.').replace('−', '-').replace('+', '')
                balance_str = balance_str.replace(',', '.').replace('−', '-').replace('+', '')

                if wallet_change_str != "":
                    mult = 1
                    if '€' in wallet_change_str:
                        mult = EUR_TO_PLN
                    wallet_change = float(wallet_change_str.replace('zł', '').replace('€', '')) * mult

                if balance_str != "":
                    mult = 1
                    if '€' in balance_str:
                        mult = EUR_TO_PLN
                    balance = float(balance_str.replace('zł', '').replace('€', '')) * mult


            # Extract payment methods from payment_line
            payment_method = []
            for pm in payment_line:
                pm = pm.strip()
                if pm and not re.match(r'\d{1,2} \w{3}, \d{4}', pm):
                    # Remove amount (e.g. '46,55zł MasterCard' -> 'MasterCard')
                    m = re.match(r'[-+−]?\d+,\d+(zł|€)?\s*(.*)', pm)
                    if m:
                        method = m.group(2).strip()
                        if method:
                            payment_method.append(method)
                    else:
                        payment_method.append(pm)

    
            payment_method = [pm for pm in payment_method if pm != '']


            transactions.append({
                'date': date,
                'items': items,
                'type': transaction_type,
                'spent': (spent-wallet_change) if transaction_type != "Refund" else -spent,
                'wallet_change': wallet_change,
                'balance': balance,
                'payment_method': payment_method
            })

    return transactions


# ================== TAGS FETCHING ==================
def load_tag_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_tag_cache(cache):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def load_missing_games():
    missing_file = "missing_" + CACHE_FILE
    if os.path.exists(missing_file):
        with open(missing_file, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_missing_games(missing_games):
    missing_file = "missing_" + CACHE_FILE
    with open(missing_file, 'w', encoding='utf-8') as f:
        for name in missing_games:
            f.write(name + "\n")

def generate_name_variants(name):
    """Generate variants by removing up to 50% of words from the end, one at a time."""
    words = name.split()
    variants = []
    n = len(words)
    min_words = max(1, n // 2)
    for i in range(n, min_words - 1, -1):
        variant = " ".join(words[:i])
        if variant:
            variants.append(variant)
    return variants

def save_name_simmilarities(variant_for_name):
    """Save matching word percentage, original name and variant to a file"""
    simm_file = 'simm_' + CACHE_FILE
    with open(simm_file, 'w', encoding='utf-8') as f:
        for original, variant in variant_for_name.items():
            original_words = set(original.split())
            variant_words = set(variant.split())
            common_words = original_words.intersection(variant_words)
            simm_percentage = len(common_words) / len(original_words) * 100 if original_words else 0
            f.write(f"{simm_percentage:.2f}%\t{original}\t{variant}\n")

def load_name_simmilarities():
    simm_file = 'simm_' + CACHE_FILE
    if os.path.exists(simm_file):
        with open(simm_file, 'r', encoding='utf-8') as f:
            simmilarities = {}
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) == 3:
                    _, original, variant = parts
                    simmilarities[original] = variant
            return simmilarities
    return {}

def fetch_game_tags(games):
    tag_counts = defaultdict(int)
    cache = load_tag_cache()
    updated = False
    missing_games = load_missing_games()
    cache_cnt = 0
    requests_cnt = 0
    variant_for_name = {}

    for name in tqdm(games, desc="Fetching game tags", unit="game"):
        found = False
        tags = []
        tried_variants = []

        # Check if the name is already in the cache or missing games
        for variant in generate_name_variants(name):
            tried_variants.append(variant)
            if variant in cache:
                cache_cnt += 1
                tags = cache[variant]
                found = True
                variant_for_name[name] = variant
                break
            elif variant in missing_games:
                cache_cnt += 1
                tags = []
                found = True
                break

        # If not found in cache or missing games, make a request
        if not found:
            for variant in generate_name_variants(name):
                try:
                    requests_cnt += 1
                    r = requests.get('https://steamcommunity.com/actions/SearchApps/' + variant)
                    results = r.json()
                    if not results:
                        continue
                    appid = results[0]['appid']
                    details = requests.get(f'https://store.steampowered.com/api/appdetails?appids={appid}&cc=pl&l=english').json()
                    tags = details[str(appid)]['data'].get('genres', [])
                    tags = [tag['description'] for tag in tags]
                    cache[variant] = tags
                    updated = True
                    found = True
                    variant_for_name[name] = variant
                    break
                except Exception:
                    continue


        if not found:
            missing_games.add(name)
            continue
        for tag in tags:
            tag_counts[tag] += 1

    if updated:
        save_tag_cache(cache)
    if missing_games:
        save_missing_games(missing_games)

    if variant_for_name:
        save_name_simmilarities(variant_for_name)

    # print(f"Cache hit: {cache_cnt}/{len(games)} games")
    # print(f"Requests made: {requests_cnt}")
    # if not tag_counts:
    #     print("No tags found for the games.")
    #     return {}
    # print(f"Total tags found: {len(tag_counts)}")

    return tag_counts


# ================== PLOTTING ==================
def plot_spending_over_time(transactions, plot_game_names=False):
    dates = [t['date'] for t in transactions]
    spends = [t['spent'] for t in transactions]
    game_names = [", ".join(t['items']) if t['items'] else "" for t in transactions]

    # Filter out transactions with zero spent or of type "Market Transaction"
    if plot_game_names:
        filtered = [
            (d, s, n)
            for d, s, n, t in zip(dates, spends, game_names, [t['type'] for t in transactions])
            if s != 0 and t != "Market Transaction"
        ]
        if not filtered:
            print("No non-zero, non-market transactions to plot.")
            return
        dates, spends, game_names = zip(*filtered)

    if not dates or not spends:
        print("No data to plot.")
        return

    plt.figure(figsize=(10, 4))

    if plot_game_names:
        # Assign a unique color to each game name
        unique_names = list(set(game_names))
        color_map = {name: [random.random() for _ in range(3)] for name in unique_names}

        # Plot each point individually with its color
        for x, y, name in zip(dates, spends, game_names):
            color = color_map.get(name, [0, 0, 0])
            plt.plot(x, y, marker='o', linestyle='', color=color)
        plt.plot([], [], marker='o', linestyle='', color='black', label='Spent')  # For legend

        # Load name similarities if available
        variant_for_name = load_name_simmilarities()

        for x, y, name in zip(dates, spends, game_names):
            display_name = variant_for_name.get(name, name)
            if display_name:
                color = color_map.get(name, [0, 0, 0])
                plt.annotate(
                    display_name,
                    (x, y),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha='center',
                    fontsize=8,
                    rotation=30,
                    color=color,
                    alpha=0.7
                )
    else:
        plt.plot(dates, spends, marker='o', linestyle='-', label='Spent')

    plt.title("Money spent over time")
    plt.ylabel("Amount [PLN]")
    plt.grid(True)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.gcf().autofmt_xdate()
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_spent_sum_over_time(transactions):
    # Sort transactions by date ascending
    sorted_transactions = sorted(transactions, key=lambda t: t['date'])
    dates = [t['date'] for t in sorted_transactions]
    spends = [t['spent'] for t in sorted_transactions]
    cumulative_spends = []
    total = 0
    for s in spends:
        total += s
        cumulative_spends.append(total)

    if not dates or not cumulative_spends:
        print("No data to plot.")
        return

    # Cumulative spending over time
    plt.figure(figsize=(10, 4))
    plt.plot(dates, cumulative_spends, marker='o', linestyle='-', label='Cumulative Spent')
    plt.title("Cumulative money spent over time")
    plt.ylabel("Cumulative Amount [PLN]")
    plt.grid(True)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.gcf().autofmt_xdate()
    plt.legend()
    plt.tight_layout()
    plt.show()

def wallet_balance_over_time(transactions):
    dates = [t['date'] for t in transactions if t['balance'] is not None]
    balances = [t['balance'] for t in transactions if t['balance'] is not None]
    if not dates or not balances:
        print("No wallet balance data to plot.")
        return
    
    # Wallet balance over time
    plt.figure(figsize=(10, 4))
    plt.plot(dates, balances, marker='o', linestyle='-', label='Wallet Balance')
    plt.title("Wallet balance over time")
    plt.ylabel("Balance [PLN]")
    plt.grid(True)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.gcf().autofmt_xdate()
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_game_tags(transactions):
    games = set()
    for t in transactions:
        for item in t['items']:
            games.add(item)

    if not games:
        print("No games found in transactions.")
        return

    tag_counts = fetch_game_tags(games)
    if not tag_counts:
        print("No tags found for the games.")
        return
    
    # Sort tags by frequency
    tag_counts = dict(sorted(tag_counts.items(), key=lambda item: item[1], reverse=True))

    # Plotting tags
    plt.figure(figsize=(10, 6))
    tags, counts = zip(*tag_counts.items())
    plt.barh(tags, counts, color='skyblue')
    plt.xlabel('Number of Games')
    plt.title('Game Tags Frequency')
    plt.tight_layout()
    plt.show()


# ================== MAIN FUNCTION ==================
def pretty_print_transaction(transaction):
    date_str = transaction['date'].strftime('%Y-%m-%d')
    items_str = ', '.join(transaction['items']) if transaction['items'] else "No items"
    type_str = transaction['type'] if transaction['type'] else "Unknown"
    spent_str = f"{transaction['spent']:.2f} PLN"
    wallet_change_str = f"{transaction['wallet_change']:.2f} PLN" if transaction['wallet_change'] else "0.00 PLN"
    balance_str = f"{transaction['balance']:.2f} PLN" if transaction['balance'] is not None else "N/A"
    payment_method_str = ', '.join(transaction['payment_method']) if transaction['payment_method'] else "Unknown"

    print(f"Date: {date_str}, Items: {items_str}, Type: {type_str}, Spent: {spent_str}, "
          f"Wallet Change: {wallet_change_str}, Balance: {balance_str}, Payment Method: {payment_method_str}")


def export_transactions_to_csv(transactions):
    with open(EXPORT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['date', 'items', 'type', 'spent', 'wallet_change', 'balance', 'payment_method']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for t in transactions:
            writer.writerow({
                'date': t['date'].strftime('%Y-%m-%d'),
                'items': ', '.join(t['items']),
                'type': t['type'],
                'spent': t['spent'],
                'wallet_change': t['wallet_change'],
                'balance': t['balance'],
                'payment_method': ', '.join(t['payment_method'])
            })
    print(f"Transactions exported to {EXPORT_FILE}")


def plot_stats(transactions):
    spends = [t['spent'] for t in transactions]
    total_spent = sum(spends)
    print(f"Total spent: {total_spent:.2f} PLN")

    # Spending over time
    plot_spending_over_time(transactions)

    # Cumulative spending over time
    plot_spent_sum_over_time(transactions)

    # Wallet balance over time
    wallet_balance_over_time(transactions)

    # Tags
    plot_game_tags(transactions)

    # Plot game names over time
    plot_spending_over_time(transactions, plot_game_names=True)


def main():
    file_path = "purchase_history.in"  # or whatever your file is
    transactions = parse_file(file_path)

    # for t in transactions:
    #     pretty_print_transaction(t)

    plot_stats(transactions)

    export_transactions_to_csv(transactions)

if __name__ == "__main__":
    main()
