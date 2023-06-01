import gspread
from google.auth.exceptions import TransportError
from oauth2client.service_account import ServiceAccountCredentials
import requests
import time
from bs4 import BeautifulSoup

import cloudscraper
from urllib3.exceptions import MaxRetryError, NewConnectionError


def get_company_info(siret):
    siret = siret.replace(" ", "")
    url = f"https://www.pappers.fr/recherche?q={siret}"

    scraper = cloudscraper.create_scraper()

    response = scraper.get(url).text


    soup = BeautifulSoup(response, "html.parser")

    h1 = soup.find_all("h1")
    siretStatus = soup.find_all("span", {"class": "status"})

    company_name = "UNKNOWN"
    company_status = "UNKNOWN"

    if len(h1):
        company_name = h1[0].get_text().strip()

        splited = company_name.split("(")
        company_name = splited[0] if len(splited) else company_name

        company_name = company_name.strip()

    if len(siretStatus):
        company_status = siretStatus[0].get_text().strip()

        splitedStatus = company_status.split("depuis")
        company_status = splitedStatus[0] if len(splitedStatus) else company_status

        company_status = company_status.strip()

    return company_name, company_status

def get_update_sheet(sheet, i, siret_number, delay=30):
    try:
        saved_name = sheet.cell(i, 2).value
        saved_status = sheet.cell(i, 3).value

        print(f" save name {saved_name} status {saved_status}")

        if saved_name == None:
            company_name, company_status = get_company_info(siret_number)
            sheet.update_cell(i, 2, company_name)
            sheet.update_cell(i, 3, company_status)
            time.sleep(5)
        else:
            print("Ignorer....")
            time.sleep(1)

    except gspread.exceptions.APIError as e:
        print("Limite de quota atteinte. Le requette reprend dans une (1) minutes. Merci de patienter")
        time.sleep(61)

    except requests.exceptions.ConnectionError:
        print(f"La connexion a été perdue. Reconnexion dans {delay} secondes.....")
        # attente de delay seconde puis on essaye
        time.sleep(delay)
        get_update_sheet(sheet, i, siret_number, delay)
    except ConnectionError:
        print(f"La connexion a été perdue. Reconnexion dans {delay} secondes.....")
        # attente de delay seconde puis on essaye
        time.sleep(delay)
        get_update_sheet(sheet, i, siret_number, delay)

    except ConnectionAbortedError:
        print(f"La connexion a été avorté. Reconnexion dans {delay} secondes.....")
        # attente de delay seconde puis on essaye
        time.sleep(delay)
        get_update_sheet(sheet, i, siret_number, delay)
    except ConnectionRefusedError:
        print(f"La connexion a été refusé par l'hôte. Reconnexion dans {delay} secondes.....")
        # attente de delay seconde puis on essaye
        time.sleep(delay)
        get_update_sheet(sheet, i, siret_number, delay)
    except ConnectionResetError:
        print(f"La connexion a été reinitialisé. Reconnexion dans {delay} secondes.....")
        # attente de delay seconde puis on essaye
        time.sleep(delay)
        get_update_sheet(sheet, i, siret_number, delay)

    except MaxRetryError:
        print(f"Le nombre d'essai maximale a été atteinte. Reconnexion dans {delay} secondes.....")
        # attente de delay seconde puis on essaye
        time.sleep(delay)
        get_update_sheet(sheet, i, siret_number, delay)
    except:
        print(f"Erreur générale. Reconnexion dans {delay} secondes.....")
        # attente de delay seconde puis on essaye
        time.sleep(delay)
        get_update_sheet(sheet, i, siret_number, delay)



if __name__ == "__main__":

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

    for i, siret_number in enumerate(siret_numbers, start=1):
        get_update_sheet(sheet, i, siret_number, 30)


