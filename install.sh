#!/bin/bash

red=`tput setaf 1`
green=`tput setaf 2`
reset=`tput sgr0`

echo "${green}Installing all the dependencies...${reset}"
where pip
if [ $? != "0" ]; then
    echo "${green}Installing pip...${reset}"
    curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
    python get-pip.py
fi

echo "${green}Installing dependencies through requirements...${reset}"
pip install -r requirements.txt

echo "${green}Doing some final checks...${reset}"
pip freeze > installed_files.txt
diff installed_files.txt requirements.txt
if [ $? == "0" ]; then
    echo "${green}Everything is good to go!${reset}"
else
    echo "${red}Error: Some files seem to be missing...${reset}"
fi

rm installed_files.txt

read -n 1 -s -r -p "Press any key to continue..."
