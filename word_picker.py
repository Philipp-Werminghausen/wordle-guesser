
"""
Wordel.com word of the day guesser
-----------------------------------
Created by Philipp Werminghausen
-----------------------------------
Description: Commandline app that tries to efficiently guess the word of the day from wordl.com with the user.

Notes:
This app is not perfect. 38 words still need more than 6 guesses.

Here is the info from a test run:

Test guessed 2314 words with an average guess tries of 3.8910976663785655 with low of 1 and high of 10
found 735 words in 3 guesses
found 114 words in 2 guesses
found 957 words in 4 guesses
found 358 words in 5 guesses
found 111 words in 6 guesses
found 26 words in 7 guesses
found 6 words in 8 guesses
found 1 words in 1 guesses
found 4 words in 9 guesses
found 2 words in 10 guesses

Improvements that were tried and failed:
1) prioratizing the first 2-3 guessed to get the most information of letters instead of guessing the word.
	- theoretically you could test 25 letters in 5 guesses, but does that guarantee you can always find the word on the 6th guess?
2) prioratizing finding voules first.
"""


class WordGuesser():
	"""Class to try and guess the word of the day from wordle.com
	"""
	def __init__(self):
		"""Load in possible words and set up variables
		"""
		self.LETTER_FILE="words5-exact-set.txt"
		# the lower the number the higher efficiency
		self.RESULTS_MORE_THAN=0
		self.data = []
		with open(self.LETTER_FILE, 'r') as f:
			self.data = f.read()
			self.data = self.data.split(',')
		# Set up variables to track known letters and ther position if applicable
		self.known_letters=[]
		self.known_unused=[]
		self.known_position=[]
		self.known_wrong_position=[]

	def get_common_letters(self,words=None):
		"""Loops through givel list of words and returns list of letters sorted
		by number of occurance in given words.

		Args:
			words (list, optional): List of word to generate alphabet for. Defaults to None.

		Returns:
			list: list of all letters contained in given words sorted by occurance decending
		"""
		if words is None:
			words = self.data	
		letter_count = {}
		for word in words:
			for letter in word:
				if letter not in letter_count:
					letter_count[f"{letter}"] = 1
				else:
					letter_count[f"{letter}"] = int(letter_count[f"{letter}"]) + 1
		sorted_letters = dict(sorted(letter_count.items(), key=lambda item: item[1],reverse=True))
		return list(sorted_letters.keys())

	def contains_chars(self,word,letters):
		"""Checks if all letters from list of letters is within a word

		Args:
			word (str): word to search
			letters (list): letters to search for

		Returns:
			bool: True if word contains all letters, else False
		"""
		return len(list(filter(lambda letter: letter in word, letters))) == len(letters)
	
	def doesn_not_contain(self,word,letters):
		"""Check if word does not use any letters from list of letters

		Args:
			word (str): word to check
			letters (list): list of letters

		Returns:
			bool: True if word does not use any letter from the letters list, False otherwise
		"""
		return len(list(filter(lambda letter: letter not in word, letters))) == len(letters)

	def filter_known_positions(self,word):
		"""Check if letters in word are all possible based on already know information.
		Assumes known letters exist in all words.

		Args:
			word (str): word to check

		Returns:
			bool: False if known letter is not in know position or is in a known wrong position, else True
		"""
		for i,letter in enumerate(self.getKnownLetters()):
			#remove any guess that that don't have the known letter in right poss
			if len(self.known_position[i]):
				for pos in self.known_position[i]:
					if word[pos] != letter:
						return False
			#otherwise check wrong positions
			if len(self.known_wrong_position[i]):
				for pos in self.known_wrong_position[i]:
					if word[pos] == letter:
						return False
		return True

	def no_dup_unknown_chars(self,word):
		"""Checks if the word contains an unknown dupe character.
		This is a filter to guess more efficiently by getting the most info
		by use the most amount of possible unknown character to get information.

		Args:
			word (str): word to check

		Returns:
			bool: False if unknow letter appears multiple times, True otherwice
		"""
		chars = []
		for char in word:
			if char in chars and char not in self.getKnownLetters():
				return False
			chars.append(char)
		return True

	def filter_knowns(self):
		"""Filters the original data set to take into consideration all known info

		Returns:
			list: list of possible words after applying constraints
		"""
		# filter out wrods that don't use the used charcters
		filter1 = list(filter(lambda x: self.contains_chars(x,self.getKnownLetters()), self.data))
		# filter out words that use the unused characters
		filter2 = list(filter(lambda x: self.doesn_not_contain(x,self.known_unused), filter1))
		# filter out words that have the wrong position known charcters
		filter3 = list(filter(lambda x: self.filter_known_positions(x), filter2))
		# filter out words that have duplicate unknown chacters
		filter4 = list(filter(lambda x: self.filter_known_positions(x), filter3))
		return filter4

	def get_word_that_contains_most(self,words=None,letters=None):
		"""Get one or more words that contain most amout of unknown letters
		With priority decending

		Args:
			words (list, optional): list of words filter. Defaults to None.
			letters (list, optional): list of letters sorted in decending importance. Defaults to None.

		Returns:
			list: list with more than (self.RESULTS_MORE_THAN) matching results
		"""
		if letters is None:
			letters=self.get_common_letters()
		if words is None:
			words=self.data
		orig_letters = letters.copy()
		offset = 0
		res = []
		while len(res) <= self.RESULTS_MORE_THAN and len(letters) > 0:
			if len(letters) >= 5:
				letters = letters[:4]
			res = list(filter(lambda x: self.contains_chars(x,letters), words))
			letters = letters[:-1]
			if len(letters) <= 0:
				offset += 1
				letters = orig_letters[offset:]
		return res

	def get_best_guess(self, filtered_words=None, letters=None):
		"""Returns the best next guesses

		Args:
			filtered_words (list, optional): list of pre filtered words. Defaults to None.
			letters (list, optional): list of letters with decending importance. Defaults to None.

		Returns:
			list: list of words that should be optimal next guesses with decending efficiency
		"""
		if letters is None:
			letters=self.get_common_letters()
		if filtered_words is None:
			filtered_words=self.data
		res = []

		print(f'Options left {len(filtered_words)}')

		if len(res) <= 0:
			res = self.get_word_that_contains_most(filtered_words,letters)
		return res

	def best_guess_letters(self):
		"""Generate list of next letters to use in decending order of importance.
		This takes into account any known information and filteres out already used letters and impossible words
		to generate the resulting most common letters list.

		Returns:
			list: List of letters to use in next guess decending efficiency.
		"""
		#returns the best guess of letters to try
		result = self.getKnownLetters()
		for letter in self.get_common_letters():
			if letter in result or letter in self.known_unused:
				continue
			result.append(letter)
		return result

	def process_previous_word_result(self,last_word,match):
		"""process feedback from a word guess.

		Args:
			last_word (str): The word that was guessed
			match (str): str representing the feedback. _ = wrong letter. 0 = wrong position. 1 = correct possition
		"""
		for i,letter in enumerate(last_word):
			if match[i] == '_':
				self.known_unused.append(letter)
			elif match[i] == '0':
				if letter in self.getKnownLetters():
					index_in_known_letters = self.getKnownLetters().index(letter)
					self.known_wrong_position[index_in_known_letters].append(i)
				else:
					self.known_letters.append(letter)
					self.known_position.append([])
					self.known_wrong_position.append([i])
			elif match[i] == '1':
				if letter in self.getKnownLetters():
					index_in_known_letters = self.getKnownLetters().index(letter)
					self.known_position[index_in_known_letters].append(i)
				else:
					self.known_letters.append(letter)
					self.known_position.append([i])
					self.known_wrong_position.append([])

	def get_result(self,word):
		"""collect console input from the user to get feedback on last guessed word

		Args:
			word (str): word to get feedback for

		Returns:
			str: user input
		"""
		print(f"input the result for {word}: '_' -> unused letter, '0' -> wrong possition, '1' correct")
		x = input()
		if len(x) == 5:
			self.process_previous_word_result(last_word,x)
		return x

	def reset_results(self):
		"""Reset known info to start a new session
		"""
		self.known_letters=[]
		self.known_unused=[]
		self.known_position=[]
		self.known_wrong_position=[]

	def getKnownLetters(self):
		"""Get a copy of known letters

		Returns:
			list: known letters
		"""
		return self.known_letters.copy()

	def getKnownUnusedLetters(self):
		"""get a copy of known letters that are unused

		Returns:
			list: list of known unused letters
		"""
		return self.known_unused.copy()

	def get_result_comp(self,word,guess):
		"""Generate feedback on a guess compared to a word that needs to be guessed.
		This is for the automatic test.

		Args:
			word (str): word to be guessed
			guess (str): the guess word

		Returns:
			str: result string of the guess compared to the word
		"""
		result = ""
		for i,letter in enumerate(guess):
			if letter == word[i]:
				result += '1'
			elif letter in word:
				result += '0'
			else:
				result += '_'
		return result

	def guess(self):
		"""Guess the next word

		Returns:
			str: next word to guess
		"""
		filtered = self.filter_knowns()
		res = self.get_best_guess(filtered,self.best_guess_letters())
		if len(res):
			return res[0]
		return ''

	def test_word(self,word):
		"""Tests a scenario of this program trying to get the input word

		Args:
			word (str): word that needs to be guessed

		Returns:
			int: returns the number of guesses it took to guess this word
			it is capped at 10 guesses
		"""
		self.reset_results()
		guesses = 1
		guess = self.guess()
		while word != guess:
			print(f'{guesses}{"  -  st" if guesses==1 else "nd" if guesses==2 else "rd" if guesses==3 else "th"} guess {guess}')
			result = self.get_result_comp(word,guess)
			self.process_previous_word_result(guess,result)
			guess = self.guess()
			guesses += 1
			if guesses == 10:
				break
		print(f'word "{word}" took {guesses} guesses')
		return guesses

	def test_all(self):
		"""run through database and try and guess each word

		Returns:
			list: list of number of guesses per word guessed
		"""
		num_of_guesses = []
		for word in self.data:
			num_of_guesses.append(self.test_word(word))
		return num_of_guesses

