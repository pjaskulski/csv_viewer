#! /usr/bin/env python3

import sys
import argparse
from PyQt5.QtWidgets import QApplication
from mainwindow import MainWindow


sep_type = {'comma':',', 'semicolon':';', 'tab':'\t'}
dec_type = {'dot':'.', 'comma':','}

app = QApplication(sys.argv)
window = MainWindow("CSV Viewer")

# parse command line arguments if present
if len(sys.argv) > 1:
    parser = argparse.ArgumentParser("python csv_viewer.py")
    parser.add_argument('-p', action='store', dest='path', required=True,
                        help='Path to CSV file')
    parser.add_argument('-s', action='store', dest='separator', required=True,
                        help='Separator: comma, semicolon or tab')
    parser.add_argument('-d', action='store', dest='decimal', required=False,
                        help='Decimal point: dot or comma')
    results = parser.parse_args()
    if results.path != "" and results.separator in sep_type and results.decimal in dec_type:
        window.open_csv_file(results.path,
                             sep_type[results.separator],
                             dec_type[results.decimal])
    else:
        print("Invalid parameters. Run csv_view with -h option to help.")

window.show()
sys.exit(app.exec_())
