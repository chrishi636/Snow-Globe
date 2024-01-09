import maya.cmds as cmds
import random as r
import mtoa.utils as mutils
import mtoa.core as core
import math


################### Method Definitions ###################
def createShadingNode(nameOfNode, typeName, asShader, asTexture=False):
    cmds.shadingNode(typeName, asShader=asShader, asTexture=asTexture, n=nameOfNode)


def createAiStandardSurface(nameOfMat):
    createShadingNode(nameOfMat, "aiStandardSurface", True)
    cmds.setAttr(f"{nameOfMat}.specular", 0)
    # cmds.shadingNode('aiStandardSurface', asShader = True, n = nameOfMat)


def assignMaterial(nameOfObject, nameOfMat):
    cmds.select(nameOfObject)
    cmds.hyperShade(assign=nameOfMat)


def createAndAssignAiStandardSurface(nameOfObject, nameOfMat):
    createAiStandardSurface(nameOfMat)
    assignMaterial(nameOfObject, nameOfMat)


def createTreeLayer(height=25, radius=20, y=135):
    treeName, _ = cmds.polyCone(h=height, r=radius, subdivisionsAxis=14)
    for i in range(0, 14, 2):
        cmds.scale(0.75, 0.75, 0.75, f"{treeName}.vtx[{i}]")
    cmds.rotate(0, height * 2, 0, treeName)
    cmds.move(0, y, 0, treeName)
    cmds.polyExtrudeFacet(f"{treeName}.f[0]", ltz=4)

    assignMaterial(treeName, snowMatName)
    treeMatName = "treeMat"
    createAndAssignAiStandardSurface(f"{treeName}.f[15:28]", treeMatName)
    cmds.setAttr(f"{treeMatName}.baseColor", 0.069, 0.167, 0.102)
    cmds.setAttr(f"{treeMatName}.baseColor", 0.069, 0.167, 0.102)

    cmds.displaySmoothness(
        treeName,
        divisionsU=3,
        divisionsV=3,
        pointsWire=16,
        pointsShaded=4,
        polygonObject=3,
    )

    return treeName


def createSnowmanLayer(radius=20, y=58):
    snowmanBottomName, _ = cmds.polySphere(
        r=radius, subdivisionsAxis=10, subdivisionsHeight=10
    )
    cmds.move(45, y, 20, snowmanBottomName)
    cmds.scale(1, 0.8, 1, snowmanBottomName)
    for i in range(0, 92):
        ranX = r.uniform(-0.6, 0.6)
        ranY = r.uniform(-0.6, 0.6)
        ranZ = r.uniform(-0.6, 0.6)
        cmds.move(ranX, ranY, ranZ, f"{snowmanBottomName}.vtx[{i}]", r=True)
    cmds.displaySmoothness(
        snowmanBottomName,
        divisionsU=3,
        divisionsV=3,
        pointsWire=16,
        pointsShaded=4,
        polygonObject=3,
    )
    assignMaterial(snowmanBottomName, snowMatName)


def createCoal(x, y, z, radius=1.5):
    coalName, _ = cmds.polySphere(r=radius, subdivisionsAxis=6, subdivisionsHeight=6)
    cmds.move(x, y, z, coalName)
    buttonMatName = "blackButtonMat"
    createAndAssignAiStandardSurface(coalName, buttonMatName)
    cmds.setAttr(f"{buttonMatName}.baseColor", 0, 0, 0)
    return coalName


def createOrnament(x, y, z, parent, red=True):
    # flickerSeed = r.randint(-48, 0)

    ornamentName, _ = cmds.polySphere(r=5)
    cmds.parent(ornamentName, parent)
    cmds.move(x, y, z, ornamentName)

    if red:
        redOrnamentMatName = "redOrnamentMat"
        createAndAssignAiStandardSurface(ornamentName, redOrnamentMatName)
        cmds.setAttr(f"{redOrnamentMatName}.base", 1)
        cmds.setAttr(f"{redOrnamentMatName}.baseColor", 1, 0, 0)
        cmds.setAttr(f"{redOrnamentMatName}.metalness", 1)
    else:
        goldOrnamentMatName = "goldOrnamentMat"
        createAndAssignAiStandardSurface(ornamentName, goldOrnamentMatName)
        cmds.setAttr(f"{goldOrnamentMatName}.base", 1)
        cmds.setAttr(f"{goldOrnamentMatName}.baseColor", 1, 0.522, 0)
        cmds.setAttr(f"{goldOrnamentMatName}.metalness", 1)

    return ornamentName


def createStringLightLight(radius, parent, height, a, midpoint, lightMatName, i):
    y = i
    x = ((height - (y - midpoint)) / height) * (radius - 5) * math.cos(a * y)
    z = ((height - (y - midpoint)) / height) * (radius - 5) * math.sin(a * y)

    lightName, _ = cmds.polySphere(r=2)
    assignMaterial(lightName, lightMatName)

    pointLightName = cmds.pointLight(rgb=(1, 0.9, 0.418))
    cmds.setAttr(f"{pointLightName}.aiExposure", 8)
    cmds.setAttr(f"{pointLightName}.aiSamples", 3)

    cmds.move(x, y, z, pointLightName)
    cmds.move(x, y, z, lightName)

    cmds.parent(lightName, parent)
    cmds.parent(pointLightName, parent)