if __name__ == "__main__":
	"""Main program loop
	Console interface to help guess a word or run a test
	"""
	x = 'r'
	last_word = ""
	guesser = WordGuesser()
	guesses = 0
	print('press q to quit, or r to restart and t for test')
	while x != 'q':
		if x == 'q':
			# Exit
			break
		elif x == 't':
			# Run a test of the program logic and see some stats
			num_of_guesses = guesser.test_all()
			words = guesser.data
			high = max(num_of_guesses)
			low = min(num_of_guesses)
			nums = {}
			for value in num_of_guesses:
				if str(value) not in nums:
					nums[f"{value}"] = 1
				else:
					nums[f"{value}"] = int(nums[f"{value}"]) + 1
			print(nums)
			print(f'Test guessed {len(words)} words with an average guess tries of {sum(num_of_guesses) / len(num_of_guesses)} with low of {low} and high of {high}')
			for key, value in nums.items():
				print(f"found {value} words in {key} guesses")
			x = 'r'
		elif x == 'r':
			# reset the guesser and try again
			guesser.reset_results()
			last_word = guesser.guess()
			guesses += 1
			print(f'First use this word:',last_word)
			x = guesser.get_result(last_word)
		else:
			# Keep guessing
			last_word = guesser.guess()
			guesses += 1
			print(f'Next try:',last_word)
			x = guesser.get_result(last_word)
		if x == '11111':
			# word found
			print(f"Yay! Word found in {guesses}guesses")
			x = 'r'




