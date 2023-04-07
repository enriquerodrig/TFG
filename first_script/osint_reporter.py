import sys
import os
import argparse
import time

path = os.path.dirname(__file__)
deps = os.path.join(path,'dependencies')
if path not in sys.path or deps not in sys.path:
    sys.path.append(path)
    sys.path.append(deps)

from json_handler import handler
from linkedin_scrapper import scrapper
from e_validator import validator
from organigramm import organigramm
from pdf_generator import generator

# Define argument parser and parse arguments from console
parser = argparse.ArgumentParser(description='OSINT Company Reporter')
parser.add_argument('name', type=str, help='Name of the company. Example: "Google"')
parser.add_argument('domain', type=str, help='Email domain of the company. Example: "first.last@gmail.com, flast@gmail.com"')
parser.add_argument('-o', '--output', type=str, help='Output path. Example: "./output/"', default='./output/')
parser.add_argument('-t', '--timeout', type=int, help='Timeout between requests. Example: 5', default=5)
parser.add_argument('-j', '--jitter', type=int, help='Jitter between requests (Prevents bot detection). Example: 2', default=2)
parser.add_argument('-n', '--number', type=int, help='Number of employees to scrap. Example: 10', default=None)
parser.add_argument('-c', '--candidates', type=int, help='Number of candidates for phishing to select. Example: 10', default=10)
parser.add_argument('-m', '--mail-provider', type=str, help='Mail provider against which the emails will be validated. Values: "gmail" or "o365"', default='Any', choices=['any', 'google', 'o365'])
parser.add_argument('-d', '--directors-board', type=str, help='Select all the positions from [Owner, Director, Manager, Administrative, HHRR, Collaborator] you want to print in the report. Example: "Owner, Director, Manager"', default='Owner, Director, Manager')
parser.add_argument('-k', '--keywords', type=str, help='Keywords to select the candidates for phishing. Example "CEO, CTO, Owner, Director"', default='CEO, CTO, Owner, Director')
parser.add_argument('-p', '--pdf-template', type=str, help='Path to the pdf template. Example: "./pdf_generator/templates/osint_report.html"', default='./pdf_generator/templates/osint_report.html')
parser.add_argument('--data-folder', type=str, help='Path to the data folder. Example: "./data"', default='/tmp/osint_reporter')
parser.add_argument('--username', type=str, help='Username for the mail provider. Example: "test@protonmail.com"', default=None)
parser.add_argument('--password', type=str, help='Password for the mail provider. Example: "password"', default=None)
args = parser.parse_args()


def setup_script(output_folder, keywords, directors_board, data_folder='./data/'):
    """
    Setup the script execution initializing the data and output folders
    :param output_folder: Output folder path
    :param keywords: Keywords to select the candidates for phishing
    :param directors_board: Select all the positions from [Owner, Director, Manager, Administrative, HHRR, Collaborator] you want to print in the report
    :param data_folder: Path to the temporal data folder
    :return: None. Global variable id is set
    """
    # Start the script execution 
    id = round(time.time())
    print('[+] Starting script execution with id: {}'.format(id))

    # Create data and output folders if they don't exist
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Parse lists from arguments
    keywords = [keyword.strip() for keyword in keywords.split(',')]
    directors_board = [director.strip() for director in directors_board.split(',')]

    return id, keywords, directors_board

def run_scrapper(id, name, timeout, jitter, n_employees, data_folder='./data/', username=None, password=None):
    """
    Set up input data for linkedin scrapper and execute it
    :param id: Script execution id
    :param name: Name of the company
    :param timeout: Timeout between requests
    :param jitter: Jitter between requests
    :param n_employees: Number of employees to scrap
    :param data_folder: Path to the temporal data folder
    :return: None
    """
    # Define and parse parameters to inputs for the first sub-script
    meta = {'_descriptor':'meta','id':id}
    inputs = {'_descriptor':'input','name':name}
    output = {'_descriptor':'output'}

    # Save the inputs for the first sub-script
    handler.write_json('{}/scrapper-{}.json'.format(data_folder,id), meta, inputs, output)

    # Execute the first sub-script
    scrapper.start('{}/scrapper-{}.json'.format(data_folder,id), timeout=timeout, jitter=jitter, n_employees=n_employees, username=username, password=password)

def run_validator(id, domain, mail_provider, data_folder='./data/'):
    """
    Set up input data for email validator and execute it
    :param id: Script execution id
    :param domain: Email domain of the company
    :param mail_provider: Mail provider against which the emails will be validated
    :param data_folder: Path to the temporal data folder
    :return: None
    """
    # Define and parse parameters to inputs for the second sub-script
    meta, _, outputs = handler.read_json('{}/scrapper-{}.json'.format(data_folder,id))
    inputs = {'_descriptor':'input','employees':outputs['employees'],'domain':domain, 'mail_provider':mail_provider}
    output = {'_descriptor':'output'}

    # Save the inputs for the second sub-script
    handler.write_json('{}/validator-{}.json'.format(data_folder, id), meta, inputs, output)

    # Execute the second sub-script
    validator.start('{}/validator-{}.json'.format(data_folder, id))