def createConicalStringLights(
    treeTop, treeMiddle, treeBottom, height=75, radius=48, a=100, midpoint=70
):
    lightMatName = "stringLightMat"
    createAiStandardSurface(lightMatName)
    cmds.setAttr(f"{lightMatName}.transmission", 0.8)

    for i in range(75, 100, 2):
        createStringLightLight(
            radius - 5, treeBottom, height, a, midpoint, lightMatName, i
        )
    for i in range(100, 125, 2):
        createStringLightLight(radius, treeMiddle, height, a, midpoint, lightMatName, i)
    for i in range(125, 140, 5):
        createStringLightLight(
            radius + 20, treeTop, height, a, midpoint, lightMatName, i
        )


def calculateRandomCoordinatesWithinSphere(
    radius, centerX=0, centerY=0, centerZ=0, yLowerBound=0
):
    y = r.uniform(
        yLowerBound, centerY + radius
    )  # constrain y by bounds of globe and generate within those bounds

    zMax = math.sqrt(
        radius**2 - (y - centerY) ** 2
    )  # calculate outer bounds of z given randomly generated y
    z = r.uniform(-zMax, zMax)  # randomly assign z within constraints

    xMax = math.sqrt(
        radius**2 - (y - centerY) ** 2 - z**2
    )  # calculate outer bounds of x given y and z
    x = r.uniform(-xMax, xMax)  # randomly assign x within constraints

    return [x, y, z]


def makeCookie(x, y, z, rotX=0, rotY=0, rotZ=0, scaleX=20, scaleY=1.75, scaleZ=20):
    cookieName, _ = cmds.polyCylinder()
    cmds.move(x, y, z, cookieName)
    cmds.rotate(rotX, rotY, rotZ, cookieName)
    cmds.scale(scaleX, scaleY, scaleZ, cookieName)
    cmds.polyExtrudeFacet(f"{cookieName}.f[21]", offset=4)
    cmds.polyExtrudeFacet(f"{cookieName}.f[21]", offset=-2, ltz=2)
    cmds.displaySmoothness(
        cookieName,
        divisionsU=3,
        divisionsV=3,
        pointsWire=16,
        pointsShaded=4,
        polygonObject=3,
    )
    assignMaterial(f"{cookieName}.f[21]", frostingMatName)
    assignMaterial(f"{cookieName}.f[42:61]", frostingMatName)


#################### End Method Definitions ###################

cmds.file(force=True, newFile=True)
# cmds.select(all=True)
# cmds.delete()

# create black and white skydome
skydome = mutils.createLocator("aiSkyDomeLight", asLight=True)
cmds.setAttr("aiSkyDomeLight1.color", 0.091, 0.179, 0.212)
cmds.setAttr("aiSkyDomeLight1.color", 0.167, 0.167, 0.167)
cmds.setAttr("aiSkyDomeLight1.aiExposure", -3.5)
cmds.setAttr("aiSkyDomeLight1.aiSamples", 3)
rampName = cmds.shadingNode("ramp", asTexture=True)
cmds.setAttr("ramp1.colorEntryList[0].position", 0.452)
cmds.setAttr("ramp1.colorEntryList[0].color", 0, 0, 0)
cmds.setAttr("ramp1.colorEntryList[1].position", 0.530)
cmds.setAttr("ramp1.colorEntryList[1].color", 1, 1, 1)
cmds.connectAttr(f"{rampName}.outColor", "aiSkyDomeLight1.color", force=True)

# create front light
frontLightName = cmds.shadingNode("areaLight", asLight=True)
cmds.move(-0.162, 92.666, 239.784, frontLightName)
cmds.scale(100, 100, 100, frontLightName)
cmds.rotate(0.525, -17.671, 13.255, frontLightName)
cmds.setAttr(f"{frontLightName}.color", 0.497, 0.094, 0)
cmds.setAttr(f"{frontLightName}.aiExposure", 14)
cmds.setAttr(f"{frontLightName}.aiSamples", 3)
cmds.setAttr(f"{frontLightName}.decayRate", 2)

cmds.modelEditor(cmds.getPanel(withFocus=True), edit=True, displayLights="all")

# create back light
backLightName = cmds.shadingNode("areaLight", asLight=True)
cmds.move(-355, 60, -355, backLightName)
cmds.scale(225, 225, 225, backLightName)
cmds.rotate(0, -135, 0, backLightName)
cmds.setAttr(f"{backLightName}.color", 0, 0.037, 1)
cmds.setAttr(f"{backLightName}.aiExposure", 16.5)
cmds.setAttr(f"{backLightName}.aiSamples", 3)
cmds.setAttr(f"{backLightName}.decayRate", 2)

