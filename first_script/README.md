# Company OSINT Reporter
## Installation
The actual installation is very simple. You just need to clone the repository and install the requirements.
```bash
git clone $REPO_URL
cd first_script
bash install.sh
```
> **Note:** Be aware that the installation at this point is only prepared for linux systems with apt package manager. If you are using another system, you will need to install the requirements manually.
### Manual installation
If you want to install the requirements manually, you can do it with the following command:
```bash
pip install -r requirements.txt
```
Then you will need to install `wkhtmltopdf`, if you are not using linux, follow the instructions in the [official website](https://wkhtmltopdf.org/).

## Usage
To use the script, locate the directory where you cloned the repository and execute the following command:
```bash
python osint_reporter.py $COMPANY_NAME $COMPANY_DOMAIN [-n $NUMBER_OF_RESULTS] [-c $NUMBER_OF_CANDIDATES] [-o $OUTPUT_DIRECTORY] [-t $TIMEOUT] [-j $JITTER] [-m $MAIL_PROVIDER] [-k $KEYWORDS] [-l $LANGUAGE] [--data-folder $DATA_FOLDER] [--username $USERNAME] [--password $PASSWORD]
```
### Parameters
The parameters shown above are the only required parameters to run the script. However, there are some optional parameters that you can use to customize the output of the script:
- `$COMPANY_NAME`: This parameter is the name of the company that you want to get the report from. This parameter is required.
- `$COMPANY_DOMAIN`: This parameter is the domain of the company that you want to get the report from. This parameter is required. Remember that this parameter represents the pattern of the company emails, recognized by the keywords ['name','lname','@']. A valid domain would be `name.lname@company.com` or `lname.name@company.com`, and an invalid one would be `company.com`.
- `-o` or `--output`: This parameter allows you to specify the output directory where the report will be saved. If you don't specify this parameter, the report will be saved in the path `./output/`.
- `-t` or `--timeout`: This parameter allows you to specify the maximum time for the requests to recieve a response. If you don't specify this parameter, the default timeout will be 15 seconds.
- `-j` or `--jitter`: This parameter allows you to specify the time between requests take place, to try to avoid being detected as bot. If you don't specify this parameter, the default jitter will be 2 seconds.
- `-n` or `--number`: This parameter allows you to specify the number of results that you want to get from the script. Specifying a value of `0` will get all the results, this is the default value.
- `-c` or `--candidates`: This parameter allows you to specify the number of candidates that you want to get from the script. Specifying a value of `0` will not get any candidate. If you don't specify this parameter, the default value will be 10.
- `-m` or `--mail-provider`: This parameter allows you to specify the mail provider that you want to use to validate the emails. If you don't specify this parameter, the default value will be both `google` and `o365`.
- `-k` or `--keywords`: This parameter allows you to specify the keywords that you want to use to search for candidates in the company. This is a list of items separated by commas `,`. If you don't specify this parameter, the default value will be an empty list.
- `-d` or `--directors-board`: This parameter allows you to specify which positions of the company you want displayed in the final report. Possible values are: `[Owner, Director, Manager, Administrative, HHRR, Collaborator]`. If you don't specify this parameter, the default value will be an empty list.
- `-p` or `--pdf-template`: This parameter allows you to specify the template that you want to use to generate the final report, found at `./pdf_generator/templates`. If you don't specify this parameter, the default value will be `./pdf_generator/templates/osint_report.html`.
- `--data-folder`: This parameter allows you to specify the folder where the temporal data will be saved. If you don't specify this parameter, the default value will be `/tmp/osint_reporter/`.
- `--username`: This parameter allows you to specify the username that you want to use to login to the LinkedIn API. If you don't specify this parameter, the default value will be `None`, and an anonymous scrapper will be used.
- `--password`: This parameter allows you to specify the password that you want to use to login to the LinkedIn API. If you don't specify this parameter, the default value will be `None`, and an anonymous scrapper will be used.

### Examples
If you want to get the report of the company `Company Name` with the domain `company.com` and you want to save the report in the directory `./reports/`, you can do it with the following command:
```bash
python osint_reporter.py "Company Name" name.lname@company.com -o ./reports/
```
If you are signed in to LinkedIn and you want to use the authenticated scrapper, you can do it with the following command:
```bash
python osint_reporter.py "Company Name" <mail_structure>@company.com --username <linkedin_username> --password <linkedin_password>
```
The partial results of the script are saved at the data folder, `/tmp/osint_reporter` by default, you can change that setting as follows:
```bash
python osint_reporter.py "Company Name" <mail_structure>@company.com --data-folder ./data/
```
If you want to get the report of the company `Company Name` with the domain `company.com` and you want to get only 20 results, you can do it with the following command:
```bash
python osint_reporter.py "Company Name" lname@company.com -n 20
```
If you want to get the report of the company `Company Name` with the domain `company.com` but you want only founder and director candidates, you can do it with the following command:
```bash
python osint_reporter.py "Company Name" lname.name@company.com -k "founder,director"
```
If you know the mail provider of the company `Company Name` with the domain `company.com` and you want to validate the emails with that specific provider, you can do it with the following command:
```bash
python osint_reporter.py "Company Name" name.lname@company.com -m o365
```
Any other combination of parameters is possible for the script, to get more information about the parameters, you can use the `-h` or `--help` parameter.