def run_organigramm(id, output_folder, data_folder='./data/'):
    """
    Set up input data for organigramm and execute it
    :param id: Script execution id
    :param output_folder: Output folder path
    :param data_folder: Path to the temporal data folder
    :return: None
    """
    # Obtain the output from the email validator
    meta, _, outputs = handler.read_json('{}/validator-{}.json'.format(data_folder,id))

    # Transfer output from the email validator to the organigramm
    inputs = {'_descriptor':'input','employees':outputs['employees']}
    output = {'_descriptor':'output'}

    # Save the inputs for the organigramm script
    handler.write_json('{}/organigramm-{}.json'.format(data_folder,id), meta, inputs, output)
    # Execute the organigramm script
    organigramm.start('{}/organigramm-{}.json'.format(data_folder,id), output_folder)


def select_ordered(employees, c, candidates):
    """
    Select at most c best candidates for phishing based on organisational hierarchy
    :param employees: Dictionary of employees sorted by position
    :param c: Number of candidates to select
    :param candidates: List of already selected candidates
    :return: List of candidates for phishing
    """
    positions = sorted(employees.keys(), key=lambda x: employees[x][0], reverse=True)
    while len(candidates) < c and len(positions) > 0:
        position = positions.pop(0)
        candidates += employees[position][1]

    return candidates[:c]

def select_candidates(c, employees, keywords):
    """
    Select at most c best candidates for phishing based on the selected keywords
    :param c: Number of candidates to select
    :param employees: Dictionary of employees sorted by position
    :param keywords: List of keywords to select the candidates
    :return: List of candidates for phishing
    """
    # Select the best candidates for phishing based on the keywords
    candidates = []
    for key in keywords:
        position = organigramm.classify_position(key)
        if position in employees:
            candidates += employees[position][1]

        if len(candidates) >= c:
            candidates = candidates[:c]
            break

    if len(candidates) < c:
        print('[!] Couldn\'t find enough candidates for phishing. Only {} candidates found.'.format(len(candidates)))
        print('[!] Adding candidates based on authority...')
        candidates = select_ordered(employees, c, candidates)
    
    return candidates
    
def generate_report(id, organigramm, candidates, directors_board, template, output_folder, data_folder='./data/'):
    """
    Generate the final report with the results of the main script
    :param id: Script execution id
    :param organigramm: Organigramm of the company
    :param candidates: List of candidates for phishing
    :param output_folder: Output folder path
    :param data_folder: Path to the temporal data folder
    :return: None
    """
    # Save the results
    inputs = {'_descriptor':'input','name':args.name,'domain':args.domain}
    output = {'_descriptor':'output','organigramm':organigramm,'candidates':candidates}

    # Generate the final report with the results of the main script
    handler.write_json('{}/report-{}.json'.format(data_folder,id), meta, inputs, output)
    
    PDFGenerator = generator.PDFGenerator('./')
    PDFGenerator.set_template(template)
    print('[+] Script execution with id: {} finished. Generating PDF report...'.format(id))

    target = inputs
    # TODO: Get the description and data from LinkedIn
    # target['title'] = 'LinkedIn title'
    # target['description'] = 'LinkedIn description'
    # target['data'] = {
    #     'phone': '123456789',
    #     'address': 'Calle 123',
    #     'city': 'Madrid',
    #     'country': 'Spain',
    # }

    # Filter organigramm to table of directors
    organigramm['employees'] = {k:v for k,v in organigramm['employees'].items() if k in directors_board}

    pdf_path = output_folder+'/report-{}.pdf'.format(id)
    context = {'target':inputs, 'organigramm':organigramm, 'candidates':candidates, 'directors_board':directors_board, 'keywords':args.keywords}
    PDFGenerator.generate(context, pdf_path)
    print('[+] Check the PDF report generated at {}'.format(pdf_path))

if __name__ == '__main__':
    id,keywords,directors_board = setup_script(args.output, args.keywords, args.directors_board, args.data_folder)

    try:
        # Execute the linkedin scrapper
        run_scrapper(id, args.name, args.timeout, args.jitter, args.number, args.data_folder, args.username, args.password)

        # Execute the mail validator
        run_validator(id, args.domain, args.mail_provider, data_folder=args.data_folder)

        # Execute the organigramm script
        run_organigramm(id, args.output, data_folder=args.data_folder)
        
        # Select n best candidates for phishing from the organigramm
        print('[+] Obtaining the organization chart of {}...'.format(args.name))
        meta, _, outputs = handler.read_json('{}/organigramm-{}.json'.format(args.data_folder,id))
        print('[+] Selecting the {} best candidates for phishing...'.format(args.candidates))
        candidates = select_candidates(employees=outputs['organigramm']['employees'], c=args.candidates, keywords=keywords)


        try:
            # Generate the final report
            generate_report(id, outputs['organigramm'], candidates, directors_board, args.pdf_template, args.output, data_folder=args.data_folder)
        except Exception as e:
            print('\n[-] PDF report could not be generated. Still, your results are saved in {}}/report-{}.json'.format(args.data_folder,id))
            print('[-] Error: {}'.format(e))

        # Save a copy of all validated employees in a csv file
        _,_,outputs = handler.read_json('{}/validator-{}.json'.format(args.data_folder,id))
        headers, rows = handler.json_to_csv(outputs['employees'])
        handler.write_csv('{}/employees-{}.csv'.format(args.output,id), rows, headers, separator=';')
        print('[+] Saved all validated employees to {}/employees-{}.csv'.format(args.output,id))
    except KeyboardInterrupt as e:
        print('\n[!] Script interrupted by the user. Exiting...')
        print('[!] Your results are saved at {} under the id {}'.format(args.data_folder,id))
    except Exception as e:
        print('\n[!] Script execution failed. Exiting...')
        print('[!] Error: {}'.format(e))
        print('[!] Check the logs at {} under the id {}'.format(args.data_folder,id))