cmds.modelEditor(cmds.getPanel(withFocus=True), edit=True, displayLights="all")

# create spot light
spotLightName = cmds.shadingNode("spotLight", asLight=True)
cmds.move(0, 268, 0, spotLightName)
cmds.scale(36, 36, 36, spotLightName)
cmds.rotate(270, 0, 0, spotLightName)
cmds.setAttr(f"{spotLightName}.color", 0.403, 0.701, 1)
cmds.setAttr(f"{spotLightName}.aiExposure", 16.25)
cmds.setAttr(f"{spotLightName}.aiSamples", 3)
cmds.setAttr(f"{spotLightName}.decayRate", 2)

cmds.modelEditor(cmds.getPanel(withFocus=True), edit=True, displayLights="all")

# create under the tree light
treeLight = cmds.shadingNode("areaLight", asLight=True)
cmds.move(7.863, 69, 18, treeLight)
cmds.scale(19.5, 19.5, 19.5, treeLight)
cmds.rotate(-90, 0, 0, treeLight)
cmds.setAttr(f"{treeLight}.color", 1, 0.864, 0.522)
cmds.setAttr(f"{treeLight}.aiExposure", 10)
cmds.setAttr(f"{treeLight}.aiSamples", 3)
cmds.setAttr(f"{treeLight}.decayRate", 2)

# create train light
trainLight = cmds.shadingNode("areaLight", asLight=True)
cmds.move(0, -8.5, 0, trainLight)
cmds.scale(48.5, 48.5, 48.5, trainLight)
cmds.rotate(-90, 0, 0, trainLight)
cmds.setAttr(f"{trainLight}.aiExposure", 16)
cmds.setAttr(f"{trainLight}.aiSamples", 3)

cmds.modelEditor(cmds.getPanel(withFocus=True), edit=True, displayLights="all")

# create table
tableName, _ = cmds.polyCube(subdivisionsWidth=25, subdivisionsDepth=15)
cmds.scale(500, 25, 375, tableName)
cmds.move(0, -41.731, 0, tableName)
cmds.displaySmoothness(
    tableName,
    divisionsU=3,
    divisionsV=3,
    pointsWire=16,
    pointsShaded=4,
    polygonObject=3,
)

tableGold = "tableGoldMat"
tableRed = "tableRedMat"
tableDarkRed = "tableDarkRedMat"
createAndAssignAiStandardSurface(tableName, tableGold)
cmds.setAttr(f"{tableGold}.baseColor", 1, 0.571, 0)
createAndAssignAiStandardSurface(f"{tableName}.f[50:74]", tableRed)
assignMaterial(f"{tableName}.f[100:124]", tableRed)
assignMaterial(f"{tableName}.f[150:174]", tableRed)
assignMaterial(f"{tableName}.f[200:224]", tableRed)
assignMaterial(f"{tableName}.f[250:274]", tableRed)
assignMaterial(f"{tableName}.f[300:324]", tableRed)
assignMaterial(f"{tableName}.f[350:374]", tableRed)
cmds.setAttr(f"{tableRed}.baseColor", 1, 0, 0)
createAndAssignAiStandardSurface(f"{tableName}.f[50:74]", tableRed)
createAiStandardSurface(tableDarkRed)
cmds.setAttr(f"{tableDarkRed}.baseColor", 0.167, 0.015, 0)
for i in range(25, 50, 2):
    for j in range(i, i + 351, 25):
        assignMaterial(f"{tableName}.f[{j}]", tableDarkRed)

# create base of snow globe
baseName, _ = cmds.polyCylinder(r=75, h=15)
cmds.polyExtrudeFacet(f"{baseName}.f[21]", offset=25, ltz=5)
cmds.polyExtrudeFacet(f"{baseName}.f[21]", ltz=0.1)
for i in range(5):
    cmds.polyExtrudeFacet(f"{baseName}.f[21]", ltz=1)

cmds.scale(1.05, 1, 1.05, f"{baseName}.f[62:121]")
cmds.scale(0.5, 0.5, 0.5, f"{baseName}.e[20:39]")
cmds.scale(0.5, 0.5, 0.5, f"{baseName}.e[0:19]")
cmds.move(0, 7, 0, f"{baseName}.f[20]", r=True)
cmds.polyExtrudeFacet(f"{baseName}.f[20]", offset=-8, ltz=5)
cmds.polyExtrudeFacet(f"{baseName}.f[20]", offset=-3, ltz=10)
cmds.polyExtrudeFacet(f"{baseName}.f[20]", ltz=0.5)
cmds.polyExtrudeFacet(f"{baseName}.f[20]", ltz=10)
cmds.polyExtrudeFacet(f"{baseName}.f[20]", ltz=0.5)
cmds.scale(1.3, 1.3, 1.3, baseName)
cmds.move(0, 1, 0, baseName)
cmds.polyExtrudeFacet(f"{baseName}.f[20]", offset=30)
cmds.polyExtrudeFacet(f"{baseName}.f[20]", offset=1)
cmds.polyExtrudeFacet(f"{baseName}.f[20]", ltz=-60)
cmds.displaySmoothness(
    baseName, divisionsU=3, divisionsV=3, pointsWire=16, pointsShaded=4, polygonObject=3
)
cmds.select(f"{baseName}.f[184:187]", f"{baseName}.f[204:207]", f"{baseName}.f[224:227]")
cmds.delete()

