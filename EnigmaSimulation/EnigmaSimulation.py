# == Enigma Machine and Bombe Decryption ==
# =     by John Finegan          v 1.0.00 =
# =                                       =
# =       University of Cincinnati        =
# =             Spring 2019               =
# =========================================

import pygame as pg
#import glob

# check out http://enigmaco.de/enigma/enigma.html

alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

# Reflectors
#   Standard
reflectorA = 'EJMZALYXVBWFCRQUONTSPIKHGD'
reflectorB = 'YRUHQSLDPXNGOKMIEBFZCWVJAT'
reflectorC = 'FVPJIAOYEDRZXWGCTKUQSBNMHL'
#   Navy
reflectorBt = 'ENKQAUYWJICOPBLMDXZVFTHRGS'
reflectorCt = 'RDOBJNTKVEHMLFCWZAXGYIPSUQ'


# Class for individual rotors.
# Includes:
#   rotorConnections - Cipherbet of the rotor class, static per rotor
#   currentRotation - rotational location of the rotor, changes as operates
#   ringSetting - configurable setting of cipherbet in relation to rotation (a fixed rotation)
#   turnoverNotch - digital representation of when to signal next rotor to rotate
#   
#   Initialization, setters for all settings, rotate method, encipherment/decipherment both forward and back
#
class rotor:

    def __init__(self, cipherbet, notches=None):
        self.currentRotation = 1
        self.ringSetting = 1
        self.turnoverNotch = notches
        self.setConnections(cipherbet)

    def setConnections(self, cipherbet):
        self.rotorConnections = cipherbet

    def setRotate(self, input):
        self.currentRotation = input

    def setRing(self, input):
        self.ringSetting = input

    def rotate(self):
        if self.currentRotation == 26:
            self.currentRotation = 1
        else:
            self.currentRotation = self.currentRotation + 1
        if self.turnoverNotch is not None:
            for notch in self.turnoverNotch:
                if (self.currentRotation - 1) == (alphabet.index(notch) + 1):
                    return True
        elif self.currentRotation == 26:
            return True

    def validate(self, num):
        if num <= 0:
            return 26 + num
        elif num >= 26:
            return num - 26
        else:
            return num
    
    def mapLetter(self, input, direction):
        num = input
        num = self.validate(num - self.ringSetting)
        num = self.validate(num + self.currentRotation)
        
        if direction == 2:
            letter = alphabet[num]
            num = self.rotorConnections.index(letter)
        else:
            letter = self.rotorConnections[num]
            num = alphabet.index(letter)

        num = self.validate(num - self.currentRotation)
        num = self.validate(num + self.ringSetting)
        
        return num

    def getLetter(self, input):
        return alphabet[input]


# Standard Rotors
rotor1 = rotor('EKMFLGDQVZNTOWYHXUSPAIBRCJ', 'Q')
rotor2 = rotor('AJDKSIRUXBLHWTMCQGZNPYFVOE', 'E')
rotor3 = rotor('BDFHJLCPRTXVZNYEIWGAKMUSQO', 'V')
rotor4 = rotor('ESOVPZJAYQUIRHXLNFTGKDCMWB', 'J')
rotor5 = rotor('VZBRGITYUPSDNHLXAWMJQOFECK', 'Z')
rotor6 = rotor('JPGVOUMFYQBENHZRDKASXLICTW', 'ZM')
rotor7 = rotor('NZJHGRCXMYSWBOUFAIVLPEKQDT', 'ZM')
rotor8 = rotor('FKQHTLXOCBJSPDZRAMEWNIUYGV', 'ZM')

# Navy Rotors
rotorBeta = rotor('LEYJVCNIXWPBQMDRTAKZGFUHOS')
rotorGamma = rotor('FSOKANUERHMBTIYCWLQPZXVGJD')

