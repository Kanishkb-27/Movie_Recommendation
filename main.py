import time, pandas as pd
from textblob import TextBlob
from colorama import init, Fore

# Init colors
init(autoreset=True)

# Load CSV (same error output)
try: df = pd.read_csv("imdb_top_1000.csv")
except FileNotFoundError:
    print(Fore.RED + "Error: The file 'imdb_top_1000.csv' was not found."); raise SystemExit

# Unique genres
genres = sorted({g.strip() for xs in df["Genre"].dropna().str.split(", ") for g in xs})

def dots():
    """Prints ... with delay (AI thinking effect)."""
    for _ in range(3): print(Fore.YELLOW + ".", end="", flush=True); time.sleep(0.5)

def senti(p):
    """Polarity -> label."""
    return "Positive 😊" if p > 0 else "Negative 😞" if p < 0 else "Neutral 😐"

    # 1) Start: d = df
    # 2) If genre: filter Genre contains (case-insensitive)
    # 3) If rating not None: filter IMDB_Rating >= rating
    # 4) If empty: return "No suitable movie recommendations found."
    # 5) Shuffle: sample(frac=1).reset_index(drop=True)
    # 6) need_nonneg = bool(mood)
    # 7) Loop rows:
    #    - skip missing Overview
    #    - pol = TextBlob(overview).sentiment.polarity
    #    - if not need_nonneg or pol >= 0: append (Series_Title, pol)
    #    - stop at n
    # 8) Return list else same message
def recommend(genre=None, mood=None, rating=None, n=5):
    d = df
    if genre: 
        d = d[d["Genre"].str.contains(genre, case=False, na=False)]
    if rating is not None: 
        d = d[d["IMDB_Rating"] >= rating]
    if d.empty: 
        return "No suitable movie recommendations found."
    d, need_nonneg, out = d.sample(frac=1).reset_index(drop=True), bool(mood), []
    for _, r in d.iterrows():
        ov = r.get("Overview")
        if pd.isna(ov): 
            continue
        pol = TextBlob(ov).sentiment.polarity
        if (not need_nonneg) or pol >= 0:
            out.append((r["Series_Title"], pol))
            if len(out) == n: 
                break
    return out if out else "No suitable movie recommendations found."
def show(recs, name):
    """Print in same format: header + numbered 🎥 lines with polarity + senti()."""
    # Print: "\n🍿 AI-Analyzed Movie Recommendations for {name}:"
    # Loop enumerate(recs, 1) and print:
    # "{i}. 🎥 {title} (Polarity: {p:.2f}, {senti(p)})"
    print(f"{Fore.YELLOW}\n AI-Analyzed Movie Recommendations for {name}")
    for i, (t,p) in enumerate(recs, 1):
        print(f"{Fore.CYAN}{i}.{t} (Polarity: {p:.2f}, {senti(p)})")

def get_genre():
    """Print genres, then ask: Enter genre number or name: (repeat until valid)."""
    # Print "Available Genres: " then each: "{i}. {genre}"
    # Input prompt must match exactly
    # Accept valid number OR exact title-cased genre name
    # On invalid: print "Invalid input. Try again.\n"
    print(Fore.GREEN+"Available Genres: ",end="")
    for i, g in enumerate(genres, 1): print(f"{Fore.CYAN}{i}. {g}")
    print()
    while True:
        x=input(Fore.YELLOW+"Enter genre number or names: ").strip()
        if x.isdigit() and 1 <= int(x) <= len(genres): return genres[int(x)-1]
        x=x.title()
        if x in genres: return x
        print(Fore.RED+"Invalid input. Try again.\n")

def get_rating():
    """Ask rating or 'skip' (repeat until valid)."""
    # Prompt must match exactly
    # If skip -> None
    # Else float in 7.6..9.3
    # Out of range -> "Rating out of range. Try again.\n"
    # Bad float -> "Invalid input. Try again.\n"
    while True:
        x=input(Fore.YELLOW+"Enter minimum IMDB rating (7.6-9.3) or 'skip': ").strip()
        if x.lower()=="skip":return None
        try:
            r=float(x)
            if 7.6<=r<=9.3: return r
            print(Fore.RED+"Rating out of range. Try again.\n")
        except ValueError:
            print(Fore.RED+"Invalid input. Try again\n")

# MAIN (students write)
# 1) Print welcome + ask name + greet
# 2) Print 🔍 line
# 3) genre = get_genre(); mood input
# 4) Print "Analyzing mood" + dots(); compute mood polarity + print mood line
# 5) rating = get_rating()
# 6) Print "Finding movies for {name}" + dots()
# 7) recs = recommend(...); if str print red else show()
# 8) Loop ask "Would you like more recommendations? (yes/no):"
#    - no -> print enjoy line + break
#    - yes -> recommend again + show
#    - else -> invalid choice line
print(Fore.BLUE + "🎥 Welcome to your Personal Movie Recommendation Assistant! 🎥\n")
name = input(Fore.YELLOW + "What's your name? ").strip()
print(f"\n{Fore.GREEN}Great to meet you, {name}!\n")
print(Fore.BLUE + "\n🔍 Let's find the perfect movie for you!\n")
genre = get_genre()
mood = input(Fore.YELLOW + "How do you feel today? (Describe your mood): ").strip()
print(Fore.BLUE + "\nAnalyzing mood", end="", flush=True); dots()
mp = TextBlob(mood).sentiment.polarity
md = "positive 😊" if mp > 0 else "negative 😞" if mp < 0 else "neutral 😐"
print(f"\n{Fore.GREEN}Your mood is {md} (Polarity: {mp:.2f}).\n")
rating = get_rating()
print(f"{Fore.BLUE}\nFinding movies for {name}", end="", flush=True); dots()
recs = recommend(genre=genre, mood=mood, rating=rating, n=5)
print(Fore.RED + recs + "\n") if isinstance(recs, str) else show(recs, name)
while True:
    a = input(Fore.YELLOW + "\nWould you like more recommendations? (yes/no): ").strip().lower()
    if a == "no":
        print(Fore.GREEN + f"\nEnjoy your movie picks, {name}! 🎬🍿\n"); break
    if a == "yes":
        recs = recommend(genre=genre, mood=mood, rating=rating, n=5)
        print(Fore.RED + recs + "\n") if isinstance(recs, str) else show(recs, name)
    else:
        print(Fore.RED + "Invalid choice. Try again.\n")