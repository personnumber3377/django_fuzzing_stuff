
fh = open("dictionary_sqli.txt", "r")
for line in fh.readlines():
	if len(line) <= 10:
		print(line, end="")
fh.close()