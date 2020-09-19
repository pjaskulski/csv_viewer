# CSV_viewer
CSV files viewer.
 
App reads local csv files as data frame (thanks to pandas), downloads csv from internet by api, exports data to xlsx, sqlite, html, csv, markdown, deletes rows with missing values, shows summary and info about dataframe. 

## Requirement 
-   PyQt5
-   Python 3.x  
-   Pandas 
-   XlsWriter
-   SQLAlchemy
-   requests
-   argparse

## Command line usage: 

    python csv_viewer.py [-h] -p PATH -s SEPARATOR -d DECIMAL

    optional arguments:
        -h, --help    show this help message and exit
        -p PATH       Path to CSV file
        -s SEPARATOR  Separator: comma, semicolon or tab
        -d DECIMAL    Decimal point: dot or comma
    
    example:
        python csv_viewer.py -p small_data.csv -s comma -d dot 

## Screenshots:

![Screen](/doc/csv_viewer.png)

![Screen](/doc/csv_viewer2.png)

![Screen](/doc/csv_viewer3.png)

![Screen](/doc/csv_viewer4.png)

![Screen](/doc/csv_viewer5.png)

![Screen](/doc/csv_viewer6.png)

![Screen](/doc/csv_viewer7.png)