'''
A 'Size CSV' is a CSV file with schema:  [ClassId, SecuritySize, Count]
Such CSV can be used to create 'Count' number securities of 'SecuritySize' in aurora db for given 'ClassId'.

For this scripts will accept two files:
	1. Intial 'Size CSV' .. Lets say InitialSizeCsv
	2. Bucket CSV: [ ClassId, AverageSize, DistinctSizesCount, PeakSecuritiesCount,	TotalSecurities, StdDev ]

The BucketCSV needs to generate 'Size CSV' (as originally, it was created from a Size CSV), lets name that SizeFromBucketCsv

The objective is to produce final 'FinalSizeCsv' after combininng InitialSizeCsv and SizeFromBucketCsv
'''
import csv
import random

def maxSizeAllowed(classId):
	if classId != 4020:
		return 32711
	else:
		return 10e6;

def convertBucketToSizes(bucketTable, excludes = set()):
	outputTable = []; #list of {ClassId, Size, Count}
	classId = bucketTable[0]['ClassId']
	maxSize = maxSizeAllowed(classId)
	for row in bucketTable:
		outputTable.append( [classId, row['AverageSize'], row['PeakSecuritiesCount'] ] )
		excludes.add(row['AverageSize']);
		
		securitiesToAdd = row['TotalSecurities'] - row['PeakSecuritiesCount']
		distinctsRemaining = row['DistinctSizesCount'] - 1
		avgFill = securitiesToAdd / distinctsRemaining;
		while( securitiesToAdd > 0 and distinctsRemaining > 0):
			deviation = random.gauss(0, row['StdDev'])
			deviation = round(abs(deviation)) if( deviation > 0 ) else -round(abs(deviation));
			step = 1

			cx = row['AverageSize'] + deviation
			if( cx < 1 or cx > maxSize ):  #disallow negative sizes, huge sizes
				continue;

			while( cx in excludes and cx < maxSize ):
				cx += step

			if distinctsRemaining > 1:
				cy = min(
					round( ( avgFill + 2*random.random()*avgFill )/2 ), #gives you random point between 0.5 to 1.5 stdDev
					row['PeakSecuritiesCount'], #never cross the peak
					securitiesToAdd - distinctsRemaining + 1
				);
				cy = max(1,cy)  ##defensive, dont let cy go below 1
			else:
				cy = securitiesToAdd

			excludes.add(cx) #dont repeat this point again
			outputTable.append([classId, cx, cy])
			distinctsRemaining -= 1;
			securitiesToAdd -= cy

	return(outputTable);

def produceFinalCsv(initialSizeTable, bucketTable):
	pass;

def readCsvToTable(csvFileName):
	table = []
	with open(csvFileName) as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		head = next(readCSV)
		#print(".....", head)
		for row in readCSV:
			#print(row)
			row = [float(x) if '.' in x else int(x) for x in row]
			table += [ dict(zip(head,row)) ]
	
	return table;

def readCsvsToTable():
	bucketCsv = 'C:\\Users\\User\\Desktop\\work\\Buckets1.csv';
	initialSizeCsv = 'C:\\Users\\User\\Desktop\\work\\DistinctSize.csv';
	bucketTable = readCsvToTable(bucketCsv);
	initialSizeTable = readCsvToTable(initialSizeCsv);

	print(bucketTable);
	print(initialSizeTable)

	return( [bucketTable, initialSizeTable])

def main():
	[bucketTable, initialSizeTable] = readCsvsToTable()
	print( convertBucketToSizes( bucketTable, set() ))

	pass;

main();	
