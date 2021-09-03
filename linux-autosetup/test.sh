#!/bin/bash

while getopts ":h" option; do
   case $option in
      h) # display Help
         Help
         exit;;
     \?) # incorrect option
         echo "Error: Invalid option"
         exit;;
   esac
done

Help() {
	echo "Help hath been displayed."
}

string='Help'

