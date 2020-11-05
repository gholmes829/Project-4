#!/usr/bin/env python3

import numpy as np
from clustering import Clusters
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

k=None

def main():
	print("Testing...")
	# generating test data
	d0, d1 = (50, 3)
	scale = 1  # how much points should deviate from center
	if d1 == 2:
		c0 = np.full((d0, d1), [1.5, 3.5]) + unitNoise(d0, d1)*scale  # modify values to adjust center
		c1 = np.full((d0, d1), [-0.25, -0.65]) + unitNoise(d0, d1)*scale
		c2 = np.full((d0, d1), [-3.5, 2.15]) + unitNoise(d0, d1)*scale
		c3 = np.full((d0, d1), [-1.1, 5.65]) + unitNoise(d0, d1)*scale
		c4 = np.full((d0, d1), [-0.5, 2.5]) + unitNoise(d0, d1)*scale
	elif d1 == 3:
		c0 = np.full((d0, d1), [1.5, 3.5, 4]) + unitNoise(d0, d1)*scale  # modify values to adjust center
		c1 = np.full((d0, d1), [-0.25, -0.65, 3]) + unitNoise(d0, d1)*scale
		c2 = np.full((d0, d1), [-3.5, 2.15, 3]) + unitNoise(d0, d1)*scale
		c3 = np.full((d0, d1), [-1.1, 5.65, 4]) + unitNoise(d0, d1)*scale
		c4 = np.full((d0, d1), [-0.5, 2.5, 2]) + unitNoise(d0, d1)*scale
	elif d1 == 4:
		c0 = np.full((d0, d1), [1.5, 3.5, 4, 1]) + unitNoise(d0, d1)*scale  # modify values to adjust center
		c1 = np.full((d0, d1), [-0.25, -0.65, 3, -5.15]) + unitNoise(d0, d1)*scale
		c2 = np.full((d0, d1), [-3.5, 2.15, 3, -5.3]) + unitNoise(d0, d1)*scale
		c3 = np.full((d0, d1), [-1.1, 5.65, 0, -5.15]) + unitNoise(d0, d1)*scale
		c4 = np.full((d0, d1), [-0.5, 2.5, 2, -5.2]) + unitNoise(d0, d1)*scale
	
	clusters = []
	clusters.append(c0)
	clusters.append(c1)
	clusters.append(c2)
	clusters.append(c3)
	clusters.append(c4)

	data = np.concatenate(clusters, axis=0)
	standardized = (data-data.mean(axis=0))/data.std(axis=0)
	clusters = testKMeans(standardized, k)

def testKMeans(data, k):  # testing kmeans
	plt.style.use(["dark_background"])
	plt.rc("grid", linestyle="--", color="white", alpha=0.5)
	plt.rc("axes", axisbelow=True)

	clusters = Clusters(data, k)
	centroids = clusters.keys()

	d, s = clusters.orderedData, clusters.orderedScores
	t = 0.75
	a, b = d[:int(t*len(d))], d[int(t*len(d)):]
	
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

	print("Plotting...")
	if clusters[centroids[0]][0].shape[0] == 2:
		plt.figure()
		plt.grid()
		plt.plot(centroids[:,0], centroids[:,1], '*', c="blue", mec="white", ms=20, zorder=3, label="final")
		plt.legend(loc="upper right")

		c=0
		for centroid in clusters:
			data = clusters[centroid]
			plt.plot(data[:,0], data[:,1], 'o', c=colors[c], mec="white", ms=7.5, zorder=1)
			c+=1

		plt.xlabel("x")
		plt.ylabel("y")

		plt.figure()
		plt.grid()
		plt.xlabel("x")
		plt.ylabel("y")
		plt.plot(centroids[:,0], centroids[:,1], '*', c="green", mec="white", ms=15, zorder=3, label="final")
		plt.plot(clusters._center[0], clusters._center[1], 's', c="purple", mec="white", ms=15, zorder=1)
		plt.plot(a[:,0], a[:,1], 'o', c="blue", mec="white", ms=7.5, zorder=1)
		plt.plot(b[:,0], b[:,1], 'o', c="red", mec="white", ms=7.5, zorder=1)
	
	elif clusters[centroids[0]][0].shape[0] == 3:
		plt.figure()
		ax = plt.axes(projection="3d")
		ax.scatter3D(centroids[:,0], centroids[:,1], centroids[:,2], '*', c="blue", zorder=3, label="final")

		c=0
		for centroid in clusters:
			data = clusters[centroid]
			ax.scatter3D(data[:,0], data[:,1], data[:,2], c=colors[c], zorder=1)
			c+=1
		
		plt.figure()
		ax = plt.axes(projection="3d")
		ax.scatter3D(0, 0, 0, '*', c="green", zorder=1)
		ax.scatter3D(a[:,0], a[:,1], a[:,2], 'o', c="blue", zorder=1)
		ax.scatter3D(b[:,0], b[:,1], b[:,2], 'o', c="red", zorder=1)
		
	if clusters[centroids[0]][0].shape[0] > 3:
		for i, centroid in enumerate(clusters):
			data = clusters[centroid]
			print("Cluster "+str(i)+": "+str(len(data)))
	
	if clusters[centroids[0]][0].shape[0] <= 3:
		plt.show()


def unitNoise(d0, d1):
		noise =  np.random.randn(d0, d1)
		minimum = noise.min()
		noise-=minimum
		maximum = noise.max()
		return (noise/maximum)*2-1	

if __name__ == "__main__":
	main()