# Class for enigma machines
# Includes:
#   Rotors - 3 objects of the 'rotor' class, can be configured
#               Navy Rotor is optional, defaults to None, does not rotate (by design!)
#   Reflector - current reflector cipherbet used, can be configured
#   Plugboard - list of pairs of characters indicating which swaps need to be made
#   
#   Initialization, setters for all settings of enigma machine and individual rotors,
#   encryption/decryption operation letter by letter
#
class EnigmaMachine:
    
    def __init__(self, RR = rotor1, MR = rotor2, LR = rotor3, RF = reflectorA, NR = None, PB = None):
        if NR is not None:
            self.NavyRotor = NR
        else:
            self.NavyRotor = None
        
        self.plugboard = {}
        if PB is not None:
           self.setPlugboard(PB)

        self.RightRotor = RR
        self.MiddleRotor = MR
        self.LeftRotor = LR
        self.MachineReflector = RF
        self.setRotorRotation([26,1,1])
        

    def setRotor(self, position, choice):
        switchRotor = {
            1: rotor1,
            2: rotor2,
            3: rotor3,
            4: rotor4,
            5: rotor5,
            6: rotor6,
            7: rotor7,
            8: rotor8,
            9: None,
            10: rotorBeta,
            11: rotorGamma
            }
        switchPosition = {
            1: 'Left',
            2: 'Middle',
            3: 'Right',
            4: 'Navy'
            }
        if switchPosition.get(position) == 'Left':
            self.LeftRotor = switchRotor.get(choice)
        elif switchPosition.get(position) == 'Middle':
            self.MiddleRotor = switchRotor.get(choice)
        elif switchPosition.get(position) == 'Right':
            self.RightRotor = switchRotor.get(choice)
        elif switchPosition.get(position) == 'Navy':
            self.NavyRotor = switchRotor.get(choice)

    def setReflector(self, input):
        self.MachineReflector = input
        

    def setRotorRotation(self, rotSettings):
        self.RightRotor.setRotate(rotSettings[0])
        self.MiddleRotor.setRotate(rotSettings[1])
        self.LeftRotor.setRotate(rotSettings[2])

    def setRingSetting(self, rinSettings):
        self.RightRotor.setRing(rinSettings[0])
        self.MiddleRotor.setRing(rinSettings[1])
        self.LeftRotor.setRing(rinSettings[2])


    def setPlugboard(self, plugboardString):
        if plugboardString == '':
            self.plugboard = {}
        else:
            PB = plugboardString.split(' ')
            for i in PB:
                if len(i) == 2:
                    if i[0] not in self.plugboard and i[1] not in self.plugboard and len(self.plugboard) <= 10:
                        self.plugboard.update( { i[0] : i[1] } )
                        self.plugboard.update( { i[1] : i[0] } )

    # Input text to be encrypted/decrypted.  Rotate after each letter
    def cryption(self, inputText):
        text = inputText
        cipheredText = ''
        for i in text:
            if i != " ":
                self.rotateRotors()
                cipheredText += self.cipher(i)
            else:
                cipheredText += i
        return cipheredText

    # Rotate rotors 1 machine state - Notches implemented as true checks in rotor class...double stepping implemented
    def rotateRotors(self):
        if self.RightRotor.rotate():
            if self.MiddleRotor.rotate():
                self.LeftRotor.rotate()
                self.MiddleRotor.rotate()

    # Letter by letter encryption/decryption        
    def cipher(self, letter):
        #Plugboard Character Swap Forward
        ciphered = self.plugboardSwap(letter)

        #Forward cipherment - R -> M -> L
        ciphered = self.RightRotor.mapLetter(alphabet.index(ciphered), 1) 
        ciphered = self.MiddleRotor.mapLetter(ciphered, 1)
        ciphered = self.LeftRotor.mapLetter(ciphered, 1)

        if type(self.NavyRotor) == rotor:
            ciphered = self.NavyRotor.mapLetter(ciphered, 1)

        #reflector
        ciphered = alphabet.index( self.MachineReflector[ciphered] )
        
        #Backward cipherment - L -> M -> R
        if type(self.NavyRotor) == rotor:
            ciphered = self.NavyRotor.mapLetter(ciphered, 2)

        ciphered = self.LeftRotor.mapLetter(ciphered, 2)
        ciphered = self.MiddleRotor.mapLetter(ciphered, 2)
        ciphered = self.RightRotor.mapLetter(ciphered, 2)
        
        ciphered = alphabet[ciphered]

        #Plugboard Character Swap Backward
        ciphered = self.plugboardSwap(ciphered)

        return ciphered

    def decryption(self, inputText):
        return self.cryption(text)
 
    def plugboardSwap(self, letter):
        if letter in self.plugboard:
            return self.plugboard.get(letter)
        else:
            return letter

