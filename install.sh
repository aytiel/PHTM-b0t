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

echo "${green}Updating pip...${reset}"
python -m pip install --upgrade pip

echo "${green}Installing dependencies through requirements...${reset}"
python -m pip install -r requirements.txt

echo "${green}Installing discord.py...${reset}"
python -m pip install -U discord.py[voice]

read -n 1 -s -r -p "${green}Press any key to continue...${reset}"
