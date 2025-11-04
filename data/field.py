import os
from random import randint


class GameEngine(object):

    def __init__(self):

        self.levelPelletRemaining = 0
        self.levelObjects = [[levelObject("empty") for j in range(32)] for i in range(28)]   # Generar objetos vacíos de 28x32
        self.movingObjectPacman = movingObject("Pacman")
        self.movingObjectGhosts = [movingObject("Ghost") for n in range(4)]

        self.levelObjectNamesBlocker = ["wall", "cage"]
        self.levelObjectNamesPassable = ["empty", "pellet", "powerup"]


    def levelGenerate(self, level):
        # Establecer un directorio para el archivo de recursos
        pathCurrentDir = os.path.dirname(__file__)  # directorio de script actual
        pathRelDir = "../resource/level{}.txt".format(level)
        pathAbsDir = os.path.join(pathCurrentDir, pathRelDir)

        levelFile = open(pathAbsDir, encoding="utf-8")
        levelLineNo = 0

        # leer línea por línea con readlines(), 'levelLine' guarda temporalmente la cadena
        for levelLine in levelFile.readlines():

            levelLineSplit = list(levelLine) # Divide la línea de nivel en caracteres

            # generar objetos de nivel
            for i in range(28):

                if levelLineSplit[i] == "_":    # pasaje
                    self.levelObjects[i][levelLineNo].name = "empty"
                elif levelLineSplit[i] == "#":  # pared
                    self.levelObjects[i][levelLineNo].name = "wall"
                elif levelLineSplit[i] == "$":  # punto de aparición de fantasma
                    self.levelObjects[i][levelLineNo].name = "cage"


                elif levelLineSplit[i] == ".":  # pellet de puntuación
                    self.levelObjects[i][levelLineNo].name = "pellet"

                    # Comprobar cuántos pellets hay en el nivel
                    if self.levelObjects[i][levelLineNo].isDestroyed == False:
                        self.levelPelletRemaining += 1
                    else:
                        pass


                elif levelLineSplit[i] == "*":  # power pellet
                    self.levelObjects[i][levelLineNo].name = "powerup"

                    # Comprobando cuántas bolitas hay en el nivel
                    if self.levelObjects[i][levelLineNo].isDestroyed == False:
                        self.levelPelletRemaining += 1
                    else:
                        pass


                elif levelLineSplit[i] == "@":  # pacman
                    self.levelObjects[i][levelLineNo].name = "empty"

                    # Indica la coordenada inicial
                    self.movingObjectPacman.coordinateRel[0] = i
                    self.movingObjectPacman.coordinateRel[1] = levelLineNo
                    self.movingObjectPacman.coordinateAbs[0] = i * 4
                    self.movingObjectPacman.coordinateAbs[1] = levelLineNo * 4


                elif levelLineSplit[i] == "&":  # fantasma libre
                    self.levelObjects[i][levelLineNo].name = "empty"

                    # encontrar un fantasma inactivo y darle la coordenada inicial
                    for n in range(4):
                        if self.movingObjectGhosts[n].isActive == False:
                            self.movingObjectGhosts[n].isActive = True
                            self.movingObjectGhosts[n].isCaged = False
                            self.movingObjectGhosts[n].coordinateRel[0] = i
                            self.movingObjectGhosts[n].coordinateRel[1] = levelLineNo
                            self.movingObjectGhosts[n].coordinateAbs[0] = i * 4
                            self.movingObjectGhosts[n].coordinateAbs[1] = levelLineNo * 4
                            break   # interrumpir el bucle actual (con el generador 'n')

                elif levelLineSplit[i] == "%":  # fantasma enjaulado
                    self.levelObjects[i][levelLineNo].name = "empty"

                    # encontrar un fantasma inactivo y darle la coordenada inicial
                    for n in range(4):
                        if self.movingObjectGhosts[n].isActive == False:
                            self.movingObjectGhosts[n].isActive = True
                            self.movingObjectGhosts[n].coordinateRel[0] = i
                            self.movingObjectGhosts[n].coordinateRel[1] = levelLineNo
                            self.movingObjectGhosts[n].coordinateAbs[0] = i * 4
                            self.movingObjectGhosts[n].coordinateAbs[1] = levelLineNo * 4
                            break   # interrumpir el bucle actual (con el generador 'n')


            levelLineNo += 1 # indicar qué línea somos

        levelFile.close()


    def encounterFixed(self, x, y):     # rel coord.
        if self.levelObjects[x][y].name == "empty":
            result = "empty"

        elif self.levelObjects[x][y].name == "pellet":
            result = "pellet"

        elif self.levelObjects[x][y].name == "powerup":
            result = "powerup"
        
        return result

    
    def encounterMoving(self, x, y):    # abs coord.

        result = "alive"    # default return

        for i in range(4):  # Comprobar si Pac-Man se encontró con un fantasma
            m = self.movingObjectGhosts[i].coordinateAbs[0] # fantasma x coord.
            n = self.movingObjectGhosts[i].coordinateAbs[1] # fantasma y coord.

            if self.movingObjectGhosts[i].isActive == True and self.movingObjectGhosts[i].isCaged == False:
                if (m-3 < x < m+3) and (n-3 < y < n+3):   # Comprobar las coordenadas x e y en paralelo; esto es un poco benigno para determinar (podemos usar +/-4).
                    result = "dead"
                else:
                    pass
            else:
                pass
        
        return result



    def loopFunction(self):
        self.movingObjectPacman.MoveNext(self)
        self.movingObjectPacman.MoveCurrent(self)

        for i in range(4):
            if self.movingObjectGhosts[i].isActive == True:
                self.movingObjectGhosts[i].dirNext = self.movingObjectGhosts[i].MoveNextGhost(self, self.movingObjectGhosts[i].dirCurrent)
                self.movingObjectGhosts[i].MoveNext(self)
                self.movingObjectGhosts[i].MoveCurrent(self)
            
            else:
                pass






