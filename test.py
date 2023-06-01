import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import time
from bs4 import BeautifulSoup

import cloudscraper


def get_company_info(siret):
    siret = siret.replace(" ", "")
    url = f"https://www.pappers.fr/recherche?q={siret}"

    scraper = cloudscraper.create_scraper()

    response = scraper.get(url).text

    soup = BeautifulSoup(response, "html.parser")

    h1 = soup.find_all("h1", {"class": "big-text"})
    siretStatus = soup.find_all("span", {"class": "status"})

    company_name = "UNKNOWN"
    company_status = "UNKNOWN"

    if len(h1):
        company_name = h1[0].text.strip()

    if len(siretStatus):
        company_status = siretStatus[0].get_text().strip()

    return company_name, company_status


def get_company_info_limited(siret):
    siret = siret.replace(" ", "")
    url = f"https://suggestions.pappers.fr/v2?q={siret}&longueur=10&cibles=siret"
    response = requests.get(url)
    res = response.json()
    company_name = "UNKNOWN"
    company_status = "UNKNOWN"
    if res.get("resultats_siret"):
        for company in res.get("resultats_siret"):
            c_siret = company.get("siege").get("siret")
            c_mention = company.get("mention").split("</em>")
            c_mention = c_mention[0].replace("<em>", "") if len(c_mention) else ""
            if c_siret == siret or c_mention == siret:
                company_name = company.get("nom_entreprise")
                company_status = company.get("statut_rcs")
                break  # Stop searching after finding a matching company
    return company_name, company_status


scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name("cred.json", scope)
client = gspread.authorize(creds)

sheet = client.open("siret numbers").sheet1

siret_numbers = sheet.col_values(1)

company_name, company_status = get_company_info("37876982200024")

print(f"name {company_name} status {company_status}")


company_name, company_status = get_company_info("41506828700051")

print(f"name {company_name} status {company_status}")
# for i, siret_number in enumerate(siret_numbers, start=1):
#     company_name, company_status = get_company_info(siret_number)
#     sheet.update_cell(i, 2, company_name)
#     sheet.update_cell(i, 3, company_status)
#     time.sleep(10)