#TODO Bombe Machine - Time permitting
# Class for Bombe Machine Operation
# Includes:
#   crib - substring believed to be contained in encryptedText
#   cribPosition - position of the start of the crib in relation to encryptedText
#   encryptedText - text to be decrypted/analyzed
#   settingsFound - array of settings that map the crib onto part of the encrypted text, includes false positives
#   enigmaArray - array of enigmas set to progressive rotations to find matches
#   
#   Initialization, crib/encryptedText letter by letter validity check (Enigma cannot map a letter as itself)
#   
#   
#   
#   
#   
class BombeMachine:
    
    def __init__(self):
        print("It's a Bombe!")
        self.crib = ''
        self.cribPosition = 0
        self.encryptedText = ''
        self.settingsFound = []
        self.enimgaArray = [EnigmaMachine(rotor1, rotor2, rotor3, reflectorA) for i in range(36)]

    def checkCribPosition(self):
        if ( self.cribPosition + self.crib.len() ) > self.encryptedText.len():
            return False
        searchEncrypt = self.encryptedText[ self.cribPosition : self.cribPosition + self.crib.len() ]
        noMatch = True
        for i in range( crib.len() ):
            if self.crib[i] == searchEncrypt[i]:
                noMatch = False
        if not noMatch:
            self.cribPosition += 1
            self.checkCribPosition()
        return True
    
    def deducePlugboard(self):
        # assume some combination 'AA' -> 'AZ', then move to 'BB' -> 'BZ'
        # if exists in invalidated setting or is the reverse, skip to next setting.
        invalidatedSettings = []
        settingsFound = []
        contradictionFound = False
        i = 0
        j = 0
        assumption = plugboardOptions[i] + plugboardOptions[j]
        
        while assumption in invalidatedSettings or assumption[::-1] in invalidatedSettings:
            if i > 26:
                break
            else:
                i += 1
                j += 1
            assumption = alphabet[i] + alphabet[j]

        #Work through Assumption and build plugboard combinations until a false flag is triggered
        for letter in self.crib:
            if letter in assumption:
                self.encryptedText  
        
        #if false, all deductions so far go to invalidated settings
        if contradictionFound:
            for plug in self.settingsFound:
                invalidatedSettings.append(plug)
            
            #if no match, change rotor positions and 
            self.incrementRotors()
            self.deducePlugboard()
        return

    def incrementRotors(self):
        for enigma in self.enimgaArray:
            enigma.rotateRotors()
    
    def resetBombe(self):
        self.crib = ''
        self.cribPosition = 0
        self.encryptedText = ''
        self.invalidatedSettings = []
        self.settingsFound = []





#TODO Pygame interface
# Need ----
# Title
# Text Box - input
# Settings for Enigma displayed, connect to current methods
#
#

SCREEN_SQW = 35
SCREEN_SQH = 25
SQ = 30

pg.init()
screen = pg.display.set_mode((SCREEN_SQW * SQ, SCREEN_SQH * SQ))

pg.display.set_caption('Enigma Machine')

COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')
FONT = pg.font.Font(None, 32)


class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.text2 = ''
        self.text3 = ''
        self.txt_surface = FONT.render(text, True, self.color)
        self.txt_surface2 = FONT.render(self.text2, True, self.color)
        self.txt_surface3 = FONT.render(self.text3, True, self.color)
        self.active = False
        self.enabled = True

        self.charLim = 23

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    self.active = False
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif len(self.text) < 3*self.charLim:
                    if event.unicode.upper() in alphabet or event.unicode == ' ':
                        self.text += event.unicode
                        self.text = self.text.upper()
                

    def update(self):
        # Resize the box if the text is too long.
        width = max(13*SQ, self.txt_surface.get_width()+10)
        self.rect.w = width
        # Re-render the text.
        if len(self.text) >= self.charLim:
            if len(self.text2) >= self.charLim:
                self.text2 = self.text[ self.charLim : ( self.charLim * 2 ) ]
                self.text3 = self.text[ ( self.charLim * 2 ) : ]
            else:
                self.text2 = self.text[ self.charLim : ]
            
            self.text1 = self.text[ : self.charLim ]
            
            self.txt_surface = FONT.render(self.text1, True, self.color)
            self.txt_surface2 = FONT.render(self.text2, True, self.color)
            self.txt_surface3 = FONT.render(self.text3, True, self.color)
        else:
            self.txt_surface = FONT.render(self.text, True, self.color)
            self.txt_surface2 = FONT.render('', True, self.color)
            self.txt_surface3 = FONT.render('', True, self.color)

    def draw(self, screen):
        if self.enabled is True:
            # Blit the text.
            screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
            screen.blit(self.txt_surface2, (self.rect.x+5, self.rect.y+35))
            screen.blit(self.txt_surface3, (self.rect.x+5, self.rect.y+65))

            # Blit the rect.
            pg.draw.rect(screen, self.color, self.rect, 2)


