import socket
import sys
import datetime

"""Extracting arguments data"""
myPort = int(sys.argv[1])
parentIP = sys.argv[2]
parentPort = int(sys.argv[3])
ipsFileName = str(sys.argv[4])

"""Opening socket to myPort"""
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
s.bind(('', myPort))

"""Timestamp the static ip addresses with -1 ttl"""
file = open(ipsFileName, 'r')
ipsLines = file.readlines()

arrLine = []
for line in ipsLines:
	# not adding flag to already flagged lines
	if ",-1" in line:
		arrLine.append(line)
		continue
	# searching if already exist time stamp
	firstComma = line.find(',')
	secondComma = line.find(',', firstComma + 1)
	thirdComma = line.find(',', secondComma + 1)
	# if found third comma that means its got time stamp
	if thirdComma != -1:
		continue
	# other cases, adding -1 to static lines
	newLine = line[0:len(line)-1] + ",-1"
	arrLine.append(newLine)
	arrLine.append("\n")
file.close()
file = open(ipsFileName, 'w')
for line in arrLine:
	file.write(line)
file.close()



while True:
	"""Setting variables with default values and flags"""
	"""Setting variables with default values and flags"""
	ip, ttl, timeStamp = "", "", ""
	deleteLineNum = -1
	forCounter = 0
	urlFound = False
	"""Client's request and convert to string"""
	url, (clientIp, clientPort) = s.recvfrom(1024)
	url = url.decode()

	"""Searching the url in the file"""
	file = open(ipsFileName, 'r')
	for line in file:
		firstCommaInLine = line.find(',')
		linesUrl = line[:firstCommaInLine]
		if url == linesUrl:
			urlFound = True
			"""Parsing the ip, ttl and timestamp from the ips file"""
			firstComma = line.find(',')
			secondComma = line.find(',', firstComma + 1)
			thirdComma = line.find(',', secondComma + 1)
			ip = line[firstComma + 1:secondComma]
			ttl = int(line[secondComma + 1:thirdComma])
			timeDiff = -1 #default value
			if line[thirdComma + 1:] != "-1\n":
				timeStamp = datetime.datetime.strptime(line[thirdComma + 1:], "%m-%d-%Y %H:%M:%S.%f")
				"""checking if the ttl has not expired"""
				currentTime = datetime.datetime.now()
				timeDiff = currentTime - timeStamp
				timeDiff = timeDiff.total_seconds()
			"""checking if the site is not static and it's ttl valid"""
			if line[thirdComma + 1:] != "-1\n" and (timeDiff >= ttl):
				"""saving the line that needed to be delete"""
				deleteLineNum = forCounter
		forCounter += 1
	lines = file.readlines()
	file.close()
	if urlFound:
		"""Delete url if the ttl expired"""
		if deleteLineNum != -1:
			del lines[deleteLineNum]
			"""re-writing the file without the deleted line"""
			newFile = open(ipsFileName, "w+")
			for line in lines:
				newFile.write(line)
			newFile.close()
			"""setting the url bool to not found"""
			urlFound = False
		else:
			"""sending information to the client/ server"""
			siteData = "\n".join([str(ip), str(ttl)])
			s.sendto(siteData.encode(), (clientIp, clientPort))
	"""url not found"""
	if not urlFound:
		if parentIP != "-1":
			s.sendto(url.encode(), (parentIP.encode(), parentPort))
			parentData, parentAddr = s.recvfrom(1024)
			parentData = parentData.decode()
			pIp, pTtl = [str(i) for i in parentData.split("\n")]
			addUrlFile = open(ipsFileName, "a")
			"""Creating new url line we got from parent"""
			newUrlLine = url + "," + pIp + "," + pTtl + "," + datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S.%f")
			addUrlFile.write(newUrlLine)
			addUrlFile.close()
			"""sending information to the client/ server"""
			siteDataFromParent = "\n".join([str(pIp), str(pTtl)])
			s.sendto(siteDataFromParent.encode(), (clientIp, clientPort))












