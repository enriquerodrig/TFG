echo '[+] Starting installation for first_script'
echo '[+] Checking python is installed'
if ! $(command -v python > /dev/null)
then
    echo "[!] python could not be found. Do you want to install it now? (y/n)"
    read -r install_python
    if [ "$install_python" = "y" ]; then
        echo '[+] Installing python'
        sudo apt-get install python
    else
        echo '[+] Skipping python installation. Note that the script will not be able to run until you install it.'
        exit
    fi
fi

echo '[+] Checking pip is installed'
if ! $(command -v pip > /dev/null)
then
    echo "[!] pip could not be found. Do you want to install it now? (y/n)"
    read -r install_pip
    if [ "$install_pip" = "y" ]; then
        echo '[+] Installing pip'
        sudo apt-get install python-pip
    else
        echo '[+] Skipping pip installation. Note that the script will not be able to run until you install it.'
        exit
    fi
fi

echo '[+] Installing python dependencies'
pip3 install -r requirements.txt && echo '[+] Installation completed' || (echo '[!] Installation failed, please check the logs' && exit)

echo '[+] For the script to export pdfs, you need to install wkhtmltopdf. Do you want to install it now? (y/n)'
read -r install_wkhtmltopdf
if [ "$install_wkhtmltopdf" = "y" ]; then
    echo '[+] Installing wkhtmltopdf'
    sudo apt-get install wkhtmltopdf
else
    echo '[+] Skipping wkhtmltopdf installation. Note that the script will not be able to export pdfs until you install it.'
fi

echo '[+] Installation complete, you can now run the script with `python3 osint_reporter.py COMPANY_NAME, COMPANY_DOMAIN`. For mor information, run `python osint_reporter.py --help`'
python osint_reporter.py -h