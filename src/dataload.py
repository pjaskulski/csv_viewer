# DEMO address: import data from World Bank’s Climate Data API, yearly average of temperature for selected country
# address: 'http://climatedataapi.worldbank.org/climateweb/rest/v1/country/cru/tas/year/POL.csv'
# tas = temperature at surface
# csv = comma separated file
# ISO code, POL = Poland

import requests


def import_data_by_api(address: str):

    try:
        resp = requests.get(address)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        return False, "Http Error: " + str(errh)
    except requests.exceptions.ConnectionError as errc:
        return False, "Error Connecting: " + str(errc)
    except requests.exceptions.Timeout as errt:
        return False, "Timeout Error: " + str(errt)
    except requests.exceptions.RequestException as err:
        return "Error: " + str(err)

    return True, resp.text
