from tkinter import Tk, Label, Entry, Button, PhotoImage, messagebox, END, Canvas
from threading import Timer
from data import field
import os, pygame
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    # Pillow no disponible: cargaremos imágenes sin redimensionar
    PIL_AVAILABLE = False


class MainEngine(object):

    def __init__(self):

        # Inicializar parámetros de ventana de tkinter
        self.root = Tk()
        self.root.title("Pac-Man")
        self.root.geometry("480x640")
        self.root.resizable(0, 0)

        # Inicializar algunas variables del motor
        self.currentLv = 1              # default: nivel 1
        self.isLevelGenerated = False   # Comprobar si el nivel (mapa) se ha generado o no
        self.isPlaying = False          # Comprobar si el juego ha comenzado (en movimiento) o no
        self.statusStartingTimer = 0    # temporizador de cuenta atrás para la función 'prepararse'
        self.statusDeadTimer = 0        # temporizador de cuenta atrás para el evento de muerte
        self.statusFinishTimer = 0      # temporizador de cuenta atrás para el evento de finalización
        self.statusScore = 0            # puntuación
        self.statusLife = 2             # vida
        self.infolebel= ""
        # Llamar a la siguiente fase de inicialización: carga de recursos
        self.__initResource()


    def __initResource(self):
        ## leer los archivos de sprites
        # Todos los sprites se guardarán en este diccionario
        self.wSprites = {
            'getready': PhotoImage(file="resource/sprite_get_ready.png"),
            'gameover': PhotoImage(file="resource/sprite_game_over.png"),
            'wall': PhotoImage(file="resource/sprite_wall.png"),
            'cage': PhotoImage(file="resource/sprite_cage.png"),
            'pellet': PhotoImage(file="resource/sprite_pellet.png")
        }

        # enlazar sprites para objetos en movimiento
        for i in range(4):
            # pacman: pacman(dirección)(índice)
            if i == 3:
                pass
            else:
                self.wSprites['pacmanL{}'.format(i+1)] = PhotoImage(file="resource/sprite_pacman_left{}.png".format(i+1))
                self.wSprites['pacmanR{}'.format(i+1)] = PhotoImage(file="resource/sprite_pacman_right{}.png".format(i+1))
                self.wSprites['pacmanU{}'.format(i+1)] = PhotoImage(file="resource/sprite_pacman_up{}.png".format(i+1))
                self.wSprites['pacmanD{}'.format(i+1)] = PhotoImage(file="resource/sprite_pacman_down{}.png".format(i+1))
            # ghosts: ghost(index1)(direction)(index2)
            self.wSprites['ghost{}L1'.format(i+1)] = PhotoImage(file="resource/sprite_ghost_{}_left1.png".format(i+1))
            self.wSprites['ghost{}L2'.format(i+1)] = PhotoImage(file="resource/sprite_ghost_{}_left2.png".format(i+1))
            self.wSprites['ghost{}R1'.format(i+1)] = PhotoImage(file="resource/sprite_ghost_{}_right1.png".format(i+1))
            self.wSprites['ghost{}R2'.format(i+1)] = PhotoImage(file="resource/sprite_ghost_{}_right2.png".format(i+1))
            self.wSprites['ghost{}U1'.format(i+1)] = PhotoImage(file="resource/sprite_ghost_{}_up1.png".format(i+1))
            self.wSprites['ghost{}U2'.format(i+1)] = PhotoImage(file="resource/sprite_ghost_{}_up2.png".format(i+1))
            self.wSprites['ghost{}D1'.format(i+1)] = PhotoImage(file="resource/sprite_ghost_{}_down1.png".format(i+1))
            self.wSprites['ghost{}D2'.format(i+1)] = PhotoImage(file="resource/sprite_ghost_{}_down2.png".format(i+1))

        for i in range(11):
            self.wSprites['pacmanDeath{}'.format(i+1)] = PhotoImage(file="resource/sprite_pacman_death{}.png".format(i+1))
            # Redimensionar los sprites de muerte para que coincidan con el tamaño del pacman
            try:
                target_w = self.wSprites['pacmanL1'].width()
                target_h = self.wSprites['pacmanL1'].height()
                img = Image.open("resource/sprite_pacman_death{}.png".format(i+1)).convert("RGBA")
                img = img.resize((target_w, target_h), Image.LANCZOS)
                self.wSprites['pacmanDeath{}'.format(i+1)] = ImageTk.PhotoImage(img)
            except Exception:
                # Si falla, cargar la imagen sin redimensionar como fallback
                self.wSprites['pacmanDeath{}'.format(i+1)] = PhotoImage(file="resource/sprite_pacman_death{}.png".format(i+1))
        
        # DEBUG: mostrar tamaños de las imágenes de Pac‑Man en la consola
        try:
            print("Pacman L1 size:", self.wSprites['pacmanL1'].width(), "x", self.wSprites['pacmanL1'].height())
            print("Pacman R1 size:", self.wSprites['pacmanR1'].width(), "x", self.wSprites['pacmanR1'].height())
            print("Pacman U1 size:", self.wSprites['pacmanU1'].width(), "x", self.wSprites['pacmanU1'].height())
            print("Pacman D1 size:", self.wSprites['pacmanD1'].width(), "x", self.wSprites['pacmanD1'].height())
            # tamaño de las imágenes de muerte (ejemplo con la primera)
            print("PacmanDeath1 size:", self.wSprites['pacmanDeath1'].width(), "x", self.wSprites['pacmanDeath1'].height())
        except Exception as e:
            print("No se pudo leer tamaño de sprites:", e)
 
       # Llamar a la siguiente fase de inicialización: generar widgets
        self.__initWidgets()


    def __initWidgets(self):
       # Inicializar widgets para la selección de nivel
        self.wLvLabel = Label(self.root, text="¡Selecciona un nivel! (1-5).")
        self.wLvEntry = Entry(self.root)
        self.wLvBtn = Button(self.root, text="CLICK", command=self.lvSelect, width=5, height=1)
        self.instLabel = Label(self.root, text="Puedes moverte SOLO con las flechas de tu teclado")

        # Inicializar widgets para el juego
        self.wGameLabelScore = Label(self.root, text=("Puntuación: " + str(self.statusScore)))
        self.wGameLabelLife = Label(self.root, text=("Vida: " + str(self.statusLife)))
        self.wGameCanv = Canvas(width=480, height=600)
        self.wGameCanvLabelGetReady = self.wGameCanv.create_image(240,326,image=None)
        self.wGameCanvLabelGameOver = self.wGameCanv.create_image(240,327,image=None)  
        self.wGameCanvObjects = [[self.wGameCanv.create_image(0,0,image=None) for j in range(32)] for i in range(28)]
        self.wGameCanv.config(background="black")
        self.wGameCanvMovingObjects = [self.wGameCanv.create_image(0,0,image=None) for n in range(5)] # 0: pacman, 1-4: ghosts

        # Atajos de teclado para el control del juego
        self.root.bind('<Left>', self.inputResponseLeft)
        self.root.bind('<Right>', self.inputResponseRight)
        self.root.bind('<Up>', self.inputResponseUp)
        self.root.bind('<Down>', self.inputResponseDown)
        self.root.bind('<Escape>', self.inputResponseEsc)
        self.root.bind('<Return>', self.inputResponseReturn)

        # Llamar a la siguiente fase de inicialización: selección de nivel
        self.__initLevelSelect()


    def __initLevelSelect(self):
        ## selección de nivel, mostrando todos los widgets relevantes
        self.wLvLabel.pack()
        self.wLvEntry.pack()
        self.wLvBtn.pack()
        self.instLabel.pack()
 
        # ejecutar el juego
        self.root.mainloop()


    def lvSelect(self):
        try:
            self.__initLevelOnce(self.wLvEntry.get())

        except ValueError:
            self.wLvEntry.delete(0, END)  # Borrar el cuadro de texto
            messagebox.showinfo("Error!", "Enter a valid level.")

        except FileNotFoundError:
            self.wLvEntry.delete(0, END)  # Borrar el cuadro de texto
            messagebox.showinfo("Error!", "Enter a valid level.")


    def __initLevelOnce(self, level):
        ## Esta función se llamará solo una vez

        self.__initLevel(level)

        # eliminar características de selección de nivel
        self.wLvLabel.destroy()
        self.wLvEntry.destroy()
        self.wLvBtn.destroy()
        # colocar el lienzo y establecer isPlaying en True
        self.wGameCanv.place(x=0, y=30)
        self.wGameLabelScore.place(x=10, y=5)
        self.wGameLabelLife.place(x=420, y=5)
        self.wGameLabelScore.place(x=10, y=5)



    def __initLevel(self, level):

        self.currentLv = int(level)
        field.gameEngine.levelGenerate(level)   # Generar nivel seleccionado/aprobado

        # Comprobar el nombre del objeto y enlazar el sprite, ajustar sus coordenadas
        for j in range(32):
            for i in range(28):

                if field.gameEngine.levelObjects[i][j].name == "empty":
                    pass
                elif field.gameEngine.levelObjects[i][j].name == "wall":
                    self.wGameCanv.itemconfig(self.wGameCanvObjects[i][j], image=self.wSprites['wall'], state='normal')
                    self.wGameCanv.coords(self.wGameCanvObjects[i][j], 3+i*17+8, 30+j*17+8)
                elif field.gameEngine.levelObjects[i][j].name == "cage":
                    self.wGameCanv.itemconfig(self.wGameCanvObjects[i][j], image=self.wSprites['cage'], state='normal')
                    self.wGameCanv.coords(self.wGameCanvObjects[i][j], 3+i*17+8, 30+j*17+8)
                elif field.gameEngine.levelObjects[i][j].name == "pellet":
                    if field.gameEngine.levelObjects[i][j].isDestroyed == False:
                        self.wGameCanv.itemconfig(self.wGameCanvObjects[i][j], image=self.wSprites['pellet'], state='normal')
                        self.wGameCanv.coords(self.wGameCanvObjects[i][j], 3+i*17+8, 30+j*17+8)
                    else:
                        pass

        # enlazar el sprite y darle su coordenada actual para pacman
        self.wGameCanv.coords(self.wGameCanvMovingObjects[0], 
                            3+field.gameEngine.movingObjectPacman.coordinateRel[0]*17+8,
                            30+field.gameEngine.movingObjectPacman.coordinateRel[1]*17+8)
        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanL1'], state='normal')

        # Asigna las coordenadas actuales al sprite para los fantasmas
        for i in range(4):
            if field.gameEngine.movingObjectGhosts[i].isActive == True:
                self.wGameCanv.coords(self.wGameCanvMovingObjects[i+1],
                                    3+field.gameEngine.movingObjectGhosts[i].coordinateRel[0]*17+8,
                                    30+field.gameEngine.movingObjectGhosts[i].coordinateRel[1]*17+8)
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[i+1], image=self.wSprites['ghost{}L1'.format(i+1)], state='normal')


        # ¡Avanza a la siguiente fase: prepárate!
        pygame.mixer.music.stop()
        pygame.mixer.music.load("resource/sound_intro.mp3")
        pygame.mixer.music.play(loops=0, start=0.0)
        self.isLevelGenerated = True
        self.timerReady = PerpetualTimer(0.55, self.__initLevelStarting)
        self.timerReady.start()


    def inputResponseLeft(self, event):
        field.gameEngine.movingObjectPacman.dirNext = "Left"

    def inputResponseRight(self, event):
        field.gameEngine.movingObjectPacman.dirNext = "Right"

    def inputResponseUp(self, event):
        field.gameEngine.movingObjectPacman.dirNext = "Up"

    def inputResponseDown(self, event):
        field.gameEngine.movingObjectPacman.dirNext = "Down"

    def inputResponseEsc(self, event):
        self.timerLoop.stop()
        messagebox.showinfo("Game Over!", "You hit the escape key!")

    def inputResponseReturn(self, event):
        # skip feature
        if self.isLevelGenerated == True and self.isPlaying == False:
            self.gameStartingTrigger()
        else:
            pass



    def __initLevelStarting(self):
        self.statusStartingTimer += 1   # Temporizador de cuenta regresiva para esta función

       # Enlazar el sprite para el widget
        self.wGameCanv.itemconfig(self.wGameCanvLabelGetReady, image=self.wSprites['getready'])

        if self.statusStartingTimer < 8:
            # función de parpadeo
            if self.statusStartingTimer % 2 == 1:
                self.wGameCanv.itemconfigure(self.wGameCanvLabelGetReady, state='normal')
            else:
                self.wGameCanv.itemconfigure(self.wGameCanvLabelGetReady, state='hidden')

        else:   # Después de 8 iteraciones, el juego principal comenzará con la función loopFunction
            self.gameStartingTrigger()


    def gameStartingTrigger(self):
        ## Detente para imprimir "prepárate" y comienza el juego
        self.timerReady.stop()
        self.wGameCanv.itemconfigure(self.wGameCanvLabelGetReady, state='hidden')
        self.statusStartingTimer = 0
        self.isPlaying = True
        field.gameEngine.movingObjectPacman.dirNext = "Left"

        # sonido de fantasma como música
        pygame.mixer.music.stop()
        pygame.mixer.music.load("resource/sound_ghost.ogg")
        pygame.mixer.music.play(-1)

        self.timerLoop = PerpetualTimer(0.045, self.loopFunction)
        self.timerLoop.start()


    def loopFunction(self):

        field.gameEngine.loopFunction()

        coordGhosts = {}

        for i in range(4):
            coordGhosts['RelG{}'.format(i+1)] = field.gameEngine.movingObjectGhosts[i].coordinateRel    # coordenada relativa de fantasmas
            coordGhosts['AbsG{}'.format(i+1)] = field.gameEngine.movingObjectGhosts[i].coordinateAbs    # coordenada absoluta de fantasmas

        self.spritePacman(field.gameEngine.movingObjectPacman.coordinateRel, field.gameEngine.movingObjectPacman.coordinateAbs)
        self.spriteGhost(coordGhosts)
        self.encounterEvent(field.gameEngine.movingObjectPacman.coordinateRel, field.gameEngine.movingObjectPacman.coordinateAbs)




    def spritePacman(self, coordRelP, coordAbsP):
        ## Función de sprites de Pac-Man
        # Esto ajustará las coordenadas del sprite y lo animará, basándose en sus coordenadas absolutas.
        if field.gameEngine.movingObjectPacman.dirCurrent == "Left":

            # Comprobar los bordes del campo del objeto pasado
            if field.gameEngine.movingObjectPacman.dirEdgePassed == True:
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 17*27+17, 0)    # Ten en cuenta que esto moverá el sprite 17*27+17 (no 17*27+12), ya que el sprite se moverá una vez más abajo.
                field.gameEngine.movingObjectPacman.dirEdgePassed = False
            else:
                pass

            if coordAbsP[0] % 4 == 0:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanL2'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], -4, 0)
            elif coordAbsP[0] % 4 == 1:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanL3'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], -4, 0)
            elif coordAbsP[0] % 4 == 2:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanL2'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], -4, 0)
            elif coordAbsP[0] % 4 == 3:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanL1'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], -5, 0)


        elif field.gameEngine.movingObjectPacman.dirCurrent == "Right":

            # Comprobar los bordes del campo del objeto pasado
            if field.gameEngine.movingObjectPacman.dirEdgePassed == True:
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], -(17*27+17), 0)
                field.gameEngine.movingObjectPacman.dirEdgePassed = False
            else:
                pass

            if coordAbsP[0] % 4 == 0:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanR2'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 4, 0)
            elif coordAbsP[0] % 4 == 1:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanR3'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 4, 0)
            elif coordAbsP[0] % 4 == 2:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanR2'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 4, 0)
            elif coordAbsP[0] % 4 == 3:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanR1'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 5, 0)


        elif field.gameEngine.movingObjectPacman.dirCurrent == "Up":

            # Comprobar los bordes del campo del objeto pasado
            if field.gameEngine.movingObjectPacman.dirEdgePassed == True:
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 0, 17*31+17)
                field.gameEngine.movingObjectPacman.dirEdgePassed = False
            else:
                pass

            if coordAbsP[1] % 4 == 0:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanU2'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 0, -4)
            elif coordAbsP[1] % 4 == 1:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanU3'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 0, -4)
            elif coordAbsP[1] % 4 == 2:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanU2'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 0, -4)
            elif coordAbsP[1] % 4 == 3:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanU1'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 0, -5)


        elif field.gameEngine.movingObjectPacman.dirCurrent == "Down":

            # Comprobar los bordes del campo del objeto pasado
            if field.gameEngine.movingObjectPacman.dirEdgePassed == True:
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 0, -(17*31+17))
                field.gameEngine.movingObjectPacman.dirEdgePassed = False
            else:
                pass

            if coordAbsP[1] % 4 == 0:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanD2'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 0, 4)
            elif coordAbsP[1] % 4 == 1:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanD3'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 0, 4)
            elif coordAbsP[1] % 4 == 2:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanD2'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 0, 4)
            elif coordAbsP[1] % 4 == 3:
                self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0], image=self.wSprites['pacmanD1'])
                self.wGameCanv.move(self.wGameCanvMovingObjects[0], 0, 5)


    def spriteGhost(self, coordGhosts):
        ## Función de sprites de fantasmas
        # Esto ajustará las coordenadas del sprite y lo animará, basándose en sus coordenadas absolutas.
        for ghostNo in range(4):
            if field.gameEngine.movingObjectGhosts[ghostNo].isActive == True:   # Solo se mostrará el fantasma activo
                if field.gameEngine.movingObjectGhosts[ghostNo].dirCurrent == "Left":

                    # Comprobar los bordes del campo del objeto pasado
                    if field.gameEngine.movingObjectGhosts[ghostNo].dirEdgePassed == True:
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 17*27+17, 0)
                        field.gameEngine.movingObjectGhosts[ghostNo].dirEdgePassed = False
                    else:
                        pass

                    if coordGhosts['AbsG{}'.format(ghostNo+1)][0] % 4 == 0:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}L1'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], -4, 0)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][0] % 4 == 1:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}L1'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], -4, 0)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][0] % 4 == 2:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}L2'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], -4, 0)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][0] % 4 == 3:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}L2'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], -5, 0)


                elif field.gameEngine.movingObjectGhosts[ghostNo].dirCurrent == "Right":

                    # Comprobar los bordes del campo del objeto pasado
                    if field.gameEngine.movingObjectGhosts[ghostNo].dirEdgePassed == True:
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], -(17*27+17), 0)
                        field.gameEngine.movingObjectGhosts[ghostNo].dirEdgePassed = False
                    else:
                        pass

                    if coordGhosts['AbsG{}'.format(ghostNo+1)][0] % 4 == 0:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}R1'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 4, 0)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][0] % 4 == 1:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}R1'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 4, 0)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][0] % 4 == 2:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}R2'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 4, 0)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][0] % 4 == 3:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}R2'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 5, 0)

                elif field.gameEngine.movingObjectGhosts[ghostNo].dirCurrent == "Up":

                    # Comprobar los bordes del campo del objeto pasado
                    if field.gameEngine.movingObjectGhosts[ghostNo].dirEdgePassed == True:
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 0, 17*31+17)
                        field.gameEngine.movingObjectGhosts[ghostNo].dirEdgePassed = False
                    else:
                        pass

                    if coordGhosts['AbsG{}'.format(ghostNo+1)][1] % 4 == 0:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}U1'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 0, -4)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][1] % 4 == 1:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}U1'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 0, -4)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][1] % 4 == 2:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}U2'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 0, -4)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][1] % 4 == 3:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}U2'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 0, -5)


                elif field.gameEngine.movingObjectGhosts[ghostNo].dirCurrent == "Down":

                    # Comprobar los bordes del campo del objeto pasado
                    if field.gameEngine.movingObjectGhosts[ghostNo].dirEdgePassed == True:
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 0, -(17*31+17))
                        field.gameEngine.movingObjectGhosts[ghostNo].dirEdgePassed = False
                    else:
                        pass

                    if coordGhosts['AbsG{}'.format(ghostNo+1)][1] % 4 == 0:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}D1'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 0, 4)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][1] % 4 == 1:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}D1'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 0, 4)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][1] % 4 == 2:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}D2'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 0, 4)
                    elif coordGhosts['AbsG{}'.format(ghostNo+1)][1] % 4 == 3:
                        self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[ghostNo+1], image=self.wSprites['ghost{}D2'.format(ghostNo+1)])
                        self.wGameCanv.move(self.wGameCanvMovingObjects[ghostNo+1], 0, 5)
            
            else:   # fantasma inactivo
                pass


    def encounterEvent(self, coordRelP, coordAbsP):
        ## funciones de encuentro

        encounterMov = field.gameEngine.encounterMoving(coordAbsP[0], coordAbsP[1]) # Llamar a encounterEvent para objetos en movimiento

        if encounterMov == 'dead':
            self.encounterEventDead()

        else:
            pass

        # check the object reaches grid coordinate
        if coordAbsP[0] % 4 == 0 and coordAbsP[1] % 4 == 0:
            encounterFix = field.gameEngine.encounterFixed(coordRelP[0], coordRelP[1]) # Llamar a la función encounterEvent
            if encounterFix == "empty":
                pass
            elif encounterFix == "pellet":
                if field.gameEngine.levelObjects[coordRelP[0]][coordRelP[1]].isDestroyed == False:  # Comprobar que el perdigón esté vivo
                    field.gameEngine.levelObjects[coordRelP[0]][coordRelP[1]].isDestroyed = True # destruir el perdigón
                    self.wGameCanv.itemconfigure(self.wGameCanvObjects[coordRelP[0]][coordRelP[1]], state='hidden') # eliminar del lienzo

                    # reproducir el sonido (wa, ka, wa, ka, ...)
                    if self.statusScore % 20 == 0:
                        self.wSounds['chomp1'].play(loops=0)
                    else:
                        self.wSounds['chomp2'].play(loops=0)

                    self.statusScore += 10 # ajustar la puntuación
                    self.wGameLabelScore.configure(text=("Score: " + str(self.statusScore))) # mostrar en el tablero
                    field.gameEngine.levelPelletRemaining -= 1 # ajustar el número de perdigones restantes

                    if field.gameEngine.levelPelletRemaining == 0:
                        self.encounterEventLevelClear() # nivel claro
                    else:
                        pass


                else:   # El punto ya ha sido tomado
                    pass

        else: # pacman no está en la coordenada de la cuadrícula
            pass


    def encounterEventLevelClear(self):
        # pause the game
        pygame.mixer.music.stop()
        self.timerLoop.stop()
        self.isPlaying = False

        for i in range(5):  # Ocultar el sprite de los objetos en movimiento
            self.wGameCanv.itemconfigure(self.wGameCanvMovingObjects[i], state='hidden')

        self.timerClear = PerpetualTimer(0.4, self.encounterEventLevelClearLoop)
        self.timerClear.start()


    def encounterEventLevelClearLoop(self):
        self.statusFinishTimer += 1  # Temporizador de cuenta regresiva para esta función

        if self.statusFinishTimer < 9:
            # Función de parpadeo de pared
            if self.statusFinishTimer % 2 == 1:
                self.wSprites.update({'wall': PhotoImage(file="resource/sprite_wall2.png")})                
                for j in range(32):
                    for i in range(28):
                        if field.gameEngine.levelObjects[i][j].name == "wall":
                            self.wGameCanv.itemconfig(self.wGameCanvObjects[i][j], image=self.wSprites['wall'])
                        else:
                            pass
            else:
                self.wSprites.update({'wall': PhotoImage(file="resource/sprite_wall.png")})
                for j in range(32):
                    for i in range(28):
                        if field.gameEngine.levelObjects[i][j].name == "wall":
                            self.wGameCanv.itemconfig(self.wGameCanvObjects[i][j], image=self.wSprites['wall'])
                        else:
                            pass

        else:   # Después de 11 iteraciones, continuará el proceso de eliminación de nivel
            self.encounterEventLevelClearFinish()


    def encounterEventLevelClearFinish(self):
        self.timerClear.stop()
        self.statusFinishTimer = 0

        # reset all values and hide the sprite (or level generate process will be shown)
        for j in range(32):
            for i in range(28):
                field.gameEngine.levelObjects[i][j].reset('')
                #self.wGameCanv.itemconfigure(self.wGameCanvObjects[i][j], state='hidden')

        field.gameEngine.movingObjectPacman.reset('Pacman')

        for n in range(4):
            field.gameEngine.movingObjectGhosts[n].reset('Ghost')
        
        self.currentLv += 1
        self.isLevelGenerated = False
        self.__initLevel(self.currentLv)



    def encounterEventDead(self):

        self.statusLife -= 1   # restar la vida restante

        if self.statusLife >= 0:
            self.wGameLabelLife.configure(text=("Life: " + str(self.statusLife))) # mostrar en el tablero
        else:   # Evitar mostrar vidas negativas (de todos modos, se acabará la partida)
            pass

        # pausa el juego
        self.isPlaying = False
        pygame.mixer.music.stop()
        self.timerLoop.stop()

        # Llama al bucle de la muerte
        self.timerDeath = PerpetualTimer(0.10, self.encounterEventDeadLoop)
        self.timerDeath.start()


    def encounterEventDeadLoop(self):

        self.statusDeadTimer += 1   # temporizador de cuenta regresiva para esta función

        if self.statusDeadTimer <= 5:   # esperando un momento
            pass

        elif self.statusDeadTimer == 6:
            # efecto de sonido
            pygame.mixer.music.load("resource/sound_death.mp3")
            pygame.mixer.music.play(loops=0, start=0.0)
            for i in range(4):  # Ocultar el sprite fantasma e inicializar su estado
                self.wGameCanv.itemconfigure(self.wGameCanvMovingObjects[i+1], state='hidden')
                field.gameEngine.movingObjectGhosts[i].isActive = False
                field.gameEngine.movingObjectGhosts[i].isCaged = True

        elif 6 < self.statusDeadTimer <= 17:    # animar el sprite de muerte
            self.wGameCanv.itemconfig(self.wGameCanvMovingObjects[0],
                                        image=self.wSprites['pacmanDeath{}'.format(self.statusDeadTimer-6)])

        elif self.statusDeadTimer == 18:    # parpadeo!
            self.wGameCanv.itemconfigure(self.wGameCanvMovingObjects[0], state='hidden')

        elif 18 < self.statusDeadTimer <= 22:   # esperando un momento
            pass

        else:
            self.encounterEventDeadRestart()


    def encounterEventDeadRestart(self):
        ## Detén el evento de muerte y reinicia el juego
        if self.statusLife >= 0:
            self.statusDeadTimer = 0    # Reiniciar el temporizador de cuenta regresiva
            self.timerDeath.stop()      # Detener el temporizador para el evento de muerte
            self.isPlaying = False      # Verificar la bandera isPlaying
            field.gameEngine.levelPelletRemaining = 0   # Reiniciar el conteo de pellets (se volverá a contar en __initLevel)
            self.__initLevel(self.currentLv)
        
        else:   # game over!!
            self.statusDeadTimer = 0
            self.timerDeath.stop()
            self.gameOverTimer = PerpetualTimer(0.55, self.encounterEventDeadGameOver)
            self.gameOverTimer.start()



    def encounterEventDeadGameOver(self):
        self.statusDeadTimer += 1
        self.wGameCanv.itemconfig(self.wGameCanvLabelGameOver, image=self.wSprites['gameover'])

        if self.statusDeadTimer < 8:
            # función de parpadeo
            if self.statusDeadTimer % 2 == 1:
                self.wGameCanv.itemconfigure(self.wGameCanvLabelGameOver, state='normal')
            else:
                self.wGameCanv.itemconfigure(self.wGameCanvLabelGameOver, state='hidden')

        else:   # Después de 8 iteraciones, el juego ha finalizado por completo.
            self.gameOverTimer.stop()




class PerpetualTimer(object):
    
    def __init__(self, interval, function, *args):
        self.thread = None
        self.interval = interval
        self.function = function
        self.args = args
        self.isRunning = False

    
    def _handleFunction(self):
        self.isRunning = False
        self.start()
        self.function(*self.args)

    def start(self):
        if not self.isRunning:
            self.thread = Timer(self.interval, self._handleFunction)
            self.thread.start()
            self.isRunning = True

    def stop(self):
            self.thread.cancel()
            self.isRunning = False


# Inicializar Pygame para efectos de sonido
pygame.mixer.init(22050, -16, 2, 64)
pygame.init()

mainEngine = MainEngine()