# assign red material to base
baseMatName = "redMat"
createAndAssignAiStandardSurface(baseName, baseMatName)
cmds.setAttr(f"{baseMatName}.baseColor", 0.205, 0, 0)
cmds.setAttr(f"{baseMatName}.specular", 0.8)

# create globe
globeName, _ = cmds.polySphere(r=90)
cmds.move(0, 90, 0, globeName)
cmds.delete(f"{globeName}.f[360:379]")
cmds.polyExtrudeFacet(f"{globeName}", thickness=-5)

# assign glass material to globe
globeMatName = "glassMat"
createAndAssignAiStandardSurface(globeName, globeMatName)
cmds.setAttr(f"{globeMatName}.base", 0.25)
cmds.setAttr(f"{globeMatName}.transmission", 0.9)
# cmds.setAttr(f'{globeMatName}.transmissionScatter', .4, .4, .4)
# cmds.setAttr(f'{globeMatName}.transmissionColor', .828, 1, 1)
cmds.setAttr(f"{globeMatName}.specular", 0.5)
cmds.setAttr(f"{globeMatName}.specularRoughness", 0.05)
# cmds.setAttr(f'{globeMatName}.specularIOR', 1.5)
# cmds.setAttr(f'{globeMatName}.thinWalled', True)

# create snow on ground
groundSnowName, _ = cmds.polySphere(r=85)
cmds.move(0, 90, 0, groundSnowName)
cmds.delete(f"{groundSnowName}.f[160:399]")
cmds.scale(0.5, 0.5, 0.5, f"{groundSnowName}.e[160:179]", r=True)
cmds.move(0, -40, 0, f"{groundSnowName}.e[160:179]", r=True)
cmds.polyCloseBorder(f"{groundSnowName}.e[160:179]", ch=True)
for i in range(140, 159):  # for i in range(140, 179):
    cmds.move(0, r.randrange(-8, 8), 0, f"{groundSnowName}.vtx[{i}]", r=True)
cmds.displaySmoothness(
    groundSnowName,
    divisionsU=3,
    divisionsV=3,
    pointsWire=16,
    pointsShaded=4,
    polygonObject=3,
)

# assign white material to ground snow
snowMatName = "snowMaterial"
createAndAssignAiStandardSurface(groundSnowName, snowMatName)
cmds.setAttr(f"{snowMatName}.baseColor", 0.914, 1, 1)
cmds.setAttr(f"{snowMatName}.emission", 0.15)

# add falling snow
radius = 75 # this will define the horizontal radius in which snow is created
yMid = 100 # defines center of sphere
for i in range(100):
    # create snowflake within globe
    [x, y, z] = calculateRandomCoordinatesWithinSphere(radius, 0, yMid, 0, 60)
    snowFlakeName, _ = cmds.polyCube()

    # assign snow material to snowflake
    cmds.select(snowFlakeName)
    cmds.hyperShade(assign = snowMatName)

    #animate snowflake
    cmds.setKeyframe(snowFlakeName, at = 'translateX', v = x, t=[0])
    cmds.setKeyframe(snowFlakeName, at = 'translateZ', v = z, t=[0])

    for j in range(0, 722,3):
        cmds.setKeyframe(snowFlakeName, at = 'translateY', v = y, t=[j])
        newY = y - 3
        cmds.setKeyframe(snowFlakeName, at = 'translateY', v = newY, t=[j + 2])
        if newY < 55:
            cmds.setKeyframe(snowFlakeName, at = 'translateX', v = x, t=[j + 1.9])
            cmds.setKeyframe(snowFlakeName, at = 'translateZ', v = z, t=[j + 1.9])

            [x, newY, z] = calculateRandomCoordinatesWithinSphere(radius, 0, yMid, 0, 90)
            cmds.setKeyframe(snowFlakeName, at = 'translateX', v = x, t=[j + 2])
            cmds.setKeyframe(snowFlakeName, at = 'translateZ', v = z, t=[j + 2])
        cmds.keyTangent(snowFlakeName, itt = 'linear', ott = 'linear', time = (0, 722))
        y = newY

# create tree
trunkName, _ = cmds.polyCylinder(h=25, r=7)
trunkMatName = "trunkMat"
createAndAssignAiStandardSurface(trunkName, trunkMatName)
cmds.setAttr(f"{trunkMatName}.baseColor", 0.141, 0.079, 0.052)
cmds.move(0, 60, 0, trunkName)

