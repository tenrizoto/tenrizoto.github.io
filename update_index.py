import os
import json
from datetime import datetime
from bs4 import BeautifulSoup

ARTICLE_DIR = "article"
INDEX_FILE = "index.html"
DATA_FILE = "articles_data.json"

# Načtení uložených dat
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
else:
    saved_data = {}

articles = []

for filename in os.listdir(ARTICLE_DIR):
    if not filename.endswith(".html"):
        continue
    filepath = os.path.join(ARTICLE_DIR, filename)

    # zachování původního data vytvoření
    if filename in saved_data:
        created_date = saved_data[filename]["date"]
        ctime = saved_data[filename]["ctime"]
    else:
        ctime_val = os.path.getctime(filepath)
        created_date = datetime.fromtimestamp(ctime_val).strftime("%d-%m-%Y")
        ctime = ctime_val
        saved_data[filename] = {"date": created_date, "ctime": ctime}

    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        h3 = soup.find("h3")
        title = h3.text if h3 else filename.replace(".html", "")
        first_p = soup.find("p")
        prefix = first_p.text if first_p else ""

    articles.append({
        "filename": filename,
        "title": title,
        "prefix": prefix,
        "date": created_date,
        "ctime": ctime
    })

# Seřazení podle ctime (nejnovější nahoře)
articles.sort(key=lambda x: x["ctime"], reverse=True)

# Generování HTML pro index
section_html = '<section id="articles">\n<ul>\n'
for art in articles:
    link = f'?article={art["filename"].replace(".html","")}'
    section_html += f'<li><a href="{link}">{art["title"]}</a> <span class="date">{art["date"]}</span><br><p class="prefix">{art["prefix"]}</p></li>\n'
section_html += "</ul>\n</section>"

# Aktualizace index.html
with open(INDEX_FILE, "r", encoding="utf-8") as f:
    index_soup = BeautifulSoup(f, "html.parser")

old_section = index_soup.find("section", {"id": "articles"})
if old_section:
    old_section.replace_with(BeautifulSoup(section_html, "html.parser"))
else:
    index_soup.body.append(BeautifulSoup(section_html, "html.parser"))

with open(INDEX_FILE, "w", encoding="utf-8") as f:
    f.write(str(index_soup))

# Uložení dat o článcích
with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(saved_data, f, indent=2)
