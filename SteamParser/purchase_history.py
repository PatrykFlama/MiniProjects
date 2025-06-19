import re
import requests
import json
import os
from datetime import datetime
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
from tqdm import tqdm
import matplotlib.dates as mdates

EUR_TO_PLN = 4.30  # <-- update with real-time rate if needed
CACHE_FILE = "game_tags_cache.out"
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
            special_transaction = date_match.group(2) if date_match.group(2) else ""
            i += 1

            transaction_type = ""
            items = []
            while i < len(block) and not re.match(r'\d{1,2} \w{3}, \d{4}(?:\t([^\t]+))?', block[i]):
                if re.match(r'Purchase', block[i]) and transaction_type == "":
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
                'spent': spent-wallet_change,
                'wallet_change': wallet_change,
                'balance': balance,
                'payment_method': payment_method
            })

    return transactions

def load_tag_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_tag_cache(cache):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def fetch_game_tags(games):
    tag_counts = defaultdict(int)
    cache = load_tag_cache()
    updated = False

    for name in tqdm(games, desc="Fetching game tags", unit="game"):
        if name in cache:
            tags = cache[name]
        else:
            try:
                r = requests.get('https://steamcommunity.com/actions/SearchApps/' + name)
                results = r.json()
                if not results:
                    continue
                appid = results[0]['appid']
                details = requests.get(f'https://store.steampowered.com/api/appdetails?appids={appid}&cc=pl&l=english').json()
                tags = details[str(appid)]['data'].get('genres', [])
                tags = [tag['description'] for tag in tags]
                cache[name] = tags
                updated = True
            except Exception:
                continue
        for tag in tags:
            tag_counts[tag] += 1

    if updated:
        save_tag_cache(cache)
    return tag_counts


# ================== PLOTTING ==================
def plot_spending_over_time(transactions):
    dates = [t['date'] for t in transactions]
    spends = [t['spent'] for t in transactions]
    if not dates or not spends:
        print("No data to plot.")
        return
    
    # Spending over time
    plt.figure(figsize=(10, 4))
    plt.plot(dates, spends, marker='o', linestyle='-', label='Spent')
    plt.title("Money spent over time")
    plt.ylabel("Amount [PLN]")
    plt.grid(True)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.gcf().autofmt_xdate()
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_spet_sum_over_time(transactions):
    dates = [t['date'] for t in transactions]
    spends = [t['spent'] for t in transactions]
    cumulative_spends = [sum(spends[:i+1]) for i in range(len(spends))]
    
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

    # Plotting tags
    plt.figure(figsize=(10, 6))
    tags, counts = zip(*tag_counts.items())
    plt.barh(tags, counts, color='skyblue')
    plt.xlabel('Number of Games')
    plt.title('Game Tags Frequency')
    plt.tight_layout()
    plt.show()


# ================== MAIN FUNCTION ==================
def plot_stats(transactions):

    dates = [t['date'] for t in transactions]
    spends = [t['spent'] for t in transactions]
    balances = [t['balance'] for t in transactions if t['balance'] is not None]
    balance_dates = [t['date'] for t in transactions if t['balance'] is not None]

    total_spent = sum(spends)
    print(f"💸 Total spent: {total_spent:.2f} PLN")

    # Payment methods
    methods = Counter(t['payment_method'] for t in transactions if t['payment_method'])
    print("\n📌 Most frequent payment methods:")
    for method, count in methods.most_common():
        print(f"  {method}: {count}x")

    # Game frequency
    game_counter = Counter()
    for t in transactions:
        for game in t['items']:
            game_counter[game] += 1
    print("\n🎮 Most purchased games:")
    for game, count in game_counter.most_common(5):
        print(f"  {game}: {count}x")

    # Spending over time
    plot_spending_over_time(transactions)

    # Cumulative spending over time
    plot_spet_sum_over_time(transactions)

    # Wallet balance over time
    wallet_balance_over_time(transactions)

    # Tags
    plot_game_tags(transactions)


def main():
    file_path = "purchase_history.in"  # or whatever your file is
    transactions = parse_file(file_path)

    for t in transactions[:10]:
        print(t)

    plot_stats(transactions)

if __name__ == "__main__":
    main()