treeTopName = createTreeLayer()
for i in range(1, 721, 48):
    cmds.setKeyframe(treeTopName, at="rotateX", v=-2, t=[i])
    cmds.setKeyframe(treeTopName, at="rotateX", v=2, t=[i + 24])
treeMiddleName = createTreeLayer(35, 35, 115)
for i in range(-8, 721, 48):
    cmds.setKeyframe(treeMiddleName, at="rotateX", v=1, t=[i])
    cmds.setKeyframe(treeMiddleName, at="rotateX", v=-1, t=[i + 24])
treeBottomName = createTreeLayer(50, 50, 95)
for i in range(-24, 721, 48):
    cmds.setKeyframe(treeBottomName, at="rotateX", v=2, t=[i])
    cmds.setKeyframe(treeBottomName, at="rotateX", v=-2, t=[i + 24])

# create ornaments
flag = True
for x in [-24, 24]:
    for z in [-24, 24]:
        if flag:
            red = True
        else:
            red = False
            if x == -24:
                flag = not flag
        flag = not flag
        ornamentName = createOrnament(x, 83, z, treeBottomName, red)

createOrnament(-8, 135, -8, treeTopName, False)
createOrnament(8, 135, 8, treeTopName)
createOrnament(22, 110, 0, treeMiddleName)
createOrnament(-22, 110, 0, treeMiddleName)
createOrnament(0, 110, 22, treeMiddleName, False)
createOrnament(0, 110, -22, treeMiddleName, False)

# animate garland
height = 85
radius = 45
a = 100
midpoint = 70

curvePoints = []
for i in range(70, 140, 1):
    y = i
    x = ((height - (y - midpoint)) / height) * (radius) * math.cos(a * y)
    z = ((height - (y - midpoint)) / height) * (radius) * math.sin(a * y)

    curvePoints.append([-x, y, -z])

garlandPath = cmds.curve(p=curvePoints[::-1])

garlandMatName = "garlandMat"
createAiStandardSurface(garlandMatName)
cmds.setAttr(f"{garlandMatName}.baseColor", 1, 1, 0.5)

for i in range(350):
    garlandPiece, _ = cmds.polySphere(r=2)

    assignMaterial(garlandPiece, garlandMatName)

    # start = 1 + 12 * i
    garlandAnimName = cmds.pathAnimation(
        garlandPiece,
        c=garlandPath,
        su=0,
        # eu=i / 5
        eu = 66 / 350 * i,
        # stu=100,
        stu = 0,
        # etu=180,
        etu = i,
        followAxis="x",
        upAxis="y",
    )
    # cmds.keyTangent(garlandAnimName, itt="linear", ott="linear", time=(0, 720))
    cmds.keyTangent(garlandAnimName, itt="flat", ott="step", time=(0, 720))
cmds.hide(garlandPath)

# create snowman
createSnowmanLayer()
createSnowmanLayer(11, 78)
createSnowmanLayer(7, 90)

createCoal(49.982, 69.609, 33.316)
createCoal(48.417, 75.936, 28.727)
createCoal(48.417, 82.473, 28.727)

eyeOne = createCoal(44.635, 92.051, 25.95, 1)  # for eyes
eyeTwo = createCoal(49.028, 92.051, 24.208, 1)
for i in [20, 25, 120, 400, 640, 700]:
    cmds.setKeyframe(eyeOne, at="scaleY", v=1, t=[i])
    cmds.setKeyframe(eyeOne, at="scaleY", v=0.2, t=[i + 3])
    cmds.setKeyframe(eyeOne, at="scaleY", v=1, t=[i + 4])
    cmds.setKeyframe(eyeTwo, at="scaleY", v=1, t=[i])
    cmds.setKeyframe(eyeTwo, at="scaleY", v=0.2, t=[i + 3])
    cmds.setKeyframe(eyeTwo, at="scaleY", v=1, t=[i + 4])

noseName, _ = cmds.polyCone(h=5)
cmds.move(47.8, 91.5, 27.5, noseName)
cmds.rotate(87.8, 16.7, -0.63, noseName)
noseMatName = "noseMat"
createAndAssignAiStandardSurface(noseName, noseMatName)
cmds.setAttr(f"{noseMatName}.baseColor", 0.619, 0.323, 0)

hatName, _ = cmds.polyCylinder(height=2, subdivisionsAxis=8)
cmds.scale(0.8, 0.8, 0.8, f"{hatName}.vtx[8:15]")
cmds.polyExtrudeFacet(f"{hatName}.f[8]", offset=2.5)
cmds.polyExtrudeFacet(f"{hatName}.f[8]", ltz=0.75)
createAndAssignAiStandardSurface(hatName, "hatMatName")
cmds.setAttr("hatMatName.baseColor", 0, 0, 0)
cmds.move(50.3, 99.3, 20, hatName)
cmds.rotate(-16, -5.5, -19.5, hatName)
cmds.scale(1.495, 1.495, 1.495, hatName)
for i in range(0, 721, 36):
    cmds.setKeyframe(hatName, at="translateY", v=98.5, t=[i])
    cmds.setKeyframe(hatName, at="translateY", v=99.5, t=[i + 18])