class levelObject(object):

    def __init__(self, name):
        self.reset(name)

    def reset(self, name):
        self.name = name
        self.isDestroyed = False



class movingObject(object):

    def __init__(self, name):
        self.reset(name)


    def reset(self, name):
        self.name = name
        self.isActive = False       # Comprobar si este objeto es un fantasma activo (no se usa para Pac-Man)
        self.isCaged = True         # Comprobar si este objeto está enjaulado (solo para fantasmas)
        self.dirCurrent = "Left"    # dirección actual, si no puede moverse con dirNext, el objeto procederá en esta dirección
        self.dirNext = "Left"       # el objeto se moverá en esta dirección si puede
        self.dirOpposite = "Right"  # dirección opuesta a la dirección actual, utilizada para determinar el movimiento del fantasma
        self.dirEdgePassed = False  # Comprobar si el objeto ha pasado uno de los bordes del campo
        self.coordinateRel = [0, 0] # Coordenada Relativa, comprobar si el objeto puede moverse en la dirección dada
        self.coordinateAbs = [0, 0] # Coordenada Absoluta, utilizada para encuentros de widgets (imagen) y objetos


    def MoveNextGhost(self, GameEngine, dirCur):
        ## Esta función determinará la dirección del fantasma
        # Si el fantasma alcanza una coordenada de la cuadrícula, se comprobarán todas las direcciones desde la ubicación actual del fantasma.
        # Deberíamos obtener DOF aquí y determinaremos cómo gestionamos la dirección de Ghost
        # DOF == 1 ... dirección opuesta
        # DOF == 2 ... dirección actual
        # DOF == 3 ... dirección aleatoria (excepto dirección opuesta)
        # DOF == 4 ... dirección aleatoria (excepto dirección opuesta)

        if self.isCaged == True:    # Si el fantasma está enjaulado, impedir el movimiento
            pass

        elif self.coordinateAbs[0] % 4 != 0: # si el objeto se está moviendo, evitar cambiar su dirección
            pass

        elif self.coordinateAbs[1] % 4 != 0: # si el objeto se está moviendo, evitar cambiar su dirección
            pass
        
        else:
            dirIndex = ['Left', 'Right', 'Up', 'Down'] # [0]: Left, [1]: Right, [2]: Up, [3]: Down
            dirAvailable = []
            dirDOF = 0

            # encontrar la dirección opuesta
            if dirCur == 'Left':
                self.dirOpposite = 'Right'
            elif dirCur == 'Right':
                self.dirOpposite = 'Left'
            elif dirCur == 'Up':
                self.dirOpposite = 'Down'
            elif dirCur == 'Down':
                self.dirOpposite = 'Up'
            else: # dirCur == 'Stop'
                pass

            # comprobando todas las direcciones
            try:
                for i in range(4):

                    if i == 0:
                        nextObject = GameEngine.levelObjects[self.coordinateRel[0]-1][self.coordinateRel[1]] # Objeto de nivel a la izquierda
                    elif i == 1:
                        nextObject = GameEngine.levelObjects[self.coordinateRel[0]+1][self.coordinateRel[1]] # Objeto de nivel a la derecha
                    elif i == 2:
                        nextObject = GameEngine.levelObjects[self.coordinateRel[0]][self.coordinateRel[1]-1] # Objeto de nivel arriba
                    elif i == 3:
                        nextObject = GameEngine.levelObjects[self.coordinateRel[0]][self.coordinateRel[1]+1] # Objeto de nivel abajo

                    if nextObject.name in GameEngine.levelObjectNamesPassable:
                        dirDOF += 1
                        dirAvailable.append(dirIndex[i])    # Agregar dirección disponible a la lista
                    elif nextObject.name in GameEngine.levelObjectNamesBlocker:
                        pass

            except IndexError:  # en caso de teletransportación al borde
                dirDOF = 2
                dirAvailable.append(dirCur)
            

            try:
                if dirDOF == 1: # en dirección opuesta, en este caso, dirAvailable solo tiene un elemento (que es el opuesto a dir)
                    return dirAvailable[0]  # Es posible que esto no utilice dirOpp, ya que si el objeto se detiene, dirOpp no ​​se enlaza correctamente.

                elif dirDOF == 2: # avanzar hacia la dirección actual
                    if dirCur in dirAvailable:  # recto
                        return dirCur
                    elif dirCur == 'Stop':  # De alguna manera este objeto se detuvo en línea recta
                        return dirAvailable[0]
                    else:   # curva
                        dirAvailable.remove(self.dirOpposite)
                        return dirAvailable[0]


                elif dirDOF == 3 or dirDOF == 4:
                    if dirCur == 'Stop':
                        randNo = randint(0, dirDOF-1)   # Generar un número aleatorio, selección de grados de libertad
                        return dirAvailable[randNo]
                    else:
                        dirAvailable.remove(self.dirOpposite) # except the opposite direction
                        randNo = randint(0, dirDOF-2)   # generar un número aleatorio, selección de grado de libertad (excepto la dirección opuesta)
                        return dirAvailable[randNo]
            

            except ValueError:   #Evitar el error del primer bucle (los valores predeterminados provocarían un ValueError)

                pass



    def MoveNext(self, GameEngine):
       # Esta función determinará si Pac-Man puede moverse en la dirección indicada o no.

        if self.dirNext == self.dirCurrent: # en este caso, no se requiere ninguna acción
            pass

        elif self.coordinateAbs[0] % 4 != 0: # si el objeto se está moviendo, evitar cambiar su dirección
            pass

        elif self.coordinateAbs[1] % 4 != 0: # si el objeto se está moviendo, evitar cambiar su dirección
            pass

        else:
            if self.dirNext == "Left":  # Comprueba primero la dirección

                if self.coordinateRel[0] == 0: # En el borde izquierdo, permite cambiar de dirección sin comprobar (evita errores de índice)
                    self.dirCurrent = "Left"

                else:
                    nextObject = GameEngine.levelObjects[self.coordinateRel[0]-1][self.coordinateRel[1]] # Objeto de nivel a la izquierda

                    # Comprobar el objeto de nivel y permitir que el objeto en movimiento cambie su dirección actual
                    if nextObject.name in GameEngine.levelObjectNamesPassable:
                        self.dirCurrent = "Left"
                    elif nextObject.name in GameEngine.levelObjectNamesBlocker:
                        pass
                

            elif self.dirNext == "Right":

                if self.coordinateRel[0] == 27: # En el borde derecho, permite cambiar de dirección sin comprobar (evita errores de índice)
                    self.dirCurrent = "Right"

                else:
                    nextObject = GameEngine.levelObjects[self.coordinateRel[0]+1][self.coordinateRel[1]] # Objeto de nivel a la derecha

                    # Comprobar el objeto de nivel y permitir que el objeto en movimiento cambie su dirección actual
                    if nextObject.name in GameEngine.levelObjectNamesPassable:
                        self.dirCurrent = "Right"
                    elif nextObject.name in GameEngine.levelObjectNamesBlocker:
                        pass


            elif self.dirNext == "Down":

                if self.coordinateRel[1] == 31: # En el borde inferior, permite cambiar de dirección sin comprobar (evita errores de índice)
                    self.dirCurrent = "Down"

                else:
                    nextObject = GameEngine.levelObjects[self.coordinateRel[0]][self.coordinateRel[1]+1] # Objeto de nivel abajo de este objeto

                    # Comprobar el objeto de nivel y permitir que el objeto en movimiento cambie su dirección actual
                    if nextObject.name in GameEngine.levelObjectNamesPassable:
                        self.dirCurrent = "Down"
                    elif nextObject.name in GameEngine.levelObjectNamesBlocker:
                        pass


            elif self.dirNext == "Up":

                if self.coordinateRel[1] == 0: # En el borde superior, permite cambiar de dirección sin comprobar (evita errores de índice)
                    self.dirCurrent = "Up"

                else:
                    nextObject = GameEngine.levelObjects[self.coordinateRel[0]][self.coordinateRel[1]-1] # Objeto de nivel arriba de este objeto

                    # Comprobar el objeto de nivel y permitir que el objeto en movimiento cambie su dirección actual
                    if nextObject.name in GameEngine.levelObjectNamesPassable:
                        self.dirCurrent = "Up"
                    elif nextObject.name in GameEngine.levelObjectNamesBlocker:
                        pass

        
    
    def MoveCurrent(self, GameEngine):

        if self.dirCurrent == "Left":

            if self.coordinateAbs[0] == 0: # En el borde izquierdo, mueve al borde derecho
                self.coordinateAbs[0] = 27*4 + 3
                self.coordinateRel[0] = 28
                self.dirEdgePassed = True
            
            else:
                nextObject = GameEngine.levelObjects[self.coordinateRel[0]-1][self.coordinateRel[1]] # Objeto de nivel a la izquierda de este objeto
                # Comprobar el objeto de nivel y permitir que el objeto en movimiento cambie su dirección actual
                if nextObject.name in GameEngine.levelObjectNamesPassable:
                    self.coordinateAbs[0] -= 1 # ajustar la coordenada actual
                    if self.coordinateAbs[0] % 4 == 0: # comprobar si el objeto alcanza una coordenada de cuadrícula (coordinateRel)
                        self.coordinateRel[0] -= 1

                elif nextObject.name in GameEngine.levelObjectNamesBlocker:
                    self.dirCurrent = "Stop"


        elif self.dirCurrent == "Right":

            if self.coordinateAbs[0] == 27*4:  # En el borde derecho, mueve al borde izquierdo
                self.coordinateAbs[0] = -3
                self.coordinateRel[0] = -1
                self.dirEdgePassed = True

            else:
                nextObject = GameEngine.levelObjects[self.coordinateRel[0]+1][self.coordinateRel[1]] # Objeto de nivel a la derecha de este objeto
                # Comprobar el objeto de nivel y permitir que el objeto en movimiento cambie su dirección actual
                if nextObject.name in GameEngine.levelObjectNamesPassable:
                    self.coordinateAbs[0] += 1  # ajustar la coordenada actual
                    if self.coordinateAbs[0] % 4 == 0: # comprobar si el objeto alcanza una coordenada de cuadrícula (coordinateRel)
                        self.coordinateRel[0] += 1

                elif nextObject.name in GameEngine.levelObjectNamesBlocker:
                    self.dirCurrent = "Stop"


        elif self.dirCurrent == "Down":

            if self.coordinateAbs[1] == 31*4:  # En el borde inferior, mueve al borde superior
                self.coordinateAbs[1] = -3
                self.coordinateRel[1] = -1
                self.dirEdgePassed = True

            else:
                nextObject = GameEngine.levelObjects[self.coordinateRel[0]][self.coordinateRel[1]+1] # Objeto de nivel colocado debajo de este objeto
                # Comprobar el objeto de nivel y permitir que el objeto en movimiento cambie su dirección actual
                if nextObject.name in GameEngine.levelObjectNamesPassable:
                    self.coordinateAbs[1] += 1  # ajustar la coordenada actual
                    if self.coordinateAbs[1] % 4 == 0: # comprobar si el objeto alcanza una coordenada de cuadrícula (coordinateRel)
                        self.coordinateRel[1] += 1

                elif nextObject.name in GameEngine.levelObjectNamesBlocker:
                    self.dirCurrent = "Stop"


        elif self.dirCurrent == "Up":

            if self.coordinateAbs[1] == 0:  # En el borde superior, mueve al borde inferior
                self.coordinateAbs[1] = 31*4 + 3
                self.coordinateRel[1] = 32
                self.dirEdgePassed = True

            else:
                nextObject = GameEngine.levelObjects[self.coordinateRel[0]][self.coordinateRel[1]-1] # Objeto de nivel colocado arriba de este objeto
                # Comprobar el objeto de nivel y permitir que el objeto en movimiento cambie su dirección actual
                if nextObject.name in GameEngine.levelObjectNamesPassable:
                    self.coordinateAbs[1] -= 1  # adjust current coordinate
                    if self.coordinateAbs[1] % 4 == 0: # check the object reaches a grid coordinate (coordinateRel)
                        self.coordinateRel[1] -= 1

                elif nextObject.name in GameEngine.levelObjectNamesBlocker:
                    self.dirCurrent = "Stop"


        elif self.dirCurrent == "Stop":
            pass


gameEngine = GameEngine()