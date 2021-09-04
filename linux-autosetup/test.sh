#!/bin/bash

name="java"
echo $name' is the name of the app.'
declare $name.hello = 'hello'
$name.hello = "hi."
echo $(java.hello)
