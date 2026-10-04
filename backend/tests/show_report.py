"""Print the wording of the sample report, so it can be read and reviewed.

Run from the backend folder:
    .venv\\Scripts\\python -X utf8 -m tests.show_report        (English)
    .venv\\Scripts\\python -X utf8 -m tests.show_report hi     (Hindi)

To save it to a file for the astrologer, add:  > report_hi.txt
"""

import sys

from app.report import build_report
from tests.darak_sample import BIRTH


def main(lang):
    report = build_report(**BIRTH, gender="male", surname="Darak", kuldevi="Ashapura Mata")
    content = report["content"]

    def heading(title):
        print(f"\n===== {title} =====")

    heading("YOGAS")
    for y in content["yogas"]:
        print(f"- {y['name'][lang]}\n    {y['formation'][lang]}\n    {y['result'][lang]}")

    heading("DOSHAS")
    for d in content["doshas"]:
        print(f"- {d['name'][lang]} [{d['status_label'][lang]}]\n    {d['details'][lang]}")

    heading("KEY ASPECTS")
    for line in content["aspects"]:
        print(f"- {line[lang]}")

    heading("DIVISIONAL CHARTS")
    for line in content["vargas"]:
        print(f"- {line[lang]}")

    heading("HOUSES")
    for h in content["houses"]:
        print(f"- {h['house']}. {h['name'][lang]} - {h['sign'][lang]}\n    {h['text'][lang]}")

    heading("PLANETARY STRENGTH")
    for group in content["strength"].values():
        planets = "; ".join(f"{p['planet'][lang]} ({p['reasons'][lang]})" for p in group["planets"])
        print(f"- {group['label'][lang]}: {planets}")

    heading("DASHA")
    for d in content["dasha"]:
        print(f"- {d['lord'][lang]} ({d['from'][lang]} - {d['to'][lang]}, age {d['age_from']}-{d['age_to']})"
              f"\n    {d['text'][lang]}")

    heading("LIFE PREDICTIONS")
    for p in content["predictions"]:
        print(f"- {p['title'][lang]}\n    {p['text'][lang]}")

    heading("REMEDIES")
    for r in content["remedies"]:
        print(f"- {r['for'][lang]}: {r['text'][lang]}")

    heading("SANSKAR CALENDAR")
    for s in content["sanskar"]:
        print(f"- {s['name'][lang]}: {s['when'][lang]}\n    {s['note'][lang]}")

    heading("LUCKY FACTORS")
    lucky = content["lucky"]
    for key in ("days", "colours", "metal", "direction", "deity"):
        print(f"- {key}: {lucky[key][lang]}")
    print(f"- numbers: {lucky['numbers']}\n- mantras: {' · '.join(lucky['mantras'])}")

    heading("NAME LETTERS AND NAMES")
    names = content["names"]
    print(f"- first letter: {names['primary'][lang]}")
    print(f"- nakshatra letters: {', '.join(x[lang] for x in names['nakshatra'])}")
    print(f"- rashi letters: {', '.join(x[lang] for x in names['rashi'])}")
    for n in names["suggestions"]:
        num = n["numerology"]
        full = f", with surname {num['full_name']['compound']} -> {num['full_name']['number']}" if num["full_name"] else ""
        print(f"- {n['en']} / {n['hi']}: {n['meaning'][lang]} "
              f"[{num['compound']} -> {num['number']}{full}] {'*' * num['stars']}")
    print(f"  {names['note'][lang]}")

    heading("NUMEROLOGY")
    num = content["numerology"]
    print(f"- Mulank {num['mulank']['number']}: {num['mulank']['text'][lang]}")
    print(f"- Bhagyank {num['bhagyank']['number']}: {num['bhagyank']['text'][lang]}")
    print(f"- {num['combination'][lang]}")
    print(f"- Kua {num['kua']['number']}: {num['kua']['element'][lang]}, {num['kua']['group'][lang]}. "
          f"{num['kua']['advice'][lang]}")
    for item in num["lo_shu_present"]:
        print(f"- {str(item['number']) * item['count']}: {item['text'][lang]}")
    for item in num["lo_shu_missing"]:
        print(f"- missing {item['number']}: {item['effect'][lang]} -> {item['remedy'][lang]}")

    heading("SUMMARY")
    print(content["summary"]["astrologer_note"][lang])
    print("Strongest areas:", ", ".join(a[lang] for a in content["summary"]["strongest_areas"]))
    print(content["general"]["disclaimer"][lang])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "en")
