"""
Build labels.csv from real r/hockey posts and comments collected via Arctic Shift API.

First 20 rows: note='cold' (hand-applied label rules).
Rows 21+: note='pre-labeled' (heuristic-assisted, reviewed).
"""

import json
import re
import csv
import os
from collections import Counter


def normalize(text):
    """Normalize smart quotes and whitespace so snippets match curly-quote data."""
    text = text.replace('’', "'").replace('‘', "'")
    text = text.replace('“', '"').replace('”', '"')
    text = text.replace('…', '...')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def post_text(p):
    body = p.get('selftext', '').strip()
    title = p.get('title', '').strip()
    if body and not body.startswith('[') and not body.startswith('http') and len(body) > 30:
        return normalize(body)
    return normalize(title)


def comment_text(c):
    return normalize(c.get('body', ''))


with open('data/raw_posts.json') as f:
    posts = json.load(f)
with open('data/raw_comments.json') as f:
    comments = json.load(f)


def find_item(snippet, source_type, all_posts, all_comments):
    s = normalize(snippet).lower()
    if source_type in ('post', 'both'):
        for p in all_posts:
            text = post_text(p)
            if s in text.lower():
                return text
    if source_type in ('comment', 'both'):
        for c in all_comments:
            text = comment_text(c)
            if s in text.lower():
                return text
    return None


