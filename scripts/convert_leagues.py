import csv
import json

leagues = []
with open('data/leagues_complete.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        country = row['pays']
        levels = []
        for level in ['ligue1', 'ligue2', 'ligue3', 'ligue4']:
            if row[level] and row[level] != '':
                levels.append(row[level])
        if levels:
            leagues.append({
                'pays': country,
                'ligues': levels,
                'niveau_max': len(levels)
            })

with open('data/leagues.json', 'w', encoding='utf-8') as f:
    json.dump(leagues, f, ensure_ascii=False, indent=2)

print(f"✅ {len(leagues)} pays avec leurs ligues")
