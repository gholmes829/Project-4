"""
Note:
	Consider having "playlist put togetherness metric" based on how well clustered all songs are.
		Or maybe based on average distance from mean of data

Things to consider:
	Handling 1 or few songs
"""
import numpy as np
import matplotlib.pyplot as plt
import cProfile
from time import process_time as time

class Clusters(dict):
	def __init__(self, data: np.ndarray, k: int = 0, maxK=6, maxIterations: int = 50, samples=10, alpha=0.85, accuracy=4) -> None:
		if not k>=0:
			raise ValueError("K must be greater than or equal to zero")

		super().__init__(self)
		
		# public attributes
		self.data = data
		self.k, self.maxK = k, maxK
		self.alpha = alpha
		self.accuracy = accuracy
		self.score = 0

		self.maxIterations = maxIterations
		self.samples = samples
		self.autoSolve = (k==0)

		# data attributes
		self._bounds = np.array([[data[:,0].min(), data[:,0].max()], [data[:,1].min(), data[:,1].max()]])
		self._xRange, self._yRange = np.diff(self._bounds).flatten()
		self._range = self.dist(*np.array([[self._xRange, 0], [0, self._yRange]]))

		self._convergenceLimit = 1*(10**(-1*self.accuracy))
		self._scoreTolerance = 0.05
		
		# state attributes
		self._dp = 0
		self._prevIteration = {}
		self._isAssigned = False
		self._solved = False

		# evaluation attributes
		self._scores = {}
		
		
		pr = cProfile.Profile()
		pr.enable()
		self._solve()
		pr.disable()
		print()
		pr.print_stats(sort="cumulative")
			
	def keys(self) -> np.ndarray:  # return centroid positions
		return np.array([np.frombuffer(centroid) for centroid in super().keys()])

	def items(self) -> list:
		return [(np.frombuffer(centroid), self._getPoints(centroid)) for centroid, points in super().items()]

	@staticmethod
	def dist(pt1: np.ndarray, pt2: np.ndarray) -> np.float64:
		return np.sqrt(np.sum((pt2-pt1)**2))

	@staticmethod
	def optimizedDist(pt1: np.ndarray, pt2: np.ndarray) -> np.float64:
		return np.sum((pt2-pt1)**2)

	@staticmethod
	def rand(low, high, size=None):
		return np.random.uniform(low, high, size=size)

	def _solve(self):
		if self.k != 0:
			self._singleSolve()
		else:
			self._autoSolve()

		self._solved = True

	def _singleSolve(self):
		print("Solving for K="+str(self.k) + "...")
		optimal = self._optimalPartition(self.k)
		self._revert(optimal)

	def _autoSolve(self):
		print("Using heuristics to auto solve for K...")
		pivot = None
		optimal = None

		for k in range(2, self.maxK+1):
			print("\nAnalyzing K="+str(k))
			if k > 2:  # store current configuration as previous
				self._prevIteration = optimal
				
			optimal = self._optimalPartition(k)
			self._scores[k] = self._silhouette(optimal)
			print("Silhouette score: " + str(self._scores[k]))

			if k > 2:
				dScore = (self._scores[k-1] - self._scores[k])
				if dScore <= 0:  # if new score is better than prev score
					if pivot is not None and (pivot-self._scores[k]) <= 0:  # if pivot is set and new score is better than or euqal to pivot score
						pivot = None
					if k==self.maxK:
						self._simplify()
						self.score = self._scores[k]
				elif dScore <= self._scoreTolerance and (pivot is None or (pivot-self._scores[k]) <= self._scoreTolerance):  # new score is worse but within tolerance
					if pivot is None:
						pivot = self._scores[k-1]
					if k==self.maxK:
						self._simplify()
						self.score = self._scores[k-1]
				else:   # new score is worse and exceeds tolerance
					self._revert(self._prevIteration)
					self.score = self._scores[k-1]
					break

	def _optimalPartition(self, k):
		samples = []
		for i in range(self.samples):
			self.clear()
			self._kmeans(k)
			samples.append(self._simpleCopy())
		
		initialized = False
		best, bestCost = None, 0
		
		for i in range(1, len(samples)):
			cost = self._cost(samples[i])
			if cost == -1:
				continue
				
			elif not initialized:
				best, bestCost = samples[i], cost
				initialized = True
			elif cost <= bestCost:
				best, bestCost = samples[i], cost
		print("Completed randomized sampling...")
		return best

	def _cost(self, copy):
		totalDist = 0
		maxDist = 0
		ptCount = 0
		
		for bufferCentroid, points in copy.items():
			size = len(points)
			ptCount += size
			if size == 0:
				return -1
			centroid = np.frombuffer(bufferCentroid)
			for pt in points:
				dist = Clusters.optimizedDist(pt, centroid)
				totalDist+=dist
				if dist > maxDist:
					maxDist = dist
		print("Cost: "+str((totalDist/size)*(maxDist)) +", Avg: "+ str(totalDist/size) +", Max: " +str(maxDist))
		return (totalDist/ptCount)*(maxDist**2)  # average distance * max distance^2

	def _silhouette(self, partition):
		partitionScore = 0
		centroids = [np.frombuffer(bufferCentroid) for bufferCentroid in partition.keys()]
		for bufferCentroid, points in partition.items():  # for each centroid
			if len(points) > 0: 
				centroidScore = 0
				parent = np.frombuffer(bufferCentroid)
				for pt in points:  # for each point in centroid
					second = self._findSecondCentroid(pt, parent, centroids)  # find closest centroid
					a = self._computeA(pt, partition[bufferCentroid])  # average dist of pt to other points in cluster
					b = self._computeB(pt, partition[second.tobytes()])  # average dist of pt to points in closest non parent cluster
					centroidScore += self._silhouetteCoeffient(a, b)  # (b-a)/max(a, b)
					
				partitionScore += centroidScore/len(points)
			else:
				return -1

		return partitionScore/len(centroids)

	def _silhouetteCoeffient(self, a, b):
		return (b-a)/max(a, b)

	def _computeA(self, pt, points):
		totalDist = 0
		size = len(points) - 1
		for otherPt in points:
			totalDist += Clusters.optimizedDist(pt, otherPt)
		return np.sqrt(totalDist)/size

	def _computeB(self, pt, points):
		totalDist = 0
		size = len(points)
		for otherPt in points:
			totalDist += Clusters.optimizedDist(pt, otherPt)
		return np.sqrt(totalDist)/size

	def _simplify(self):
		simplified = self._simpleCopy()
		self._revert(simplified)

	def _revert(self, copy):
		self.clear()
		for centroid, points in copy.items():
			self[centroid] = points

	def _kmeans(self, k):
		if not k>0:
			raise ValueError("k must be greater than 0")

		self.clear()

		for _ in range(k):  # initialize centroids
			centroid = self._getRandomCentroid()
			self._add(centroid)

		for _ in range(self.maxIterations):  # train clusters until near convergence
			self._assign()
			self._update()
			if self._dp <= self._convergenceLimit*self._range:  # if centroids don't move very much
				self._assign()
				break

	def _getRandomCentroid(self):
		x, y = Clusters.rand(self._bounds[0].min(), self._bounds[0].max()), Clusters.rand(self._bounds[1].min(), self._bounds[1].max())
		return np.array([x, y])

	def _findSecondCentroid(self, pt, parent, centroids):
		closest, closestDist = None, 0
		initialized = False
		for centroid in centroids:
			if not np.all(centroid == parent):
				if not initialized:
					closest, closestDist = centroid, Clusters.optimizedDist(pt, centroid)
					initialized = True
				elif initialized:
					dist = Clusters.optimizedDist(pt, centroid)
					if dist <= closestDist:
						closest, closestDist = centroid, dist
		return closest

	def _add(self, centroid: np.ndarray) -> None:  # add centroid
		self[centroid] = {"data": np.zeros((self.data.shape[0], 2)), "size": 0}

	def _assign(self) -> None:  # assign data points to nearest centroid
		if self._isAssigned:
			self._clearAssignments()
		else:
			self._isAssigned = True
		centroids = self.keys()
		for pt in self.data:
			closest, closestDist = centroids[0], Clusters.optimizedDist(pt, centroids[0])
			for centroid in centroids:
				dist = Clusters.optimizedDist(centroid, pt)
				if dist <= closestDist:
					closest, closestDist = centroid, dist
			self[closest]["data"][self[closest]["size"]] = pt
			self[closest]["size"] += 1

	def _update(self) -> None:  # update position of centroids
		maxDP = 0
		for bufferCentroid in self._bufferKeys():
			if self[bufferCentroid]["size"] > 0:
				centroid = np.frombuffer(bufferCentroid)

				data = self._getPoints(bufferCentroid)
				center = data.mean(axis=0)
				
				dp = self.alpha*(center-centroid)
				ds = self.dist(*np.array([[dp[0], 0], [0, dp[1]]]))

				if ds > maxDP:
					maxDP = ds

				del self[bufferCentroid]
				self._add(centroid+dp)
				
		self._dp = maxDP

	def _getPoints(self, centroid: any) -> np.ndarray:
		if not self._solved:
			return self[centroid]["data"][:self[centroid]["size"]]
		else:
			return self[centroid]

	def _simpleCopy(self):
		copy = {}
		for centroid in self._bufferKeys():
			copy[centroid] = self._getPoints(centroid)
		return copy	

	def _clearAssignments(self) -> None:  # clear all data points assigned to centroids
		for centroid in self:
			self[centroid]["data"] = np.zeros((self.data.shape[0], 2))
			self[centroid]["size"] = 0

	def _bufferKeys(self):
		return super().keys()

	def __setitem__(self, centroid: any, points: np.ndarray) -> None:
		if type(centroid) == np.ndarray:
			super().__setitem__(centroid.tobytes(), points)
		elif type(centroid) == bytes:
			super().__setitem__(centroid, points)
		else:
			raise TypeError("Invalid type: " + str(type(centroid)))

	def __getitem__(self, centroid: any) -> set:
		if type(centroid) == np.ndarray:
			return super().__getitem__(centroid.tobytes())
		elif type(centroid) == bytes:
			return super().__getitem__(centroid)
		else:
			raise TypeError("Invalid type: " + str(type(centroid)))

	def __delitem__(self, centroid: any) -> None:
		if type(centroid) == np.ndarray:
			return super().__delitem__(centroid.tobytes())
		elif type(centroid) == bytes:
			return super().__delitem__(centroid)
		else:
			raise TypeError("Invalid type: " + str(type(centroid)))

	def __iter__(self) -> iter(list()):
		return [np.frombuffer(centroid) for centroid in self.keys()].__iter__()

def kmeans(data, k):  # testing kmeans
	clusters = Clusters(data, k)
	centroids = clusters.keys()
	#initial = clusters.getCentroids(initial=True)

	plt.figure()
	plt.grid()
	plt.plot(centroids[:,0], centroids[:,1], '*', c="blue", mec="white", ms=20, zorder=3, label="final")
	#plt.plot(initial[:,0], initial[:,1], 's', c="blue", mec="white", ms=10, zorder=2, label="initial")
	plt.legend(loc="upper right")
	
	colors = {
		0: "green",
		1: "red",
		2: "orange",
		3: "purple",
		4: "cyan",
		5: "magenta",
	}

	c=0
	for centroid in clusters:
		data = clusters[centroid]
		#print(data)
		plt.plot(data[:,0], data[:,1], 'o', c=colors[c], mec="white", ms=7.5, zorder=1)
		c+=1

	plt.xlabel("x")
	plt.ylabel("y")
	
	plt.show()	

	return None