class EncryptBox(InputBox):
    def UpdateOther(self, enigma, other, rotSet):
        enigma.setRotorRotation(rotSet)
        other.text = enigma.cryption(self.text)


class DecryptBox(InputBox):

    def UpdateOther(self, enigma, other, rotSet):
        enigma.setRotorRotation(rotSet)
        other.text = enigma.cryption(self.text)

    def setEnigmaSettings(self, enigma):
        print('Settings set')

class ReflectorBox:
    def __init__(self, x, y, w, h, enigma=EnigmaMachine(), text='0'):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.index = 0
        self.machine = enigma
        self.reflectorList = [reflectorA, reflectorB, reflectorC, reflectorBt, reflectorCt]
        self.txt_surface = FONT.render(self.text, True, self.color)
        self.enabled = True
    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if self.index == 4:
                self.index = 0
            else:
                self.index += 1
            self.machine.setReflector(self.reflectorList[self.index])
            self.text = str(self.index)
    def draw(self, screen):
        if self.enabled is True:
            self.txt_surface = FONT.render(self.text, True, self.color)
            screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
            pg.draw.rect(screen, self.color, self.rect, 2)

class RotorBox:
    def __init__(self, x, y, w, h, enigma = EnigmaMachine(), position = '', text='0'):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.index = 0
        self.machine = enigma
        self.postion = position
        self.rotorList = [rotor1, rotor2, rotor3, rotor4, rotor5, rotor6, rotor7, rotor8]
        self.txt_surface = FONT.render(self.text, True, self.color)
        self.enabled = True
    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if self.index == 7:
                self.index = 0
            else:
                self.index += 1
            self.machine.setRotor(self.postion, self.index + 1)
            self.text = str(self.index)
    def draw(self, screen):
        if self.enabled is True:
            self.txt_surface = FONT.render(self.text, True, self.color)
            screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
            pg.draw.rect(screen, self.color, self.rect, 2)

class NavyRotorBox:
    def __init__(self, x, y, w, h, enigma = EnigmaMachine(), text = '0'):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.index = 0
        self.machine = enigma
        self.position = 4
        self.rotorList = [None, rotorBeta, rotorGamma]
        self.txt_surface = FONT.render(self.text, True, self.color)
        self.enabled = True
    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if self.index == 2:
                self.index = 0
            else:
                self.index += 1
            if self.rotorList[self.index] is not None:
                self.machine.setRotor(self.position, self.index + 9)
            self.text = str(self.index)
    def draw(self, screen):
        if self.enabled is True:
            self.txt_surface = FONT.render(self.text, True, self.color)
            screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
            pg.draw.rect(screen, self.color, self.rect, 2)

class RingSettingBox:
    def __init__(self, x, y, w, h, text='A'):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.index = 0
        self.txt_surface = FONT.render(self.text, True, self.color)
        self.enabled = True
    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if self.index == 25:
                self.index = 0
            else:
                self.index += 1
            self.text = alphabet[self.index]
    def draw(self, screen):
        if self.enabled is True:
            self.txt_surface = FONT.render(self.text, True, self.color)
            screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
            pg.draw.rect(screen, self.color, self.rect, 2)

