"""
File: __main__.py\n
Author: Grant Holmes and Peyton Doherty\n
Date: 11/08/20\n
Description: This runs the main code for the backend. Takes in a dictionary from the frontend and creates a new one with the scores connected to their IDs
"""
import numpy as np
from clustering import Clusters
import json
import matplotlib.pyplot as plt
import sys

print("entered file")
def standardized(arr):
	"""
	Pre: This function takes in an array to be standardized

	Post: This function will return the array that was passed in and have it standardized by taking the mean
	and dividing it by the standard deviation
	"""
	return (arr-arr.mean(axis=0))/arr.std(axis=0)

def main(argv):
	"""
	Pre: Runs the main code for the backend. This will take in the data from the front end and
	put it into a new dicitonary called newDict.

	Middle: newDict will take each ID as its keys, with each one having a valule of None. From there, the program
	will create a list that contains each ID's attributes and then will assign that list to its corresponding key in newDict.
	Each ID is then given a score based on its attributes attachted to it. The higher the score the more the song is determined
	to not belong to the playlist

	Post: At the end, the backend will give the front a finalDict, that will contain the ID of each song as its keys
	and each will have a value that is its corresponding score
	"""
	print("Running...")
	spotify = json.loads(argv[0])
	amount = spotify["Playlist"]
	g=len(amount)
	newDict = {}
	i=0

	#This for loop creates a new dictionary and will make the keys the ID of the songs and give
	#each key a list of the attributes that match that song
	for i in range(g):
		prop = []
		temp = spotify["Playlist"][i]
		x = temp["ID"]
		newDict[x] = None
		#prop.append(temp["acousticness"])
		prop.append(temp["danceability"])
		prop.append(temp["energy"])
		#prop.append(temp["instrumentalness"])
		prop.append(temp["key"])
		#prop.append(temp["liveness"])
		#prop.append(temp["loudness"])
		#prop.append(temp["speechiness"])
		prop.append(temp["tempo"])
		prop.append(temp["valence"])
		newDict[x] = prop
	print("Appending")
	#Creates a 2d list of the of the lists of attributes that are connected to each song
	newList = []
	for key in newDict:
		newList.append(newDict[key])
	#Plots the centroids on a graph with the other data points
	converted = np.array(newList)
	std = standardized(converted)
	clusters = Clusters(std)
	centroids = clusters.keys()
	clusters.printInfo()

	colors = {
		0: "green",
		1: "red",
		2: "orange",
		3: "purple",
		4: "cyan",
		5: "magenta",
		6: "pink",
		7: "yellow",
	}

	plt.figure()
	ax = plt.axes(projection="3d")
	ax.scatter3D(centroids[:,0], centroids[:,1], centroids[:,2], '*', c="blue", zorder=3, label="final")

	c=0
	for centroid in clusters:
		data = clusters[centroid]
		ax.scatter3D(data[:,0], data[:,1], data[:,2], c=colors[c], zorder=1)
		c+=1

	d, s = clusters.orderedData, clusters.orderedScores

	#Creates a new dictionary called finalDict that, when filled, will have the IDs of the songs as the keys
	#and a score as the value to each key.
	d = d*converted.std(axis = 0) + converted.mean(axis = 0)

	finalDict = {}
	for i in range(g):
		temp = spotify["Playlist"][i]
		x = temp["ID"]
		finalDict[x] = None

	count = 0
	original = std*converted.std(axis = 0) + converted.mean(axis = 0)
	for i in range(g):
		for j in range(g):
			if(np.all(original[i] == d[j])):
				temp = spotify["Playlist"][i]
				x = temp["ID"]
				finalDict[x] = s[j]
				count+=1
	print(finalDict)
	print("Done!")

if __name__ == "__main__":
	main(sys.argv[1:])
