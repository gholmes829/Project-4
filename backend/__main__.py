#!/usr/bin/env python3
import numpy as np
from clustering import Clusters
import json
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

"""
Post: This will return the current directory that I am in. 
This will be used to help read in the json file.
"""
def getCurrent() -> str:
     return os.getcwd()
"""
Post: This function will return the parent directory of the directiry that I am in
I will use this to retrieve the json file that is in the parent directory
"""
def getParent(path: str) -> str:
    return os.path.dirname(path)   
"""
Post: This function will return the child of the parent function
From this function, we can load in the json file in the parent function
"""    
def getChild(path: str, target: str) -> str:
    return os.path.join(path, target)
"""
Pre: This function takes in an array to be standardized
Post: This function will return the array that was passed in and have it standardized by taking the mean
and dividing it by the standard deviation 
"""
def standardized(arr):
    return (arr-arr.mean(axis=0))/arr.std(axis=0)
"""
Post: Runs the main code for the backend
"""
def main():
    print("Running...") 
    
    #This code is loading in the json file and creating a variable spotify to hold the dictionary in the file
    current = getCurrent()
    parent = getParent(current)
        
    filePath = getChild(parent, 'playlist.json')
    file = open(filePath)
    spotify = json.load(file)
    file.close()

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
        prop.append(temp["acousticness"])
        prop.append(temp["danceability"]) 
        prop.append(temp["energy"]) 
        prop.append(temp["instrumentalness"]) 
        prop.append(temp["key"]) 
        prop.append(temp["liveness"]) 
        prop.append(temp["loudness"]) 
        prop.append(temp["speechiness"]) 
        prop.append(temp["tempo"]) 
        prop.append(temp["valence"])
        newDict[x] = prop
 
 
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
    threshold = 0.7  # change this value to change 
    a, b = d[:int(threshold*len(d))], d[int(threshold*len(d)):]
    
    
    
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

    
    #This will create a final graph of clusters with the blue points being songs we keep 
    #and the red points being songs that we get rid of    
    plt.figure()
    ax = plt.axes(projection="3d")
    ax.scatter3D(0, 0, 0, '*', c="green", zorder=1)
    ax.scatter3D(a[:,0], a[:,1], a[:,2], 'o', c="blue", zorder=1)
    ax.scatter3D(b[:,0], b[:,1], b[:,2], 'o', c="red", zorder=1)
    plt.show()

    
    #Opens a new json file and will write finalDict to the file. finalDict will be
    #used by the front end to remove songs from the playlist. Also will erase anything on the 
    #file before writing to it
    f = open("newPlaylist.json", "w")
    f.truncate(0)
    f.write(json.dumps(finalDict))
    f.close()
    
    print("Done!")
    
if __name__ == "__main__":
    main()

