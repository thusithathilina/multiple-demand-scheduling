import inputs as P
from csv import reader


def main(lookup_file):
    lookup = []
    with open(lookup_file, 'rb') as csvfile:
        spamreader = reader(csvfile, delimiter=',', quotechar='|')

        for row in spamreader:
            lookup_row = map(float, row)
            # lookup_row = ', '.join(row)
            lookup.append(lookup_row)

    P.lookup_base = lookup
    return lookup
