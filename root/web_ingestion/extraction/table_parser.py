from bs4 import BeautifulSoup


def parse_tables(html: str):
    soup = BeautifulSoup(html, "html.parser")
    tables = []

    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if cells:
                rows.append(cells)
        if rows:
            tables.append(rows)

    return tables
