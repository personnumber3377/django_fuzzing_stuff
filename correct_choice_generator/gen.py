
def s():
	fh = open("choices.txt", "r")
	lines = fh.readlines()
	fh.close()
	output = set()
	# Choices are: 
	sep = "Choices are: "
	for line in lines:
		line = line[line.index(sep)+len(sep):]
		if "\n" == line[-1]: # Cutout newline
			line = line[:-1]
		print(line)
		things = line.split(", ")
		for thing in things:
			output.add(thing) # Add the thing.
	for thing in list(output):
		print("\""+str(thing)+"\"")
	return


if __name__=="__main__":
	s()
	exit(0)
