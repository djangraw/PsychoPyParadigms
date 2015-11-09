#!/bin/bash


for filename in "$@"
do
	#filename='wordlist.txt'

	say -v "Alex" "$(cat $filename)" -o ${filename%.*}.aiff

done