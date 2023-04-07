from json_handler import handler
import regex as re

def filter_owner(position):
    """
    Filter the owner of the company
    :param position: Position of the employee
    :returns: True if the employee is the owner of the company
    """
    position = position.lower()
    # English regex
    regex = r'owner|founder'
    # Spanish regex
    regex += r'|propietari|fundador|creador|dueñ'
    return re.search(regex, position)

def filter_director(position):
    """
    Filter the director of the company
    :param position: Position of the employee
    :returns: True if the employee is the director of the company
    """
    position = position.lower()
    # English regex
    regex = r'director|chief|president|head|principal|c[e|t|f|o|hr|s|g|a|m|d|o|i]o'
    # Spanish regex
    regex += r'|jefe|general'
    return re.search(regex, position)

def filter_administrative(position):
    """
    Filter the administrative employees of the company
    :param position: Position of the employee
    :returns: True if the employee is administrative
    """
    position = position.lower()
    # English regex
    regex = r'administrative|secretary|assistant|executive|notary|clerk'
    # Spanish regex
    regex += r'|secretaria|asistente|ejecutivo|notario|secretario'
    return re.search(regex, position)

def filter_manager(position):
    """
    Filter the supervisor employees of the company
    :param position: Position of the employee
    :returns: True if the employee is a supervisor
    """
    position = position.lower()
    # English regex
    regex = r'manager|leader|supervisor|coordinator'
    # Spanish regex
    regex += r'|gerente|lider|coordinador'
    return re.search(regex, position)

def filter_hhrr(position):
    """
    Filter the human resources employees of the company
    :param position: Position of the employee
    :returns: True if the employee is human resources
    """
    position = position.lower()
    # English regex
    regex = r'human resources|recruitment|hr|talent|recruiter'
    # Spanish regex
    regex += r'|reclutamiento|reclutador|reclutadora|reclutadores|reclutadoras|recursos humanos'
    return re.search(regex, position)

def filter_employee(position):
    """
    Filter the common employees of the company
    :param position: Position of the employee
    :returns: True if the employee is common
    """
    position = position.lower()
    regex = r''
    
    # English regex
    regex += r'product|developer|engineer|designer|programmer|architect|analyst|tester|consultant|specialist'
    regex += r'|technician|administrator|support'
    regex += r'|sales|marketing|brand|media|advertising|promotion'
    regex += r'|worker|operator|logistic|driver'

    # Spanish regex
    regex += r'|desarrollador|ingeniero|diseñador|programador|arquitecto|analista|consultor|especialista'
    regex += r'|tecnico|administrador|soporte'
    regex += r'|ventas|marketing|marca|medios|publicidad|promocion'
    regex += r'|trabajador|operador|logistica|chofer'


    return re.search(regex, position)

def classify_position(position):
    """
    Classify employees by position
    :param position: Position of the employee
    :returns: String with the general classification
    """
    if filter_owner(position):
        return 'Owner'
    elif filter_director(position):
        return 'Director'
    elif filter_administrative(position):
        return 'Administrative'
    elif filter_manager(position):
        return 'Manager'
    elif filter_hhrr(position):
        return 'HHRR'
    else:
        return 'Collaborator'

def get_hierarchy(employees):
    """
    Obtain a dictionary with the employees sorted by position
    :param employees: List of employee objects
    :returns: dictionary sorted by positions
    """
    # Define a general hierarchy for any company
    hierarchy = {"Owner": [1, []], "Director": [2, []], "Administrative": [3, []], "Manager": [3, []], "HHRR":[4, []], "Collaborator": [4,[]], "Other": [4, []]}

    for employee in employees:
        position = employee['position']

        # Classify employees by position
        hierarchy[classify_position(position)][1].append(employee)
       
    return hierarchy

def start(input_filename, output_folder):
    # Obtain the inputs and output template
    meta, inputs, outputs = handler.read_json(input_filename)

    # Get a list of positions from the employees
    employees = inputs['employees']

    organigramm_obj = {'n_employees': len(employees)}

    hierarchy = get_hierarchy(employees)

    organigramm_obj['employees'] = hierarchy
    outputs['organigramm'] = organigramm_obj
    handler.write_json(input_filename, meta, inputs, outputs)

if __name__ == '__main__':
    start('data.json','.')