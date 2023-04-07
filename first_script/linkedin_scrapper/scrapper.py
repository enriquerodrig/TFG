from json_handler import handler
import dependencies.crosslinked as crosslinked
import dependencies.linkedin2username.linkedin2username as li2u

def count_users_per_search_engine(se_dict):
        for search_engine in se_dict:
            print('[+] {} users found in {} search engine'.format(len(se_dict[search_engine]), search_engine))

def search_crosslinked(search_engines, target, timeout, jitter, n_employees=None):
    """
    Search for employees of the target company using crosslinked library
    :param search_engines: List of search engines to use, select from {'google', 'bing'}
    :param target: String with the name of the target company
    :param timeout: Timeout for each request
    :return: Dictionary with users found in each search engine. Each user
    contains the following fields: 'fname', 'lname', 'title', 'url', 'text'
    """
    users = {} # Auxiliar dictionary, stores users per search engine
    user_count = 0 # Counter of users found
    # Search for employees in each search engine
    for search_engine in search_engines:
        print('[+] Searching for {} in {}...'.format(target, search_engine))
        # Define a scrapper for the search engine
        scrapper = crosslinked.CrossLinked(search_engine=search_engine,target=target,timeout=timeout, jitter=jitter, n_targets=n_employees)
        # Parse links using crosslinked and store user data in users[search_engine]
        users[search_engine] = scrapper.search()
        user_count += len(users[search_engine])
        if n_employees and user_count >= n_employees:
            break
    return users

def scrap_employees_anon(target, timeout, jitter, n_employees=None):
    """
    Main function, sets up the scrapper and prepares the output
    :param target: String with the name of the target company
    :param timeout: Timeout for each request
    :param jitter: Jitter for each request
    :param n_employees: Number of employees to scrap
    :return: List of employees, each employee is a dictionary with the following fields:
    'fname', 'lname', 'position'
    """
    search_engines = ['google','bing'] # Available search engines for scrapping
    employees = [] # List of employees, final output

    # Obtain users through web scrapping
    users_se = search_crosslinked(search_engines, target, timeout=timeout, jitter=jitter, n_employees=n_employees)

    count_users_per_search_engine(users_se)
    
    # Store needed information in employees list
    for search_engine in users_se:
        for user in users_se[search_engine]:
            employee = {
                'fname': user['fname'],
                'lname': user['lname'],
                'position': user['title'],
            }
            if employee not in employees:
                employees.append(employee)
    return employees

def scrap_employees(company, session, jitter=0, n_employees=None):
    """
    Sets up the scrapper and search for employees of the target company
    :param company: String with the name of the target company
    :param session: Requests session
    :param jitter: Jitter for each request
    :param n_employees: Number of employees to scrap
    :return: List of employees, each employee is a dictionary with the following fields:
    'full_name','fname', 'lname', 'position'
    """
    # Get basic company info
    print('[*] Trying to get company info...')
    company_id, staff_count = li2u.get_company_info(company, session)

    # Define inner and outer loops
    print("[*] Calculating inner and outer loops...")
    depth, geoblast = li2u_set_ineer_loops(staff_count=staff_count)
    outer_loops = li2u.set_outer_loops(geoblast=geoblast)

    # Start searching for employees
    print("[*] Starting scrapping for employees...")
    employees = li2u.do_loops(session=session, company_id=company_id, outer_loops=outer_loops, geoblast=geoblast, depth=depth, jitter=jitter, needed_employees=n_employees)
    return employees

def li2u_set_ineer_loops(staff_count):
    """
    Set simplified inner loops for li2u, without keyword search
    :param staff_count: Number of employees in the company
    :return: Tuple with the number of inner loops and a boolean indicating if geoblast should be used
    """
    loops = int((staff_count / 25) + 1)
    print(f"[*] Company has {staff_count} profiles to check on {loops} loops. Some may be anonymous.")
    return loops, staff_count > 1000 # If company has more than 1000 employees, use geoblast to avoid IP ban

def start(input_filename, timeout=15, jitter=0, n_employees=None, username=None, password=None):
    """
    Start scrapping for employees
    :param input_filename: String with the name of the input file
    :param timeout: Timeout for each request
    :param jitter: Jitter for each request
    :param n_employees: Number of employees to scrap
    :return: None
    """
    # Obtain inputs and output template
    meta, inputs,outputs = handler.read_json(input_filename)
    target = inputs['name']

    anon_scrapping = True
    # Login into linkedin
    if username and password:
        print('[+] Username and password provided. Logging into linkedin...')
        session = li2u.login(username, password)
        # Scrap employees using li2u
        if session:
            print('[+] Login successful. Starting scrapping for employees...')
            employees = scrap_employees(target, session, jitter, n_employees)
            anon_scrapping = False
        else:
            print('[!] Login failed. Using anonymous scrapping to continue the script...')

    # Start scrapping for employees
    if anon_scrapping:
        print('[+] Starting anonymous scrapping for employees...')
        employees = scrap_employees_anon(target, timeout, jitter, n_employees)

    # Write results and finish script
    print('[+] {} unique employees found'.format(len(employees)))
    outputs['employees'] = employees
    print('[+] Script completed. Writing output to {}...'.format(input_filename))
    handler.write_json(input_filename, meta, inputs, outputs)

if __name__ == '__main__':
    # Obtain inputs and output template
    filename = 'data.json'
    start(filename, n_employees=10)