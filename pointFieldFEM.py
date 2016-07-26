import numpy as np
from scipy import ndimage
import os
import matplotlib.pyplot as plt

folder = '/media/carl/4ECC-1C44/ComsolData/thickerEndoneurium'
filename1 = 'xP_0.txt'
filename2 = 'xP_180.txt'

fields = [[] for i in range(2)]

fields[0] = np.loadtxt(os.path.join(folder, filename1))
fields[1] = np.loadtxt(os.path.join(folder, filename2))

axonXs = [0,180]
axonXSteps = 2

x = fields[0][:,0]
y = fields[0][:,1]
z = fields[0][:,2]

voltages = []

for i in range(axonXSteps):
    voltages.append(fields[i][:,3])

# sort by coordinate values, x changing fastest, z slowest
orderIndices = np.lexsort((z,y,x))
x=x[orderIndices]
y=y[orderIndices]
z=z[orderIndices]

# get values
xValues = np.unique(x)
yValues = np.unique(y)
zValues = np.unique(z)

# get number of steps
xSteps = len(xValues)
ySteps = len(yValues)
zSteps = len(zValues)

# transform data to 3D-field with integer indices replacing actual coordinate values
fieldImage = np.zeros([xSteps, ySteps, zSteps, axonXSteps])
for axonXInd in range(axonXSteps):
    for xInd in range(xSteps):
        for yInd in range(ySteps):
            for zInd in range(zSteps):
                vIndex = xInd + xSteps*(yInd + zInd*ySteps)
                fieldImage[xInd, yInd, zInd, axonXInd] = voltages[axonXInd][vIndex]

fieldDict = {'fieldImage': fieldImage,
             'x': xValues,
             'y': yValues,
             'z': yValues,
             'axonX': axonXs}

# print fieldImage.shape
def getImageCoords(xValues, yValues, zValues, axonXValues, points):

    # assume equidistant original points

    xMin = min(xValues)
    xMax = max(xValues)
    xNum = len(xValues)

    yMin = min(yValues)
    yMax = max(yValues)
    yNum = len(yValues)

    zMin = min(zValues)
    zMax = max(zValues)
    zNum = len(zValues)

    axonXMin = min(axonXValues)
    axonXMax = max(axonXValues)
    axonXNum = len(axonXValues)

    points = np.array(points)

    if min(points.shape)>1:
        if points.shape[1] > 3:
            points = np.transpose(points)
        xCoords = np.add(points[:, 0], -xMin) / (xMax - xMin) * xNum
        yCoords = np.add(points[:, 1], -yMin)/ (yMax - yMin) * yNum
        zCoords = np.add(points[:, 2], -zMin) / (zMax - zMin) * zNum
        xAxonCoords = np.add(points[:, 3], -axonXMin) / (axonXMax - axonXMin) * axonXNum
    else:
        xCoords = (points[0] - xMin) / (xMax - xMin) * xNum
        yCoords = (points[1] - yMin) / (yMax - yMin) * yNum
        zCoords = (points[2] - zMin) / (zMax - zMin) * zNum
        xAxonCoords = (points[3] - axonXMin) / (axonXMax - axonXMin) * axonXNum

    return np.vstack([xCoords, yCoords, zCoords, xAxonCoords])

def interpolateFromImage(fieldDict, points):

    # first transform coordinates in points into position coordinates
    imageCoords = getImageCoords(fieldDict['x'], fieldDict['y'], fieldDict['z'], fieldDict['axonX'], points)

    # then with new coords to the interpolation
    return  ndimage.map_coordinates(fieldDict['fieldImage'], imageCoords, order=1)

# print getImageCoords(xValues, yValues, zValues, np.array([[1,2,3], [1,2,3], [1,2,3]]))
#
# print ndimage.map_coordinates(fieldImage, [[0.01], [0.01], [0.01]], order=3)
#
# print 'hm'

# print ndimage.map_coordinates(a, [[0.5], [0.5]], order=3)

xPlot = np.linspace(-0.005, 0.005, 100)
xAxonPlot = np.linspace(0, 180, 100)

# points = np.array([np.zeros(100), np.zeros(100), np.zeros(100), xAxonPlot])
points = np.array([xPlot, np.zeros(100), np.zeros(100), np.zeros(100)])
values = interpolateFromImage(fieldDict, points)

plt.plot(xAxonPlot, values)
plt.show()


