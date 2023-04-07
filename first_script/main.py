import sys
import os
import argparse
import time

if os.path.abspath('.') not in sys.path:
    sys.path.append(os.path.abspath('.'))

from json_handler import handler
from linkedin_scrapper import scrapper
from email_validator import validator
from organigramm import organigramm
from pdf_generator import generator

# # Define argument parser and parse arguments from console
# parser = argparse.ArgumentParser(description='LinkedIn Scraper')
# parser.add_argument('name', type=str, help='Name of the company. Example: "Google"')
# # TODO: Mail pattern first.last firstlast first_last
# parser.add_argument('domain', type=str, help='Email domain of the company. Example: "first.last@gmail.com, flast@gmail.com"')
# parser.add_argument('-o', '--output', type=str, help='Output path. Example: "./output/"')
# parser.add_argument('-t', '--timeout', type=int, help='Timeout between requests. Example: 5')
# # Define wait time between requests - Done
# parser.add_argument('-j', '--jitter', type=int, help='Jitter between requests (Prevents bot detection). Example: 2')
# # TODO: Number of valid employees wanted
# parser.add_argument('-n', '--number', type=int, help='Number of employees to scrap. Example: 10')
# parser.add_argument('-c', '--candidates', type=int, help='Number of candidates for phishing to select. Example: 10')
# # TODO: Select between O365 and Gmail
# parser.add_argument('-m', '--mail-provider', type=str, help='Mail provider against which the emails will be validated. Values: "Google" or "O365"')
# parser.add_argument('-p', '--pdf', action='store_true', help='Generate PDF file')
# parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
# parser.add_argument('-d', '--directors-board', action='store_true', help='Select all the positions from [Owner, Director, Manager, Administrative, HHRR, Collaborator] you want to print in the report. Example: "Owner, Director, Manager"', default='Owner, Director, Manager')
# args = parser.parse_args()

# Start the script execution 
name, domain, output_folder, timeout, jitter, n, c, directors_board = 'uah','uah.es','output', 15, 0, 0, 10, ['Owner','Director', 'Manager'] # TODO: Obtain these from parameters
id = round(time.time())
print('[+] Starting script execution with id: {}'.format(id))

# Define and parse parameters to inputs for the first sub-script
meta = {'_descriptor':'meta','id':id}
inputs = {'_descriptor':'input','name':name}
output = {'_descriptor':'output'}
# Save the inputs for the first sub-script
handler.write_json('data/scrapper-{}.json'.format(id), meta, inputs, output)

# Execute the first sub-script
scrapper.start('data/scrapper-{}.json'.format(id), timeout=timeout, jitter=jitter, n_employees=n)

# Transfer output from the scrapper to the email validator
meta, _, outputs = handler.read_json('data/scrapper-{}.json'.format(id))
inputs = {'_descriptor':'input','employees':outputs['employees'],'domain':domain}
output = {'_descriptor':'output'}
# Save the inputs for the email validator
handler.write_json('data/validator-{}.json'.format(id), meta, inputs, output)

# Execute the email validator
validator.start('data/validator-{}.json'.format(id))

# Obtain the output from the email validator
meta, _, outputs = handler.read_json('data/validator-{}.json'.format(id))

# Save a copy of all validated employees in a csv file
headers, rows = handler.json_to_csv(outputs['employees'])
handler.write_csv('output/employees-{}.csv'.format(id), rows, headers, separator=';')
print('[+] Saved all validated employees to output/employees-{}.csv'.format(id))

# Transfer output from the email validator to the organigramm
inputs = {'_descriptor':'input','employees':outputs['employees']}
output = {'_descriptor':'output'}

# Save the inputs for the organigramm script
handler.write_json('data/organigramm-{}.json'.format(id), meta, inputs, output)

# Execute the organigramm script
organigramm.start('data/organigramm-{}.json'.format(id), output_folder)

# Select n best candidates for phishing from the organigramm
meta, _, outputs = handler.read_json('data/organigramm-{}.json'.format(id))

# TODO: Modularize the following loop in a method
candidates = []
employee_hierarchy = outputs['organigramm']['employees']
positions = list(employee_hierarchy.keys())
while len(candidates) < c and len(positions) > 0:
    for candidate in employee_hierarchy[positions.pop(0)][1]:
        if candidate not in candidates:
            candidates.append(candidate)
        if len(candidates) == c:
            break
    
# Save the results
inputs = {'_descriptor':'input','name':name,'domain':domain}
output = {'_descriptor':'output','organigramm':outputs['organigramm'],'candidates':candidates}

# Generate the final report with the results of the main script
handler.write_json('data/report-{}.json'.format(id), meta, inputs, output)

# Generate a pdf report with the results of the main script
PDFGenerator = generator.PDFGenerator('./')
PDFGenerator.set_template('templates/osint_report.html')
print('[+] Script execution with id: {} finished. Generating PDF report...'.format(id))

# Dentro de pdf:
#  TODO: Descripcion de la empresa - LinkedIn
#  TODO: Datos sobre la empresa (telefono, direccion...)

target = {'name':name, 'domain':domain}

# TODO: Get the description and data from LinkedIn
target['title'] = 'LinkedIn title'
target['description'] = 'LinkedIn description'
target['data'] = {
    'phone': '123456789',
    'address': 'Calle 123',
    'city': 'Madrid',
    'country': 'Spain',
}


# Filter organigramm to table of directors
stripped_organigramm = output['organigramm']
stripped_organigramm['employees'] = {k:v for k,v in stripped_organigramm['employees'].items() if k in ['Owner','Director', 'Manager']} # TODO: change this to directors_board

pdf_path = 'output/report-{}.pdf'.format(id)
context = {'target':target, 'organigramm':stripped_organigramm, 'candidates':output['candidates']}
if PDFGenerator.generate(context, pdf_path):
    print('[+] Check the PDF report generated at {}'.format(pdf_path))
else:
    print('\n[-] PDF report could not be generated. Still, your results are saved in data/report-{}.json'.format(id))