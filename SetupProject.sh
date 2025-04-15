#!/bin/bash

if test -d ./venv; then
    while true; do
	    echo "Virtual Environment detected!";
        read -p "Delete and override environment? (Y/n):" ANSWER;
        case $ANSWER in 
	    "Y" ) echo "Okay will will delete the enviroment and rebulid";
            rm -rf ./venv/
            break;;
	    "n" ) echo "Exiting...";
		    exit;;
	    * ) echo "Invalid response";
            exit;;
        esac
    done
fi

echo "Creating virtual environment named venv";
python -m venv venv;

echo "Activating virtual environment";
source ./venv/Scripts/activate;

echo "Install Python packages into the virtual enviornemnt";
pip install -r ProjectInstalledLibraries.txt;
