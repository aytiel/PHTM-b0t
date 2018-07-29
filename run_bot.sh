#!/bin/bash

red=`tput setaf 1`
green=`tput setaf 2`
reset=`tput sgr0`

echo "${green}Checking for updates...${reset}"
git pull origin gw2-uploader
if [ $? == "0" ]; then
    echo "${green}Update successful.${reset}"
else
    echo "${red}An error has occurred : update unsuccessful."
    echo "Would you like to force update? This will result in a fresh, up-to-date version of the bot.${reset}"
    echo -n "Type y/n and press enter: "
    read ans
    if [ "$ans" != "${ans#[Yy]}" ]; then
        git reset --hard
        git pull origin gw2-uploader
        if [ $? == "0" ]; then
            read -n 1 -s -r -p "${green}Force update successful. Please replace your bot TOKEN again then run this script again.${reset}"
            exit
        else
            echo "${red}An error has occurred : force update unsuccessful. Please manually delete this bot folder and download a fresh copy.${reset}"
        fi
    else
        echo "${red}Update canceled.${reset}"
    fi
fi

echo "${green}Booting up the bot...${reset}"
python -u bot.py
