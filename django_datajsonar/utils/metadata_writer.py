#!coding=utf8
import csv

from xlsxwriter import Workbook


class CSVMetadataWriter:
    def __init__(self, output, headers):
        self.writer = csv.DictWriter(output, headers, extrasaction='ignore')

    def write_metadata(self, metadata_list):
        self.writer.writeheader()
        for catalog in metadata_list:
            self.writer.writerow(catalog)


class XLSXMetadataWriter:
    def __init__(self, output, headers):
        self.headers = headers
        self.workbook = Workbook(output, {'in_memory': True})

    def write_metadata(self, metadata_list):
        worksheet = self.workbook.add_worksheet()
        for column, header in enumerate(self.headers):
            worksheet.write(0, column, header)
        for row, catalog in enumerate(metadata_list):
            for column, field in enumerate(catalog.values()):
                worksheet.write(row + 1, column, field)
        self.workbook.close()
