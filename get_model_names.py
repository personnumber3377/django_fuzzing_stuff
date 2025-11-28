

fh = open("expression_models.py", "r")
lines = fh.readlines()
fh.close()
for line in lines:
	if line.startswith("class "):
		line = line[6:]
		# print(line)
		assert "(" in line
		line = line[:line.index("(")]
		print("\""+line+"\",")