scarfName, _ = cmds.polyTorus(
    r=0.75, sectionRadius=0.1, subdivisionsAxis=10, subdivisionsHeight=10
)
cmds.move(45.5, 86.3, 19.8, scarfName)
cmds.scale(10, 20, 10, scarfName)
cmds.polyExtrudeFacet(f"{scarfName}.f[67]", ltz=2)
cmds.polyExtrudeFacet(f"{scarfName}.f[67]")
cmds.move(2, -5, 2, f"{scarfName}.f[67]", r=True)
cmds.polyExtrudeFacet(f"{scarfName}.f[67]")
cmds.move(0, -10, 0, f"{scarfName}.f[67]", r=True)
cmds.displaySmoothness(
    scarfName,
    divisionsU=3,
    divisionsV=3,
    pointsWire=16,
    pointsShaded=4,
    polygonObject=3,
)
scarfMatName = "scarfMat"
createAndAssignAiStandardSurface(scarfName, scarfMatName)
cmds.setAttr(f"{scarfMatName}.baseColor", 0.205, 0, 0)
for i in range(0, 721, 100):
    for edge in [210, 212, 214, 215]:
        cmds.move(-2, 0, 0, f"{scarfName}.e[{edge}]", r = True)
        cmds.setKeyframe(f"{scarfName}.e[{edge}]", t=[i])
        cmds.move(2, 0, 0, f"{scarfName}.e[{edge}]", r = True)
        cmds.setKeyframe(f"{scarfName}.e[{edge}]", t=[i + 50])
    for edge in [216, 220, 223, 222]:
        cmds.move(-3, 0, 0, f"{scarfName}.e[{edge}]", r = True)
        cmds.setKeyframe(f"{scarfName}.e[{edge}]", t=[i - 25])
        cmds.move(3, 0, 0, f"{scarfName}.e[{edge}]", r = True)
        cmds.setKeyframe(f"{scarfName}.e[{edge}]", t=[i + 25])

# add star on top of tree
starName, _ = cmds.polyCylinder(subdivisionsAxis=10)
cmds.scale(
    0.46,
    1,
    0.46,
    f"{starName}.e[20]",
    f"{starName}.e[22]",
    f"{starName}.e[24]",
    f"{starName}.e[26]",
    f"{starName}.e[28]",
)
# cmds.scale(1, 0.2, 1, starName)
cmds.displaySmoothness(
    starName, divisionsU=3, divisionsV=3, pointsWire=16, pointsShaded=4, polygonObject=3
)
cmds.scale(11.665, 2.33, 11.665, starName)
cmds.move(0, 147.797, 0, starName)
cmds.rotate(100.395, 41.931, 21.67)

starMatName = "starMat"
createAndAssignAiStandardSurface(starName, starMatName)
cmds.setAttr(f"{starMatName}.baseColor", 1, 1, 0.25)
cmds.setAttr(f"{starMatName}.transmission", 0.9)
cmds.parent(starName, treeTopName)

pointLightName = cmds.pointLight(rgb=(1, 1, 0.218))
cmds.setAttr(f"{pointLightName}.aiExposure", 10.5)
cmds.setAttr(f"{pointLightName}.decayRate", 2)
cmds.move(0, 147.797, 0, pointLightName)

# create string lights
createConicalStringLights(treeTopName, treeMiddleName, treeBottomName)

# make presents
presentName, _ = cmds.polyCube(subdivisionsWidth=3, subdivisionsDepth=3)

goldWrappingMatName = "goldWrappingMat"
createAndAssignAiStandardSurface(presentName, goldWrappingMatName)
cmds.setAttr(f"{goldWrappingMatName}.baseColor", 0.947, 0.776, 0.371)
cmds.setAttr(f"{goldWrappingMatName}.metalness", 0.75)
cmds.setAttr(f"{goldWrappingMatName}.specularColor", 1, 0.982, 0.753)

blackRibbonMatName = "blackRibbonMat"
createAiStandardSurface(blackRibbonMatName)
cmds.setAttr(f"{blackRibbonMatName}.baseColor", 0.025, 0, 0)
for i in [
    f"{presentName}.f[1]",
    f"{presentName}.f[4]",
    f"{presentName}.f[6:8]",
    f"{presentName}.f[10]",
    f"{presentName}.f[13]",
    f"{presentName}.f[25]",
    f"{presentName}.f[28]",
]:
    assignMaterial(i, blackRibbonMatName)

cmds.polyExtrudeFacet(
    f"{presentName}.f[1]",
    f"{presentName}.f[4]",
    f"{presentName}.f[6:8]",
    f"{presentName}.f[10]",
    f"{presentName}.f[13]",
    f"{presentName}.f[25]",
    f"{presentName}.f[28]",
    ltz=0.05,
)
cmds.polyBevel3(
    presentName,
    fraction=1,
    offsetAsFraction=True,
    chamfer=False,
    subdivideNgons=1,
    mergeVertices=1,
    mergeVertexTolerance=0.0001,
)
cmds.displaySmoothness(
    presentName,
    divisionsU=3,
    divisionsV=3,
    pointsWire=16,
    pointsShaded=4,
    polygonObject=3,
)