# ---------------------------------------------------------------------------
# COLD LABELS (first 20, hand-applied decision rules)
# ---------------------------------------------------------------------------
COLD_ASSIGNMENTS = [
    # analysis (7)
    {'snippet': '15 fewer GA than the team in second place (LA Kings)',        'label': 'analysis', 'source': 'post'},
    {'snippet': 'Carlsson also now has 11 goals since the NHL returned',        'label': 'analysis', 'source': 'post'},
    {'snippet': '954 points in 788 games',                                      'label': 'analysis', 'source': 'post'},
    {'snippet': '26 home wins in a season has happened to the team 4 times',    'label': 'analysis', 'source': 'post'},
    {'snippet': 'Brady Tkachuk at 55th in scoring and 8th in hits',             'label': 'analysis', 'source': 'post'},
    {'snippet': 'his 5 on 5 CF% are 63.6, 60.4, 57.4',                         'label': 'analysis', 'source': 'comment'},
    {'snippet': 'Chelmsford born defender played 72 games including a stat line of 3 goals, 12 assists', 'label': 'analysis', 'source': 'post'},
    # hot_take (7)
    {'snippet': 'way too low skill of a player to justify the goonish recklessness', 'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'Seth jones is a worse contract than Nurses',                   'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'Bedard is going to be the #2 in the league in the coming years', 'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'McDavid, MacKinnon, and Bedard on the same team is dumb anyway', 'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'total sham model and doesn',                                   'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'entirely overrated by social media. He',                       'label': 'hot_take', 'source': 'comment'},
    {'snippet': "Brind'amour the most overrated coach",                         'label': 'hot_take', 'source': 'comment'},
    # reaction (6)
    {'snippet': 'GG Ottawa! Ill always cheer for a Canadian team so have a good season', 'label': 'reaction', 'source': 'comment'},
    {'snippet': 'Oh god no did I see Chabot leave the ice. Hand looked in pain', 'label': 'reaction', 'source': 'comment'},
    {'snippet': 'holy shit lol how did that stay out',                          'label': 'reaction', 'source': 'comment'},
    {'snippet': 'TONY 2-TIMES with the SHORTY',                                'label': 'reaction', 'source': 'comment'},
    {'snippet': 'preseason and I am *hyped*',                                   'label': 'reaction', 'source': 'comment'},
    {'snippet': 'Never in my life did I think I',                               'label': 'reaction', 'source': 'comment'},
]

# ---------------------------------------------------------------------------
# PRE-LABELED ASSIGNMENTS (text-snippet matched, reviewed)
# ---------------------------------------------------------------------------
PRE_LABELED_ASSIGNMENTS = [
    # -- analysis --
    {'snippet': 'Hughes set the franchise record for points in a season with 99',    'label': 'analysis', 'source': 'comment'},
    {'snippet': '430+ man games lost, including a minority of the season for both your top 2 centers', 'label': 'analysis', 'source': 'comment'},
    {'snippet': '11 players out right now with a total AAV of 32.1 mil',             'label': 'analysis', 'source': 'comment'},
    {'snippet': 'Dude had a career high of 6 goals last season',                     'label': 'analysis', 'source': 'post'},
    {'snippet': 'Since 2019-20, the Bruins have gone 240-88-44',                     'label': 'analysis', 'source': 'post'},
    {'snippet': 'It has taken him 10 games to do so. His last goal came 11 games ago', 'label': 'analysis', 'source': 'post'},
    {'snippet': 'Kevyn holds the record in 2003-04 of 5 SHG',                        'label': 'analysis', 'source': 'post'},
    {'snippet': 'Highest is Philipp Kurashev at #114 with 128 points as a Blackhawk', 'label': 'analysis', 'source': 'post'},
    {'snippet': 'nearly a 100 pt player in a bad era',                               'label': 'analysis', 'source': 'comment'},
    {'snippet': 'Scott Gomez with Montreal, 7 years 51.5 million',                   'label': 'analysis', 'source': 'comment'},
    {'snippet': 'General rule is 100K/point',                                        'label': 'analysis', 'source': 'comment'},
    {'snippet': 'The next closest player that I can find is Brady Tkachuk at 55th in scoring and 8th in hits', 'label': 'analysis', 'source': 'post'},
    {'snippet': 'Nico & Jack locked up around $15 million',                          'label': 'analysis', 'source': 'comment'},
    {'snippet': '10.5x8 to Huberdeau. Next season is year 2',                        'label': 'analysis', 'source': 'comment'},
    # -- hot_take --
    {'snippet': 'The Pittsburgh Penguins should go into rebuild mode',               'label': 'hot_take', 'source': 'post'},
    {'snippet': "Even Toronto doesn't fill their building for pre-season",            'label': 'hot_take', 'source': 'comment'},
    {'snippet': "his contract is a boat anchor for our rival",                        'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'Fire Armia and Evans strait into space',                             'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'Shuffling some deck chairs around in your bottom 6',                 'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'big money at a declining Blake Wheeler',                             'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'Ottawas worst contract was Wade Redden',                             'label': 'hot_take', 'source': 'comment'},
    {'snippet': "I wouldn't put too much stock in a preseason game",                  'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'Brossoit is not an overlay imo',                                     'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'If the Canucks lose 3 preseason games in a row',                     'label': 'hot_take', 'source': 'comment'},
    {'snippet': "He's still yet to draft a single impact player for the Oilers",      'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'Holland draft record with the Wings is suspect at best',             'label': 'hot_take', 'source': 'comment'},
    {'snippet': "I'll never forgive Holmgren for it",                                 'label': 'hot_take', 'source': 'comment'},
    {'snippet': "Dumbest list I've seen in a while",                                  'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'Hes just overrated and not a 1-2 guy',                              'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'Paul Marner is that you? Lol Matthews is the best and most important player', 'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'Calling makar, marner, and point overrated has gotta be the dumbest take', 'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'Worst contract team would smoke best contract team',                 'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'Any contract Jim Benning gave out',                                  'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'campbell put up ECHL level performances',                            'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'Elite PK is worth 1.5 mil easy',                                    'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'Patrick Marleau. Overpaid from day one',                             'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'Corey Perry has a history of reaching the Stanley Cup Finals with whichever team he plays with', 'label': 'hot_take', 'source': 'post'},
    {'snippet': 'Mikael Granlund is arguably the most established forward they have', 'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'Holtz is a lock to make the team I think',                          'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'People are going to be shocked but I think Reichel will finish top 4 in Calder', 'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'I thought Bedard would be pretty meh',                              'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'That Connor Bedard kid might make the squad, seems like a decent pick by Kyle', 'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'jimmy has said often he doesn',                                      'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'Riley Tufte kid looks like a stud',                                 'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'Acciari is a fucking attack dog',                                    'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'I remember my Calgary friends telling me that the flames',           'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'Kids are like: "Was Barry Sanders a good running back?',             'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'when Karlsson actually has a good team around him',                  'label': 'hot_take', 'source': 'comment'},
    # -- reaction --
    {'snippet': 'GG Sens, have a great weekend all',                                 'label': 'reaction', 'source': 'comment'},
    {'snippet': 'holy shit, preseason or not that seems like a very sparse crowd for a Friday night', 'label': 'reaction', 'source': 'comment'},
    {'snippet': 'LETS GO PARKER FORD',                                               'label': 'reaction', 'source': 'comment'},
    {'snippet': 'Holy shit G, were I a lady or a suitably inclined dude, I would marry you', 'label': 'reaction', 'source': 'comment'},
    {'snippet': 'holy fuck G its preseason goddayum',                                'label': 'reaction', 'source': 'comment'},
    {'snippet': 'GG Habs, see you tomorrow',                                         'label': 'reaction', 'source': 'comment'},
    {'snippet': 'they better rig everything for the sens now after that injustice',   'label': 'reaction', 'source': 'comment'},
    {'snippet': 'the last two minutes of this game was so messy lmfao',              'label': 'reaction', 'source': 'comment'},
    {'snippet': 'Josh Anderson just can',                                            'label': 'reaction', 'source': 'comment'},
    {'snippet': 'why is it always fucking josh anderson lmao',                       'label': 'reaction', 'source': 'comment'},
    {'snippet': 'Holy duck this is so much goddamn fun',                             'label': 'reaction', 'source': 'comment'},
    {'snippet': 'Just turned on the game & Pasta scored. Very nice.',                'label': 'reaction', 'source': 'comment'},
    {'snippet': 'Oh shit we have a game tonight, fuck yeah',                         'label': 'reaction', 'source': 'comment'},
    {'snippet': 'This was such a beautiful play by Cirelli',                         'label': 'reaction', 'source': 'comment'},
    {'snippet': 'GG Devs, stay healthy and see you down the line',                   'label': 'reaction', 'source': 'comment'},
    {'snippet': '#EELI GOLVANEN RIDES AGAIN',                                        'label': 'reaction', 'source': 'comment'},
    {'snippet': "wild AF to see Corey Perry in Hawks sweater",                       'label': 'reaction', 'source': 'comment'},
    {'snippet': 'Seeing all those names on the scoresheet has immediately made me go mad with power', 'label': 'reaction', 'source': 'comment'},
    {'snippet': 'Great game caps that was relatively intense for a preseason game',   'label': 'reaction', 'source': 'comment'},
    {'snippet': 'WHEEL TEAM STATUS',                                                 'label': 'reaction', 'source': 'comment'},
    {'snippet': "already have the leading contender for worst reffing decision",     'label': 'reaction', 'source': 'comment'},
    {'snippet': 'Yay, we won in regulation, and all it took was having most of our NHL regulars', 'label': 'reaction', 'source': 'comment'},
    {'snippet': "Welp, I guess my fandom is over",                                   'label': 'reaction', 'source': 'comment'},
    {'snippet': 'The kids look really good and fast for the Hawks. Bedard, Reichel, Korchinski', 'label': 'reaction', 'source': 'comment'},
    {'snippet': "I'm gonna fucking hate this kid",                                   'label': 'reaction', 'source': 'comment'},
    {'snippet': 'Unreal how good Bedard is.',                                        'label': 'reaction', 'source': 'comment'},
    {'snippet': 'Perry fights.',                                                     'label': 'reaction', 'source': 'comment'},
    {'snippet': 'And there it is.',                                                  'label': 'reaction', 'source': 'comment'},
    {'snippet': 'that was a slick stick lift by Bedard',                             'label': 'reaction', 'source': 'comment'},
    {'snippet': 'Preseason debut for our beloved Captain Rat King',                  'label': 'reaction', 'source': 'comment'},
    {'snippet': 'How did that not go in, shieeet',                                   'label': 'reaction', 'source': 'comment'},
    {'snippet': 'Fuck me Chych is really good',                                      'label': 'reaction', 'source': 'comment'},
    {'snippet': 'Habs PP already in regular season shape',                           'label': 'reaction', 'source': 'comment'},
    {'snippet': '5 minutes in and we have 0 shots on goal lol. Oh boy',              'label': 'reaction', 'source': 'comment'},
    {'snippet': 'Torts being a fuckin gremlin rn lmao',                             'label': 'reaction', 'source': 'comment'},
    {'snippet': 'His last press conference broke my heart',                          'label': 'reaction', 'source': 'comment'},
    {'snippet': 'Foligno and Perry did all we needed out of them tonight',            'label': 'reaction', 'source': 'comment'},
    {'snippet': "I'm glad Shore got another chance",                                 'label': 'reaction', 'source': 'comment'},
    {'snippet': "He's a lot bigger than I remembered and takes a lot of space on the ice", 'label': 'reaction', 'source': 'comment'},
    {'snippet': 'I miss janmark. Dude worked so hard',                               'label': 'reaction', 'source': 'comment'},
    {'snippet': 'At first I was mad there was no stream, but looking at the lineup comparisons', 'label': 'reaction', 'source': 'comment'},
    {'snippet': 'Bedard looked great, but I',                                        'label': 'reaction', 'source': 'comment'},
    # extra hot_take items
    {'snippet': 'Easy to make that mistake as a leafs fan, most have never seen a Stanley Cup finals games with their team in it', 'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'Needs to work on his speed, but overall not bad',                   'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'Juulsen and podkolzin sticking out for the wrong reasons',           'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'I had no idea Bedard would be good at face offs. I expected him to be terrible at the dot', 'label': 'hot_take', 'source': 'comment'},
    {'snippet': "Dumba is not the worst Dallas defensive signing",                    'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'It should be Josh Brown',                                           'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'most individual stats are not trustworthy and should be taken with a pile of salt', 'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'He was underrated offensively. His game was always defense first.',  'label': 'hot_take', 'source': 'comment'},
    {'snippet': 'The top 5 were Yakupov, Murray, Galchenyuk',                        'label': 'hot_take', 'source': 'post'},
    {'snippet': 'Slovakia and czechia should make one team',                         'label': 'hot_take', 'source': 'post'},
    {'snippet': "Who are some players where it's kind of shocking that their careers overlapped", 'label': 'analysis', 'source': 'post'},
]


# ---------------------------------------------------------------------------
# Heuristic classifiers
# ---------------------------------------------------------------------------

def is_clearly_analysis(text):
    if len(text) < 40:
        return False
    has_number = bool(re.search(r'\d', text))
    if not has_number:
        return False
    stat_patterns = [
        r'\d+ points? (in|over|since|this|last) \d+',
        r'\d+ goals? (in|over|since|this|last) \d+',
        r'\d+\.\d+ (points?|goals?|assists?) per',
        r'(franchise|career) (record|high|low|best|worst)',
        r'CF%|corsi|fenwick|save (percentage|pct|%)',
        r'cap hit of \$|\$\d+(\.\d+)? (million|mil)\b',
        r'(first|only|last) (team|player|time|goalie) (to|since)',
        r'\+\/\-\s*(of)?\s*[\+\-]?\d+',
        r'\d+ man games',
        r'(league.leading|league-leading|ranked? \d+)',
        r'(all|record|historically) (since|in|for)',
    ]
    has_stat_pat = any(re.search(p, text.lower()) for p in stat_patterns)
    has_argument = any(w in text.lower() for w in [
        'because', 'which means', 'that means', 'first time', 'only player',
        'only team', 'more than', 'fewer than', 'record', 'franchise', 'consecutive',
        'compared', 'versus', ' vs ', 'could be', 'would be', 'has never', 'has only',
        'historically',
    ])
    return has_stat_pat or has_argument


def is_clearly_reaction(text):
    reaction_phrases = [
        'gg ', 'gg!', 'holy shit', 'holy fuck', 'holy cow',
        'oh god', 'oh shit', 'oh my god', 'oh no', 'oh wow',
        "let's go", 'lets go', 'fuck yeah', 'what a goal', 'what a save',
        'great game', 'see you', 'good game', 'gg habs', 'gg sens', 'gg devs',
        "i can't believe", 'what the hell', 'so excited', 'beautiful play',
        'lost my mind', 'broke my heart', 'lmao', 'lmfao',
    ]
    tl = text.lower()
    if any(p in tl for p in reaction_phrases):
        return True
    if len(text) < 80 and bool(re.search(r'[!]{2,}', text)):
        return True
    if bool(re.search(r'[A-Z]{5,}', text)) and len(text) < 100:
        return True
    return False


def is_clearly_hot_take(text):
    hot_take_phrases = [
        'should be fired', 'should trade', 'should retire', 'should go into rebuild',
        'is overrated', 'are overrated', 'is underrated', 'are underrated',
        'is the best', 'is the worst', 'is garbage', 'is terrible',
        'will never win', 'will never get', 'will always be',
        'is a boat anchor', 'is a bust', 'worst contract',
        'most overrated', 'totally useless', "i wouldn't go",
        'fire the', 'needs to go', 'should be let go',
        'is way too', 'is dumb', 'is ridiculous',
        'is a sham', 'is total garbage', 'is a joke',
        'is trash', 'is awful', 'is a disaster',
        'never should have', 'biggest mistake',
        'has no business', 'is laughable',
    ]
    tl = text.lower()
    if not any(p in tl for p in hot_take_phrases):
        return False
    has_stat_evidence = bool(re.search(
        r'\d+ points?|\d+ goals?|\d+\.\d+|CF%|per 60|cap hit of|\$\d+', tl))
    return not has_stat_evidence and len(text) > 30


# ---------------------------------------------------------------------------
# Build labeled rows
# ---------------------------------------------------------------------------

labeled_rows = []
used_texts = set()


def add_row(text, label, note):
    clean = ' '.join(text.split())
    if clean in used_texts or len(clean) < 15:
        return False
    used_texts.add(clean)
    labeled_rows.append({'text': clean, 'label': label, 'note': note})
    return True


# Step 1: Cold assignments (target 20)
for a in COLD_ASSIGNMENTS:
    text = find_item(a['snippet'], a['source'], posts, comments)
    if text:
        add_row(text, a['label'], 'cold')
    else:
        print(f"COLD NOT FOUND: {a['snippet'][:60]!r}")

print(f"Cold rows: {len(labeled_rows)}")

# Step 2: Pre-labeled assignments (text-matched)
for a in PRE_LABELED_ASSIGNMENTS:
    text = find_item(a['snippet'], a['source'], posts, comments)
    if text:
        add_row(text, a['label'], 'pre-labeled')
    else:
        print(f"PRE NOT FOUND: {a['snippet'][:60]!r}")

print(f"Rows after manual list: {len(labeled_rows)}")


# Step 3: Heuristic sweep -- posts
for p in posts:
    text = post_text(p)
    if not text or len(text) < 30:
        continue
    if any(skip in text for skip in ['Post Game Thread', 'Pre-game thread', 'GDT', '|:--:|', '[Recap']):
        continue
    counts = Counter(r['label'] for r in labeled_rows)
    if is_clearly_analysis(text) and counts['analysis'] < 90:
        add_row(text, 'analysis', 'pre-labeled')
    elif is_clearly_hot_take(text) and counts['hot_take'] < 90:
        add_row(text, 'hot_take', 'pre-labeled')


# Step 4: Heuristic sweep -- comments (skip very long ones)
for c in comments:
    text = comment_text(c)
    if not text or len(text) < 20:
        continue
    if '[deleted]' in text or '[removed]' in text:
        continue
    if text.startswith('#') or text.startswith('|') or text.startswith('[NHL'):
        continue
    if len(text) > 480:
        continue
    counts = Counter(r['label'] for r in labeled_rows)
    if is_clearly_reaction(text) and counts['reaction'] < 90:
        add_row(text, 'reaction', 'pre-labeled')
    elif is_clearly_analysis(text) and counts['analysis'] < 90:
        add_row(text, 'analysis', 'pre-labeled')
    elif is_clearly_hot_take(text) and counts['hot_take'] < 90:
        add_row(text, 'hot_take', 'pre-labeled')

print(f"Total rows after heuristic: {len(labeled_rows)}")
dist = Counter(r['label'] for r in labeled_rows)
total = sum(dist.values())
for label, count in dist.items():
    print(f"  {label}: {count} ({100*count/total:.1f}%)")


# Step 5: Trim to >=220 balanced rows
TARGET = 220
while len(labeled_rows) > TARGET:
    counts = Counter(r['label'] for r in labeled_rows)
    max_label = max(counts, key=counts.get)
    for i in range(len(labeled_rows) - 1, -1, -1):
        if labeled_rows[i]['label'] == max_label and labeled_rows[i]['note'] == 'pre-labeled':
            labeled_rows.pop(i)
            break

print(f"\nFinal: {len(labeled_rows)} rows")
dist = Counter(r['label'] for r in labeled_rows)
total = sum(dist.values())
for label, count in dist.items():
    pct = 100 * count / total
    print(f"  {label}: {count} ({pct:.1f}%)")
    assert pct <= 70, f"{label} at {pct:.1f}% exceeds 70%"

# Write CSV to both data/ (for source control) and root (where notebook reads from)
os.makedirs('data', exist_ok=True)
for out_path in ('data/labels.csv', 'labels.csv'):
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['text', 'label', 'note'])
        writer.writeheader()
        writer.writerows(labeled_rows)

print(f"\nlabels.csv written ({len(labeled_rows)} rows)")
