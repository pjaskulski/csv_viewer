import requests

# import data from World Bank’s Climate Data API, yearly average of temperature for selected country
from PyQt5.QtWidgets import QMessageBox


def import_data_climate():
    temp_type = 'tas'  # tas = temperature at surface
    file_type = 'csv'  # csv = comma separated file
    country_iso = 'POL'  # ISO code, POL = Poland

# error code
    err_code = {200: "OK, The request has succeeded.",
                204: "No Content. The server has completed the request, but doesn’t need to return any data.",
                400: "Bad Request. The request is badly formatted.",
                401: "Unauthorized. The request requires authentication.",
                404: "Not Found. The requested resource could not be found.",
                408: "Timeout. The server gave up waiting for the client.",
                418: "I’m a teapot. No, really",
                500: "Internal Server Error	An error occurred in the server."
                }

    address = 'http://climatedataapi.worldbank.org/climateweb/rest/v1/country/cru/' + \
              f'{temp_type}/year/{country_iso}.{file_type}'

    resp = requests.get(address)
    if resp.status_code != 200:
        return False, f"{resp.status_code}: Failed to get data:\n {err_code[resp.status_code]}"
    else:
        return True, resp.text