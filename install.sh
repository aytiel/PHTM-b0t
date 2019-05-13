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
if [ $? == "0" ]; then
    echo "${green}pip successfully updated.${reset}"
else
    echo "${red}An error has occurred : pip.${reset}"
fi

echo "${green}Installing dependencies through requirements...${reset}"
python -m pip install -r requirements.txt
if [ $? == "0" ]; then
    echo "${green}requirements successfully installed.${reset}"
else
    echo "${red}An error has occurred : requirements.${reset}"
fi

echo "${green}Installing discord.py...${reset}"
python -m pip install -U git+https://github.com/Rapptz/discord.py
if [ $? == "0" ]; then
    echo "${green}discord.py successfully installed.${reset}"
else
    echo "${red}An error has occurred : discord.py.${reset}"
fi

read -n 1 -s -r -p "${green}Press any key to continue...${reset}"