cmds.move(1.7, 52.2, 30.9, presentName)
cmds.scale(16, 16, 16, presentName)

present2Name, _ = cmds.polyCylinder(height=1, subdivisionsCaps=1)

assignMaterial(present2Name, blackRibbonMatName)

cmds.polyExtrudeFacet(
    f"{present2Name}.f[1:2]",
    f"{present2Name}.f[6:7]",
    f"{present2Name}.f[11:12]",
    f"{present2Name}.f[16:17]",
    f"{present2Name}.f[41:42]",
    f"{present2Name}.f[46:47]",
    f"{present2Name}.f[51:52]",
    f"{present2Name}.f[56:57]",
    ltz=0.05,
)
cmds.displaySmoothness(
    present2Name,
    divisionsU=3,
    divisionsV=3,
    pointsWire=16,
    pointsShaded=4,
    polygonObject=3,
)

for i in [
    f"{present2Name}.f[1:2]",
    f"{present2Name}.f[6:7]",
    f"{present2Name}.f[11:12]",
    f"{present2Name}.f[16:17]",
    f"{present2Name}.f[41:42]",
    f"{present2Name}.f[46:47]",
    f"{present2Name}.f[51:52]",
    f"{present2Name}.f[56:57]",
    f"{present2Name}.f[56:57]",
    f"{present2Name}.f[56:57]",
    f"{present2Name}.f[56:57]",
    f"{present2Name}.f[75:77]",
    f"{present2Name}.f[73]",
    f"{present2Name}.f[69:71]",
    f"{present2Name}.f[67]",
    f"{present2Name}.f[63:65]",
    f"{present2Name}.f[61]",
    f"{present2Name}.f[79]",
    f"{present2Name}.f[81:83]",
]:
    assignMaterial(i, goldWrappingMatName)

cmds.move(7.7, 50.5, 15.4, present2Name)
cmds.scale(6.2, 6.2, 6.2, present2Name)
cmds.rotate(26, -8, -65.6, present2Name)

present3Name, _ = cmds.polyCube(subdivisionsWidth=3, subdivisionsDepth=3)

assignMaterial(present3Name, blackRibbonMatName)

for i in [
    f"{present3Name}.f[1]",
    f"{present3Name}.f[4]",
    f"{present3Name}.f[6:8]",
    f"{present3Name}.f[10]",
    f"{present3Name}.f[13]",
    f"{present3Name}.f[25]",
    f"{present3Name}.f[28]",
]:
    assignMaterial(i, goldWrappingMatName)

cmds.polyExtrudeFacet(
    f"{present3Name}.f[1]",
    f"{present3Name}.f[4]",
    f"{present3Name}.f[6:8]",
    f"{present3Name}.f[10]",
    f"{present3Name}.f[13]",
    f"{present3Name}.f[25]",
    f"{present3Name}.f[28]",
    ltz=0.05,
)
cmds.polyBevel3(
    present3Name,
    fraction=1,
    offsetAsFraction=True,
    chamfer=False,
    subdivideNgons=1,
    mergeVertices=1,
    mergeVertexTolerance=0.0001,
)
cmds.displaySmoothness(
    present3Name,
    divisionsU=3,
    divisionsV=3,
    pointsWire=16,
    pointsShaded=4,
    polygonObject=3,
)

cmds.move(-14.3, 52.5, 8.692, present3Name)
cmds.scale(9.5, 27.053, 9.5, present3Name)

# cookies and milk
milkGlassName, _ = cmds.polyCylinder()
cmds.move(125, 2, -20, milkGlassName)
cmds.scale(18, 32, 18, milkGlassName)
cmds.scale(1.3, 1.3, 1.25, f"{milkGlassName}.f[21]")
cmds.polyExtrudeFacet(f"{milkGlassName}.f[21]", offset=4.5)
cmds.polyExtrudeFacet(f"{milkGlassName}.f[21]", ltz=-65)
cmds.scale(0.85, 0.85, 0.85, f"{milkGlassName}.f[21]")
assignMaterial(milkGlassName, globeMatName)

milkName, _ = cmds.polyCylinder()
cmds.move(125, -1.35, -20, milkName)
cmds.scale(14, 17, 14, milkName)
cmds.scale(1.25, 1, 1.25, f"{milkName}.f[21]")
milkMatName = "milkMat"
createAndAssignAiStandardSurface(milkName, milkMatName)
cmds.setAttr(f"{milkMatName}.baseColor", 1, 1, 1)

plateName, _ = cmds.polyCylinder()
cmds.move(187, -26, 18, plateName)
cmds.scale(42, 3, 42, plateName)
cmds.polyExtrudeFacet(f"{plateName}.f[21]", offset=8, ltz=-4)
cmds.displaySmoothness(
    plateName,
    divisionsU=3,
    divisionsV=3,
    pointsWire=16,
    pointsShaded=4,
    polygonObject=3,
)

