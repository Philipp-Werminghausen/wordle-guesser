import os
ALL_FILE="words.txt"
LETTER_FILE="words5.txt"
filtered_data = []

with open(ALL_FILE, 'r') as f:
    data = f.read()
    data = data.split('\n')
    #filter out any non 5 letter charcters
    filtered_data = filter(lambda x: len(x) == 5 and x.isalpha(), data)

result = map(lambda x: x.lower(), filtered_data)

with open(LETTER_FILE, 'w') as f:
	f.write(','.join(result))