class RotationBox:
    def __init__(self, x, y, w, h, text='1'):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.index = 0
        self.txt_surface = FONT.render(self.text, True, self.color)
        self.enabled = True
    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if self.index == 25:
                self.index = 0
            else:
                self.index += 1
            self.text = str(self.index + 1)
    def draw(self, screen):
        if self.enabled is True:
            self.txt_surface = FONT.render(self.text, True, self.color)
            screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
            pg.draw.rect(screen, self.color, self.rect, 2)

class FunctionButton:
    def __init__(self, x, y, w, h, function):
        self.rect = pg.Rect(x, y, w, h)
        self.color = pg.Color("red")
        self.function = function
        self.enabled = True
        self.running = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.running = True
                self.color = pg.Color("green")
        else:
            self.color = pg.Color("red")
            self.running = False
    def draw(self, screen):
        if self.enabled is True:
            pg.draw.rect(screen, self.color, self.rect, 2)

class HelpButton:
    def __init__(self, x, y, w, h):
        self.rect = pg.Rect(x, y, w, h)
        self.color = pg.Color("red")
        self.HelpScreen = False
        self.enabled = True

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.HelpScreen = not self.HelpScreen
             
    def draw(self, screen):
        if self.HelpScreen is True:
            self.color = pg.Color("green")
        else:
            self.color = pg.Color("red")
        pg.draw.rect(screen, self.color, self.rect, 2)

class TextLink:
    def __init__(self, x, y, text = '', displayBox = None):
        self.x = x
        self.y = y
        self.link = text
        self.color = COLOR_ACTIVE
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False
        self.displayBox = displayBox
    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.active = not self.ative
            if self.displayBox is not None:
                self.displayBox.active = not self.displayBox.active
            
    def draw(self, screen):
        if self.active is True:
            self.txt_surface = FONT.render(self.link, True, COLOR_ACTIVE)
        else:
            self.txt_surface = FONT.render(self.link, True, COLOR_INACTIVE)
        screen.blit(self.txt_surface, (self.x+5, self.y+5))

class helpDisplay:
    def __init__(self, x, y, title = '', caption = '', imagePath='', text=''):
        self.x = x
        self.y = y
        self.color = COLOR_ACTIVE
        
        self.image = pg.transform.scale(pg.image.load(imagePath), (600,400))

        self.text = text
        self.txt_surface_title = FONT.render(title, True, self.color)
        self.txt_surface_caption = FONT.render(caption, True, self.color)
        self.txt_surface_text = FONT.render(text, True, self.color)
        
        self.active = False
    def draw(self, screen):
        screen.blit(self.txt_surface_title, (self.x+5, self.y+5))
        screen.blit(self.txt_surface_caption, (self.x+5, self.y+430))
        screen.blit(self.txt_surface_text, (self.x+5, self.y+460))
        screen.blit(self.image, (self.x+5, self.y+30))

def main():
    # Populate Help Links and Descriptions
    #for file in glob.glob('.txt'):
    #   file.open()

    #Help1 = helpDisplay(10*SQ, 2*SQ, 'Instructions', 'Enigma and Bombe Simulator', 'Help.png', 'TO USE THE SIMMULATOR, SET THE SETTINGS AND INPUT YOUR TEXT VIA THE ENCRYPTION BOX')
    #Help1Link = TextLink(2*SQ, 2*SQ, 'Instructions', Help1)





    clock = pg.time.Clock()

    HelpEnabled = False

