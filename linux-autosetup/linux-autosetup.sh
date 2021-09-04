#!/bin/bash

# OOP emulation credit to Maxim Norin from https://stackoverflow.com/questions/36771080/creating-classes-and-objects-using-bash-scripting#comment115718570_40981277
# source app and rec class files
. classes/app.h
. classes/rec.h

# Import and source config files
# . applist
. config


app java
java.constructor 

