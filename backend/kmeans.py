"""
A few notes:
	- tobytes and frombuffer used bc mutable objects can't be hashed and used in dict
"""
import numpy as np
import matplotlib.pyplot as plt
from time import process_time as time

class KMeans(dict):
	def __init__(self, data: np.ndarray, k: int, iterations: int = 100) -> None:
		if not k>0:
			raise ValueError("k must be greater than 0")
		start = time()  # timing
		super().__init__(self)
		self._data = data
		self._bounds = np.array([[data[:,0].min(), data[:,0].max()], [data[:,1].min(), data[:,1].max()]])
		self._xRange, self._yRange = np.diff(self._bounds).flatten()
		self._range = self.dist(*np.array([[self._xRange, 0], [0, self._yRange]]))
		self._alpha = 0.75
		self._convergence = 0.0001
		self._dp = 0

		for centroid in range(k):
			x, y = KMeans.rand(self._bounds[0].min(), self._bounds[0].max()), KMeans.rand(self._bounds[1].min(), self._bounds[1].max())
			self.add(np.array([x, y]))	

		# graphing data and randomly initialized centroids
		plt.figure()
		plt.grid()
		centroids = self.getCentroids()
		plt.plot(centroids[:,0], centroids[:,1], 's', c="blue", mec="white", ms=10, zorder=2)

		plt.plot(data[:,0], data[:,1], 'o', c="red", mec="white", ms=7.5, zorder=1)

		plt.xlabel("x")
		plt.ylabel("y")
		
		#plt.show()	

		#  train clusters until near convergence
		for i in range(iterations):
			print("\nIteration: " + str(i))
			self.assign()
			self.update()
			if self._dp <= self._convergence*self._range:  # if centroids don't move very much
				self.assign()
				break
		print("\nFinished: "+str(round(time()-start, 5)))
			
	def add(self, centroid: np.ndarray) -> None:  # add centroid
		self[centroid] = {"data": np.zeros((self._data.shape[0], 2)), "size": 0}

	def assign(self) -> None:  # assign data points to nearest centroid
		self.clearCentroids()
		centroids = self.getCentroids()
		for pt in self._data:
			closest, closestDist = centroids[0], KMeans.dist(pt, centroids[0])
			for centroid in centroids:
				dist = KMeans.dist(centroid, pt)
				if dist <= closestDist:
					closest, closestDist = centroid, dist
			self[closest]["data"][self[closest]["size"]] = pt
			self[closest]["size"] += 1

	def update(self) -> None:  # update position of centroids
		maxDP = 0
		for centroid in self:
			if self[centroid]["size"] > 0:
				data = self.getPoints(centroid)
				center = data.mean(axis=0)
				del self[centroid.tobytes()]
				dp = self._alpha*(center-centroid)
				print(dp)
				self.add(centroid+dp)
				ds = self.dist(*np.array([[dp[0], 0], [0, dp[1]]]))
				if ds > maxDP:
					maxDP = ds
		self._dp = maxDP
		
	def getCentroids(self) -> np.ndarray:  # return centroid positions
		return np.array([np.frombuffer(centroid) for centroid in self.keys()])

	def clearCentroids(self) -> None:  # clear all data points assigned to centroids
		for centroid in self:
			self[centroid]["data"] = np.zeros((self._data.shape[0], 2))
			self[centroid]["size"] = 0

	@staticmethod
	def dist(pt1: np.ndarray, pt2: np.ndarray) -> np.float64:
		return np.sqrt(np.sum((pt2-pt1)**2))

	@staticmethod
	def rand(low, high, size=None):
		return np.random.uniform(low, high, size=size)


	def items(self) -> list:
		return [(np.frombuffer(centroid), points) for centroid, points in super().items()]

	def getPoints(self, centroid: np.ndarray) -> np.ndarray:
		return self[centroid]["data"][:self[centroid]["size"]]

	def __setitem__(self, centroid: np.ndarray, points: np.ndarray) -> None:
		super().__setitem__(centroid.tobytes(), points)

	def __getitem__(self, centroid: np.ndarray) -> set:
		return super().__getitem__(centroid.tobytes())

	def __iter__(self) -> iter(list()):
		return [np.frombuffer(centroid) for centroid in self.keys()].__iter__()	

def kmeans(data, k):  # testing kmeans
	clusters = KMeans(data, k)
	centroids = clusters.getCentroids()

	plt.figure()
	plt.grid()
	plt.plot(centroids[:,0], centroids[:,1], 's', c="blue", mec="white", ms=10, zorder=2)
	
	colors = {
		0: "green",
		1: "red",
		2: "orange",
		3: "purple",
	}

	c=0
	for centroid in clusters:
		data = clusters.getPoints(centroid)
		print(len(data))
		plt.plot(data[:,0], data[:,1], 'o', c=colors[c], mec="white", ms=7.5, zorder=1)
		c+=1

	plt.xlabel("x")
	plt.ylabel("y")
	
	plt.show()	

	return None





