#This function is used to get the name of each item
#and remove the offset and write the results into temp file
#The users need to remove the temp file by themselves
def getItemName(downloadDir='', filename='', itemNameList=[], rowOffset=0, rowOffset2=0, columnOffset=0):
    inputFile = open(downloadDir + filename,'r')
    itemList = []
    #outputFile = open(downloadDir + 'temp' + filename, 'w+')
    outputFile = open(downloadDir + 'input.csv', 'w+')

    #skip first rowOffset rows
    for i in range(0, int(rowOffset)):
        itemList = inputFile.readline()

    #obtain item name from the list
    #go back to the start of the file
    itemNameLine = inputFile.readline()
    itemList = itemNameLine.rstrip().split(',')

    #remove the first columnOffset elements
    for i in range(0, int(columnOffset)):
        itemList.pop(0)

    #does not work to do this: itemNameList = itemList
    #should use the following method
    for item in itemList:
        itemNameList.append(str(item))

    #skip second rowOffset rows
    for i in range(0, int(rowOffset2)):
        itemList = inputFile.readline()

    #add the item name list into csv file
    tempList = []
    tempList = itemNameLine.split(',')
    outputFile.write(','.join(tempList))

    #skip first columnOffset columns
    #this is used to get every line of this file
    for line in inputFile:
        tempList = line.split(',')
        for i in range(0, int(columnOffset)):
            tempList.pop(0)        
        outputFile.write(','.join(tempList))
        tempList = []

    #close file
    inputFile.close()
    outputFile.close()

