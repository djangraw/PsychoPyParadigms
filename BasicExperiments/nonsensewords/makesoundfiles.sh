#!/bin/bash

filename=$1
#filename='wordlist.txt'

for word in $(cat $filename); do
	 say -v "Alex" "$word" -o $word.aiff
done

say -v "Alex" "the word" -o theword.aiff
say -v "Alex" "means" -o means.aiff