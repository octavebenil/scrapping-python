import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
import time

def get_company_info(siret):
    url = f"https://www.pappers.fr/entreprise/{siret}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get company name

    print(soup)

    company_name_tag = soup.find('h1')

    print(company_name_tag)


    company_name = company_name_tag[0].text.strip() if company_name_tag else "UNKNOWN"



    # Check for active company
    active_company = soup.find('div', {'class': 'company-status'})
    if active_company and 'Active' in active_company.text:
        company_status = 'YES'
    elif active_company and 'Radiée depuis le' in active_company.text:
        company_status = 'NO'
    else:
        company_status = 'UNKNOWN'

    print(f"Company name {company_name} status {company_status}")
    return company_name, company_status

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Let's get Google Sheets in on the action
    # scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
    #          "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    #
    # # Point this to your Google Sheets API JSON file. Don't leave your keys under the doormat!
    # creds = ServiceAccountCredentials.from_json_keyfile_name("/Users/nico_isrd/Desktop/cap-forma-siret.json", scope)
    # client = gspread.authorize(creds)
    #
    # # Open up your Google Sheet. Make sure you replace "siret numbers" with your actual sheet name
    # sheet = client.open("siret numbers").sheet1
    #
    # # Get all SIRET numbers from the first column
    # siret_numbers = sheet.col_values(1)

    # Loop through each SIRET number
    get_company_info("37876982200024")
    # for i, siret_number in enumerate(siret_numbers, start=2):
    #     # Get the company info
    #     company_name, company_status = get_company_info(siret_number)
    #
    #     # Write the company name to the Google Sheet
    #     sheet.update_cell(i, 2, company_name)
    #
    #     # Write the company status to the Google Sheet
    #     sheet.update_cell(i, 3, company_status)
    #
    #     # Pause for 1 second to avoid exceeding the Google Sheets API usage limits
    #     time.sleep(1)