#!/bin/bash

red=`tput setaf 1`
green=`tput setaf 2`
reset=`tput sgr0`

echo "${green}Checking for updates...${reset}"
git pull origin gw2-uploader
if [ $? == "0" ]; then
    echo "${green}Update successful.${reset}"
else
    echo "${red}An error has occurred : update unsuccessful.${reset}"
fi

echo "${green}Booting up the bot...${reset}"
python -u bot.py
