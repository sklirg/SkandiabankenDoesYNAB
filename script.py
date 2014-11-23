# -*- coding: utf-8 -*-

# Python script for converting Skandiabanken CSV to YNAB import format

import sys, os
from datetime import date

files = os.listdir()
csv = []

for f in files:
    if f.lower().endswith('.csv') and f.lower() != 'new_trans.csv' and f[0].isnumeric():
        csv.append(f)

default = len(csv)-1

if default < 0:
    print('Found no csv files, exiting…')
    sys.exit(0)


# Let user decide from files in execution dir

print("Please select a file to process - default is last alphabetically")

for i in range(len(csv)):
    print("%1s %2s %25s" %
            ("*" if i == default else "", (i+1), csv[i][-25:]))

user_input = input('Select a file (leave empty for default): ')
if user_input.startswith('q') or user_input.startswith('e'):
    print('Quitting…')
    sys.exit(0)
elif user_input:
    if not user_input.isnumeric():
        print('I do not understand your input')
        sys.exit(0)
    if int(user_input)+1 > len(csv):
        print('Could not find that item')
        sys.exit(0)
    transactions = csv[int(user_input)-1]
else:
    transactions = csv[default]

print("Running conversion on %s" % transactions)

known_payees = {
    'BANK NORWE': 'Bank Norwegian',
    'BUNNPRIS M': 'Bunnpris Moholt',
    'BURGER KIN': 'Burger King',
    'CLAS OHLSO': 'Clas Ohlson',
    'REMA ELGES': 'Rema 1000 Elgeseter',
    'REMA MOHOL': 'Rema 1000 Moholt',
    'RIMI VALEN': 'Rimi Valentinlyst',
    'SIT STORKI': 'SiT Mat',
    'SIT KAFE S': 'SiT Mat',
    'VISMA COLL': 'OneCall',
    'SPOTIFY SP': 'Spotify',
}

new_lines = []
with open(transactions, 'r', encoding='utf-8') as f:
    # Data not needed
    f.readline()
    f.readline()
    f.readline()

    for line in f:
        transaction = line.strip()
        td = transaction.split(',')

        # Cleaning data
        for i in range(len(td)):
            td[i] = td[i].strip('"')

        if td[2] == "" or 'Varekj' in td[4]:
            #print('skipping')
            td[4] = ''
            td[3] = 'Not yet cleared'

        # Dict setup
        """
        trans_dict_keys = ('date', 'payee', 'category', 'memo', 'out', 'in')
        trans_dict = {}
        for key in trans_dict_keys:
            trans_dict[key] = ''
        """

        # Convert date-string
        plz = td[1].split('-')
        plz.reverse()
        td[1] = '/'.join(plz)

        # Find out what kind of transaction this is
        if 'Vare' in td[3]: # Varekjøp
            td[4] = td[4][6:]
        elif 'Visa' in td[3]: # Visa
            # Find end
            end = td[4].find("KURS:")
            li = td[4].split(' ')
            newli = []
            for i in range(4, len(li)):
                if li[i] == "KURS:":
                    break
                newli.append(li[i])
            td[4] = " ".join(newli)#[:td[4].find()]
        elif 'Giro' in td[3] or 'e-Faktura' in td[3]: # Giroer
            if 'melding' in td[3]:
                if 'Nettgiro' in td[4]:
                    td[4] = ''
                if 'NETTGIRO' in td[4]:
                    td[4] = td[4][14:]
                else:
                    td[4] = td[4][5:]
            elif 'KID' in td[3]:
                td[4] = td[4][5:]
            else:
                td[4] = td[4]

            # Find BETNR in transaction and remove it if it exists
            betnr = td[4].find('BETNR')
            if not betnr == -1:
                td[4] = td[4][:betnr-1]
        elif 'Avtale' in td[3]:
            td[4] = td[4][5:]
        elif ('Over' and 'sel') in td[3]: # Overførsel, eksterne banker
            td[4] = td[4][5:]
        elif ('Over' and 'ing') in td[3]: # Overføring, internt i skb
            if 'EGNE KONTI' in td[4]:
                td[3] = 'ToDo: Make transfer'
            td[4] = ''
        elif 'Omkostninger' in td[3]:
            td[4] = 'Skandiabanken'

        if td[4][:10] != "":
            if td[4][:10] in known_payees:
                td[4] = known_payees[td[4][:10]]

        # Format: date, payee, category, memo, outflow, inflow
        cleaned_data = "%s,%s,,%s,%s,%s" % (td[1], td[4], td[3], td[5], td[6])
        new_lines.append(cleaned_data)

    f.close()

outfile = 'new_trans.csv'
with open(outfile, 'w') as of:
    of.write('Date,Payee,Category,Memo,Outflow,Inflow\n')
    for new_line in new_lines:
        of.write(new_line + '\n')
    f.close()
#print('done')
print('Converted %s transactions' % len(new_lines))
