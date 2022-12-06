import requests
from bs4 import BeautifulSoup
import lxml
from pprint import pprint
import json

link = "https://www.cricbuzz.com/live-cricket-scorecard/56955/ban-vs-ind-1st-odi-india-tour-of-bangladesh-2022"
rows = []

page = requests.get(link).text
soup = BeautifulSoup(page, "lxml")

for row in soup.find_all("div", {"class": "cb-scrd-itms"}):
    stat_row = [i.text.strip() for i in row.find_all("div", {"class": "cb-col"})]
    rows.append(stat_row)

teams = [
    i.text.strip().split()[0]
    for i in soup.find_all("div", {"class": "cb-scrd-hdr-rw"})[:-1]
]

scorecard = {
    "MatchInfo": {
        "Winner": soup.find("div", {"class": "cb-scrcrd-status"})
        .text.split()[0]
        .strip()
    },
    "Batting": [],
    "Bowling": [],
}

temp = {teams[0]: {}, teams[1]: {}}

extra_or_total_count = 0
for row in rows:
    length = len(row)
    if length == 3:
        extra_or_total_count += 1
        if extra_or_total_count % 2 == 0:
            temp[teams[0 if extra_or_total_count == 2 else 1]]["Total"] = int(row[1])
            temp[teams[0 if extra_or_total_count == 2 else 1]]["Wickets"] = int(
                row[2].split()[0].replace("(", "")
            )
            temp[teams[0 if extra_or_total_count == 2 else 1]]["Overs"] = float(
                row[2].split()[2]
            )

extra_or_total_count = 0
for row in rows:
    length = len(row)
    if length == 3:
        extra_or_total_count += 1
        if extra_or_total_count % 2 == 0:
            temp[teams[0 if extra_or_total_count == 2 else 1]]["Total"] = int(row[1])
            temp[teams[0 if extra_or_total_count == 2 else 1]]["Wickets"] = int(
                row[2].split()[0].replace("(", "")
            )
            temp[teams[0 if extra_or_total_count == 2 else 1]]["Overs"] = float(
                row[2].split()[2]
            )
    elif length == 7:
        player = {
            "Name": row[0].replace("(c)", "").replace("(wk)", "").strip(),
            "Runs": int(row[2]),
            "Balls": int(row[3]),
            "Fours": int(row[4]),
            "Sixes": int(row[5]),
            "StrikeRate": float(row[6]),
            "WinLoss": teams[0 if extra_or_total_count == 0 else 1]
            == scorecard["MatchInfo"]["Winner"],
            "Team": teams[0 if extra_or_total_count == 0 else 1],
            "MathcInfo": temp[teams[0 if extra_or_total_count == 0 else 1]],
        }

        scorecard["Batting"].append(player)
    elif length == 8:
        player = {
            "Name": row[0].replace("(c)", "").replace("(wk)", "").strip(),
            "Overs": float(row[1]),
            "Maiden": int(row[2]),
            "Runs": int(row[3]),
            "Wickets": int(row[4]),
            "NoBalls": int(row[5]),
            "Wides": int(row[6]),
            "EconomyRate": float(row[7]),
            "WinLoss": teams[1 if extra_or_total_count == 2 else 0]
            == scorecard["MatchInfo"]["Winner"],
            "Team": teams[1 if extra_or_total_count == 2 else 0],
            "MatchInfo": temp[teams[1 if extra_or_total_count == 2 else 0]],
        }

        scorecard["Bowling"].append(player)

with open("scorecard.json", "w") as f:
    json.dump(scorecard, f)
