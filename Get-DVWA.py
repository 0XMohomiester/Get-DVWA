#!/usr/bin/python3
import os
import time
import pymysql
import pyfiglet
import subprocess
from termcolor import *


# Notes about ubuntu Installlation:
#   1) libraries installed using : sudo apt install python3-pyfiglet,   sudo apt install python3-pymysql,  sudo apt install python3-termcolor
#   if necessary: In config file this line must be : $_DVWA[ 'db_server' ]   = getenv('DB_SERVER') ?: 'localhost'; 


# Printing Banner

def printBanner():
    banner = pyfiglet.figlet_format("Get-DVWA", font='slant')
    colored_banner = colored(banner, 'green')
    print(colored_banner)
    print("Twitter: @0XMohomiester")
printBanner()

# Check if the script is being run with root privileges

def checking_root():
    if os.geteuid() != 0:
        print('[+] Please run the script with root privileges')
        exit()
    else:
        print("Starting...")
        time.sleep(2)
checking_root()

# Extract ip address of machine
ip = os.popen("ip a | grep -m 3 'inet'| tail -n 1 | awk '{print $2}' | cut -d '/' -f 1 | head -n 1 | tr -d '\n'").read()

# Install packages, libraries and dependencies. 
def Install_dependencies():
    os.system("sudo apt update -y && sudo apt upgrade -y")
    os.system("sudo apt install -y git")
    os.system("sudo apt install -y apache2 mariadb-server mariadb-client php php-mysqli php-gd libapache2-mod-php")
    # Changing the password root user in mysql. 
    os.system("sudo mysqladmin -u root password 'password'")
    time.sleep(0.5)
    # Staring apache2 
    print("starting apache and mysql services .......")
    os.system("sudo service apache2 start")
    os.system("sudo service mysql start")

Install_dependencies()

# Installing DVWA Repo from Github and save it in apache2 configuration folder  
def configuring_DVWA():
    os.system("sudo rm -rf /var/www/html/*")
    os.system("sudo mkdir /var/www/html/DVWA")
    os.system("git clone https://github.com/digininja/DVWA.git")
    os.system("sudo mv -f DVWA/ /var/www/html/")
    os.system("sudo cp -f /var/www/html/DVWA/config/config.inc.php.dist /var/www/html/DVWA/config/config.inc.php")
    time.sleep(2)

configuring_DVWA()

def Configuring_db():
    try:
        # Connection parameter
        host = 'localhost'
        port = 3306
        user = 'root'
        password = 'password'
        database = 'mysql'
        # Establish a connection 
        conn = pymysql.connect(host=host, port=port, user=user, password=password,database=database)
        #creat a cursor 
        cursor = conn.cursor()
        queries = ["create database dvwa", 
        "create user dvwa@localhost identified by 'p@ssw0rd'",
        "grant all on dvwa.* to dvwa@localhost",
        "flush privileges"]
        
        # Execute SQL Query after looping through each query. 
        for query in queries:
            cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
        print("Database is configured successfully")
        time.sleep(3)
    except pymysql.Error as e:
        print(f"Error {e}")

Configuring_db()
# Run the shell command to extract the PHP version
php_os_command = "php --version | head -n 1  | cut -d '(' -f 1 | cut -d ' ' -f 2 | cut -d '.' -f1-2"
output = subprocess.check_output(php_os_command, shell=True)

# Decode the output bytes to a string
PHP_V = output.decode('utf-8').strip() # This variable contain version of php like: 7.4 or 5.3

php_ini= f'/etc/php/{PHP_V}/apache2/php.ini'
config_inc_php  = "/var/www/html/DVWA/config/config.inc.php"

def Editing_files():
    try:
        try:
            # Disable authentication in config.inc.php

            with open(config_inc_php, 'r') as f:
                config_file_content = f.read()

            new_config_file_content = config_file_content.replace("$_DVWA[ 'disable_authentication' ] = false;","$_DVWA[ 'disable_authentication' ] = true;")

            with open(config_inc_php,'w') as f:
                f.write(new_config_file_content)
            time.sleep(1)
            # set default_security_level to low

            with open(config_inc_php, 'r') as f:
                config_file_content = f.read()

            new_config_file_content = config_file_content.replace("$_DVWA[ 'default_security_level' ] = 'impossible';","$_DVWA[ 'default_security_level' ] = 'low';")

            with open(config_inc_php,'w') as f:
                f.write(new_config_file_content)
            time.sleep(1)
            # Creating captcha
        
            with open(config_inc_php,'r') as f:
                pub_DVWA_conf_content = f.read()
            
            new_pub_DVWA_conf_content = pub_DVWA_conf_content.replace("$_DVWA[ 'recaptcha_public_key' ]  = '';","$_DVWA[ 'recaptcha_public_key' ]  = '6Le7FtsnAAAAAOoaO7sOz2087p4wbOi8j7Jzkdkz';")
            
            with open(config_inc_php,'w') as f:
                f.write(new_pub_DVWA_conf_content)
            time.sleep(1)
            with open(config_inc_php,'r') as f:
                priv_DVWA_conf_content = f.read()
            
            new_priv_DVWA_conf_content = priv_DVWA_conf_content.replace("$_DVWA[ 'recaptcha_private_key' ] = '';","$_DVWA[ 'recaptcha_private_key' ] = '6Le7FtsnAAAAAAjtSW_83jR4TQ0j9pqPqxY6rE86';")
            
            with open(config_inc_php,'w') as f:
                f.write(new_priv_DVWA_conf_content)
        except Exception as e:
            time.sleep(2)
            print(f"There is an error in config.inc.php, {e}")
        
        # Change uploads and config folders permission to be writeable by the web service.

        os.system("sudo chmod 757 /var/www/html/DVWA/hackable/uploads/")
        os.system("sudo chmod 757 /var/www/html/DVWA/config")
        try:
            # Changing the allow_url_include and display_errors values to on  
            
            os.system(f"sudo sed -i 's/allow_url_include = Off/allow_url_include = On/g' /etc/php/{PHP_V}/apache2/php.ini")
            os.system(f"sudo sed -i 's/allow_url_fopen = Off/allow_url_fopen = On/g' /etc/php/{PHP_V}/apache2/php.ini")
            os.system(f"sudo sed -i 's/display_errors = Off/display_errors = On/g' /etc/php/{PHP_V}/apache2/php.ini")
            os.system(f"sudo sed -i 's/display_startup_errors = Off/display_startup_errors = On/g' /etc/php/{PHP_V}/apache2/php.ini")
        except Exception as e:
            print(f"There is an error in php.ini, {e}")
            time.sleep(2)
        try:
            # Editing /etc/apache2/sites-available/000-default.conf to make website accessible from Document root to DVWA Directly. 
            os.system("sudo sed -i -e 's#/var/www/html#/var/www/html/DVWA#g' /etc/apache2/sites-available/000-default.conf")
        except Exception as e:
            print(f"There is an error while editing 000-default.conf, {e}")
            time.sleep(2)

        # Restaring apache2 and mysql
        time.sleep(0.5)
        print("starting apache and mysql services.......")
        os.system("sudo service apache2 restart")
        os.system("sudo service mysql restart")
    except Exception as e:
        print(f"There is an error while editing files {e}")
Editing_files()

os.system("clear")
printBanner()
time.sleep(1)
print("Please note that the password you use for the root user in MySQL is referred to as 'password'.")
print("Congratulation!!")
print(f"You can access your lab from browser using: http://{ip}:80")
