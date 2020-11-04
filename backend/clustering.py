"""
File: kmeans.py
Author: Grant Holmes
Date: 11/04/20
Description: Uses extension of kmeans clustering alongside silhouette coefficient scoring to organize nth dimensional data into k clusters. Can also auto solve for k.
"""
import numpy as np

class Clusters(dict):
	"""
	Uses kmeans clustering and silhoutte coefficient scoring to find clusters amongst data.
	"""
	def __init__(self, data: np.ndarray, k: int = None, maxK=10, maxIterations: int = 50, samples=10, alpha=0.85, accuracy=4) -> None:
		if not (k is None or k>=0):
			raise ValueError("K must be greater than or equal to zero")
		if not (data.shape[0] > 1):
			raise ValueError("Data must have greater that one point")
		super().__init__(self)
		# public attributes
		self.data = data
		self.k, self.maxK = k, maxK
		self.alpha = alpha
		self.accuracy = accuracy
		self.partitionQuality = 0

		self.orderedData = None
		self.orderedScores = None
		
		self.rawScoreMin, self.rawScoreMax = None, None
		self.rawScoreAvg = None
		self.scoreAvg = None

		self.maxIterations = maxIterations
		self.samples = samples
		self.autoSolve = k is None

		# data attributes
		self._center = self.data.mean(axis=0)
		self._bounds = np.zeros((self.data.shape[1], 2))
		for dimension in range(len(self._bounds)):
			self._bounds[dimension][0] = self.data[:,dimension].min()
			self._bounds[dimension][1] = self.data[:,dimension].max()

		self._ranges = np.diff(self._bounds).flatten()

		space = np.zeros((2, self.data.shape[1]))
		for dimension in range(len(self._bounds)):
			space[1][dimension] = self._ranges[dimension]
			
		self._range = self.dist(space[0], space[1])
		
		self._convergenceLimit = 1*(10**(-1*self.accuracy))
		self._silhouetteThreshold = 0.0375
		
		# state attributes
		self._dp = 0
		self._prevIteration = {}
		self._isAssigned = False
		self._solved = False

		# evaluation attributes
		self._silhouettes = {}
		
		self._solve()
		self._generateScores()
			
	def keys(self) -> np.ndarray:  # return centroid positions
		return np.array([np.frombuffer(centroid) for centroid in super().keys()])

	def items(self) -> list:
		return [(np.frombuffer(centroid), self._getPoints(centroid)) for centroid, points in super().items()]

	def split(self, threshold):  # rework to use score
		valid, invalid = np.zeros(self.data.shape), np.zeros(self.data.shape)
		numValid, numInvalid = 0, 0
		for centroid, points in self.items():
			cache = {}
			localMax = 0
			for pt in points:
				dist = Clusters.dist(centroid, pt)
				cache[pt.tobytes()] = dist
				if dist > localMax:
					localMax = dist
			for bufferPt, dist in cache.items():
				if dist > threshold*localMax:
					invalid[numInvalid] = np.frombuffer(bufferPt)
					numInvalid += 1
				else:			
					valid[numValid] = np.frombuffer(bufferPt)
					numValid += 1
		return valid[:numValid], invalid[:numInvalid]

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
		if self.k is not None:
			self._singleSolve()
		else:
			self._autoSolve()

		self._solved = True

	def _singleSolve(self):
		optimal = self._optimalPartition(self.k)
		self._revert(optimal)

	def _autoSolve(self):
		pivot = None
		optimal = None

		for k in range(2, self.maxK+1):
			if k > 2:  # store current configuration as previous
				self._prevIteration = optimal
				
			optimal = self._optimalPartition(k)
			self._silhouettes[k] = self._silhouette(optimal)

			if k > 2:
				dScore = (self._silhouettes[k-1] - self._silhouettes[k])
				if dScore <= 0:  # if new score is better than prev score
					if pivot is not None and (pivot-self._silhouettes[k]) <= 0:  # if pivot is set and new score is better than or euqal to pivot score
						pivot = None
					if k==self.maxK:
						self._simplify()
						self.k = k
						self.partitionQuality = self._silhouettes[k]
				elif dScore <= self._silhouetteThreshold and (pivot is None or (pivot-self._silhouettes[k]) <= self._silhouetteThreshold):  # new score is worse but within tolerance
					if pivot is None:
						pivot = self._silhouettes[k-1]
					if k==self.maxK:
						self._simplify()
						self.k = k-1
						self.partitionQuality = self._silhouettes[k-1]
				else:   # new score is worse and exceeds tolerance
					self._revert(self._prevIteration)
					self.k = k-1
					self.partitionQuality = self._silhouettes[k-1]
					break

	def _optimalPartition(self, k):
		samples = []
		for i in range(self.samples):
			self.clear()
			self._kmeans(k)
			samples.append(self._simpleCopy())
		
		initialized = False
		best, bestCost = None, 0
		
		for i in range(len(samples)):
			cost = self._cost(samples[i])
			if cost == -1:
				continue
				
			elif not initialized:
				best, bestCost = samples[i], cost
				initialized = True
			elif cost <= bestCost:
				best, bestCost = samples[i], cost
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

		return (totalDist/ptCount)*(maxDist**2)  # average distance * max distance^2

	def _silhouette(self, partition):
		if partition is None:
			return -1
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
		if size == 0:
			return 0
		for otherPt in points:
			totalDist += Clusters.optimizedDist(pt, otherPt)
		return np.sqrt(totalDist)/size

	def _computeB(self, pt, points):
		totalDist = 0
		size = len(points)
		for otherPt in points:
			totalDist += Clusters.optimizedDist(pt, otherPt)
		return np.sqrt(totalDist)/size

	def _generateScores(self):
		size = 0
		scores = np.zeros(self.data.shape[0])
		data =  np.zeros(self.data.shape)

		for centroid, points in self.items():
			clusterDistance = {
				"avg": 0,
				"total": 0,
				"max": 0,	
			}
			clusterSize = len(points)
			cache = {}

			for pt in points:
				distCentroidPt = Clusters.dist(centroid, pt)
				clusterDistance["total"] += distCentroidPt
				cache[pt.tobytes()] = distCentroidPt
				if distCentroidPt > clusterDistance["max"]:
					clusterDistance["max"] = distCentroidPt

			clusterDistance["avg"] = clusterDistance["total"]/clusterSize

			for bufferPt, distCentroidPt in cache.items():
				pt = np.frombuffer(bufferPt)
				distFromCenter = Clusters.optimizedDist(pt, self._center)
				score = self._score(pt, distCentroidPt, clusterSize, clusterDistance["max"], clusterDistance["avg"], distFromCenter)
				scores[size] = score
				data[size] = pt
				size += 1

		minScore, maxScore = scores.min(), scores.max()
		avgScore = scores.mean()
		scale = lambda pt: ((pt-minScore)/(maxScore-minScore))*100
		normalized = np.array(list(map(scale, scores)))
		
		order = normalized.argsort()
		self.orderedScores = normalized[order]
		self.orderedData = (data.T[:,order]).T

		self.rawScoreMin = minScore
		self.rawScoreMax = maxScore
		self.rawScoreAvg = avgScore
		self.scoreAvg = np.mean(normalized)

	def _score(self, pt, distCentroidPt, clusterSize, clusterMax, avgClusterDist, distFromCenter):
		relativeClusterSize = (clusterSize/(self.data.shape[0]/self.k)) 
		relativeDist = (distCentroidPt/clusterMax)
		return (relativeClusterSize**2)*(np.sqrt(relativeDist**3))*avgClusterDist*(distFromCenter**2)

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
		coords = np.zeros(self.data.shape[1])
		for dimension in range(self.data.shape[1]):
			coords[dimension] = Clusters.rand(self._bounds[dimension].min(), self._bounds[dimension].max())
		return coords

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
		self[centroid] = {"data": np.zeros((self.data.shape[0], self.data.shape[1])), "size": 0}

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
		bufferCentroids = self._bufferKeys()
	
		for bufferCentroid in bufferCentroids:
			if self[bufferCentroid]["size"] > 0:
				centroid = np.frombuffer(bufferCentroid)

				data = self._getPoints(bufferCentroid)
				center = data.mean(axis=0)
				
				dp = self.alpha*(center-centroid)
				ds = self.dist(np.zeros(self.data.shape[1]), dp)

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
			self[centroid]["data"] = np.zeros((self.data.shape[0], self.data.shape[1]))
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