#    MaineBombe = BombeMachine()
    
    Plugs = ""

    Encrypt = ""
    Decrypt = ""

    #Enigma Operation UI
    MainEnigma = EnigmaMachine(rotor3, rotor2, rotor1, reflectorB)
    #Buttoms
    UpdateEnigmaButton = FunctionButton(2*SQ,13*SQ,2*SQ,2*SQ,MainEnigma.rotateRotors())
    RunBombeButton = FunctionButton(31*SQ,13*SQ,2*SQ,2*SQ,MainEnigma.rotateRotors())
    Help = HelpButton(32*SQ,2*SQ,1*SQ,1*SQ)

    # Input Boxes
    ReflectorChoice = ReflectorBox(1*SQ, 2*SQ, 1*SQ, 1*SQ, MainEnigma)
    
    MarineRingSetting = RingSettingBox(3*SQ, 1*SQ, 1*SQ, 1*SQ)
    MarineRotorChoice = NavyRotorBox(3*SQ, 2*SQ, 1*SQ, 1*SQ, MainEnigma)

    LeftRingSetting = RingSettingBox(5*SQ, 1*SQ, 1*SQ, 1*SQ)
    LeftRotorChoice = RotorBox(5*SQ, 2*SQ, 1*SQ, 1*SQ, MainEnigma, 1)
    LeftRotationSetting = RotationBox(5*SQ, 3*SQ, 1*SQ, 1*SQ)
    
    MiddleRingSetting = RingSettingBox(7*SQ, 1*SQ, 1*SQ, 1*SQ)
    MiddleRotorChoice = RotorBox(7*SQ, 2*SQ, 1*SQ, 1*SQ, MainEnigma, 2)
    MiddleRotationSetting = RotationBox(7*SQ, 3*SQ, 1*SQ, 1*SQ)

    RightRingSetting = RingSettingBox(9*SQ, 1*SQ, 1*SQ, 1*SQ)
    RightRotorChoice = RotorBox(9*SQ, 2*SQ, 1*SQ, 1*SQ, MainEnigma, 3)
    RightRotationSetting = RotationBox(9*SQ, 3*SQ, 1*SQ, 1*SQ)

    RotationSettings = [RightRotationSetting.index + 1, MiddleRotationSetting.index + 1, MiddleRotationSetting.index + 1]
    
    
    MainEnigma.setRotorRotation(RotationSettings)


    PlugboardSettings = InputBox(2*SQ,16*SQ,12*SQ,2*SQ)
    EncryptionInput = EncryptBox(2*SQ,19*SQ,12*SQ,4*SQ)
    DecryptionInput = DecryptBox(17*SQ,19*SQ,12*SQ,4*SQ)
    CribInput = InputBox(17*SQ,16*SQ,4*SQ,2*SQ)
    PlugboardFound = InputBox(17*SQ,13*SQ,4*SQ,2*SQ)

    en_settings = [ReflectorChoice, MarineRotorChoice, MarineRingSetting, LeftRotorChoice, LeftRingSetting, LeftRotationSetting, MiddleRotorChoice, MiddleRingSetting, MiddleRotationSetting, RightRotorChoice, RightRingSetting, RightRotationSetting]

    input_boxes = [PlugboardSettings, EncryptionInput, DecryptionInput, CribInput, PlugboardFound]

    buttons = [UpdateEnigmaButton, RunBombeButton, Help]

    #helpLinks = [Help1Link]
    
    #Enigma Help Screen UI
    
    
    
    
    
    
    done = False

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            for box in input_boxes:
                box.handle_event(event)
            for button in buttons:
                button.handle_event(event)
            for item in en_settings:
                item.handle_event(event)

        screen.fill((30, 30, 30))

        #Enigma Operation
        for setting in en_settings:
            if Help.HelpScreen is True:
                setting.enabled = False
            else:
                setting.enabled = True
            setting.draw(screen)
        
            RotationSettings = [RightRotationSetting.index + 1, MiddleRotationSetting.index + 1, MiddleRotationSetting.index + 1]
            RingSettings = [RightRingSetting.index, MiddleRingSetting.index, LeftRingSetting.index]
            MainEnigma.setRotorRotation(RotationSettings)
            MainEnigma.setRingSetting(RingSettings)
            Plugs = PlugboardSettings.text
            MainEnigma.setPlugboard(Plugs)

        if EncryptionInput.active is True:
            EncryptionInput.UpdateOther(MainEnigma, DecryptionInput, RotationSettings)
        elif DecryptionInput.active is True:
            DecryptionInput.UpdateOther(MainEnigma, EncryptionInput, RotationSettings)
        
        for box in input_boxes:
            if Help.HelpScreen is True:
                box.enabled = False
            else:
                box.enabled = True
            box.draw(screen)

        for button in buttons:
            if Help.HelpScreen is True:
                button.enabled = False
            else:
                button.enabled = True
            button.draw(screen)

        for box in input_boxes:
            box.update()

            #Help Links Rendering    
        
        '''
        for link in helpLinks:
            if Help.HelpScreen is True:
                link.active = True
                link.draw(screen)
                link.displayBox.draw(screen)
            else:
                link.active = False
                link.displayBox.active = False
        '''
            
        pg.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    main()
    pg.quit()