frostingMatName = "frostingMat"
createAiStandardSurface(frostingMatName)
cmds.setAttr(f"{frostingMatName}.baseColor", 1, 0, 0)

makeCookie(170, -24, 16)
makeCookie(193, -22, 30, 14)
makeCookie(196, -23, 7, -3.4, 0.8, -11.5)

# make and animate a train
trainMatName = "trainMat"
createAiStandardSurface(trainMatName)
cmds.setAttr(f"{trainMatName}.baseColor", 0.05, 0.05, 0.05)

trainFrontName, _ = cmds.polyCylinder(subdivisionsHeight=3)
cmds.polyExtrudeFacet(f"{trainFrontName}.f[28:29]", ltz=1.5)
cmds.polyExtrudeFacet(f"{trainFrontName}.f[61]", offset=0.2)
cmds.polyExtrudeFacet(f"{trainFrontName}.f[61]", ltz=0.5)
cmds.scale(6, 6, 6, trainFrontName)
assignMaterial(trainFrontName, trainMatName)

trainPath, _ = cmds.circle()
cmds.scale(54, 54, 54, trainPath)
cmds.move(0, -18, 0, trainPath)
cmds.rotate(-90, 90, 0, trainPath)

motionPaths = []
trainPathAnimName = cmds.pathAnimation(
    trainFrontName,
    c=trainPath,
    stu=1,
    etu=240,
    followAxis="y",
    upAxis="x",
    inverseUp=True,
)  # start euler, end euler, start time, end time
motionPaths.append(trainPathAnimName)
cmds.keyTangent(
    trainPathAnimName, itt="linear", ott="linear", time=(0, 720)
)  # itt = in tangent type

for i in range(1, 4):
    trainCar, _ = cmds.polyCube()
    cmds.scale(15, 9, 9, trainCar)
    assignMaterial(trainCar, trainMatName)

    start = 1 + 12 * i
    trainCarAnimName = cmds.pathAnimation(
        trainCar,
        c=trainPath,
        stu=start,
        etu=start + 240,
        followAxis="x",
        upAxis="y",
    )
    cmds.keyTangent(trainCarAnimName, itt="linear", ott="linear", time=(0, 720))
    motionPaths.append(trainCarAnimName)

for motionPath in motionPaths:
    cmds.selectKey(f'{motionPath}_uValue', time = (1,240) )
    cmds.setInfinity( pri='cycle', poi='cycle')

# PENGUIN
penguinName, _ = cmds.polyCylinder(subdivisionsAxis=6)
cmds.polyExtrudeFacet(f"{penguinName}.f[7]", offset=0.5, ltz=0.7)
cmds.move(-30, 58, 40, penguinName)
cmds.scale(15.2, 12, 15.2, penguinName)

penguinBlack = "penguinBlackMat"
createAndAssignAiStandardSurface(penguinName, penguinBlack)
cmds.setAttr(f"{penguinBlack}.baseColor", 0.02, 0.02, 0.02)

penguinWhite = "penguinWhiteMat"
createAndAssignAiStandardSurface(f"{penguinName}.f[3:4]", penguinWhite)
assignMaterial(f"{penguinName}.f[11:12]", penguinWhite)
cmds.setAttr(f"{penguinWhite}.baseColor", 1, 1, 1)

penguinEyeOne = createCoal(-30.364, 73.457, 48.257, 2)  # for eyes
penguinEyeTwo = createCoal(-22.228, 73.457, 44.627, 2)
cmds.parent(penguinEyeOne, penguinName)
cmds.parent(penguinEyeTwo, penguinName)

cmds.displaySmoothness(
    penguinName,
    divisionsU=3,
    divisionsV=3,
    pointsWire=16,
    pointsShaded=4,
    polygonObject=3,
)

for i in range(-5, 700, 48):
    cmds.setKeyframe(penguinName, at="rotateZ", v=-10, t=[i])
    cmds.setKeyframe(penguinName, at="rotateZ", v=10, t=[i + 24])

# camera
cmds.move(203, 101, 237, "perspShape")
cmds.rotate(-2.738, 41, 0, "perspShape")

cmds.playbackOptions( minTime='0sec', maxTime='30sec' )

# # TODO:
# move hat to other side
# add arms
### make him blink
### add garland and animate
## add star on tree
# background objects
### fix lighting
### add presents under tree
### train moving in circle?
# add sva logo to globe base
### animate ornaments (parent to tree?)
# animate scarf
# add wind that blows scarf and snow?
# add holly on base
# plaid scarf
### add cookies and milk on table?
# tiny santa flying in background
# holding a tiny mug of hot chocolate
# gifts open with a little teddy bear inside
### cutout in base with train
# environment lights to reflect on glass
# ribbon, scissors, tape, boxes scattered on table
# add a melted snowman on other side
### PENGUINS
