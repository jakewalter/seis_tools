#! /usr/bin/env picpython
# BEGIN PROGRAM: QPEEK
# By: Bob Greschke
# Started: 2012.291
#   Q330/Nanometrics data file reader and plotter.

from sys import argv, exit, platform
PROGSystem = platform[:3].lower()
PROG_NAME = "QPEEK"
PROG_NAMELC = "qpeek"
PROG_VERSION = "2013.282"
PROG_LONGNAME = "Q330/Nanometrics Data File Reader/Plotter"
PROG_SETUPSVERS = "A"
PROG_CPSETUPSVERS = "A"

# If True the program will ignore the saved main display geometry information.
PROGIgnoreGeometry = False
PROGSmallScreen = False
for Arg in argv[1:]:
    if Arg == "-#":
        print PROG_VERSION
        exit()
    elif Arg == "-g":
        PROGIgnoreGeometry = True
        PROGSmallScreen = False
    elif Arg == "-s":
        PROGSmallScreen = True
        PROGIgnoreGeometry = True

########################
# BEGIN: versionChecks()
# LIB:versionChecks():2013.296
#   Checks the current version of Python and sets up a couple of things for the
#   rest of the program to use.
#   Obviously this is not a real function. It's just a collection of things for
#   all programs to check and making it look like a library function makes it
#   easy to update everywhere.
# For putting Python 3 support in.
from sys import version_info
PROG_PYVERSION = "%d.%d.%d"%(version_info[0], version_info[1], version_info[2])

if version_info[0] != 2:
    print ("%s only runs on Python 2."%PROG_NAME)
    if version_info[1] < 4:
# The isinstance(X, *tuple*) stuff requires this.
        print ("%s only runs on Python 2.4 and above."%PROG_NAME)
    exit()
# basestring covers ASCII and Unicode str's and showed up in v2.4.
try:
    isinstance(PROG_NAME, basestring)
except NameError:
    basestring = str
# END: versionChecks

from Tkinter import *
from calendar import monthcalendar, setfirstweekday
from copy import deepcopy
from math import cos, sin, sqrt
from os import access, environ, listdir, makedirs, popen, remove, sep, umask, \
        W_OK
from os.path import abspath, basename, dirname, exists, getsize, isdir, isfile
from string import rstrip, strip
from struct import pack, unpack
from sys import maxint
from time import gmtime, localtime, sleep, strftime, time
from tkFont import Font
from urllib import urlopen
from warnings import filterwarnings

filterwarnings("ignore")
setfirstweekday(6)

# This is way up here so StringVars and IntVars can be declared throughout the
# code.
Root = Tk()
Root.withdraw()

# For the program's forms, Text fields, buttons...
PROGBar = {}
PROGCan = {}
PROGEnt = {}
PROGFrm = {}
PROGMsg = {}
PROGTxt = {}

# All files will be created with u=rw g=rw o=rw.
umask(0000)

#####################
# BEGIN: option_add()
# LIB:option_add():2013.184
#   A collection of setup items common to most of my programs.
# Where all of the vars for saving and loading are kept.
PROGSetups = []
# These will be saved if this program saves setups. They will be used by some
# programs to determine if they are running on the same hardware as the
# previous time or not.
PROGScreenWidthOrig = IntVar()
PROGScreenHeightOrig = IntVar()
PROGScreenWidthOrig.set(Root.winfo_screenwidth())
PROGScreenHeightOrig.set(Root.winfo_screenheight())
PROGSetups += ["PROGScreenWidthOrig", "PROGScreenHeightOrig"]
# These are not saved and will be what gets compared with the above after
# starting if the program cares.
PROGScreenWidthOrigNow = Root.winfo_screenwidth()
PROGScreenHeightOrigNow = Root.winfo_screenheight()
# The small screen setting is usually for testing purposes.
if PROGSmallScreen == False:
# These are for the program to mess with.
    PROGScreenWidth = PROGScreenWidthOrig.get()
    PROGScreenHeight = PROGScreenHeightOrig.get()
else:
    PROGScreenWidth = 1024
    PROGScreenHeight = 768
# Fonts: a constant nagging problem, though less now. I've stopped trying
# to micromanage them and mostly let the user suffer with what the system
# decides to use.
# Some items (like ToolTips and Help text) may not want to have their fonts
# resizable. So in that case use these Orig fonts whose values do not get saved
# to the setups.
PROGOrigMonoFont = Text().cget("font")
PROGOrigPropFont = Entry().cget("font")
# Only two fonts. If something needs more it will have to modify these.
PROGMonoFont = Font(font = Text()["font"])
PROGMonoFontSize = IntVar()
PROGMonoFontSize.set(PROGMonoFont["size"])
# Entry() is used because it seems to be messed with less on different
# systems unlike Label() font which can be set to some bizarre stuff.
PROGPropFont = Font(font = Entry()["font"])
# Used by some plotting routines.
PROGPropFontHeight = PROGPropFont.metrics("ascent")+ \
        PROGPropFont.metrics("descent")
PROGPropFontSize = IntVar()
PROGPropFontSize.set(PROGPropFont["size"])
Root.option_add("*Font", PROGPropFont)
Root.option_add("*Text*Font", PROGMonoFont)
if PROGSystem == "dar":
# A "new" version of PASSCAL Tkinter sets this to 1.
    Root.option_add("*Button*borderWidth", "2")
    PROGSystemName = "Darwin"
elif PROGSystem == "lin":
    PROGSystemName = "Linux"
elif PROGSystem == "win":
    PROGSystemName = "Windows"
elif PROGSystem == "sun":
    PROGSystemName = "Sun"
else:
    PROGSystemName = "Unknown (%s)"%PROGSystem
# Depending on the Tkinter version or how it was compiled the scroll bars can
# get pretty narrow.
if Scrollbar().cget("width") < "16":
    Root.option_add("*Scrollbar*width", "16")
# Just using RGB for everything since some things don't handle color names
# correctly, like PIL on OSX doesn't handle "green" very well.
# B = black, C = cyan, G = green, M = magenta, R = red, O = orange, W = white,
# Y = yellow, E = light gray, A = gray, K = dark gray, U = blue,
# N = dark green, S = dark red, y = dark yellow, D = default widget color,
# u = light blue, s = salmon, p = light pink, g = light green,
# r = a little lighter grey almost white, P = Purple, b = dark blue (was the
# U value for years, but it can be hard to see, so U was lightened up a bit)
# Orange should be #FF7F00, but #DD5F00 is easier to see on a white background
# and it still looks OK on a black background. Purple should be A020F0, but
# that was a little dark.
Clr = {"B":"#000000", "C":"#00FFFF", "G":"#00FF00", "M":"#FF00FF", \
        "R":"#FF0000", "O":"#FF7F00", "W":"#FFFFFF", "Y":"#FFFF00", \
        "E":"#DFDFDF", "A":"#8F8F8F", "K":"#3F3F3F", "U":"#0070FF", \
        "N":"#007F00", "S":"#7F0000", "y":"#7F7F00", "D":Root.cget("bg"), \
        "u":"#ADD8E6", "s":"#FA8072", "p":"#FFB6C1", "g":"#90EE90", \
        "r":"#EFEFEF", "P":"#AA22FF", "b":"#0000FF"}
Root.option_add("*Button*takeFocus", "0")
Root.option_add("*Canvas*borderWidth", "0")
Root.option_add("*Canvas*highlightThickness", "0")
Root.option_add("*Checkbutton*anchor", "w")
Root.option_add("*Checkbutton*takeFocus", "0")
Root.option_add("*Entry*background", Clr["W"])
Root.option_add("*Entry*foreground", Clr["B"])
Root.option_add("*Entry*highlightThickness", "2")
Root.option_add("*Entry*insertWidth", "3")
Root.option_add("*Entry*highlightColor", Clr["B"])
Root.option_add("*Entry*disabledBackground", Clr["D"])
Root.option_add("*Entry*disabledForeground", Clr["B"])
Root.option_add("*Listbox*background", Clr["W"])
Root.option_add("*Listbox*foreground", Clr["B"])
Root.option_add("*Listbox*selectBackground", Clr["G"])
Root.option_add("*Listbox*selectForeground", Clr["B"])
Root.option_add("*Listbox*takeFocus", "0")
Root.option_add("*Listbox*exportSelection", "0")
Root.option_add("*Radiobutton*takeFocus", "0")
Root.option_add("*Scrollbar*takeFocus", "0")
# When the slider is really small this might help make it easier to see, but
# I don't know what the system might set for the slider color.
Root.option_add("*Scrollbar*troughColor", Clr["A"])
Root.option_add("*Text*background", Clr["W"])
Root.option_add("*Text*foreground", Clr["B"])
Root.option_add("*Text*takeFocus", "0")
Root.option_add("*Text*highlightThickness", "0")
Root.option_add("*Text*insertWidth", "0")
Root.option_add("*Text*width", "0")
Root.option_add("*Text*padX", "3")
Root.option_add("*Text*padY", "3")
# To control the color of the buttons better in X-Windows programs.
Root.option_add("*Button*activeBackground", Clr["D"])
Root.option_add("*Checkbutton*activeBackground", Clr["D"])
Root.option_add("*Radiobutton*activeBackground", Clr["D"])
# Used by various time functions.
# First day of the month for each non-leap year month MINUS 1. This will get
# subtracted from the DOY, so a DOY of 91, minus the first day of April 90
# (91-90) will leave the 1st of April. The 365 is the 1st of Jan of the next
# year.
PROG_FDOM = (0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365)
# Max days per month.
PROG_MAXDPMNLY = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
PROG_MAXDPMLY = (0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
# Not very friendly to other countries, but...
PROG_CALMON = ("", "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", \
        "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER")
PROG_CALMONS = ("", "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", \
        "SEP", "OCT", "NOV", "DEC")
PROG_MONNUM = {"JAN":1, "FEB":2, "MAR":3, "APR":4, "MAY":5, "JUN":6, "JUL":7, \
        "AUG":8, "SEP":9, "OCT":10, "NOV":11, "DEC":12}
# For use with the return of the calendar module weekday function.
PROG_DOW = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
# Stores the number of seconds to the beginning of a year so they don't have
# to be recalculated all the time.
Y2EPOCH = {}
# First characters that can be used to modifiy searches (only PIS so far).
PROG_SEARCHMODS = "><=#*~_&|"
# END: option_add

# Try to get the machine's name. We'll put that in the Root.title().
PROGHostname = ""
try:
    from socket import gethostname
    PROGHostname = gethostname().split(".")[0]
except:
    pass


# ==============================================
# BEGIN: ========== PROGRAM FUNCTIONS ==========
# ==============================================


################################
# BEGIN: beep(Howmany, e = None)
# LIB:beep():2013.228
#   Just rings the terminal bell the number of times requested.
# NEEDS: from time import sleep
#        updateMe()
PROGNoBeepingCRVar = IntVar()
PROGSetups += ["PROGNoBeepingCRVar", ]

def beep(Howmany, e = None):
    if PROGNoBeepingCRVar.get() == 0:
# In case someone passes something wild.
        if Howmany > 20:
            Howmany = 20
        for i in xrange(0, Howmany):
            Root.bell()
            if i < Howmany-1:
                updateMe(0)
                sleep(.15)
    return
# END: beep




##############################
# BEGIN: class BButton(Button)
# LIB:BButton():2009.239
#   A sub-class of Button() that adds a bit of additional color control and
#   that adds a space before and after the text on Windows systems, otherwise
#   the edge of the button is right at the edge of the text.
class BButton(Button):
    def __init__(self, master = None, **kw):
        if PROGSystem == "win" and "text" in kw:
            if kw["text"].find("\n") == -1:
                kw["text"] = " "+kw["text"]+" "
            else:
# Add " " to each end of each line so all lines get centered.
                parts = kw["text"].split("\n")
                ntext = ""
                for part in parts:
                    ntext += " "+part+" \n"
                kw["text"] = ntext[:-1]
# Some systems have the button change color when rolled over.
        if "bg" in kw:
            kw["activebackground"] = kw["bg"]
        if "fg" in kw:
            kw["activeforeground"] = kw["fg"]
        Button.__init__(self, master, **kw)
# END: BButton




#############################################
# BEGIN: buttonBG(Butt, Colr, State = NORMAL)
# LIB:buttonBG():2012.270
def buttonBG(Butt, Colr, State = ""):
# Try since this may get called without the button even existing.
    try:
        if isinstance(Butt, basestring):
# Set both items to keep the button from changing colors on *NIXs when the
# mouse rolls over. Also only use the first character of the passed value so
# we can pass bg/fg color pairs (I don't think this will ever actually happen).
# If the State is "" leave it alone (it may be one that has been disabled by
# the checklists), otherwise change it to what we are told.
            if State == "":
                PROGButs[Butt].configure(bg = Clr[Colr[0]], \
                        activebackground = Clr[Colr[0]])
            else:
                PROGButs[Butt].configure(bg = Clr[Colr[0]], \
                        activebackground = Clr[Colr[0]], state = State)
        else:
            if State == "":
                Butt.configure(bg = Clr[Colr[0]], \
                        activebackground = Clr[Colr[0]])
            else:
                Butt.configure(bg = Clr[Colr[0]], \
                        activebackground = Clr[Colr[0]], state = State)
        updateMe(0)
    except:
        pass
    return
# END: buttonBG




##########################
# BEGIN: busyCursor(OnOff)
# LIB:busyCursor():2012.104
# Needs PROGFrm, and updateMe().
DefCursor = Root.cget("cursor")

def busyCursor(OnOff):
    if OnOff == 0:
        TheCursor = DefCursor
    else:
        TheCursor = "watch"
    Root.config(cursor = TheCursor)
    for Fram in PROGFrm.values():
        if Fram != None:
            Fram.config(cursor = TheCursor)
    updateMe(0)
    return
# END: busyCursor




#################################################################
# BEGIN: canText(Can, Cx, Cy, Color, Str, Anchor = "w", Tag = "")
# LIB:canText():2013.190
#   Used to print text to a canvas such that the color of individual words
#   in a line can be changed. Use 0 for Cx to tell the routine to place this
#   Str at the end of the last Str passed.
CANTEXTLastX = 0
CANTEXTLastWidth = 0

def canText(Can, Cx, Cy, Color, Str, Anchor = "w", Tag = ""):
    global CANTEXTLastX
    global CANTEXTLastWidth
    if Cx == 0:
        Cx = CANTEXTLastX
    if isinstance(Color, basestring):
# This way it can be passed "W" or #000000.
        if Color.startswith("#") == False:
            FClr = Clr[Color[0]]
        else:
            FClr = Color
        if Tag == "":
            ID = Can.create_text(Cx, Cy, text = Str, fill = FClr, \
                    font = PROGPropFont, anchor = Anchor)
        else:
            ID = Can.create_text(Cx, Cy, text = Str, fill = FClr, \
                    font = PROGPropFont, anchor = Anchor, tags = Tag)
# This may be an input from getAColor().
    elif isinstance(Color, tuple):
        if Tag == "":
            ID = Can.create_text(Cx, Cy, text = Str, fill = Color[0], \
                    font = PROGPropFont, anchor = Anchor)
        else:
            ID = Can.create_text(Cx, Cy, text = Str, fill = Color[0], \
                    font = PROGPropFont, anchor = Anchor, tags = Tag)
    else:
        if Tag == "":
            ID = Can.create_text(Cx, Cy, text = Str, fill = "white", \
                    font = PROGPropFont, anchor = Anchor)
        else:
            ID = Can.create_text(Cx, Cy, text = Str, fill = "white", \
                    font = PROGPropFont, anchor = Anchor, tags = Tag)
    L, T, R, B = Can.bbox(ID)
# -1: I don't know if this is a Tkinter bug or if it just happens to be
# specific to the font that is being used or what, but it has to be done.
    CANTEXTLastX = R-1
    CANTEXTLastWidth = R-L
    return ID
# END: canText




###############################################################################
# BEGIN: center(Parent, TheFrame, Where, InOut, Show, CenterX = 0, CenterY = 0)
# LIB:center():2012.210
# Needs PROGFrm, PROGScreenWidth, PROGScreenHeight, updateMe(), and PROGSystem.
#   Where tells the function where in relation to the Parent TheFrame should
#   show up.  Use the diagram below to figure out where things will end up.
#
#      +---------------+
#      | NW    N    NE |
#      |               |
#      | W     C     E |
#      |               |
#      | SW    S    SE |
#      +---------------+
#
#   Set Parent to None to use the whole display as the parent.
#   Set InOut to "I" or "O" to control if TheFrame shows "I"nside or "O"outside
#   the Parent (does not apply if the Parent is None).
#
#   CenterX and CenterY not equal to zero overrides everything.
#
def center(Parent, TheFrame, Where, InOut, Show, CenterX = 0, CenterY = 0):
    if isinstance(Parent, basestring):
        Parent = PROGFrm[Parent]
    if isinstance(TheFrame, basestring):
        TheFrame = PROGFrm[TheFrame]
# Size of the display(s). Still won't be good for dual displays, but...
    DW = PROGScreenWidth
    DH = PROGScreenHeight
# Kiosk mode. Just take over the whole screen. Doesn't check for, but only
# works for Root. The -30 is a fudge, because systems lie about their height
# (but not their age).
    if Where == "K":
        Root.geometry("%dx%d+0+0"%(DW, DH-30))
        Root.lift()
        Root.deiconify()
        updateMe(0)
        return
# So all of the dimensions get updated.
    updateMe(0)
    FW = TheFrame.winfo_reqwidth()
    if TheFrame == Root:
# Different systems have to be compensated for a little because of differences
# in the reported heights (mostly title and menu bar heights). Some systems
# include the height and some don't, and, of course, it all depends on the
# font sizes, so there is little chance of this fudge ever being 100% correct.
        if PROGSystem == "dar" or PROGSystem == "win":
            FH = TheFrame.winfo_reqheight()
        else:
            FH = TheFrame.winfo_reqheight()+50
    else:
        FH = TheFrame.winfo_reqheight()
# Find the center of the Parent.
    if CenterX == 0 and CenterY == 0:
        if Parent == None:
            PX = 0
            PY = 0
            PW = PROGScreenWidth
            PH = PROGScreenHeight
# A PW of >1920 (the width of a 24" iMac) probably means the user has two
# monitors. Tkinter just gets fed the total width and the smallest display's
# height, so just set the size to 1024x768 and then let the user resize and
# reposition as needed. It's what they get for being so lucky.
            if PW > 1920:
                PW = 1024
                PH = 768
            CenterX = PW/2
            CenterY = PH/2-25
        elif Parent == Root:
            PX = Parent.winfo_x()
            PW = Parent.winfo_width()
            CenterX = PX+PW/2
# Macs, Linux and Suns think the top of the Root window is below the title
# and menu bars.  Windows thinks the top of the window is the top of the
# window, so adjust the window heights accordingly to try and cover that up.
# Same problem as the title and menu bars.
            if PROGSystem == "win":
                PY = Parent.winfo_y()
                PH = Parent.winfo_height()
            else:
                PY = Parent.winfo_y()-50
                PH = Parent.winfo_height()+50
            CenterY = PY+PH/2
        else:
            PX = Parent.winfo_x()
            PW = Parent.winfo_width()
            CenterX = PX+PW/2
            PY = Parent.winfo_y()
            PH = Parent.winfo_height()
            CenterY = PY+PH/2
# Can't put forms outside the whole display.
        if Parent == None or InOut == "I":
            InOut = 1
        else:
            InOut = -1
# C centers and checkes to see that the form is not going to be off the left
# bottom or right edge of the display. CC does not. Non of the others do any
# checking. Most will want checking.
        if Where == "C":
            XX = CenterX-FW/2
            if XX < 0:
                XX = 10
            elif (CenterX+FW/2) > DW:
                XX = XX-((CenterX+FW/2)-DW+20)
            YY = CenterY-FH/2
            if YY < 0:
                YY = 10
            elif (CenterY+FH/2) > DH:
                YY = YY-((CenterY+FH/2)-DH+20)
            TheFrame.geometry("+%i+%i"%(XX, YY))
        elif Where == "CC":
            TheFrame.geometry("+%i+%i"%(CenterX-FW/2, CenterY-FH/2))
        elif Where == "N":
            TheFrame.geometry("+%i+%i"%(CenterX-FW/2, PY+(50*InOut)))
        elif Where == "NE":
            TheFrame.geometry("+%i+%i"%(PX+PW-FW-(50*InOut), PY+(50*InOut)))
        elif Where == "E":
            TheFrame.geometry("+%i+%i"%(PX+PW-FW-(50*InOut), \
                    CenterY-TheFrame.winfo_reqheight()/2))
        elif Where == "SE":
            TheFrame.geometry("+%i+%i"%(PX+PW-FW-(50*InOut), \
                    PY+PH-FH-(50*InOut)))
        elif Where == "S":
            TheFrame.geometry("+%i+%i"%(CenterX-TheFrame.winfo_reqwidth()/2, \
                    PY+PH-FH-(50*InOut)))
        elif Where == "SW":
            TheFrame.geometry("+%i+%i"%(PX+(50*InOut), PY+PH-FH-(50*InOut)))
        elif Where == "W":
            TheFrame.geometry("+%i+%i"%(PX+(50*InOut), \
                    CenterY-TheFrame.winfo_reqheight()/2))
        elif Where == "NW":
            TheFrame.geometry("+%i+%i"%(PX+(50*InOut), PY+(50*InOut)))
    else:
        TheFrame.geometry("+%i+%i"%(CenterX-FW/2, CenterY-FH/2))
    if Show == True:
        TheFrame.lift()
        TheFrame.deiconify()
    updateMe(0)
    return
# END: center




# FINISHME - when formTMRNG comes on line.
###################################
# BEGIN: changeDateFormat(WhereMsg)
# FUNC:changeDateFormat():2013.045
#   Makes sure that the format of any data in the from/to fields matches the
#   format selected in the Options menu.
def changeDateFormat(WhereMsg):
    updateMe(0)
    Format = OPTDateFormatRVar.get()
    for Fld in ("From", "To"):
        eval("%sDateVar"%Fld).set(eval("%sDateVar"%Fld).get().strip().upper())
        if eval("%sDateVar"%Fld).get() != "":
            Ret = dt2Time(0, 80, eval("%sDateVar"%Fld).get(), True)
            if Ret[0] != 0:
                setMsg(WhereMsg, Ret[1], "%s date: %s"%(Fld, Ret[2]), Ret[3])
                return False
            eval("%sDateVar"%Fld).set(Ret[1][:-13])
# For the time range form formTMRNG().
#    for Fld in ("From", "To"):
#        eval("TMRNG%sVar"%Fld).set(eval("TMRNG%sVar"% \
#                Fld).get().strip().upper())
#        if eval("TMRNG%sVar"%Fld).get() != "":
# convertDate is gone.
#            Ret = (Format, eval("TMRNG%sVar"%Fld).get())
#            if Ret[0] != 0:
#                setMsg("TMRNG", "%s field value bad."%Fld, 2)
#                return False
#            eval("TMRNG%sVar"%Fld).set(Ret[1])
    return True
# END: changeDateFormat




####################
# BEGIN: changeDir()
# FUNC:changeDir():2013.047
#   QPEEK just needs to reload the file list after an otherwise normal main
#   data directory change.
def changeDir():
    changeMainDirs(Root, "thedata", 1, None, "")
    loadSourceFiles(MFFiles, "MF")
    return
# END: changeDir




########################################################
# BEGIN: changeMainDirs(Parent, Which, Mode, Var, Title)
# LIB:changeMainDirs():2012.344
# Needs PROGFrm, formMYDF(), PROGMsgsDirVar, PROGDataDirVar, PROGWorkDirVar,
# and msgLn().
#   Mode = formMYDF() mode value (some callers may not want to allow directory
#          creation, for example).
#      1 = just picking
#      2 = picking and creating
#  D,W,M = may be added to the Mode for the main directories Default button
#          (see formMYDF()).
#   Var = if not None the selected directory will be placed there, instead of
#         one of the "main" Vars. May not be used in all programs.
#   Title = Will be used for the title of the form if Var is not None.
#   Not all programs will use all items.
def changeMainDirs(Parent, Which, Mode, Var, Title):
# The caller can pass either.
    if isinstance(Parent, basestring):
        Parent = PROGFrm[Parent]
    if Which == "theall":
# Just use the directory as a starting point.
        Answer = formMYDF(Parent, Mode, "Pick A Main Directory For All", \
                PROGMsgsDirVar.get(), "")
        if Answer == "":
            return (1, "", "Nothing done.", 0, "")
        else:
# Some of these may not exist in a program.
            try:
                PROGDataDirVar.set(Answer)
            except:
                pass
            try:
                PROGMsgsDirVar.set(Answer)
            except:
                pass
            try:
                PROGWorkDirVar.set(Answer)
            except:
                pass
            return (0, "WB", "All main directories changed to\n   %s"% \
                    Answer, 0, "")
    elif Which == "thedata":
        Answer = formMYDF(Parent, Mode, "Pick A Main Data Directory", \
                PROGDataDirVar.get(), "")
        if Answer == "":
            return (1, )
        elif Answer == PROGDataDirVar.get():
            return (0, "", "Main data directory unchanged.", 0, "")
        else:
            PROGDataDirVar.set(Answer)
            return (0, "WB", "Main Data directory changed to\n   %s"% \
                    Answer, 0, "")
    elif Which == "themsgs":
        Answer = formMYDF(Parent, Mode, "Pick A Main Messages Directory", \
                PROGMsgsDirVar.get(), "")
        if Answer == "":
            return (1, )
        elif Answer == PROGMsgsDirVar.get():
            return (0, "", "Main messages directory unchanged.", 0, "")
        else:
            PROGMsgsDirVar.set(Answer)
            return (0, "WB", "Main Messages directory changed to\n   %s"% \
                    Answer, 0, "")
    elif Which == "thework":
        Answer = formMYDF(Parent, Mode, "Pick A Main Work Directory", \
                PROGWorkDirVar.get(), "")
        if Answer == "":
            return (1, )
        elif Answer == PROGWorkDirVar.get():
            return (0, "", "Main work directory unchanged.", 0, "")
        else:
            PROGWorkDirVar.set(Answer)
            return (0, "WB", "Main work directory changed to\n   %s"% \
                    Answer, 0, "")
# Var and Title must be set for "self".
    elif Which == "self":
        Answer = formMYDF(Parent, Mode, Title, Var.get(), Title)
        if Answer == "":
            return (1, )
        elif Answer == Var.get():
            return (0, "", "Directory unchanged.", 0, "")
        else:
            Var.set(Answer)
        return (0, "WB", "Directory changed to\n   %s"%Answer, 0, "")
    return
#####################################################################
# BEGIN: changeMainDirsCmd(Parent, Which, Mode, Var, Title, e = None)
# FUNC:changeMainDirsCmd():2011.281
def changeMainDirsCmd(Parent, Which, Mode, Var, Title, e = None):
    Ret = changeMainDirs(Parent, Which, Mode, Var, Title)
    if Ret[0] == 0:
# Some programs may not have a messages area.
        try:
            msgLn(0, Ret[1], Ret[2], True, Ret[3])
        except:
            pass
    return
# END: changeMainDirs




#######################################
# BEGIN: checkForUpdates(Parent = Root)
# LIB:checkForUpdates():2013.035
# Needs PROGFrm, updateMe(), from urllib import urlopen, readFileLines(),
# formMYD(), progQuitter(), PROGSetupsDirVar, from os.path import abspath,
# from os import sep.
#   Finds the new<prog>.txt file at the URL and checks to see if the version
#   in that file matches the version of this program.
VERS_DLALLOW = True
VERS_VERSURL = "http://www.passcal.nmt.edu/~bob/passoft/"
VERS_PARTS = 4
#VERS_NAME = 0
VERS_VERS = 1
#VERS_USIZ = 2
VERS_ZSIZ = 3

def checkForUpdates(Parent = Root):
    if isinstance(Parent, basestring):
        Parent = PROGFrm[Parent]
# Otherwise the menu doesn't go away on slow connections while url'ing.
    updateMe(0)
# Get the file that tells us about the current version on the server.
# One line:  PROG; version; original size; compressed size
    try:
        Fp = urlopen(VERS_VERSURL+"new"+PROG_NAMELC+".txt")
        Line = readFileLines(Fp)
        Fp.close()
        Line = Line[0]
# If the file doesn't exist you get something like
#     <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
# How unhandy.
        if Line.find("DOCTYPE") != -1:
            raise IOError
    except (IndexError, IOError):
        Line = ""
# If we didn't get this then there must have been a problem.
    if Line == "":
        formMYD(Parent, (("(OK)", TOP, "ok"), ), "ok", "RW", \
                "It's Probably The Net.", \
        "There was an error obtaining the version information from PASSCAL.", \
                "", 2)
        return
    Parts = map(strip, Line.split(";"))
    Parts += (VERS_PARTS-len(Parts))*[""]
    if PROG_VERSION < Parts[VERS_VERS]:
# Some programs don't need to be professionally installed, some do.
        if VERS_DLALLOW == True:
            Answer = formMYD(Parent, (("Download New Version", TOP, \
                    "dlprod"), ("(Don't)", TOP, "dont"), ), "dont", \
                    "YB", "Oh Oh...", \
                    "This is an old version of %s.\nThe current version generally available is %s."% \
                    (PROG_NAME, Parts[VERS_VERS]), "", 2)
            if Answer == "dont":
                return
            if Answer == "dlprod":
                Ret = checkForUpdatesDownload(Parent, Answer, Parts)
            if Ret == "quit":
                progQuitter(True)
                return
        elif VERS_DLALLOW == False:
            Answer = formMYD(Parent, (("(OK)", TOP, "ok"), ), "ok", \
                    "YB", "Tell Someone.", \
                    "This is an old version of %s.\nThe current version generally available is %s."% \
                    (PROG_NAME, Parts[VERS_VERS]), "", 2)
            return
    elif PROG_VERSION == Parts[VERS_VERS]:
        Answer = formMYD(Parent, (("Download Anyway", TOP, "dlprod"), \
                ("(OK)", TOP, "ok")), "ok", "", "Good To Go.", \
                "This copy of %s is up to date."%PROG_NAME)
        if Answer == "ok":
            return
        if Answer == "dlprod":
            Ret = checkForUpdatesDownload(Parent, Answer, Parts)
        if Ret == "quit":
            progQuitter(True)
        return
    elif PROG_VERSION > Parts[VERS_VERS]:
        if VERS_DLALLOW == False:
            Answer = formMYD(Parent, (("(OK)", TOP, "ok"), ), "ok", "GB", \
                    "All Right!", \
                    "Congratulations! This is a newer version of %s than is generally available. Everyone else probably still has version %s."% \
                    (PROG_NAME, Parts[VERS_VERS]))
        elif VERS_DLALLOW == True:
            Answer = formMYD(Parent, (("Download Older Version", TOP, \
                    "dlprod"), ("(No, Thanks.)", TOP, "ok"), ), "ok", \
                    "GB", "All Right!!", \
                    "Congratulations! This is a newer version of %s than is generally available. Everyone else probably still has version %s. You can download and use the older version if you want."% \
                    (PROG_NAME, Parts[VERS_VERS]))
        if Answer == "ok" or Answer == "keep":
            return
        if Answer == "dlprod":
            Ret = checkForUpdatesDownload(Parent, Answer, Parts)
        if Ret == "quit":
            progQuitter(True)
        return
    return
######################################################
# BEGIN: checkForUpdatesDownload(Parent, Which, Parts)
# FUNC:checkForUpdatesDownload():2012.101
def checkForUpdatesDownload(Parent, Which, Parts):
    formMYD(Parent, (), "", "CB", "", "Downloading...")
    ZSize = int(Parts[VERS_ZSIZ])
    try:
        if Which == "dlprod":
            GetFile = "new%s.zip"%PROG_NAMELC
            Fpr = urlopen(VERS_VERSURL+GetFile)
# SetupsDir may not be the best place to put it, but at least it will be
# consistant and not dependent on where the user was working (like it was).
# Some programs may not have PROGSetupsDirVar set to anything, or even call
# this function, but check and set this just in case. .<sep> may not point to
# anywhere sensible, but this is the best we can do.
        SetupsDir = PROGSetupsDirVar.get()
        if SetupsDir == "":
            SetupsDir = "%s%s"%(abspath("."), sep)
        Fpw = open(SetupsDir+GetFile, "wb")
        DLSize = 0
        while 1:
            Buffer = Fpr.read(20000)
            if len(Buffer) == 0:
                break
            Fpw.write(Buffer)
            DLSize += 20000
            formMYDMsg("Downloading (%d%%)...\n"%(100*DLSize/ZSize))
    except Exception, e:
# They may not exist.
        try:
            Fpr.close()
        except:
            pass
        try:
            Fpw.close()
        except:
            pass
        formMYDReturn("")
        formMYD(Parent, (("(OK)", TOP, "ok"), ), "ok", "MW", "Ooops.", \
                "Error downloading new version.\n\n%s"%e, "", 3)
        return ""
    Fpr.close()
    Fpw.close()
    formMYDReturn("")
    if Which == "dlprod":
        Answer = formMYD(Parent, (("Quit %s"%PROG_NAME, TOP, "quit"), \
                ("Don't Quit", TOP, "cont")), "cont", "GB", "Finished?", \
                "The downloaded program file has been saved as\n\n%s\n\nYou should quit %s using the Quit button below, unzip the downloaded file, test the new program file to make sure it is OK, then rename it %s.py and move it to the proper location to replace the old version.\n\nTAKE NOTE OF WHERE THE FILE HAS BEEN DOWNLOADED TO!"% \
                (SetupsDir+GetFile, PROG_NAME, PROG_NAMELC))
    if Answer == "quit":
        return "quit"
    return ""
# END: checkForUpdates




#############################################
# BEGIN: checkLatiLong(Which, Value, Ret = 0)
# LIB:checkLatiLong():2013.048
#   Accepts N00.000 or 00.000N values and returns checked string N00.000
#   values. If Ret == 1 then the float version of the passed Lat/Lon will be
#   returned.
def checkLatiLong(Which, Value, Ret = 0):
    Value = Value.upper().strip()
    if Which == "lati":
        try:
            if Value.startswith("N") or Value.startswith("+"):
                Lat = float(Value[1:])
                Sign = "N"
            elif Value.startswith("S") or Value.startswith("-"):
                Lat = abs(float(Value[1:]))
                Sign = "S"
            elif Value.endswith("N"):
                Lat = floatt(Value)
                Sign = "N"
            elif Value.endswith("S"):
                Lat = floatt(Value)
                Sign = "S"
            else:
                raise ValueError
            if Lat > 90.0:
                return (1, "RW", "Latitude > 90.0.", 2, "")
            if Ret == 0:
                return (0, Sign+"%010.7f"%Lat)
            else:
                if Sign == "S":
                    Lat = -Lat
                return (0, Lat)
        except ValueError:
            return (1, "RW", "Bad latitude: '%s'"%Value, 2, "")
    elif Which == "long":
        try:
            if Value.startswith("E") or Value.startswith("+"):
                Long = float(Value[1:])
                Sign = "E"
            elif Value.startswith("W") or Value.startswith("-"):
                Long = abs(float(Value[1:]))
                Sign = "W"
            elif Value.endswith("E"):
                Long = floatt(Value)
                Sign = "E"
            elif Value.endswith("W"):
                Long = floatt(Value)
                Sign = "W"
            else:
                raise ValueError
            if Long > 180.0:
                return (1, "RW", "Longitude > 180.0.", 2, "")
            if Ret == 0:
                return (0, Sign+"%011.7f"%Long)
            else:
                if Sign == "W":
                    Long = -Long
                return (0, Long)
        except ValueError:
            return (1, "RW", "Bad longitude: '%s'"%Value, 2, "")
# END: checkLatiLong




###########################
# BEGIN: cleanAFilename(In)
# LIB:cleanAFilename():2013.246
#   Goes through the passed string and turns any sep characters or colons into
#   -.
def cleanAFilename(In):
    Out = ""
    for C in In:
        if C == sep or C == ":":
            C = "-"
        Out += C
    return Out
# END: cleanAFilename



    
#################################
# BEGIN: closeForm(Who, e = None)
# LIB:closeForm():2012.145
#   Handles closing a form.
def closeForm(Who, e = None):
# In case it is a "busy" form that takes a long time to close.
    updateMe(0)
# The form may not exist or PROGFrm[Who] may be pointing to a "lost" form, so
# try.
    try:
        if PROGFrm[Who] == None:
            return
        PROGFrm[Who].destroy()
    except:
        pass
    try:
        PROGFrm[Who] = None
    except:
        pass
    return
###############################
# BEGIN: closeFormAll(e = None)
# FUNC:closeFormAll():2012.103
#   Goes through all of the forms and shuts them down.
def closeFormAll(e = None):
    for Frmm in PROGFrm.keys():
# Try to call a formXControl() function. Some may have them and some may not.
        try:
# Expecting from formXControl() functions:
# Ret[0] 0 == Continue.
# Ret[0] 1 == Problem solved, can continue.
# Ret[0] 2 == Problem has or has not been resolved, should stop.
# What actually gets done is handled by the caller this just passes back
# anything that is not 0.
            Ret = eval("form%sControl"%Frmm)("close")
            if Ret[0] != 0:
                return Ret
        except:
            closeForm(Frmm)
    return (0, )
# END: closeForm




######################
# BEGIN: class Command
# LIB:Command():2006.114
#   Pass arguments to functions from button presses and menu selections! Nice!
#   In your declaration:  ...command = Command(func, args,...)
#   Also use in bind() statements
#       x.bind("<****>", Command(func, args...))
class Command:
    def __init__(self, func, *args, **kw):
        self.func = func
        self.args = args
        self.kw = kw
    def __call__(self, *args, **kw):
        args = self.args+args
        kw.update(self.kw)
        self.func(*args, **kw)
# END: Command




#########################
# BEGIN: clearQPGlobals()
# FUNC:clearQPGlobals():2013.046
#   Clears out the QP global variables in one call.
def clearQPGlobals():
    global QPData
    global QPLogs
    global QPGaps
    global QPErrors
    global QPStaIDs
    global QPNetCodes
    global QPTagNos
    global QPSWVers
    global QPLocIDs
    global QPSampRates
    global QPAntSpikesWhacked
    global QPUnknownChanIDs
    global QPUnknownBlocketteType
    global QPFilesProcessed
    global QPPlotRanges
    QPData.clear()
    del QPLogs[:]
    QPGaps.clear()
    del QPErrors[:]
    del QPStaIDs[:]
    del QPNetCodes[:]
    del QPTagNos[:]
    del QPSWVers[:]
    del QPLocIDs[:]
    QPSampRates.clear()
    QPAntSpikesWhacked = 0
    del QPUnknownChanIDs[:]
    del QPUnknownBlocketteType[:]
    del QPFilesProcessed[:]
    del QPPlotRanges[:]
# END: clearQPGlobals




##################################################
# BEGIN: compFs(DirVar, FileVar, VarSet, e = None)
# LIB:compFs():2013.045
# Needs setMsg(), beep()
#     from fnmatch import fnmatch
#     from os.path import basename, dirname, isdir
#   Attempts to complete the directory or file name in an Entry field using
#   the Tab key.
#   - If DirVar is set to a field's StringVar and FileVar is None then the
#     routine only looks for directories.
#   - If DirVar and FileVar are set to StringVars then it works to find a
#     complete fliespec, but getting the path and filenames from different
#     fields.
#   - If DirVar is None and FileVar is set to a StringVar then it trys to
#     complete path and filenames.
#
#   Call compFsSetup() after the Entry field has been created.
def compFs(DirVar, FileVar, VarSet, e = None):
    if VarSet != None:
        setMsg(VarSet, "", "")
# ---- Caller only wants directories.
    if DirVar != None and FileVar == None:
        Dir = dirname(DirVar.get())
# This is a slight gotchya. If the field is empty that might mean that the user
# means "/" should be the starting point. If it is they will have to enter the
# / since if we are on Windows I'd have no idea what the default should be.
        if len(Dir) == 0:
            beep(2)
            return
        if Dir.endswith(sep) == False:
            Dir += sep
# Now get what must be a partial directory name, treat it as a file name, but
# then only allow the result of everything to be a directory.
        PartialFile = basename(DirVar.get())
        if len(PartialFile) == 0:
            beep(2)
            return
        PartialFile += "*"
        Files = listdir(Dir)
        Matched = []
        for File in Files:
            if fnmatch(File, PartialFile):
                Matched.append(File)
        if len(Matched) == 0:
            beep(2)
            return
        elif len(Matched) == 1:
            Dir = Dir+Matched[0]
# If whatever matched is not a directory then just beep and return, otherwise
# make it look like a directory and put it into the field.
            if isdir(Dir) == False:
                beep(2)
                return
            if Dir.endswith(sep) == False:
                Dir += sep
            DirVar.set(Dir)
            e.widget.icursor(END)
            return
        else:
# Get the max number of characters that matched and put the partial directory
# path into the Var. If Dir+PartialDir is really the directory the user wants
# they will have to add the sep themselves since with multiple matches I won't
# know what to do. Consider DIR DIR2 DIR3 with a compFsMaxMatch() return of
# DIR. The directory DIR would always be selected and set as the path which
# may not be what the user wanted. Now this could cause trouble downstream
# since I'm leaving a path in the field without a trailing sep (everything
# tries to avoid doing that), so the caller will have to worry about that.
            PartialDir = compFsMaxMatch(Matched)
            DirVar.set(Dir+PartialDir)
            e.widget.icursor(END)
            beep(1)
            return
    else:
# ---- Find a file, but the filespec is in one field.
        if DirVar == None and FileVar != None:
            Dir = dirname(FileVar.get())
            Which = 1
# ---- Find a file, but path and file are in separate fields.
        elif DirVar != None and FileVar != None:
            Dir = dirname(DirVar.get())
            Which = 2
        if len(Dir) == 0:
            beep(2)
            return
        if Dir.endswith(sep) == False:
            Dir += sep
        PartialFile = basename(FileVar.get())
        if len(PartialFile) == 0:
            beep(2)
            return
# Match anything to what the user has entered for the file name.
        PartialFile += "*"
        Files = listdir(Dir)
        Matched = []
        for File in Files:
            if fnmatch(File, PartialFile):
                Matched.append(File)
        if len(Matched) == 0:
            beep(2)
            return
        elif len(Matched) == 1:
            File = Matched[0]
            Filespec = Dir+File
# We can stick a directory name in a single field, but the user will have to
# change the directory field if they are separate (it may be that the user
# is not allowed to change the directory field value and I don't want to
# violate that, plus that could be really confusing for everyone when we have
# multiple matches).
            if isdir(Filespec):
                if Which == 1:
                    if Filespec.endswith(sep) == False:
                        Filespec += sep
                    FileVar.set(Filespec)
                    e.widget.icursor(END)
                    return
                elif Which == 2:
                    beep(2)
                    return
            if Which == 1:
                FileVar.set(Filespec)
            elif Which == 2:
                FileVar.set(File)
            e.widget.icursor(END)
            return
        else:
            PartialFile = compFsMaxMatch(Matched)
            if Which == 1:
                FileVar.set(Dir+PartialFile)
            elif Which == 2:
                FileVar.set(PartialFile)
            e.widget.icursor(END)
            beep(1)
            return
################################
# BEGIN: compFsMaxMatch(TheList)
# FUNC:compFsMaxMatch():2010.056
#   Goes through the items in TheList (should be str's) and returns the string
#   that matches the start of all of the items.
#   This is the same as the library function maxMatch().
def compFsMaxMatch(TheList):
# This should be the only special case. What is the sound of one thing matching
# itself?
    if len(TheList) == 1:
        return TheList[0]
    Accum = ""
    CharIndex = 0
# If anything goes wrong just return whatever we've accumulated. This will end
# by no items being in TheList or one of the items running out of characters
# (the try) or by the TargetChar not matching a character from one of the
# items (the raise).
    try:
        while 1:
            TargetChar = TheList[0][CharIndex]
            for ItemIndex in xrange(1, len(TheList)):
                if TargetChar != TheList[ItemIndex][CharIndex]:
                    raise Exception
            Accum += TargetChar
            CharIndex += 1
    except Exception:
        pass
    return Accum
##############################################################
# BEGIN: compFsSetup(LFrm, LEnt, DirVar, FileVar, VarSet = "")
# FUNC:compFsSetup():2010.255
#   Just sets up the bind's for the passed Entry field. See compFs() for the
#   DirVar and FileVar explainations.
def compFsSetup(LFrm, LEnt, DirVar, FileVar, VarSet):
    LEnt.bind("<FocusIn>", Command(compFsTabOff, LFrm))
    LEnt.bind("<FocusOut>", Command(compFsTabOn, LFrm))
    LEnt.bind("<Key-Tab>", Command(compFs, DirVar, FileVar, VarSet))
    return
#####################################
# BEGIN: compFsTabOff(LFrm, e = None)
# FUNC:compFsTabOff():2010.225
def compFsTabOff(LFrm, e = None):
    LFrm.bind("<Key-Tab>", compFsNullCall)
    return
###################################
# BEGIN: compFsTabOn(LFrm, e = None)
# FUNC:compFsTabOn():2010.225
def compFsTabOn(LFrm, e = None):
    LFrm.unbind("<Key-Tab>")
    return
#################################
# BEGIN: compFsNullCall(e = None)
# FUNC:compFsNullCall():2012.294
def compFsNullCall(e = None):
    return "break"
# END: compFs




####################
# BEGIN: deComma(In)
# LIB:deComma():2006.190
#   Removes trailng spaces and commas.
def deComma(In):
    Len = len(In)-1
    while Len >= 0:
        if In[Len] != "," and In[Len] != " ":
            break
        Len -= 1
    return In[:Len+1]
# END: deComma




####################################
# BEGIN: diskSizeFormat(Which, Size)
# LIB:diskSizeFormat():2013.036
#   Which = b or e. See below.
def diskSizeFormat(Which, Size):
# The user must do whatever it takes to pass bytes. Which determines what will
# be returned: b=millions/1024K or e=mega/1000K bytes.
# Binary 2^20, 1024K.
    if Which == "b":
        if Size >= 1099511627776:
            return "%.2fTiB"%(Size/1099511627776.0)
        elif Size >= 1073741824:
            return "%.2fGiB"%(Size/1073741824.0)
        elif Size >= 1048576:
            return "%.2fMiB"%(Size/1048576.0)
        elif Size >= 1024:
            return "%.2fKiB"%(Size/1024.0)
        else:
            return "%dB"%Size
# Engineering 10^6, 1000K.
    elif Which == "e":
        if Size >= 1000000000000:
            return "%.2fTB"%(Size/1000000000000.0)
        elif Size >= 1000000000:
            return "%.2fGB"%(Size/1000000000.0)
        elif Size >= 1000000:
            return "%.2fMB"%(Size/1000000.0)
        elif Size >= 1000:
            return "%.2fKB"%(Size/1000.0)
        else:
            return "%dB"%Size
    return "Error"
# END: diskSizeFormat




###############################################################
# BEGIN: dt2Time(InFormat, OutFormat, DateTime, Verify = False)
# LIB:dt2Time():2013.310
#   InFormat = -1 = An Epoch has been passed.
#               0 = Figure out what was passed.
#           other = Use if the caller knows exactly what they have.
#   OutFormat = -1 = Epoch
#                0 = Y M D D H M S.s
#                1 = Uses OPTDateFormatRVar value.
#            other = whatever supported string format the caller wants
#   The format of the time will always be HH:MM:SS.sss.
#   Returns (0/1, <answer or error msg>) if Verify is True, or <answer/0/"">
#   if Verify is False. Confusing, but most of the calls are with Verify set
#   to False, and having to always put [1] at the end of each call was getting
#   old fast. This probably will cause havoc if there are other errors like
#   passing date/times that cannot be deciphered, or passing bad In/OutFormat
#   codes (just "" will be returned), but that's the price of progress. You'll
#   still have to chop off the milliseconds if they are not wanted ([:-4]).
#   Needs option_add(), intt(), floatt(), rtnPattern()
def dt2Time(InFormat, OutFormat, DateTime, Verify = False):
    global Y2EPOCH
    if InFormat == -1:
        YYYY = 1970
        while 1:
            if YYYY%4 != 0:
                if DateTime >= 31536000:
                    DateTime -= 31536000
                else:
                    break
            elif YYYY%100 != 0 or YYYY%400 == 0:
                if DateTime >= 31622400:
                    DateTime -= 31622400
                else:
                    break
            else:
                if DateTime >= 31536000:
                    DateTime -= 31536000
                else:
                    break
            YYYY += 1
        DOY = 1
        while DateTime >= 86400:
            DateTime -= 86400
            DOY += 1
        HH = 0
        while DateTime >= 3600:
            DateTime -= 3600
            HH += 1
        MM = 0
        while DateTime >= 60:
            DateTime -= 60
            MM += 1
        SS = DateTime
        MMM, DD = dt2Timeydoy2md(YYYY, DOY)
    else:
        DateTime = DateTime.strip().upper()
# The caller will have to decide if these returns are OK or not.
        if len(DateTime) == 0:
            if OutFormat -1:
                if Verify == False:
                    return 0.0
                else:
                    return (0, 0.0)
            elif OutFormat == 0:
                if Verify == False:
                    return 0, 0, 0, 0, 0, 0, 0.0
                else:
                    return (0, 0, 0, 0, 0, 0, 0, 0.0)
            elif InFormat == 5:
                if Verify == False:
                    return "00:00:00:00"
                else:
                    return (0, "00:00:00:00")
            else:
                if Verify == False:
                    return ""
                else:
                    return (0, "")
# The overall goal of the decode will be to get the passed string time into
# YYYY, MMM, DD, DOY, HH, MM integers and SS.sss float values then proceed to
# the encoding section ready for anything.
# These will try and figure out what the date is between the usual formats.
# Checks first to see if the date and time are together (like with a :) or if
# there is a space between them.
        if InFormat == 0:
            Parts = DateTime.split()
            if len(Parts) == 1:
# YYYY:DOY:... - 71:2 will pass.
                if DateTime.find(":") != -1:
                    Parts = DateTime.split(":")
# There has to be something that looks like YYYY:DOY.
                    if len(Parts) >= 2:
                        InFormat = 11
# YYYY-MM-DD:HH:...
# If there was only one thing and there are dashes then it could be Y-M-D or
# Y-M-D:H:M:S. Either way there must be 3 parts.
                elif DateTime.find("-") != -1:
                    Parts = DateTime.split("-")
                    if len(Parts) == 3:
                        InFormat = 21
# YYYYMMMDD:HH:... - 68APR3 will pass.
                elif (DateTime.find("A") != -1 or DateTime.find("E") != -1 or \
                        DateTime.find("O") != -1 or DateTime.find("U") != -1):
                    InFormat = 31
# YYYYDOYHHMMSS - Date/time must be exactly like this.
                elif len(DateTime) == 13:
                    if rtnPattern(DateTime) == "0000000000000":
                        InFormat = 41
# YYYYMMDDHHMMSS - Date/time must be exactly like this.
                elif len(DateTime) == 14:
                    if rtnPattern(DateTime) == "00000000000000":
                        InFormat = 51
# (There is no 1974JAN23235959 that I know of, but the elif for it would be
# here. ->
# There were two parts.
            else:
                Date = Parts[0]
                Time = Parts[1]
# YYYY:DOY HH:MM...
                if Date.find(":") != -1:
# Must have at least YYYY:DOY.
                    Parts = Date.split(":")
                    if len(Parts) >= 2:
                        InFormat = 12
# May be YYYY-MM-DD HH:MM...
                elif Date.find("-") != -1:
                    Parts = Date.split("-")
                    if len(Parts) == 3:
                        InFormat = 22
# YYYYMMMDD - 68APR3 will pass.
                elif (Date.find("A") != -1 or Date.find("E") != -1 or \
                    Date.find("O") != -1 or Date.find("U") != -1):
                        InFormat = 32
# If it is still 0 then something is wrong.
            if InFormat == 0:
                if Verify == False:
                    return ""
                else:
                    return (1, "RW", "Bad date/time(%d): '%s'"%(InFormat, \
                            DateTime), 2, "")
# These can be fed from the Format 0 stuff above, or called directly if the
# caller knows what DateTime is.
        if InFormat < 20:
# YYYY:DOY:HH:MM:SS.sss
# Sometimes this comes as  YYYY:DOY:HH:MM:SS:sss. We'll look for that here.
# (It's a Reftek thing.)
            if InFormat == 11:
                DT = DateTime.split(":")
                DT += (5-len(DT))*["0"]
                if len(DT) == 6:
                    DT[4] = "%06.3f"%(intt(DT[4])+intt(DT[5])/1000.0)
                    DT = DT[:-1]
# YYYY:DOY HH:MM:SS.sss
            elif InFormat == 12:
                Parts = DateTime.split()
                Date = Parts[0].split(":")
                Date += (2-len(Date))*["0"]
                Time = Parts[1].split(":")
                Time += (3-len(Time))*["0"]
                DT = Date+Time
            else:
                if Verify == False:
                    return ""
                else:
                    return (1, "MW", "dt2Time: Unknown InFormat code (%d)."% \
                            InFormat, 3, "")
# Two-digit years shouldn't happen a lot, so this is kinda inefficient.
            if DT[0] < "100":
                YYYY = intt(Date[0])
                if YYYY < 70:
                    YYYY += 2000
                else:
                    YYYY += 1900
                DT[0] = str(YYYY)
# After we have all of the parts then do the check if the caller wants.
            if Verify == True:
                Ret = dt2TimeVerify("ydhms", DT)
                if Ret[0] != 0:
                    return Ret
# I'm using intt() and floatt() throughout just because it's safer than the
# built-in functions.
# This trick makes it so the Epoch for a year only has to be calculated once
# during a program's run.
            YYYY = intt(DT[0])
            DOY = intt(DT[1])
            MMM, DD = dt2Timeydoy2md(YYYY, DOY)
            HH = intt(DT[2])
            MM = intt(DT[3])
            SS = floatt(DT[4])
        elif InFormat < 30:
# YYYY-MM-DD:HH:MM:SS.sss
            if InFormat == 21:
                Parts = DateTime.split(":", 1)
                Date = Parts[0].split("-")
                Date += (3-len(Date))*["0"]
# Just the date must have been supplied.
                if len(Parts) == 1:
                    Time = ["0", "0", "0"]
                else:
                    Time = Parts[1].split(":")
                    Time += (3-len(Time))*["0"]
                DT = Date+Time
# YYYY-MM-DD HH:MM:SS.sss
            elif InFormat == 22:
                Parts = DateTime.split()
                Date = Parts[0].split("-")
                Date += (3-len(Date))*["0"]
                Time = Parts[1].split(":")
                Time += (3-len(Time))*["0"]
                DT = Date+Time
# If parts of 23 are missing we will fill them in with Jan, 1st, or 00:00:00.
# If parts of 24 are missing we will format to the missing item then stop and
# return what we have.
            elif InFormat == 23 or InFormat == 24:
# The /DOY may or may not be there.
                if DateTime.find("/") == -1:
                    Parts = DateTime.split()
                    Date = Parts[0].split("-")
                    if InFormat == 23:
                        Date += (3-len(Date))*["1"]
                    else:
# The -1's will stand in fro the missing items. OutFormat=24 will figure it
# out from there.
                        Date += (3-len(Date))*["-1"]
                    if len(Parts) == 2:
                        Time = Parts[1].split(":")
                        if InFormat == 23:
                            Time += (3-len(Time))*["0"]
                        else:
                            Time += (3-len(Time))*["-1"]
                    else:
                        if InFormat == 23:
                            Time = ["0", "0", "0"]
                        else:
                            Time = ["-1", "-1", "-1"]
# Has a /. We'll only use the YYYY-MM-DD part and assume nothing about the DOY
# part.
                else:
                    Parts = DateTime.split()
                    Date = Parts[0].split("-")
                    if InFormat == 23:
                        Date += (3-len(Date))*["0"]
                    elif InFormat == 24:
                        Date += (3-len(Date))*["-1"]
                    Date[2] = Date[2].split("/")[0]
                    if len(Parts) == 2:
                        Time = Parts[1].split(":")
                        if InFormat == 23:
                            Time += (3-len(Time))*["0"]
                        else:
                            Time += (3-len(Time))*["-1"]
                    else:
                        if InFormat == 23:
                            Time = ["0", "0", "0"]
                        else:
                            Time = ["1-", "-1", "-1"]
                DT = Date+Time
            else:
                if Verify == False:
                    return ""
                else:
                    return (1, "MW", "dt2Time: Unknown InFormat code (%d)."% \
                            InFormat, 3, "")
            if DT[0] < "100":
                YYYY = intt(DT[0])
                if YYYY < 70:
                    YYYY += 2000
                else:
                    YYYY += 1900
                DT[0] = str(YYYY)
            if Verify == True:
                if InFormat != 24:
                    Ret = dt2TimeVerify("ymdhms", DT)
                else:
                    Ret = dt2TimeVerify("xymdhms", DT)
                if Ret[0] != 0:
                    return Ret
            YYYY = intt(DT[0])
            MMM = intt(DT[1])
            DD = intt(DT[2])
# This will get done in OutFormat=24.
            if InFormat != 24:
                DOY = dt2Timeymd2doy(YYYY, MMM, DD)
            else:
                DOY = -1
            HH = intt(DT[3])
            MM = intt(DT[4])
            SS = floatt(DT[5])
        elif InFormat < 40:
# YYYYMMMDD:HH:MM:SS.sss
            if InFormat == 31:
                Parts = DateTime.split(":", 1)
                Date = Parts[0]
                if len(Parts) == 1:
                    Time = ["0", "0", "0"]
                else:
                    Time = Parts[1].split(":")
                    Time += (3-len(Time))*["0"]                
# YYYYMMMDD HH:MM:SS.sss
            elif InFormat == 32:
                Parts = DateTime.split()
                Date = Parts[0]
                Time = Parts[1].split(":")
                Time += (3-len(Time))*["0"]
            else:
                if Verify == False:
                    return ""
                else:
                    return (1, "MW", "dt2Time: Unknown InFormat code (%d)."% \
                            InFormat, 3, "")
# Date is still "YYYYMMMDD", so just make place holders.
            DT = ["0", "0", "0"]+Time
            YYYY = intt(Date)
            if YYYY < 100:
                if YYYY < 70:
                    YYYY += 2000
                else:
                    YYYY += 1900
            MMM = 0
            DD = 0
            M = 1
            for Month in PROG_CALMONS[1:]:
                try:
                    i = Date.index(Month)
                    MMM = M
                    DD = intt(Date[i+3:])
                    break
                except:
                    pass
                M += 1
            if Verify == True:
# DT values need to be strings for the dt2TimeVerify() intt() call. It's
# assumed the values would come from split()'ing something, so they would
# normally be strings to begin with.
                DT[0] = str(YYYY)
                DT[1] = str(MMM)
                DT[2] = str(DD)
                Ret = dt2TimeVerify("ymdhms", DT)
                if Ret[0] != 0:
                    return Ret
            DOY = dt2Timeymd2doy(YYYY, MMM, DD)
            HH = intt(Time[0])
            MM = intt(Time[1])
            SS = intt(Time[2])
        elif InFormat < 50:
# YYYYDOYHHMMSS
            if InFormat == 41:
                if DateTime.isdigit() == False:
                    if Verify == False:
                        return ""
                    else:
                        return (1, "RW", "Non-digits in value.", 2)
                YYYY = intt(DateTime[:4])
                DOY = intt(DateTime[4:7])
                MMM, DD = dt2Timeydoy2md(YYYY, DOY)
                HH = intt(DateTime[7:9])
                MM = intt(DateTime[9:11])
                SS = floatt(DateTime[11:])
            else:
                if Verify == False:
                    return ""
                else:
                    return (1, "MW", "dt2Time: Unknown InFormat code (%d)."% \
                            InFormat, 3, "")
        elif InFormat < 60:
# YYYYMMDDHHMMSS
            if InFormat == 51:
                if DateTime.isdigit() == False:
                    if Verify == False:
                        return ""
                    else:
                        return (1, "RW", "Non-digits in value.", 2)
                YYYY = intt(DateTime[:4])
                MMM = intt(DateTime[4:6])
                DD = intt(DateTime[6:8])
                DOY = dt2Timeymd2doy(YYYY, MMM, DD)
                HH = intt(DateTime[8:10])
                MM = intt(DateTime[10:12])
                SS = floatt(DateTime[12:])
            else:
                if Verify == False:
                    return ""
                else:
                    return (1, "MW", "dt2Time: Unknown InFormat code (%d)."% \
                            InFormat, 3, "")
# If the caller just wants to work with the seconds we'll split it up and
# return the number of seconds into the day. In this case the OutFormat value
# will not be used.
        elif InFormat == 100:
            Parts = DateTime.split(":")
            Parts += (3-len(Parts))*["0"]
            if Verify == True:
                Ret = dt2TimeVerify("hms", Parts)
                if Ret[0] != 0:
                    return Ret
            if Verify == False:
                return (intt(Parts[0])*3600)+(intt(Parts[1])*60)+ \
                        float(Parts[2])
            else:
                return (0, (intt(Parts[0])*3600)+(intt(Parts[1])*60)+ \
                        float(Parts[2]))
# Now that we have all of the parts do what the caller wants and return the
# result.
# Return the Epoch.
    if OutFormat == -1:
        try:
            Epoch = Y2EPOCH[YYYY]
        except KeyError:
            Epoch = 0.0
            for YYY in xrange(1970, YYYY):
                if YYY%4 != 0:
                    Epoch += 31536000.0
                elif YYY%100 != 0 or YYY%400 == 0:
                    Epoch += 31622400.0
                else:
                    Epoch += 31536000.0
            Y2EPOCH[YYYY] = Epoch
        Epoch += ((DOY-1)*86400.0)+(HH*3600.0)+(MM*60.0)+SS
        if Verify == False:
            return Epoch
        else:
            return (0, Epoch)
    elif OutFormat == 0:
        if Verify == False:
            return YYYY, MMM, DD, DOY, HH, MM, SS
        else:
            return (0, YYYY, MMM, DD, DOY, HH, MM, SS)
    elif OutFormat == 1:
        Format = OPTDateFormatRVar.get()
        if Format == "YYYY:DOY":
            OutFormat = 11
        elif Format == "YYYY-MM-DD":
            OutFormat = 22
        elif Format == "YYYYMMMDD":
            OutFormat = 32
# Usually used for troubleshooting.
        elif Format == "":
            try:
                Epoch = Y2EPOCH[YYYY]
            except KeyError:
                for YYY in xrange(1970, YYYY):
                    if YYY%4 != 0:
                        Epoch += 31536000.0
                    elif YYY%100 != 0 or YYY%400 == 0:
                        Epoch += 31622400.0
                    else:
                        Epoch += 31536000.0
                Y2EPOCH[YYYY] = Epoch
            Epoch += ((DOY-1)*86400.0)+(HH*3600.0)+(MM*60.0)+SS
            if Verify == False:
                return Epoch
            else:
                return (0, Epoch)
# This is the easiest way I can think of to keep an SS of 59.9999 from being
# rounded and formatted to 60.000. Some stuff at some point may slip into the
# microsecond realm. Then this whole library of functions may have to be
# changed.
    if SS%1 > .999:
        SS = int(SS)+.999
# These OutFormat values are the same as InFormat values, plus others.
# YYYY:DOY:HH:MM:SS.sss
    if OutFormat == 11:
        if Verify == False:
            return "%d:%03d:%02d:%02d:%06.3f"%(YYYY, DOY, HH, MM, SS)
        else:
            return (0, "%d:%03d:%02d:%02d:%06.3f"%(YYYY, DOY, HH, MM, SS))
# YYYY:DOY HH:MM:SS.sss
    elif OutFormat == 12:
        if Verify == False:
            return "%d:%03d %02d:%02d:%06.3f"%(YYYY, DOY, HH, MM, SS)
        else:
            return (0, "%d:%03d %02d:%02d:%06.3f"%(YYYY, DOY, HH, MM, SS))
# YYYY:DOY - just because it's popular (for LOGPEEK) and it saves having the
# caller always doing  .split()[0]
    elif OutFormat == 13:
        if Verify == False:
            return "%d:%03d"%(YYYY, DOY)
        else:
            return (0, "%d:%03d"%(YYYY, DOY))
# YYYY:DOY:HH:MM:SS - just because it's really popular in POCUS and other
# programs.
    elif OutFormat == 14:
        if Verify == False:
            return "%d:%03d:%02d:%02d:%02d"%(YYYY, DOY, HH, MM, int(SS))
        else:
            return (0, "%d:%03d:%02d:%02d:%02d"%(YYYY, DOY, HH, MM, int(SS)))
# YYYY-MM-DD:HH:MM:SS.sss
    elif OutFormat == 21:
        if Verify == False:
            return "%d-%02d-%02d:%02d:%02d:%06.3f"%(YYYY, MMM, DD, HH, MM, SS)
        else:
            return (0, "%d-%02d-%02d:%02d:%02d:%06.3f"%(YYYY, MMM, DD, HH, \
                    MM, SS))
# YYYY-MM-DD HH:MM:SS.sss
    elif OutFormat == 22:
        if Verify == False:
            return "%d-%02d-%02d %02d:%02d:%06.3f"%(YYYY, MMM, DD, HH, MM, SS)
        else:
            return (0, "%d-%02d-%02d %02d:%02d:%06.3f"%(YYYY, MMM, DD, HH, \
                    MM, SS))
# YYYY-MM-DD/DOY HH:MM:SS.sss
    elif OutFormat == 23:
        if Verify == False:
            return "%d-%02d-%02d/%03d %02d:%02d:%06.3f"%(YYYY, MMM, DD, DOY, \
                    HH, MM, SS)
        else:
            return (0, "%d-%02d-%02d/%03d %02d:%02d:%06.3f"%(YYYY, MMM, DD, \
                    DOY, HH, MM, SS))
# Some portion of YYYY-MM-DD HH:MM:SS. Returns integer seconds.
# In that this is a human-entered thing (programs like PIS don't store partial
# date/times) we'll return whatever was entered without the /DOY, since the
# next step would be to do something like look it up in a database.
    elif OutFormat == 24:
        DateTime = "%d"%YYYY
        if MMM != -1:
            DateTime += "-%02d"%MMM
        else:
# Return what we have if this item was not provided, same on down.
            if Verify == False:
                return DateTime
            else:
                return (0, DateTime)
        if DD != -1:
            DateTime += "-%02d"%DD
        else:
            if Verify == False:
                return DateTime
            else:
                return (0, DateTime)
        if HH != -1:
            DateTime += " %02d"%HH
        else:
            if Verify == False:
                return DateTime
            else:
                return (0, DateTime)
        if MM != "-1":
            DateTime += ":%02d"%MM
        else:
            if Verify == False:
                return DateTime
            else:
                return (0, DateTime)
# Returns integer second since the caller has no idea what is coming back.
        if SS != "-1":
            DateTime += ":%02d"%SS
        if Verify == False:
            return DateTime
        else:
            return (0, DateTime)
# YYYYMMMDD:HH:MM:SS.sss
    elif OutFormat == 31:
        if Verify == False:
            return "%d%s%02d:%02d:%02d:%06.3f"%(YYYY, PROG_CALMONS[MMM], DD, \
                    HH, MM, SS)
        else:
            return (0, "%d%s%02d:%02d:%02d:%06.3f"%(YYYY, PROG_CALMONS[MMM], \
                    DD, HH, MM, SS))
# YYYYMMMDD HH:MM:SS.sss
    elif OutFormat == 32:
        if Verify == False:
            return "%d%s%02d %02d:%02d:%06.3f"%(YYYY, PROG_CALMONS[MMM], DD, \
                    HH, MM, SS)
        else:
            return (0, "%d%s%02d %02d:%02d:%06.3f"%(YYYY, PROG_CALMONS[MMM], \
                    DD, HH, MM, SS))
# YYYYDOYHHMMSS.sss
    elif OutFormat == 41:
        if Verify == False:
            return "%d%03d%02d%02d%06.3f"%(YYYY, DOY, HH, MM, SS)
        else:
            return (0, "%d%03d%02d%02d%06.3f"%(YYYY, DOY, HH, MM, SS))
# YYYYMMDDHHMMSS.sss
    elif OutFormat == 51:
        if Verify == False:
            return "%d%02d%02d%02d%02d%06.3f"%(YYYY, MMM, DD, HH, MM, SS)
        else:
            return (0, "%d%02d%02d%02d%02d%06.3f"%(YYYY, MMM, DD, HH, MM, SS))
# Returns what ever OPTDateFormatRVar is set to.
# 80 is dt, 81 is d and 82 is t.
    elif OutFormat == 80 or OutFormat == 81 or OutFormat == 82:
        if OPTDateFormatRVar.get() == "YYYY:DOY":
            if OutFormat == 80:
                if Verify == False:
                    return "%d:%03d:%02d:%02d:%06.3f"%(YYYY, DOY, HH, MM, SS)
                else:
                    return (0, "%d:%03d:%02d:%02d:%06.3f"%(YYYY, DOY, HH, MM, \
                            SS))
            elif OutFormat == 81:
                if Verify == False:
                    return "%d:%03d"%(YYYY, DOY)
                else:
                    return (0, "%d:%03d"%(YYYY, DOY))
            elif OutFormat == 82:
                if Verify == False:
                    return "%02d:%02d:%06.3f"%(HH, MM, SS)
                else:
                    return (0, "%02d:%02d:%06.3f"%(HH, MM, SS))
        elif OPTDateFormatRVar.get() == "YYYY-MM-DD":
            if OutFormat == 80:
                if Verify == False:
                    return "%d-%02d-%02d %02d:%02d:%06.3f"%(YYYY, MMM, DD, \
                            HH, MM, SS)
                else:
                    return (0, "%d-%02d-%02d %02d:%02d:%06.3f"%(YYYY, MMM, \
                            DD, HH, MM, SS))
            elif OutFormat == 81:
                if Verify == False:
                    return "%d-%02d-%02d"%(YYYY, MMM, DD)
                else:
                    return (0, "%d-%02d-%02d"%(YYYY, MMM, DD))
            elif OutFormat == 82:
                if Verify == False:
                    return "%02d:%02d:%06.3f"%(HH, MM, SS)
                else:
                    return (0, "%02d:%02d:%06.3f"%(HH, MM, SS))
        elif OPTDateFormatRVar.get() == "YYYYMMMDD":
            if OutFormat == 80:
                if Verify == False:
                    return "%d%s%02d %02d:%02d:%06.3f"%(YYYY, \
                            PROG_CALMONS[MMM], DD, HH, MM, SS)
                else:
                    return (0, "%d%s%02d %02d:%02d:%06.3f"%(YYYY, \
                            PROG_CALMONS[MMM], DD, HH, MM, SS))
            elif OutFormat == 81:
                if Verify == False:
                    return "%d%s%02d"%(YYYY, PROG_CALMONS[MMM], DD)
                else:
                    return (0, "%d%s%02d"%(YYYY, PROG_CALMONS[MMM], DD))
            elif OutFormat == 82:
                if Verify == False:
                    return "%02d:%02d:%06.3f"%(HH, MM, SS)
                else:
                    return (0, "%02d:%02d:%06.3f"%(HH, MM, SS))
        elif OPTDateFormatRVar.get() == "":
            if Verify == False:
                return str(DateTime)
            else:
                return (0, str(DateTime))
    else:
        if Verify == False:
            return ""
        else:
            return (1, "MW", "dt2Time: Unknown OutFormat code (%d)."% \
                    OutFormat, 3, "")
################################
# BEGIN: dt2Timedhms2Secs(InStr)
# FUNC:dt2Timedhms2Secs():2008.013
#   Returns the number of seconds in strings like 1h30m.
def dt2Timedhms2Secs(InStr):
    InStr = InStr.replace(" ", "").lower()
    if InStr == "":
        return 0
    Chars = list(InStr)
    Value = 0
    SubValue = ""
    for Char in Chars:
        if Char.isdigit():
            SubValue += Char
        elif Char == "s":
            Value += intt(SubValue)
            SubValue = ""
        elif Char == "m":
            Value += intt(SubValue)*60
            SubValue = ""
        elif Char == "h":
            Value += intt(SubValue)*3600
            SubValue = ""
        elif Char == "d":
            Value += intt(SubValue)*86400
            SubValue = ""
# Must have just been passed a number with no s m h or d or 1h30 which will be
# treated as 1 hour, 30 seconds.
    if SubValue != "":
        Value += intt(SubValue)
    return Value
######################################
# BEGIN: dt2TimeDT(InFormat, DateTime)
# FUNC:dt2TimeDT():2013.294
#   This is for the one-off time conversion items that have been needed here
#   and there for specific items. Input is some string of date and/or time.
#   Some of these can be done with dt2Time(), but these are more for when the
#   code knows exactly what it has and exactly what it needs. It's program
#   dependent and maybe useful to others.
#   InFormat = 1 = [dd]hhmmss or even blank to [DD:]HH:MM:SS
#                  Replaces dhms2DHMS().
#              2 = YYYY:DOY:HH:MM:SS to ISO8601 time YYYY-MM-DDTHH:MM:SSZ.
#                  No time zone conversion is done (or any error checking) so
#                  you need to make sure the passed time is really Zulu or this
#                  will return a lie.
#                  Replaces YDHMS28601().
#              3 = The opposite of above.
#                  Replaces iso86012YDHMS().
#              4 = Adds /DOY to a passed date/time that can be just the date,
#                  but that must be a YYYY-MM-DD format. Date and time must be
#                  separated by a space. It's the only date format that I've
#                  ever wanted to add the DOY to. Returns the fixed up
#                  date/time. Does NO error checking, and, as you can see, the
#                  split() and map() will choke causing an ebarrassing crash if
#                  the date is not the right format. You have been warned.
#                  Replaces addDDD().
#              5 = Anti-InFormat 4. Is OK if /DOY is not there.
#                  Replaces remDDD().
#              6 = yyydoyhhmmss... to YYYY:DOY:HH:MM...
#                  Replaces ydhmst2YDHMST().
#              7 = YYYY:DOY:HH:MM:SS -> YYYY-MM-DD:HH:MM:SS.
#                  Replaces ydhms2ymdhmsDash().
#              8 = YYYYMMDDHHMMSS to YYYY-MM-DD HH:MM:SS
def dt2TimeDT(InFormat, DateTime):
    if InFormat == 1:
# Check the length before the .strip(). DateTime may be just blanks, but we'll
# use the length to determine what to return.
        Len = len(DateTime)
        DateTime = DateTime.strip()
        if DateTime == "":
            return "00:00:00:00"
        if Len == 6:
            return "%s:%s:%s"%(DateTime[:2], DateTime[2:4], DateTime[4:6])
        else:
            return "%s:%s:%s:%s"%(DateTime[:2], DateTime[2:4], DateTime[4:6], \
                    DateTime[6:8])
    elif InFormat == 2:
        Parts = DateTime.split(":")
        if len(Parts) != 5:
            return ""
        MM, DD, = dt2Timeydoy2md(intt(Parts[0]), intt(Parts[1]))
        return "%s-%02d-%02dT%s:%s:%sZ"%(Parts[0], MM, DD, Parts[2], \
            Parts[3], Parts[4])
    elif InFormat == 3:
        Parts = DateTime.split("T")
        if len(Parts) != 2:
            return ""
# Who knows what may be wrong with the passed time.
        try:
            YYYY, MMM, DD = map(intt, Parts[0].split("-"))
            DOY = dt2Timeymd2doy(YYYY, MMM, DD)
            HH, MM, SS = map(intt, Parts[1].split(":"))
        except:
            return ""
        return "%d:%03d:%02d:%02d:%02d"%(YYYY, DOY, HH, MM, SS)
    elif InFormat == 4:
        Parts = DateTime.split()
        if len(Parts) == 0:
            return ""
        YYYY, MMM, DD = map(int, Parts[0].split("-"))
        DOY = dt2Timeymd2doy(YYYY, MMM, DD)
        if len(Parts) == 1:
            return "%s/%03d"%(Parts[0], DOY)
        else:
            return "%s/%03d %s"%(Parts[0], DOY, Parts[1])
    elif InFormat == 5:
        Parts = DateTime.split()
        if len(Parts) == 0:
            return ""
# A little bit of protection.
        try:
            i = Parts[0].index("/")
            Parts[0] = Parts[0][:i]
        except ValueError:
            pass
        if len(Parts) == 1:
            return Parts[0]
        else:
            return "%s %s"%(Parts[0], Parts[1])
# yyyydoyhhmmssttt or yyyydoyhhmmss.
    elif InFormat == 6:
        Len = len(DateTime)
        DateTime = DateTime.strip()
# yyyydoyhhmm
        if Len == 12:
            if DateTime == "":
                return "0000:000:00:00"
            return "%s:%s:%s:%s"%(DateTime[:4], DateTime[4:7], DateTime[7:9], \
                    DateTime[9:11])
# yyyydoyhhmmss  All of the fields that may contain this are 14 bytes long
# with a trailing space which got removed above (it was that way in LOGPEEK
# anyways).
        elif Len == 14:
            if DateTime == "":
                return "0000:000:00:00:00"
            return "%s:%s:%s:%s:%s"%(DateTime[:4], DateTime[4:7], \
                    DateTime[7:9], DateTime[9:11], DateTime[11:13])
# yyyydoyhhmmssttt
        elif Len == 16:
            if DateTime == "":
                return "0000:000:00:00:00:000"
            return "%s:%s:%s:%s:%s:%s"%(DateTime[:4], DateTime[4:7], \
                    DateTime[7:9], DateTime[9:11], DateTime[11:13], \
                    DateTime[13:])
        return ""
    elif InFormat == 7:
        Parts = DateTime.split(":")
        YYYY = intt(Parts[0])
        DOY = intt(Parts[1])
        MMM, DD = dt2Timeydoy2md(YYYY, DOY)
        return "%d-%02d-%02d:%s:%s:%s"%(YYYY, MMM, DD, Parts[2], Parts[3], \
                Parts[4])
# YYYYMMDDHHMMSS to YYYY-MM-DD HH:MM:SS
    elif InFormat == 8:
        if len(DateTime) == 14:
            return "%s-%s-%s %s:%s:%s"%(DateTime[0:4], DateTime[4:6], \
                    DateTime[6:8], DateTime[8:10], DateTime[10:12], \
                    DateTime[12:14])
        return ""
######################################################################
# BEGIN: dt2TimeMath(DeltaDD, DeltaSS, YYYY, MMM, DD, DOY, HH, MM, SS)
# LIB:dt2TimeMath():2013.039
#   Adds or subtracts (depending on the sign of DeltaDD/DeltaSS) the requested
#   amount of time to/from the passed date.  Returns a tuple with the results:
#           (YYYY, MMM, DD, DOY, HH, MM, SS)
#   Pass -1 or 0 for MMM/DD, or DOY depending on which is to be used. If MMM/DD
#   are >=0 then MMM, DD, and DOY will be filled in on return. If MMM/DD is -1
#   then just DOY will be used/returned. If MMM/DD are 0 then DOY will be used
#   but MMM and DD will also be returned.
#   SS will be int or float depending on what was passed.
def dt2TimeMath(DeltaDD, DeltaSS, YYYY, MMM, DD, DOY, HH, MM, SS):
    DeltaDD = int(DeltaDD)
    DeltaSS = int(DeltaSS)
    if YYYY < 1000:
        if YYYY < 70:
            YYYY += 2000
        else:
            YYYY += 1900
# Work in DOY.
    if MMM > 0:
        DOY = dt2Timeymd2doy(YYYY, MMM, DD)
    if DeltaDD != 0:
        if DeltaDD > 0:
            Forward = 1
        else:
            Forward = 0
        while 1:
# Speed limit the change to keep things simpler.
            if DeltaDD < -365 or DeltaDD > 365:
                if Forward == 1:
                    DOY += 365
                    DeltaDD -= 365
                else:
                    DOY -= 365
                    DeltaDD += 365
            else:
                DOY += DeltaDD
                DeltaDD = 0
            if YYYY%4 != 0:
                Leap = 0
            elif YYYY%100 != 0 or YYYY%400 == 0:
                Leap = 1
            else:
                Leap = 0
            if DOY < 1 or DOY > 365+Leap:
                if Forward == 1:
                    DOY -= 365+Leap
                    YYYY += 1
                else:
                    YYYY -= 1
                    if YYYY%4 != 0:
                        Leap = 0
                    elif YYYY%100 != 0 or YYYY%400 == 0:
                        Leap = 1
                    else:
                        Leap = 0
                    DOY += 365+Leap
            if DeltaDD == 0:
                break
    if DeltaSS != 0:
        if DeltaSS > 0:
            Forward = 1
        else:
            Forward = 0
        while 1:
# Again, speed limit just to keep the code reasonable.
            if DeltaSS < -59 or DeltaSS > 59:
                if Forward == 1:
                    SS += 59
                    DeltaSS -= 59
                else:
                    SS -= 59
                    DeltaSS += 59
            else:
                SS += DeltaSS
                DeltaSS = 0
            if SS < 0 or SS > 59:
                if Forward == 1:
                    SS -= 60
                    MM += 1
                    if MM > 59:
                        MM = 0
                        HH += 1
                        if HH > 23:
                            HH = 0
                            DOY += 1
                            if DOY > 365:
                                if YYYY%4 != 0:
                                    Leap = 0
                                elif YYYY%100 != 0 or YYYY%400 == 0:
                                    Leap = 1
                                else:
                                    Leap = 0
                                if DOY > 365+Leap:
                                    YYYY += 1
                                    DOY = 1
                else:
                    SS += 60
                    MM -= 1
                    if MM < 0:
                        MM = 59
                        HH -= 1
                        if HH < 0:
                            HH = 23
                            DOY -= 1
                            if DOY < 1:
                                YYYY -= 1
                                if YYYY%4 != 0:
                                    DOY = 365
                                elif YYYY%100 != 0 or YYYY%400 == 0:
                                    DOY = 366
                                else:
                                    DOY = 365
            if DeltaSS == 0:
                 break
    if MMM != -1:
        MMM, DD = dt2Timeydoy2md(YYYY, DOY)
    return (YYYY, MMM, DD, DOY, HH, MM, SS)
####################################
# BEGIN: dt2TimeVerify(Which, Parts)
# FUNC:dt2TimeVerify():2013.290
#   This could figure out what to check just by passing [Y,M,D,D,H,M,S], but
#   that means the splitters() in dt2Time would need to work much harder to
#   make sure all of the Parts were there, thus it needs a Which value.
def dt2TimeVerify(Which, Parts):
    if Which.startswith("ydhms"):
        YYYY = intt(Parts[0])
        MMM = -1
        DD = -1
        DOY = intt(Parts[1])
        HH = intt(Parts[2])
        MM = intt(Parts[3])
        SS = floatt(Parts[4])
    elif Which.startswith("ymdhms") or Which.startswith("xymdhms"):
        YYYY = intt(Parts[0])
        MMM = intt(Parts[1])
        DD = intt(Parts[2])
        DOY = -1
        HH = intt(Parts[3])
        MM = intt(Parts[4])
        SS = floatt(Parts[5])
    elif Which.startswith("hms"):
        YYYY = -1
        MMM = -1
        DD = -1
        DOY = -1
        HH = intt(Parts[0])
        MM = intt(Parts[1])
        SS = floatt(Parts[2])
    if YYYY != -1 and (YYYY < 1000 or YYYY > 9999):
        return (1, "RW", "Bad year value: %d"%YYYY, 2, "")
# Normally do the normal checking.
    if Which.startswith("x") == False:
        if MMM != -1 and (MMM < 1 or MMM > 12):
            return (1, "RW", "Bad month value: %d"%MMM, 2, "")
        if DD != -1:
            if DD < 1 or DD > 31:
                return (1, "RW", "Bad day value: %d"%DD, 2, "")
            if YYYY%4 != 0:
                if DD > PROG_MAXDPMNLY[MMM]:
                    return (1, "RW", "Too many days for month %d: %d"%(MMM, \
                            DD), 2, "")
            elif (YYYY%100 != 0 or YYYY%400 == 0) and MMM > 2:
                if DD > PROG_MAXDPMLY[MMM]:
                    return (1, "RW", "Too many days for month %d: %d"%(MMM, \
                            DD), 2, "")
            else:
                if DD > PROG_MAXDPMNLY[MMM]:
                    return (1, "RW", "Too many days for month %d: %d"%(MMM, \
                            DD), 2, "")
        if DOY != -1:
            if DOY < 1 or DOY > 366:
                return (1, "RW", "Bad day of year value: %d"%DOY, 2, "")
            if YYYY%4 != 0 and DOY > 365:
                return (1, "RW" "Too many days for non-leap year: %d"%DOY, \
                        2, "")
        if HH < 0 or HH >= 24:
            return (1, "RW", "Bad hour value: %d"%HH, 2, "")
        if MM < 0 or MM >= 60:
            return (1, "RW", "Bad minute value: %d"%MM, 2, "")
        if SS < 0 or SS >= 60:
            return (1, "RW", "Bad seconds value: %06.3f"%SS, 2, "")
# "x" checks.
# Here if Which starts with "x" then it is OK if month and day values are
# missing. This is for checking an entry like  2013-7  for example. If the
# portion of the date(/time) that was passed looks OK then (0,) will be
# returned. If it is something like  2013-13  then that will be bad.
    else:
# If the user entered just the year, then we are done, etc.
        if MMM != -1:
            if MMM < 1 or MMM > 12:
                return (1, "RW", "Bad month value: %d"%MMM, 2, "")
            if DD != -1:
                if DD < 1 or DD > 31:
                    return (1, "RW", "Bad day value: %d"%DD, 2, "")
                if YYYY%4 != 0:
                    if DD > PROG_MAXDPMNLY[MMM]:
                        return (1, "RW", "Too many days for month %d: %d"% \
                                (MMM, DD), 2, "")
                elif (YYYY%100 != 0 or YYYY%400 == 0) and MMM > 2:
                    if DD > PROG_MAXDPMLY[MMM]:
                        return (1, "RW", "Too many days for month %d: %d"% \
                                (MMM, DD), 2, "")
                else:
                    if DD > PROG_MAXDPMNLY[MMM]:
                        return (1, "RW", "Too many days for month %d: %d"% \
                                (MMM, DD), 2, "")
                if DOY != -1:
                    if DOY < 1 or DOY > 366:
                        return (1, "RW", "Bad day of year value: %d"%DOY, 2, \
                                "")
                    if YYYY%4 != 0 and DOY > 365:
                        return (1, "RW" \
                                "Too many days for non-leap year: %d"%DOY, \
                                2, "")
                if HH != -1:
                    if HH < 0 or HH >= 24:
                        return (1, "RW", "Bad hour value: %d"%HH, 2, "")
                    if MM != -1:
                        if MM < 0 or MM >= 60:
                            return (1, "RW", "Bad minute value: %d"%MM, 2, "")
# Checking these special values are usually from user input and are date/time
# values and not timing values, so the seconds part here will just be an int.
                        if SS != -1:
                            if SS < 0 or SS >= 60:
                                return (1, "RW", "Bad seconds value: %d"%SS, \
                                        2, "")
    return (0,)
##########################################
# BEGIN: dt2TimeydoyMath(Delta, YYYY, DOY)
# LIB:dt2TimeydoyMath():2013.036
#   Adds or subtracts the passed number of days (Delta) to the passed year and
#   day of year values. Returns YYYY and DOY.
#   Replaces ydoyMath().
def dt2TimeydoyMath(Delta, YYYY, DOY):
    if Delta == 0:
        return YYYY, DOY
    if Delta > 0:
        Forward = 1
    elif Delta < 0:
        Forward = 0
    while 1:
# Speed limit the change to keep things simpler.
        if Delta < -365 or Delta > 365:
            if Forward == 1:
                DOY += 365
                Delta -= 365
            else:
                DOY -= 365
                Delta += 365
        else:
            DOY += Delta
            Delta = 0
# This was isLeap(), but it's such a simple thing I'm not sure it was worth the
# function call, so it became this in all library functions.
        if YYYY%4 != 0:
            Leap = 0
        elif YYYY%100 != 0 or YYYY%400 == 0:
            Leap = 1
        else:
            Leap = 0
        if DOY < 1 or DOY > 365+Leap:
            if Forward == 1:
                DOY -= 365+Leap
                YYYY += 1
            else:
                YYYY -= 1
                if YYYY%4 != 0:
                    Leap = 0
                elif YYYY%100 != 0 or YYYY%400 == 0:
                    Leap = 1
                else:
                    Leap = 0
                DOY += 365+Leap
            break
        if Delta == 0:
            break
    return YYYY, DOY
##################################
# BEGIN: dt2Timeydoy2md(YYYY, DOY)
# FUNC:dt2Timeydoy2md():2013.030
#   Does no values checking, so make sure you stuff is in one sock before
#   coming here.
def dt2Timeydoy2md(YYYY, DOY):
    if DOY < 32:
        return 1, DOY
    elif DOY < 60:
        return 2, DOY-31
    if YYYY%4 != 0:
        Leap = 0
    elif YYYY%100 != 0 or YYYY%400 == 0:
        Leap = 1
    else:
        Leap = 0
# Check for this special day.
    if Leap == 1 and DOY == 60:
        return 2, 29
# The PROG_FDOM values for Mar-Dec are set up for non-leap years. If it is a
# leap year and the date is going to be Mar-Dec (it is if we have made it this
# far), subtract Leap from the day.
    DOY -= Leap
# We start through PROG_FDOM looking for dates in March.
    Month = 3
    for FDOM in PROG_FDOM[4:]:
# See if the DOY is less than the first day of next month.
        if DOY <= FDOM:
# Subtract the DOY for the month that we are in.
            return Month, DOY-PROG_FDOM[Month]
        Month += 1
# If anything goes wrong...
    return 0, 0
######################################
# BEGIN: dt2Timeymd2doy(YYYY, MMM, DD)
# FUNC:dt2Timeymd2doy():2013.030
def dt2Timeymd2doy(YYYY, MMM, DD):
    if YYYY%4 != 0:
        return (PROG_FDOM[MMM]+DD)
    elif (YYYY%100 != 0 or YYYY%400 == 0) and MMM > 2:
        return (PROG_FDOM[MMM]+DD+1)
    else:
        return (PROG_FDOM[MMM]+DD)
#################################################################
# BEGIN: dt2Timeymddhms(OutFormat, YYYY, MMM, DD, DOY, HH, MM, SS)
# FUNC:dt2Timeymddhms():2013.033
#   The general-purpose time handler for when the time is already split up into
#   it's parts.
#   Make MMM, DD -1 if passing DOY and DOY -1 if passing MMM, DD.
def dt2Timeymddhms(OutFormat, YYYY, MMM, DD, DOY, HH, MM, SS):
    global Y2EPOCH
# Returns a float Epoch is SS is a float, otherwise an int value.
    if OutFormat == -1:
        Epoch = 0
        if YYYY < 70:
            YYYY += 2000
        if YYYY < 100:
            YYYY += 1900
        try:
            Epoch = Y2EPOCH[YYYY]
        except KeyError:
            for YYY in xrange(1970, YYYY):
                if YYY%4 != 0:
                    Epoch += 31536000
                elif YYY%100 != 0 or YYY%400 == 0:
                    Epoch += 31622400
                else:
                    Epoch += 31536000
            Y2EPOCH[YYYY] = Epoch
        if DOY == -1:
            DOY = dt2Timeymd2doy(YYYY, MMM, DD)
        return Epoch+((DOY-1)*86400)+(HH*3600)+(MM*60)+SS
##########################################
# BEGIN: dt2Timeystr2Epoch(YYYY, DateTime)
# FUNC:dt2Timeystr2Epoch():2013.035
#   A slightly specialized time to Epoch converter where the input can be
#       YYYY, DOY:HH:MM:SS:TTT or
#       None,YYYY:DOY:HH:MM:SS:TTT or
#       None,YYYY-MM-DD:HH:MM:SS:TTT
#   DOY/DD and HH must be separated by a ':' -- no space.
#   The separator between SS and TTT may be : or .
#   Returns 0 if ANYTHING goes wrong.
#   Returns a float if the seconds were a float (SS:TTT or SS.ttt), or an int
#   if the time was incomplete or there was an error. The caller will just
#   have to do an int() if that is all they want.
#   Replaces str2Epoch(). Used a lot in RT130/72A data decoding.
def dt2Timeystr2Epoch(YYYY, DateTime):
    global Y2EPOCH
    Epoch = 0
    try:
        if DateTime.find("-") != -1:
            DT = DateTime.split(":", 1)
            Parts = map(float, DT[0].split("-"))
            Parts += map(float, DT[1].split(":"))
# There "must" have been a :TTT part.
            if len(Parts) == 6:
                Parts[5] += Parts[6]/1000.0
        else:
            Parts = map(float, DateTime.split(":"))
# There "must" have been a :TTT part.
            if len(Parts) == 7:
                Parts[5] += Parts[6]/1000.0
        if YYYY == None:
# Change this since it gets used in loops and dictionary keys and stuff. If
# the year is passed (below) then we're already covered.
            Parts[0] = int(Parts[0])
# Just in case someone generates 2-digit years.
            if Parts[0] < 100:
                if Parts[0] < 70:
                    Parts[0] += 2000
                else:
                    Parts[0] += 1900
        else:
# Check this just in case. The caller will just have to figure this one out.
            if YYYY < 1970:
                YYYY = 1970
            Parts = [YYYY, ]+Parts
        Parts += (5-len(Parts))*[0]
# This makes each year's Epoch get calculated only once.
        try:
            Epoch = Y2EPOCH[Parts[0]]
        except KeyError:
            for YYY in xrange(1970, Parts[0]):
                if YYY%4 != 0:
                    Epoch += 31536000
                elif YYY%100 != 0 or YYY%400 == 0:
                    Epoch += 31622400
                else:
                    Epoch += 31536000
            Y2EPOCH[Parts[0]] = Epoch
# This goes along with forcing YYYY to 1970 if things are bad.
        if Parts[1] < 1:
            Parts[1] = 1
        Epoch += ((int(Parts[1])-1)*86400)+(int(Parts[2])*3600)+ \
                (int(Parts[3])*60)+Parts[4]
    except ValueError:
        Epoch = 0
    return Epoch
# END: dt2Time




###############################
# BEGIN: fileSelected(e = None)
# FUNC:fileSelected():2013.171
#   Puts together the filespec(s) of the file(s) selected by the user and
#   handles the higher-level functions to get it/them processed and the data
#   into QPData and it's friends.
def fileSelected(e = None):
    global QPEarliestData
    global QPLatestData
    global QPUserChannels
    global QPFilesProcessed
    Root.focus_set()
    setMsg("MF", "", "")
    DataDir = PROGDataDirVar.get()
# Just in case.
    if DataDir.endswith(sep) == False:
        DataDir += sep
        PROGDataDirVar.set(DataDir)
# Loop through the selected file(s) in the Listbox.
    Sel = MFFiles.curselection()
    if len(Sel) == 0:
        setMsg("MF", "RW", \
                "No data source files/folders have been selected.", 2)
        return
# Do this up here, because it can take a while for the TPS plot to clear.
    progControl("go")
    plotMFClear()
    setMsg("INFO", "", "")
    formLOGClear()
    formQPERRClear()
    formTPSClear(True)
# Check out the dates that the user may have entered as limits for reading.
# Use changeDateFormat() in case the user put in dates not matching the
# current format and since it will return detailed error messages if anything
# is wrong.
    if changeDateFormat("MF") == False:
        progControl("stopped")
        return
    Date = FromDateVar.get()
    if Date != "":
        FromEpoch = dt2Time(0, -1, Date+" 00:00:00")
    else:
        FromEpoch = 0.0
    Date = ToDateVar.get()
    if Date != "":
        ToEpoch = dt2Time(0, -1, Date+" 24:00:00")
    else:
        ToEpoch = float(maxint)
    if FromEpoch > ToEpoch:
        setMsg("MF", "RW", \
                "The From date field value is after the To value.", 2)
        progControl("stopped")
        return
# If this is not "" there will be filtering.
    PROGStaIDFilterVar.set(PROGStaIDFilterVar.get().upper().strip())
    StaIDFilter = PROGStaIDFilterVar.get()
# Check out The Gap.
    if plotMFMindTheGap() == False:
        progControl("stopped")
        return
# Either they get it right, or they turn off the checkbutton.
    if OPTPlotTPSCVar.get() == 1:
        Ret = formTPSChkChans()
        if Ret[0] != 0:
            setMsg("MF", Ret)
            progControl("stopped")
            return
# I suppose there could be a "msg" function in plotMF() to do these messages,
# but since the main plot of the program is the main point of the program we'll
# just do it directly.
    setMsg("MF", "CB", "Working...")
    formTPSMsg("CB", "Working...")
    formLOGMsg("CB", "Working...")
    formQPERRMsg("CB", "Working...")
    clearQPGlobals()
    GapsDetect = OPTGapsDetectCVar.get()
# Clean up and get the list of selected channels to display.
    Ret = setQPUserChannels("plot")
    if Ret[0] != 0:
        setMsg("MF", Ret)
        fileSelectedStop("", "")
        return
    BMSDataDir = OPTBMSDataDirRVar.get()
    for Index in Sel:
        Filename = MFFiles.get(Index)
# Blank line in the list.
        if len(Filename) == 0:
            continue
# Most items will have a (x bytes) or something like that following the file.
        if Filename.find(" (") != -1:
            Filename = Filename[:Filename.index(" (")]
# The plotter will use this/these in the title and the files will be listed in
# the INFO area when we're done.
        QPFilesProcessed.append(Filename)
        Filespec = DataDir+Filename
# The directory may have gotten changed, but the list of files not.
        if exists(Filespec) == False:
            setMsg("MF", "RW", "File %s does not exist."%Filespec, 2)
            fileSelectedStop("", "")
            return
        FilespecLC = Filespec.lower()
        if FilespecLC.endswith(".bms"):
# We only really want to check this once, but we don't know until here that a
# .bms folder was selected, so we'll just check it each file.
            if BMSDataDir not in ("data", "sdata"):
                setMsg("MF", "RW", \
                        "Select the '.bms Dir' checkbutton again.", 2)
                fileSelectedStop("", "")
                return
            if exists(Filespec+sep+BMSDataDir+sep) == False:
                setMsg("MF", "RW", "%s does not exist."% \
                        (Filespec+sep+BMSDataDir+sep), 2)
                fileSelectedStop("", "")
                return
# Get a list of all the files that we will be looking at.
            Ret = walkDirs2(Filespec, False, sep+BMSDataDir+sep, "", 1)
            if Ret[0] != 0:
                setMsg("MF", Ret)
                fileSelectedStop("", "")
                return
            Files = Ret[1]
            if len(Files) == 0:
                setMsg("MF", "RW", "No files were found in\n   %s"% \
                        (Filespec+sep+BMSDataDir+sep), 2)
                fileSelectedStop("", "")
                return
            Files.sort()
            FileCount = 0
            for File in Files:
                FileCount += 1
                if FileCount%500 == 0:
                    setMsg("MF", "CB", "Working on file %d of %d..."% \
                            (FileCount, len(Files)))
                Ret = q330Process(File, FromEpoch, ToEpoch, StaIDFilter, \
                        GapsDetect, 0, False, None, None, None)
                if Ret[0] != 0:
# Dump whatever may have been collected so far to keep from being a RAM pig.
                    clearQPGlobals()
                    setMsg("MF", Ret)
                    fileSelectedStop("", "")
                    return
# Check for stopping each file.
                PROGStopBut.update()
                if PROGRunning == 0:
                    clearQPGlobals()
                    setMsg("MF", "YB", "Stopped.")
                    fileSelectedStop("YB", "Stopped.")
                    return
# .ALL files usually made by EzBaler.
        elif FilespecLC.endswith(".all"):
# It's all-in-one so there is nly the one file to process. Tell q330process()
# to handle the update messages and checking for the Stop button press.
            Ret = q330Process(Filespec, FromEpoch, ToEpoch, StaIDFilter, \
                    GapsDetect, 0, False, PROGStopBut, PROGRunning, "MF")
            if Ret[0] != 0:
                clearQPGlobals()
                setMsg("MF", Ret)
                fileSelectedStop("", "")
                return
            PROGStopBut.update()
            if PROGRunning == 0:
                clearQPGlobals()
                setMsg("MF", "YB", "Stopped.")
                fileSelectedStop("YB", "Stopped.")
                return
        elif FilespecLC.endswith(".soh"):
# Again, just one file to work with.
            Ret = q330Process(Filespec, FromEpoch, ToEpoch, StaIDFilter, \
                    GapsDetect, 0, False, PROGStopBut, PROGRunning, "MF")
            if Ret[0] != 0:
                clearQPGlobals()
                setMsg("MF", Ret)
                fileSelectedStop("", "")
                return
            PROGStopBut.update()
            if PROGRunning == 0:
                clearQPGlobals()
                setMsg("MF", "YB", "Stopped.")
                fileSelectedStop("YB", "Stopped.")
                return
        elif FilespecLC.endswith(".sdr"):
            Ret = walkDirs2(Filespec, False, "", "", 0)
            if Ret[0] != 0:
                setMsg("MF", Ret)
                fileSelectedStop("", "")
                return
            Files = Ret[1]
            if len(Files) == 0:
                setMsg("MF", "RW", "No channel files were found in\n   %s"% \
                        Filespec, 2)
                fileSelectedStop("", "")
                return
            Files.sort()
            FileCount = 0
# There is no real good way to check these. We'll just have to try reading all
# of them and hope for the best. They should have the channel name in the file
# name, but we'll just go by the stuff in the files themselves.
            for File in Files:
                FileCount += 1
                if FileCount%50 == 0:
                    setMsg("MF", "CB", "Working on file %d of %d..."% \
                            (FileCount, len(Files)))
                Ret = q330Process(File, FromEpoch, ToEpoch, StaIDFilter, \
                        GapsDetect, 0, True, None, None, None)
                if Ret[0] != 0:
                    clearQPGlobals()
                    setMsg("MF", Ret)
                    fileSelectedStop("", "")
                    return
# Check for stopping each file.
                PROGStopBut.update()
                if PROGRunning == 0:
                    clearQPGlobals()
                    setMsg("MF", "YB", "Stopped.")
                    fileSelectedStop("YB", "Stopped.")
                    return
# A folder that ends in .nan, has seed or ms files (one channel per file), and
# may have .csv files with engineering data in them. It's a Nanometrics thing.
# This works for data recorded on TitanSMA SDCards, and stuff extracted from
# an Apollo server...at least the stuff we have.
        elif FilespecLC.endswith(".nan"):
            Ret = walkDirs2(Filespec, False, "", "", 1)
            if Ret[0] != 0:
                setMsg("MF", Ret)
                fileSelectedStop("", "")
                return
            Files = Ret[1]
            if len(Files) == 0:
                setMsg("MF", "RW", "No channel files were found in\n   %s"% \
                        Filespec, 2)
                fileSelectedStop("", "")
                return
            Files.sort()
            FileCount = 0
            for File in Files:
                FileCount += 1
                if FileCount%50 == 0:
                    setMsg("MF", "CB", "Working on file %d of %d..."% \
                            (FileCount, len(Files)))
                if File.endswith(".csv"):
                    Ret = nanProcessCSV(File, FromEpoch, ToEpoch, StaIDFilter)
                    if Ret[0] != 0:
                        clearQPGlobals()
                        setMsg("MF", Ret)
                        fileSelectedStop("", "")
                        return
# These are Nanometrics files that need to be converted with SohConvert.java
# from Nanometrics. I won't read them.
                elif File.endswith(".np"):
                    continue
# It's not normal for the user to have to run the SohConvert program on the .np
# files, but if it is done the program creates a .log file. Just ignore it.
                elif File.endswith(".log"):
                    continue
                else:
                    Ret = q330Process(File, FromEpoch, ToEpoch, StaIDFilter, \
                            GapsDetect, 0, True, None, None, None)
                    if Ret[0] != 0:
                        clearQPGlobals()
                        setMsg("MF", Ret)
                        fileSelectedStop("", "")
                        return
# Check for stopping each file.
                PROGStopBut.update()
                if PROGRunning == 0:
                    clearQPGlobals()
                    setMsg("MF", "YB", "Stopped.")
                    fileSelectedStop("YB", "Stopped.")
                    return
        elif FilespecLC.endswith(".ant"):
            Ret = walkDirs2(Filespec, False, "", "", 0)
            if Ret[0] != 0:
                setMsg("MF", Ret)
                fileSelectedStop("", "")
                return
            Files = Ret[1]
            if len(Files) == 0:
                setMsg("MF", "RW", "No channel files were found in\n   %s"% \
                        Filespec, 2)
                fileSelectedStop("", "")
                return
            Files.sort()
            FileCount = 0
            WhackAntSpikes = OPTWhackAntSpikesCVar.get()
# There is no real good way to check these. We'll just have to try reading all
# of them and hope for the best. They should have the channel name in the file
# name, but we'll just go by the stuff in the files themselves.
            for File in Files:
                FileCount += 1
                if FileCount%50 == 0:
                    setMsg("MF", "CB", "Working on file %d of %d..."% \
                            (FileCount, len(Files)))
# This will be called with SkipFile == False. .ant folders may be channel files
# or multiplexed files.
                Ret = q330Process(File, FromEpoch, ToEpoch, StaIDFilter, \
                        GapsDetect, WhackAntSpikes, False, None, None, None)
                if Ret[0] != 0:
                    clearQPGlobals()
                    setMsg("MF", Ret)
                    fileSelectedStop("", "")
                    return
# Check for stopping each file.
                PROGStopBut.update()
                if PROGRunning == 0:
                    clearQPGlobals()
                    setMsg("MF", "YB", "Stopped.")
                    fileSelectedStop("Stopped.")
                    return
        elif FilespecLC != "":
            setMsg("MF", "RW", \
                    "I don't know what to do with the file/folder\n   %s"% \
                    Filespec, 2)
            fileSelectedStop("", "")
            return
# Sometimes the data is so screwed up it can't even be viewed. This might help
# especially if the file names for .bms, .sdr, .nan and .ant sources were
# messed up. QPEEK gets a list of files in those directories, SORT THEM, and
# then processes and plots them. This could cause the data to be jumbled
# (though probably not in .sdr sources since they are supposed to be one
# channel per file). This will, of course, make overlaps go away, which might
# be a bad thing.
    if OPTSortAfterReadCVar.get() == 1:
        for Key in QPData.keys():
            QPData[Key].sort()
# Collect the earliest and latest times in the data.
    QPEarliestData = float(maxint)
    QPLatestData = -float(maxint)
    for Chan in QPData:
# It's possible that channels we didn't know how to decode will be in here,
# but will be [], so try.
        try:
            Min = min(QPData[Chan])[0]
            if Min < QPEarliestData:
                QPEarliestData = Min
            Max = max(QPData[Chan])[0]
            if Max > QPLatestData:
                QPLatestData = Max
        except ValueError:
            pass
# Must be something worth looking at.
    if QPEarliestData != float(maxint):
        plotMFPlot()
        formTPSPlot()
    if len(QPLogs) == 0:
        closeForm("LOG")
    else:
        formLOG()
    if len(QPErrors) == 0:
        closeForm("QPERR")
    else:
        formQPERR()
    INFOMsg = "Source(s) read:\n"
    for File in QPFilesProcessed:
        INFOMsg += "   "+File+"\n"
# Don't say anything if nothing was plotted.
    if QPEarliestData != float(maxint):
        INFOMsg += "Data times:\n   %s to\n   %s\n"%(dt2Time(-1, 80, \
                QPEarliestData), dt2Time(-1, 80, QPLatestData))
    INFOMsg += "Station ID:\n"
    for Value in QPStaIDs:
        INFOMsg += "   %s\n"%Value
    INFOMsg += "Net Code:\n"
    for Value in QPNetCodes:
        INFOMsg += "   %s\n"%Value
    INFOMsg += "Tag Number:\n"
    for Value in QPTagNos:
        INFOMsg += "   %s\n"%Value
    INFOMsg += "Software Version:\n"
    for Value in QPSWVers:
        INFOMsg += "   %s\n"%Value
    setMsg("INFO", "", INFOMsg)
# Now finish by displaying something in the MF message area.
    if QPEarliestData == float(maxint):
        if PROGStaIDFilterVar.get() == "":
            setMsg("MF", "YB", \
                "There doesn't appear to be anything I know how to plot.", 2)
        else:
# In case this is why there is nothing to plot (like maybe there was something
# in the field, but the wrong file was read).
            setMsg("MF", "YB", \
    "There doesn't appear to be anything I know how to plot for station %s."% \
                    PROGStaIDFilterVar.get(), 2)
    else:
        Message = "Done."
        C = ""
        if len(QPStaIDs) > 1:
            Message += " %d station IDs."%len(QPStaIDs)
            C = "YB"
        if len(QPNetCodes) > 1:
            Message += " %d network codes."%len(QPNetCodes)
            C = "YB"
        if len(QPTagNos) > 1:
            Message += " %d tag numbers."%len(QPTagNos)
            C = "YB"
        if len(QPSWVers) > 1:
            Message += " %d different firmware versions."%len(QPSWVers)
            C = "YB"
        if QPAntSpikesWhacked > 0:
            Message += " %d Antelope %s whacked."%(QPAntSpikesWhacked, \
                    sP(QPAntSpikesWhacked, ("spike", "spikes")))
            C = "YB"
        if OPTSortAfterReadCVar.get() == 1:
            Message += " Data is being sorted after reading! Be careful."
            C = "YB"
        setMsg("MF", C, Message)
    progControl("stopped")
    return
####################################
# BEGIN: fileSelectedStop(MClr, Msg)
# FUNC:fileSelectedStop():2013.047
def fileSelectedStop(MClr, Msg):
    formTPSMsg(MClr, Msg)
    formLOGMsg(MClr, Msg)
    formQPERRMsg(MClr, Msg)
    progControl("stopped")
    return
##################################
# BEGIN: setQPUserChannels(Action)
# FUNC:setQPUserChannels():2013.135
def setQPUserChannels(Action):
    global QPUserChannels
    global QPUnknownChanIDs
# Clean up and get the list of selected channels to display.
    formCPREFClean()
    UserChannels = eval("CPREFIDs%sVar"%CPREFCurrChanRVar.get()).get()
    if len(UserChannels) == 0:
        return (1, "RW", \
   "No channels have been entered in the selected Channel Preferences list.", \
                2)
# Break the list up into a List and then check to see if there is a 3-letter
# entry for each item in the list. The user will see the missing ones later.
# We'll remove them from the list for now.
    QPUserChannels = UserChannels.split(",")
    QPUCCopy = deepcopy(QPUserChannels)
    for Chan in QPUCCopy:
# The user list might be LHZ01 where the QPChans entries will only ever be LHZ.
# Throw out the channels we don't know how to deal with.
        if Chan[:3] not in QPChans:
# If we are replotting the main display we'll assume the user saw these
# already.
            if Action == "plot":
                QPErrors.append((1, "RW", \
           "Don't know how to plot channel '%s' in list. Removed from list."% \
                        Chan, 2))
# This is why we need the deepcopy.
            QPUserChannels.remove(Chan)
# Make a note of this for the Q330Process() part so it doesn't crash trying to
# find this channel in QPChans.  There may be XYZ01, XYZ02 and we want the
# whole family XYZ to be in here.
            if Chan[:3] not in QPUnknownChanIDs:
                QPUnknownChanIDs.append(Chan[:3])
# Oops. We removed everything.
    if len(QPUserChannels) == 0:
        return (1, "RW", \
                "No channels have been entered in the selected Channel Preferences list that the program knows how to deal with.", 2)
    return (0, )
# END: fileSelected




###################
# BEGIN: floatt(In)
# LIB:floatt():2009.102
#    Handles all of the annoying shortfalls of the float() function (vs C).
#    Does not handle scientific notation numbers.
def floatt(In):
    In = str(In).strip()
    if In == "":
        return 0.0
# At least let the system give it the ol' college try.
    try:
        return float(In)
    except:
        Number = ""
        for c in In:
            if c.isdigit() or c == ".":
                Number += c
            elif Number == "" and (c == "-" or c == "+"):
                Number += c
            elif c == ",":
                continue
            else:
                break
        try:
            return float(Number)
        except ValueError:
            return 0.0
# END: floatt




####################
# BEGIN: fmti(Value)
# LIB:fmti():2013.129
#   Just couldn't rely on the system to do this, although this won't handle
#   European-style numbers.
def fmti(Value):
    Value = int(Value)
    if Value > -1000 and Value < 1000:
        return str(Value)
    Value = str(Value)
    NewValue = ""
# There'll never be a + sign.
    if Value[0] == "-":
        Offset = 1
    else:
        Offset = 0
    CountDigits = 0
    for i in xrange(len(Value)-1, -1+Offset, -1):
        NewValue = Value[i]+NewValue
        CountDigits += 1
        if CountDigits == 3 and i != 0:
            NewValue = ","+NewValue
            CountDigits = 0
    if Offset != 0:
        if NewValue.startswith(","):
            NewValue = NewValue[1:]
        NewValue = Value[0]+NewValue
    return NewValue
# END: fmti




#####################
# BEGIN: fontBigger()
# LIB:fontBigger():2012.069
PROGSetups += ["PROGPropFontSize", "PROGMonoFontSize"]

def fontBigger():
    PSize = PROGPropFont["size"]
    if PSize < 0:
        PSize -= 1
    else:
        PSize += 1
    MSize = PROGMonoFont["size"]
    if MSize < 0:
        MSize -= 1
    else:
        MSize += 1
# If either font is at the limit don't change the other one or they will get
# 'out of synch' with each other (like if the original prop font size was 12
# and the mono font size was 10).
    if abs(PSize) > 16 or abs(MSize) > 16:
        beep(1)
        return
    PROGPropFontSize.set(PSize)
    PROGMonoFontSize.set(MSize)
    fontSetSize()
    return
######################
# BEGIN: fontSmaller()
# FUNC:fontSmaller():2012.067
def fontSmaller():
    PSize = PROGPropFont["size"]
    if PSize < 0:
        PSize += 1
    else:
        PSize -= 1
    MSize = PROGMonoFont["size"]
    if MSize < 0:
        MSize += 1
    else:
        MSize -= 1
    if abs(PSize) < 6 or abs(MSize) < 6:
        beep(1)
        return
    PROGPropFontSize.set(PSize)
    PROGMonoFontSize.set(MSize)
    fontSetSize()
    return
######################
# BEGIN: fontSetSize()
# FUNC:fontSetSize():2012.067
def fontSetSize():
    global PROGPropFontHeight
    PROGPropFont["size"] = PROGPropFontSize.get()
    PROGMonoFont["size"] = PROGMonoFontSize.get()
    PROGPropFontHeight = PROGPropFont.metrics("ascent")+ \
            PROGPropFont.metrics("descent")
    return
# END: fontBigger




#################################
# BEGIN: formABOUT(Parent = Root)
# LIB:formABOUT():2013.296
def formABOUT(Parent = Root):
# For the versions info.
    import Tkinter
    if isinstance(Parent, basestring):
        Parent = PROGFrm[Parent]
    Message = "%s (%s)\n   "%(PROG_LONGNAME, PROG_NAME)
    Message += "Version %s\n"%PROG_VERSION
    Message += "%s\n"%"PASSCAL Instrument Center"
    Message += "%s\n\n"%"Socorro, New Mexico USA"
    Message += "%s\n"%"Email: passcal@passcal.nmt.edu"
    Message += "%s\n"%"Phone: 575-835-5070"
    Message += "\n"
    Message += "--- Configuration ---\n"
    Message += \
            "%s %dx%d\nProportional font: %s (%d)\nFixed font: %s (%d)\n"% \
            (PROGSystemName, PROGScreenWidth, PROGScreenHeight, \
            PROGPropFont["family"], PROGPropFont["size"], \
            PROGMonoFont["family"], PROGMonoFont["size"])
# Some programs don't care about the geometry of the main display.
    try:
# If the variable has something in it get the current geometry. The variable
# value may still be the initial value from when the program was started.
        if PROGGeometryVar.get() != "":
            Message += "\n"
            Message += "Geometry: %s\n"%Root.geometry()
    except Exception, e:
        pass
# Some don't have setup files.
    try:
        if PROGSetupsFilespec != "":
            Message += "\n"
            Message += "--- Setups File ---\n"
            Message += "%s\n"%PROGSetupsFilespec
    except:
        pass
# This is only for QPEEK.
    try:
        if ChanPrefsFilespec != "":
            Message += "\n"
            Message += "--- Channel Preferences File ---\n"
            Message += "%s\n"%ChanPrefsFilespec
    except:
        pass
    Message += "\n"
    Message += "--- Versions ---\n"
    Message += "Python: %s\n"%PROG_PYVERSION
    Message += "Tcl/Tk: %s/%s\n"%(Tkinter.TclVersion, Tkinter.TkVersion)
    Message += "Tkinter: %s\n"%Tkinter.__version__
    formMYD(Parent, (("(OK)", LEFT, "ok"), ), "ok", "", "About", \
            Message.strip())
    return
# END: formABOUT




################################################################
# BEGIN: formCAL(Parent, Months = 3, Show = True, AllowX = True,
#                OrigFont = False)
# LIB:formCAL():2013.273
#   Displays a 1 or 3-month calendar with dates and day-of-year numbers.
#   Pass in 1 or 3 as desired.
PROGFrm["CAL"] = None
CALTmModeRVar = StringVar()
CALTmModeRVar.set("lt")
CALDtModeRVar = StringVar()
CALDtModeRVar.set("dates")
PROGSetups += ["CALTmModeRVar", "CALDtModeRVar"]
CALYear = 0
CALMonth = 0
CALText1 = None
CALText2 = None
CALText3 = None
CALMonths = 3
CALTipLastValue = ""

def formCAL(Parent, Months = 3, Show = True, AllowX = True, OrigFont = False):
    global CALText1
    global CALText2
    global CALText3
    global CALMonths
    global CALTipLastValue
    CALTipLastValue = ""
    if showUp("CAL"):
        return
    CALMonths = Months
    LFrm = PROGFrm["CAL"] = Toplevel(Parent)
    LFrm.withdraw()
    LFrm.resizable(0, 0)
    if AllowX == True:
        LFrm.protocol("WM_DELETE_WINDOW", Command(closeForm, "CAL"))
    if CALTmModeRVar.get() == "gmt":
        LFrm.title("Calendar (GMT)")
    elif CALTmModeRVar.get() == "lt":
        GMTDiff = getGMT(20)
        LFrm.title("Calendar (LT: GMT%+.2f hours)"%(float(GMTDiff)/3600.0))
    LFrm.iconname("Cal")
    Sub = Frame(LFrm)
    if CALMonths == 3:
        if OrigFont == False:
            CALText1 = Text(Sub, bg = Clr["D"], fg = Clr["B"], height = 11, \
                    width = 29, relief = SUNKEN, \
                    cursor = Button().cget("cursor"), state = DISABLED)
        else:
            CALText1 = Text(Sub, bg = Clr["D"], fg = Clr["B"], height = 11, \
                    width = 29, relief = SUNKEN, font = PROGOrigMonoFont, \
                    cursor = Button().cget("cursor"), state = DISABLED)
        CALText1.pack(side = LEFT, padx = 7)
    if OrigFont == False:
        CALText2 = Text(Sub, bg = Clr["W"], fg = Clr["B"], height = 11, \
                width = 29, relief = SUNKEN, \
                cursor = Button().cget("cursor"), state = DISABLED)
    else:
        CALText2 = Text(Sub, bg = Clr["W"], fg = Clr["B"], height = 11, \
                width = 29, relief = SUNKEN, font = PROGOrigMonoFont, \
                cursor = Button().cget("cursor"), state = DISABLED)
    CALText2.pack(side = LEFT, padx = 7)
    if CALMonths == 3:
        if OrigFont == False:
            CALText3 = Text(Sub, bg = Clr["D"], fg = Clr["B"], height = 11, \
                    width = 29, relief = SUNKEN, \
                    cursor = Button().cget("cursor"), state = DISABLED)
        else:
            CALText3 = Text(Sub, bg = Clr["D"], fg = Clr["B"], height = 11, \
                    width = 29, relief = SUNKEN, font = PROGOrigMonoFont, \
                    cursor = Button().cget("cursor"), state = DISABLED)
        CALText3.pack(side = LEFT, padx = 7)
    Sub.pack(side = TOP, padx = 3, pady = 3)
    if CALYear != 0:
        formCALMove("c")
    else:
        formCALMove("n")
    Sub = Frame(LFrm)
    BButton(Sub, text = "<<", command = Command(formCALMove, \
            "-y")).pack(side = LEFT)
    BButton(Sub, text = "<", command = Command(formCALMove, \
            "-m")).pack(side = LEFT)
    BButton(Sub, text = "Today", command = Command(formCALMove, \
            "n")).pack(side = LEFT)
    BButton(Sub, text = ">", command = Command(formCALMove, \
            "+m")).pack(side = LEFT)
    BButton(Sub, text = ">>", command = Command(formCALMove, \
            "+y")).pack(side = LEFT)
    Sub.pack(side = TOP, padx = 3, pady = 3)
    Sub = Frame(LFrm)
    SSub = Frame(Sub)
    SSSub = Frame(SSub)
    LRb = Radiobutton(SSSub, text = "GMT", value = "gmt", \
            variable = CALTmModeRVar, command = Command(formCALMove, "c"))
    LRb.pack(side = LEFT)
    ToolTip(LRb, 30, "Use what appears to be this computer's GMT time.")
    LRb = Radiobutton(SSSub, text = "LT", value = "lt", \
            variable = CALTmModeRVar, command = Command(formCALMove, "c"))
    LRb.pack(side = LEFT)
    ToolTip(LRb, 30, \
          "Use what appears to be this computer's time and time zone setting.")
    SSSub.pack(side = TOP, anchor = "w")
    SSub.pack(side = LEFT)
    Label(Sub, text = " ").pack(side = LEFT)
    SSub = Frame(Sub)
    LRb = Radiobutton(SSub, text = "Dates", value = "dates", \
            variable = CALDtModeRVar, command = Command(formCALMove, "c"))
    LRb.pack(side = TOP, anchor = "w")
    ToolTip(LRb, 30, "Show the calendar dates.")
    LRb = Radiobutton(SSub, text = "DOY", value = "doy", \
            variable = CALDtModeRVar, command = Command(formCALMove, "c"))
    LRb.pack(side = TOP, anchor = "w")
    ToolTip(LRb, 30, "Show the day-of-year numbers.")
    SSub.pack(side = LEFT)
    Label(Sub, text = " ").pack(side = LEFT)
    BButton(Sub, text = "Close", fg = Clr["R"], command = Command(closeForm, \
            "CAL")).pack(side = LEFT)
    Sub.pack(side = TOP, padx = 3, pady = 3)
    if Show == True:
        center(Parent, LFrm, "C", "I", True)
    return
####################################
# BEGIN: formCALMove(What, e = None)
# FUNC:formCALMove():2013.129
#   Handles changing the calendar form's display.
def formCALMove(What, e = None):
    global CALYear
    global CALMonth
    global CALText1
    global CALText2
    global CALText3
    PROGFrm["CAL"].focus_set()
    DtMode = CALDtModeRVar.get()
    Year = CALYear
    Month = CALMonth
    if What == "-y":
        Year -= 1
    elif What == "-m":
        Month -= 1
    elif What == "n":
        if CALTmModeRVar.get() == "gmt":
            Year, Month, Day = getGMT(4)
        elif CALTmModeRVar.get() == "lt":
            Year, DOY, HH, MM, SS = getGMT(11)
            GMTDiff = getGMT(20)
            if GMTDiff != 0:
                Year, Month, Day, DOY, HH, MM, SS = dt2TimeMath(0, GMTDiff, \
                        Year, 0, 0, DOY, HH, MM, SS)
    elif What == "+m":
        Month += 1
    elif What == "+y":
        Year += 1
    elif What == "c":
        if CALTmModeRVar.get() == "gmt":
            PROGFrm["CAL"].title("Calendar (GMT)")
        elif CALTmModeRVar.get() == "lt":
            GMTDiff = getGMT(20)
            PROGFrm["CAL"].title("Calendar (LT: GMT%+.2f hours)"% \
                    (float(GMTDiff)/3600.0))
    if Year < 1971:
        beep(1)
        return
    elif Year > 2050:
        beep(1)
        return
    if Month > 12:
        Year += 1
        Month = 1
    elif Month < 1:
        Year -= 1
        Month = 12
    CALYear = Year
    CALMonth = Month
# Only adjust this back one month if we are showing all three months.
    if CALMonths == 3:
        Month -= 1
    if Month < 1:
        Year -= 1
        Month = 12
    for i in xrange(0, 0+3):
# Skip the first and last months if we are only showing one month.
        if CALMonths == 1 and (i == 0 or i == 2):
            continue
        LTxt = eval("CALText%d"%(i+1))
        LTxt.configure(state = NORMAL)
        LTxt.delete("0.0", END)
        LTxt.tag_delete(*LTxt.tag_names())
        DOM1date = 0
        DOM1doy = PROG_FDOM[Month]
        if (Year%4 == 0 and Year%100 != 0) or Year%400 == 0:
            if Month > 2:
                DOM1doy += 1
        if i == 1:
            LTxt.insert(END, "\n")
            LTxt.insert(END, "%s"%(PROG_CALMON[Month]+" "+ \
                    str(Year)).center(29))
            LTxt.insert(END, "\n\n")
            IdxS = LTxt.index(CURRENT)
            LTxt.tag_config(IdxS, background = Clr["W"], foreground = Clr["R"])
            LTxt.insert(END, " Sun ", IdxS)
            IdxS = LTxt.index(CURRENT)
            LTxt.tag_config(IdxS, background = Clr["W"], foreground = Clr["U"])
            LTxt.insert(END, "Mon Tue Wed Thu Fri", IdxS)
            IdxS = LTxt.index(CURRENT)
            LTxt.tag_config(IdxS, background = Clr["W"], foreground = Clr["R"])
            LTxt.insert(END, " Sat", IdxS)
            LTxt.insert(END, "\n")
        else:
            LTxt.insert(END, "\n")
            LTxt.insert(END, "%s"%(PROG_CALMON[Month]+" "+ \
                    str(Year)).center(29))
            LTxt.insert(END, "\n\n")
            LTxt.insert(END, " Sun Mon Tue Wed Thu Fri Sat")
            LTxt.insert(END, "\n")
        All = monthcalendar(Year, Month)
        if CALTmModeRVar.get() == "gmt":
            NowYear, NowMonth, NowDay = getGMT(4)
        elif CALTmModeRVar.get() == "lt":
            NowYear, DOY, HH, MM, SS = getGMT(11)
            GMTDiff = getGMT(20)
            if GMTDiff != 0:
                NowYear, NowMonth, NowDay, DOY, HH, MM, SS = dt2TimeMath(0, \
                        GMTDiff, NowYear, 0, 0, DOY, HH, MM, SS)
        if DtMode == "dates":
            TargetDay = DOM1date+NowDay
        else:
            TargetDay = DOM1doy+NowDay
        for Week in All:
            LTxt.insert(END, " ")
            for DD in Week:
                if DD != 0:
                    if DtMode == "dates":
                        ThisDay = DOM1date+DD
                        ThisDay1 = DOM1date+DD
                        ThisDay2 = DOM1doy+DD
                    else:
                        ThisDay = DOM1doy+DD
                        ThisDay1 = DOM1doy+DD
                        ThisDay2 = DOM1date+DD
                    IdxS = LTxt.index(CURRENT)
                    if ThisDay == TargetDay and Month == NowMonth and \
                            Year == NowYear:
                        LTxt.tag_config(IdxS, background = Clr["C"], \
                                foreground = Clr["B"])
                    LTxt.tag_bind(IdxS, "<Enter>", \
                            Command(formCALStartTip, LTxt, "%s/%s"% \
                                    (ThisDay1, ThisDay2)))
                    LTxt.tag_bind(IdxS, "<Leave>", formCALHideTip)
                    LTxt.tag_bind(IdxS, "<ButtonPress>", formCALHideTip)
                    if DtMode == "dates":
                        if ThisDay < 10:
                            LTxt.insert(END, " ")
                            LTxt.insert(END, " %d"%ThisDay, IdxS)
                            LTxt.insert(END, " ")
                        else:
                            LTxt.insert(END, " ")
                            LTxt.insert(END, "%d"%ThisDay, IdxS)
                            LTxt.insert(END, " ")
                    else:
                        if ThisDay < 10:
                            LTxt.insert(END, "  %d"%ThisDay, IdxS)
                            LTxt.insert(END, " ")
                        elif ThisDay < 100:
                            LTxt.insert(END, " %d"%ThisDay, IdxS)
                            LTxt.insert(END, " ")
                        else:
                            LTxt.insert(END, "%d"%ThisDay, IdxS)
                            LTxt.insert(END, " ")
                else:
                    LTxt.insert(END, "    ")
            LTxt.insert(END, "\n")
        LTxt.configure(state = DISABLED)
        Month += 1
        if Month > 12:
            Year += 1
            Month = 1
    return
#################################################
# BEGIN: formCALStartTip(Parent, Value, e = None)
# FUNC:formCALStartTip():2011.110
#   Pops up a "tool tip" when mousing over the dates of Date/DOY.
CALTip = None

def formCALStartTip(Parent, Value, e = None):
# Multiple <Entry> events can be generated just by moving the cursor around.
# If we are still in the same date number just return.
    if Value == CALTipLastValue:
        return
    formCALHideTip()
    formCALShowTip(Parent, Value)
    return
######################################
# BEGIN: formCALShowTip(Parent, Value)
# FUNC:formCALShowTip():2011.110
def formCALShowTip(Parent, Value):
    global CALTip
    global CALTipLastValue
    CALTip = Toplevel(Parent)
    CALTip.withdraw()
    CALTip.wm_overrideredirect(1)
    LLb = Label(CALTip, text = Value, bg = Clr["Y"], bd = 1, fg = Clr["B"], \
            relief = SOLID, padx = 3, pady = 2)
    LLb.pack()
    x = Parent.winfo_pointerx()+4
    y = Parent.winfo_pointery()+4
    CALTip.wm_geometry("+%d+%d" % (x, y))
# If you do a .lift() along with the deiconify the tooltip "flashes", so I'm
# not doing it and it seems to work OK.
    CALTip.deiconify()
    CALTipLastValue = Value
    return
#################################
# BEGIN: formCALHideTip(e = None)
# FUNC:formCALHideTip():2011.110
def formCALHideTip(e = None):
    global CALTip
    global CALTipLastValue
    try:
        CALTip.destroy()
    except:
        pass
    CALTip = None
    CALTipLastValue = ""
    return
# END: formCAL




####################
# BEGIN: formCPREF()
# FUNC:formCPREF():2013.191
PROGFrm["CPREF"] = None
CPREFCurrChanRVar = StringVar()
CPREFCurrChanRVar.set("1")
CPREFCurrNameVar = StringVar()
# This is the easiest way to do this and not have to do something special to
# the ChanPrefsSetups saver and loader.
CPREFName1Var = StringVar()
CPREFIDs1Var = StringVar()
CPREFName2Var = StringVar()
CPREFIDs2Var = StringVar()
CPREFName3Var = StringVar()
CPREFIDs3Var = StringVar()
CPREFName4Var = StringVar()
CPREFIDs4Var = StringVar()
CPREFName5Var = StringVar()
CPREFIDs5Var = StringVar()
CPREFName6Var = StringVar()
CPREFIDs6Var = StringVar()
CPREFName7Var = StringVar()
CPREFIDs7Var = StringVar()
CPREFName8Var = StringVar()
CPREFIDs8Var = StringVar()
CPREFName9Var = StringVar()
CPREFIDs9Var = StringVar()
CPREFName10Var = StringVar()
CPREFIDs10Var = StringVar()
CPREFName11Var = StringVar()
CPREFIDs11Var = StringVar()
CPREFName12Var = StringVar()
CPREFIDs12Var = StringVar()
CPREFName13Var = StringVar()
CPREFIDs13Var = StringVar()
CPREFName14Var = StringVar()
CPREFIDs14Var = StringVar()
CPREFName15Var = StringVar()
CPREFIDs15Var = StringVar()
CPREFName16Var = StringVar()
CPREFIDs16Var = StringVar()
CPREFName17Var = StringVar()
CPREFIDs17Var = StringVar()
CPREFName18Var = StringVar()
CPREFIDs18Var = StringVar()
CPREFName19Var = StringVar()
CPREFIDs19Var = StringVar()
CPREFName20Var = StringVar()
CPREFIDs20Var = StringVar()
# FINISHME - Leave these in here for a while. This will make a bridge until
# everyone has a channel prefs setups file. They get saved and loaded after
# anything happens with the make setups file, so they should always be good
# to go.
PROGSetups += ["CPREFCurrChanRVar", "CPREFCurrNameVar", \
        "CPREFName1Var", "CPREFIDs1Var", \
        "CPREFName2Var", "CPREFIDs2Var", \
        "CPREFName3Var", "CPREFIDs3Var", \
        "CPREFName4Var", "CPREFIDs4Var", \
        "CPREFName5Var", "CPREFIDs5Var", \
        "CPREFName6Var", "CPREFIDs6Var", \
        "CPREFName7Var", "CPREFIDs7Var", \
        "CPREFName8Var", "CPREFIDs8Var", \
        "CPREFName9Var", "CPREFIDs9Var", \
        "CPREFName10Var", "CPREFIDs10Var", \
        "CPREFName11Var", "CPREFIDs11Var", \
        "CPREFName12Var", "CPREFIDs12Var", \
        "CPREFName13Var", "CPREFIDs13Var", \
        "CPREFName14Var", "CPREFIDs14Var", \
        "CPREFName15Var", "CPREFIDs15Var", \
        "CPREFName16Var", "CPREFIDs16Var", \
        "CPREFName17Var", "CPREFIDs17Var", \
        "CPREFName18Var", "CPREFIDs18Var", \
        "CPREFName19Var", "CPREFIDs19Var", \
        "CPREFName20Var", "CPREFIDs20Var"]
ChanPrefsSetups = ["CPREFCurrChanRVar", "CPREFCurrNameVar", \
        "CPREFName1Var", "CPREFIDs1Var", \
        "CPREFName2Var", "CPREFIDs2Var", \
        "CPREFName3Var", "CPREFIDs3Var", \
        "CPREFName4Var", "CPREFIDs4Var", \
        "CPREFName5Var", "CPREFIDs5Var", \
        "CPREFName6Var", "CPREFIDs6Var", \
        "CPREFName7Var", "CPREFIDs7Var", \
        "CPREFName8Var", "CPREFIDs8Var", \
        "CPREFName9Var", "CPREFIDs9Var", \
        "CPREFName10Var", "CPREFIDs10Var", \
        "CPREFName11Var", "CPREFIDs11Var", \
        "CPREFName12Var", "CPREFIDs12Var", \
        "CPREFName13Var", "CPREFIDs13Var", \
        "CPREFName14Var", "CPREFIDs14Var", \
        "CPREFName15Var", "CPREFIDs15Var", \
        "CPREFName16Var", "CPREFIDs16Var", \
        "CPREFName17Var", "CPREFIDs17Var", \
        "CPREFName18Var", "CPREFIDs18Var", \
        "CPREFName19Var", "CPREFIDs19Var", \
        "CPREFName20Var", "CPREFIDs20Var"]
CPREF_SLOTS = 20

def formCPREF(e = None):
    if showUp("CPREF"):
        return
    LFrm = PROGFrm["CPREF"] = Toplevel(Root)
    LFrm.withdraw()
    LFrm.resizable(0, 0)
    LFrm.protocol("WM_DELETE_WINDOW", Command(formCPREFControl, "close"))
    LFrm.title("Channel Preferences")
    LFrm.iconname("CPref")
    Label(LFrm, \
            text = "Place a list of channels you want records decoded for, and in the order you want them plotted, separated by commas in the\nIDs field, select the radiobutton, and then read the data source file. A name can be given to the set to make it easier\nto remember. If you want LOG records decoded just place LOG at the in the list.").pack(side = TOP)
    for i in xrange(1, 1+CPREF_SLOTS):
        Sub = Frame(LFrm)
        Radiobutton(Sub, text = "Name:", variable = CPREFCurrChanRVar, \
                value = str(i), command = formCPREFCurrName).pack(side = LEFT)
        LEnt = Entry(Sub, textvariable = eval("CPREFName%dVar"%i), width = 14)
        LEnt.pack(side = LEFT)
        LEnt.bind("<KeyRelease>", formCPREFCurrName)
        Label(Sub, text = " IDs:").pack(side = LEFT)
        Entry(Sub, textvariable = eval("CPREFIDs%dVar"%i), \
                width = 105).pack(side = LEFT)
        Sub.pack(side = TOP, anchor = "w", padx = 3)
    Sub = Frame(LFrm)
    BButton(Sub, text = "Copy", \
            command = formCPREFCopy).pack(side = LEFT)
    BButton(Sub, text = "Paste", \
            command = formCPREFPaste).pack(side = LEFT)
    Label(Sub, text = " ").pack(side = LEFT)
    BButton(Sub, text = "Scan For Channel IDs", \
            command = formSFCI).pack(side = LEFT)
    BButton(Sub, text = "Sort", command = formCPREFSort).pack(side = LEFT)
    Label(Sub, text = " ").pack(side = LEFT)
    BButton(Sub, text = "Close", fg = Clr["R"], \
            command = Command(formCPREFControl, "close")).pack(side = LEFT)
    Sub.pack(side = TOP, padx = 3, pady = 3)
    center(Root, LFrm, "C", "I", True)
    return
####################################
# BEGIN: formCPREFCurrName(e = None)
# FUNC:formCPREFCurrName():2012.319
#   Just sets CPREFCurrNameVar to the name of the currently selected field
#   every time the radiobutton selection is changed or the form is closed for
#   others (like the main display to show).
def formCPREFCurrName(e = None):
    CPREFCurrNameVar.set(eval("CPREFName%sVar"%CPREFCurrChanRVar.get()).get())
    return
########################
# BEGIN: formCPREFCopy()
# FUNC:formCPREFCopy():2012.311
#   Grabs the list of channel IDs from the selected slot.
def formCPREFCopy():
    formCPREFClean()
    Chans = eval("CPREFIDs%sVar"%CPREFCurrChanRVar.get()).get()
    if Chans == "":
        Answer = formMYD("CPREF", (("(OK)", TOP, "ok"), ), "ok", "", \
                "She's Empty.", "There is nothing to copy.")
        return
    PROGClipboardVar.set(Chans)
    setMsg("CPREF", "", "Copied.")
    return
#########################
# BEGIN: formCPREFPaste()
# FUNC:formCPREFPaste():2012.319
#   Sticks what should be a list of channel IDs into the selected slot. These
#   will normally be from the list built in formSFCI().
def formCPREFPaste():
    if PROGClipboardVar.get() == "":
        Answer = formMYD("CPREF", (("(OK)", TOP, "ok"), ), "ok", "", \
                "She's Empty.", "There is nothing to paste.")
        return
    if eval("CPREFIDs%sVar"%CPREFCurrChanRVar.get()).get() != "":
        Answer = formMYD("CPREF", (("Yes", LEFT, "yes"), ("No!", LEFT, \
                "no")), "no", "YB", "I See Old Channels.", \
                "The selected channel slot already contains something. It will be overwritten. Is that OK?")
        if Answer == "no":
            setMsg("CPREF", "", "Nothing done.")
    eval("CPREFName%sVar"%CPREFCurrChanRVar.get()).set("PASTED")
    eval("CPREFIDs%sVar"%CPREFCurrChanRVar.get()).set(PROGClipboardVar.get())
    setMsg("CPREF", "", "Pasted.")
    formCPREFCurrName()
    return
########################
# BEGIN: formCPREFSort()
# FUNC:formCPREFSort():2012.319
def formCPREFSort():
    PROGFrm["CPREF"].focus_set()
    DSorter = {}
    formCPREFClean()
    for i in xrange(1, 1+CPREF_SLOTS):
# Combining the items to make the key will help with duplicate names while...
        Key = eval("CPREFName%dVar"%i).get()+","+eval("CPREFIDs%dVar"%i).get()
        if Key == ",":
            continue
# ...doing this will get rid of duplicate entries.
        DSorter[Key] = [eval("CPREFName%dVar"%i).get(), \
                eval("CPREFIDs%dVar"%i).get()]
# Clear.
    for i in xrange(1, 1+CPREF_SLOTS):
        eval("CPREFName%dVar"%i).set("")
        eval("CPREFIDs%dVar"%i).set("")
    CPREFCurrChanRVar.set("1")
    Keys = DSorter.keys()
    Keys.sort()
    Slot = 1
    for Key in Keys:
        eval("CPREFName%dVar"%Slot).set(DSorter[Key][0])
        eval("CPREFIDs%dVar"%Slot).set(DSorter[Key][1])
        Slot += 1
    formCPREFCurrName()
    return
#########################
# BEGIN: formCPREFClean()
# FUNC:formCPREFClean():2012.319
def formCPREFClean():
    for i in xrange(1, 1+CPREF_SLOTS):
        eval("CPREFName%dVar"%i).set(eval("CPREFName%dVar"% \
                i).get().strip().upper())
        Str = eval("CPREFIDs%dVar"%i).get()
        Str = Str.replace(" ", "")
        Str = Str.upper()
        Str = deComma(Str)
# FINISHME - should probably look for anything other than letters, numbers and commas
        eval("CPREFIDs%dVar"%i).set(Str)
    formCPREFCurrName()
    return
#################################
# BEGIN: formCPREFControl(Action)
# FUNC:formCPREFControl():2012.319
def formCPREFControl(Action):
    if Action == "close":
        formCPREFCurrName()
        closeForm("CPREF")
    return
# END: formCPREF




##########################################
# BEGIN: formFind(Who, WhereMsg, e = None)
# LIB:formFind():2013.303
#   Implements a "find" function in a form's Text() field.
#   The caller must set up the global Vars:
#      <Who>FindLookForVar = StringVar()
#      <Who>FindLastLookForVar = StringVar()
#      <Who>FindLinesVar = StringVar()
#      <Who>FindIndexVar = IntVar()
#   <Who> must be the string "INE", "CKTRD", etc.
#   Then on the form set up an Entry field and two Buttons like:
#
#   LEnt = Entry(Sub, width = 20, textvariable = HELPFindLookForVar)
#   LEnt.pack(side = LEFT)
#   LEnt.bind("<Return>", Command(formFind, "HELP", "HELP"))
#   LEnt.bind("<KP_Enter>", Command(formFind, "HELP", "HELP"))
#   BButton(Sub, text = "Find", command = Command(formFind, "HELP", \
#           "HELP")).pack(side = LEFT)
#   BButton(Sub, text = "Next", command = Command(formFindNext, \
#           "HELP", "HELP")).pack(side = LEFT)
#
def formFind(Who, WhereMsg, e = None):
    setMsg(WhereMsg, "CB", "Finding...")
    LTxt = PROGTxt[Who]
    LookFor = eval("%sFindLookForVar"%Who).get().lower()
    LTxt.tag_delete("Find%s"%Who)
    LTxt.tag_delete("FindN%s"%Who)
    if LookFor == "":
        eval("%sFindLinesVar"%Who).set("")
        eval("%sFindIndexVar"%Who).set(-1)
        setMsg(WhereMsg)
        return 0
    Found = 0
# Do this in case there is a lot of text from any previous find, otherwise
# the display just sits there.
    updateMe(0)
    eval("%sFindLastLookForVar"%Who).set(LookFor)
    eval("%sFindLinesVar"%Who).set("")
    eval("%sFindIndexVar"%Who).set(-1)
    FindLines = ""
    N = 1
    while 1:
        if LTxt.get("%d.0"%N) == "":
            break
        Line = LTxt.get("%d.0"%N, "%d.0"%(N+1)).lower()
        if Line.find(LookFor) != -1:
            TagStart = "%d.%d"%(N, Line.find(LookFor))
            TagEnd = "%d.%d"%(N, Line.find(LookFor)+len(LookFor))
            LTxt.tag_add("Find%s"%Who, TagStart, TagEnd)
            LTxt.tag_config("Find%s"%Who, background = Clr["U"], \
                    foreground = Clr["W"])
            FindLines += " %s,%s"%(TagStart, TagEnd)
            Found += 1
        N += 1
    if Found == 0:
        setMsg(WhereMsg, "", "No matches found.")
    else:
        eval("%sFindLinesVar"%Who).set(FindLines)
        formFindNext(Who, WhereMsg, True, True)
        setMsg(WhereMsg, "", "Matches found: %d"%Found)
    return Found
###########################################################################
# BEGIN: formFindNext(Who, WhereMsg, Find = False, First = False, e = None)
# FUNC:formFindNext():2013.303
def formFindNext(Who, WhereMsg, Find = False, First = False, e = None):
    LTxt = PROGTxt[Who]
    LTxt.tag_delete("FindN%s"%Who)
    FindLines = eval("%sFindLinesVar"%Who).get().split()
    if len(FindLines) == 0:
        beep(1)
        return
# Figure out which line we are at (at the top of the Text()) and then go
# through the found lines and find the closest one. Only do this on the first
# go of a search and not on "next" finds.
    if First == True:
        Y0, Y1 = LTxt.yview()
        AtLine = LTxt.index("@0,%d"%Y0)
# If we are at the top of the scroll then just go on normally.
        if AtLine > "1.0":
            AtLine = intt(AtLine)
            Index = -1
            Found = False
            for Line in FindLines:
                Index += 1
                Line = intt(Line)
                if Line >= AtLine:
                    Found = True
                    break
# If the current position is past the last found item just let things happen
# normally (i.e. jump to the first item found).
            if Found == True:
                eval("%sFindIndexVar"%Who).set(Index-1)
    Index = eval("%sFindIndexVar"%Who).get()
    Index += 1
    try:
        Line = FindLines[Index]
        eval("%sFindIndexVar"%Who).set(Index)
    except IndexError:
        Index = 0
        Line = FindLines[Index]
        eval("%sFindIndexVar"%Who).set(0)
# Make the "current find" red.
    TagStart, TagEnd = Line.split(",")
    LTxt.tag_add("FindN%s"%Who, TagStart, TagEnd)
    LTxt.tag_config("FindN%s"%Who, background = Clr["R"], \
            foreground = Clr["W"])
    LTxt.see(TagStart)
# If this is the first find just let the caller set a message.
    if Find == False:
        setMsg(WhereMsg, "", "Match %d of %d."%(Index+1, len(FindLines)))
    return
# END: formFind




##################
# BEGIN: formGPS()
# FUNC:formGPS():2013.246
PROGFrm["GPS"] = None
GPSPoints = []
GPSPOINTS_DT = 0
GPSPOINTS_FIX = 1
GPSPOINTS_SATS = 2
GPSPOINTS_LATI = 3
GPSPOINTS_LONG = 4
GPSPOINTS_ELEV = 5

def formGPS():
    if showUp("GPS") == True:
        return
    LFrm = PROGFrm["GPS"] = Toplevel(Root)
    LFrm.withdraw()
    LFrm.resizable(0, 0)
    LFrm.protocol("WM_DELETE_WINDOW", Command(formGPSControl, "close"))
    LFrm.title("GPS Data Plotter")
    LFrm.iconname("GPS")
    Sub = Frame(LFrm)
    LCan = PROGCan["GPS"] = Canvas(LFrm, height = 400, width = 400, \
            bg = DClr["GS"])
    LCan.pack(side = TOP)
    Sub = Frame(LFrm)
    BButton(Sub, text = "Read/Plot", command = Command(formGPSRead, \
            "read")).pack(side = LEFT)
    Label(Sub, text = " ").pack(side = LEFT)
    BButton(Sub, text = "Export", command = formGPSExport).pack(side = LEFT)
    Label(Sub, text = " ").pack(side = LEFT)
    BButton(Sub, text = "Close", fg = Clr["R"], \
            command = Command(closeForm, "GPS")).pack(side = LEFT)
    Label(Sub, text = " ").pack(side = LEFT)
    LLb = Label(Sub, text = "Hints ")
    LLb.pack(side = LEFT)
    ToolTip(LLb, 30, "--Right-click on dot: Right-clicking on a dot shows the information for that dot.\n--Left-click on dot: Left-clicking on a dot removes that dot from the plot and replots all of the remaining points. Use this to remove outliers.")
    Sub.pack(side = TOP, pady = 3)
    PROGMsg["GPS"] = Text(LFrm, font = PROGPropFont, height = 2, wrap = WORD)
    PROGMsg["GPS"].pack(side = TOP, fill = X)
    center(Root, LFrm, "C", "I", True)
    return
#############################
# BEGIN: formGPSClear(Action)
# FUNC:formGPSClear():2013.246
def formGPSClear(Action):
    global GPSPoints
    PROGFrm["GPS"].title("GPS Data Plotter")
    LCan = PROGCan["GPS"]
    LCan.delete(ALL)
    LCan.configure(bg = DClr["GS"])
    if Action == "read":
        del GPSPoints[:]
    setMsg("GPS", "", "")
    return
########################
# BEGIN: formGPSExport()
# FUNC:formGPSExport():2013.246
def formGPSExport():
    if len(GPSPoints) == 0:
        setMsg("GPS", "RW", "There are no points to export.", 2)
        return
    setMsg("GPS", "CB", "Exporting...")
# The names may have naughty characters in them.
    print QPFilesProcessed[0]
    File = cleanAFilename(QPFilesProcessed[0]+"gps.dat")
    try:
        Fp = open(PROGDataDirVar.get()+File, "w")
    except:
        setMsg("GPS", "MW", "Error opening file\n   %s"%File, 3)
        return
    try:
        Fp.write("# GPS data points for %s\n"%list2Str(QPFilesProcessed))
        for Point in GPSPoints:
            Fp.write("%s\t%s\t%d\t%+f\t%+f\t%f\n"%(Point[GPSPOINTS_DT], \
                    Point[GPSPOINTS_FIX], Point[GPSPOINTS_SATS], \
                    Point[GPSPOINTS_LATI]-90.0, Point[GPSPOINTS_LONG]-180.0, \
                    Point[GPSPOINTS_ELEV]))
        Fp.close()
    except:
        setMsg("GPS", "MW", "Error writing to file\n   %s"%File, 3)
        return
    setMsg("GPS", "GB", "GPS data exported to\n   %s"%File, 1)
    return
############################
# BEGIN: formGPSRead(Action)
# FUNC:formGPSRead():2013.246
def formGPSRead(Action):
    global GPSPoints
    LCan = PROGCan["GPS"]
    formGPSClear(Action)
    Found = 0
    MinLati = float(maxint)
    MaxLati = -float(maxint)
    MinLong = float(maxint)
    MaxLong = -float(maxint)
    if Action == "read":
        if len(QPLogs) == 0:
            setMsg("GPS", "RW", "There are no LOG messages to read.", 2)
            return
        setMsg("GPS", "CB", "Plotting...")
# Don't list all of the files.
        Filename = QPFilesProcessed[0]
        if len(QPFilesProcessed) > 1:
            Filename += "+"
        PROGFrm["GPS"].title(Filename)
        GPSPoints = []
        Lines = len(QPLogs)
        Index = 0
        while Index < Lines:
            Line = QPLogs[Index]
            if Line.find("GPS Status") != -1:
                Index += 1
                DateTime = "?"
                Fix = "?"
                Sats = 0
                Height = 0.0
                Lati = 0.0
                Long = 0.0
                while Index < Lines:
                    Line = QPLogs[Index].lower()
                    C = Line.find("fix type:")
                    if C != -1:
                        Fix = Line[C+10:].strip().upper()
                        Index += 1
                        continue
                    C = Line.find("height:")
                    if C != -1:
                        Height = floatt(Line[C+7:])
                        Index += 1
                        continue
                    C = Line.find("latitude:")
                    if C != -1:
                        Pos = Line[C+10:]
                        Lati = floatt(Pos[0:2])+floatt(Pos[2:])/60.0
                        if Pos.find("s") != -1:
                            Lati = -Lati
# The +90 and +180 below gets rid of the negative numbers so latitudes will
# always be 0 at south pole to 180 at north pole and longitudes will always
# be 0 at Greenwich to 360 at Greenwich. Much easier to plot.
                        Lati += 90.0
                        Index += 1
                        continue
                    C = Line.find("longitude:")
                    if C != -1:
                        Pos = Line[C+11:]
                        Long = floatt(Pos[0:3])+floatt(Pos[3:])/60.0
                        if Pos.find("w") != -1:
                            Long = -Long
                        Long += 180.0
                        Index += 1
                        continue
                    C = Line.find("sat. used:")
                    if C != -1:
                        Sats = intt(Line[C+11:])
                        Index += 1
                        continue
                    C = Line.find("last gps timemark:")
                    if C != -1:
                        DateTime = Line[C+19:].strip()
# Hopefully the timemark will always be the last item.
                        if Height != 0.0 and Lati != 0.0 and Long != 0.0:
# FINISHME - something may need to go here to filter bad positions.
# Might as well determine these as we go.
                            if Lati < MinLati:
                                MinLati = Lati
                            if Lati > MaxLati:
                                MaxLati = Lati
                            if Long < MinLong:
                                MinLong = Long
                            if Long > MaxLong:
                                MaxLong = Long
                            GPSPoints.append([DateTime, Fix, Sats, Lati, \
                                    Long, Height])
                            Found += 1
# Break out even if it is not.
                        break
                    Index += 1
# Made up GPS messages from .nan processing.
            elif Line.find("GPSPOS:") != -1:
# 0 1    2      3    4    5   6     7
# d t GPSPOS: lati long elev SATS: sats
                Parts = Line.split()
                if len(Parts) < 8:
                    Index += 1
                    continue
                Fix = "?"
                Height = floatt(Parts[5])
                Ret = checkLatiLong("lati", Parts[3], 1)
                if Ret[0] != 0:
                    Index += 1
                    continue
                Lati = Ret[1]
# The +90 and +180 below gets rid of the negative numbers so latitudes will
# always be 0 at South Pole to 180 at North Pole and longitudes will always
# be 0 at Greenwich to 360 at Greenwich. Much easier to plot.
                Lati += 90.0
                Ret = checkLatiLong("long", Parts[4], 1)
                if Ret[0] != 0:
                    Index += 1
                    continue
                Long = Ret[1]
                Long += 180.0
                Sats = intt(Parts[7])
                DateTime = "%s %s"%(Parts[0], Parts[1])
                if Height != 0.0 and Lati != 0.0 and Long != 0.0:
# FINISHME - something may need to go here to filter bad positions.
# Might as well determine these as we go.
                    if Lati < MinLati:
                        MinLati = Lati
                    if Lati > MaxLati:
                        MaxLati = Lati
                    if Long < MinLong:
                        MinLong = Long
                    if Long > MaxLong:
                        MaxLong = Long
                    GPSPoints.append([DateTime, Fix, Sats, Lati, Long, Height])
                    Found += 1
            Index += 1
    elif Action == "replot":
        for Point in GPSPoints:
#              0      1    2     3      4      5
# Point = [DateTime, Fix, Sats, Lati, Long, Height]
            if Point[GPSPOINTS_LATI] < MinLati:
                MinLati = Point[GPSPOINTS_LATI]
            if Point[GPSPOINTS_LATI] > MaxLati:
                MaxLati = Point[GPSPOINTS_LATI]
            if Point[GPSPOINTS_LONG] < MinLong:
                MinLong = Point[GPSPOINTS_LONG]
            if Point[GPSPOINTS_LONG] > MaxLong:
                MaxLong = Point[GPSPOINTS_LONG]
            Found += 1
    if Found == 0:
        setMsg("GPS", "YB", "No GPS information was found.", 1)
        return
# The MaxRange is going to be plotted in a square 75% of the height of the
# canvas (which should be a square).
    PY = LCan.winfo_height()
    Buff = PY*.25/2.0
    PlotW = PY*.75
    Index = 0
    Plotted = 0
# Special case, otherwise the point ends up in the lower left-hand corner.
    if Found == 1:
        XY = Buff+PlotW/2.0
        ID = LCan.create_rectangle(XY-2, XY-2, XY+2, XY+2, fill = DClr["GD"])
        LCan.tag_bind(ID, "<Button-1>", Command(formGPSShowPoint, Index))
    else:
# The plot area (no matter what shape the canvas is) is just going to be the
# greater of maxlat x maxlat, or maxlong x maxlong for simplicity, so figure
# out the max size in degrees.
        LatiRange = getRange(MinLati, MaxLati)
# Just in case.
        if LatiRange == 0.0:
            LatiRange = 1.0
# Get this back into -90 0 +90 range for the cos().
        LatiAve = (MinLati+MaxLati)/2.0-90.0
        LongRange = getRange(MinLong, MaxLong)
        if LongRange == 0.0:
            LongRange = 1.0
        if LatiRange == 1.0 and LongRange == 1.0:
            canText(LCan, 10, PROGPropFontHeight, DClr["TX"], "No range.")
        else:
            canText(LCan, 10, PROGPropFontHeight, DClr["TX"], \
                    "LatRange: %.2fm    LongRange: %.2fm"%(LatiRange* \
                    110574.27, LongRange*111319.458*cos(LatiAve/360.0* \
                    3.14159*2.0)))
# The Nanometrics receivers that we were testing showed the same position for
# days. Highly suspicious. Skip points that don't change.
        LastLati = -0.0
        LastLong = -0.0
        for Point in GPSPoints:
            Lati = Point[GPSPOINTS_LATI]
            Long = Point[GPSPOINTS_LONG]
            if Lati == LastLati and Long == LastLong:
                Index += 1
                continue
            LastLati = Lati
            LastLong = Long
# We have to switch the Y zero point to the bottom of the canvas (the plot
# area, actually) and then come back up the amount of the latitude.
            YY = (Buff+PlotW)-((Lati-MinLati)/LatiRange*PlotW)
# These just plot in from the edge.
            XX = Buff+(Long-MinLong)/LongRange*PlotW
# Don't make an outline so the boxes have a black border which will separate
# them a little since they will mostly be on top of each other (on black bg).
            ID = LCan.create_rectangle(XX-2, YY-2, XX+2, YY+2, \
                    fill = DClr["GD"])
            LCan.tag_bind(ID, "<Button-1>", Command(formGPSShowPoint, Index))
            LCan.tag_bind(ID, "<Button-3>", Command(formGPSZapPoint, Index))
            updateMe(0)
            Index += 1
            Plotted += 1
    setMsg("GPS", "", "Done. Plotted %d of %d."%(Plotted, Found))
    return
##########################################
# BEGIN: formGPSShowPoint(Index, e = None)
# FUNC:formGPSShowPoint():2012.318
def formGPSShowPoint(Index, e = None):
    setMsg("GPS", "", \
            "Mark: %s   Fix: %s   Sats: %d\nLat: %s   Long: %s   Elev: %gm"% \
            (GPSPoints[Index][GPSPOINTS_DT], GPSPoints[Index][GPSPOINTS_FIX], \
            GPSPoints[Index][GPSPOINTS_SATS], \
            pm2nsew("lat", GPSPoints[Index][GPSPOINTS_LATI]-90.0), \
            pm2nsew("lon", GPSPoints[Index][GPSPOINTS_LONG]-180.0), \
            GPSPoints[Index][GPSPOINTS_ELEV]))
    return
#########################################
# BEGIN: formGPSZapPoint(Index, e = None)
# FUNC:formGPSZapPoint():2013.113
#   Removed points from GPSPoints and calls for a replot.
def formGPSZapPoint(Index, e = None):
    global GPSPoints
    del GPSPoints[Index]
    formGPSRead("replot")
    return
###############################
# BEGIN: formGPSControl(Action)
# FUNC:formGPSControl():2012.318
#   Just for freeing up the GPSPoints.
def formGPSControl(Action):
    global GPSPoints
    if Action == "close":
        del GPSPoints[:]
        closeForm("GPS")
        return
# END: formGPS




HELPText = \
"QUICK START\n\
===========\n\
1. Start QPEEK by entering qpeek or qpeek.py or ./qpeek.py or by clicking \
on QPEEK's icon depending on the operating system of the computer and \
how the program was installed.\n\
\n\
2. If this is the first time QPEEK has been run on the computer or in \
the user account a file navigation dialog will show up. Navigate to a \
directory with some data source files and click OK.\n\
\n\
3. A list of data source files should show up in the file list area.\n\
\n\
4. If this is the first time QPEEK has been run select one of the data \
source files of interest in the file list area (just one click) and then \
select the menu item Commands|Scan For Channel IDs. If applicable, select \
data/ or sdata/ on the scan form if a .bms folder is to be scanned.\n\
\n\
5. Click the Scan button. The function will read through the selected \
data source directory/file and produce a button for each channel (like \
\"LHZ\") that it finds. You can either select the buttons one at a time and \
add them to the long empty field on the scan form in the order you want \
them plotted, or you can just click the All button to copy them all to \
the field in alphabetical order.\n\
\n\
6. Once the list of channels has been made click the Copy button. This \
puts the list of channels on a 'clipboard' in QPEEK.\n\
\n\
7. Click the Channel Preferences button on the scan form. On the form \
that comes up select one of the radiobuttons next to the Name labels \
(an empty line, or a previously used one) and click the Paste button at \
the bottom of the form. This will place the list of channels into the \
selected slot.\n\
\n\
8. Now go back to the main display and double-click the same data source \
file that was scanned, or click the Read button, to read and plot the data.\n\
\n\
Once you have \"standard\" sets of channel IDs in the Channel \
Preferences form you don't need to scan files anymore. If there are \
different sets of channels for different sets of stations (like POLENET or \
GLISN stations, as an example) or sets of equipment (like Guralp \
or Streckeisen stations) you just put together different lists of \
channels for those, select the right set for the data you are going to \
read, and then Read the data. If there are channels in the list that \
are not in the data, or vice versa, it won't matter. Messages about \
that will show up in the Error Messages display. You can then just alter \
the list of channels in use as needed and Read again.\n\
\n\
\n\
DESCRIPTION\n\
===========\n\
QPEEK is a graphical data visualizer program for examining the data files \
produced by Quanterra Q330 recorders and programs used to retrieve data \
from Quanterra Balers. QPEEK will read data from B44 baler memory sticks, \
.ALL and .SOH files produced by programs like EzBaler, and files that \
were created by splitting the data using a program like sdrsplit. QPEEK \
will also read data offloaded fro the SD cards recorded by Nanometrics \
TitanSMA units. The Titan data reading is still under development.\n\
\n\
Starting QPEEK is dependent on the operating system of the computer it is \
running on, and how it was installed. It may be by entering qpeek or \
qpeek.py on the command line, or by double-clicking on an icon.\n\
\n\
The first time QPEEK is started in an account it will request an initial \
directory to look in for data source files and sub-directories. This, and \
all of the program's settings, will be saved when QPEEK is stopped, so this \
should not need to be done on subsequent starts.\n\
\n\
Since any combination of channels may be in a data source file or \
directory QPEEK must be told which channels to look for and plot. This \
can be done by first scanning the data source that is going to be plotted \
using the Commands | Scan For Channel IDs function. The list of channels \
it produces can then be copied and pasted into a slot on the Commands \
| Channel Preferences form. This list will tell QPEEK which channels to \
look for. This list can be use when reading data files from any similarly \
programmed station/recorder. The scanning does not need to be done for each \
individual recorder.\n\
\n\
\n\
DATA SOURCE FILE FORMATS\n\
========================\n\
QPEEK recognizes six different formats of data files and directories, but \
it needs just a little help to make the data source files show up in the \
file selection list on the right side of the main program display.\n\
\n\
Baler Memory Sticks\n\
-------------------\n\
The data on USB memory sticks writtin by Quanterra B44s can be read by \
QPEEK if the files and directories on a memory stick are dragged to a \
folder/directory that ends in .bms. A folder named WHIT1.bms, for \
example, would be created and then the contents of the first memory \
stick from the station WHIT could be placed in there. The contents of a \
second stick could be placed in WHIT2.bms. WHIT1.bms and WHIT2.bms would \
then show up in the file list when QPEEK is pointed at the parent directory \
where the two folders are located.\n\
\n\
The B44's usually record a data/ and an sdata/ directory. Which directory \
gets read when a .bms folder is selected can be controlled using the '.bms \
Dir' radiobuttons on the main display.\n\
\n\
.ALL And .SOH Files\n\
-------------------\n\
These types, usually produced by EzBaler or some such program, can be read \
directly by QPEEK without renaming them or placing them in a specially named \
folder or sub-directory. There names must just end with .all or .soh.\n\
\n\
Files From sdrsplit\n\
-------------------\n\
If, for example, a .ALL or .SOH file is split up using a program like \
sdrsplit into a file for each channel these can be read by QPEEK if they \
are all placed into a folder/directory whose name ends with .sdr.\n\
\n\
This method can also be used when reading real time data files created \
by Antelope. If each file is a separate channel in something like a \
directory for each day, then the day directory need only be renamed \
so it ends with .sdr and QPEEK will be able to read the data for the \
day. If there is data from more than one station in the day directory \
the Station field on the main display can be used to filter out and \
plot data from only one of them.\n\
\n\
Files From An Antelope Archive\n\
------------------------------\n\
Data files created by Antelope can be read using the .sdr extension, but \
only if the individual files are one channel per file. If the files are \
multiplexed, then the .ant extension should be used for the day directories \
in the example above.\n\
\n\
Files From Nanometrics Sources\n\
------------------------------\n\
I only have access to data from a few of these units, so things may still \n\
need to be changed.\n\
\n\
Generally, Nanometrics recorders write seismic data to seed/mini-seed \
files, and State Of Health (SOH) information to ASCII Comma Separated \
Values (CSV) files. QPEEK will read through directories whose names \
end with .nan and plot the information from those two file types.\n\
\n\
GPS postion information, if found in the CSV files, will be converted to \
LOG file lines and displayed in the LOG Messages window so their values \
can be plotted using the Commands | GPS Data Plotter function. The \
positions are recorded every minute, which for seismic work is a bit \
excessive. QPEEK only generates a LOG line once every 30 minutes.\n\
\n\
\n\
TO READ OR NOT TO READ\n\
======================\n\
To see some settings take effect a source data file will need to be read \
or re-read, while other settings will only need the display to be replotted. \
Some of the tooltips indicate (Read), (Read or Replot), or (Replot) to \
indicate what needs to be done. The Detect Gaps checkbutton tooltip \
indicates (Read or Replot). This means that if a file is read with \
gap detection turned off you cannot just turn it on and Replot to display \
the gaps. The file must be re-Read. If it is selected when the file is read \
then it can be turned off and it will not show up in a Replot. It can then \
subsequently be turned back on and show up again.\n\
\n\
Items that will change with a Replot:\n\
   Options | MP Coloring...\n\
   Options | Show YYYY... (any of the date formats)\n\
   Magnify radiobuttons\n\
   Background color radiobuttons\n\
   Gap Len value\n\
   Removing channels from a channel list\n\
\n\
Items that need source data to be (re)Read:\n\
   Options | Whack Antelope Spikes\n\
   Station name filtering\n\
   Changing to a different channel list, or adding channels to the\n\
       current list\n\
   Changing .bms Dir radiobuttons\n\
   Detect Gaps checkbutton (maybe - see above)\n\
   Turning on TPS plot\n\
\n\
\n\
DATE FORMATS\n\
============\n\
QPEEK understands the date as\n\
   YYYY-MM-DD like 2012-11-10\n\
   YYYY:DOY like 2012:315\n\
   YYYYMMMDD like 2012NOV10\n\
\n\
Text messages from the Q330 seem to use the YYYY-MM-DD format so it is the \
default. Changing how QPEEK displays the dates it displays can be changed \
with the Options menu items.\n\
\n\
\n\
MAIN DISPLAY BUTTONS AND FIELDS\n\
===============================\n\
Main Data Directory Button\n\
--------------------------\n\
Click this item to open a directory selection dialog and use it to \
navigate to a folder/directory where .bms/.ALL/.SOH/.sdr/.nan data source \
files/folders/directories are located. When the OK button on the \
directory selector is clicked the file list area will be filled in \
with the data source files and folders that QPEEK understands.\n\
\n\
A directory path may also be entered directly into the file path field \
and the Return key pressed to change directories, or to reload the list \
of files.\n\
\n\
From And To Date Fields\n\
-----------------------\n\
Dates can be entered in these fields that will restrict the reading of \
data source files to just those two dates from 00:00 on the From date \
to 24:00 on the To date. The date can be entered in any of the formats \
described in the DATE FORMATS section.\n\
\n\
The C buttons open a calendar whose dates can be clicked on to select \
a data for each field.\n\
\n\
The File Selection List\n\
-----------------------\n\
The file selection list displays all of the data format types that QPEEK \
knows how to deal with based on the file extensions (.bms, .All, .SOH, \
.srd, .ant and .nan) of the names of the files and directories in the \
Main Data Directory.\n\
\n\
The Options | Calculate File Sizes menu item will toggle showing the \
sizes of the sorces. This can sometimes take a while to calculate, so it \
can be turned off.\n\
\n\
----- Find:= Field and Clear Button\n\
Text can be placed in the Find field, the Return key pressed, and the \
list of files will be rearranged such that file names containing the entered \
text will be listed in a group at the top of the file list. You could use \
this to pull out all of the \"WHIT\" station files from a long list of \
files, for example. The Clear button clears the field and updates the \
list of files.\n\
\n\
----- Reload Button\n\
Just refreshes the list of files in case items have been added to the data \
directory or renamed.\n\
\n\
Station Field\n\
-------------\n\
Sometimes there may be more than one station's information in a source \
file or directory/folder. If that happens you can enter the name of the \
station of interest in this field and records from any other station will be \
ignored. Using the Scan For Channel IDs function will list the stations \
found in a data source when it is finished scanning.\n\
\n\
This only applies to seed/mini-seed data sources. Nanometrics CSV files \
do not contain any information about which station they are information \
for, so QPEEK will read and plot all of the CSV files in its path without \
knowing which station the data belongs to even if it is correctly filtering \
the seed/mini-seed information.\n\
\n\
Replot Button\n\
-------------\n\
This can be used to redo the plots after changing the background color \
radiobuttons, changing the channel list (with the exception of adding \
channels to the current list -- that will require a re-Read), changing \
the magnification level, changing the gap detection length, changing the \
date format, or changing the mass position coloring ranges.\n\
\n\
The Replot button cannot be used when adding channels to the current \
channel list to get those channel to plot, or when changing the station \
name in the Station field, or when turning on Detect Gaps when it was \
off during the initial reading of the data source.\n\
\n\
Background: B W Radiobuttons\n\
----------------------------\n\
The background color of the main and the TPS display plot areas are \
controlled with this. The choices are \"B\"lack or \"W\"hite. Black is \
good for viewing on a computer and White is good for saving toner when \
printing. The Replot button can be used to replot if the background \
color selection is changed.\n\
\n\
Magnifiy: 1x 2x 4x Radiobuttons\n\
-------------------------------\n\
In 1x mode all information is plotted in the horizontal space of the \
plotting area. 2x and 4x simply extend the plotting area so that \
the plots are stretched out two and four times the width of the visible \
plotting area. The horizontal scrollbar at the bottom of the plotting \
area would then be used to see all of the data.\n\
\n\
S,C Buttons, Curr: Field\n\
------------------------\n\
The S button simply opens the Scan For Channel IDs form.\n\
The C button simply opens the Channel Preferences form.\n\
\n\
The Curr: field displays the currently selected slot on the Channel \
Preferences form. The slot cannot be changed from here. It is just for \
informational purposes.\n\
\n\
.bms Dir: data/ sdata/ Radiobuttons\n\
-----------------------------------\n\
The B44 memory sticks usually have a sub-directory on them named \"data\" \
which contains all channels recorded by the Q330, and a sub-directory \
named \"sdata\" which contains only the State Of Health (SOH) channels \
of data and the low sample rate seismic data. Use these radiobuttons to \
select which directory to read data from and plot.\n\
\n\
Detect Gaps Checkbutton, Len Field\n\
----------------------------------\n\
QPEEK can be directed to detect gaps when no data from any channel was \
recorded. The gaps will appear as red bars above all other plots. The \
program splits up the range of data into 5-minute blocks (similar to \
the TPS plot) and keeps track of if there was any data point recorded \
during each 1-minute block (starting from 00:00:00 UT each day).\n\
\n\
Because of the sparse number of data points currently extracted the \
minimum gap length that can reliably be detected depends on what is \
being read. For low sample rate SOH-type data sources the minimum gap \
length may be upto 120 minutes. For any source containing 20sps data \
and up it can be between 5 and 30 minutes. 40sps and up should be able \
to always handle 1-minute gap detection.\n\
\n\
The gap time length may be entered in the Len field. It must be some \
multiple of 1 minute, and can be entered like 5m, 300s, 120m, 1h, 2h30m, \
etc. If just a number is entered it will be treated as seconds.\n\
\n\
When the Detect Gaps checkbutton is on it will, of course, slow down \
the reading of a data source a little bit since the timestamp of every \
data point will be examined. QPEEK will skip channels that are not in \
the channel list, and even skip whole files when reading a .sdr data \
source if that file's channels are not being plotted, there may be a \
lot of false alarms when just reading a few channels.\n\
\n\
----- TPS Checkbutton, Chans Field -----\n\
The TPS checkbutton controls whether or not the Time-Power-Squared \
plotting form will appear when a data source is read.\n\
\n\
The TPS plot shows the square root of the average of the sum of the \
squares of the data amplitudes over each 5-minute period of each day \
covering the time range of the data on the main display. Each \
horizontal line is one UT day. All of the requested data is plotted \
after the data source has been read, but because it can take a long \
time to plot everything replotting the information must be done \
manually using the Plot button on the TPS form. This allows you to \
quickly zoom in on an area and then redo the TPS plot without having \
to wait for it every time you zoom in or out.\n\
\n\
The Chans field on the main display is used to tell the TPS plotter which \
channels to plot. The desired seismic data channels to plot should be \
entered into this field. Multiple channels may be entered separated by a \
comma. An asterisk can be added to the end of a channel name to cover \
things like location codes. For example \"LHZ*\" will cover plotting \
channels LHZ01 and LHZ02. LHZ02 may also be entered if you just want \
that channel plotted.  If the channels have location codes and you just \
enter \"LHZ\" in the list LHZ01 and LHZ02 will not be plotted. The asterisk \
may only be added at the end of the channel name, and not, for example, \
in the middle like L*Z.\n\
\n\
Each 5-minute block is color-coded according to the average amplitude \
during the period. There are four ranges, Antarctica, Low, Medium and \
High.\n\
Antarctica:\n\
    Dark Grey/Black - there was no data for that period or the\n\
                      average really was 0.0 (not likely)\n\
          Dark blue - the average was +/-10 counts\n\
               Cyan - +/-100 counts\n\
              Green - +/-1,000 counts\n\
             Yellow - +/-10,000 counts\n\
                Red - +/-100,000 counts\n\
            Magenta - +/-1,000,000 counts\n\
   Light Grey/White - > +/-1,000,000 counts\n\
Low:\n\
    Dark Grey/Black - there was no data for that period or the\n\
                      average really was 0.0 (not likely)\n\
          Dark blue - the average was +/-20 counts\n\
               Cyan - +/-200 counts\n\
              Green - +/-2,000 counts\n\
             Yellow - +/-20,000 counts\n\
                Red - +/-200,000 counts\n\
            Magenta - +/-2,000,000 counts\n\
   Light Grey/White - > +/-2,000,000 counts\n\
Medium:\n\
    Dark Grey/Black - there was no data for that period or the\n\
                      average really was 0.0 (not likely)\n\
          Dark blue - the average was +/-50 counts\n\
               Cyan - +/-500 counts\n\
              Green - +/-5,000 counts\n\
             Yellow - +/-50,000 counts\n\
                Red - +/-500,000 counts\n\
            Magenta - +/-5,000,000 counts\n\
   Light Grey/White - > +/-5,000,000 counts\n\
High:\n\
    Dark Grey/Black - there was no data for that period or the\n\
                      average really was 0.0 (not likely)\n\
          Dark blue - the average was +/-80 counts\n\
               Cyan - +/-800 counts\n\
              Green - +/-8,000 counts\n\
             Yellow - +/-80,000 counts\n\
                Red - +/-800,000 counts\n\
            Magenta - +/-8,000,000 counts\n\
   Light Grey/White - > +/-8,000,000 counts\n\
\n\
The ranges are selected by using the \"A\", \"L\", \"M\" and \"H\" \
radiobuttons on the plot window. The Chans field is the same as the \
Chans field on the main display.\n\
\n\
Clicking along a days line will draw a box around the point clicked \
on and display the counts value during the five-minute period for that \
point on the line. It also draws a line on the main display at the same \
time as the 5-minute block of time that was clicked on.\n\
\n\
A broken dark line of boxes (a dotted line) indicates that there was no \
data for 1 or more days. This is done instead of plotting, possibly 100's, \
of lines with nothing in them. The dots in the line can be clicked on \
to see how many days were skipped.\n\
\n\
----- Read/Stop Buttons -----\n\
The Read button starts the reading of the selected source file, and \
the Stop button halts the reading of a source file. This may be \
used if it is decided that the file selected is not the correct one, \
or is too long to wait to be read.\n\
\n\
----- Write .ps Button -----\n\
This creates a PostScript file of the the contents of the main plot area. \
When selected a dialog box will allow the name of the output file to be \
selected or entered.\n\
\n\
----- Replot Button (lower right-hand corner) -----\n\
Use this button after changing the size of the window to command QPEEK \
to redraw the plots. There is too much inconsistancy between installations \
and versions of operating systems for this to be done automatically. Some \
systems command QPEEK to redraw the plots after the resizing of the \
window is finished, and some send the command many times WHILE resizing \
the window. On some systems it is easy to change this behavior, and on \
some systems it isn't. This button makes it the responsibility of the \
user to click the Redraw button when they are finished resizing the \
window.\n\
\n\
This button is the same as the other Replot button below the files list.\n\
\n\
\n\
MENU COMMANDS\n\
=============\n\
FILE MENU\n\
---------\n\
----- Delete Setups File -----\n\
Sometimes a bad setups file can cause the program to misbehave. This can \
be caused by upgrading the program, but reading the setups file created \
by an earlier version of the program, or reading the setups file copied \
from a computer with a different operating system. This function will \
delete the current setups file (whose location can be found in the Help | \
About command box) and then quit the program without saving the current \
parameters. This will reset all parameters to their default values. When \
the program is restarted a dialog box should appear saying that the setups \
file could not be found.\n\
\n\
----- Quit -----\n\
Quits QPEEK.\n\
\n\
\n\
COMMANDS MENU\n\
-------------\n\
----- Log Search -----\n\
Displays a window where a string of text may be entered. The LOG messages \
currently in the LOG Messages form will be searched for lines containing the \
entered string. The search is not case-sensitive. Just the lines matching \
the search string will be displayed. This is different from the search \
field at the bottom of the LOG Messages window.\n\
\n\
GPS Data Plotter\n\
----------------\n\
The LOG messages may contain GPS information. This function brings up a \
form that can be used to plot that information. Clicking the Read/Plot \
button will tell the function to read through all of the LOG messages \
that were read from the data source and plot the results. The plotted \
points can be clicked on to display the time, fix type, number of satellites \
used for the reading, latitude, longitude, and elevation values. The \
range of the latitude and longitude readings in meters are displayed at \
the top of the plot.\n\
\n\
Some recorders will record the same GPS position repeatedly even when the \
GPS is off. The function filters out positions that are the same more than \
once in a row. This is why the display may show something like 'Plotted \
4 of 1235.'\n\
\n\
Right-clicking on a point will delete that point from the plot to allow \
throwing out \"bad\" points. If multiple data points are plotted on top \
of each other multiple right-clicks will be required to eliminate them. \
Re-reading the data source is required to recover deleted points.\n\
\n\
The Export button writes the currently read data points (all points \
read minus any deleted with the right-click) a tab-delimited file. The \
lines have the format\n\
\n\
    # Comment about the source information file(s)\n\
    Time  Latitude  Longitude  Elevation\n\
    Time  Latitude  Longitude  Elevation\n\
    ...\n\
The file will be in the current data directory and will be named the \
same as the source information file with \"gps.dat\" appended to the \
end.\n\
\n\
TPS Form\n\
--------\n\
This opens the TPS Plot form. If a data source is read, and the TPS \
checkbutton was not checked, this can be used to open the TPS Plot form. \
After setting the channels to plot (Chans field) the Plot button on \
the TPS Plot form can then be used to generate the plots without rereading \
the data source.\n\
\n\
----- Channel Preferences -----\n\
----- Scan For Channel IDs -----\n\
Figuring out which channels to look for and/or plot is not entirely \
straightforward in QPEEK. Mostly this is because the channel naming \
convention used to record the different kinds of data, while being \
\"standardized\", is not set in stone, and in reality the channels \
can be named whatever the user wants.\n\
\n\
Internally the program has a set list of three-character codes for \
channels that it knows how to deal with. This list can be seen using \
the Help | Known Channels menu item. If a channel is found in the data \
that is not in that list there will be an error message in the Error \
Messages form after a data source is read. Getting a channel on that \
list requires a change to the program. Which sub-set of the channels \
in the internal list that get extracted from the selected data source \
file is the job of the lists made on the Channel Preferences form. Up \
to 20 different lists/slots of channels may be created. The list that \
is selected with the radiobutton at the left side of each slot is the \
one that will be applied to the next data source file that is read. \
Each list/slot can be given a name to make it easier to remember what \
the list of channels applies to. The name of the selected list will \
appear in the 'Curr:' field on the main display.\n\
\n\
The channels in the slots are listed like\n\
\n\
    LCQ,VCO,VEA,LHZ,LHN,LHE...\n\
\n\
The order that the channels are listed will be the order that they are \
plotted. If the order of the channels is changed the data only need be \
replotted to show the change with the exception of adding channels to the \
list. If channels are added the data source file will need to be re-Read \
so the data for the added channel(s) can be extracted.\n\
\n\
A copy of a list can be made by using the Copy button to copy the selected \
entry, then by selecting another slot's radiobutton and then using the \
Paste button.\n\
\n\
The Scan For Channel IDs form is a helper that will read through a data \
source file selected in the file selection list and list all of the \
channels found as buttons on the form. A button may be clicked to add \
that channel to the entry field on the form. Once the list of channels \
is created it can be copied to the Channel Preferences form using the \
Copy button on the Scan For Channel IDs form, and pasted into a slot \
using the Paste button on the Channel Preferences form.\n\
\n\
All channel names \"made up\" from information in Nanometrics CSV files \
will begin with the letter N.\n\
\n\
\n\
OPTIONS MENU\n\
------------\n\
----- Show Seismic Data In Counts -----\n\
Shows the max and min values for seismic data plot in counts, instead \
of converting them to volts.\n\
\n\
This option is still under development.\n\
\n\
----- MP Coloring: x.x, x.x, x.x, x.x -----\n\
These items are used to set the voltage ranges and values for coloring \
mass position plots. The x.x values are in volts. The first range of \
settings are for \"regular\" broadband sensors (Guralp, Streckheisen) \
and the second set is for Trillium sensors.\n\
\n\
----- Show YYYY-MM-DD Dates -----\n\
----- Show YYYYMMMDD Dates -----\n\
----- Show YYYY:DOY Dates ----\n\
Selecting one of these menu items will tell QPEEK to display all of \
the dates in the selected format, except for the actual SOH messages. \
They will always be in the YYYY-DD-MM format used by the Q330 and \
Nanometrics recorders.\n\
\n\
----- Calculate File Sizes -----\n\
The sizes of the files and folders/directories listed in the file \
selection list can have their sizes displayed. This is off by default, \
because calculating the sizes of all of the files listed can take a \
significant amount of time. Each \"file\" can contain 1000's of files \
each depending on the type.\n\
\n\
This defaults to 'off' every time QPEEK is started.\n\
\n\
----- Sort Data By Time After Read -----\n\
Sometimes the data is so screwed up it can't even be viewed. This might \
help, especially if the file names for .bms, .sdr, .nan or .ant sources are \
not named such that they sort correctly. QPEEK gets a list of files in \
those directories, SORTS THEM, and then processes and plots them. This \
could cause the data to be jumbled (though probably not in .sdr sources \
since they are supposed to be one channel per file and one file per \
channel). Using this setting will, of course, make overlaps go away, \
which might be a bad thing.\n\
\n\
This defaults to 'off' every time QPEEK is started.\n\
\n\
Whack Antelope Spikes\n\
---------------------\n\
Antelope can be configured to insert large values into a data stream \
when data is missing. It's very annoying, because the spkies will show \
up when plotting, but everything else will be flatlined. Selecting this \
option will detect data points that have this large value (16384^2) \
and simply ignore them which will create a gap in the data which is \
what you would really want to see.\n\
\n\
This defaults to 'off' every time QPEEK is started.\n\
\n\
----- Fonts BIGGER -----\n\
----- Fonts smaller -----\n\
These two items will decrease or increase the size of the program's \
fonts.\n\
\n\
\n\
FORMS MENU\n\
----------\n\
The currently open forms of the program will show up here. Selecting one \
will bring that form to the foreground.\n\
\n\
\n\
HELP MENU\n\
---------\n\
----- Known Channels -----\n\
This lists the 3-letter SEED codes that the program knows how to extract \
and plot. Changing this list is not difficult (for me), but requires \
changes to the program's code.\n\
\n\
----- Calendar -----\n\
Just a built-in calendar that shows dates or DOY values for three months \
in a row. Of course the clock of the computer that is running QPEEK must \
be correct for this to show the right current date.\n\
\n\
----- Check For Updates -----\n\
If the computer is connected to the Internet selecting this function will \
contact PASSCAL's website and check the version of the program against \
a copy of the program that is on the website. Appropriate dialog boxes \
will be shown depending on the result of the check.\n\
\n\
If the current version is old the Download button in the dialog box that \
will appear may be clicked to obtain the new version. The new version will \
be delivered in a zipped file/folder and the name of the program will be \
preceeded by \"new\". A dialog box indicating the location of the \
downloaded file will be shown after the downloading finishes. Once it has \
been confirmed by the user that the \"new\" program file is OK, it should \
be renamed (remove \"new\") and placed in the proper location which \
depends on the operating system of the computer.\n"


##############################################
# BEGIN: formHELP(Parent, AllowWriting = True)
# LIB:formHELP():2013.035
#   Put the help contents in global variable HELPText somewhere in the
#   program.
PROGFrm["HELP"] = None
HELPFindIndexVar = IntVar()
HELPFindLastLookForVar = StringVar()
HELPFindLookForVar = StringVar()
HELPFindLinesVar = StringVar()
HELPFilespecVar  = StringVar()
PROGSetups += ["HELPFindLookForVar", "HELPFilespecVar"]
HELPHeight = 25
HELPWidth = 80
HELPFont = PROGOrigMonoFont

def formHELP(Parent, AllowWriting = True):
    if PROGFrm["HELP"] != None:
        PROGFrm["HELP"].deiconify()
        PROGFrm["HELP"].lift()
        return
    LFrm = PROGFrm["HELP"] = Toplevel(Parent)
    LFrm.withdraw()
    LFrm.protocol("WM_DELETE_WINDOW", Command(closeForm, "HELP"))
    LFrm.title("Help - %s"%PROG_NAME)
    LFrm.iconname("Help")
    Sub = Frame(LFrm)
    LTxt = PROGTxt["HELP"] = Text(Sub, font = HELPFont, height = HELPHeight, \
            width = HELPWidth, wrap = WORD, relief = SUNKEN)
    LTxt.pack(side = LEFT, expand = YES, fill = BOTH)
    LSb = Scrollbar(Sub, orient = VERTICAL, command = LTxt.yview)
    LSb.pack(side = RIGHT, fill = Y)
    LTxt.configure(yscrollcommand = LSb.set)
    Sub.pack(side = TOP, expand = YES, fill = BOTH)
    Sub = Frame(LFrm)
    labelTip(Sub, "Find:=", LEFT, 30, "[Find]")
    LEnt = Entry(Sub, width = 20, textvariable = HELPFindLookForVar)
    LEnt.pack(side = LEFT)
    LEnt.bind("<Return>", Command(formFind, "HELP", "HELP"))
    LEnt.bind("<KP_Enter>", Command(formFind, "HELP", "HELP"))
    BButton(Sub, text = "Find", command = Command(formFind, \
            "HELP", "HELP")).pack(side = LEFT)
    BButton(Sub, text = "Next", command = Command(formFindNext, \
            "HELP", "HELP")).pack(side = LEFT)
    if AllowWriting:
        Label(Sub, text = " ").pack(side = LEFT)
        BButton(Sub, text = "Write To File", \
                command = Command(formHELPWrite, LTxt)).pack(side = LEFT)
    Label(Sub, text = " ").pack(side = LEFT)
    BButton(Sub, text = "Close", fg = Clr["R"], \
            command = Command(closeForm, "HELP")).pack(side = LEFT)
    Sub.pack(side = TOP, padx = 3, pady = 3)
    PROGMsg["HELP"] = Text(LFrm, font = PROGPropFont, height = 3, wrap = WORD)
    PROGMsg["HELP"].pack(side = TOP, fill = X)
    LTxt.insert(END, HELPText)
# Clear this so the formFind() routine does the right thing if this form was
# brought up previously.
    HELPFindLinesVar.set("")
    center(Parent, LFrm, "C", "I", True)
    if HELPFilespecVar.get() == "" or \
            exists(dirname(HELPFilespecVar.get())) == False:
# Not all programs will have all directory vars. Look for them in this order.
        try:
            HELPFilespecVar.set(PROGWorkDirVar.get()+PROG_NAMELC+"help.txt")
        except NameError:
            try:
                HELPFilespecVar.set(PROGMsgsDirVar.get()+PROG_NAMELC+ \
                        "help.txt")
            except NameError:
# The program HAS to have one of these, so don't try here. Let it crash.
                HELPFilespecVar.set(PROGDataDirVar.get()+PROG_NAMELC+ \
                        "help.txt")
    return
#####################################
# BEGIN: formHELPWrite(Who, e = None)
# FUNC:formHELPWrite():2011.128
def formHELPWrite(Who, e = None):
    Dir = dirname(HELPFilespecVar.get())
    if Dir.endswith(sep) == False:
        Dir += sep
    File = basename(HELPFilespecVar.get())
    Filespec = formMYDF("HELP", 3, "Save Help To...", Dir, File)
    if Filespec == "":
        setMsg("HELP", "", "Nothing done.")
    try:
        Fp = open(Filespec, "wb")
    except Exception, e:
        setMsg("HELP", "MW", "Error opening help file\n   %s\n   %s"% \
                (Filespec, e), 3)
        return
    Fp.write("Help for %s version %s\n\n"%(PROG_NAME, PROG_VERSION))
    N = 1
    while 1:
        if Who.get("%d.0"%N) == "":
            break
# The lines from the Text field do not come with a \n after each screen line,
# so we'll have to split the lines up ourselves.
        Line = Who.get("%d.0"%N, "%d.0"%(N+1))
        N += 1
        if len(Line) < 65:
            Fp.write(Line)
            continue
        Out = ""
        for c in Line:
            if c == " " and len(Out) > 60:
                Fp.write(Out+"\n")
                Out = ""
            elif c == "\n":
                Fp.write(Out+"\n")
                Out == ""
            else:
                Out += c
    Fp.close()
    HELPFilespecVar.set(Filespec)
    setMsg("HELP", "", "Help written to\n   %s"%Filespec)
    return
# END: formHELP




####################################################################
# BEGIN: formMYD(Parent, Clicks, Close, C, Title, Msg1, Msg2 = "", \
#                Bell = 0, CenterX = 0, CenterY = 0, Width = 0)
# LIB:formMYD():2013.311
#   The built-in dialog boxes cannot be associated with a particular frame, so
#   the Root/Main window kept popping to the front and covering up everything
#   on some systems when they were used, so I wrote this. I'm sure there is a
#   "classy" way of doing this, but I couldn't figure out how to return a
#   value after the window was destroyed from a classy-way.
#
#   The dialog box can contain an input field by using something like:
#
#   Answer = formMYD(Root, (("Input60", TOP, "input"), ("Write", LEFT, \
#           "input"), ("(Cancel)", LEFT, "cancel")), "cancel", "YB"\
#           "Let it be written...", \
#   "Enter a message to write to the Messages section (60 characters max.):")
#   if Answer == "cancel":
#       return
#   What = Answer.strip()
#   if len(What) == 0 or len(What) > 60:
#       Root.bell()
#   print (What)
#
#   The "Input60" tells the function to make an entry field 60 characters
#   long.  The "input" return value for the "Write" button tells the routine
#   to return whatever was entered into the input field. The "Cancel" button
#   will return "cancel", which, of course, could be confusing if the user
#   entered "cancel" in the input field and hit the Write button. In the case
#   above the Cancel button should probably return something like "!@#$%^&",
#   or something else that the user would never normally enter.
#
#   A "default" button may be designated by enclosing the text in ()'s.
#   Pressing the Return or keypad Enter keys will return that button's value.
#   The Cancel button is the default button in this example.
#
#   A caller must clear, or may set MYDAnswerVar to clear a previous
#   call's entry or to provide a default value for the input field before
#   calling formMYD().
#
#   To bring up a "splash dialog" for messages like "Working..." use
#
#       formMYD(Root, (), "", "", "", "Working...")
#
#   Call formMYDReturn to get rid of the dialog:
#
#       formMYDReturn("")
#
#   CenterX and CenterY can be used to position the dialog box when there is
#   no Parent if they are set to something other than 0 and 0.
#
#   Width may be set to something other than 0 to not use the default message
#   width.
#
#   Adding a length and text to the end of a button definition like below will
#   cause a ToolTip item to be created for that button.
#       ("Stop", LEFT, "stop", 30, "Click this to stop the program.")
#
#   This is REALLY kinda kludgy, but there's already a lot of arguments...
#      The normal font will be PROGPropFont.
#      If the Msg1 value begins "|" then PROGMonoFont.
#      Starts with "}" will be PROGOrigPropFont.
#      Starts with "]" will be PROGOrigMonoFont.
#
#   A secret Shift-Control-Button-1 click on the main message Label will
#   return the string "woohoo" which can be used to exit a while-loop of
#   some kind to get the dialog box to keep the program held in place until
#   someone knows the secret to get the program to continue.
MYDFrame = None
MYDLabel = None
MYDAnswerVar = StringVar()

def formMYD(Parent, Clicks, Close, C, Title, Msg1, Msg2 = "", Bell = 0, \
        CenterX = 0, CenterY = 0, Width = 0):
    global MYDFrame
    global MYDLabel
    MonoFont = False
    if Parent != None:
# Allow either way of passing the parent.
        if isinstance(Parent, basestring) == True:
            Parent = PROGFrm[Parent]
# Without this update() sometimes when running a program through ssh everyone
# loses track of where the parent is and the dialog box ends up at 0,0.
# It's possible for this to fail if the program is being stopped in a funny
# way (like with a ^C over an ssh connection, etc.).
        try:
            Parent.update()
        except:
            pass
    TheFont = PROGPropFont
    MonoFont = False
    if Msg1.startswith("|"):
        Msg1 = Msg1[1:]
        TheFont = PROGMonoFont
        MonoFont = True
    if Msg1.startswith("}"):
        Msg1 = Msg1[1:]
        TheFont = PROGOrigPropFont
        MonoFont = False
    if Msg1.startswith("]"):
        Msg1 = Msg1[1:]
        TheFont = PROGOrigMonoFont
        MonoFont = True
    LFrm = MYDFrame = Toplevel(Parent)
    LFrm.withdraw()
    LFrm.resizable(0, 0)
    LFrm.protocol("WM_DELETE_WINDOW", Command(formMYDReturn, Close))
# A number shows up in the title bar if you do .title(""), and if you don't
# set the title it ends up with the program name in it.
    if Title == "":
        Title = " "
    LFrm.title(Title)
    LFrm.iconname(Title)
# Gets rid of some of the extra title bar buttons.
    LFrm.transient(Parent)
    LFrm.bind("<Visibility>", formMYDStay)
    if C != "":
        LFrm.configure(bg = Clr[C[0]])
# Break up the incoming message about every 50 characters or whatever Width is
# set to.
    if Width == 0:
        Width = 50
    if len(Msg1) > Width:
        Count = 0
        Mssg = ""
        for c in Msg1:
            if Count == 0 and c == " ":
                continue
            if Count > Width and c == " ":
                Mssg += "\n"
                Count = 0
                continue
            if c == "\n":
                Mssg += c
                Count = 0
                continue
            Count += 1
            Mssg += c
        Msg1 = Mssg
# This is an extra line that gets added to the message after a blank line.
    if Msg2 != "":
        if len(Msg2) > Width:
            Count = 0
            Mssg = ""
            for c in Msg2:
                if Count == 0 and c == " ":
                    continue
                if Count > Width and c == " ":
                    Mssg += "\n"
                    Count = 0
                    continue
                if c == "\n":
                    Mssg += c
                    Count = 0
                    continue
                Count += 1
                Mssg += c
            Msg1 += "\n\n"+Mssg
        else:
            Msg1 += "\n\n"+Msg2
    if C == "":
        if MonoFont == False:
            MYDLabel = Label(LFrm, text = Msg1, bd = 20, font = TheFont)
        else:
            MYDLabel = Label(LFrm, text = Msg1, bd = 20, font = TheFont, \
                    justify = LEFT)
        MYDLabel.pack(side = TOP)
        Sub = Frame(LFrm)
    else:
        if MonoFont == False:
            MYDLabel = Label(LFrm, text = Msg1, bd = 20, bg = Clr[C[0]], \
                    fg = Clr[C[1]], font = TheFont)
        else:
            MYDLabel = Label(LFrm, text = Msg1, bd = 20, bg = Clr[C[0]], \
                    fg = Clr[C[1]], font = TheFont, justify = LEFT)
        MYDLabel.pack(side = TOP)
        Sub = Frame(LFrm, bg = Clr[C[0]])
    MYDLabel.bind("<Shift-Control-Button-1>", Command(formMYDReturn, "woohoo"))
    One = False
    InputField = False
    for Click in Clicks:
        if Click[0].startswith("Input"):
            InputEnt = Entry(LFrm, textvariable = MYDAnswerVar, \
                    width = intt(Click[0][5:]))
            InputEnt.pack(side = TOP, padx = 10, pady = 10)
# So we know to do the focus_set at the end.
            InputField = True
            continue
        if One == True:
            if C == "":
                Label(Sub, text = " ").pack(side = LEFT)
            else:
                Label(Sub, text = " ", bg = Clr[C[0]]).pack(side = LEFT)
        But = BButton(Sub, text = Click[0], command = Command(formMYDReturn, \
                Click[2]))
        if Click[0].startswith("Clear") or Click[0].startswith("(Clear"):
            But.configure(fg = Clr["U"], activeforeground = Clr["U"])
        elif Click[0].startswith("Close") or Click[0].startswith("(Close"):
            But.configure(fg = Clr["R"], activeforeground = Clr["R"])
        But.pack(side = Click[1])
# Check to see if there is ToolTip text.
        try:
            ToolTip(But, Click[3], Click[4])
        except:
            pass
        if Click[0].startswith("(") and Click[0].endswith(")"):
            LFrm.bind("<Return>", Command(formMYDReturn, Click[2]))
            LFrm.bind("<KP_Enter>", Command(formMYDReturn, Click[2]))
        if Click[1] != TOP:
            One = True
    Sub.pack(side = TOP, padx = 3, pady = 3)
    center(Parent, LFrm, "C", "I", True, CenterX, CenterY)
# If the user clicks to dismiss the window before any one of these things get
# taken care of then there will be touble. This may only happen when the user
# is running the program over a network and not on the local machine. It has
# something to do with changes made to the beep() routine which fixed a
# problem of occasional missing beeps.
    try:
        LFrm.focus_set()
        LFrm.grab_set()
        if InputField == True:
            InputEnt.focus_set()
            InputEnt.icursor(END)
        if Bell != 0:
            beep(Bell)
# Everything will pause here until one of the buttons are pressed if there are
# any, then the box will be destroyed, but the value will still be returned.
# since it was saved in a "global".
        if len(Clicks) != 0:
            LFrm.wait_window()
    except:
        pass
# At least do this much cleaning for the caller.
    MYDAnswerVar.set(MYDAnswerVar.get().strip())
    return MYDAnswerVar.get()
######################################
# BEGIN: formMYDReturn(What, e = None)
# FUNC:formMYDReturn():2008.145
def formMYDReturn(What, e = None):
# If What is "input" just leave whatever is in the var in there.
    global MYDFrame
    if What != "input":
        MYDAnswerVar.set(What)
    MYDAnswerVar.set(MYDAnswerVar.get().strip())
    MYDFrame.destroy()
    MYDFrame = None
    updateMe(0)
    return
############################
# BEGIN: formMYDMsg(Message)
# FUNC:formMYDMsg():2008.012
def formMYDMsg(Message):
    global MYDLabel
    MYDLabel.config(text = Message)
    updateMe(0)
    return
##############################
# BEGIN: formMYDStay(e = None)
# FUNC:formMYDStay():2010.257
def formMYDStay(e = None):
# The user may dismiss the dialog box before these get a chance to do their
# thing.
    try:
        MYDFrame.unbind("<Visibility>")
        MYDFrame.focus_set()
        MYDFrame.update()
        MYDFrame.lift()
        MYDFrame.bind("<Visibility>", formMYDStay)
    except TclError:
        pass
    return
# END: formMYD




######################################################################
# BEGIN: formMYDF(Parent, Mode, Title, StartDir, StartFile, Mssg = "",
#                EndsWith = "", SameCase = True, CompFs = True, \
#                DePrefix = "", ReturnEmpty = False)
# LIB:formMYDF():2013.273
# NEEDS: PROGMsgsDirVar, PROGDataDirVar, PROGWorkDirVar if anyone tries to
#        use the Default codes in Mode.
#   Mode = 0 = allow picking a file
#          1 = just allow picking directories
#          2 = allow picking and making directories only
#          3 = pick/save directories and files (the works)
#          4 = pick multiple files/change dirs
#          5 = enter/pick a file, but not change directory
#   Mode = A second character that specifies one of the "main" directories
#          that can be selected using a "Default" button.
#          D = Main Data Directory
#          W = Main Work Directory
#          M = Main Messages Directory
#   Mssg = A message that can be displayed at the top of the form. It's a
#          Label, so \n's should be put in the passed Mssg string.
#   EndsWith = The module will only display files ending with EndsWith, the
#              entered filename's case will be matched with the case of
#              EndsWith (IF it is all one case or another). EndsWith may be
#              a passed string of file extensions seperated by commas. EndsWith
#              will be added to the entered filename if it is not there before
#              returning, but only if there is one extension passed.
#   SameCase = If True then the case of the filename must match the case of
#              the EndsWith items.
#   CompFs = If True then directory and file completion with the Tab key are
#            set up.
#   DePrefix = If not "" then only the files starting with DePrefix will be
#              loaded and the DePrefix will be removed.
#   ReturnEmpty = If True it allows clearing the file name field and clicking
#                 the OK button, instead of complaining that no file name was
#                 entered.
#   Tabbing in the directory field is supported.
MYDFFrame = None
MYDFModeVar = StringVar()
MYDFDirVar = StringVar()
MYDFFiles = None
MYDFDirField = None
MYDFFileVar = StringVar()
MYDFEndsWithVar = StringVar()
MYDFAnswerVar = StringVar()
MYDFHiddenCVar = IntVar()
MYDFSameCase = True
MYDFDePrefix = ""
MYDFReturnEmpty = False

def formMYDF(Parent, Mode, Title, StartDir, StartFile, Mssg = "", \
        EndsWith = "", SameCase = True, CompFs = True, DePrefix = "", \
        ReturnEmpty = False):
    global MYDFFrame
    global MYDFFiles
    global MYDFDirField
    global MYDFSameCase
    global MYDFDePrefix
    global MYDFReturnEmpty
    if isinstance(Parent, basestring):
        Parent = PROGFrm[Parent]
    MYDFModeVar.set(str(Mode))
    MYDFEndsWithVar.set(EndsWith)
    MYDFSameCase = SameCase
    MYDFDePrefix = DePrefix
    MYDFReturnEmpty = ReturnEmpty
# Without this update() sometimes when running a program through ssh everyone
# loses track of where the parent is and the dialog box ends up at 0,0.
# It's possible for this to fail if the program is being stopped in a funny
# way (like with a ^C over an ssh connection, etc.).
    try:
        Parent.update()
    except:
        pass
    LFrm = MYDFFrame = Toplevel(Parent)
    LFrm.withdraw()
    LFrm.protocol("WM_DELETE_WINDOW", Command(formMYDFReturn, None))
    LFrm.bind("<Button-1>", Command(setMsg, "MYDF", "", ""))
    LFrm.title(Title)
    LFrm.iconname("PickDF")
    LFrm.bind("<Visibility>", formMYDFStay)
    Sub = Frame(LFrm)
# The incoming Mode may be something like "1W". There are special versions of
# intt() out there that don't convert the passed item to a string first, so do
# that here.
    ModeI = intt(str(Mode))
    if Mssg != "":
        Label(Sub, text = Mssg).pack(side = TOP)
    if ModeI != 5:
        BButton(Sub, text = "Up", command = formMYDFUp).pack(side = LEFT)
        LLb = Label(Sub, text = ":=")
        LLb.pack(side = LEFT)
        ToolTip(LLb, 35, \
                "[List Files] Press the Return key to list the files in the entered directory after editing the directory name.")
        LEnt = MYDFDirField = Entry(Sub, textvariable = MYDFDirVar, width = 65)
        LEnt.pack(side = LEFT, fill = X, expand = YES)
        if CompFs == True:
            LEnt.bind("<FocusIn>", Command(formMYDFCompFsTabOff, LFrm))
            LEnt.bind("<FocusOut>", Command(formMYDFCompFsTabOn, LFrm))
            LEnt.bind("<Key-Tab>", Command(formMYDFCompFs, MYDFDirVar, None))
        LEnt.bind("<Return>", formMYDFFillFiles)
        LEnt.bind("<KP_Enter>", formMYDFFillFiles)
# KeyPress clears the field when typing. KeyRelease clears the field after it
# has been filled in.
        LEnt.bind("<KeyPress>", formMYDFClearFiles)
        if ModeI == 2 or ModeI == 3:
            But = BButton(Sub, text = "Mkdir", command = formMYDFNew)
            But.pack(side = LEFT)
            ToolTip(But, 25, \
                    "Add the name of the new directory to the end of the current contents of the entry field and click this button to create the new directory.")
# Just show the current directory.
    elif ModeI == 5:
        MYDFDirField = Entry(Sub, textvariable = MYDFDirVar, \
                state = DISABLED, width = 65)
        MYDFDirField.pack(side = LEFT, fill = X, expand = YES)
    Sub.pack(side = TOP, fill = X)
    Sub = Frame(LFrm)
    if Mode == 4:
        LLb = MYDFFiles = Listbox(Sub, relief = SUNKEN, bd = 2, height = 15, \
                selectmode = EXTENDED)
    else:
        LLb = MYDFFiles = Listbox(Sub, relief = SUNKEN, bd = 2, height = 15, \
                selectmode = SINGLE)
    LLb.pack(side = LEFT, expand = YES, fill = BOTH)
    LLb.bind("<ButtonRelease-1>", formMYDFPicked)
    Scroll = Scrollbar(Sub, command = LLb.yview)
    Scroll.pack(side = RIGHT, fill = Y)
    LLb.configure(yscrollcommand = Scroll.set)
    Sub.pack(side = TOP, expand = YES, fill = BOTH)
# The user can type in the filename.
    if Mode == 0 or Mode == 3 or Mode == 5:
        Sub = Frame(LFrm)
        Label(Sub, text = "Filename:=").pack(side = LEFT)
        LEnt = Entry(Sub, textvariable = MYDFFileVar, width = 65)
        LEnt.pack(side = LEFT, fill = X, expand = YES)
        if CompFs == True:
            LEnt.bind("<FocusIn>", Command(formMYDFCompFsTabOff, LFrm))
            LEnt.bind("<FocusOut>", Command(formMYDFCompFsTabOn, LFrm))
            LEnt.bind("<Key-Tab>", Command(formMYDFCompFs, None, MYDFFileVar))
        LEnt.bind("<Return>", Command(formMYDFReturn, ""))
        LEnt.bind("<KP_Enter>", Command(formMYDFReturn, ""))
        Sub.pack(side = TOP, fill = X, padx = 3)
    Sub = Frame(LFrm)
# Create a Default button and tooltip if the Mode says so.
    if isinstance(Mode, basestring):
        if Mode.find("D") != -1:
            LBu = BButton(Sub, text = "Default", \
                    command = Command(formMYDFDefault, "D"))
            LBu.pack(side = LEFT)
            ToolTip(LBu, 35, "Set to Main Data Directory")
            Label(Sub, text = " ").pack(side = LEFT)
        elif Mode.find("W") != -1:
            LBu = BButton(Sub, text = "Default", \
                    command = Command(formMYDFDefault, "W"))
            LBu.pack(side = LEFT)
            ToolTip(LBu, 35, "Set to Main Work Directory")
            Label(Sub, text = " ").pack(side = LEFT)
        elif Mode.find("M") != -1:
            LBu = BButton(Sub, text = "Default", \
                    command = Command(formMYDFDefault, "M"))
            LBu.pack(side = LEFT)
            ToolTip(LBu, 35, "Set to Main Messages Directory")
            Label(Sub, text = " ").pack(side = LEFT)
    BButton(Sub, text = "OK", command = Command(formMYDFReturn, \
            "")).pack(side = LEFT)
    Label(Sub, text = " ").pack(side = LEFT)
    BButton(Sub, text = "Cancel", \
            command = Command(formMYDFReturn, None)).pack(side = LEFT)
    Label(Sub, text = " ").pack(side = LEFT)
    LCb = Checkbutton(Sub, text = "Show hidden\nfiles", \
            variable = MYDFHiddenCVar, command = formMYDFFillFiles)
    LCb.pack(side = LEFT)
    ToolTip(LCb, 30, "Select this to show hidden/system files in the list.")
    Sub.pack(side = TOP, pady = 3)
    PROGMsg["MYDF"] = Text(LFrm, font = PROGPropFont, height = 1, \
            width = 1, highlightthickness = 0, insertwidth = 0, takefocus = 0)
    PROGMsg["MYDF"].pack(side = TOP, expand = YES, fill = X)
    if len(StartDir) == 0:
        StartDir = sep
    if StartDir.endswith(sep) == False:
        StartDir += sep
    MYDFDirVar.set(StartDir)
    Ret = formMYDFFillFiles()
    if Ret == True and (Mode == 0 or Mode == 3 or Mode == 5):
        MYDFFileVar.set(StartFile)
    center(Parent, LFrm, "C", "I", True)
    MYDFFrame.grab_set()
# Set the cursor for the user.
    if Mode == 0 or Mode == 3 or Mode == 5:
        LEnt.focus_set()
        LEnt.icursor(END)
# Everything will pause here until one of the buttons are pressed, then the
# box will be destroyed, but the value will still be returned since it was
# saved in a "global".
    MYDFFrame.wait_window()
    return MYDFAnswerVar.get()
#####################################
# BEGIN: formMYDFClearFiles(e = None)
# FUNC:formMYDFClearFiles():2013.207
def formMYDFClearFiles(e = None):
    if MYDFFiles.size() > 0:
        MYDFFiles.delete(0, END)
    return
#####################################################
# BEGIN: formMYDFFillFiles(FocusSet = True, e = None)
# FUNC:formMYDFFillFiles():2013.273
#   Fills the Listbox with a list of directories and files, or with drive
#   letters if in Windows (and the directory field is just sep).
def formMYDFFillFiles(FocusSet = True, e = None):
# Some directoryies may have a lot of files in them which could make listdir()
# take a long time, so do this.
    setMsg("MYDF", "CB", "Reading...")
    Mode = intt(MYDFModeVar.get())
# Make sure whatever is in the directory field ends, or is at least a
# separator.
    if len(MYDFDirVar.get()) == 0:
        MYDFDirVar.set(sep)
    if MYDFDirVar.get().endswith(sep) == False:
        MYDFDirVar.set(MYDFDirVar.get()+sep)
    Dir = MYDFDirVar.get()
    if PROGSystem == "dar" or PROGSystem == "lin" or PROGSystem == "sun" or \
            (PROGSystem == "win" and Dir != sep):
        try:
            Files = listdir(Dir)
        except:
            MYDFFileVar.set("")
            setMsg("MYDF", "YB", " There is no such directory.", 2)
            return False
        MYDFDirField.icursor(END)
        MYDFFiles.delete(0, END)
        Files.sort(formMYDFCmp)
# Always add this to the top of the list unless we are not supposed to.
        if Mode != 5:
            MYDFFiles.insert(END, " .."+sep)
# To show or not to show.
        ShowHidden = MYDFHiddenCVar.get()
# Do the directories first.
        for File in Files:
# The DePrefix stuff is only applied to the files (below).
            if ShowHidden == 0:
# FINISHME - This may need/want to be system dependent at some point (i.e. more
# than just files that start with a . or _ in different OSs).
                if File.startswith(".") or File.startswith("_"):
                    continue
            if isdir(Dir+sep+File):
                MYDFFiles.insert(END, " "+File+sep)
# Check to see if we are going to be filtering.
        EndsWith = ""
        if MYDFEndsWithVar.get() != "":
            EndsWith = MYDFEndsWithVar.get()
        EndsWithParts = EndsWith.split(",")
        Found = False
        for File in Files:
# DeFile will be used for what the user ends up seeing, and File will be used
# internally.
            DeFile = File
            if MYDFDePrefix != "":
                if File.startswith(MYDFDePrefix) == False:
                    continue
                DeFile = File[len(MYDFDePrefix):]
            if ShowHidden == 0:
                if DeFile.startswith(".") or DeFile.startswith("_"):
                    continue
            if isdir(Dir+sep+File) == False:
                if EndsWith == "":
# We only want to see the file sizes when we are looking for files.
                    if Mode == 0 or Mode == 3 or Mode == 5:
# Trying to follow links will trip this so just show them.
                        try:
                            MYDFFiles.insert(END, " %s  (bytes: %s)"%(DeFile, \
                                    fmti(getsize(Dir+sep+File))))
                        except OSError:
                            MYDFFiles.insert(END, " %s  (a link?)"%DeFile)
                    else:
                        MYDFFiles.insert(END, " %s"%DeFile)
                    Found += 1
                else:
                    for EndsWithPart in EndsWithParts:
                        if File.endswith(EndsWithPart):
                            if Mode == 0 or Mode == 3 or Mode == 5:
                                try:
                                    MYDFFiles.insert(END, " %s  (bytes: %s)"% \
                                            (DeFile, fmti(getsize(Dir+sep+ \
                                            File))))
                                except OSError:
                                    MYDFFiles.insert(END, " %s  (a link?)"% \
                                            DeFile)
                            else:
                                MYDFFiles.insert(END, " %s"%DeFile)
                            Found += 1
                            break
        if Mode == 0 or Mode == 3 or Mode == 5:
            setMsg("MYDF", "", "%d %s found."%(Found, sP(Found, ("file", \
                    "files"))))
        else:
            setMsg("MYDF")
    elif PROGSystem == "win" and Dir == sep:
        MYDFFiles.delete(0, END)
# This loop takes a while to run.
        updateMe(0)
        Found = 0
        for Drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            Drivespec = "%s:%s"%(Drive, sep)
            if exists(Drivespec):
                MYDFFiles.insert(END, Drivespec)
                Found += 1
        if Mode == 0 or Mode == 3 or Mode == 5:
            setMsg("MYDF", "", "%d %s found."%(Found, sP(Found, ("drive", \
                    "drives"))))
        else:
            setMsg("MYDF")
    if FocusSet == True:
        PROGMsg["MYDF"].focus_set()
    return True
###############################
# BEGIN: formMYDFDefault(Which)
# FUNC:formMYDFDefault():2012.343
def formMYDFDefault(Which):
    if Which == "D":
        MYDFDirVar.set(PROGDataDirVar.get())
    elif Which == "W":
        MYDFDirVar.set(PROGWorkDirVar.get())
    elif Which == "M":
        MYDFDirVar.set(PROGMsgsDirVar.get())
    formMYDFFillFiles()
    return
##########################
# BEGIN: formMYDFCmp(x, y)
# FUNC:formMYDFCmp():2009.171
#   So the directory listings are sorted in alphabetical and not ASCII order.
def formMYDFCmp(x, y):
    x = x.lower()
    y = y.lower()
    if x < y:
        return -1
    if x == y:
        return 0
    if x > y:
        return 1
######################
# BEGIN: formMYDFNew()
# FUNC:formMYDFNew():2013.207
def formMYDFNew():
    setMsg("MYDF")
# Make sure whatever is in the directory field ends in a separator.
    if len(MYDFDirVar.get()) == 0:
        MYDFDirVar.set(sep)
    if MYDFDirVar.get().endswith(sep) == False:
        MYDFDirVar.set(MYDFDirVar.get()+sep)
    Dir = MYDFDirVar.get()
    if exists(Dir):
        setMsg("MYDF", "YB", " Directory already exists.", 2)
        return
    try:
        makedirs(Dir)
        formMYDFFillFiles()
        setMsg("MYDF", "GB", " New directory made.", 1)
    except Exception, e:
# The system messages can be a bit cryptic and/or long, so simplifiy them here.
        if str(e).find("ermission") != -1:
            setMsg("MYDF", "RW", " Permission denied.", 2)
        else:
            setMsg("MYDF", "RW", " "+str(e), 2)
        return
    return
#################################
# BEGIN: formMYDFPicked(e = None)
# FUNC:formMYDFPicked():2013.207
def formMYDFPicked(e = None):
# This is just to get the focus off of the entry field if it was there since
# the user is now clicking on things.
    PROGMsg["MYDF"].focus_set()
    setMsg("MYDF")
    Mode = intt(MYDFModeVar.get())
# Make sure whatever is in the directory field ends with a separator.
    if len(MYDFDirVar.get()) == 0:
        MYDFDirVar.set(sep)
    if MYDFDirVar.get().endswith(sep) == False:
        MYDFDirVar.set(MYDFDirVar.get()+sep)
    Dir = MYDFDirVar.get()
# Otherwise the selected stuff will just keep piling up.
    if Mode == 4:
        MYDFFileVar.set("")
# There could be multiple files selected. Go through all of them and see if any
# of them will make us change directories.
    Sel = MYDFFiles.curselection()
    SelectedFiles = ""
    for Index in Sel:
# If the user is not right on the money this will sometimes trip.
        try:
            Selected = MYDFFiles.get(Index).strip()
        except TclError:
            beep(1)
            return
        if Selected == ".."+sep:
            Parts = Dir.split(sep)
# If there are only two Parts then we have hit the top of the directory tree.
            NewDir = ""
            if len(Parts) == 2 and Parts[1] == "":
                if PROGSystem == "dar" or PROGSystem == "lin" or \
                        PROGSystem == "sun":
                    NewDir = Parts[0]+sep
                elif PROGSystem == "win":
                    NewDir = sep
            else:
                for i in xrange(0, len(Parts)-2):
                    NewDir += Parts[i]+sep
# Insurance.
            if len(NewDir) == 0:
                NewDir = sep
            MYDFDirVar.set(NewDir)
            formMYDFFillFiles()
            return
# We have to do a Texas Two-Step here to get everyone in the right frame of
# mind. If Dir is just sep then we have just clicked on a directory and not
# on a file, so make it look like the former.
        if PROGSystem == "win" and Dir == sep:
            Dir = Selected
            Selected = ""
        if isdir(Dir+Selected):
            MYDFDirVar.set(Dir+Selected)
            formMYDFFillFiles()
            return
        if Mode == 1 or Mode == 2:
            setMsg("MYDF", "YB", "That is not a directory.", 2)
            MYDFFiles.selection_clear(0, END)
            return
# Must have clicked on a file with byte size and that must be allowed.
        if Selected.find("  (") != -1:
            Selected = Selected[:Selected.index("  (")]
# Build the whole path for the multiple file mode.
        if Mode == 4:
            if SelectedFiles == "":
                SelectedFiles = Dir+Selected
            else:
# An * should be a safe separator, right?
                SelectedFiles += "*"+Dir+Selected
        else:
# This should end up the only file.
            SelectedFiles = Selected
    MYDFFileVar.set(SelectedFiles)
    return
#############################
# BEGIN: formMYDFUp(e = None)
# FUNC:formMYDFUp():2013.207
def formMYDFUp(e = None):
# This is just to get the focus off of the entry field if it was there.
    PROGMsg["MYDF"].focus_set()
    setMsg("MYDF")
    Dir = MYDFDirVar.get()
    Parts = Dir.split(sep)
# If there are only two Parts then we have hit the top of the directory tree.
    NewDir = ""
    if len(Parts) == 2 and Parts[1] == "":
        if PROGSystem == "dar" or PROGSystem == "lin" or PROGSystem == "sun":
            NewDir = Parts[0]+sep
        elif PROGSystem == "win":
            NewDir = sep
    else:
        for i in xrange(0, len(Parts)-2):
            NewDir += Parts[i]+sep
# Insurance.
    if len(NewDir) == 0:
        NewDir = sep
    MYDFDirVar.set(NewDir)
    formMYDFFillFiles()
    return
#########################################
# BEGIN: formMYDFReturn(Return, e = None)
# FUNC:formMYDFReturn():2013.207
def formMYDFReturn(Return, e = None):
# This update keeps the "OK" button from staying pushed in when there is a lot
# to do before returning.
    MYDFFrame.update()
    setMsg("MYDF")
    Mode = intt(MYDFModeVar.get())
    if Return == None:
        MYDFAnswerVar.set("")
    elif Return != "":
        MYDFAnswerVar.set(Return)
    elif Return == "":
# The programmer is responsible for making sure this is used correctly.
        if MYDFDirVar.get() == "" and MYDFReturnEmpty == True:
            MYDFAnswerVar.set("")
        else:
            if Mode == 1 or Mode == 2:
                if MYDFDirVar.get() == "":
                    setMsg("MYDF", "YB", "There is no directory name.", 2)
                    return
                if MYDFDirVar.get().endswith(sep) == False:
                    MYDFDirVar.set(MYDFDirVar.get()+sep)
                MYDFAnswerVar.set(MYDFDirVar.get())
            elif Mode == 0 or Mode == 3 or Mode == 5:
# Just in case the user tries to pull a fast one. Mode 5 above is just for
# completness since the directory must be right (it can't be changed by the
# user).
                if MYDFDirVar.get() == "":
                    setMsg("MYDF", "YB", "There is no directory name.", 2)
                    return
# What was the point of coming here??
                if MYDFFileVar.get() == "":
                    setMsg("MYDF", "YB", "No filename has been entered.", 2)
                    return
                if MYDFEndsWithVar.get() != "":
# I'm sure this may come back to haunt US someday, but make sure that the case
# of the entered filename matches the passed 'extension'.  My programs, as a
# general rule, are written to handle all upper or lowercase file names, but
# not mixed. Of course, on some operating systems it won't make any difference.
                    if MYDFSameCase == True:
                        if MYDFEndsWithVar.get().isupper():
                            if MYDFFileVar.get().isupper() == False:
                                setMsg("MYDF", "YB", \
                              "Filename needs to be all uppercase letters.", 2)
                                return
                        elif MYDFEndsWithVar.get().islower():
                            if MYDFFileVar.get().islower() == False:
                                setMsg("MYDF", "YB", \
                              "Filename needs to be all lowercase letters.", 2)
                                return
# If the user didn't put the 'extension' on the file add it so the caller
# won't have to do it, unless the caller passed multiple extensions, then don't
# do anything.
                    if MYDFEndsWithVar.get().find(",") == -1:
                        if MYDFFileVar.get().endswith( \
                                MYDFEndsWithVar.get()) == False:
                            MYDFFileVar.set(MYDFFileVar.get()+ \
                                MYDFEndsWithVar.get())
                MYDFAnswerVar.set(MYDFDirVar.get()+MYDFFileVar.get())
            elif Mode == 4:
                MYDFAnswerVar.set(MYDFFileVar.get())
    MYDFFrame.destroy()
    updateMe(0)
    return
##################################################
# BEGIN: formMYDFCompFs(DirVar, FileVar, e = None)
# FUNC:formMYDFCompFs():2013.207
#   Attempts to complete the directory or file name in an Entry field using
#   the Tab key.
#   - If DirVar is set to a field's StringVar and FileVar is None then the
#     routine only looks for directories and leaves completion results in
#     DirVar.
#   - If FileVar is set to a field's StringVar and DirVar is None then the
#     routine tries to complete a file name using the files loaded into the
#     file listbox and leaves the results in FileVar.
def formMYDFCompFs(DirVar, FileVar, e = None):
    setMsg("MYDF")
# ---- Directories...looking to find you.
    if DirVar != None:
        Dir = dirname(DirVar.get())
# This is a slight gotchya. If the field is empty that might mean that the user
# means "/" should be the starting point. If it is they will have to enter the
# / since if we are on Windows I'd have no idea what the default should be.
        if len(Dir) == 0:
            beep(2)
            return
        if Dir.endswith(sep) == False:
            Dir += sep
# Now get what must be a partial directory name, treat it as a file name, but
# then only allow the result of everything to be a directory.
        PartialFile = basename(DirVar.get())
        if len(PartialFile) == 0:
            beep(2)
            return
        PartialFile += "*"
        Files = listdir(Dir)
        Matched = []
        for File in Files:
            if fnmatch(File, PartialFile):
                Matched.append(File)
        if len(Matched) == 0:
            beep(2)
            return
        elif len(Matched) == 1:
            Dir = Dir+Matched[0]
# If whatever matched is not a directory then just beep and return, otherwise
# make it look like a directory and put it into the field.
            if isdir(Dir) == False:
                beep(2)
                return
            if Dir.endswith(sep) == False:
                Dir += sep
            DirVar.set(Dir)
            e.widget.icursor(END)
            formMYDFFillFiles(False)
            return
        else:
# Get the max number of characters that matched and put the partial directory
# path into the Var. If Dir+PartialDir is really the directory the user wants
# they will have to add the sep themselves since with multiple matches I won't
# know what to do. Consider DIR DIR2 DIR3 with a formMYDFMaxMatch() return of
# DIR. The directory DIR would always be selected and set as the path which
# may not be what the user wanted. Now this could cause trouble downstream
# since I'm leaving a path in the field without a trailing sep (everything
# tries to avoid doing that), so the caller will have to worry about that.
            PartialDir = formMYDFMaxMatch(Matched)
            DirVar.set(Dir+PartialDir)
            e.widget.icursor(END)
            beep(1)
    elif FileVar != None:
        PartialFile = FileVar.get().strip()
        if len(PartialFile) == 0:
            beep(1)
            return
        Files = MYDFFiles.get(0, END)
        Index = 0
        Found = 0
        for Sel in xrange(0, len(Files)):
# .strip() off the leading space.
            File = Files[Sel].strip()
            if File.startswith(PartialFile):
                Index = Sel
                Found += 1
        if Found == 0:
            beep(1)
            return
        elif Found > 1:
            MYDFFiles.see(Index)
            beep(1)
            return
        MYDFFiles.see(Index)
        File = Files[Index].strip()
# File contains the matching line from the Listbox, but it should have an
# (x bytes) message at the end. Get rid of that.
        if File.find("  (") != -1:
            File = File[:File.index("  (")]
        FileVar.set(File)
        e.widget.icursor(END)
    return
#############################################
# BEGIN: formMYDFCompFsTabOff(LFrm, e = None)
# FUNC:formMYDFCompFsTabOff():2010.225
def formMYDFCompFsTabOff(LFrm, e = None):
    LFrm.bind("<Key-Tab>", formMYDFNullCall)
    return
############################################
# BEGIN: formMYDFCompFsTabOn(LFrm, e = None)
# FUNC:formMYDFCompFsTabOn():2010.225
def formMYDFCompFsTabOn(LFrm, e = None):
    LFrm.unbind("<Key-Tab>")
    return
##################################
# BEGIN: formMYDFMaxMatch(TheList)
# FUNC:formMYDFMaxMatch():2010.056
#   Goes through the items in TheList (should be str's) and returns the string
#   that matches the start of all of the items.
#   This is the same as the library function maxMatch().
def formMYDFMaxMatch(TheList):
# This should be the only special case. What is the sound of one thing matching
# itself?
    if len(TheList) == 1:
        return TheList[0]
    Accum = ""
    CharIndex = 0
# If anything goes wrong just return whatever we've accumulated. This will end
# by no items being in TheList or one of the items running out of characters
# (the try) or by the TargetChar not matching a character from one of the
# items (the raise).
    try:
        while 1:
            TargetChar = TheList[0][CharIndex]
            for ItemIndex in xrange(1, len(TheList)):
                if TargetChar != TheList[ItemIndex][CharIndex]:
                    raise Exception
            Accum += TargetChar
            CharIndex += 1
    except Exception:
        pass
    return Accum
###############################
# BEGIN: formMYDFStay(e = None)
# FUNC:formMYDFStay():2010.260
def formMYDFStay(e = None):
# The window may already be gone by this point so try.
    try:
        MYDFFrame.unbind("<Visibility>")
        MYDFFrame.focus_set()
        MYDFFrame.update()
        MYDFFrame.lift()
        MYDFFrame.bind("<Visibility>", formMYDFStay)
    except TclError:
        pass
    return
###################################
# BEGIN: formMYDFNullCall(e = None)
# FUNC:formMYDFNullCall():2013.037
def formMYDFNullCall(e = None):
    return "break"
# END: formMYDF




####################################################################
# BEGIN: formMYDT(Parent, Clicks, Close, BgFg, Title, Wrap, TheText)
# LIB:formMYDT():2013.135
#   This is a general purpose dialog box that just has one big Text() field to
#   dump TheText to.
MYDTFrame = None
MYDTText = None
MYDTAnswerVar = StringVar()
# FINISHME - maybe add autosizing and things like that.

def formMYDT(Parent, Clicks, Close, BgFg, Title, Wrap, TheText):
    global MYDTFrame
    global MYDTText
    if Parent != None:
# Allow either way of passing the parent.
        if isinstance(Parent, basestring) == True:
            Parent = PROGFrm[Parent]
# Without this update() sometimes when running a program through ssh everyone
# loses track of where the parent is and the dialog box ends up at 0,0.
# It's possible for this to fail if the program is being stopped in a funny
# way (like with a ^C over an ssh connection, etc.).
        try:
            Parent.update()
        except:
            pass
    TheFont = PROGPropFont
    if TheText[0].startswith("|"):
        TheText = TheText[1:]
        TheFont = PROGMonoFont
    if TheText[0].startswith("}"):
        TheText = TheText[1:]
        TheFont = PROGOrigPropFont
    if TheText[0].startswith("]"):
        TheText = TheText[1:]
        TheFont = PROGOrigMonoFont
    LFrm = MYDTFrame = Toplevel(Parent)
    LFrm.withdraw()
    LFrm.protocol("WM_DELETE_WINDOW", Command(formMYDTReturn, "ok"))
# A number shows up in the title bar if you do .title(""), and if you don't
# set the title it ends up with the program name in it.
    if Title == "":
        Title = " "
    LFrm.title(Title)
    LFrm.iconname(Title)
# Gets rid of some of the extra title bar buttons.
    LFrm.transient(Parent)
    LFrm.bind("<Visibility>", formMYDTStay)
    Sub = Frame(LFrm)
    if BgFg == "":
        BgFg = "WB"
    LTxt = MYDTText = Text(Sub, bg = Clr[BgFg[0]], fg = Clr[BgFg[1]], \
            width = 90, height = 25, wrap = Wrap, font = TheFont, \
            relief = SUNKEN)
    LTxt.pack(side = LEFT, expand = YES, fill = BOTH)
    LSb = Scrollbar(Sub, orient = VERTICAL, command = LTxt.yview)
    LSb.pack(side = RIGHT, fill = Y)
    LTxt.configure(yscrollcommand = LSb.set)
    Sub.pack(side = TOP, expand = YES, fill = BOTH)
    LSb = Scrollbar(LFrm, orient = HORIZONTAL, command = LTxt.xview)
    LSb.pack(side = TOP, fill = X)
    LTxt.configure(xscrollcommand = LSb.set)
    for Line in TheText:
        if Line.startswith("CCBB"):
            Cb = Checkbutton(LTxt, bg = Clr[BgFg[0]], bd = 0, \
                    activebackground = Clr[BgFg[0]], highlightthickness = 0, \
                    cursor = "left_ptr")
            LTxt.window_create(END, window = Cb)
            Line = Line[4:]
        MYDTText.insert(END, Line+"\n")
# Clicks like: (("OK", LEFT, "ok"), ("Close", LEFT, "close"))
    One = False
    Sub = Frame(LFrm)
    for Click in Clicks:
        if One == True:
            Label(Sub, text = " ").pack(side = LEFT)
        But = BButton(Sub, text = Click[0], command = Command(formMYDTReturn, \
                Click[2]))
        if Click[0].startswith("Clear") or Click[0].startswith("(Clear"):
            But.configure(fg = Clr["U"], activeforeground = Clr["U"])
        elif Click[0].startswith("Close") or Click[0].startswith("(Close"):
            But.configure(fg = Clr["R"], activeforeground = Clr["R"])
        But.pack(side = Click[1])
# Check to see if there is ToolTip text.
        try:
            ToolTip(But, Click[3], Click[4])
        except:
            pass
        if Click[0].startswith("(") and Click[0].endswith(")"):
            LFrm.bind("<Return>", Command(formMYDTReturn, Click[2]))
            LFrm.bind("<KP_Enter>", Command(formMYDTReturn, Click[2]))
        if Click[1] != TOP:
            One = True
    Sub.pack(side = TOP, padx = 3, pady = 3)
    center(Parent, LFrm, "C", "I", True)
# If the user clicks to dismiss the window before any one of these things get
# taken care of then there will be trouble. This may only happen when the user
# is running the program over a network and not on the local machine. It has
# something to do with changes made to the beep() routine which fixed a
# problem of occasional missing beeps.
    try:
        LFrm.focus_set()
        LFrm.grab_set()
# Everything will pause here until one of the buttons are pressed if there are
# any, then the box will be destroyed, but the value will still be returned.
# since it was saved in a global.
        if len(Clicks) != 0:
            LFrm.wait_window()
    except:
        pass
    return MYDTAnswerVar.get()
#######################################
# BEGIN: formMYDTReturn(What, e = None)
# FUNC:formMYDReturn():2012.263
def formMYDTReturn(What, e = None):
    MYDTAnswerVar.set(What)
    MYDTFrame.destroy()
    updateMe(0)
    return
###############################
# BEGIN: formMYDTStay(e = None)
# FUNC:formMYDTStay():2010.257
def formMYDTStay(e = None):
# The user may dismiss the dialog box before these get a chance to do their
# thing.
    try:
        MYDTFrame.unbind("<Visibility>")
        MYDTFrame.focus_set()
        MYDTFrame.update()
        MYDTFrame.lift()
        MYDTFrame.bind("<Visibility>", formMYDTStay)
    except TclError:
        pass
    return
# END: formMYDT




##################
# BEGIN: formLOG()
# FUNC:formLOG():2013.171
#   Handles the window that displays the LOG messages in QPLogs.
PROGFrm["LOG"] = None
PROGTxt["LOG"] = None
LOGFindLookForVar = StringVar()
LOGFindLastLookForVar = StringVar()
LOGFindLinesVar = StringVar()
LOGFindIndexVar = IntVar()
LOGFilespecVar  = StringVar()
PROGSetups += ["LOGFindLookForVar", "LOGFilespecVar"]
LOGStopBut = None

def formLOG():
    global QPLogs
    global LOGStopBut
    if PROGFrm["LOG"] != None:
        PROGFrm["LOG"].deiconify()
        LTxt = PROGTxt["LOG"]
    else:
        LFrm = PROGFrm["LOG"] = Toplevel(Root)
        LFrm.withdraw()
        LFrm.protocol("WM_DELETE_WINDOW", Command(closeForm, "LOG"))
        LFrm.title("LOG Messages")
        LFrm.iconname("LOG")
        Sub = Frame(LFrm)
        SSub = Frame(Sub)
        LTxt = PROGTxt["LOG"] = Text(SSub, font = PROGMonoFont, wrap = NONE, \
                width = 95, relief = SUNKEN)
        LTxt.pack(side = LEFT, expand = YES, fill = BOTH)
        LSb = Scrollbar(SSub, orient = VERTICAL, command = LTxt.yview)
        LSb.pack(side = RIGHT, fill = Y)
        LTxt.configure(yscrollcommand = LSb.set)
        SSub.pack(side = TOP, expand = YES, fill = BOTH)
        LSb = Scrollbar(Sub, command = LTxt.xview, orient = HORIZONTAL)
        LSb.pack(side = BOTTOM, fill = X)
        LTxt.configure(xscrollcommand = LSb.set)
        Sub.pack(side = TOP, expand = YES, fill = BOTH, padx = 1, pady = 1)
        Sub = Frame(LFrm)
        labelTip(Sub, "Find:=", LEFT, 30, "[Find]")
        LEnt = Entry(Sub, width = 20, textvariable = LOGFindLookForVar)
        LEnt.pack(side = LEFT)
        LEnt.bind("<Return>", Command(formFind, "LOG", "LOG"))
        LEnt.bind("<KP_Enter>", Command(formFind, "LOG", "LOG"))
        BButton(Sub, text = "Find", command = Command(formFind, \
                "LOG", "LOG")).pack(side = LEFT)
        BButton(Sub, text = "Next", command = Command(formFindNext, \
                "LOG", "LOG")).pack(side = LEFT)
        Label(Sub, text = " ").pack(side = LEFT)
        LOGStopBut = BButton(Sub, text = "Stop", \
                command = Command(formLOGControl, "stop"))
        LOGStopBut.pack(side = LEFT)
        Label(Sub, text = " ").pack(side = LEFT)
        BButton(Sub, text = "Write To File", command = Command(formWrite, \
                "LOG", "LOG", "LOG", "Write LOG Messages", LOGFilespecVar, \
                True)).pack(side = LEFT)
        Label(Sub, text = " ").pack(side = LEFT)
        BButton(Sub, text = "Close", fg = Clr["R"], \
                command = Command(closeForm, "LOG")).pack(side = LEFT)
        Sub.pack(side = TOP, padx = 3, pady = 3)
        PROGMsg["LOG"] = Text(LFrm, font = PROGPropFont, height = 3, \
                wrap = WORD)
        PROGMsg["LOG"].pack(side = TOP, fill = X)
        center(Root, LFrm, "NW", "O", True)
# FINISHME - this is where we need to start changing the library (formHELP in
# this case) functions to handle things like no Work dir. It should fall back
# to the Data dir if PROGWorkDirVar does not exist. (this was PROGWorkDirVar)
    if LOGFilespecVar.get() == "" or \
            exists(dirname(LOGFilespecVar.get())) == False:
        LOGFilespecVar.set(PROGDataDirVar.get()+PROG_NAMELC+"log.txt")
# Clear this so the formFind() routine does the right thing if this form was
# brought up previously.
    LOGFindLinesVar.set("")
    if len(QPLogs) > 2000000:
# Make sure it can be seen.
        showUp("LOG")
        formMYD("LOG", (("(OK)", TOP, "ok"), ), "ok", "YB", "Wow!", \
                "There are more than 2,000,000 LOG messages. This may take quite a while to display. You can use the Stop button if you want to stop early.")
    setMsg("LOG", "CB", "Working...")
    formLOGControl("go")
    LTxt.delete(0.0, END)
    LineCount = 0
    for Line in QPLogs:
        LTxt.insert(END, Line+"\n")
        LineCount += 1
        if LineCount%500000 == 0:
            LOGStopBut.update()
            if LOGRunning == 0:
                formLOGControl("stop")
                break
            setMsg("LOG", "CB", "Working on line %d..."%LineCount)
    setMsg("LOG", "", "%d %s listed."%(LineCount, sP(LineCount, ("line", \
            "lines"))))
    formLOGControl("stopped")
    return
#######################
# BEGIN: formLOGClear()
# FUNC:formLOGClear():2013.047
def formLOGClear():
    if PROGFrm["LOG"] != None:
        PROGTxt["LOG"].delete(0.0, END)
        PROGTxt["LOG"].tag_delete("hilite")
        setMsg("LOG", "", "")
    return
#########################################
# BEGIN: formLOGHilite(Line, HClr = "YB")
# BEGIN:formLOGHilite():2013.050
def formLOGHilite(Line, HClr = "YB"):
    LFrm = PROGFrm["LOG"]
    if LFrm != None:
        LTxt = PROGTxt["LOG"]
        LTxt.tag_delete("hilite")
        LTxt.yview(Line-5)
        LTxt.tag_add("hilite", "%d.0"%Line, "%d.end"%Line)
        LTxt.tag_configure("hilite", background = Clr[HClr[0]], \
                foreground = Clr[HClr[1]])
        LFrm.lift()
        LFrm.deiconify()
    return
##############################
# BEGIN: formLOGMsg(MClr, Msg)
# FUNC:formLOGMsg():2013.047
def formLOGMsg(MClr, Msg):
    if PROGFrm["LOG"] != None:
        setMsg("LOG", MClr, Msg)
    return
###############################
# BEGIN: formLOGControl(Action)
# FUNC:formLOGControl():2012.318
def formLOGControl(Action):
    global LOGRunning
    if Action == "go":
        buttonBG(LOGStopBut, "R", NORMAL)
        LOGRunning = 1
        return
    elif Action == "stop":
        if LOGRunning == 0:
            beep(1)
        else:
            buttonBG(LOGStopBut, "Y", NORMAL)
    elif Action == "stopped":
        buttonBG(LOGStopBut, "D", DISABLED)
    LOGRunning = 0
    return
# END: formLOG




######################
# BEGIN: formLOGSRCH()
# FUNC:formLOGSRCH():2012.325
PROGFrm["LOGSRCH"] = None
LOGSRCHSearchVar = StringVar()
PROGSetups += ["LOGSRCHSearchVar"]

def formLOGSRCH():
    if PROGFrm["LOGSRCH"] != None:
        PROGFrm["LOGSRCH"].deiconify()
        PROGFrm["LOGSRCH"].lift()
        return
# Create the window and put it in the middle of the screen.
    LFrm = PROGFrm["LOGSRCH"] = Toplevel(Root)
    LFrm.withdraw()
    LFrm.title("LOG Search")
    LFrm.protocol("WM_DELETE_WINDOW", Command(closeForm, "LOGSRCH"))
# Where the user will enter the search string.
    LEnt = Entry(LFrm, textvariable = LOGSRCHSearchVar)
    LEnt.pack(side = TOP, fill = X)
    LEnt.bind('<Return>', formLOGSRCHGo)
    LEnt.focus_set()
    LEnt.icursor(END)
# Where the search results will be.
    Sub = Frame(LFrm)
    PROGTxt["LOGSRCH"] = Text(Sub, width = 80, height = 20, wrap = NONE, \
             relief = SUNKEN)
    PROGTxt["LOGSRCH"].pack(side = LEFT, expand = YES, fill = BOTH)
    Scroll = Scrollbar(Sub, orient = VERTICAL, \
            command = PROGTxt["LOGSRCH"].yview)
    Scroll.pack(side = RIGHT, fill = Y)
    PROGTxt["LOGSRCH"].configure(yscrollcommand = Scroll.set)
    Sub.pack(side = TOP, fill = BOTH, expand = YES)
    Sub = Frame(LFrm)
    BButton(Sub, text = "Search", command = formLOGSRCHGo).pack(side = LEFT)
    Label(Sub, text = " ").pack(side = LEFT)
    BButton(Sub, text = "Close", fg = Clr["R"], command = Command(closeForm, \
            "LOGSRCH")).pack(side = LEFT)
    Sub.pack(side = TOP, padx = 3, pady = 3)
# Status messages.
    PROGMsg["LOGSRCH"] = Text(LFrm, font = PROGPropFont, height = 1)
    PROGMsg["LOGSRCH"].pack(side = TOP, fill = X)
    setMsg("LOGSRCH", "WB", \
            "Enter what to search for in the field at the top of the form.")
    center(Root, "LOGSRCH", "C", "I", True)
    return
################################
# BEGIN: formLOGSRCHGo(e = None)
# FUNC:formLOGSRCHGo():2012.325
def formLOGSRCHGo(e = None):
    LTxt = PROGTxt["LOGSRCH"]
    LTxt.delete(0.0, END)
    updateMe(0)
    LookFor = LOGSRCHSearchVar.get().lower()
    if len(QPLogs) == 0:
        setMsg("LOGSRCH", "RW", "There are no LOG messages to search.", 2)
        return
    setMsg("LOGSRCH", "CB", "Searching...")
    busyCursor(1)
    Found = 0
    for Line in QPLogs:
        LLine = Line.lower()
        if LLine.find(LookFor) != -1:
            LTxt.insert(END, Line+"\n")
            Found += 1
    setMsg("LOGSRCH", "", "%d matching %s found."%(Found, sP(Found, ("line", \
            "lines"))))
    busyCursor(0)
    return
# END: formLOGSRCH




############################################################################
# BEGIN: formPCAL(Parent, Where, VarSet, EntryVar, Entryidget, Wait, Format,
#                OrigFont = False)
# LIB:formPCAL():2013.273
#    Fills in EntryVar with a date selected by the user in YYYY:DOY,
#    YYYY-MM-DD, or YYYYMMMDD format. If a time like:
#        YYYY:DOY:HH:MM:SS
#        YYYY-MM-DD HH:MM:SS
#        YYYYMMMDD HH:MM:SS
#    is in the EntryVar value then that time will be preserved and returned
#    appended to the selected date.
#    Whatever is detected as the time will just be kept as a string and
#    appended back to the rest of the date. No error checking or anything is
#    done.
#    VarSet = If "" then the calling form's ChgBar will not be messed with.
#    Format = The format of the date to return. Can also be a StringVar that
#             contains the desired format string (as shown above).
PROGFrm["PCAL"] = None
PCALYear = 0
PCALMonth = 0
PCALTime = ""
PCALText = None
PCALModeRVar = StringVar()
PCALModeRVar.set("dates")
PROGSetups += ["PCALModeRVar", ]

def formPCAL(Parent, Where, VarSet, EntryVar, EntryWidget, Wait, Format, \
        OrigFont = False):
    global PCALYear
    global PCALMonth
    global PCALTime
    global PCALText
    if isinstance(Parent, basestring):
        Parent = PROGFrm[Parent]
    if isinstance(Format, StringVar):
        Format = Format.get()
# Set the calendar to the month of whatever may already be in the EntryVar and
# seal with any time that was passed.
    PCALTime = ""
    if rtnPattern(EntryVar.get()).startswith("0000-0"):
        PCALYear = intt(EntryVar.get())
        PCALMonth = intt(EntryVar.get()[5:])
        Parts = EntryVar.get().split()
        if len(Parts) == 2:
            PCALTime = Parts[1]
    elif rtnPattern(EntryVar.get()).startswith("0000:0"):
        PCALYear = intt(EntryVar.get())
        DOY = intt(EntryVar.get()[5:])
        PCALMonth, DD = dt2Timeydoy2md(PCALYear, DOY)
        Parts = EntryVar.get().split(":")
        if len(Parts) > 2:
            Parts += (5-len(Parts))*["0"]
            PCALTime = "%02d:%02d:%02d"%(intt(Parts[2]), intt(Parts[3]), \
                    intt(Parts[4]))
    elif rtnPattern(EntryVar.get()).startswith("0000AAA"):
        PCALYear = intt(EntryVar.get())
        MMM = EntryVar.get()[4:4+3].upper()
        PCALMonth = PROG_MONNUM[MMM]
        Parts = EntryVar.get().split()
        if len(Parts) == 2:
            PCALTime = Parts[1]
    if PROGFrm["PCAL"] != None:
        formPCALMove("c", VarSet, EntryVar, EntryWidget, Format)
        PROGFrm["PCAL"].deiconify()
        PROGFrm["PCAL"].lift()
        PROGFrm["PCAL"].focus_set()
        return
    LFrm = PROGFrm["PCAL"] = Toplevel(Parent)
    LFrm.withdraw()
    LFrm.resizable(0, 0)
    LFrm.protocol("WM_DELETE_WINDOW", Command(closeForm, "PCAL"))
    LFrm.title("Pick A Date")
    LFrm.iconname("PickCal")
    if Wait == True:
# Gets rid of some of the extra title bar buttons.
        LFrm.transient(Parent)
        LFrm.bind("<Visibility>", formPCALStay)
    if OrigFont == False:
        PCALText = Text(LFrm, bg = Clr["W"], fg = Clr["B"], height = 11, \
                width = 29, relief = SUNKEN, state = DISABLED)
    else:
        PCALText = Text(LFrm, bg = Clr["W"], fg = Clr["B"], \
                font = PROGOrigMonoFont, height = 11, width = 29, \
                relief = SUNKEN, state = DISABLED)
    PCALText.pack(side = TOP, padx = 3, pady = 3)
    if PCALYear != 0:
        formPCALMove("c", VarSet, EntryVar, EntryWidget, Format)
    else:
        formPCALMove("n", VarSet, EntryVar, EntryWidget, Format)
    Sub = Frame(LFrm)
    BButton(Sub, text = "<<", command = Command(formPCALMove, "-y", VarSet, \
            EntryVar, EntryWidget, Format)).pack(side = LEFT)
    BButton(Sub, text = "<", command = Command(formPCALMove, "-m", VarSet, \
            EntryVar, EntryWidget, Format)).pack(side = LEFT)
    BButton(Sub, text = "Today", command = Command(formPCALMove, "n", VarSet, \
            EntryVar, EntryWidget, Format)).pack(side = LEFT)
    BButton(Sub, text = ">", command = Command(formPCALMove, "+m", VarSet, \
            EntryVar, EntryWidget, Format)).pack(side = LEFT)
    BButton(Sub, text = ">>", command = Command(formPCALMove, "+y", VarSet, \
            EntryVar, EntryWidget, Format)).pack(side = LEFT)
    Sub.pack(side = TOP, padx = 3, pady = 3)
    Sub = Frame(LFrm)
    Radiobutton(Sub, text = "Dates", value = "dates", \
            variable = PCALModeRVar, command = Command(formPCALMove, "c", \
            VarSet, EntryVar, EntryWidget, Format)).pack(side = LEFT)
    Radiobutton(Sub, text = "DOY", value = "doy", variable = PCALModeRVar, \
            command = Command(formPCALMove, "c", VarSet, EntryVar, \
            EntryWidget, Format)).pack(side = LEFT)
    Label(Sub, text = " ").pack(side = LEFT)
    BButton(Sub, text = "Close", fg = Clr["R"], command = Command(closeForm, \
            "PCAL")).pack(side = TOP)
    Sub.pack(side = TOP, padx = 3, pady = 3)
    center(Parent, LFrm, Where, "I", True)
    if Wait == True:
        LFrm.grab_set()
        LFrm.focus_set()
        LFrm.wait_window()
    return
#######################################################
# BEGIN: formPCALCursorControl(Widget, Which, e = None)
# FUNC:formPCALCursorControl():2011.112
def formPCALCursorControl(Widget, Which, e = None):
    if e == None:
        Widget.config(cursor = "")
    elif e.type == "7":
        Widget.config(cursor = "%s"%Which)
    else:
        Widget.config(cursor = "")
    return
##################################################################
# BEGIN: formPCALMove(What, VarSet, EntryVar, EntryWidget, Format)
# FUNC:formPCALMove():2013.035
#   Handles changing the calendar form's display.
def formPCALMove(What, VarSet, EntryVar, EntryWidget, Format):
    global PCALYear
    global PCALMonth
    global PCALText
    Year = PCALYear
    Month = PCALMonth
    if What == "-y":
        Year -= 1
    elif What == "-m":
        Month -= 1
    elif What == "n":
        (Year, Month, Day) = getGMT(4)
    elif What == "+m":
        Month += 1
    elif What == "+y":
        Year += 1
    elif What == "c":
        pass
    if Year < 1971:
        beep(1)
        return
    elif Year > 2050:
        beep(1)
        return
    if Month > 12:
        Year += 1
        Month = 1
    elif Month < 1:
        Year -= 1
        Month = 12
    PCALYear = Year
    PCALMonth = Month
    LTxt = PCALText
    LTxt.configure(state = NORMAL)
    LTxt.delete("0.0", END)
# Otherwise "today" is cyan on every month.
    LTxt.tag_delete(*LTxt.tag_names())
    if PCALModeRVar.get() == "dates":
        DOM1 = 0
    else:
        DOM1 = PROG_FDOM[Month]
        if (Year%4 == 0 and Year%100 != 0) or Year%400 == 0:
            if Month > 2:
                DOM1 += 1
    LTxt.insert(END, "\n%s\n\n "%(PROG_CALMON[Month]+" "+str(Year)).center(29))
    IdxS = LTxt.index(CURRENT)
    LTxt.tag_config(IdxS, background = Clr["W"], foreground = Clr["R"])
    LTxt.insert(END, "Sun", IdxS)
    IdxS = LTxt.index(CURRENT)
    LTxt.tag_config(IdxS, background = Clr["W"], foreground = Clr["U"])
    LTxt.insert(END, " Mon Tue Wed Thu Fri ", IdxS)
    IdxS = LTxt.index(CURRENT)
    LTxt.tag_config(IdxS, background = Clr["W"], foreground = Clr["R"])
    LTxt.insert(END, "Sat ", IdxS)
    LTxt.insert(END, "\n")
    All = monthcalendar(Year, Month)
    NowYear, NowMonth, NowDay = getGMT(4)
    TargetDay = DOM1+NowDay
    for Week in All:
        LTxt.insert(END, " ")
        for DD in Week:
            if DD != 0:
                ThisDay = DOM1+DD
                IdxS = LTxt.index(CURRENT)
                if ThisDay == TargetDay and Month == NowMonth and \
                        Year == NowYear:
                    LTxt.tag_config(IdxS, background = Clr["C"], \
                            foreground = Clr["B"])
                    LTxt.tag_bind(IdxS, "<Button-1>", Command(formPCALPicked, \
                            VarSet, EntryVar, EntryWidget, (Year, Month, DD), \
                            Format))
                    LTxt.tag_bind(IdxS, "<Enter>", \
                            Command(formPCALCursorControl, LTxt, \
                            "right_ptr black white"))
                    LTxt.tag_bind(IdxS, "<Leave>", \
                            Command(formPCALCursorControl, LTxt, ""))
                else:
                    LTxt.tag_bind(IdxS, "<Button-1>", Command(formPCALPicked, \
                            VarSet, EntryVar, EntryWidget, (Year, Month, DD), \
                            Format))
                    LTxt.tag_bind(IdxS, "<Enter>", \
                            Command(formPCALCursorControl, LTxt, \
                            "right_ptr black white"))
                    LTxt.tag_bind(IdxS, "<Leave>", \
                            Command(formPCALCursorControl, LTxt, ""))
                if ThisDay < 10:
                    LTxt.insert(END, "  ")
                    LTxt.insert(END, "%d"%ThisDay, IdxS)
                    LTxt.insert(END, " ")
                elif ThisDay < 100:
                    LTxt.insert(END, " ")
                    LTxt.insert(END, "%d"%ThisDay, IdxS)
                    LTxt.insert(END, " ")
                else:
                    LTxt.insert(END, "%d"%ThisDay, IdxS)
                    LTxt.insert(END, " ")
            else:
                LTxt.insert(END, "    ")
        LTxt.insert(END, "\n")
    LTxt.configure(state = DISABLED)
    return
##############################################################################
# BEGIN: formPCALPicked(VarSet, EntryVar, EntryWidget, Date, Format, e = None)
# FUNC:formPCALPicked():2013.107
def formPCALPicked(VarSet, EntryVar, EntryWidget, Date, Format, e = None):
    if Format.startswith("YYYY-MM-DD"):
        if PCALTime == "":
            EntryVar.set("%d-%02d-%02d"%Date)
        else:
            EntryVar.set("%d-%02d-%02d %s"%(Date, PCALTime))
    elif Format == "YYYY:DOY":
        DOY = dt2Timeymd2doy(Date[0], Date[1], Date[2])
        if PCALTime == "":
            EntryVar.set("%d:%03d"%(Date[0], DOY))
        else:
            EntryVar.set("%d:%03d:%s"%(Date[0], DOY, PCALTime))
    elif Format == "YYYYMMMDD":
        if Date[1] > 0 and Date[1] < 13:
            MMM = PROG_CALMONS[Date[1]]
        else:
            MMM = "ERR"
        if PCALTime == "":
            EntryVar.set("%d%s%02d"%(Date[0], MMM, Date[2]))
        else:
            EntryVar.set("%d%s%02d %s"%(Date[0], MMM, Date[2], PCALTime))
    if EntryWidget != None:
        EntryWidget.icursor(END)
# The program or the VarSet form may not have any changebars.
    try:
        if VarSet != "":
# This is relevent portion of chgPROGChgBar() just to get rid of the reference.
             try:
                 PROGBar[VarSet].configure(bg = Clr["R"])
                 eval("%sBarSVar"%VarSet).set(1)
             except:
                 pass
    except NameError:
        pass
    closeForm("PCAL")
    return
###############################
# BEGIN: formPCALStay(e = None)
# FUNC:formPCALStay():2010.261
def formPCALStay(e = None):
# The window may not be up yet when this gets called.
    try:
        LFrm = PROGFrm["PCAL"]
        LFrm.unbind("<Visibility>")
        LFrm.focus_set()
        LFrm.update()
        LFrm.lift()
        LFrm.bind("<Visibility>", formPCALStay)
    except TclError:
        pass
    return
# END: formPCAL




#######################################
# BEGIN: formQPERR(MClr = "", Msg = "")
# FUNC:formQPERR():2013.171
#   Handles the window that displays the error messages that were collected
#   in QPErrors.
PROGFrm["QPERR"] = None
PROGTxt["QPERR"] = None
QPERRFindLookForVar = StringVar()
QPERRFindLastLookForVar = StringVar()
QPERRFindLinesVar = StringVar()
QPERRFindIndexVar = IntVar()
QPERRFilespecVar  = StringVar()
PROGSetups += ["QPERRFindLookForVar", "QPERRFilespecVar"]

def formQPERR(MClr = "", Msg = ""):
    global QPErrors
    if PROGFrm["QPERR"] != None:
        PROGFrm["QPERR"].deiconify()
        LTxt = PROGTxt["QPERR"]
    else:
        LFrm = PROGFrm["QPERR"] = Toplevel(Root)
        LFrm.withdraw()
        LFrm.protocol("WM_DELETE_WINDOW", Command(closeForm, "QPERR"))
        LFrm.title("Error Messages")
        LFrm.iconname("QPERR")
        Sub = Frame(LFrm)
        SSub = Frame(Sub)
        LTxt = PROGTxt["QPERR"] = Text(SSub, font = PROGMonoFont, \
                wrap = NONE, height = 12, width = 95, relief = SUNKEN)
        LTxt.pack(side = LEFT, expand = YES, fill = BOTH)
        LSb = Scrollbar(SSub, orient = VERTICAL, command = LTxt.yview)
        LSb.pack(side = RIGHT, fill = Y)
        LTxt.configure(yscrollcommand = LSb.set)
        SSub.pack(side = TOP, expand = YES, fill = BOTH)
        LSb = Scrollbar(Sub, command = LTxt.xview, orient = HORIZONTAL)
        LSb.pack(side = BOTTOM, fill = X)
        LTxt.configure(xscrollcommand = LSb.set)
        Sub.pack(side = TOP, expand = YES, fill = BOTH, padx = 1, pady = 1)
        Sub = Frame(LFrm)
        labelTip(Sub, "Find:=", LEFT, 30, "[Find]")
        LEnt = Entry(Sub, width = 20, textvariable = QPERRFindLookForVar)
        LEnt.pack(side = LEFT)
        LEnt.bind("<Return>", Command(formFind, "QPERR", "QPERR"))
        LEnt.bind("<KP_Enter>", Command(formFind, "QPERR", "QPERR"))
        BButton(Sub, text = "Find", command = Command(formFind, \
                "QPERR", "QPERR")).pack(side = LEFT)
        BButton(Sub, text = "Next", command = Command(formFindNext, \
                "QPERR", "QPERR")).pack(side = LEFT)
        Label(Sub, text = " ").pack(side = LEFT)
        BButton(Sub, text = "Write To File", command = Command(formWrite, \
                "QPERR", "QPERR", "QPERR", "Write QPErrors Lines", \
                QPERRFilespecVar, \
                True)).pack(side = LEFT)
        Label(Sub, text = " ").pack(side = LEFT)
        BButton(Sub, text = "Close", fg = Clr["R"], \
                command = Command(closeForm, "QPERR")).pack(side = LEFT)
        Sub.pack(side = TOP, padx = 3, pady = 3)
        PROGMsg["QPERR"] = Text(LFrm, font = PROGPropFont, height = 3, \
                wrap = WORD)
        PROGMsg["QPERR"].pack(side = TOP, fill = X)
        center(Root, LFrm, "N", "O", True)
# FINISHME - this is where we need to start changing the library (formHELP in
# this case) functions to handle things like no Work dir. It should fall back
# to the Data dir if PROGWorkDirVar does not exist. (this was PROGWorkDirVar)
    if QPERRFilespecVar.get() == "" or \
            exists(dirname(QPERRFilespecVar.get())) == False:
        QPERRFilespecVar.set(PROGDataDirVar.get()+PROG_NAMELC+"log.txt")
# Clear this so the formFind() routine does the right thing if this form was
# brought up previously.
    QPERRFindLinesVar.set("")
    setMsg("QPERR", "CB", "Working...")
    LTxt.delete(0.0, END)
    for Line in QPErrors:
# These are standard error messages which I will figure out how to display in
# all their glory someday. FINISHME
# Sometimes the Filespec where the error occurs is in Line[4] and sometimes
# not. Use the value to figure out the best way to print the messages.
        if Line[0] == 1:
            LTxt.insert(END, "%s\n"%Line[2])
        elif Line[0] == 4:
            LTxt.insert(END, "%s  File: %s\n"%(Line[2], basename(Line[4])))
    setMsg("QPERR", "", "%d %s encountered."%(len(QPErrors), \
            sP(len(QPErrors), ("error", "errors"))))
    return
#########################
# BEGIN: formQPERRClear()
# FUNC:formQPERRClear():2013.047
def formQPERRClear():
    if PROGFrm["QPERR"] != None:
        PROGTxt["QPERR"].delete(0.0, END)
        setMsg("QPERR", "", "")
    return
################################
# BEGIN: formQPERRMsg(MClr, Msg)
# FUNC:formQPERRMsg(MClr, Msg):2013.047
def formQPERRMsg(MClr, Msg):
    if PROGFrm["QPERR"] != None:
        setMsg("QPERR", MClr, Msg)
    return
# END: formQPERR




###################
# BEGIN: formSFCI()
# FUNC:formSFCI():2013.049
#   Scans through the selected source on the main display and makes a list of
#   all of the channels it finds in the file. The user can then rearrange them
#   in the order they want, copy the list to a "clipboard" (!!) and then
#   paste it into a slot in the Channel Preferences form. Fancy schmancy.
PROGFrm["SFCI"] = None
SFCISubButtons = None
SFCIButtons = []
SFCIIDsVar = StringVar()
SFCIChans = []
SFCIStaIDs = []
SFCIScanBut = None
SFCIStopBut = None
SFCIRunning = 0

def formSFCI():
    global SFCISubButtons
    global SFCIScanBut
    global SFCIStopBut
    if showUp("SFCI"):
        return
    LFrm = PROGFrm["SFCI"] = Toplevel(Root)
    LFrm.withdraw()
    LFrm.resizable(0, 0)
    LFrm.protocol("WM_DELETE_WINDOW", Command(closeForm, "SFCI"))
    LFrm.title("Scan For Channel IDs")
    LFrm.iconname("SFCIds")
    Label(LFrm, \
            text = "Select the source to read on the main display (as well as the desired '.bms Dir'\nradiobutton, if appropriate) and click the Scan button below.").pack(side = TOP)
# Where the buttons will be created.
    SFCISubButtons = Frame(LFrm)
    SFCISubButtons.pack(side = TOP, padx = 10, pady = 10)
    Entry(LFrm, width = 120, textvariable = SFCIIDsVar).pack(side = TOP, \
            padx = 3)
    Sub = Frame(LFrm)
    labelTip(Sub, ".bms Dir:", LEFT, 35, \
       "Select which directory on a baler memory stick to read if applicable.")
    Radiobutton(Sub, text = "data"+sep, variable = OPTBMSDataDirRVar, \
            value = "data").pack(side = LEFT)
    Radiobutton(Sub, text = "sdata"+sep, variable = OPTBMSDataDirRVar, \
            value = "sdata").pack(side = LEFT)
    Label(Sub, text = " ").pack(side = LEFT)
    SFCIScanBut = BButton(Sub, text = "Scan", command = formSFCIGo)
    SFCIScanBut.pack(side = LEFT)
    SFCIStopBut = BButton(Sub, text = "Stop", state = DISABLED, \
            command = Command(formSFCIControl, "stop"))
    SFCIStopBut.pack(side = LEFT)
    Label(Sub, text = " ").pack(side = LEFT)
    BButton(Sub, text = "All", command = formSFCIAll).pack(side = LEFT)
    BButton(Sub, text = "Copy", command = formSFCICopy).pack(side = LEFT)
    Label(Sub, text = " ").pack(side = LEFT)
    BButton(Sub, text = "Channel Preferences", \
            command = formCPREF).pack(side = LEFT)
    BButton(Sub, text = "Clear", fg = Clr["U"], \
            command = Command(formSFCIClear, "ids")).pack(side = LEFT)
    BButton(Sub, text = "Close", fg = Clr["R"], \
            command = Command(formSFCIControl, "close")).pack(side = LEFT)
    Sub.pack(side = TOP, padx = 3, pady = 3)
    PROGMsg["SFCI"] = Text(LFrm, font = PROGPropFont, height = 2)
    PROGMsg["SFCI"].pack(side = LEFT, fill = X, expand = YES)
# Bring up any old set of buttons.
    formSFCIMakeButtons()
    center(Root, LFrm, "W", "O", True)
    return
#####################
# BEGIN: formSFCIGo()
# FUNC:formSFCIGo():2013.171
#   This will basically be a simplified combination of fileSelected() and
#   then q330Process().
def formSFCIGo():
    global SFCIButtons
    PROGFrm["SFCI"].focus_set()
    formSFCIControl("go")
    DataDir = PROGDataDirVar.get()
# Just in case.
    if DataDir.endswith(sep) == False:
        DataDir += sep
        PROGDataDirVar.set(DataDir)
    Sel = MFFiles.curselection()
    if len(Sel) == 0 or MFFiles.get(Sel[0]) == "":
        setMsg("SFCI", "RW", \
                "No data source files/folders have been selected.", 2)
        formSFCIControl("stopped")
        return
# Only one-at-a-time for this routine.
    if len(Sel) > 1:
        setMsg("SFCI", "RW", \
           "Only one data source file/folder may be selected for scanning.", 2)
        formSFCIControl("stopped")
        return
    Filename = MFFiles.get(Sel[0])
# Most items will have a (x bytes) or something like that.
    if Filename.find(" (") != -1:
        Filename = Filename[:Filename.index(" (")]
    Filespec = DataDir+Filename
    Message = "Scanning %s..."%Filespec
    setMsg("SFCI", "CB", Message)
    BMSDataDir = OPTBMSDataDirRVar.get()
# The directory may have gotten changed, but the list of files not.
    if exists(Filespec) == False:
        setMsg("SFCI", "RW", "File %s does not exist."%Filespec, 2)
        formSFCIControl("stopped")
        return
    formSFCIClear("all")
    FilespecLC = Filespec.lower()
    Problems = 0
    if FilespecLC.endswith(".bms"):
        if BMSDataDir not in ("data", "sdata"):
            setMsg("SFCI", "RW", "Select the '.bms Dir' checkbutton again.", 2)
            formSFCIControl("stopped")
            return
        if exists(Filespec+sep+BMSDataDir+sep) == False:
            setMsg("SFCI", "RW", "%s does not exist."% \
                    (Filespec+sep+BMSDataDir+sep), 2)
            formSFCIControl("stopped")
            return
        Ret = walkDirs2(Filespec, False, sep+BMSDataDir+sep, "", 1)
        if Ret[0] != 0:
            setMsg("SFCI", Ret)
            formSFCIControl("stopped")
            return
        Files = Ret[1]
        if len(Files) == 0:
            setMsg("SFCI", "RW", "No files were found in\n   %s"% \
                    (Filespec+sep+BMSDataDir+sep), 2)
            formSFCIControl("stopped")
            return
        Files.sort()
        FileCount = 0
        for File in Files:
            FileCount += 1
            if FileCount%500 == 0:
                setMsg("SFCI", "CB", "%s\nWorking on file %d of %d..."% \
                        (Message, FileCount, len(Files)))
            Ret = formSFCIFileProcess(File, "", False)
# Just count the problems and keep plowing through the files.
            if Ret == False:
                Problems += 1
# Check for stopping each file.
            SFCIStopBut.update()
# Just break out and show what we've collected so far.
            if SFCIRunning == 0:
                break
    elif FilespecLC.endswith(".all"):
        Ret = formSFCIFileProcess(Filespec, Message, False)
        if Ret == False:
            Problems += 1
    elif FilespecLC.endswith(".soh"):
        Ret = formSFCIFileProcess(Filespec, Message, False)
        if Ret == False:
            Problems += 1
    elif FilespecLC.endswith(".sdr"):
        Ret = walkDirs2(Filespec, False, "", "", 0)
        if Ret[0] != 0:
            setMsg("SFCI", Ret)
            formSFCIControl("stopped")
            return
        Files = Ret[1]
        if len(Files) == 0:
            setMsg("SFCI", "RW", "No channel files were found in\n   %s"% \
                    (Filespec+sep+BMSDataDir+sep), 2)
            formSFCIControl("stopped")
            return
        Files.sort()
        FileCount = 0
        for File in Files:
            FileCount += 1
            if FileCount%50 == 0:
                setMsg("SFCI", "CB", "%s\nWorking on file %d of %d..."% \
                        (Message, FileCount, len(Files)))
            Ret = formSFCIFileProcess(File, "", True)
            if Ret == False:
                Problems += 1
            SFCIStopBut.update()
            if SFCIRunning == 0:
                break
    elif FilespecLC.endswith(".nan"):
        Ret = walkDirs2(Filespec, False, "", "", 1)
        if Ret[0] != 0:
            setMsg("SFCI", Ret)
            formSFCIControl("stopped")
            return
        Files = Ret[1]
        if len(Files) == 0:
            setMsg("SFCI", "RW", "No channel files were found in\n   %s"% \
                    (Filespec+sep), 2)
            formSFCIControl("stopped")
            return
        Files.sort()
        FileCount = 0
        for File in Files:
            FileCount += 1
            if FileCount%50 == 0:
                setMsg("SFCI", "CB", "%s\nWorking on file %d of %d..."% \
                        (Message, FileCount, len(Files)))
            Ret = formSFCIFileProcess(File, "", True)
            if Ret == False:
                Problems += 1
            SFCIStopBut.update()
            if SFCIRunning == 0:
                break
    elif FilespecLC.endswith(".ant"):
        Ret = walkDirs2(Filespec, False, "", "", 0)
        if Ret[0] != 0:
            setMsg("SFCI", Ret)
            formSFCIControl("stopped")
            return
        Files = Ret[1]
        if len(Files) == 0:
            setMsg("SFCI", "RW", "No channel files were found in\n   %s"% \
                    (Filespec+sep), 2)
            formSFCIControl("stopped")
            return
        Files.sort()
        FileCount = 0
        for File in Files:
            FileCount += 1
            if FileCount%50 == 0:
                setMsg("SFCI", "CB", "%s\nWorking on file %d of %d..."% \
                        (Message, FileCount, len(Files)))
            Ret = formSFCIFileProcess(File, "", False)
            if Ret == False:
                Problems += 1
            SFCIStopBut.update()
            if SFCIRunning == 0:
                break
    elif FilespecLC != "":
        setMsg("SFCI", "RW", \
                "I don't know what to do with the file/folder\n   %s"% \
                Filespec, 2)
        formSFCIControl("stopped")
        return
    if len(SFCIChans) == 0:
        setMsg("SFCI", "YB", "No channels were found!?", 2)
        formSFCIControl("stopped")
        return
    SFCIChans.sort()
    AllGood = formSFCIMakeButtons()
    Stas = list2Str(SFCIStaIDs)
    if AllGood == True:
        setMsg("SFCI", "", "Done. Channels found: %s  Stations found: %s"% \
                (len(SFCIChans), Stas))
    else:
        setMsg("SFCI", "YB", \
                "Done. Channels found: %s  Stations found: %s\nSome channels unrecognized. Requires changing the program to read them."% \
                (len(SFCIChans), Stas))
    formSFCIControl("stopped")
    return
##############################
# BEGIN: formSFCIMakeButtons()
# FUNC:formSFCIMakeButtons():2013.191
def formSFCIMakeButtons():
    ChanCount = 0
    AllGood = True
    for Chan in SFCIChans:
        if ChanCount%14 == 0:
            Sub = Frame(SFCISubButtons)
# If this is a recognized channel then make a ToolTip description using the
# plot label info, otherwise point it out by making the button yellow.
        if Chan[:3] in QPChans:
            LBut = BButton(Sub, text = Chan, font = PROGMonoFont, \
                    command = Command(formSFCIAdd, Chan))
            LBut.pack(side = LEFT)
            ToolTip(LBut, 30, QPChans[Chan[:3]][QPCHANS_LABEL])
        else:
            LBut = BButton(Sub, text = Chan, font = PROGMonoFont, \
                    bg = Clr["Y"], command = Command(formSFCIAdd, Chan))
            LBut.pack(side = LEFT)
            ToolTip(LBut, 30, "Unrecognized channel.")
            AllGood = False
        SFCIButtons.append(LBut)
        ChanCount += 1
        if ChanCount%14 == 0:
            Sub.pack(side = TOP)
            SFCIButtons.append(Sub)
    if ChanCount%14 != 0:
        Sub.pack(side = TOP)
        SFCIButtons.append(Sub)
    return AllGood
######################################################
# BEGIN: formSFCIFileProcess(Filespec, Message, Break)
# FUNC:formSFCIFileProcess():2013.080
#   This reads enough of the files to get the channel names/codes, but just
#   returns a True or False as to whether things went OK. Who knows what the
#   caller might send it. The caller can keep track of how many errors there
#   were and let the user know at the end of scanning.
#   If Break is True then the routine can break out of reading a file after
#   the first block, because the file should only have one channel of data in
#   it.
def formSFCIFileProcess(Filespec, Message, Break):
    global SFCIChans
    global SFCIStaIDs
    try:
        Fp = open(Filespec, "rb")
    except Exception, e:
        return False
# These come from Nanometrics systems. Read the first line of each file type
# and look at the column header titles. Certain titles will correspond to
# certain "channels".
    if Filespec.endswith(".csv"):
        Line = Fp.readline()
        Parts = map(strip, Line.split(","))
        if "GPS Receiver Status" in Parts:
            if "NGS" not in SFCIChans:
                SFCIChans.append("NGS")
        if "Timing Phase Lock" in Parts:
            if "NPL" not in SFCIChans:
                SFCIChans.append("NPL")
        if "Timing Uncertainty(ns)" in Parts:
            if "NTU" not in SFCIChans:
                SFCIChans.append("NTU")
# Note capitalization. TitanSMA?
        if "Supply voltage(V)" in Parts:
            if "NSV" not in SFCIChans:
                SFCIChans.append("NSV")
# Everyone else.
        if "Supply Voltage(mV)" in Parts:
            if "NSV" not in SFCIChans:
                SFCIChans.append("NSV")
        if "Total current(A)" in Parts:
            if "NTC" not in SFCIChans:
                SFCIChans.append("NTC")
        if "Temperature(&deg;C)" in Parts:
            if "NTM" not in SFCIChans:
                SFCIChans.append("NTM")
        if "Sensor SOH Voltage 1(V)" in Parts:
            if "NM1" not in SFCIChans:
                SFCIChans.append("NM1")
        if "Sensor SOH Voltage 2(V)" in Parts:
            if "NM2" not in SFCIChans:
                SFCIChans.append("NM2")
        if "Sensor SOH Voltage 3(V)" in Parts:
            if "NM3" not in SFCIChans:
                SFCIChans.append("NM3")
        if "Timing Error(ns)" in Parts:
            if "NTE" not in SFCIChans:
                SFCIChans.append("NTE")
        if "Controller Current(mA)" in Parts:
            if "NCC" not in SFCIChans:
                SFCIChans.append("NCC")
        if "Digitizer Current(mA)" in Parts:
            if "NDC" not in SFCIChans:
                SFCIChans.append("NDC")
        if "NMX Bus Current(mA)" in Parts:
            if "NNC" not in SFCIChans:
                SFCIChans.append("NNC")
        if "Sensor Current(mA)" in Parts:
            if "NSC" not in SFCIChans:
                SFCIChans.append("NSC")
        if "Serial Port Current(mA)" in Parts:
            if "NSP" not in SFCIChans:
                SFCIChans.append("NSP")
        Fp.close()
        return True
# Determine if this is a 256B, 1K or 4K miniseed file. Some recorders change
# record size depending on the sample rate of the channel, so check this for
# each file, eventhough it wouldn't be a really big deal for this scanning
# function (vs. for the data extraction part).
    RecordSize = 0
    for i in xrange(0, 17):
        Record = Fp.read(256)
# If the file is too small to determine it's record size then just go on.
        if len(Record) < 256:
            Fp.close()
            return True
        if i == 0:
            StaID = Record[8:13]
            continue
        if StaID == Record[8:13]:
            if i == 1:
                RecordSize = 256
            elif i == 2:
                RecordSize = 512
            elif i == 4:
                RecordSize = 1024
            elif i == 8:
                RecordSize = 2048
            elif i == 16:
                RecordSize = 4096
            break
    if RecordSize == 0:
        Fp.close()
        return False
    Fp.seek(0)
    RecordsSize = RecordSize*10
    RecordsReads = 0
    NoOfRecords = int(getsize(Filespec)/RecordSize)
    while 1:
        Records = Fp.read(RecordsSize)
# We're done with this file.
        if len(Records) == 0:
            Fp.close()
            return True
        RecordsReads += 10
        if RecordsReads%10000 == 0:
            SFCIStopBut.update()
            if SFCIRunning == 0:
# Nothing wrong here. The caller will handle the stopping.
                Fp.close()
                return True
# Sometimes the caller will provide a file name for big files to show and
# report the status of reading.
            if Message != "":
                setMsg("SFCI", "CB", "%s\nReading record %d of %d..."% \
                        (Message, RecordsReads, NoOfRecords))
        for i in xrange(0, 10):
            Ptr = RecordSize*i
            Record = Records[Ptr:Ptr+RecordSize]
# Need another set of Records.
            if len(Record) < RecordSize:
                break
            ChanID = Record[15:18]
# The Q330 may create an "empty" file (all 00H) and then not finish filling it
# in. The read()s keep reading, but there's nothing to process. This detects
# that and goes on to the next file. This may only happen in .bms-type data.
            if ChanID == "\x00\x00\x00":
                Fp.close()
                return True
            LocID = Record[13:15].strip()
            ChanID = ChanID+LocID
            if ChanID not in SFCIChans:
                SFCIChans.append(ChanID)
# Check this on the first Record of a file.
            if RecordsReads == 10:
                StaID = Record[8:13].strip()
                if StaID not in SFCIStaIDs:
                    SFCIStaIDs.append(StaID)
            if Break == True:
                Fp.close()
                return True
    return True
####################################
# BEGIN: formSFCIAdd(Chan, e = None)
# FUNC:formSFCIAdd(Chan, e = None):2012.305
def formSFCIAdd(Chan, e = None):
    setMsg("SFCI", "", "")
    Str = SFCIIDsVar.get()
    Str = Str.replace(" ", "")
    Str = Str.upper()
    Str = deComma(Str)
# Warn the user. It gets hard to keep track of these things.
    if Str.find(Chan) != -1:
        setMsg("SFCI", "YB", "%s may already be in the list."%Chan)
    if len(Str) > 0:
        Str += ","
    Str += Chan
    SFCIIDsVar.set(Str)
    return
##############################
# BEGIN: formSFCIAll(e = None)
# FUNC:formSFCIAll(e = None):2012.305
def formSFCIAll(e = None):
    setMsg("SFCI", "", "")
    SFCIIDsVar.set("")
    Str = ""
    for Item in SFCIButtons:
# Sub won't have a "text".
        try:
            Chan = Item.cget("text")
            if Chan == "":
                continue
            if len(Str) > 0:
                Str += ","
            Str += Chan
        except TclError:
            pass
    SFCIIDsVar.set(Str)
    return
##############################
# BEGIN: formSFCIClear(Action)
# FUNC:formSFCIClear():2013.049
def formSFCIClear(Action):
    global SFCIButtons
    global SFCIChans
    global SFCIStaIDs
    if Action == "all":
        for Item in SFCIButtons:
            Item.destroy()
        del SFCIChans[:]
        del SFCIStaIDs[:]
    SFCIIDsVar.set("")
    updateMe(0)
    return
#######################
# BEGIN: formSFCICopy()
# FUNC:formSFCICopy():2012.304
def formSFCICopy():
    Str = SFCIIDsVar.get()
    Str = Str.replace(" ", "")
    Str = Str.upper()
    Str = deComma(Str)
# FINISHME - should probably look for anything other than letters, numbers and commas
    SFCIIDsVar.set(Str)
    PROGClipboardVar.set(Str)
    setMsg("SFCI", "", "Copied.")
    return
##############################
# BEGIN: formSFCIControl(What)
# FUNC:formSFCIControl():2012.322
def formSFCIControl(What):
    global SFCIRunning
    if What == "go":
        buttonBG(SFCIScanBut, "G", NORMAL)
        buttonBG(SFCIStopBut, "R", NORMAL)
        SFCIRunning = 1
        return
    elif What == "stop":
        if SFCIRunning == 0:
            beep(1)
        else:
            buttonBG(SFCIStopBut, "Y", NORMAL)
    elif What == "stopped":
        buttonBG(SFCIScanBut, "D", NORMAL)
        buttonBG(SFCIStopBut, "D", DISABLED)
    elif What == "close":
        if SFCIRunning == 1:
            beep(1)
            return
        closeForm("SFCI")
    SFCIRunning = 0
    return
# END: formSFCI




##################
# BEGIN: formTPS()
# FUNC:formTPS():2013.177
PROGFrm["TPS"] = None
TPSColorRangeRVar = StringVar()
TPSColorRangeRVar.set("med")
TPSPSFilespecVar = StringVar()
PROGSetups += ["TPSColorRangeRVar", "TPSPSFilespecVar"]
TPSBufLeft = 0
TPSPWidth = 0
TPSStart = 0
TPSRunning = 0
TPSPlotted = False
TPSPlotBut = None
TPSStopBut = None

def formTPS():
    global TPSPlotBut
    global TPSStopBut
    global TPSRunning
    global TPSPlotted
    if showUp("TPS") == False:
        LFrm = PROGFrm["TPS"] = Toplevel(Root)
        LFrm.withdraw()
        LFrm.protocol("WM_DELETE_WINDOW", Command(formTPSControl, "close"))
        LFrm.title("TPS Plot")
        Sub = Frame(LFrm)
        SSub = Frame(Sub)
# 915 = 25+(3*288)+25, plus 1
        LCan = PROGCan["TPS"] = Canvas(SSub, bg = DClr["TC"], \
                relief = SUNKEN, height = 500, width = 915, \
                scrollregion = (0, 0, 915, 500))
        LCan.bind("<Button-1>", Command(formTPSTimeClick, -1, "", 0, 0))
        LCan.bind("<Control-Button-1>", Command(formTPSTimeClick, -1, "", 0, \
                0))
        LCan.bind("<MouseWheel>", Command(mouseWheel, LCan))
        LCan.bind("<Button-4>", Command(mouseWheel, LCan))
        LCan.bind("<Button-5>", Command(mouseWheel, LCan))
        LCan.pack(side = LEFT, expand = YES, fill = BOTH)
        Sb = Scrollbar(SSub, orient = VERTICAL, command = LCan.yview)
        Sb.pack(side = RIGHT, expand = NO, fill = Y)
        LCan.configure(yscrollcommand = Sb.set)
        SSub.pack(side = TOP, expand = YES, fill = BOTH)
        Sb = Scrollbar(Sub, orient = HORIZONTAL, command = LCan.xview)
        Sb.pack(side = BOTTOM, expand = NO, fill = X)
        LCan.configure(xscrollcommand = Sb.set)
        Sub.pack(side = TOP, expand = YES, fill = BOTH)
        Sub = Frame(LFrm)
        SSub = Frame(Sub)
        SSSub = Frame(SSub)
        LRb = Radiobutton(SSSub, text = "A", variable = TPSColorRangeRVar, \
                value = "antarctica")
        LRb.pack(side = LEFT)
        ToolTip(LRb, 30, "\"Antarctica\" color range.")
        LRb = Radiobutton(SSSub, text = "L", variable = TPSColorRangeRVar, \
                value = "low")
        LRb.pack(side = LEFT)
        ToolTip(LRb, 30, "\"Low\" color range.")
        LRb = Radiobutton(SSSub, text = "M", variable = TPSColorRangeRVar, \
                value = "med")
        LRb.pack(side = LEFT)
        ToolTip(LRb, 30, "\"Medium\" color range.")
        LRb = Radiobutton(SSSub, text = "H", variable = TPSColorRangeRVar, \
                value = "high")
        LRb.pack(side = LEFT)
        ToolTip(LRb, 30, "\"High\" color range.")
        SSSub.pack(side = TOP)
        SSSub = Frame(SSub)
        labelTip(SSSub, "Chans:", LEFT, 35, \
                "Enter the channels to plot separated by a comma.")
        Entry(SSSub, textvariable = OPTPlotTPSChansVar, \
                width = 25).pack(side = LEFT)
        SSSub.pack(side = TOP)
        SSub.pack(side = LEFT, padx = 3, pady = 3)
        Label(Sub, text = " ").pack(side = LEFT)
        TPSPlotBut = BButton(Sub, text = "Plot", \
                command = Command(formTPSPlot, "button"))
        TPSPlotBut.pack(side = LEFT)
        TPSStopBut = BButton(Sub, text = "Stop", state = DISABLED, \
                command = Command(formTPSControl, "stop"))
        TPSStopBut.pack(side = LEFT)
        BButton(Sub, text = "Write .ps", command = Command(formWritePS, \
                "TPS", "TPS", TPSPSFilespecVar)).pack(side = LEFT)
        Label(Sub, text = " ").pack(side = LEFT)
        PROGMsg["TPS"] = Text(Sub, font = PROGPropFont, height = 3, \
                wrap = WORD, cursor = "")
        PROGMsg["TPS"].pack(side = LEFT, fill = X, expand = YES)
        LLb = Label(Sub, text = " Hints ")
        LLb.pack(side = LEFT)
        ToolTip(LLb, 35, "PLOT AREA HINT:\n--Click on plot: Clicking on a point on the plot shows the time and average signal value at that position in the message area, and shows a rule at that position in time on the main plot display. (Control-click also does this.)\n--Click on left/right: Click on the far left or right to clear the time and signal level value.\n--Click on dotted line: Clicking on a dotted day line will display the number of days that were skipped to produce that dotted day line.")
        Sub.pack(side = TOP, fill = X, expand = NO)
        if TPSPSFilespecVar.get() == "":
            TPSPSFilespecVar.set(PROGDataDirVar.get())
        center(Root, LFrm, "E", "O", True)
        TPSPlotted = False
        TPSRunning = 0
    return
################################
# BEGIN: formTPSPlot(Who = None)
# FUNC:formTPSPlot():2013.108
#   Outsiders can call this to bring up the form and start the plotting.
def formTPSPlot(Who = None):
    global TPSPlotted
    LFrm = PROGFrm["TPS"]
# If this is being called by the Plot button then the user probably doesn't
# want to close the form, and the form probably doesn't need to be brought up.
# Set the Var in case it is not since the form is up and being used.
    if Who == "button":
        OPTPlotTPSCVar.set(1)
    elif Who == None:
        if OPTPlotTPSCVar.get() == 0:
            if LFrm != None:
                formTPSControl("close")
            return
        else:
            if LFrm == None:
                formTPS()
# Do this here, because clearing can take a long time.
    setMsg("TPS", "CB", "Working...")
    formTPSControl("go")
    formTPSClear(False)
    if MFPlotted == False:
        setMsg("TPS", "RW", "It doesn't look like anything has been read.", 2)
        formTPSControl("stopped")
        return
    Ret = setQPUserChannels("tpsplot")
    if Ret[0] != 0:
        setMsg("TPS", Ret)
        formTPSControl("stopped")
        return
    Ret = formTPSChkChans()
    if Ret[0] != 0:
        setMsg("TPS", Ret)
        formTPSControl("stopped")
        return
    formTPSGo()
    L, T, R, B = PROGCan["TPS"].bbox(ALL)
    PROGCan["TPS"].configure(scrollregion = (0, 0, R+25, (B+15)))
    if TPSRunning == 0:
        setMsg("TPS", "YB", "Stopped.")
    else:
        setMsg("TPS", "", "Done.")
# Do this after the check above.
    formTPSControl("stopped")
    TPSPlotted = True
    return
####################
# BEGIN: formTPSGo()
# FUNC:formTPSGo():2013.082
TPSPlotData = []

def formTPSGo():
    global TPSBufLeft
    global TPSPWidth
    global TPSStart
    global TPSRunning
    global TPSPlotData
    LFrm = PROGFrm["TPS"]
    LFrm.focus_set()
# Don't list all of the files. Do this here, instead of formTPSPlot() so we
# can put the Filename at the top of the plots too.
    Filename = QPFilesProcessed[0]
    if len(QPFilesProcessed) > 1:
        Filename += "+"
    LFrm.title("TPS Plot - %s"%Filename)
    LCan = PROGCan["TPS"]
    LCan.configure(bg = DClr["TC"])
    ColorRange = TPSColorRangeRVar.get()
# Set the ranges for the colors based on the A H M L radiobuttons.
    if ColorRange == "antarctica":
        Bin0 = 0.0
        Bin1 = 100.0   # 10
        Bin2 = 10000.0   # 100
        Bin3 = 1000000.0   # 1000
        Bin4 = 100000000.0   # 10000
        Bin5 = 10000000000.0   # 100000
        Bin6 = 1000000000000.0   # 1000000
    elif ColorRange == "low":
        Bin0 = 0.0
        Bin1 = 400.0   # 20
        Bin2 = 40000.0   # 200
        Bin3 = 4000000.0   # 2000
        Bin4 = 400000000.0   # 20000
        Bin5 = 40000000000.0   # 200000
        Bin6 = 4000000000000.0   # 2000000
    elif ColorRange == "med":
        Bin0 = 0.0
        Bin1 = 2500.0   # 50
        Bin2 = 250000.0   # 500
        Bin3 = 25000000.0   # 5000
        Bin4 = 2500000000.0   # 50000
        Bin5 = 250000000000.0   # 500000
        Bin6 = 25000000000000.0   # 5000000
    elif ColorRange == "high":
        Bin0 = 0.0
        Bin1 = 6400.0   # 80
        Bin2 = 640000.0   # 800
        Bin3 = 64000000.0   # 8000
        Bin4 = 6400000000.0   # 80000
        Bin5 = 640000000000.0   # 800000
        Bin6 = 64000000000000.0   # 8000000
# The channels to plot (and the order to plot them).
    PlotChans = OPTPlotTPSChansVar.get().split(",")
# Will be a list of lists with a list for each 5-minute bin as
#    [[sum of squared counts, number of data points, AveValue, X, Y], ...]
    del TPSPlotData[:]
# Make sure GY never becomes a float, otherwise it could make the day plot
# lines run together and generally look really bad on some operating/X11
# systems.
    GY = PROGPropFontHeight
    TPSBufLeft = 25
# 3 pixels per 5 mins.
    TPSPWidth = 3*288
# The display will always show whole days, but only plot the data corresponding
# to the main form's time range.
# This is going to bite me in the ass wrt leap seconds, but there you go. It's
# only a second.
    TPSStart = int(QPEarliestCurr/86400.0)*86400
    TPSEnd = int(QPLatestCurr/86400.0)*86400+86400
# Get local copies.
    EarliestCurr = QPEarliestCurr
    LatestCurr = QPLatestCurr
    Message = "File: %s   Station: %s   %s  to  %s  (%s)"%(Filename, \
            list2Str(QPStaIDs), dt2Time(-1, 80, EarliestCurr), dt2Time(-1, \
            80, LatestCurr), timeRangeFormat(LatestCurr-EarliestCurr))
    canText(LCan, 10, GY, DClr["TX"], Message)
    GY += PROGPropFontHeight
# Channel loop.
    for Chan in QPUserChannels:
        if Chan not in QPSampRates:
            continue
# Since there can be wildcards (*) just a 'not in' won't work.
        Found = False
        for PlotChan in PlotChans:
            if PlotChan.endswith("*"):
                Aster = PlotChan.index("*")
                if Chan[:Aster] == PlotChan[:Aster]:
                    Found = True
                    break
            elif Chan == PlotChan:
                Found = True
                break
        if Found == False:
            continue
        TheQPData = QPData[Chan]
# This shouldn't happen.
        if len(TheQPData) == 0:
            ID = canText(LCan, 10, GY, DClr["TX"], \
                    "No data to plot for '%s'."%Chan)
            L, T, R, B = LCan.bbox(ID)
            ID2 = LCan.create_rectangle(L, T-1, R, B, fill = DClr["TC"], \
                    outline = DClr["TC"])
            LCan.tag_raise(ID, ID2)
            GY += PROGPropFontHeight
            continue
# The labels "in" the plot need to be printed, then a box the same color as
# the background be made, then the text lifted above the box, so the hour
# lines that will be generated at the end will not be visible through the text.
# That goes for the message above too.
        NewLabel = QPChans[Chan[:3]][QPCHANS_LABEL]
        NewLabel = Chan+NewLabel[3:]
# This will probably always be turned on for seismic data.
        if QPChans[Chan[:3]][QPCHANS_SHOWSR] == 1:
            Rate = QPSampRates[Chan]
            if Rate >= 1.0:
                Str = "%dsps"%Rate
            else:
                Str = "%gsps"%Rate
        else:
            Rate = ""
            Str = ""
        ID = canText(LCan, 10, GY, DClr["TX"], "%s %s"%(NewLabel, Str))
        L, T, R, B = LCan.bbox(ID)
        ID2 = LCan.create_rectangle(L, T-1, R, B, fill = DClr["TC"], \
                outline = DClr["TC"])
        LCan.tag_raise(ID, ID2)
        GY += PROGPropFontHeight
        formTPSTimeNumbers(LCan, GY)
        GY += PROGPropFontHeight
# Create a list with as many 5-minute bins as we are going to need to cover
# TPSStart to TPSEnd days.
# TPSPlotData[0] = Counts value
# TPSPlotData[1] = Number of data points
        TPSPlotData = [[0, 0] for i in \
                xrange(int((TPSEnd-TPSStart)/86400.0)*288)]
# Now go through all of the raw data points, calculate which bin created above
# each data point value should be added to based on the epoch time of each
# point and add it in.
        for Data in TheQPData:
            if Data[0] < TPSStart:
                continue
            if Data[0] > TPSEnd:
                break
# Filter once more so we only plot what the user has selected and not whole
# days (that's what the above lets pass).
            if Data[0] < EarliestCurr:
                continue
            if Data[0] > LatestCurr:
                break
            Index = int((Data[0]-TPSStart)//300)
            TPSPlotData[Index][0] += Data[1]**2
            TPSPlotData[Index][1] += 1
# Now go through the bins by day and each bin within each day.
# Was there data the day(s) before?
        WasData = True
        Missing = 0
        for DayIndex in xrange(0, len(TPSPlotData), 288):
            setMsg("TPS", "CB", "Plotting channel '%s'..."%Chan)
            GX = TPSBufLeft
# Take a quick glance at this day's data. If there is none for a day or more
# in-a-row, then we will just draw a special line covering that time, instead
# of drawing a black line for each empty day.
# Was there data for this day?
            HasData = False
            for BinIndex in xrange(DayIndex, DayIndex+288):
                if TPSPlotData[BinIndex][1] != 0:
                    HasData = True
                    break
# We've just run out of data or there still is no data, so keep looking.
            if HasData == False:
                Missing += 1
                WasData = False
                continue
# We're back, so draw the special line.
            if WasData == False:
                for i in xrange(0, 288):
# Draw a dotted line.
                    if i%2 == 0:
                        ID = LCan.create_rectangle(GX-1, GY-1, GX+1, GY+1, \
                                fill = Clr["K"], outline = Clr["K"])
                        LCan.tag_bind(ID, "<Button-1>", \
                                Command(formTPSDaysMissing, Missing))
# For next 5-minute block.
                    GX += 3
# For the next line, today's line, that has data.
                GX = TPSBufLeft
                GY += 5
                WasData = True
                Missing = 0
                if TPSRunning == 0:
# These have to be done here, instead of formTPSPlot(), because the lines
# need to be done before the color key, and formTPSColorKey() needs the Bin
# values, which are defined in here to make them local for speed.
                    formTPSTimeNumbers(LCan, GY)
                    formTPSTimeLines(LCan)
                    formTPSColorKey(LCan, Bin0, Bin1, Bin2, Bin3, Bin4, \
                            Bin5, Bin6)
                    return
# Draw a normal day's line.
            for BinIndex in xrange(DayIndex, DayIndex+288):
# If there are no points in this bin check the bins on either side. If they
# both have values then calculate an average and use that.
                if TPSPlotData[BinIndex][1] == 0:
                    try:
                        if TPSPlotData[BinIndex-1][1] != 0 and \
                                TPSPlotData[BinIndex+1][1] != 0:
                            Value = (TPSPlotData[BinIndex-1][0]+ \
                                    TPSPlotData[BinIndex+1][0])
                            Points = (TPSPlotData[BinIndex-1][1]+ \
                                    TPSPlotData[BinIndex+1][1])
# Save the results so we don't have to do this again.
                            TPSPlotData[BinIndex][0] = Value
                            TPSPlotData[BinIndex][1] = Points
                            AveValue = Value/Points
                        else:
                            AveValue = 0.0
                    except:
                        AveValue = 0.0
                else:
                    AveValue = float(TPSPlotData[BinIndex][0])/ \
                            TPSPlotData[BinIndex][1]
                if AveValue == Bin0:
                    C = "K"
                elif AveValue < Bin1:
                    C = "U"
                elif AveValue < Bin2:
                    C = "C"
                elif AveValue < Bin3:
                    C = "G"
                elif AveValue < Bin4:
                    C = "Y"
                elif AveValue < Bin5:
                    C = "R"
                elif AveValue < Bin6:
                    C = "M"
                else:
                    C = "E"
                ID = LCan.create_rectangle(GX-1, GY-1, GX+1, GY+2, \
                        fill = Clr[C], outline = Clr[C])
                LCan.tag_bind(ID, "<Button-1>", Command(formTPSTimeClick, \
                        BinIndex, fmti(sqrt(AveValue)), GX, GY))
                LCan.tag_bind(ID, "<Control-Button-1>", \
                        Command(formTPSTimeClick, BinIndex, \
                        fmti(sqrt(AveValue)), GX, GY))
# For next 5-minute block.
                GX += 3
# For next day.
            GY += 5
            updateMe(0)
            if TPSRunning == 0:
                formTPSTimeLines(LCan)
                formTPSTimeNumbers(LCan, 0)
                formTPSColorKey(LCan, Bin0, Bin1, Bin2, Bin3, Bin4, Bin5, Bin6)
                return
# For next channel.
        GY += PROGPropFontHeight
        L, T, R, B = LCan.bbox(ALL)
        LCan.configure(scrollregion = (0, 0, R+25, (B+15)))
        updateMe(0)
        if TPSRunning == 0:
            formTPSTimeLines(LCan)
            formTPSTimeNumbers(LCan, 0)
            formTPSColorKey(LCan, Bin0, Bin1, Bin2, Bin3, Bin4, Bin5, Bin6)
            return
    formTPSTimeLines(LCan)
    formTPSTimeNumbers(LCan, 0)
    formTPSColorKey(LCan, Bin0, Bin1, Bin2, Bin3, Bin4, Bin5, Bin6)
    return
###############################
# BEGIN: formTPSTimeLines(LCan)
# FUNC:formTPSTimeLines():2012.322
def formTPSTimeLines(LCan):
    L, T, R, B = LCan.bbox(ALL)
    for i in xrange(1, 24):
        XX = TPSBufLeft+(i*(3.0*288.0/24.0))
        ID = LCan.create_line(XX, T+PROGPropFontHeight*2, XX, B+5, \
                fill = Clr["A"])
        LCan.tag_lower(ID, ALL)
    return
#####################################
# BEGIN: formTPSTimeNumbers(LCan, GY)
# FUNC:formTPSTimeNumbers():2012.322
def formTPSTimeNumbers(LCan, GY):
    if GY == 0:
        L, T, R, B = LCan.bbox(ALL)
        GY = B+PROGPropFontHeight/2
    for i in xrange(4, 24, 4):
        XX = TPSBufLeft+(i*(3.0*288.0/24.0))
# Text with a black background.
        ID = canText(LCan, XX, GY, DClr["TX"], "%02d"%i, "c")
        L, T, R, B = LCan.bbox(ID)
        ID2 = LCan.create_rectangle(L, T-1, R, B, fill = DClr["TC"], \
                outline = DClr["TC"])
        LCan.tag_raise(ID, ID2)
    return
########################################################################
# BEGIN: formTPSColorKey(LCan, Bin0, Bin1, Bin2, Bin3, Bin4, Bin5, Bin6)
# FUNC:formTPSColorKey():2012.322
def formTPSColorKey(LCan, Bin0, Bin1, Bin2, Bin3, Bin4, Bin5, Bin6):
    L, T, R, B = LCan.bbox(ALL)
    GY = B+25
    Index = 0
    for C in ("K", "U", "C", "G", "Y", "R", "M", "E"):
        GYY = GY+PROGPropFontHeight*Index
        LCan.create_rectangle(25, GYY-5, 40, GYY+5, fill = Clr[C], \
                outline = Clr["B"])
        if Index == 0:
            canText(LCan, 45, GYY, DClr["TX"], "%s counts"% \
                    fmti(int(sqrt(eval("Bin%d"%Index)))))
        elif Index != 7:
            canText(LCan, 45, GYY, DClr["TX"], "+/- %s counts"% \
                    fmti(int(sqrt(eval("Bin%d"%Index)))))
        else:
            canText(LCan, 45, GYY, DClr["TX"], "> %s counts"% \
                    fmti(int(sqrt(Bin6))))
        Index += 1
    return
##########################
# BEGIN: formTPSChkChans()
# FUNC:formTPSChkChans():2013.070
#    Do this as a separate function, instead of as just part of the regular
#    plotting so any error message can be displayed in the right place by
#    external callers. Just make sure it gets called before plotting, because
#    formTPS does not check for any errors.
def formTPSChkChans():
# So callers don't have to check.
    if OPTPlotTPSCVar.get() == 0:
        return (0, )
    Str = OPTPlotTPSChansVar.get().strip().upper()
    if Str.endswith(","):
        Str = Str[:-1]
    Str = Str.replace(" ", "")
    if len(Str) == 0:
        return (1, "RW", \
                "TPS Chans: No channels have been entered. Either enter some or uncheck the TPS checkbutton.", \
                2)
    OPTPlotTPSChansVar.set(Str)
# Check to see that only "S" type channels are in the list.
    PlotChans = Str.split(",")
    try:
        for Chan in PlotChans:
            if QPChans[Chan[:3]][QPCHANS_TYPE] != "S":
                return (1, "RW", \
                        "TPS Chans: '%s' is not a seismic data channel."% \
                        Chan, 2)
    except KeyError:
        return (1, "RW", "TPS Chans: %s: Unknown channel."%Chan, 2)
    return (0, )
##############################
# BEGIN: formTPSMsg(Colr, Msg)
# FUNC:formTPSMsg():2012.322
def formTPSMsg(Colr, Msg):
    setMsg("TPS", Colr, Msg, 0)
    return
######################
# BEGIN: formTPSOpen()
# FUNC:formTPSOpen()
#   For others to call to bring up the TPS form (like from a menu command).
def formTPSOpen():
    OPTPlotTPSCVar.set(1)
    formTPS()
    return
#############################
# BEGIN: formTPSClear(ClrMsg)
# FUNC:formTPSClear():2012.323
#   This can be called by outsiders.
def formTPSClear(ClrMsg):
    global TPSPlotted
# Clear the TPS plot if it is up.
    if PROGFrm["TPS"] != None:
        PROGFrm["TPS"].title("TPS Plot")
        LCan = PROGCan["TPS"]
        LCan.delete("all")
        LCan.configure(scrollregion = (0, 0, 1, 1))
        LCan.configure(bg = DClr["TC"])
        if ClrMsg == True:
            setMsg("TPS", "", "")
    if OPTPlotTPSCVar.get() == 0:
        formTPSControl("close")
    TPSPlotted = False
#####################################
# BEGIN: formTPSDaysMissing(Value, e)
# FUNC:formTPSDaysMissing():2013.199
#   Just displays the number of days missing from clicks on the special
#   'days missing' lines.
def formTPSDaysMissing(Value, e):
    LCan = PROGCan["TPS"]
    if TPSPlotted == False:
        beep(1)
        return
# We don't get the position of these, so this is the best we can do.
    Cx = LCan.canvasx(e.x)
    Cy = LCan.canvasy(e.y)
    LCan.delete("TClick")
    plotMFShowTimeRule("TPS", -1)
    LCan.create_rectangle(Cx-6, Cy-6, Cx+6, Cy+6, width = 4, \
            outline = Clr["O"], tags = "TClick")
# Clear out any time square from before.
    setMsg("TPS", "", "Days missing: %d"%Value)
    return
#########################################################
# BEGIN: formTPSTimeClick(Index, Value, GX, GY, e = None)
# FUNC:formTPSTimeClick():2013.199
#   Handles Canvas clicks.
def formTPSTimeClick(Index, Value, GX, GY, e = None):
    if TPSPlotted == False:
        beep(1)
        return
    LCan = PROGCan["TPS"]
# This is a click from the Canvas().
    if Index == -1:
        Cx = LCan.canvasx(e.x)
        Cy = LCan.canvasy(e.y)
        if Cx < TPSBufLeft or Cx > (TPSBufLeft+TPSPWidth):
            setMsg("TPS", "", "")
            plotMFShowTimeRule("TPS", -1)
# Clear out any time square from before.
            LCan.delete("TClick")
# This is a click from one of the rectangles.
    else:
        LCan.delete("TClick")
        LCan.create_rectangle(GX-6, GY-6, GX+6, GY+6, width = 4, \
                outline = Clr["O"], tags = "TClick")
        Epoch = float(TPSStart+(Index*300)+150)
        Time = dt2Time(-1, 80, Epoch)
        setMsg("TPS", "", "%s: %s counts"%(Time, Value))
        plotMFShowTimeRule("TPS", Epoch)
    return
#########################
# BEGIN: formTPSControl()
# FUNC:formTPSControl():2013.082
def formTPSControl(What):
    global TPSRunning
    global TPSPlotted
    global TPSPlotData
    if What == "go":
        buttonBG(TPSPlotBut, "G", NORMAL)
        buttonBG(TPSStopBut, "R", NORMAL)
        TPSRunning = 1
        busyCursor(1)
        return
    elif What == "stop":
        if TPSRunning == 0:
            beep(1)
        else:
            buttonBG(TPSStopBut, "Y", NORMAL)
    elif What == "stopped":
        buttonBG(TPSPlotBut, "D", NORMAL)
        buttonBG(TPSStopBut, "D", DISABLED)
    elif What == "close":
        formTPSControl("stopped")
        TPSPlotted = False
        del TPSPlotData[:]
        closeForm("TPS")
        return
    TPSRunning = 0
    busyCursor(0)
    return
# END: formTPS




############################################################################
# BEGIN: formWrite(Parent, WhereMsg, TextWho, Title, FilespecVar, AllowPick)
# LIB:formWrite():2013.046
#   Writes the contents of the passed TextWho Text() widget to a file.
def formWrite(Parent, WhereMsg, TextWho, Title, FilespecVar, AllowPick):
# Sometimes it can take a while if there is a lot of text.
    updateMe(0)
    if isinstance(Parent, basestring):
        Parent = PROGFrm[Parent]
    if AllowPick == True:
        setMsg(WhereMsg, "", "")
        Filespec = formMYDF(Parent, 0, Title, dirname(FilespecVar.get()), \
                basename(FilespecVar.get()))
        if Filespec == "":
            return ""
    setMsg(WhereMsg, "CB", "Working...")
    Answer = "over"
    if exists(Filespec):
        Answer = formMYD(Parent, (("Append", LEFT, "append"), \
                ("Overwrite", LEFT, "over"), ("Cancel", LEFT, "cancel")), \
                "cancel", "YB", "Keep Everything.", \
                "The file\n\n%s\n\nalready exists. Would you like to append to that file, overwrite it, or cancel?"% \
                Filespec)
        if Answer == "cancel":
            setMsg(WhereMsg, "", "Nothing done.")
            return ""
    try:
        if Answer == "over":
            Fp = open(Filespec, "wb")
        elif Answer == "append":
            Fp = open(Filespec, "ab")
    except Exception, e:
        setMsg(WhereMsg, "MW", "Error opening file\n   %s\n   %s"% \
                (Filespec, e), 3)
        return ""
# Now that the file is OK...
    FilespecVar.set(Filespec)
    LTxt = PROGTxt[TextWho]
    N = 1
# In case the text field is empty.
    Line = "\n"
    while 1:
        if LTxt.get("%d.0"%N) == "":
            if Line != "\n":
                Fp.write(Line)
            break
# This is a little funny, but it keeps blank lines from sneaking in at the end
# of the written lines.
        if N > 1:
            Fp.write(Line)
        Line = LTxt.get("%d.0"%N, "%d.0"%(N+1))
        N += 1
    Fp.close()
    if Answer == "append":
        setMsg(WhereMsg, "WB", "Appended text to file\n   %s"%Filespec)
    elif Answer == "over":
        setMsg(WhereMsg, "WB", "Wrote text to file\n   %s"%Filespec)
# Return this in case the caller is interested.
    return Filespec
#################################################################
# BEGIN: formRead(Parent, TextWho, Title, FilespecVar, AllowPick)
# FUNC:formRead():2013.046
#   Same idea as formWrite(), but handles reading a file into a Text().
#   Only appends the text to the END of the passed Text() field.
def formRead(Parent, TextWho, Title, FilespecVar, AllowPick):
# Sometimes it can take a while if there is a lot of text.
    updateMe(0)
    if isinstance(Parent, basestring):
        Parent = PROGFrm[Parent]
    Filespec = FilespecVar.get()
    if AllowPick == True:
        Filespec = formMYDF(Parent, 0, Title, dirname(Filespec), \
                basename(Filespec))
        if Filespec == "":
            return (2, "", "Nothing done.", 0, "")
    setMsg(WhereMsg, "CB", "Working...")
    if exists(Filespec) == False:
        return (2, "RW", "File to read does not exist:\n   %s"%Filespec, 2, \
                Filespec)
    if isdir(Filespec):
        return (2, "RW", "Selected file is not a normal file:\n   %s"% \
                Filespec, 2, Filespec)
    try:
        Fp = open(Filespec, "r")
        Lines = readFileLines(Fp)
        Fp.close()
    except Exception, e:
        return (2, "MW", "Error opening file\n   %s\n   %s"%(Filespec, e), 3, \
                Filespec)
# Now that the file is OK...
    LTxt = PROGTxt[TextWho]
    if int(LTxt.index('end-1c').split('.')[0]) > 1:
        LTxt.insert(END, "\n")
    for Line in Lines:
        LTxt.insert(END, "%s\n"%Line)
    FilespecVar.set(Filespec)
    if len(Lines) == 1:
        return (0, "", "Read %d line from file\n   %s"%(len(Lines), \
                Filespec), 0, Filespec)
    else:
        return (0, "", "Read %d lines from file\n   %s"%(len(Lines), \
                Filespec), 0, Filespec)
# END: formWrite




#################################################
# BEGIN: formWritePS(Parent, VarSet, FilespecVar)
# LIB:formWritePS():2012.151
def formWritePS(Parent, VarSet, FilespecVar):
    setMsg(VarSet, "", "")
    if isinstance(Parent, basestring):
        Parent = PROGFrm[Parent]
    LCan = PROGCan[VarSet]
    Running = 0
# The form may not have an associated Running var.
    try:
        Running = eval("%sRunning.get()"%VarSet)
    except:
        pass
    if Running != 0:
        setMsg(VarSet, "YB", "I'm busy...", 2)
        sleep(.5)
        return
# This may not make any difference depending on the form.
    try:
        if LCan.cget("bg") != "#FFFFFF":
            Answer = formMYD(Parent, (("Stop And Let Me Redo It", TOP, \
                    "stop"), ("Continue anyway", TOP, "cont")), "stop", \
                    "YB", "Charcoal Footprint?", \
                    "For best results the background color of the plot area should be white. In fact, for most plots the .ps file's background will be white, and so will the text, so you won't be able to see anything.  Do you want to stop and replot, or continue anyway?")
        if Answer == "stop":
            return
    except:
        pass
# This will cryptically crash if the canvas is empty.
    try:
        L, T, R, B = LCan.bbox(ALL)
# Postscript is so litteral.
        R += 15
        B += 15
    except:
        setMsg(VarSet, "RW", "Is the area to write blank?", 2)
        return
    Dir = dirname(FilespecVar.get())
    File = basename(FilespecVar.get())
    Filespec = formMYDF(Parent, 3, ".ps File To Save To...", Dir, File, "", \
            ".ps", False)
    if Filespec == "":
        return False
    Answer = overwriteFile(Parent, Filespec)
    if Answer == "stop":
        return
    setMsg(VarSet, "CB", "Working on a %d x %d pixel area..."%(R, B))
# This might crash if the canvas is huge?
    try:
        Ps = LCan.postscript(height = B, width = R, pageheight = B, \
                pagewidth = R, pageanchor = "nw", pagex = 0, pagey = B, \
                x = 0, y = 0, colormode = "color")
    except Exception, e:
        setMsg(VarSet, "MW", "Error converting canvas to postscript.\n   %s"% \
                e, 3)
        return
    try:
        Fp = open(Filespec, "w")
        Fp.write(Ps)
        Fp.close()
    except Exception, e:
        setMsg(VarSet, "MW", "Error saving postscript commands.\n   %s"%e, 3)
        return
    setMsg(VarSet, "", "Wrote %d x %d area (%s bytes) to file\n   %s"% \
            (R, B, fmti(len(Ps)), Filespec))
    FilespecVar.set(Filespec)
    return
# END: formWritePS




##############################
# BEGIN: getFolderSize(Folder)
# LIB:getFolderSize():2011.300
#   Stolen right from the Web from Samual Lampa, Dec 6, 2010.
def getFolderSize(Folder):
    TotalSize = getsize(Folder)
    for Item in listdir(Folder):
        Itempath = Folder+sep+Item
        if isfile(Itempath):
            TotalSize += getsize(Itempath)
        elif isdir(Itempath):
            TotalSize += getFolderSize(Itempath)
    return TotalSize
# END: getFolderSize




#######################
# BEGIN: getGMT(Format)
# LIB:getGMT():2013.037
#   Gets the time in various forms from the system.
def getGMT(Format):
# YYYY:DOY:HH:MM:SS GMT
    if Format == 0:
        return strftime("%Y:%j:%H:%M:%S", gmtime(time()))
# YYYYDOYHHMMSS GMT
    elif Format == 1:
        return strftime("%Y%j%H%M%S", gmtime(time()))
# YYYY-MM-DD GMT
    elif Format == 2:
        return strftime("%Y-%m-%d", gmtime(time()))
# YYYY-MM-DD HH:MM:SS GMT
    elif Format == 3:
        return strftime("%Y-%m-%d %H:%M:%S", gmtime(time()))
# YYYY, MM and DD GMT returned as ints
    elif Format == 4:
        GMT = gmtime(time())
        return (GMT[0], GMT[1], GMT[2])
# YYYY-Jan-01 GMT
    elif Format == 5:
        return strftime("%Y-%b-%d", gmtime(time()))
# YYYYMMDDHHMMSS GMT
    elif Format == 6:
        return strftime("%Y%m%d%H%M%S", gmtime(time()))
# Reftek Texan (year-1984) time stamp in BBBBBB format (GMT)
    elif Format == 7:
        GMT = gmtime(time())
        return pack(">BBBBBB", (GMT[0]-1984), 0, 1, GMT[3], GMT[4], GMT[5])
# Number of seconds since Jan 1, 1970.
    elif Format == 8:
        return time()
# YYYY-MM-DD/DOY HH:MM:SS GMT
    elif Format == 9:
        return strftime("%Y-%m-%d/%j %H:%M:%S", gmtime(time()))
# YYYY-MM-DD/DOY GMT
    elif Format == 10:
        return strftime("%Y-%m-%d/%j", gmtime(time()))
# YYYY, DOY, HH, MM, SS GMT returned as ints
    elif Format == 11:
        GMT = gmtime(time())
        return (GMT[0], GMT[7], GMT[3], GMT[4], GMT[5])
# HH:MM:SS GMT
    elif Format == 12:
        return strftime("%H:%M:%S", gmtime(time()))
# YYYY:DOY:HH:MM:SS LT
    elif Format == 13:
        return strftime("%Y:%j:%H:%M:%S", localtime(time()))
# HHMMSS GMT
    elif Format == 14:
        return strftime("%H%M%S", gmtime(time()))
# YYYY-MM-DD LT
    elif Format == 15:
        return strftime("%Y-%m-%d", localtime(time()))
# YYYY-MM-DD/DOY Day LT
    elif Format == 16:
        return strftime("%Y-%m-%d/%j %A", localtime(time()))
# MM-DD LT
    elif Format == 17:
        return strftime("%m-%d", localtime(time()))
# YYYY, MM and DD LT returned as ints
    elif Format == 18:
        LT = localtime(time())
        return (LT[0], LT[1], LT[2])
# YYYY-MM-DD/DOY HH:MM:SS Day LT
    elif Format == 19:
        return strftime("%Y-%m-%d/%j %H:%M:%S %A", localtime(time()))
# Return GMT-LT difference.
    elif Format == 20:
        Secs = time()
        LT = localtime(Secs)
        GMT = gmtime(Secs)
        return dt2Timeymddhms(-1, LT[0], -1, -1, LT[7], LT[3], LT[4], LT[5])- \
                dt2Timeymddhms(-1, GMT[0], -1, -1, GMT[7], GMT[3], GMT[4], \
                GMT[5])
    return ""
# END: getGMT




###########################################
# BEGIN: getPROGStarted(Warn, AskWAI, Load)
# LIB:getPROGStarted():2012.135qpeek
# QPEEK: Added calls to loadChanPrefsSetups().
#   Used by everyone to look for the setups file and get the party started.
#   Warn = if False the function won't generate any error responses, except
#          True or False.
#   Load = True/False, some programs will just want PROGSetupsDirVar set.
# This does not get saved in the setups file.
PROGSetupsDirVar = StringVar()

def getPROGStarted(Warn, AskWAI, Load):
    try:
        if PROGSystem == 'dar' or PROGSystem == 'lin' or PROGSystem == 'sun':
            Dir = environ["HOME"]
            LookFor = "HOME"
# Of course Windows had to be different.
        elif PROGSystem == 'win':
            Dir = environ["HOMEDRIVE"]+environ["HOMEPATH"]
            LookFor = "HOMEDRIVE+HOMEPATH"
        else:
            if Warn == False:
                return False
            else:
                return (2, "RW", \
                        "I don't know how to get the HOME directory on this system. This system is not supported: %s"% \
                        PROGSystem, 2, "")
        if Dir.endswith(sep) == False:
            Dir += sep
    except Exception, e:
        if Warn == False:
            return False
        else:
            return (2, "MW", \
                    "There is an error building the directory to the setups file. The error is:\n\n%s\n\nThis will need to be corrected before this program can be used."% \
                    e, 3, "")
    if access(Dir, W_OK) == False:
        if Warn == False:
            return False
        else:
            return (2, "MW", \
                    "The %s directory\n\n%s\n\nis not accessible for writing. This will need to be corrected before this program may be used."% \
                    (LookFor, Dir), 3, "")
    PROGSetupsDirVar.set(Dir)
    if AskWAI == True:
        Ret = setWhoAmI()
        if Ret[0] == 2:
            if Warn == False:
                return False
            else:
                return (2, "YB", "You wanna quit? I quit.", 2)
    if Load == True:
        Ret = loadPROGSetups()
# For QPEEK.
# Sneak this in before we check the return value of loadPROGSetups().
        loadChanPrefsSetups()
        if Ret[0] != 0:
            if Warn == False:
                return False
            else:
                return Ret
# loadPROGSetups() still might return (0, message).
        else:
            if Warn == False:
                return True
            else:
                return Ret
    if Warn == False:
        return True
    else:
        return (0, )
###############################
# BEGIN: getPROGStartDir(Which)
# FUNC:getPROGStartDir():2010.181
def getPROGStartDir(Which):
# PETM
    if Which == 0:
        Answer = formMYDF(Root, 1, "Pick A Starting Directory", \
                PROGSetupsDirVar.get(), "", \
                "This may be the first time this program has been started on\nthis computer or in this account. Select a directory for\nthe program to use as the directory where all files should\nstart out being saved. Click the OK button IF the displayed\ndirectory is OK to use.")
# POCUS, CHANGEO, HOCUS...
    elif Which == 1:
        Answer = formMYDF(Root, 1, "Pick A Starting Directory", \
                PROGSetupsDirVar.get(), "", \
                "This may be the first time this program has been started on\nthis computer or in this account. Select a directory for\nthe program to use as the directory where all files should\nstart out being saved -- NOT necessarily where any data files\nmay be. We'll get to that later. Click the OK button if the\ndisplayed directory is OK to use.")
    elif Which == 2:
# LOGPEEK, QPEEK (no messages file)
        Answer = formMYDF(Root, 1, "Pick A Starting Directory...", \
                PROGSetupsDirVar.get(), "", \
                "This may be the first time this program has been started\non this computer or in this account. Select a directory\nfor the program to use as a starting point -- generally\nwhere some data files to read are located.\nClick the OK button to use the displayed\ndirectory.")
    return Answer
# END: getPROGStarted




###########################
# BEGIN: getRange(Min, Max)
# LIB:getRange():2008.360
#   Returns the absolute value of the difference between Min and Max.
def getRange(Min, Max):
    if Min <= 0 and Max >= 0:
        return Max+abs(Min)
    elif Min <= 0 and Max <= 0:
        return abs(Min-Max)
    elif Max >= 0 and Min >= 0:
        return Max-Min
# END: getRange




#################
# BEGIN: intt(In)
# LIB:intt():2009.102
#   Handles all of the annoying shortfalls of the int() function (vs C).
def intt(In):
    In = str(In).strip()
    if In == "":
        return 0
# Let the system try it first.
    try:
        return int(In)
    except ValueError:
        Number = ""
        for c in In:
            if c.isdigit():
                Number += c
            elif Number == "" and (c == "-" or c == "+"):
                Number += c
            elif c == ",":
                continue
            else:
                break
        try:
            return int(Number)
        except ValueError:
            return 0
# END: intt




###################################################################
# BEGIN: labelEntry2(Sub, Format, LabTx, TTLen, TTTx, TxVar, Width)
# LIB:labelEntry2():2013.142
#   For making simple  Label(): Entry() pairs.
#   Format: 10 = Aligned LEFT-RIGHT, entry field is disabled
#           11 = Aligned LEFT-RIGHT, entry field is normal
#           20 = Aligned TOP-BOTTOM, entry field disabled
#           21 = Aligned TOP-BOTTOM, entry field is normal
#    LabTx = the text of the label. No LabTx, no label
#    TTLen = The length of the tooltip text
#     TTTx = The text of the label's tooltip. No TTTx, no tooltip
#    TxVar = Var for the entry field
#    Width = Width to make the field, 0 = .pack(side=LEFT, expand=YES, fill=X)
#            Width should only be 0 if Format is 10 or 11.
def labelEntry2(Sub, Format, LabTx, TTLen, TTTx, TxVar, Width):
    if LabTx != "":
        if TTTx != "":
            Lab = Label(Sub, text = LabTx)
            if Format == 11 or Format == 10:
                Lab.pack(side = LEFT)
            elif Format == 21 or Format == 20:
                Lab.pack(side = TOP)
            ToolTip(Lab, TTLen, TTTx)
        else:
# Don't create the extra object if we don't have to.
            if Format == 11 or Format == 10:
                Label(Sub, text = LabTx).pack(side = LEFT)
            elif Format == 21 or Format == 20:
                Label(Sub, text = LabTx).pack(side = TOP)
    if Width == 0:
        Ent = Entry(Sub, textvariable = TxVar)
    else:
        Ent = Entry(Sub, textvariable = TxVar, width = Width+1)
    if Format == 11 or Format == 10:
        if Width != 0:
            Ent.pack(side = LEFT)
        else:
            Ent.pack(side = LEFT, expand = YES, fill = X)
    elif Format == 21 or Format == 20:
        Ent.pack(side = TOP)
    if Format == 10 or Format == 20:
        Ent.configure(state = DISABLED, bg = Clr["D"])
    return Ent
# END: labelEntry2




####################################################
# BEGIN: labelTip(Sub, LText, Side, TTWidth, TTText)
# LIB:labelTip():2006.262
#   Creates a label and assignes the passed ToolTip to it. Returns the Label()
#   widget.
def labelTip(Sub, LText, Side, TTWidth, TTText):
    Lab = Label(Sub, text = LText)
    Lab.pack(side = Side)
    ToolTip(Lab, TTWidth, TTText)
    return Lab
# END: labelTip




#####################################################
# BEGIN: list2Str(TheList, Delim = ", ", Sort = True)
# LIB:list2Str():2013.295
def list2Str(TheList, Delim = ", ", Sort = True):
    if isinstance(TheList, list) == False:
        return TheList
    if Sort == True:
        TheList.sort()
    Ret = ""
# If there is any funny-business (which has been seen).
    for Item in TheList:
        try:
            Ret += str(Item)+Delim
        except UnicodeEncodeError:
            Ret += "Error"+Delim
    return Ret[:-(len(Delim))]
# END: list2Str




#########################
# BEGIN: listKnownChans()
# FUNC:listKnownChans():2013.171
def listKnownChans():
    Chans = QPChans.keys()
    Chans.sort()
# See formMYDT().
    Msg = ["}"]
    Msg.append("These are the channels that QPEEK knows how to deal with. If a channel needs to be added to this list it requires changing the program.")
    for Chan in Chans:
        QPC = QPChans[Chan]
        if QPC[QPCHANS_PLOT] == 0:
            continue
        Msg.append("")
        Msg.append(QPC[QPCHANS_LABEL])
        Msg.append("   Desc: %s"%QPC[QPCHANS_DESC])
        Msg.append("   Units: %s"%QPC[QPCHANS_UNITS])
        Value = QPC[QPCHANS_DECODE]
        if Value == 1:
            Msg.append("   Decode: 1 count = 1 unit")
        elif Value == 2:
            Msg.append("   Decode: 1 count = .150 units")
        elif Value == 3:
            Msg.append("   Decode: 1 count = .1 units")
        elif Value == 4:
            Msg.append("   Decode: 1 count = 1 unit, but kept >= 0")
        Value = QPC[QPCHANS_PLOTTER]
        if Value == "mln":
            Msg.append("   Plot: multi-line normal, one color, line and maybe dots")
        elif Value == "mlmp":
            Msg.append("   Plot: multi-line mass position, multi-color, always line and dots")
        elif Value == "mll":
            Msg.append("   Plot: multi-line line, one color, line only")
        elif Value == "mlls":
            Msg.append("   Plot: multi-line line seismic, one color, line only, can apply bit weights")
        elif Value == "mp":
            Msg.append("   Plot: mass position, multi-color, single line")
        elif Value == "strz":
            Msg.append("   Plot: single line, \"good\"=nothing or green, \"note\"=cyan, \"hey!\"=yellow, \"bad\"=red, \"yikes!\"=magenta")
    formMYDT(Root, (("(OK)", TOP, "ok"), ), "ok", "WB", "Known Channels", \
            WORD, Msg)
    return
# END: listKnownChans




##############################
# BEGIN: loadChanPrefsSetups()
# FUNC:loadChanPrefsSetups():2013.191
#   This is basically the same as loadPROGSetups(), but only for the Channel
#   Preferences information. If anything goes wrong wiht loading the regular
#   setups it will probably go wrong here too, but this function will just
#   return.
ChanPrefsFilespec = ""

def loadChanPrefsSetups():
    global ChanPrefsFilespec
    Debug = False
# Some programs may not have PROGSetupsDirVar set to anything, or even call
# this function, but check and set this just in case. ./ may not point to
# anywhere sensible, but this is the best we can do.
    SetupsDir = PROGSetupsDirVar.get()
    if SetupsDir == "":
        SetupsDir = "%s%s"%(abspath("."), sep)
    ChanPrefsFilespec = SetupsDir+"set"+PROG_NAMELC+"chanprefs.set"
# The .set file may not be there.
    if exists(ChanPrefsFilespec) == False:
        if Debug == True:
            print("%s not found."%ChanPrefsFilespec)
        return
    try:
        Fp = open(ChanPrefsFilespec, "rb")
    except Exception, e:
        if Debug == True:
            print("Error opening setups file\n   %s\n   %s"% \
                (ChanPrefsFilespec, e))
        return
    Found = False
    Vers = False
# Just catch anything that might go wrong and blame it on the .set file.
    try:
        while 1:
            Line = Fp.readline()
            if Line.strip() == "":
                break
            if Line.startswith(PROG_NAME+":"):
                Parts = map(strip, Line.split())
# In case an old setups file is read that does not have the version item.
                Parts += [""]*(3-len(Parts))
# If the version doesn't match what the program wants then don't set Vers and
# everything will be left with it's default value.
                if Parts[2] == PROG_CPSETUPSVERS:
                    Vers = True
                Found = True
                continue
            if Found == True and Vers == True:
                Parts = map(strip, Line.split(";", 1))
                for Item in ChanPrefsSetups:
                    if Parts[0] == Item:
                        if isinstance(eval(Item), StringVar):
                            eval(Item).set(Parts[1])
                            break
                        elif isinstance(eval(Item), IntVar):
                            eval(Item).set(int(Parts[1]))
                            break
        Fp.close()
        if Found == False:
            if Debug == True:
                print("No Chan Prefs setups found in\n   %s"% \
                    ChanPrefsFilespec)
            return
        else:
            if Vers == False:
                if Debug == True:
                    print("Chan Prefs setups version mismatch.")
                return
            if Debug == True:
                print("Setups loaded from\n   %s"%ChanPrefsFilespec)
            return
    except Exception, e:
        Fp.close()
        if Debug == True:
            print("Error loading chan prefs setups from\n   %s\n   %s\n   Was loading line %s"% \
                (ChanPrefsFilespec, e, Line))
        return
##############################
# BEGIN: saveChanPrefsSetups()
# FUNC:saveChanPrefsSetups():2013.191
def saveChanPrefsSetups():
    Debug = False
    try:
        Fp = open(ChanPrefsFilespec, "wb")
    except Exception, e:
        if Debug == True:
            print("Error opening chan prefs setups file\n   %s\n   %s"% \
                (ChanPrefsFilespec, e))
    try:
        Fp.write("%s: %s %s\n"%(PROG_NAME, PROG_VERSION, PROG_CPSETUPSVERS))
        for Item in ChanPrefsSetups:
            if isinstance(eval(Item), StringVar):
                Fp.write("%s; %s\n"%(Item, eval(Item).get()))
            elif isinstance(eval(Item), IntVar):
                Fp.write("%s; %d\n"%(Item, eval(Item).get()))
        Fp.close()
        if Debug == True:
            print("Setups saved to\n   %s"%ChanPrefsFilespec)
        return
    except Exception, e:
        Fp.close()
        if Debug == True:
            print("Error saving setups to\n   %s\n   %s"% \
                (ChanPrefsFilespec, e))
# END: loadChanPrefsSetups




#########################
# BEGIN: loadPROGSetups()
# LIB:loadPROGSetups():2013.107
#   A standard setups file loader for programs that don't require anything
#   special loaded from the .set file just the PROGSetups items.
PROGSetupsFilespec = ""

def loadPROGSetups():
    global PROGSetupsFilespec
# Some programs may not have PROGSetupsDirVar set to anything, or even call
# this function, but check and set this just in case. ./ may not point to
# anywhere sensible, but this is the best we can do.
    SetupsDir = PROGSetupsDirVar.get()
    if SetupsDir == "":
        SetupsDir = "%s%s"%(abspath("."), sep)
    PROGSetupsFilespec = SetupsDir+"set"+PROG_NAMELC+".set"
# The .set file may not be there.
    if exists(PROGSetupsFilespec) == False:
        return (1, "", "Setups file not found. Was looking for\n   %s"% \
                PROGSetupsFilespec, 0, "")
    try:
        Fp = open(PROGSetupsFilespec, "rb")
    except Exception, e:
        return (2, "MW", "Error opening setups file\n   %s\n   %s"% \
                (PROGSetupsFilespec, e), 3, "")
    Found = False
    Vers = False
# Just catch anything that might go wrong and blame it on the .set file.
    try:
        while 1:
            Line = Fp.readline()
            if Line.strip() == "":
                break
            if Line.startswith(PROG_NAME+":"):
                Parts = map(strip, Line.split())
# In case an old setups file is read that does not have the version item.
                Parts += [""]*(3-len(Parts))
# If the version doesn't match what the program wants then don't set Vers and
# everything will be left with it's default value.
                if Parts[2] == PROG_SETUPSVERS:
                    Vers = True
                Found = True
                continue
            if Found == True and Vers == True:
                Parts = map(strip, Line.split(";", 1))
                for Item in PROGSetups:
                    if Parts[0] == Item:
                        if isinstance(eval(Item), StringVar):
                            eval(Item).set(Parts[1])
                            break
                        elif isinstance(eval(Item), IntVar):
                            eval(Item).set(int(Parts[1]))
                            break
        Fp.close()
        if Found == False:
            return (1, "YB", "No %s setups found in\n   %s"%(PROG_NAME, \
                    PROGSetupsFilespec), 2, "")
        else:
            if Vers == False:
                return (1, "YB", "Setups version mismatch. Using defaults.", \
                        0, "")
            return (0, "WB", "Setups loaded from\n   %s"%PROGSetupsFilespec, \
                    0, "")
    except Exception, e:
        Fp.close()
        return (2, "MW", \
           "Error loading setups from\n   %s\n   %s\n   Was loading line %s"% \
                (PROGSetupsFilespec, e, Line), 3, "")
#########################
# BEGIN: savePROGSetups()
# FUNC:savePROGSetups():2013.106
def savePROGSetups():
    try:
        Fp = open(PROGSetupsFilespec, "wb")
    except Exception, e:
        print ("savePROGSetups(): %s"%e)
        return (2, "MW", "Error opening setups file\n   %s\n   %s"% \
                (PROGSetupsFilespec, e), 3, "")
    try:
        Fp.write("%s: %s %s\n"%(PROG_NAME, PROG_VERSION, PROG_SETUPSVERS))
        for Item in PROGSetups:
            if isinstance(eval(Item), StringVar):
                Fp.write("%s; %s\n"%(Item, eval(Item).get()))
            elif isinstance(eval(Item), IntVar):
                Fp.write("%s; %d\n"%(Item, eval(Item).get()))
        Fp.close()
        return (0, "", "Setups saved to\n   %s"%PROGSetupsFilespec, 0, "")
    except Exception, e:
        Fp.close()
        return (2, "MW", "Error saving setups to\n   %s\n   %s"% \
                (PROGSetupsFilespec, e), 3, "")
###########################
# BEGIN: deletePROGSetups()
# FUNC:deletePROGSetups():2011.343
def deletePROGSetups():
    Answer = formMYD(Root, (("Delete And Quit", TOP, "doit"), ("Cancel", \
            TOP, "cancel")), "cancel", "YB", "Be careful.", \
            "This will delete the current setups file and quit the program. This should only need to be done if the contents of the current setups file is known to be causing the program problems.")
    if Answer == "cancel":
        return
    try:
        remove(PROGSetupsFilespec)
    except Exception, e:
        formMYD(Root, (("(OK)", TOP, "ok"), ), "ok", "MW", "Oh No.", \
                "The setups file could not be deleted.\n\n%s"%e)
        return
    progQuitter(False)
    return
# END: loadPROGSetups




#########################################
# BEGIN: loadSourceFiles(Filebox, VarSet)
# FUNC:loadSourceFiles():2013.047
#   Looks through the directory specified in the PROGDataDirVar and creates a
#   list of the files that it comes across which it places in Filebox.
# Don't remember the value of this in PROGSetups.
OPTCalcFileSizesCVar = IntVar()

def loadSourceFiles(Filebox, VarSet):
    Filebox.delete(0, END)
    setMsg(VarSet, "CB", "Working...")
    Dir = PROGDataDirVar.get()
# You never know about those users.
    if Dir.endswith(sep) == False:
        PROGDataDirVar.set(Dir+sep)
        Dir += sep
    CalcFileSizes = OPTCalcFileSizesCVar.get()
# Not all listboxes will have a find field.
    try:
        FileFind = eval("%sLbxFindVar"%VarSet).get().strip().upper()
    except:
        FileFind = ""
    if exists(Dir) == False:
        setMsg(VarSet, "RW", "Entered data directory does not exist.", 2)
        return
    Files = listdir(Dir)
    Files.sort()
    BMSFound = 0
    ALLFound = 0
    SOHFound = 0
    SDRFound = 0
    NANFound = 0
    ANTFound = 0
# Go through the files and pick out each type.
    for File in Files:
        if File.startswith(".") or File.startswith("_"):
            continue
        FileLC = File.lower()
        if FileLC.endswith(".bms"):
            if CalcFileSizes == 1:
                Size = getFolderSize(Dir+File)
                Filename = "%s (%s)"%(File, diskSizeFormat("b", Size))
            else:
                Filename = File
            Filebox.insert(END, Filename)
            BMSFound += 1
    if BMSFound > 0:
        Filebox.insert(END, "")
    for File in Files:
        if File.startswith(".") or File.startswith("_"):
            continue
        FileLC = File.lower()
        if FileLC.endswith(".all"):
            if CalcFileSizes == 1:
                Size = getsize(Dir+File)
                Filename = "%s (%s)"%(File, diskSizeFormat("b", Size))
            else:
                Filename = File
            Filebox.insert(END, Filename)
            ALLFound += 1
    if ALLFound > 0:
        Filebox.insert(END, "")
    for File in Files:
        if File.startswith(".") or File.startswith("_"):
            continue
        FileLC = File.lower()
        if FileLC.endswith(".soh"):
            if CalcFileSizes == 1:
                Size = getsize(Dir+File)
                Filename = "%s (%s)"%(File, diskSizeFormat("b", Size))
            else:
                Filename = File
            Filebox.insert(END, Filename)
            SOHFound += 1
    if SOHFound > 0:
        Filebox.insert(END, "")
    for File in Files:
        if File.startswith(".") or File.startswith("_"):
            continue
        FileLC = File.lower()
        if FileLC.endswith(".sdr"):
            if CalcFileSizes == 1:
                Size = getFolderSize(Dir+File)
                Filename = "%s (%s)"%(File, diskSizeFormat("b", Size))
            else:
                Filename = File
            Filebox.insert(END, Filename)
            SDRFound += 1
    if SDRFound > 0:
        Filebox.insert(END, "")
    for File in Files:
        if File.startswith(".") or File.startswith("_"):
            continue
        FileLC = File.lower()
        if FileLC.endswith(".nan"):
            if CalcFileSizes == 1:
                Size = getFolderSize(Dir+File)
                Filename = "%s (%s bytes)"%(File, diskSizeFormat("b", Size))
            else:
                Filename = File
            Filebox.insert(END, Filename)
            NANFound += 1
    if NANFound > 0:
        Filebox.insert(END, "")
    for File in Files:
        if File.startswith(".") or File.startswith("_"):
            continue
        FileLC = File.lower()
        if FileLC.endswith(".ant"):
            if CalcFileSizes == 1:
                Size = getFolderSize(Dir+File)
                Filename = "%s (%s bytes)"%(File, diskSizeFormat("b", Size))
            else:
                Filename = File
            Filebox.insert(END, Filename)
            ANTFound += 1
    if BMSFound == 0 and ALLFound == 0 and SOHFound == 0 and \
            SDRFound == 0 and NANFound == 0 and ANTFound == 0:
        Filebox.insert(END, "Looking for:")
        Filebox.insert(END, "")
        Filebox.insert(END, " .bms = Baler memory stick folder")
        Filebox.insert(END, "        (with data and/or sdata)")
        Filebox.insert(END, " .all = EZBaler ALL file")
        Filebox.insert(END, " .soh = EZBaler SOH only file")
        Filebox.insert(END, " .sdr = sdrsplit files folder")
        Filebox.insert(END, "        (separated by channel)")
        Filebox.insert(END, " .nan = Nanometrics folder of")
        Filebox.insert(END, "        seed or mini-seed channel")
        Filebox.insert(END, "        files maybe with some")
        Filebox.insert(END, "        .csv files")
        Filebox.insert(END, " .ant = Antelope files folder")
        Filebox.insert(END, "        (channel files and/or")
        Filebox.insert(END, "        multiplexed)")
        setMsg(VarSet, "YB", \
                "No recognized data source files found in\n   %s"%Dir)
    else:
        setMsg(VarSet, "WB", \
                "Found   .bms folders: %d   .all files: %d   .soh files: %d   .sdr folders: %d   .nan folders: %d   .ant folders: %d"% \
                (BMSFound, ALLFound, SOHFound, SDRFound, NANFound, ANTFound))
# Add any files we may be looking for in their own section at the bottom of
# the list.
    if FileFind != "":
        Finds = []
        for Index in xrange(0, Filebox.size()):
                File = Filebox.get(Index)
                if FileFind in File.upper():
                    Finds.append(File)
        if len(Finds) > 0:
            Finds.sort()
            Finds.reverse()
            Filebox.insert(0, "")
            for Find in Finds:
                Filebox.insert(0, Find)
    return
######################################################
# BEGIN: loadSourceFilesCmd(Filebox, VarSet, e = None)
# FUNC:loadSourceFilesCmd():2012.107
def loadSourceFilesCmd(Filebox, VarSet, e = None):
    if VarSet == "MF":
        setMsg("INFO", "", "")
    setMsg(VarSet, "", "")
    loadSourceFiles(Filebox, VarSet)
    return
################################################################
# BEGIN: loadSourceFilesClearLbxFindVar(Filebox, VarSet, Reload)
# FUNC:loadSourceFilesClearLbxFindVar()2012.093
def loadSourceFilesClearLbxFindVar(Filebox, VarSet, Reload):
    eval("%sLbxFindVar"%VarSet).set("")
    if Reload == True:
        loadSourceFiles(Filebox, VarSet)
    return
# END: loadSourceFiles




#################
# BEGIN: m2MMM(m)
# LIB:m2MMM():2013.035
def m2MMM(m):
    try:
        M = int(m)
    except:
        return "ERR"
    if M == 1:
        return "JAN"
    elif M == 2:
        return "FEB"
    elif M == 3:
        return "MAR"
    elif M == 4:
        return "APR"
    elif M == 5:
        return "MAY"
    elif M == 6:
        return "JUN"
    elif M == 7:
        return "JUL"
    elif M == 8:
        return "AUG"
    elif M == 9:
        return "SEP"
    elif M == 10:
        return "OCT"
    elif M == 11:
        return "NOV"
    elif M == 12:
        return "DEC"
    return "ERR"
#################
# BEGIN: MMM2m(M)
# FUNC:MMM2m():2013.035
def MMM2m(M):
    M = M.upper()
    if M.find("JAN") != -1:
        return 1
    elif M.find("FEB") != -1:
        return 2
    elif M.find("MAR") != -1:
        return 3
    elif M.find("APR") != -1:
        return 4
    elif M.find("MAY") != -1:
        return 5
    elif M.find("JUN") != -1:
        return 6
    elif M.find("JUL") != -1:
        return 7
    elif M.find("AUG") != -1:
        return 8
    elif M.find("SEP") != -1:
        return 9
    elif M.find("OCT") != -1:
        return 10
    elif M.find("NOV") != -1:
        return 11
    elif M.find("DEC") != -1:
        return 12
    return 0
# END: m2MMM




##################################
# BEGIN: mouseWheel(Who, e = None)
# LIB:mouseWheel():2012.317
#    Bind <MouseWheel> for Windows and <Button-4>/<Button-5> for others to
#    this to get button scrolling.
def mouseWheel(Who, e = None):
    if e.num == 5 or e.delta == -120:
        Dir = 1
    if e.num == 4 or e.delta == 120:
        Dir = -1
    Who.yview_scroll(Dir, "units")
    return
# END: mouseWheel




#########################
# BEGIN: msgCenter(Which)
# FUNC:msgCenter():2012.325
def msgCenter(Which):
    if Which == "spikes":
        if OPTWhackAntSpikesCVar.get() == 0:
            setMsg("MF", "", \
         "Turned off spike whacking. Must Read source data to show change.", 1)
        else:
            setMsg("MF", "", \
          "Turned on spike whacking. Must Read source data to show change.", 1)
    return
# END: msgCenter




##############################
# BEGIN: nsew2pm(Which, Value)
# LIB:nsew2pm():2012.089
def nsew2pm(Which, Value):
    if Value == "?":
        return "?"
    if Which == "lat":
        try:
            if Value[0] == "N":
                return Value[1:]
            elif Value[0] == "S":
                return "-"+Value[1:]
# Allow positions that are already + or -.
            elif Value[0].isdigit() or Value[0] == "-" or Value[0] == "+":
                return Value
            else:
                return "?"
        except IndexError:
            return "?"
    elif Which == "lon":
        try:
            if Value[0] == "E":
                return Value[1:]
            elif Value[0] == "W":
                return "-"+Value[1:]
            elif Value[0].isdigit() or Value[0] == "-" or Value[0] == "+":
                return Value
            else:
                return "?"
        except IndexError:
            return "?"
###############################
# BEGIN: pm2nsew(Which, SValue)
# FUNC:pm2nsew():2012.089
#   A little trickier that originally suspected since Value can be a number or
#   a string, and if a string it may or may not have a leading + sign, and we
#   don't just want to convert it to a float and go from there because of
#   introducing binary conversion errors and extra digits, and we never want
#   the - sign.
def pm2nsew(Which, Value):
    if Value == "?":
        return "?"
    Value = str(Value)
    if Value.startswith("+"):
        Value = Value[1:]
    FValue = floatt(Value)
    if Which == "lat":
# Just in case the caller passes the wrong thing.
        if Value.startswith("N") or Value.startswith("S"):
            return Value
        if FValue >= 0.0:
            return "N%09.6f"%FValue
        else:
            return "S%09.6f"%abs(FValue)
    elif Which == "lon":
        if Value.startswith("E") or Value.startswith("W"):
            return Value
        if FValue >= 0.0:
            return "E%010.6f"%FValue
        else:
            return "W%010.6f"%abs(FValue)
# END: nsew2pm




###########################
# BEGIN: openDDIR(e = None)
# FUNC:openDDIR():2012.101
#   Just for OSX. The user can right-click on the DDIR entry field and open
#   a Finder window on the directory. Don't know if it works across networks
#   and stuff.
def openDDIR(e = None):
    Fp = popen("open %s"%PROGDataDirVar.get())
    Fp.close()
    return
################################
# BEGIN: openDDIRPopup(e = None)
# FUNC:openDDIRPopup():2013.282
def openDDIRPopup(e = None):
    Xx = Root.winfo_pointerx()
    Yy = Root.winfo_pointery()
    PMenu = Menu(e.widget, font = PROGOrigPropFont, tearoff = 0, \
            bg = Clr["D"], bd = 2, relief = GROOVE)
    PMenu.add_command(label = "Open This Directory", command = openDDIR)
    PMenu.tk_popup(Xx, Yy)
    return
# END: openDDIR




########################################
# BEGIN: overwriteFile(Parent, Filespec)
# LIB:overwriteFile():2012.151
#   Returns False if the file does not exist, or the Answer.
def overwriteFile(Parent, Filespec):
    if exists(Filespec):
        if isinstance(Parent, basestring):
            Parent = PROGFrm[Parent]
        Answer = formMYD(Parent, (("Overwrite", LEFT, "over"), ("(Stop)", \
                LEFT, "stop")), "stop", "YB", "Well?", \
              "File %s already exists. Do you want to overwrite it or stop?"% \
                basename(Filespec))
        return Answer
    return False
# END: overwriteFile




#########################
# BEGIN: plotMF(e = None)
# FUNC:plotMF():2013.081
# These are the earliest and latest times of the source data file. These will
# also be affected by any date entries in the From and To fields. These get
# set in fileSelected().
QPEarliestData = 0.0
QPLatestData = 0.0
# These are the earlist and latest times of what was last plotted. These will
# change with zooming in and out.
QPEarliestCurr = 0.0
QPLatestCurr = 0.0
MFBufLeft = 0
MFPWidth = 0
MFTimeLineTop = 0
MFTimeLineBottom = 0
MFPlotTop = 0
MFPlotBottom = 0
# Tells the control-click time function how to display the time based on how
# long the stuff plotted covers.
MFTimeMode = ""
# Gets set after something has been plotted.
MFPlotted = False

def plotMF(e = None):
    global QPEarliestCurr
    global QPLatestCurr
    global QPUserChannels
    global MFBufLeft
    global MFPWidth
    global MFTimeLineTop
    global MFTimeLineBottom
    global MFPlotTop
    global MFPlotBottom
    global MFPlotted
    LCan = PROGCan["MF"]
# Set the background color et al.
    setColors()
    LCan.configure(bg = Clr[DClr["MF"]])
    MFPlotted = False
    setMsg("MF", "CB", "Working...")
    LCanW = LCan.winfo_width()
    Magnify = intt(OPTMagnifyRVar.get())
# The value may be bad for some reason.
    if Magnify != 0:
        LCanW = LCanW*Magnify
# The sample counts could get large. +5 after the end of the plot and 5 pixels
# before the right edge.
    BufRight = PROGPropFont.measure(" 000000 ")+5+5
# The left buffer will be determined by the label lengths in QPChans of the
# things that were found to plot below.
    MFBufLeft = 0
# Go through the channels that the user asked to plot.
    for Chan in QPUserChannels:
# These don't get "plotted", so skip them.
        if QPChans[Chan[:3]][QPCHANS_PLOT] == 0:
            continue
# We want to find the QPChans info for the 3-char version of Chan and then
# replace the first 3 chrs of the label with the full version of Chan. These
# will get built again down in the plotting sections.
        NewLabel = QPChans[Chan[:3]][QPCHANS_LABEL]
        NewLabel = Chan+NewLabel[3:]
        if PROGPropFont.measure(NewLabel) > MFBufLeft:
            MFBufLeft = PROGPropFont.measure(NewLabel)
# Everything starts 5 pixels from the edge and there is 10 pixels after the
# labels before the plotting starts.
    MFBufLeft += 5+10
# This can't get too small or a long date/time in the timeline may run into
# the label like "Hours" at the beginning of the time line. So just make this
# the lower limit.
    if MFBufLeft < 125:
        MFBufLeft = 125
# The actual width of the plots proper.
    MFPWidth = LCanW-MFBufLeft-BufRight
# Get local variable versions of these to make things go a bit faster.
    EarliestCurr = QPEarliestCurr
    LatestCurr = QPLatestCurr
    TimeRange = LatestCurr-EarliestCurr
# FINISHME - check for small timerange?
# Keeps track of where to plot things in Y. There will be a title and a blank
# line for the time at the top of the clock rule in 3 lines, so advance .5
# lines to get to the vertical center of the title line, plus 5 pixels to
# keep the title off the top.
    PY = PROGPropFontHeight/2+5
# Don't list all of the files.
    File = QPFilesProcessed[0]
    if len(QPFilesProcessed) > 1:
        File += "+"
    Message = "File: %s   Station: %s   %s  to  %s  (%s)"%(File, \
            list2Str(QPStaIDs), dt2Time(-1, 80, EarliestCurr), dt2Time(-1, \
            80, LatestCurr), timeRangeFormat(LatestCurr-EarliestCurr))
    if len(QPPlotRanges) > 0:
        Message += "  (Zoomed %d)"%len(QPPlotRanges)
    canText(LCan, 5, PY, DClr["TX"], Message)
# Time line for Control-Click rule.
    PY += PROGPropFontHeight
    MFTimeLineTop = PY
# Date/time line. This and the ticks line will be opposite at the end.
    PY += PROGPropFontHeight
# Ticks line.
    PYT = PY+PROGPropFontHeight
    plotMFTimeMarks("lines", LCan, PY, PYT, EarliestCurr, LatestCurr)
# Really jump over the ticks.
    PY += PROGPropFontHeight
# Where the plots really start.
    MFPlotTop = PY
# This is the vertical center line of a 1-line plot (like LCQ) or the top
# border of a multi-line plot (like LCE).
    PY += PROGPropFontHeight
# Plotting of the gaps comes first if the checkbutton is on.
    GapsDetect = OPTGapsDetectCVar.get()
    if GapsDetect == 1:
        setMsg("MF", "CB", "Plotting Gaps...")
        LCan.create_line(MFBufLeft, PY, MFBufLeft+MFPWidth, PY, \
                fill = DClr["P0"])
        canText(LCan, 5, PY, DClr["LB"], "Gaps (%s)"%PROGGapsLengthVar.get())
# The format of the Var has already been checked, so just get it.
        GapsLength = dt2Timedhms2Secs(PROGGapsLengthVar.get())
        Skip = int(GapsLength/60)
# Go through each day of the range of days that we are going to plot and then
# see if there was data for each 1-minute period (or 1h or 2h periods, etc.)
# that covers that time range.
# This should match the day indecies in QPGaps.
        DaysEarliest = int(EarliestCurr/86400.0)
        DaysLatest = int(LatestCurr/86400.0)
        Skipped = 0
        SkipStart = 0.0
        GapCount = 0
# If a day is missing just use this to fool the routine.
        M5sEmpty = [0]*1440
        for DayKey in xrange(DaysEarliest, DaysLatest+1):
            DayStart = DayKey*86400.0
            DayEnd = DayStart+86400.0
# If we're zoomed in skip the earlier days.
            if DayEnd < EarliestCurr:
                continue
# If we're zoomed in we're finished.
            if DayStart > LatestCurr:
# Check to see if we were in the middle of a down time.
                if Skipped > 0:
                    XX1 = MFBufLeft+MFPWidth*(SkipStart- \
                            EarliestCurr)/TimeRange
                    XX2 = MFBufLeft+MFPWidth*(LatestCurr- \
                            EarliestCurr)/TimeRange
                    if (XX2-XX1) < 3.0:
                        ID = LCan.create_rectangle(XX1-1, PY-1, XX1+1, PY+1, \
                                fill = DClr["GG"], outline = DClr["GG"])
                    else:
                        ID = LCan.create_rectangle(XX1, PY-1, XX2, PY+1, \
                                fill = DClr["GG"], outline = DClr["GG"])
                    GapCount += 1
                    LCan.tag_bind(ID, "<Button-1>", Command(plotMFGapClick, \
                            GapCount, SkipStart, LatestCurr))
                break
            try:
                M5s = QPGaps[DayKey]
            except KeyError:
                if DayStart >= EarliestCurr and DayEnd <= LatestCurr:
                    if Skipped == 0:
                        SkipStart = DayStart
                    Skipped += 288
                    continue
                M5s = M5sEmpty
            Index = -1
            for M5 in M5s:
                Index += 1
                M5Start = DayStart+(Index*60.0)
                M5End = M5Start+60.0
                if M5Start > LatestCurr:
                    if Skipped >= Skip:
                        XX1 = MFBufLeft+MFPWidth*(SkipStart- \
                                EarliestCurr)/TimeRange
                        XX2 = MFBufLeft+MFPWidth*(LatestCurr- \
                                EarliestCurr)/TimeRange
                        if (XX2-XX1) < 3.0:
                            ID = LCan.create_rectangle(XX1-1, PY-1, XX1+1, \
                                    PY+1, fill = DClr["GG"], \
                                    outline = DClr["GG"])
                        else:
                            ID = LCan.create_rectangle(XX1, PY-1, XX2, PY+1, \
                                    fill = DClr["GG"], outline = DClr["GG"])
                        GapCount += 1
                        LCan.tag_bind(ID, "<Button-1>", \
                                Command(plotMFGapClick, GapCount, SkipStart, \
                                LatestCurr))
                    break
                if M5End < EarliestCurr:
                    continue
                if M5Start < EarliestCurr:
                    M5Start = EarliestCurr
                if M5End > LatestCurr:
                    M5End = LatestCurr
                if M5 == 0:
                    if Skipped == 0:
                        SkipStart = M5Start
                    Skipped += 1
                    continue
                elif Skipped > 0:
                    if Skipped >= Skip:
                        XX1 = MFBufLeft+MFPWidth*(SkipStart- \
                                EarliestCurr)/TimeRange
                        XX2 = MFBufLeft+MFPWidth*(M5Start- \
                                EarliestCurr)/TimeRange
                        if (XX2-XX1) < 3.0:
                            ID = LCan.create_rectangle(XX1-1, PY-1, XX1+1, \
                                    PY+1, fill = DClr["GG"], \
                                    outline = DClr["GG"])
                        else:
                            ID = LCan.create_rectangle(XX1, PY-1, XX2, PY+1, \
                                    fill = DClr["GG"], outline = DClr["GG"])
                        GapCount += 1
                        LCan.tag_bind(ID, "<Button-1>", \
                                Command(plotMFGapClick, GapCount, SkipStart, \
                                M5End))
                    Skipped = 0
                    continue
        ID = canText(LCan, MFBufLeft+MFPWidth+5, PY, DClr["TX"], "%d"%GapCount)
        LCan.tag_bind(ID, "<Button-1>", Command(plotMFShowChan, "Gap"))
        PY += PROGPropFontHeight
    for Chan in QPUserChannels:
        QPC = QPChans[Chan[:3]]
# There may be an entry for these in QPChans, but there won't be anything in
# them and they won't get plotted.
        if QPC[QPCHANS_PLOT] == 0:
            continue
# Where's My Water?
        if Chan not in QPData:
            QPErrors.append((1, "YB", \
                    "Channel '%s' in CP list, but not found in data."%Chan, 2))
            continue
        PlotType = QPC[QPCHANS_PLOTTER]
# -------- "mln" Multi-line normal (dots and/or line) plot.
# -------- "mll" Multi-line line (no dots) plot.
# ---------"mlls" Multi-line seismic (no dots and applies the bit weight) plot.
        if PlotType == "mln" or PlotType == "mll" or PlotType == "mlls":
            setMsg("MF", "CB", "Plotting %s..."%Chan)
            Height = PROGPropFontHeight*QPC[QPCHANS_HEIGHT]
            Bottom = PY+Height
            MidY = PY+Height/2
            LCan.create_line(MFBufLeft, PY, MFBufLeft+MFPWidth, PY, \
                    fill = DClr["P0"])
            LCan.create_line(MFBufLeft, Bottom, MFBufLeft+MFPWidth, Bottom, \
                    fill = DClr["P0"])
            NewLabel = QPC[QPCHANS_LABEL]
            NewLabel = Chan+NewLabel[3:]
            canText(LCan, 5, MidY, DClr["LB"], NewLabel)
            Min = float(maxint)
            Max = -float(maxint)
# Find the min and max values of what we are going to plot for the Y range.
# Keep a count of how many points there will be so we know if we are going to
# be binning or not. Find the index of the first point we are going to plot.
# FINISHME - make a note that this may filter out some severe timing problems
# or even not plot a lot of data if there are severe timing problems.
            Plotting = 0
            Index = -1
            StartIndex = -1
            for Data in QPData[Chan]:
                Index += 1
                Time = Data[0]
                if Time < EarliestCurr:
                    continue
                if Time > LatestCurr:
                    break
                if StartIndex == -1:
                    StartIndex = Index
                Value = Data[1]
                if Value < Min:
                    Min = Value
                if Value > Max:
                    Max = Value
                Plotting += 1
# If there were no points in the specified time range set these so we don't
# put maxint and -maxint up for the plot range.
            if Plotting == 0:
                Min = 0.0
                Max = 0.0
            Range = float(Max-Min)
            if Range == 0.0:
                Range = 1.0
            XY = []
# Get the color.
            if PROGColorModeRVar.get() == "B":
                C = QPC[QPCHANS_BBG]
            else:
                C = QPC[QPCHANS_WBG]
# If there aren't any points don't start looping through things that don't
# exist.
            if Plotting == 0:
                pass
# To bin or not to bin?
# Fewer points than pixels don't bin. Oversample/overplot a bit (MFPWidth*X)
# to make the extra effort of binning worth it. Worring about 1.5 points per
# pixel is a little lame. Plotting 1000's of point doesn't seem to take any
# effort at all, but up into the higher 10.000's does.
            elif Plotting <= MFPWidth*3:
                for Data in QPData[Chan][StartIndex:]:
                    Time = Data[0]
# We already know we are past the start of the time range.
                    if Time > LatestCurr:
                        break
                    Value = Data[1]
                    XX = MFBufLeft+MFPWidth*((Time-EarliestCurr)/TimeRange)
                    YY = Bottom-Height*((Value-Min)/Range)
                    XY += XX, YY,
                if Plotting > 1:
                    if PlotType == "mln" or PlotType == "mlng":
                        LCan.create_line(XY, fill = DClr["PL"])
                        for i in xrange(0, len(XY), 2):
                            XX = XY[i]
                            YY = XY[i+1]
                            ID = LCan.create_rectangle(XX-1, YY-1, XX+1, \
                                    YY+1, fill = Clr[C], outline = Clr[C])
                            LCan.tag_bind(ID, "<Button-1>", \
                                    Command(plotMFPointClick, Chan, \
                                    StartIndex))
                            LCan.tag_bind(ID, "<Button-3>", \
                                    Command(plotMFPointZap, Chan, \
                                    StartIndex))
                            StartIndex += 1
                    elif PlotType == "mll" or PlotType == "mlls":
                        LCan.create_line(XY, fill = Clr[C])
                elif Plotting == 1:
                    XX = XY[0]
                    YY = XY[1]
                    ID = LCan.create_rectangle(XX-1, YY-1, XX+1, YY+1, \
                            fill = Clr[C], outline = Clr[C])
                    LCan.tag_bind(ID, "<Button-1>", Command(plotMFPointClick, \
                            Chan, StartIndex))
# Binning.
            else:
                BinMin = float(maxint)
                BinMax = -float(maxint)
# Start plotting at the first point's position, which may not be at the far
# left edge.
                LastXX = int(MFBufLeft+MFPWidth* \
                        ((QPData[Chan][StartIndex][0]-EarliestCurr)/TimeRange))
                for Data in QPData[Chan][StartIndex:]:
                    Time = Data[0]
# We already know we are past the start time, so just check this.
                    if Time > LatestCurr:
                        break
# When we get to a point that is farther than LastXX then we create points for
# a vertical line from BinMax to BinMin.
                    XX = int(MFBufLeft+MFPWidth* \
                            ((Time-EarliestCurr)/TimeRange))
# We don't care about the Time after this since we are plotting by X.
# This point must be in the next bin.
                    if XX > LastXX:
                        YY = Bottom-Height*((BinMax-Min)/Range)
                        XY += LastXX, YY,
                        YY = Bottom-Height*((BinMin-Min)/Range)
                        XY += LastXX, YY,
                        BinMin = float(maxint)
                        BinMax = -float(maxint)
                        LastXX = XX
# We might lose a few points here, but that's kindof what the overplotting
# math above covers up.
                        if LastXX > (MFBufLeft+MFPWidth):
                            break
                    Value = Data[1]
                    if Value < BinMin:
                        BinMin = Value
                    if Value > BinMax:
                        BinMax = Value
# If we are binning any channel there will only be a line.
                LCan.create_line(XY, fill = Clr[C])
            if PlotType == "mln" or PlotType == "mll" or PlotType == "mlng":
                Str1 = "%s%s"%(Max, QPC[QPCHANS_UNITS])
                Str2 = "%s%s"%(Min, QPC[QPCHANS_UNITS])
            elif PlotType == "mlls":
                if OPTBitWeightRVar.get() == "low":
                    Str1 = "%sV"%(Max)
                    Str2 = "%sV"%(Min)
                elif OPTBitWeightRVar.get() == "high":
                    Str1 = "%sV"%(Max)
                    Str2 = "%sV"%(Min)
                else:
                    Str1 = "%s%s"%(Max, QPC[QPCHANS_UNITS])
                    Str2 = "%s%s"%(Min, QPC[QPCHANS_UNITS])
            canText(LCan, MFBufLeft-PROGPropFont.measure(Str1)-5, PY, \
                    DClr["TX"], Str1)
            canText(LCan, MFBufLeft-PROGPropFont.measure(Str2)-5, Bottom, \
                    DClr["TX"], Str2)
            ID = canText(LCan, MFBufLeft+MFPWidth+5, MidY, DClr["TX"], \
                    "%d"%Plotting)
            LCan.tag_bind(ID, "<Button-1>", Command(plotMFShowChan, \
                    "%s:  Max: %s   Min: %s"%(NewLabel, Str1, Str2)))
# All channels should be in QPSampRates, but just in case...
            if QPC[QPCHANS_SHOWSR] == 1 and Chan in QPSampRates:
                Rate = QPSampRates[Chan]
                if Rate >= 1.0:
                    Str = "%dsps"%Rate
                else:
                    Str = "%gsps"%Rate
# Items showing the sample rate will need to be at least 4 units tall (like
# the seismic crowd), otherwise this will overwrite something.
                canText(LCan, 5, MidY+PROGPropFontHeight, DClr["TX"], Str)
            PY += Height+PROGPropFontHeight*1.5
# -------- "mp" Single-line Mass Position-type.
        elif PlotType == "mp":
            setMsg("MF", "CB", "Plotting %s..."%Chan)
# Figure out which voltages to check for.
            Range = OPTMPVoltageRangeRVar.get()
            if Range not in ("Regular", "Trillium"):
                QPErrors.append((1, "MW", \
                        "%s: Select the Mass Position color range again."% \
                        Chan, 3))
                continue
            MPVR = MPVoltageRanges[Range]
# The color pallet to use.
            MPCP = MPColorPallets[PROGColorModeRVar.get()]
            NewLabel = QPC[QPCHANS_LABEL]
            NewLabel = Chan+NewLabel[3:]
            canText(LCan, 5, PY, DClr["LB"], NewLabel)
            LCan.create_line(MFBufLeft, PY, MFBufLeft+MFPWidth, PY, \
                    fill = DClr["P0"])
            Plotted = 0
            StartIndex = -1
            Index = -1
            for Data in QPData[Chan]:
                Index += 1
                Time = Data[0]
                if Time < EarliestCurr:
                    continue
                if Time > LatestCurr:
                    break
                if StartIndex == -1:
                    StartIndex = Index
                Value = abs(Data[1])
                XX = MFBufLeft+MFPWidth*((Time-EarliestCurr)/TimeRange)
# Trying to make problems stick out more. Make the "OK" dots smaller than the
# others.
                if Value <= MPVR[0]:
                    ID = LCan.create_rectangle(XX-1, PY-1, XX+1, PY+1, \
                            fill = Clr[MPCP[0]], outline = Clr[MPCP[0]])
                elif Value <= MPVR[1]:
                    ID = LCan.create_rectangle(XX-1, PY-1, XX+1, PY+1, \
                            fill = Clr[MPCP[1]], outline = Clr[MPCP[1]])
                elif Value <= MPVR[2]:
                    ID = LCan.create_rectangle(XX-2, PY-2, XX+2, PY+2, \
                            fill = Clr[MPCP[2]], outline = Clr[MPCP[2]])
                elif Value <= MPVR[3]:
                    ID = LCan.create_rectangle(XX-2, PY-2, XX+2, PY+2, \
                            fill = Clr[MPCP[3]], outline = Clr[MPCP[3]])
                else:
                    ID = LCan.create_rectangle(XX-3, PY-3, XX+3, PY+3, \
                            fill = Clr[MPCP[4]], outline = Clr[MPCP[4]])
                LCan.tag_bind(ID, "<Button-1>", Command(plotMFPointClick, \
                        Chan, StartIndex))
                LCan.tag_bind(ID, "<Button-3>", Command(plotMFPointZap, \
                        Chan, StartIndex))
                StartIndex += 1
                Plotted += 1
            ID = canText(LCan, MFBufLeft+MFPWidth+5, PY, DClr["TX"], \
                    "%d"%Plotted)
            LCan.tag_bind(ID, "<Button-1>", Command(plotMFShowChan, \
                        "%s"%NewLabel))
            PY += PROGPropFontHeight*1.5
# -------- Multi-line Mass Position-type
        elif PlotType == "mlmp":
            setMsg("MF", "CB", "Plotting %s..."%Chan)
# Figure out which voltages to check for.
            Range = OPTMPVoltageRangeRVar.get()
# If this isn't set just make a QPErrors entry for each channel on go on.
            if Range not in ("Regular", "Trillium"):
                QPErrors.append((2, "MW", \
                        "%s: Select the Mass Position color range again."% \
                        Chan, 3))
                continue
            MPVR = MPVoltageRanges[Range]
# The color pallet to use.
            MPCP = MPColorPallets[PROGColorModeRVar.get()]
            Height = PROGPropFontHeight*QPC[QPCHANS_HEIGHT]
            Bottom = PY+Height
            MidY = PY+Height/2
            LCan.create_line(MFBufLeft, PY, MFBufLeft+MFPWidth, PY, \
                    fill = DClr["P0"])
            LCan.create_line(MFBufLeft, Bottom, MFBufLeft+MFPWidth, Bottom, \
                    fill = DClr["P0"])
            NewLabel = QPC[QPCHANS_LABEL]
            NewLabel = Chan+NewLabel[3:]
            canText(LCan, 5, MidY, DClr["LB"], NewLabel)
# Find the min and max values of what we are going to plot for the Y range.
            Min = float(maxint)
            Max = -float(maxint)
            Plotting = 0
            StartIndex = -1
            Index = -1
            for Data in QPData[Chan]:
                Index += 1
                Time = Data[0]
                if Time < EarliestCurr:
                    continue
                if Time > LatestCurr:
                    break
                if StartIndex == -1:
                    StartIndex = Index
                Value = Data[1]
                if Value < Min:
                    Min = Value
                if Value > Max:
                    Max = Value
                Plotting += 1
# If there were no points in the specified time range set these so we don't
# put maxint and -maxint up for the plot range.
            if Plotting == 0:
                Min = 0.0
                Max = 0.0
            Range = float(Max-Min)
            if Range == 0.0:
                Range = 1.0
            if Plotting == 0:
                pass
            else:
                XY = []
# Where the color for each point will be kept.
                CList = []
                for Data in QPData[Chan][StartIndex:]:
                    Time = Data[0]
                    if Time > LatestCurr:
                        break
                    Value = Data[1]
                    AValue = abs(Value)
# Get the color based on the Value.
                    if AValue <= MPVR[0]:
# We can't keep these in the XY List, because the create_lines won't like it.
                        CList += [MPCP[0]]
                    elif AValue <= MPVR[1]:
                        CList += MPCP[1]
                    elif AValue <= MPVR[2]:
                        CList += [MPCP[2]]
                    elif AValue <= MPVR[3]:
                        CList += [MPCP[3]]
                    else:
                        CList += [MPCP[4]]
                    XX = MFBufLeft+MFPWidth*((Time-EarliestCurr)/TimeRange)
                    YY = Bottom-Height*((Value-Min)/Range)
                    XY += XX, YY,
                if Plotting > 1:
# If there are are less than MFPWidth*3 points make it standard line and dots.
# If there are more than that make line segments the color that the dots would
# be.
                    if Plotting <= MFPWidth*3:
                        LCan.create_line(XY, fill = DClr["PL"])
                        CIndex = 0
                        for i in xrange(0, len(XY), 2):
                            XX = XY[i]
                            YY = XY[i+1]
                            C = CList[CIndex]
                            ID = LCan.create_rectangle(XX-1, YY-1, XX+1, \
                                    YY+1, fill = Clr[C], outline = Clr[C])
                            LCan.tag_bind(ID, "<Button-1>", \
                                    Command(plotMFPointClick, Chan, \
                                    StartIndex))
                            LCan.tag_bind(ID, "<Button-3>", \
                                    Command(plotMFPointZap, Chan, StartIndex))
                            StartIndex += 1
                            CIndex += 1
                    else:
                        CStart = 0
                        CurrClr = CList[CStart]
                        CIndex = 0
                        for i in xrange(0, len(XY)-2, 2):
                            CIndex += 1
                            C = CList[CIndex]
                            if C == CurrClr:
                                continue
# When the color changes draw a line from CStart to CIndex. Just skip changes
# that are only 1 dot long. Eveything will be so squished if we are here that
# it won't matter. These skipped dots will show up when the user zooms in and
# plotting changes to individual samples (above).
                            if CIndex-CStart > 1:
# CIndex points to X value to plot next, the +2 gets the Y value after that
# included in the slice.
                                LCan.create_line(XY[CStart*2:CIndex*2+2], \
                                        fill = Clr[CurrClr])
                            CurrClr = C
                            CStart = CIndex
# This will plot the last segment or the whole plot if, for example, the mass
# position just happens to be green for the whole plotting period. Same thing
# applies about not plotting just one last dot of a given color by itself.
                        if CIndex-CStart > 1:
                            LCan.create_line(XY[CStart*2:CIndex*2], \
                                    fill = Clr[CurrClr])
                elif Plotting == 1:
                    XX = XY[0]
                    YY = XY[1]
                    C = CList[0]
                    ID = LCan.create_rectangle(XX-1, YY-1, XX+1, YY+1, \
                            fill = Clr[C], outline = Clr[C])
                    LCan.tag_bind(ID, "<Button-1>", \
                            Command(plotMFPointClick, Chan, StartIndex))
            Str1 = "%s%s"%(Max, QPC[QPCHANS_UNITS])
            Str2 = "%s%s"%(Min, QPC[QPCHANS_UNITS])
            canText(LCan, MFBufLeft-PROGPropFont.measure(Str1)-5, PY, \
                    DClr["TX"], Str1)
            canText(LCan, MFBufLeft-PROGPropFont.measure(Str2)-5, Bottom, \
                    DClr["TX"], Str2)
            ID = canText(LCan, MFBufLeft+MFPWidth+5, MidY, DClr["TX"], \
                    "%d"%Plotting)
            LCan.tag_bind(ID, "<Button-1>", Command(plotMFShowChan, \
                    "%s:  Max: %s   Min: %s"%(NewLabel, Str1, Str2)))
            PY += Height+PROGPropFontHeight*1.5
# -------- "strz" Single-line, multi-value, Very Large Array/Very Long
#          Baseline Array star coloring scheme: -1=good/not plotted,
#          0=good/green, 1=cyan, 2=yellow, 3=red, 4=magenta
# Just use the appropriate values to get a "binary", on/off, good/bad effect.
# (There used to be a "bin" type.)
        elif PlotType == "strz":
            setMsg("MF", "CB", "Plotting %s..."%Chan)
            CLabel = QPC[QPCHANS_LABEL]
            canText(LCan, 5, PY, DClr["LB"], CLabel)
            LCan.create_line(MFBufLeft, PY, MFBufLeft+MFPWidth, PY, \
                    fill = DClr["P0"])
            Plotted = 0
            StartIndex = -1
            Index = -1
# Figure out how many points are going to be plotted. <=MFPWidth*3 do the
# rectangles, otherwise just do a colored line.
            for Data in QPData[Chan]:
                Index += 1
                if Data[0] < EarliestCurr:
                    continue
                if Data[0] > LatestCurr:
                    break
# This will be the QPData index of the first plotted value. We'll use it below.
                if StartIndex == -1:
                    StartIndex = Index
                Value = Data[1]
# These won't be plotted, so don't count them as part of the limit.
                if Data[1] == -1:
                    continue
                Plotted += 1
# There wasn't anything in the time range to plot.
            if Plotted == 0:
                pass
            elif Plotted <= MFPWidth*3:
                Plotted = 0
# The QPData index value for the click-on dot information. It gets incremented
# right away in the loop.
                Index = StartIndex-1
                for Data in QPData[Chan][StartIndex:]:
                    Index += 1
                    Time = Data[0]
# We only need to check when to jump out. StartIndex is the first point in the
# time range.
                    if Time > LatestCurr:
                        break
                    Value = Data[1]
# Don't plot these.
                    if Value == -1:
                        continue
                    XX = MFBufLeft+MFPWidth*((Time-EarliestCurr)/TimeRange)
                    if Value == 0:
                        ID = LCan.create_rectangle(XX-2, PY-1, XX+2, PY+1, \
                                fill = Clr["G"], outline = Clr["G"])
                    elif Value == 1:
                        ID = LCan.create_rectangle(XX-2, PY-2, XX+2, PY+2, \
                                fill = Clr["C"], outline = Clr["C"])
                    elif Value == 2:
                        ID = LCan.create_rectangle(XX-2, PY-2, XX+2, PY+2, \
                                fill = Clr["Y"], outline = Clr["Y"])
                    elif Value == 3:
                        ID = LCan.create_rectangle(XX-2, PY-3, XX+2, PY+3, \
                                fill = Clr["R"], outline = Clr["R"])
                    else:
                        ID = LCan.create_rectangle(XX-2, PY-3, XX+2, PY+3, \
                                fill = Clr["M"], outline = Clr["M"])
                    LCan.tag_bind(ID, "<Button-1>", Command(plotMFPointClick, \
                            Chan, Index))
                    LCan.tag_bind(ID, "<Button-3>", Command(plotMFPointZap, \
                            Chan, Index))
                    Plotted += 1
            else:
                Plotted = 0
# The first point's color. When it changes we'll draw a line.
                Value = QPData[Chan][StartIndex][1]
                if Value == -1:
                    CurrClr = ""
                elif Value == 0:
                    CurrClr = "G"
                elif Value == 1:
                    CurrClr = "C"
                elif Value == 2:
                    CurrClr = "Y"
                elif Value == 3:
                    CurrClr = "R"
                else:
                    CurrClr = "M"
# There is no Index here. These won't be clickable.
# Collect the XY values in here for each line segment.
                XY = []
                Plotted = 0
                for Data in QPData[Chan][StartIndex:]:
                    Time = Data[0]
                    if Time > LatestCurr:
                        break
                    Plotted += 1
                    Value = Data[1]
                    if Value == -1:
                        NewClr = ""
                    elif Value == 0:
                        NewClr = "G"
                    elif Value == 1:
                        NewClr = "C"
                    elif Value == 2:
                        NewClr = "Y"
                    elif Value == 3:
                        NewClr = "R"
                    else:
                        NewClr = "M"
# Add this point to the list, then check to see if we should plot.
                    XX = MFBufLeft+MFPWidth*((Time-EarliestCurr)/TimeRange)
                    XY += XX, PY,
                    if NewClr != CurrClr:
# There may only be 1 point this color if the voltages, or whatever, were
# varying a lot, so fake it.
                        if CurrClr != "":
                            if len(XY) >= 4:
                                LCan.create_line(XY, fill = Clr[CurrClr], \
                                        width = 3)
                            else:
                                LCan.create_line(XY[0], XY[1], XY[0], XY[1], \
                                        fill = Clr[CurrClr], width = 3)
                        del XY[:]
# Now add this same point to the new list as the first point of the new color.
                        XY += XX, PY,
                        CurrClr = NewClr
# Plot any leftovers.
                if CurrClr != "":
                    if len(XY) >= 4:
                        LCan.create_line(XY, fill = Clr[CurrClr], width = 3)
                    else:
                        LCan.create_line(XY[0], XY[1], XY[0], XY[1], \
                                fill = Clr[CurrClr], width = 3)
            ID = canText(LCan, MFBufLeft+MFPWidth+5, PY, DClr["TX"], \
                    "%d"%Plotted)
            LCan.tag_bind(ID, "<Button-1>", Command(plotMFShowChan, \
                        "%s"%CLabel))
            PY += PROGPropFontHeight*1.5
# Where the plots really end.
    MFPlotBottom = PY
    PYT = PY+PROGPropFontHeight
# PYT,PY opposite order from beginning.
    plotMFTimeMarks("lines", LCan, PYT, PY, EarliestCurr, LatestCurr)
    MFTimeLineBottom = PYT+PROGPropFontHeight
    L, T, R, B = LCan.bbox(ALL)
# Last item, plus space for the rule time, plus a little.
    LCan.configure(scrollregion = (0, 0, R+10, B+PROGPropFontHeight+10))
    MFPlotted = True
# This might get overwritten by fileSelected() with more news, but that's OK.
    if GapsDetect == 1 and len(QPGaps) == 0:
        QPErrors.append((1, "YB", \
                "It looks like gap detection was not originally on when the source data was read.\nRe-Read the source data with Detect Gaps selected.", \
                1))
#######################################################################
# BEGIN: plotMFTimeMarks(What, LCan, PY, PYT, EarliestTime, LatestTime)
# FUNC:plotMFTimeMarks():2013.045
def plotMFTimeMarks(What, LCan, PY, PYT, EarliestTime, LatestTime):
    global MFTimeMode
# Plot tick marks showing months, days, hours, minutes or seconds depending
# on the range of the currently displayed plot.
    TimeRange = LatestTime-EarliestTime
    if TimeRange >= 2592000.0:
        if What == "lines":
            canText(LCan, 5, PY, DClr["T0"], "10 Days")
            MFTimeMode = "DD"
# Time of the nearest midnight before the earliest time.
        Time = (EarliestTime//86400.0)*86400
        Add = 864000.0
    elif TimeRange >= 864000.0:
        if What == "lines":
            canText(LCan, 5, PY, DClr["T0"], "Days")
            MFTimeMode = "D"
        Time = (EarliestTime//86400.0)*86400
        Add = 86400.0
    elif TimeRange >= 3600.0:
        if What == "lines":
            canText(LCan, 5, PY, DClr["T0"], "Hours")
            MFTimeMode = "H"
# Nearest hour.
        Time = (EarliestTime//3600.0)*3600
        Add = 3600.0
    elif TimeRange >= 60.0:
        if What == "lines":
            canText(LCan, 5, PY, DClr["T0"], "Minutes")
            MFTimeMode = "M"
# Nearest minute.
        Time = (EarliestTime//60.0)*60
        Add = 60.0
    else:
        if What == "lines":
            canText(LCan, 5, PY, DClr["T0"], "Seconds")
            MFTimeMode = "S"
        Time = (EarliestTime//1)
        Add = 1.0
# Tick marks line.
    if What == "lines":
        LCan.create_line(MFBufLeft, PYT, MFBufLeft+MFPWidth, PYT, \
                fill = DClr["TL"])
# When we get to the tick mark that is beyond the end of the time line we will
# put the last (end) time or the last grid line here.
    LastXX = 0.0
    LastTime = 0.0
    NextTimeX = 0
    while 1:
        Time += Add
        if Time < LatestTime:
            if Time >= EarliestTime:
                XX = MFBufLeft+MFPWidth*(Time-EarliestTime)/TimeRange
                if What == "lines":
                    LCan.create_line(XX, PYT-2, XX, PYT+2, fill = DClr["TL"])
                elif What == "grid":
                    LCan.create_line(XX, MFPlotTop, XX, MFPlotBottom, \
                            fill = DClr["GR"], tags = "grid")
                LastTime = Time
                LastXX = XX
                if What == "lines" and XX > NextTimeX:
# Returns to the milli-seconds. Chop off what we don't want.
                    TheTime = dt2Time(-1, 80, Time)
                    if MFTimeMode == "DD" or MFTimeMode == "D":
                        TheTime = TheTime[:-13]
                    elif MFTimeMode == "H":
                        TheTime = TheTime[:-7]
                    elif MFTimeMode == "M" or MFTimeMode == "S":
                        TheTime = TheTime[:-4]
                    canText(LCan, XX, PY, DClr["T0"], TheTime, "c")
# Make bigger ticks where the times are written.
                    LCan.create_line(XX, PYT-3, XX, PYT+3, width = 3, \
                            fill = DClr["TL"])
# Take where this time ended up, and add to that the width of what was printed.
# When the XX above gets past that point then set WriteTime to True and write
# another time.
                    NextTimeX = CANTEXTLastX+CANTEXTLastWidth
        else:
            if What == "grid":
                LCan.create_line(LastXX, MFPlotTop, LastXX, MFPlotBottom, \
                        fill = DClr["GR"], tags = "grid")
            break
    return
######################################
# BEGIN: plotMFShowChan(Str, e = None)
# FUNC:plotMFShowChan():2012.311
#   Handles clicking on the plot point totals at the ends of the plots and
#   showing information in the messages section.
def plotMFShowChan(Str, e = None):
    setMsg("MF", "", Str)
    return
################################################
# BEGIN: plotMFPointClick(Chan, Index, e = None)
# FUNC:plotMFPointClick():2013.217
#   Handles clicking on a data point.
def plotMFPointClick(Chan, Index, e = None):
    Time = QPData[Chan][Index][0]
    Value = QPData[Chan][Index][1]
# Sometimes there will be a value like "Locked".
    try:
        Value2 = QPData[Chan][Index][2]
    except:
        Value2 = ""
    if Value2 == "":
        setMsg("MF", "", "Channel: %s   Point: %d   Time: %s   Value: %g%s"% \
                (Chan, Index+1, dt2Time(-1, 80, Time), Value, \
                QPChans[Chan[:3]][QPCHANS_UNITS]))
    else:
        setMsg("MF", "", \
                "Channel: %s   Point: %d   Time: %s   Value: %g%s (%s)"% \
                (Chan, Index+1, dt2Time(-1, 80, Time), Value, \
                QPChans[Chan[:3]][QPCHANS_UNITS], Value2))
# If there is a third item it should be the QPLogs index number, which should
# be the line number in formLOG().
    try:
        Line = QPData[Chan][Index][2]
        if isinstance(Line, (int, long)):
# WARNING
# This is a special one-time-deal only for the "strz"-type plot dots. Keep
# these colors the same as the stuff in the plotMF() "strz" section.
            if QPChans[Chan[:3]][QPCHANS_PLOTTER] == "strz":
# The -1's should never come here (they don't get plotted), but we're covered
# anyway.
                if Value == -1 or Value == 0:
# We're assuming (uh huh) a white formLOG() background.
                    HClr = "GB"
                elif Value == 1:
                    HClr = "CB"
                elif Value == 2:
                    HClr = "YB"
                elif Value == 3:
                    HClr = "RW"
                else:
                    HClr = "MW"
            else:
                HClr = QPChans[Chan[:3]][QPCHANS_LOGBF]
            formLOGHilite(Line, HClr)
    except:
        pass
    return
################################################
# BEGIN: plotMFGapClick(Gap, From, To, e = None)
# FUNC:plotMFGapClick():2013.045
def plotMFGapClick(Gap, From, To, e = None):
    setMsg("MF", "", "Gap %d: %s  to  %s  (%s)"%(Gap, dt2Time(-1, 80, From), \
            dt2Time(-1, 80, To), timeRangeFormat(To-From)))
    return
##############################################
# BEGIN: plotMFPointZap(Chan, Index, e = None)
# FUNC:plotMFPointZap():2012.334
#   Handles right-clicking on points. I'm not even going to advertise this.
#   With having to replot (because we just deleted an element, so we can't do
#   another one without re-indexing) it's kinda cumbersome.
def plotMFPointZap(Chan, Index, e = None):
    if len(QPData[Chan]) > 1:
        del QPData[Chan][Index]
    plotMFReplot()
    return
###########################################
# BEGIN: plotMFTimeRuleGrid(LCan, e = None)
# FUNC:plotMFTimeRuleGrid():2013.045
#   For time rule clicks (i.e. Control-Button-1) on the MF Canvas to draw the
#   time and/or the time grids.
MFGridOn = False

def plotMFTimeRuleGrid(LCan, e = None):
    global MFGridOn
    if MFPlotted == False:
        beep(1)
        return
    CX = LCan.canvasx(e.x)
    CY = LCan.canvasy(e.y)
    Time = plotMFEpochAtX(CX, CY)
    if Time == -10 or Time == -20 or Time == -30:
        LCan.delete("rule")
        LCan.delete("grid")
# We'll throw this in here so the user doesn't have to go all of the way back
# to (probably) the TPS plot to get rid of the line.
        LCan.delete("orule")
        setMsg("MF", "", "")
        return
    if Time == -40 or Time == -50:
        LCan.delete("rule")
        LCan.delete("orule")
        setMsg("MF", "", "")
        if MFGridOn == False:
            plotMFTimeMarks("grid", LCan, 0, 0, QPEarliestCurr, QPLatestCurr)
            MFGridOn = True
        else:
            LCan.delete("grid")
            MFGridOn = False
        return
    LCan.delete("rule")
    LCan.delete("orule")
    TheTime = dt2Time(-1, 80, Time)
    if MFTimeMode == "DD":
        TheTime = TheTime[:-13]
    elif MFTimeMode == "D" or MFTimeMode == "H":
        TheTime = TheTime[:-7]
    elif MFTimeMode == "M":
        TheTime = TheTime[:-4]
    elif MFTimeMode == "S":
        pass
    canText(LCan, CX, MFTimeLineTop, DClr["TM"], TheTime, "c", "rule")
    LCan.create_line(CX, MFPlotTop, CX, MFPlotBottom, fill = DClr["TR"], \
            tags = "rule")
    canText(LCan, CX, MFTimeLineBottom, DClr["TM"], TheTime, "c", "rule")
    setMsg("MF", "", "Time rule: %s"%TheTime)
    return
###########################
# BEGIN: plotMFEpochAtX(CX)
# FUNC:plotMFEpochAtX():2012.306
#    Takes the passed CX pixel location and returns the epoch time at that
#    plot location on the main form.
def plotMFEpochAtX(CX, CY):
# Way left.
    if CX < MFBufLeft-25:
        return -10
# Just left.
    if CX < MFBufLeft:
        return -20
# Just right.
    if CX > (MFBufLeft+MFPWidth) and CX <= (MFBufLeft+MFPWidth+25):
        return -30
# Way right.
    if CX > (MFBufLeft+MFPWidth+25):
        return -40
# Off top.
    if CY < MFPlotTop:
        return -100
# Off bottom.
    if CY > MFPlotBottom:
        return -200
    return QPEarliestCurr+(((CX-MFBufLeft)/MFPWidth)* \
            (QPLatestCurr-QPEarliestCurr))
###########################
# BEGIN: plotMFZoomClick(e)
# FUNC:plotMFZoomClick():2012.329
#   Handles shift-clicks for zooming on the MF Canvas.
MFSelectX1 = 0
MFSelectTime1 = 0.0

def plotMFZoomClick(e):
    global MFSelectX1
    global MFSelectTime1
    global QPEarliestCurr
    global QPLatestCurr
    global QPPlotRanges
    if MFPlotted == False:
        beep(1)
        return
    CX = LCan.canvasx(e.x)
    CY = LCan.canvasy(e.y)
    Time = plotMFEpochAtX(CX, CY)
# Must be the first click.
    if MFSelectX1 == 0:
# Way left, try to zoom out.
        if Time == -10:
            if len(QPPlotRanges) == 0:
                setMsg("MF", "", "Already zoomed all of the way out.", 1)
                return
            Range = QPPlotRanges[-1]
            QPEarliestCurr = Range[0]
            QPLatestCurr = Range[1]
            QPPlotRanges.remove(Range)
            plotMFReplot()
# Way right, top or bottom.
        elif Time == -40 or Time == -100 or Time == -200:
            beep(1)
        else:
# If close to the left edge of the plots then assume they wanted to click at
# the left edge of the plots.
# Just left.
            if Time == -20:
                Time = QPEarliestCurr
                CX = MFBufLeft
# Just right.
            elif Time == -30:
                Time = QPLatestCurr
                CX = MFBufLeft+MFPWidth
            LCan.create_line(CX, MFPlotTop, CX, MFPlotBottom, \
                    fill = DClr["SR"], tags = "sel")
            MFSelectX1 = CX
            MFSelectTime1 = Time
    else:
# Second select.
# Way left or way right, erase the first line.
        if Time == -10 or Time == -40:
            LCan.delete("sel")
            MFSelectX1 = 0
# Top or bottom.
        elif Time == -100 or Time == -200:
            beep(1)
        else:
# If we click in the exact same X then erase the first line.
            if MFSelectTime1 == Time:
                LCan.delete("sel")
                MFSelectX1 = 0
                return
# Just left.
            if Time == -20:
                Time = QPEarliestCurr
                CX = MFBufLeft
# Just right.
            elif Time == -30:
                Time = QPLatestCurr
                CX = MFBufLeft+MFPWidth
            LCan.create_line(CX, MFPlotTop, CX, MFPlotBottom, \
                    fill = DClr["SR"], tags = "sel")
            updateMe(0)
            sleep(.2)
            LCan.delete("sel")
            MFSelectX1 = 0
# Record these before we change them.
            QPPlotRanges.append((QPEarliestCurr, QPLatestCurr))
            if MFSelectTime1 < Time:
                QPEarliestCurr = MFSelectTime1
                QPLatestCurr = Time
            else:
                QPEarliestCurr = Time
                QPLatestCurr = MFSelectTime1
            plotMFReplot()
    return
#######################################
# BEGIN: plotMFShowTimeRule(Who, Epoch)
# FUNC:plotMFShowTimeRule():2013.045
#   For external callers to use to show and clear the "orule" rule (generally
#   caused by clicking on the TPS plot).
def plotMFShowTimeRule(Who, Epoch):
    LCan = PROGCan["MF"]
    LCan.delete("orule")
    setMsg("MF", "", "")
    if Epoch == -1:
        return
    if Epoch < QPEarliestCurr:
        setMsg("MF", "", "Time is before current time range.", 1)
        return
    if Epoch > QPLatestCurr:
        setMsg("MF", "", "Time is after current time range.", 1)
        return
    XX = MFBufLeft+MFPWidth*((Epoch-QPEarliestCurr)/ \
            (QPLatestCurr-QPEarliestCurr))
    LCan.create_line(XX, MFPlotTop, XX, MFPlotBottom, fill = DClr["OR"], \
            tags = "orule")
    setMsg("MF", "", "%s Time: %s"%(Who, dt2Time(-1, 80, Epoch)[:-4]))
    return
###########################
# BEGIN: plotMFMindTheGap()
# FUNC:plotMFMindTheGap():2013.045
def plotMFMindTheGap():
    if OPTGapsDetectCVar.get() == 1:
        GapsLength = dt2Timedhms2Secs(PROGGapsLengthVar.get())
        if GapsLength == 0:
            setMsg("MF", "RW", "The Gap Length field value is 0.", 2)
            return False
        if GapsLength%60 != 0:
            setMsg("MF", "RW", \
               "The Gap Length field value is not a multiple of 1 minute.", 2)
            return False
    return True
#####################
# BEGIN: plotMFPlot()
# FUNC:plotMFPlot():2012.334
def plotMFPlot():
    global QPEarliestCurr
    global QPLatestCurr
    Root.focus_set()
# Only fileSelected() calls this so this must be the right thing to do.
    QPEarliestCurr = QPEarliestData
    QPLatestCurr = QPLatestData
    plotMF()
# Set this back to Working... and fileSelected() will set it to Done when
# everything has finished plotting.
    setMsg("MF", "CB", "Working...")
    return
#######################
# BEGIN: plotMFReplot()
# FUNC:plotMFReplot():2013.108
def plotMFReplot():
    global QPErrors
    Root.focus_set()
    if len(QPData) == 0:
        setMsg("MF", "RW", "No file(s) have been read.", 2)
        return False
    PROGCan["MF"].delete(ALL)
# Don't reset the scroll region here so the display will stay end up somewhere
# near where it was and the user won't have to scroll back down to see what
# they were looking at.
# Get the list again. The user may have rearranged things.
    Ret = setQPUserChannels("replot")
    if Ret[0] != 0:
        setMsg("MF", Ret)
        return False
# Check this here in case the user changed it.
    if plotMFMindTheGap() == False:
        return False
    formQPERRClear()
    del QPErrors[:]
    plotMF()
    if len(QPErrors) == 0:
        closeForm("QPERR")
    else:
        formQPERR()
    setMsg("MF", "", "Done.")
    return
######################
# BEGIN: plotMFClear()
# FUNC:plotMFClear():2012.334
def plotMFClear():
    PROGCan["MF"].delete(ALL)
    PROGCan["MF"].configure(scrollregion = (0, 0, 1, 1))
    return
# END: plotMF



# TESTING
TryPyDecode = False
###########################################################################
# BEGIN: q330Process(Filespec, FromEpoch, ToEpoch, StaIDFilter, GapsDetect,
#                WhackAntSpikes, SkipFile, StopBut, Running, WhereMsg)
# FUNC:q330Process():2013.081
#   Handles getting the information from the passed mini-seed format Filespec
#   decoded and left in the global QP variables.
def q330Process(Filespec, FromEpoch, ToEpoch, StaIDFilter, GapsDetect, \
        WhackAntSpikes, SkipFile, StopBut, Running, WhereMsg):
    global QPData
    global QPLogs
    global QPGaps
    global QPErrors
    global QPStaIDs
    global QPNetCodes
    global QPTagNos
    global QPSWVers
    global QPLocIDs
    global QPSampRates
    global QPUserChannels
    global QPAntSpikesWhacked
    global QPUnknownChanIDs
    global QPUnknownBlocketteType
    try:
        Fp = open(Filespec, "rb")
    except Exception, e:
        return (1, "MW", "Error opening file. %s"%e, 3, Filespec)
# This is used to unset a gap's 1 value if we are whacking large Antelope
# values.
    GapWas = 0
# Determine the record size of the seed/miniseed file. This will chew up a
# little time, but different systems (like Nanometrics) uses different record
# sizes for different files for different sample rates.
    RecordSize = 0
    for i in xrange(0, 17):
        Record = Fp.read(256)
# If the file is too small to determine it's record size then just go on.
        if len(Record) < 256:
            Fp.close()
            return (0, )
        if i == 0:
            StaID = Record[8:13]
            continue
        if StaID == Record[8:13]:
            if i == 1:
                RecordSize = 256
            elif i == 2:
                RecordSize = 512
            elif i == 4:
                RecordSize = 1024
            elif i == 8:
                RecordSize = 2048
            elif i == 16:
                RecordSize = 4096
            break
    if RecordSize == 0:
        Fp.close()
        return (1, "MW", "Could not determine record size of\n   %s."% \
                Filespec, 3, Filespec)
    Fp.seek(0)
# ---------------
# FINISHME - I think this is where the C code will be called? Maybe I'll just
# pass each chunk a little further down, instead. We'll have to see what works
# best.
# ---------------
# Read the file in 10 record chunks to make it faster.
    RecordsSize = RecordSize*10
    RecordsReads = 0
# Some may use this for messages.
    NoOfRecords = int(getsize(Filespec)/RecordSize)
    while 1:
        Records = Fp.read(RecordsSize)
# We're done with this file.
        if len(Records) == 0:
            Fp.close()
            return (0, )
        RecordsReads += 10
        if RecordsReads%10000 == 0:
# If WhereMsg == None then the caller will handle stopping suddenly (like by
# not calling this function anymore), otherwise this function will check and
# generate the progress messages (like for when reading an all-in-one file).
            if WhereMsg != None:
                StopBut.update()
                if Running == 0:
# Nothing wrong here. The caller will handle the actual stopping.
                    return (0, )
                setMsg(WhereMsg, "CB", "Reading record %d of %d..."% \
                        (RecordsReads, NoOfRecords))
        for i in xrange(0, 10):
            Ptr = RecordSize*i
            Record = Records[Ptr:Ptr+RecordSize]
# Need another set of Records.
            if len(Record) < RecordSize:
                break
            ChanID = Record[15:18]
# The Q330 may create an "empty" file (all 00H) and then not finish filling it
# in. The read()s keep reading, but there's nothing to process. This detects
# that and goes on to the next file. This may only happen in .bms-type data.
            if ChanID == "\x00\x00\x00":
                QPErrors.append((4, "YB", "File ends empty.", 2, Filespec))
                return (0, )
            ChanID3 = ChanID[:3]
            LocID = Record[13:15].strip()
            ChanID = ChanID+LocID
            StaID = Record[8:13].strip()
            if StaIDFilter != "" and StaID != StaIDFilter:
                continue
# Just to minimize CPU cycles we'll only check all of these from the beginning
# of each file that we get passed.
            if RecordsReads == 10:
                if StaID not in QPStaIDs:
                    QPStaIDs.append(StaID)
                NetCode = Record[18:20]
                if NetCode not in QPNetCodes:
                    QPNetCodes.append(NetCode)
# ----------------------------------------------------------
# Don't go any further if the user didn't request it. Maybe.
# ----------------------------------------------------------
            if GapsDetect == 0:
# Delay doing this check until after we decode the record time if we are
# looking for gaps. This check will be repeated below.
                if ChanID not in QPUserChannels:
# Just to keep from getting a zillion error messages.
                    if ChanID not in QPUnknownChanIDs:
                        QPUnknownChanIDs.append(ChanID)
# Only complain if the channel is plottable.
                        if QPChans[ChanID3][QPCHANS_PLOT] == 1:
                            QPErrors.append((1, "YB", \
             "Channel-location '%s' found in data, but not in channel list."% \
                                    ChanID, 2))
# If this is something like an sdrsplit-produced file that has only one kind
# of channel, and the caller has authorized it, then just return back for the
# next file since this one doesn't have anything we want.
                    if SkipFile == True:
                        return (0, )
                    continue
# Everybody will need the time.
            Year, Doy, Hour, Mins, Secs, Tttt= unpack(">HHBBBxH", \
                    Record[20:30])
            RecordStartTimeEpoch = q330ydhmst2Epoch(Year, Doy, Hour, Mins, \
                    Secs, Tttt)
# FINISHME - This will need to be moved to the frame/sample level at some
# point.
            if RecordStartTimeEpoch < FromEpoch:
                continue
            if RecordStartTimeEpoch > ToEpoch:
                return (0, )
# FINISHME - this will move too.
# QPGaps will be  int(Epoch//86400.0):[1m, 1m, 1m, ...] where each 1m \
# represents each 1 minute of the day and will be 0 or 1 -- there was no
# data for that 1 minute, or there was.
            if GapsDetect == 1:
                Days = RecordStartTimeEpoch/86400.0
                DayIndex = int(Days)
                M5 = int((Days-DayIndex)*1440)
                try:
                    GapWas = QPGaps[DayIndex][M5]
                    QPGaps[DayIndex][M5] = 1
                except:
                    QPGaps[DayIndex] = [0]*1440
                    QPGaps[DayIndex][M5] = 1
                    GapWas = 0
# Now do this part that we skipped above.
                if ChanID not in QPUserChannels:
                    if ChanID not in QPUnknownChanIDs:
                        QPErrors.append((1, "YB", \
             "Channel-location '%s' found in data, but not in channel list."% \
                                ChanID, 2))
                        QPUnknownChanIDs.append(ChanID)
# Don't check SkipFile here. As punishment for detecting gaps we will read
# through the whole file even if we are not interested.
                    continue
# Set up to start collecting for this channel. A LOG (and ACE ond OCF -- not
# plottable channels -- for Q330s) entry will be made here, but won't end up
# having anything in it.
            if ChanID not in QPData:
                QPData[ChanID] = []
# LOG records are a special case. We don't need to know anything else about
# them to process them.
# All LOG messages will be written together (there's only one form to show
# them on) even if there may be a location ID associated with them.
            if ChanID.startswith("LOG"):
# An RT130-style header line just to break up the monotony. The date matches
# the Q330 YYY-MM-DD format.
                M, D = q330yd2md(Year, Doy)
                QPLogs.append( \
               "State of Health   %d-%02d-%02d %02d:%02d:%02d.%03d   ST: %s"% \
                        (Year, M, D, Hour, Mins, Secs, Tttt, StaID))
# All of this binary gibberish to save space and then they waste a byte here
# and all of the space after the messages below.
                Lines = Record[56:].split("\r\n")
# Most of the time there is wasted space for the rest of the record.
                if Lines[-1].startswith("\x00"):
                    Lines = Lines[:-1]
# Pick the stuff out of the lOG messages that we are interested in here.
                for Line in Lines:
                    try:
                        Index = Line.index("KMI Property Tag Number:")
# 24 = len("KMI...Number:")
                        Value = Line[Index+24:].strip()
                        if Value not in QPTagNos:
                            QPTagNos.append(Value)
                    except:
                        pass
                    try:
                        Index = Line.index("System Software Version:")
                        Value = Line[Index+24:].strip()
                        if Value not in QPSWVers:
                            QPSWVers.append(Value)
                    except:
                        pass
                    QPLogs.append(Line)
                QPLogs.append("")
                continue
# This will be used by many.
            QPC = QPChans[ChanID[:3]]
# We can't check for this until here, because of the LOG stuff above. Again,
# in some cases there won't be anything in the file we want. The caller will
# decide.
            if QPC[QPCHANS_PLOT] == 0:
                if SkipFile == True:
                    return (0, )
                continue
# OK. We have (probably) 4K of data with a given ChanID like HHZ or VKI. We
# will get a bit more info from the fixed header then we will see what is
# next. What needs to be next is a 1000 blockette followed by a 1001
# blockette. The 1001 blockette will tell us how many frames of 64 bytes
# of Steim compressed data samples there is going to be in the rest of the 4K.
# With just Python I don't have a lot of CPU cycles to decode everything, so
# I'll only grab the first sample of the first 64byte frame from each 4K
# block. It's the only one that must be an absolute value and not a difference.
# If the global TryPyDecode == True, then I will try to decode all of the
# data points in the record, and keep the first samples from each frame.
            BeginDataOffset = 0
            NumberOfSamples = unpack(">H", Record[30:32])[0]
            NumberOfBlockettes = unpack(">B", Record[39])[0]
# Where all of the blockettes end and the data begins.
            BlocketteOffset = unpack(">H", Record[46:48])[0]
            for i in xrange(0, NumberOfBlockettes):
                BlocketteType = unpack(">H", \
                        Record[BlocketteOffset:BlocketteOffset+2])[0]
                if BlocketteType == 1000:
                    Blockette = Record[BlocketteOffset:BlocketteOffset+8]
                    EncodingFormat = unpack(">B", Blockette[4])[0]
                    if EncodingFormat != 10 and EncodingFormat != 11:
                        print "1000: %s EncodingFormat not 10 or 11: %s"% \
                                (ChanID, EncodingFormat)
                        break
                    if ChanID not in QPSampRates:
                        SampleRateFactor = float(unpack(">h", \
                                Record[32:34])[0])
                        SampleRateMult = float(unpack(">h", \
                                Record[34:36])[0])
                        try:
                            if SampleRateFactor > 0:
                                if SampleRateMult >= 0:
                                    SampleRate = SampleRateFactor* \
                                            SampleRateMult
                                else:
                                    SampleRate = -1*SampleRateFactor/ \
                                            SampleRateMult
                            else:
                                if SampleRateMult >= 0:
                                    SampleRate = -1*SampleRateMult/ \
                                            SampleRateFactor
                                else:
                                    SampleRate = 1/(SampleRateFactor* \
                                            SampleRateMult)
# The record contains LOG messages or other non-sampled data (except we won't
# even be here if it is a LOG record - that was handled above), or it's
# corrupted.
                        except:
                            SampleRate = 0.0
                        QPSampRates[ChanID] = SampleRate
                    BeginDataOffset = unpack(">H", Record[44:46])[0]
# Next blockette. This will be in Record offset like it was before we entered
# the loop.
                    BlocketteOffset = unpack(">H", Blockette[2:4])[0]
# TESTING - If the Record only has a blockette 1000 get the data?
                    if BeginDataOffset != 0 and BlocketteOffset == 0:
# FINISHME - there may be more stuff in here when we figure out the TitanSMA
# and Apollo data layout.
                        FrameCount = 0
                        break
                    continue
                if BlocketteType == 1001:
                    Blockette = Record[BlocketteOffset:BlocketteOffset+8]
                    FrameCount = unpack(">B", Blockette[7])[0]
                    BlocketteOffset = unpack(">H", Blockette[2:4])[0]
# Next blockette. This will be in Record offset like it was before we entered
# the loop.
                    continue
# FINISHME - Just jump over these for now. The Record sample rate seems to be
# fine for our stuff. These are not in Q330 data, but in Antelope data.
                if BlocketteType == 100:
                    Blockette = Record[BlocketteOffset:BlocketteOffset+12]
                    BlocketteOffset = unpack(">H", Blockette[2:4])[0]
                    continue
                else:
                    print "%s: Unhandled blockette: %d-%d"%(ChanID, i, \
                            BlocketteType)
                    if BlocketteType not in QPUnknownBlocketteType:
                        QPErrors.append((4, "RW", \
                                "%s: Unhandled blockette: %d"% \
                                (ChanID, BlocketteType), 2, Filespec))
                        QPUnknownBlocketteType.append(BlocketteType)
                    continue
            if BeginDataOffset != 0:
                FrameTime = RecordStartTimeEpoch
                FrameOffset = BeginDataOffset+4
# Get the decode code for this channel. This keeps us from having a big if
# statement below to decide how to decode the information in this record.
                DecodeCode = QPC[QPCHANS_DECODE]
                if TryPyDecode == False:
                    Value = unpack(">l", Record[FrameOffset:FrameOffset+4])[0]
# If we get a large sample value and we are whacking Antelope spikes (where the
# large value probably came from) then if we are detecting gaps we need to set
# the 5-minute block for this sample back to 0 if it was before this sample,
# because we are going to just not record this sample and if there are enough
# of them we'll want a gap to show up.
                    if WhackAntSpikes == 1 and Value >= AntSpikesValue:
                        if GapsDetect == 1:
                            if GapWas == 0:
                                QPGaps[DayIndex][M5] = 0
                        QPAntSpikesWhacked += 1
                        continue
                    if DecodeCode == 1:
                        QPData[ChanID].append((FrameTime, Value))
                    elif DecodeCode == 2:
                        QPData[ChanID].append((FrameTime, Value*.150))
                    elif DecodeCode == 3:
                        QPData[ChanID].append((FrameTime, Value*.1))
                    elif DecodeCode == 4:
# Can't have (-) current, but it can show up that way (1 count negative).
                        if Value < 0:
                            Value = 0
                        QPData[ChanID].append((FrameTime, Value))
                    else:
                        print "1000/1001: Unknown DecodeCode: %d"%DecodeCode
# FINISHME - future. Get the first value from each frame.
                else:
# We are going to cheat by figuring out how long a record is in time and then
# just dividing that by the number of frames to get the first sample time of
# each frame. This will make sample times wrong (for sure), but will make
# things a bit quicker. The constant sample rate/not a lot of variation in
# amplitude stuff will be close, but the seismic data will be a bit off.
                    TimePerFrame = (NumberOfSamples*SampleRate)/FrameCount
# Visit each 64 byte frame.
                    for f in xrange(0, FrameCount):
                        FrameOffset += 64*f
                        FrameTime += TimePerFrame*f
                        if EncodingFormat == 10:
                            pass
                        elif EncodingFormat == 11:
                            pass
# FINISHME - will all change
                        if f == 0:
                            Value = unpack(">l", Record[Offset:Offset+4])[0]
# If we get a large sample value and we are whacking Antelope spikes (where the
# large value probably came from) then if we are detecting gaps we need to set
# the 5-minute block for this sample back to 0 if it was before this sample,
# because we are going to just not record this sample and if there are enough
# of them we'll want a gap to show up.
                            if WhackAntSpikes == 1 and Value >= AntSpikesValue:
                                if GapsDetect == 1:
                                    if GapWas == 0:
                                        QPGaps[DayIndex][M5] = 0
                                QPAntSpikesWhacked += 1
                                continue
                        if DecodeCode == 1:
                            QPData[ChanID].append((FrameTime, Value))
                        elif DecodeCode == 2:
                            QPData[ChanID].append((FrameTime, Value*.150))
                        elif DecodeCode == 3:
                            QPData[ChanID].append((FrameTime, Value*.1))
                        elif DecodeCode == 4:
# Can't have (-) current, but it can show up that way (1 count negative).
                            if Value < 0:
                                Value = 0
                            QPData[ChanID].append((FrameTime, Value))
                        else:
                            print "1000/1001: Unknown DecodeCode: %d"% \
                                    DecodeCode
    return (0, )
# END: q330Process




#############################
# BEGIN: q330yd2md(YYYY, DOY)
# LIB:q330yd2md():2013.023
#   Converts YYYY,DOY to Month, Day. Faster than using using ydhmst2Time().
#   Expects a 4-digit YYYY.
def q330yd2md(YYYY, DOY):
    if DOY < 1 or DOY > 366:
        return 0, 0
    if DOY < 32:
        return 1, DOY
    elif DOY < 60:
        return 2, DOY-31
    if YYYY%4 != 0:
        Leap = 0
    elif YYYY%100 != 0 or YYYY%400 == 0:
        Leap = 1
    else:
        Leap = 0
# Check for this special day.
    if Leap == 1 and DOY == 60:
        return 2, 29
# The PROG_FDOM values for Mar-Dec are set up for non-leap years. If it is a
# leap year and the date is going to be Mar-Dec (it is if we have made it this
# far), subtract Leap from the day.
    DOY -= Leap
# We start through PROG_FDOM looking for dates in March.
    Month = 3
    for FDOM in PROG_FDOM[4:]:
# See if the DOY is less than the first day of next month.
        if DOY <= FDOM:
# Subtract the DOY for the month that we are in.
            return Month, DOY-PROG_FDOM[Month]
        Month += 1
    return 0, 0
# END: q330yd2md




#####################################################
# BEGIN: q330ydhmst2Epoch(YYYY, DOY, HH, MM, SS, TTT)
# LIB:q330ydhmst2Epoch():2013.045
#   Converts the passed date to seconds since Jan 1, 1970.
#   Same as the epoch section of dt2Time(), but just for Q330 binary time
#   conversion to make things faster.
def q330ydhmst2Epoch(YYYY, DOY, HH, MM, SS, TTT):
    global Y2EPOCH
    Epoch = 0
    try:
        Epoch = Y2EPOCH[YYYY]
    except KeyError:
        for YYY in xrange(1970, YYYY):
            if YYY%4 != 0:
                Epoch += 31536000
            elif YYY%100 != 0 or YYY%400 == 0:
                Epoch += 31622400
            else:
                Epoch += 31536000
        Y2EPOCH[YYYY] = Epoch
    Epoch += (DOY-1)*86400
    Epoch += HH*3600
    Epoch += MM*60
    Epoch += SS
    Epoch += TTT/10000.0
    return Epoch
# END: q330ydhmst2Epoch




##########################
# BEGIN: progControl(What)
# FUNC:progControl():2012.317
PROGRunning = 0

def progControl(What):
    global PROGRunning
    if What == "go":
        buttonBG(PROGReadBut, "G", NORMAL)
        buttonBG(PROGStopBut, "R", NORMAL)
        PROGRunning = 1
        busyCursor(1)
        return
    elif What == "stop":
        if PROGRunning == 0:
            beep(1)
        else:
            buttonBG(PROGStopBut, "Y", NORMAL)
# The main form Stop button can control the TPS form activity, but not the
# other way around.
            if PROGFrm["TPS"] != None and TPSRunning != 0:
                formTPSControl("stop")
    elif What == "stopped":
        buttonBG(PROGReadBut, "D", NORMAL)
        buttonBG(PROGStopBut, "D", DISABLED)
        if PROGFrm["TPS"] != None and TPSRunning != 0:
# Let the form fully stop itself.
            formTPSControl("stop")
    PROGRunning = 0
    busyCursor(0)
    return
# END: progControl




##########################
# BEGIN: progQuitter(Save)
# FUNC:progQuitter():2013.191
def progQuitter(Save):
    if Save == True:
# Load this with the current main display position and size.
        PROGGeometryVar.set(Root.geometry())
        savePROGSetups()
        saveChanPrefsSetups()
    setMsg("MF", "CB", "Quitting...")
    Ret = closeFormAll()
    if Ret[0] == 2:
        setMsg("MF", "", "Not quitting...")
        return
    exit()
# END: progQuitter




################################################
# BEGIN: readFileLines(Fp, Strip = False, N = 0)
# LIB:readFileLines():2009.290
#   Reads the passed file and determines how to split the lines which may end
#   differently depending on which operating system the file was written by.
def readFileLines(Fp, Strip = False, N = 0):
    if N == 0:
        RawLines = Fp.readlines()
    else:
        RawLines = Fp.readlines(N)
    Lines = []
# In case the file was empty.
    try:
# The order is important: \r\n  then  \r  then  \n.
        if RawLines[0].find("\r\n") != -1:
            Count = RawLines[0].count("\r\n")
# If there is only one \r\n (presumably at the end of the line) then the OS
# must have split the file up correctly. In that case just run the map() and
# clean off the ends of the lines.
            if Count == 1:
                if Strip == False:
                    Lines += map(rstrip, RawLines)
                else:
                    Lines += map(strip, RawLines)
# If there is more than one \r\n in the string then it could mean that all of
# the file lines are all jammed together into one long string. In that case
# split the line up first then add the parts to Lines, but leave off the
# "extra" blank line ([:-1]) that the split() will produce.
            else:
                for Line in RawLines:
                    Parts = Line.split("\r\n")
                    if Strip == False:
                        Lines += Parts[:-1]
                    else:
                        Lines += map(strip, Parts[:-1])
# Same as \r\n.
        elif RawLines[0].find("\r") != -1:
            Count = RawLines[0].count("\r")
            if Count == 1:
                if Strip == False:
                    Lines += map(rstrip, RawLines)
                else:
                    Lines += map(strip, RawLines)
            else:
                for Line in RawLines:
                    Parts = Line.split("\r")
                    if Strip == False:
                        Lines += Parts[:-1]
                    else:
                        Lines += map(strip, Parts[:-1])
# Same as \r.
        elif RawLines[0].find("\n") != -1:
            Count = RawLines[0].count("\n")
            if Count == 1:
                if Strip == False:
                    Lines += map(rstrip, RawLines)
                else:
                    Lines += map(strip, RawLines)
            else:
                for Line in RawLines:
                    Parts = Line.split("\n")
                    if Strip == False:
                        Lines += Parts[:-1]
                    else:
                        Lines += map(strip, Parts[:-1])
# What else can we do?
        else:
            Lines += RawLines
    except:
        pass
    return Lines
# END: readFileLines




#########################
# BEGIN: returnReadDir(e)
# FUNC:returnReadDir():2013.047
#   Needed to handle the Return key press in the DDIR field.
def returnReadDir(e):
    setMsg("MF", "", "")
    PROGDataDirVar.set(PROGDataDirVar.get().strip())
    if PROGDataDirVar.get() == "":
        if PROGSystem == "dar" or PROGSystem == "lin" or PROGSystem == "sun":
            PROGDataDirVar.set(sep)
        elif PROGSystem == "win":
# For a lack of anyplace else.
            PROGDataDirVar.set("C:\\")
    if PROGDataDirVar.get().endswith(sep) == False:
        PROGDataDirVar.set(PROGDataDirVar.get()+sep)
    loadSourceFilesCmd(MFFiles, "MF")
    PROGEnt["DDIR"].icursor(END)
    return
# END: returnReadDir




#######################
# BEGIN: rtnPattern(In)
# LIB:rtnPattern():2006.113
def rtnPattern(In):
    Rtn = ""
    for c in In:
        if c.isdigit():
            Rtn += "0"
        elif c.isupper():
            Rtn += "A"
        elif c.islower():
            Rtn += "a"
        else:
            Rtn += c
    return Rtn
# END: rtnPattern




####################
# BEGIN: setColors()
# FUNC:setColors():2013.039
#   Uses the value of PROGColorModeRVar and sets the colors in the global DClr
#   dictionary for the non-data plotted stuff.
DClr = {}

def setColors():
    if PROGColorModeRVar.get() == "B":
# Main form background
        DClr["MF"] = "B"
# GPS background and dots.
        DClr["GS"] = Clr["K"]
        DClr["GD"] = Clr["W"]
# Time rule time and rule.
        DClr["TM"] = "W"
        DClr["TR"] = Clr["Y"]
# Time grid lines.
        DClr["GR"] = Clr["y"]
# Date/time and ticks. Different things want the colors expressed in different
# ways.
        DClr["T0"] = "W"
        DClr["TL"] = Clr["W"]
# Labels.
        DClr["LB"] = "C"
# Text like the title.
        DClr["TX"] = "W"
# The plot center line or the upper and lower bounds lines.
        DClr["P0"] = Clr["A"]
# Line connecting dots.
        DClr["PL"] = Clr["A"]
# Selector rules
        DClr["SR"] = Clr["Y"]
# TPS Canvas
        DClr["TC"] = Clr["B"]
# The main plot time rule created by others (like by TPS clicking).
        DClr["OR"] = Clr["O"]
# Gap Gap and Overlap.
        DClr["GG"] = Clr["R"]
        DClr["GO"] = Clr["R"]
    elif PROGColorModeRVar.get() == "W":
        DClr["MF"] = "W"
        DClr["GS"] = Clr["W"]
        DClr["GD"] = Clr["B"]
        DClr["TM"] = "B"
        DClr["TR"] = Clr["U"]
        DClr["GR"] = Clr["E"]
        DClr["T0"] = "B"
        DClr["TL"] = Clr["B"]
        DClr["LB"] = "B"
        DClr["TX"] = "B"
        DClr["P0"] = Clr["A"]
        DClr["PL"] = Clr["E"]
        DClr["SR"] = Clr["A"]
        DClr["TC"] = Clr["W"]
        DClr["OR"] = Clr["U"]
        DClr["GG"] = Clr["R"]
        DClr["GO"] = Clr["R"]
    return
# END: setColors




########################################################################
# BEGIN: setMsg(WhichMsg, Colors = "", Message = "", Beep = 0, e = None)
# LIB:setMsg():2013.229
#   Be careful to pass all of the arguments if this is being called by an
#   event.
def setMsg(WhichMsg, Colors = "", Message = "", Beep = 0, e = None):
# So callers don't have to always be checking for this.
    if WhichMsg == None:
        return
# This might get called when a window is not, or never has been up so try.
    try:
        if isinstance(WhichMsg, basestring):
            LMsg = PROGMsg[WhichMsg]
        else:
            LMsg = WhichMsg
# Colors may be a standard error message. If it is break it up such that the
# rest of the function won't know the difference.
        if isinstance(Colors, tuple):
            Message = Colors[2]
# Some callers may not pass a Beep value if it is 0.
            try:
                Beep = Colors[3]
            except IndexError:
                Beep = 0
            Colors = Colors[1]
        LMsg.configure(state = NORMAL)
        LMsg.delete("0.0", END)
        if Colors == "":
            LMsg.configure(bg = Clr["W"], fg = Clr["B"])
        else:
            LMsg.configure(bg = Clr[Colors[0]], fg = Clr[Colors[1]])
        LMsg.insert(END, Message)
        LMsg.update()
        LMsg.configure(state = DISABLED)
# This may get called from a generated event with no Beep value set.
        if isinstance(Beep, (int, long)) and Beep > 0:
            beep(Beep)
        updateMe(0)
    except (KeyError, TclError):
        pass
    return
###################################################################
# BEGIN: setTxt(WhichTxt, Colors = "", Message = "", Beep = 0, e = None)
# FUNC:setTxt():2013.229
#   Same as above, but for Text()s.
def setTxt(WhichTxt, Colors = "", Message = "", Beep = 0, e = None):
    if WhichTxt == None:
        return
    try:
        if isinstance(WhichTxt, basestring):
            LTxt = PROGTxt[WhichTxt]
        else:
            LTxt = WhichTxt
        if isinstance(Colors, tuple):
            Message = Colors[2]
            try:
                Beep = Colors[3]
            except IndexError:
                Beep = 0
            Colors = Colors[1]
        LTxt.configure(state = NORMAL)
        LTxt.delete("0.0", END)
        if Colors == "":
            LTxt.configure(bg = Clr["W"], fg = Clr["B"])
        else:
            LTxt.configure(bg = Clr[Colors[0]], fg = Clr[Colors[1]])
        LTxt.insert(END, Message)
        LTxt.update()
        LTxt.configure(state = DISABLED)
        if isinstance(Beep, (int, long)) and Beep > 0:
            beep(Beep)
        updateMe(0)
    except (KeyError, TclError):
        pass
    return
# END: setMsg




#####################
# BEGIN: showUp(Fram)
# LIB:showUp():2012.317
def showUp(Fram):
# If anything should go wrong just close the form and let the caller fix it
# (i.e. redraw it).
    try:
        if PROGFrm[Fram] != None:
            PROGFrm[Fram].deiconify()
            PROGFrm[Fram].lift()
            return True
    except TclError:
# This call makes sure that the PROGFrm[] value gets set to None.
        closeForm(Fram)
    return False
# END: showUp




#################################################################
# BEGIN: nanProcessCSV(Filespec, FromEpoch, ToEpoch, StaIDFilter)
# LIB:nanProcessCSV():2013.080
#   Reads the .csv files from Nanometrics recorders. It leaves the decoded data
#   in the QPData if the stuff it finds is in the list of channels the user
#   wants.
def nanProcessCSV(Filespec, FromEpoch, ToEpoch, StaIDFilter):
    global QPData
    global QPLogs
    global QPErrors
# If the station name is not in the file name then we don't want this file.
# WARNING: This might cause a problem by including files whose file name's
# just happen to have the station name in them, but it's the best we can do.
    if StaIDFilter != "":
        if Filespec.find(StaIDFilter) == -1:
            return (0, )
    try:
        Fp = open(Filespec, "rb")
    except Exception, e:
        return (1, "MW", "Error opening file. %s"%e, 3, Filespec)
    Lines = readFileLines(Fp)
    Fp.close()
# If there ends up being no column header line don't read the file.
    if Lines[0].startswith("Time") == False:
        return (0, )
# Check to see if any of the things we extract from csv files are in here, and
# if the user wants to look at them.
    Parts = map(strip, Lines[0].split(","))
# If this fails forget the rest.
    try:
        TimeIndex = Parts.index("Time(UTC)")
    except Exception, e:
        print e
        return (0, )
# Collect the things to look for in the lines of this file in here.
    PartsList = {}
    if "GPS Receiver Status" in Parts:
        if "NGS" in QPUserChannels:
            PartsList["NGS"] = Parts.index("GPS Receiver Status")
    if "Timing Phase Lock" in Parts:
        if "NPL" in QPUserChannels:
            PartsList["NPL"] = Parts.index("Timing Phase Lock")
    if "Timing Uncertainty(ns)" in Parts:
        if "NTU" in QPUserChannels:
            PartsList["NTU"] = Parts.index("Timing Uncertainty(ns)")
# Note capitalization. TitanSMA?
    if "Supply voltage(V)" in Parts:
        if "NSV" in QPUserChannels:
            PartsList["NSV"] = Parts.index("Supply voltage(V)")
            SupplyVoltsMV = False
# Everyone else.
    if "Supply Voltage(mV)" in Parts:
        if "NSV" in QPUserChannels:
            PartsList["NSV"] = Parts.index("Supply Voltage(mV)")
            SupplyVoltsMV = True
    if "Total current(A)" in Parts:
        if "NTC" in QPUserChannels:
            PartsList["NTC"] = Parts.index("Total current(A)")
    if "Temperature(&deg;C)" in Parts:
        if "NTM" in QPUserChannels:
            PartsList["NTM"] = Parts.index("Temperature(&deg;C)")
    if "Sensor SOH Voltage 1(V)" in Parts:
        if "NM1" in QPUserChannels:
            PartsList["NM1"] = Parts.index("Sensor SOH Voltage 1(V)")
    if "Sensor SOH Voltage 2(V)" in Parts:
        if "NM2" in QPUserChannels:
            PartsList["NM2"] = Parts.index("Sensor SOH Voltage 2(V)")
    if "Sensor SOH Voltage 3(V)" in Parts:
        if "NM3" in QPUserChannels:
            PartsList["NM3"] = Parts.index("Sensor SOH Voltage 3(V)")
    if "Timing Error(ns)" in Parts:
        if "NTE" in QPUserChannels:
            PartsList["NTE"] = Parts.index("Timing Error(ns)")
    if "Controller Current(mA)" in Parts:
        if "NCC" in QPUserChannels:
            PartsList["NCC"] = Parts.index("Controller Current(mA)")
    if "Digitizer Current(mA)" in Parts:
        if "NDC" in QPUserChannels:
            PartsList["NDC"] = Parts.index("Digitizer Current(mA)")
    if "NMX Bus Current(mA)" in Parts:
        if "NNC" in QPUserChannels:
            PartsList["NNC"] = Parts.index("NMX Bus Current(mA)")
    if "Sensor Current(mA)" in Parts:
        if "NSC" in QPUserChannels:
            PartsList["NSC"] = Parts.index("Sensor Current(mA)")
    if "Serial Port Current(mA)" in Parts:
        if "NSP" in QPUserChannels:
            PartsList["NSP"] = Parts.index("Serial Port Current(mA)")
# Always collect the positions if we come across them so they can be converted
# into LOG lines and give the GPS display something to plot.
    if "Earth Location" in Parts:
        PartsList["GEL"] = Parts.index("Earth Location")
# These may not be in the CSV file.
        try:
            PartsList["GSU"] = Parts.index("GPS Satellites Used")
        except:
            pass
# Nothing of interest.
    if len(PartsList) == 0:
        return (0, )
# Only record the GPS position every hour. There's just plain too much of
# everything in these CSV files. Every minute is crazy.
    LastGPSPos = -1
    for Line in Lines[1:]:
        Parts = Line.split(",")
# Convert the date/time and check to see if we want this line's info.
        try:
            DT = Parts[TimeIndex]
            Epoch = dt2Time(22, -1, DT)
        except:
# This is impossible, so this line will be skipped.
            Epoch = -1.0
# We'll assume the lines are in time order.
        if Epoch < FromEpoch:
            continue
# We're done with this file.
        if Epoch > ToEpoch:
            return (0, )
# Default to "on". Some recorders will have GPS status messages that will
# change this and some won't.
        GPSStatOn = True
# Extract the stuff from each line that we are interested in.
        ChanKeys = PartsList.keys()
# Sort these so we look for NGS before we look for NPL so GPSStatOn will be
# set correctly before doing the NPL thing.
        ChanKeys.sort()
        for Chan in ChanKeys:
            if Chan not in QPData:
                QPData[Chan] = []
            Value = Parts[PartsList[Chan]]
            if Chan == "NGS":
# Locked is good and we don't need to plot anything. Same for Off.
# "GPS locked"
                if Value.startswith("GPS l"):
# These won't be plotted.
                    QPData["NGS"].append([Epoch, -1, Value])
# Not good - red.
# "GPS unlocked"
#%%% put msgs in help.
                elif Value.startswith("GPS u"):
                    QPData["NGS"].append([Epoch, 3, Value])
# "Off" - Apollo
                elif Value.startswith("Off"):
                    QPData["NGS"].append([Epoch, -1, Value])
                    GPSStatOn = False
# "Doing fixes" - Apollo
                elif Value.startswith("Doing"):
                    QPData["NGS"].append([Epoch, 1, Value])
                    GPSStatOn = True
# "No satellites"/"No GPS time" - Apollo
                elif Value.startswith("No"):
                    QPData["NGS"].append([Epoch, 2, Value])
                    GPSStatOn = True
                else:
                    QPData["NGS"].append([Epoch, 4, Value])
            elif Chan == "NPL" and GPSStatOn == True:
# Finelock is good.
                if Value.startswith("Fine"):
                    QPData["NPL"].append([Epoch, -1, Value])
                elif Value.startswith("Coarse"):
                    QPData["NPL"].append([Epoch, 2, Value])
                elif Value.startswith("No"):
                    QPData["NPL"].append([Epoch, 3, Value])
# "Free running" or anything else.
                else:
                    QPData["NPL"].append([Epoch, 4, Value])
            elif Chan == "NTU":
                IValue = intt(Value)
# The popular choices for this are 100,000,000,000 or 100ns, so we'll temper
# that a bit.
                if IValue > 10000:
                    IValue = 10000
                QPData["NTU"].append([Epoch, IValue])
            elif Chan == "NSV":
                if SupplyVoltsMV == False:
                    QPData[Chan].append([Epoch, round(floatt(Value), 1)])
                else:
                    QPData[Chan].append([Epoch, round(floatt(Value)/1000.0, \
                            1)])
            elif Chan == "NTC" or Chan == "NTM" or Chan == "NCC" or \
                    Chan == "NDC" or Chan == "NNC" or Chan == "NSC" or \
                    Chan == "NSP":
                QPData[Chan].append([Epoch, round(floatt(Value), 1)])
            elif Chan == "NM1" or Chan == "NM2" or Chan == "NM3":
                QPData[Chan].append([Epoch, round(floatt(Value), 2)])
            elif Chan == "NTE":
                QPData["NTE"].append([Epoch, intt(Value)])
            elif Chan == "GEL" and GPSStatOn == True:
                if Epoch-LastGPSPos > 1800:
                    try:
                        Sats = Parts[PartsList["GSU"]]
                    except:
                        Sats = "0"
                    QPLogs.append("%s GPSPOS: %s SATS: %s"%(DT, Value, Sats))
                    LastGPSPos = Epoch
    return (0, )
# END: nanProcessCSV




###########################
# BEGIN: sP(Count, Phrases)
# LIB:sP():2012.223
def sP(Count, Phrases):
    if Count == 1 or Count == -1:
        return Phrases[0]
    else:
        return Phrases[1]
# END: sP




###############################
# BEGIN: timeRangeFormat(Range)
# LIB:timeRangeFormat():2012.323
def timeRangeFormat(Range):
    if Range > 86400:
        return "%.2f days"%(Range/86400.0)
    elif Range > 3600:
        return "%.2f hours"%(Range/3600.0)
    elif Range > 60:
        return "%.2f minutes"%(Range/60.0)
    else:
        return "%.3f seconds"%Range
# END: timeRangeFormat




######################
# BEGIN: class ToolTip
# LIB:ToolTip():2013.157
#   Add tooltips to objects.
#   Usage: ToolTip(obj, Len, "text")
#   Nice and clever.
class ToolTipBase:
    def __init__(self, button):
        self.button = button
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.button.bind("<Enter>", self.enter)
        self.button.bind("<Leave>", self.leave)
        self.button.bind("<ButtonPress>", self.leave)
        return
    def enter(self, event = None):
        self.schedule()
        return
    def leave(self, event = None):
        self.unschedule()
        self.hidetip()
        return
    def schedule(self):
        self.unschedule()
        self.id = self.button.after(500, self.showtip)
        return
    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.button.after_cancel(id)
        return
    def showtip(self):
        if self.tipwindow:
            return
# The tip window must be completely clear of the mouse pointer so offset the
# x and y a little. This is all in a try because I started getting TclErrors
# to the effect that the window no longer existed by the time the geometry and
# deiconify functions were reached after adding the 'keep the tooltip off the
# edge of the display' stuff. I think this additional stuff was adding enough
# time to the whole process that it would get caught trying to bring up a tip
# that was no longer needed as the user quickly moved the pointer around the
# display.
        try:
            self.tipwindow = tw = Toplevel(self.button)
            tw.withdraw()
            tw.wm_overrideredirect(1)
            self.showcontents()
            x = self.button.winfo_pointerx()
            y = self.button.winfo_pointery()
# After much trial and error...keep the tooltip away from the right edge of the
# screen and the bottom of the screen.
            tw.update()
            if x+tw.winfo_reqwidth()+5 > PROGScreenWidth:
                x -= (tw.winfo_reqwidth()+5)
            else:
                x += 5
            if y+tw.winfo_reqheight()+5 > PROGScreenHeight:
                y -= (tw.winfo_reqheight()+5)
            else:
                y += 5
            tw.wm_geometry("+%d+%d" % (x, y))
# If you do a tw.lift() along with the deiconify the tooltip "flashes", so I'm
# not doing it and it seems to work OK.
            tw.deiconify()
        except TclError:
            self.hidetip()
        return
    def showcontents(self, Len, text, BF):
# Break up the incoming message about every Len characters.
        if Len > 0 and len(text) > Len:
            Mssg = ""
            Count = 0
            for c in text:
                if Count == 0 and c == " ":
                    continue
                if Count > Len and c == " ":
                    Mssg += "\n"
                    Count = 0
                    continue
                if c == "\n":
                    Mssg += c
                    Count = 0
                    continue
                Count += 1
                Mssg += c
            text = Mssg
# Override this in derived class.
        Lab = Label(self.tipwindow, text = text, justify = LEFT, \
                bg = Clr[BF[0]], fg = Clr[BF[1]], bd = 1, relief = SOLID, \
                padx = 3, pady = 2)
        Lab.pack()
        return
    def hidetip(self):
# If it is already gone then just go back.
        try:
            tw = self.tipwindow
            self.tipwindow = None
            if tw:
                tw.destroy()
        except TclError:
            pass
        return
class ToolTip(ToolTipBase):
    def __init__(self, button, Len, text, BF = "YB"):
# If the caller doesn't pass any text then don't get this started.
        if len(text) == 0:
            return
        ToolTipBase.__init__(self, button)
        self.Len = Len
        self.text = text
        self.BF = BF
        return
    def showcontents(self):
        ToolTipBase.showcontents(self, self.Len, self.text, self.BF)
        return
# END: ToolTip




########################
# BEGIN: updateMe(Which)
# FUNC:updateMe():2006.112
def updateMe(Which):
    if Which == 0:
        Root.update_idletasks()
        Root.update()
    return
# END: updateMe




#####################################################
# BEGIN: walkDirs2(Dir, IncHidden, Middle, End, Walk)
# LIB:walkDirs2():2012.294
#   Walks the passed Dir and returns a list of every file in Dir with full
#   path.
#   If Middle is not "" then only full paths containing Middle will be
#   kept.
#   If End is not "" then only files ending with End will be passed
#   back.
#   If Walk is 0 then files only in Dir will be returned and no
#   sub-directories will be walked.
def walkDirs2(Dir, IncHidden, Middle, End, Walk):
    if (Dir.startswith(".") or Dir.startswith("_")) and IncHidden == False:
        return (1, "RW", "Directory %s is hidden or special."%Dir, 2, "")
    if exists(Dir) == False:
        return (1, "RW", "Directory %s does not exist."%Dir, 2, "")
    if isdir(Dir) == False:
        return (1, "RW", "%s is not a directory."%Dir, 2, "")
    Files = []
    if Walk == 0:
        if Dir.endswith(sep) == False:
            Dir += sep
        for Name in listdir(Dir):
# No hidden files or directories, please.
            if (Name.startswith(".") or Name.startswith("_")) and \
                    IncHidden == False:
                continue
            Fullpath = Dir+Name
            if isdir(Fullpath):
                continue
            if Fullpath.find(Middle)== -1:
                continue
            if Fullpath.endswith(End):
                Files.append(Fullpath)
    elif Walk != 0:
# Collect the directories we come across in here.
        Dirs = []
        Dirs.append(Dir)
        while len(Dirs) > 0:
            Dir = Dirs.pop()
            if Dir.endswith(sep) == False:
                Dir += sep
            for Name in listdir(Dir):
# No hidden files or directories, please.
                if (Name.startswith(".") or Name.startswith("_")) and \
                        IncHidden == False:
                    continue
                Fullpath = Dir+Name
# Save this so we can pop it and do a listdir() on it.
                if isdir(Fullpath):
                    Dirs.append(Fullpath)
                    continue
                if Fullpath.find(Middle)== -1:
                    continue
                if Fullpath.endswith(End):
                    Files.append(Fullpath)
    Files.sort()
    return (0, Files)
# END: walkDirs2




# ============================================
# BEGIN: =============== SETUP ===============
# ============================================


######################
# BEGIN: menuMake(Win)
# FUNC:makeMenu():2013.047
OPTDateFormatRVar = StringVar()
OPTDateFormatRVar.set("YYYY-MM-DD")
OPTBitWeightRVar = StringVar()
OPTBitWeightRVar.set("none")
OPTMPVoltageRangeRVar = StringVar()
OPTMPVoltageRangeRVar.set("Regular")
OPTDebugCVar = IntVar()
PROGSetups += ["OPTDateFormatRVar", "OPTMPVoltageRangeRVar", "OPTDebugCVar"]
# Don't remember this so it always goes back to off.
OPTWhackAntSpikesCVar = IntVar()
OPTSortAfterReadCVar = IntVar()
MENUMenus = {}
MENUFont = PROGOrigPropFont

def menuMake(Win):
    global MENUMenus
    MENUMenus.clear()
    Top = Menu(Win, font = MENUFont)
    Win.configure(menu = Top)
    Fi = Menu(Top, font = MENUFont, tearoff = 0)
    MENUMenus["File"] = Fi
    Top.add_cascade(label = "File", menu = Fi)
    Fi.add_command(label = "Delete Setups File", command = deletePROGSetups)
    Fi.add_separator()
    Fi.add_command(label = "Quit", command = Command(progQuitter, True))
    Co = Menu(Top, font = MENUFont, tearoff = 0)
    MENUMenus["Commands"] = Co
    Top.add_cascade(label = "Commands", menu = Co)
    Co.add_command(label = "LOG Search", command = formLOGSRCH)
    Co.add_separator()
    Co.add_command(label = "GPS Data Plotter", command = formGPS)
    Co.add_command(label = "TPS Plot", command = formTPSOpen)
    Co.add_separator()
    Co.add_command(label = "Channel Preferences", command = formCPREF)
    Co.add_command(label = "Scan For Channel IDs", command = formSFCI)
    Op = Menu(Top, font = MENUFont, tearoff = 0)
    MENUMenus["Options"] = Op
    Top.add_cascade(label = "Options", menu = Op)
    Op.add_radiobutton(label = "Show Seismic Data In Counts", \
            variable = OPTBitWeightRVar, value = "none")
    Op.add_radiobutton(label = "Use Q330 Low Gain", \
            variable = OPTBitWeightRVar, value = "low", state = DISABLED)
    Op.add_radiobutton(label = "Use Q330 High Gain", \
            variable = OPTBitWeightRVar, value = "high", state = DISABLED)
    Op.add_separator()
    Message = "MP Coloring: %s (Regular)"%list2Str(MPVoltageRanges["Regular"])
    Op.add_radiobutton(label = Message, variable = OPTMPVoltageRangeRVar, \
            value = "Regular")
    Message = "MP Coloring: %s (Trillium)"% \
            list2Str(MPVoltageRanges["Trillium"])
    Op.add_radiobutton(label = Message, variable = OPTMPVoltageRangeRVar, \
            value = "Trillium")
    Op.add_separator()
    Op.add_radiobutton(label = "Show YYYY-MM-DD Dates", \
            command = Command(changeDateFormat, "MF"), \
            variable = OPTDateFormatRVar, value = "YYYY-MM-DD")
    Op.add_radiobutton(label = "Show YYYYMMMDD Dates", \
            command = Command(changeDateFormat, "MF"), \
            variable = OPTDateFormatRVar, value = "YYYYMMMDD")
    Op.add_radiobutton(label = "Show YYYY:DOY Dates", \
            command = Command(changeDateFormat, "MF"), \
            variable = OPTDateFormatRVar, value = "YYYY:DOY")
    Op.add_separator()
    Op.add_checkbutton(label = "Calculate File Sizes", \
            variable = OPTCalcFileSizesCVar)
    Op.add_checkbutton(label = "Sort Data By Time After Read", \
            variable = OPTSortAfterReadCVar)
    Op.add_checkbutton(label = "Whack Antelope Spikes", \
            variable = OPTWhackAntSpikesCVar, command = Command(msgCenter, \
            "spikes"))
    Op.add_separator()
    Op.add_command(label = "Fonts BIGGER", command = fontBigger)
    Op.add_command(label = "Fonts smaller", command = fontSmaller)
    Op.add_separator()
    Op.add_checkbutton(label = "Debug", variable = OPTDebugCVar)
    Fo = Menu(Top, font = MENUFont, tearoff = 0, postcommand = menuMakeForms)
    MENUMenus["Forms"] = Fo
    Top.add_cascade(label = "Forms", menu = Fo)
    Hp = Menu(Top, font = MENUFont, tearoff = 0)
    MENUMenus["Help"] = Hp
    Top.add_cascade(label = "Help", menu = Hp)
    Hp.add_command(label = "Help", command = Command(formHELP, Root))
    Hp.add_command(label = "Known Channels", command = listKnownChans)
    Hp.add_command(label = "Calendar", command = Command(formCAL, Root))
    Hp.add_command(label = "Check For Updates", command = checkForUpdates)
    Hp.add_command(label = "About", command = formABOUT)
# TESTING
#    Hp.add_command(label = "Test", command = testCmd)
    return
###############################################
# BEGIN: menuMakeSet(MenuText, ItemText, State)
# FUNC:menuMakeSet():2010.203
def menuMakeSet(MenuText, ItemText, State):
    Found = False
    try:
        Menu = MENUMenus[MenuText]
        for Item in range(Menu.index("end")+1):
            Type = Menu.type(Item)
            if Type in ("tearoff", "separator"):
                continue
            if Menu.entrycget(Item, "label") == ItemText:
                Found = True
                Menu.entryconfigure(Item, state = State)
                break
# Just in case. This should never go off if I've done my job.
    except:
        print ("menuMakeSet: %s, %s\a"%(MenuText, ItemText))
    return
################################
# BEGIN: menuMakeForms(e = None)
# FUNC:menuMakeForms():2012.103qpeek
def menuMakeForms(e = None):
    FMenu = MENUMenus["Forms"]
    FMenu.delete(0, END)
# Build the list of forms so they can be sorted alphabetically.
    Forms = []
    for Frmm in PROGFrm.keys():
        try:
            if PROGFrm[Frmm] != None:
                Forms.append([PROGFrm[Frmm].title(), Frmm])
        except TclError:
            print Frmm
            closeForm(Frmm)
    if len(Forms) == 0:
        FMenu.add_command(label = "No Forms Are Open", state = DISABLED)
    else:
        Forms.sort()
        for Title, Frmm in Forms:
            FMenu.add_command(label = Title, command = Command(showUp, Frmm))
# FOR QPEEK.
#        FMenu.add_separator()
#        FMenu.add_command(label = "Close All Forms", command = closeFormAll)
    return
# END: menuMake




##############
def testCmd():
    return




###############
# BEGIN: main()
# FUNC:main():2013.172
PROGDataDirVar = StringVar()
PROGGeometryVar = StringVar()
FromDateVar = StringVar()
ToDateVar = StringVar()
MFLbxFindVar = StringVar()
OPTBMSDataDirRVar = StringVar()
OPTBMSDataDirRVar.set("sdata")
PROGColorModeRVar = StringVar()
PROGColorModeRVar.set("B")
OPTPlotTPSCVar = IntVar()
OPTPlotTPSChansVar = StringVar()
OPTMagnifyRVar = StringVar()
OPTMagnifyRVar.set("1")
MFPSFilespecVar = StringVar()
OPTGapsDetectCVar = IntVar()
PROGGapsLengthVar = StringVar()
PROGStaIDFilterVar = StringVar()
PROGSetups += ["PROGDataDirVar", "PROGGeometryVar", "FromDateVar", \
        "ToDateVar", "MFLbxFindVar", "OPTBMSDataDirRVar", \
        "PROGColorModeRVar", "OPTMagnifyRVar", "OPTPlotTPSCVar", \
        "OPTPlotTPSChansVar", "MFPSFilespecVar", "OPTGapsDetectCVar", \
        "PROGGapsLengthVar", "PROGStaIDFilterVar"]
# Antelope can be set to stick in huge (16384**2) values into data files when
# data is missing, instead of just leaving a gap. The Options menu item Whack
# Antelope Spikes can be used to not collect those values and leave a gap.
AntSpikesValue = 16384**2
PROGClipboardVar = StringVar()
MPVoltageRanges = \
        {
        "Regular":[0.5, 2.0, 4.0, 7.0], \
        "Trillium":[0.5, 1.8, 2.4, 3.5]
        }
# First value is the color to use when below the first value in the Lists in
# MPVoltageRanges. Second color when between the first and second voltages,
# and so on. Last color is used when above last voltage.
MPColorPallets = \
        {
        "B":["C", "G", "Y", "R", "M"], \
# FINISHME - change these
        "W":["B", "B", "B", "B", "B"]
        }
# Information about each channel we know how to decode and plot.
# FINISHME - someday QPChans might be editable as a preferences-like thing, but
# not until the program is older to keep a little control over what is going
# on. Besides, I'm not sure how you could specify the _DECODE part without
# having to write the code to do the math or whatever. I guess there could just
# be the possibilities it it does know about and that's that.
QPCHANS_PLOT = 0      # 0=Don't plot, 1=Plottable.
QPCHANS_TYPE = 1      # "S"=seismic data, "E"=engineering data
                      # "E" data won't be plottable by TPS, for example, even
                      # if an E-channel ends up in the TPS channel list.
# QPCHANS_DECODE: How to decode.
# WARNING: Update Known Channels stuff if these change.
# 1 = 1 for 1, 1 count = 1%, etc.
# 2 = 1 count = 150mV
# 3 = 1 count = .1%
# 4 = 1 for 1, but kept >= 0
QPCHANS_DECODE = 2
QPCHANS_DESC = 3      # A description for the list of known channels function.
QPCHANS_LABEL = 4     # Plot canvas label (may have 3-char code modified when
                      # plotted to include location code). Will also be the
                      # tooltip for channel scanner buttons
QPCHANS_UNITS = 5     # Value units: volts, micro-seconds, etc.
QPCHANS_HEIGHT = 6    # Number of PROGPropFontHeight lines height the plot is
# QPCHANS_PLOTTER: Plotting type to use
# mln  = multi-line normal, one color, line and maybe dots
# mlmp = multi-line mass position, multi-color, always line and dots until
#         <=MFPWidth*3 points, then colored line
# mll  = multi-line line, one color, line only
# mlls = multi-line line seismic, one color, line only, can apply bit weights
# mp   = mass position, multi-color, single line
# bin  = single line "binary" plot. Green/1 "on/good", red/0 "off/bad"
# strz = the code must create data values to get the desired color dots or
#        lines (if there are too many dots). -1=not plotted, 0=green, 1=cyan,
#        2=yellow, 3=red, 4=magenta
QPCHANS_PLOTTER = 7
QPCHANS_SHOWSR = 8    # 1=show sample rate on plot (not used for mlmp plots)
QPCHANS_BBG = 9       # Black background color to plot for one color plots
QPCHANS_WBG = 10      # White background color to plot
QPCHANS_LOGBF = 11    # Clicking on a point LOG line bg/fg colors
QPChans = \
        {"LCE":[1, "E", 1, "Q330 clock phase error.", \
                "LCE-Phase Error", "us", 3, "mln", 0, "Y", "B"], \
        "VCO":[1, "E", 1, \
                "Q330 voltage controlled oscillator contol voltage value", \
                "VCO-VCO Control", "", 2, "mln", 0, "W", "B"], \
        "LCQ":[1, "E", 1, "Q330 clock quality", \
                "LCQ-Clock Qual", "%", 3, "mln", 0, "Y", "B"], \
        "VEA":[1, "E", 4, "Q330 antenna amperage", \
                "VEA-Ant Amps", "mA", 2, "mln", 0, "R", "B"], \
        "VEC":[1, "E", 1, "Q330 total system amperage", \
                "VEC-Sys Amps", "mA", 3, "mln", 0, "R", "B"], \
        "VEP":[1, "E", 2, "Q330 system input supply voltage", \
                "VEP-Input Volts", "V", 3, "mln", 0, "G", "B"], \
        "VKI":[1, "E", 1, "Q330 system temperature", \
                "VKI-Sys Temp", "C", 3, "mln", 0, "C", "B"], \
        "VPB":[1, "E", 3, "Q330 percentage of memory buffer used", \
                "VPB-Buffer Used", "%", 3, "mln", 0, "W", "B"], \
        "VFP":[1, "E", 3, "Q330 percentage of memory buffer used", \
                "VFP-Buffer Used", "%", 3, "mln", 0, "W", "B"], \
        "VMZ":[1, "E", 3, "Q330 sensor mass position", \
                "VMZ-MassPos Z", "V", 2, "mlmp"], \
        "VMN":[1, "E", 3, "Q330 sensor mass position", \
                "VMN-MassPos NS", "V", 2, "mlmp"], \
        "VME":[1, "E", 3, "Q330 sensor mass position", \
                "VME-MassPos EW", "V", 2, "mlmp"], \
        "VMU":[1, "E", 3, "Q330 sensor mass position", \
                "VMU-MassPos U", "V", 2, "mlmp"], \
        "VMV":[1, "E", 3, "Q330 sensor mass position", \
                "VMV-MassPos V", "V", 2, "mlmp"], \
        "VMW":[1, "E", 3, "Q330 sensor mass position", \
                "VMW-MassPos W", "V", 2, "mlmp"], \
        "VM0":[1, "E", 3, "Q330 sensor mass position", \
                "VM0-MassPos", "V", 2, "mlmp"], \
        "VM1":[1, "E", 3, "Q330 sensor mass position", \
                "VM1-MassPos", "V", 2, "mlmp"], \
        "VM2":[1, "E", 3, "Q330 sensor mass position", \
                "VM2-MassPos", "V", 2, "mlmp"], \
        "VM3":[1, "E", 3, "Q330 sensor mass position", \
                "VM3-MassPos", "V", 2, "mlmp"], \
        "VM4":[1, "E", 3, "Q330 sensor mass position", \
                "VM4-MassPos", "V", 2, "mlmp"], \
        "VM5":[1, "E", 3, "Q330 sensor mass position", \
                "VM5-MassPos", "V", 2, "mlmp"], \
        "VM6":[1, "E", 3, "Q330 sensor mass position", \
                "VM6-MassPos", "V", 2, "mlmp"], \
        "LHZ":[1, "S", 1, "Q330 seismic data", \
                "LHZ-V", "", 4, "mlls", 1, "G", "B"], \
        "LHN":[1, "S", 1, "Q330 seismic data", \
                "LHN-NS", "", 4, "mlls", 1, "G", "B"], \
        "LHE":[1, "S", 1, "Q330 seismic data", \
                "LHE-EW", "", 4, "mlls", 1, "G", "B"], \
        "BHZ":[1, "S", 1, "Q330 seismic data", \
                "BHZ-V", "", 4, "mlls", 1, "G", "B"], \
        "BHN":[1, "S", 1, "Q330 seismic data", \
                "BHN-NS", "", 4, "mlls", 1, "G", "B"], \
        "BHE":[1, "S", 1, "Q330 seismic data", \
                "BHE-EW", "", 4, "mlls", 1, "G", "B"], \
        "EHZ":[1, "S", 1, "Q330 seismic data", \
                "EHZ-V", "", 4, "mlls", 1, "G", "B"], \
        "EHN":[1, "S", 1, "Q330 seismic data", \
                "EHN-NS", "", 4, "mlls", 1, "G", "B"], \
        "EHE":[1, "S", 1, "Q330 seismic data", \
                "EHE-EW", "", 4, "mlls", 1, "G", "B"], \
        "HHZ":[1, "S", 1, "Q330 seismic data", \
                "HHZ-V", "", 4, "mlls", 1, "G", "B"], \
        "HHN":[1, "S", 1, "Q330 seismic data", \
                "HHN-NS", "", 4, "mlls", 1, "G", "B"], \
        "HHE":[1, "S", 1, "Q330 seismic data", \
                "HHE-EW", "", 4, "mlls", 1, "G", "B"], \
        "UHZ":[1, "S", 1, "Q330 seismic data", \
                "UHZ-V", "", 4, "mlls", 1, "G", "B"], \
        "UHN":[1, "S", 1, "Q330 seismic data", \
                "UHN-NS", "", 4, "mlls", 1, "G", "B"], \
        "UHE":[1, "S", 1, "Q330 seismic data", \
                "UHE-EW", "", 4, "mlls", 1, "G", "B"], \
        "VHZ":[1, "S", 1, "Q330 seismic data", \
                "VHZ-V", "", 4, "mlls", 1, "G", "B"], \
        "VHN":[1, "S", 1, "Q330 seismic data", \
                "VHN-NS", "", 4, "mlls", 1, "G", "B"], \
        "VHE":[1, "S", 1, "Q330 seismic data", \
                "VHE-EW", "", 4, "mlls", 1, "G", "B"], \

# These showed up "somewhere", but I can't remember where.
# A GLISN station? Maybe one of the Danish ones?
        "LCC":[1, "E", 1, "No idea what these are", \
                "LCC-?", "", 3, "mln", 0, "Y", "B"], \
        "LCL":[1, "E", 1, "No idea what these are", \
                "LCL-?", "", 3, "mln", 0, "Y", "B"], \
        "LPL":[1, "E", 1, "No idea what these are", \
                "LPL-?", "", 3, "mln", 0, "Y", "B"], \

# More GLISN stuff, because the sensors are not really North and East
# (boreholes).
        "LH1":[1, "S", 1, "Q330 oddly named GLISN borehole seismic data", \
                "LH1-E", "", 4, "mlls", 1, "G", "B"], \
        "LH2":[1, "S", 1, "Q330 oddly named GLISN borehole seismic data", \
                "LH2-N", "", 4, "mlls", 1, "G", "B"], \
        "UH1":[1, "S", 1, "Q330 oddly named GLISN borehole seismic data", \
                "UH1-E", "", 4, "mlls", 1, "G", "B"], \
        "UH2":[1, "S", 1, "Q330 oddly named GLISN borehole seismic data", \
                "UH2-N", "", 4, "mlls", 1, "G", "B"], \
        "VH1":[1, "S", 1, "Q330 oddly named GLISN borehole seismic data", \
                "VH1-E", "", 4, "mlls", 1, "G", "B"], \
        "VH2":[1, "S", 1, "Q330 oddly named GLISN borehole seismic data", \
                "VH2-E", "", 4, "mlls", 1, "G", "B"], \

# TitanSMA stuff.
        "BNZ":[1, "S", 1, "Nanometrics seismic data", \
                "BNZ-V", "", 4, "mlls", 1, "G", "B"], \
        "BNN":[1, "S", 1, "Nanometrics seismic data", \
                "BNN-NS", "", 4, "mlls", 1, "G", "B"], \
        "BNE":[1, "S", 1, "Nanometrics seismic data", \
                "BNE-EW", "", 4, "mlls", 1, "G", "B"], \
        "HNZ":[1, "S", 1, "Nanometrics seismic data", \
                "HNZ-V", "", 4, "mlls", 1, "G", "B"], \
        "HNN":[1, "S", 1, "Nanometrics seismic data", \
                "HNN-NS", "", 4, "mlls", 1, "G", "B"], \
        "HNE":[1, "S", 1, "Nanometrics seismic data", \
                "HNE-EW", "", 4, "mlls", 1, "G", "B"], \
# Filled in from the .cvs file info.
        "NSV":[1, "E", 1, "Nanometrics input supply voltage", \
                "NSV-Supply V", "V", 3, "mln", 0, "G", "B", "GB"], \
        "NTC":[1, "E", 1, "Nanometrics total system current", \
                "NTC-Total Curr", "mA", 3, "mln", 0, "R", "B", "RW"], \
        "NTM":[1, "E", 1, "Nanometrics system temperature", \
                "NTM-Temp", "C", 3, "mln", 0, "C", "B", "CB"], \
        "NCC":[1, "E", 1, "Nanometrics controller current", \
                "NCC-Ctrlr Curr", "mA", 3, "mln", 0, "R", "B", "RW"], \
        "NDC":[1, "E", 1, "Nanometrics digitizer current", \
                "NDC-Digtzr Curr", "mA", 3, "mln", 0, "R", "B", "RW"], \
        "NNC":[1, "E", 1, "Nanometrics NMX bus current", \
                "NNC-NMXB Curr", "mA", 3, "mln", 0, "R", "B", "RW"], \
        "NSC":[1, "E", 1, "Nanometrics sensor current", \
                "NSC-Sensor Curr", "mA", 3, "mln", 0, "R", "B", "RW"], \
        "NSP":[1, "E", 1, "Nanometrics serial port current", \
                "NSP-SerPort Curr", "mA", 3, "mln", 0, "R", "B", "RW"], \
        "NTU":[1, "E", 1, "Nanometrics timing uncertanty", \
                "NTU-Time Uncert", "ns", 3, "mln", 0, "Y", "B", "YB"], \
        "NTE":[1, "E", 1, "Nanometrics timing error", \
                "NTE-Time Error", "ns", 3, "mln", 0, "Y", "B", "YB"], \
        "NM1":[1, "E", 3, "Nanometrics sensor mass position voltage", \
                "NM1-MassPos Ch1", "V", 2, "mlmp"], \
        "NM2":[1, "E", 3, "Nanometrics sensor mass position voltage", \
                "NM2-MassPos Ch2", "V", 2, "mlmp"], \
        "NM3":[1, "E", 3, "Nanometrics sensor mass position voltage", \
                "NM3-MassPos Ch3", "V", 2, "mlmp"], \

# Color items are not used for these. The LOG line bg/fg color is a compromise
# that will usually not match the dot color.
        "NGS":[1, "E", 1, "Nanometrics GPS lock/unlock indicator", \
                "NGS-GPS Lk/Ulk", "", 1, "strz", 0, "", "", "RW"], \
        "NPL":[1, "E", 1, "Nanometrics phase lock indicator", \
                "NPL-Phase Lock", "", 1, "strz", 0, "", "", "RW"], \
# These are not plottable things from Q330s. They are here to keep the error
# messages from popping up about them. LOG is a slightly special case. It gets
# handled separately in the code.
        "LOG":[0, "E", 0, "Q330 LOG channel messages (not plotted)", \
                "LOG-Not Plotted", "", 0, "", 0, "", ""], \
        "ACE":[0, "E", 0, "Q330 ACE channel items (not plotted)", \
                "ACE-Not Plotted"], \
        "OCF":[0, "E", 0, "Q330 OCP channel items (not plotted)", \
                "OCF-Not Plotted"]}

# QData = "ChanID":[time series]. All of the data read from the station.
# [time series] will usually be [Time, Value], [Time, Value], ...
QPData = {}
# ...except for log messages. They go here.
QPLogs = []
# An attempt to catch gaps.
# FINISHME - >2hour gaps in point timestamps for the LCQ channel. It gets
# determined while plotting LCQ and then drawn right below the LCQ plot.
# The time gap detection will shrink, but I think it will have to stay tied
# to a specific channel. LCQ always seems to be there.
QPGaps = {}
# Standard error messages about stuff the program finds as it reads the data,
# but does not stop because of.
QPErrors = []
# The name of the station whose data we just read. It SHOULD end up with only
# one ID.
QPStaIDs = []
# Where the found network codes are kept. There SHOULD only be one.
QPNetCodes = []
# What should be any tag/serial numbers found in the LOG messages.
QPTagNos = []
# Any system software versions found in the LOG messages.
QPSWVers = []
# We will combine these with the channel IDs to look for data in QPData.
# We will first look for the Chan+"" channels, then anything Chan+anything
# else that might be in there.
QPLocIDs = []
# Sample rates. Where the sample rate for each channel is collected for
# printing on the plots.
QPSampRates = {}
# Just for the end of fileSelected() message.
QPAntSpikesWhacked = 0
# For error message control.
QPUnknownChanIDs = []
QPUnknownBlocketteType = []
# The list of files processed the last time fileSelected() was called.
QPFilesProcessed = []
# Where the zooming in and out time ranges are kept.
QPPlotRanges = []
# Start creating the display.
Title = "%s - %s"%(PROG_NAME, PROG_VERSION)
if PROGHostname != "":
    Title += " (%s)"%PROGHostname
Root.title(Title)
Root.protocol("WM_DELETE_WINDOW", Command(progQuitter, True))
menuMake(Root)
# If I don't create a sub-frame of Root resizing the main window causes a lot
# of plot updates to be caught and executed causing the plot to be redrawn
# a number of times before reaching the new size of the window (on some OS's
# and setups).
SubRoot = Frame(Root)
SubRoot.pack(fill = BOTH, expand = YES)
# ----- Current directory area -----
Sub = Frame(SubRoot)
LBu = BButton(Sub, text = "Main Data Directory", command = changeDir)
LBu.pack(side = LEFT)
ToolTip(LBu, 30, "Click to change the directory.")
LEnt = PROGEnt["DDIR"] = Entry(Sub, textvariable = PROGDataDirVar)
LEnt.pack(side = LEFT, fill = X, expand = YES)
compFsSetup(Root, LEnt, PROGDataDirVar, None, "MF")
LEnt.bind('<Return>', returnReadDir)
if PROGSystem == "dar":
    LEnt.bind("<Button-3>", openDDIRPopup)
Lb = Label(Sub, text = "From:")
Lb.pack(side = LEFT)
ToolTip(Lb, 30, \
        "Fill in the 'From' and 'To' fields to the right with start and end dates to read in from the selected file.")
LEnt = Entry(Sub, width = 11, textvariable = FromDateVar)
LEnt.pack(side = LEFT)
BButton(Sub, text = "C", command = Command(formPCAL, Root, "C", "MF", \
        FromDateVar, LEnt, False, OPTDateFormatRVar)).pack(side = LEFT)
Label(Sub, text = " To ").pack(side = LEFT)
LEnt = Entry(Sub, width = 11, textvariable = ToDateVar)
LEnt.pack(side = LEFT)
BButton(Sub, text = "C", command = Command(formPCAL, Root, "C", "MF", \
        ToDateVar, LEnt, False, OPTDateFormatRVar)).pack(side = LEFT)
LLb = Label(Sub, text = " Hints ")
LLb.pack(side = LEFT)
ToolTip(LLb, 45, \
        "PLOT AREA HINTS:\n--Clicking on a point: Clicking on a plot point will display the time and data value associated with that point in the messages are below the plot area.\n--Clicking on totals: Clicking on one of the total points values at the right end of a plot will display the identity of that plot's channel in the message area.\n--Control-clicking: Control-clicking in the plotting area will draw a line and show the date/time at that point at the top and bottom of the plotting area.\n--Control-clicking: Control-clicking above or below the plots will draw lines between the tick marks on the top and bottom time lines. Control-clicking again will erase the lines.\n--Shift-click: Shift-clicking in the plotting area the first time will display a vertical selection rule at that point. Shift-clicking again will display a second selection rule at the new point, then QPEEK will zoom in on the area between the rules. Shift-clicking in the area of the plot labels when the first selection rule is visible will cancel the selection operation.\n--Shift-click on labels: If zoomed in (described above) shift-clicking in the area of the plot labels will zoom back out. Each step when zooming in will be repeated when zooming out.")
Sub.pack(side = TOP, fill = X, expand = NO, padx = 3)
# Files list and plotting area.
Sub = Frame(SubRoot)
# ----- File list, scroll bar and text area -----
SSub = Frame(Sub)
# ----- File list and the scroll bars -----
SSSub = Frame(SSub)
SSSSub = Frame(SSSub)
MFFiles = Listbox(SSSSub, relief = SUNKEN, bd = 2, height = 5, \
        selectmode = EXTENDED)
MFFiles.pack(side = LEFT, fill = BOTH, expand = YES)
MFFiles.bind("<Double-Button-1>", fileSelected)
LSb = Scrollbar(SSSSub, command = MFFiles.yview, orient = VERTICAL)
LSb.pack(side = RIGHT, fill = Y, expand = NO)
MFFiles.configure(yscrollcommand = LSb.set)
SSSSub.pack(side = TOP, fill = BOTH, expand = YES)
LSb = Scrollbar(SSSub, command = MFFiles.xview, orient = HORIZONTAL)
LSb.pack(side = TOP, fill = X, expand = NO)
MFFiles.configure(xscrollcommand = LSb.set)
SSSub.pack(side = TOP, fill = BOTH, expand = YES)
SSSub = Frame(SSub)
LEnt = labelEntry2(SSSub, 11, "Find:=", 35, \
        "[Reload] Show file names containing this at the top.", \
        MFLbxFindVar, 6)
LEnt.bind("<Return>", Command(loadSourceFilesCmd, MFFiles, "MF"))
LEnt.bind("<KP_Enter>", Command(loadSourceFilesCmd, MFFiles, "MF"))
BButton(SSSub, text = "Clear", fg = Clr["U"], \
        command = Command(loadSourceFilesClearLbxFindVar, MFFiles, "MF", \
        True)).pack(side = LEFT)
BButton(SSSub, text = "Reload", command = Command(loadSourceFilesCmd, \
        MFFiles, "MF")).pack(side = LEFT)
SSSub.pack(side = TOP)
SSSub = Frame(SSub)
labelTip(SSSub, "Station:", LEFT, 40, \
        "(Read) If anything is in this field QPEEK will check each record's station ID value to see if it matches and only process those that do. This only applies to seed/mini-seed data. Nanometrics CSV files from different stations cannot be mixed -- they will all just get plotted together.")
Entry(SSSub, width = 12, textvariable = PROGStaIDFilterVar).pack(side = LEFT)
Label(SSSub, text = " ").pack(side = LEFT)
BButton(SSSub, text = "Replot", command = plotMFReplot).pack(side = LEFT)
SSSub.pack(side = TOP)
SSSub = Frame(SSub)
labelTip(SSSub, "Background:", LEFT, 30, \
        "(Replot)\nB = Black background for all plot areas\nW = White background")
Radiobutton(SSSub, text = "B", variable = PROGColorModeRVar, \
        command = setColors, value = "B").pack(side = LEFT)
Radiobutton(SSSub, text = "W", variable = PROGColorModeRVar, \
        command = setColors, value = "W").pack(side = LEFT)
SSSub.pack(side = TOP)
SSSub = Frame(SSub)
labelTip(SSSub, "Magnify:", LEFT, 35, "(Replot) Plot the information on a canvas the width of the plotting area, or 2x or 4x the width to spread out the points.")
Radiobutton(SSSub, text = "1x", variable = OPTMagnifyRVar, \
        value = "1").pack(side = LEFT)
Radiobutton(SSSub, text = "2x", variable = OPTMagnifyRVar, \
        value = "2").pack(side = LEFT)
Radiobutton(SSSub, text = "4x", variable = OPTMagnifyRVar, \
        value = "4").pack(side = LEFT)
SSSub.pack(side = TOP)
SSSub = Frame(SSub)
BButton(SSSub, text = "S", command = formSFCI).pack(side = LEFT)
BButton(SSSub, text = "C", command = formCPREF).pack(side = LEFT)
labelTip(SSSub, " Curr:", LEFT, 35, "(Read) The currently selected Channel Preferences slot.")
Entry(SSSub, textvariable = CPREFCurrNameVar, width = 14, \
        state = DISABLED).pack(side = LEFT)
SSSub.pack(side = TOP)
SSSub = Frame(SSub)
labelTip(SSSub, ".bms Dir:", LEFT, 35, \
       "(Read) Select which directory on a baler memory stick to read if applicable.")
Radiobutton(SSSub, text = "data"+sep, variable = OPTBMSDataDirRVar, \
        value = "data").pack(side = LEFT)
Radiobutton(SSSub, text = "sdata"+sep, variable = OPTBMSDataDirRVar, \
        value = "sdata").pack(side = LEFT)
SSSub.pack(side = TOP)
SSSub = Frame(SSub)
LCb = Checkbutton(SSSub, text = "Detect Gaps:", variable = OPTGapsDetectCVar)
LCb.pack(side = LEFT)
ToolTip(LCb, 35, \
        "(Read or Replot) When selected all data records read will be used to detect gaps. Must Reread if you just turned it on.")
labelTip(SSSub, "Len:", LEFT, 35, \
        "(Replot) Enter the minimum length of time a gap must be to be detected like 5m or 1h. Must be a multiple of a whole minute.")
Entry(SSSub, width = 7, textvariable = PROGGapsLengthVar).pack(side = LEFT)
SSSub.pack(side = TOP)
SSSub = Frame(SSub)
LCb = Checkbutton(SSSub, text = "TPS:", variable = OPTPlotTPSCVar)
LCb.pack(side = LEFT)
ToolTip(LCb, 45, \
        "(Read) Opens a form and plots the Time-Power-Squared information when data source reading is finished. Only the channels in the Chans list field to the right will be plotted.")
labelTip(SSSub, "Chans:", LEFT, 35, \
        "(Read or Replot) Enter the channels to plot separated by a comma. Wildcards are allowed. See the Help.")
Entry(SSSub, textvariable = OPTPlotTPSChansVar, width = 15).pack(side = LEFT)
SSSub.pack(side = TOP)
SSSub = Frame(SSub)
PROGReadBut = BButton(SSSub, text = "Read", command = fileSelected)
PROGReadBut.pack(side = LEFT)
PROGStopBut = BButton(SSSub, text = "Stop", state = DISABLED, \
        command = Command(progControl, "stop"))
PROGStopBut.pack(side = LEFT)
BButton(SSSub, text = "Write .ps", command = Command(formWritePS, \
        Root, "MF", MFPSFilespecVar)).pack(side = LEFT)
SSSub.pack(side = TOP, pady = 3)
# ----- Information area -----
SSSub = Frame(SSub)
LMsg = PROGMsg["INFO"] = Text(SSSub, cursor = "", font = PROGPropFont, \
        height = 10, wrap = WORD)
LMsg.pack(side = LEFT, fill = X, expand = YES)
LSb = Scrollbar(SSSub, orient = VERTICAL, command = LMsg.yview)
LSb.pack(side = TOP, fill = Y, expand = YES)
LMsg.configure(yscrollcommand = LSb.set)
SSSub.pack(side = TOP, fill = X, expand = NO)
SSub.pack(side = LEFT, fill = Y, expand = NO, padx = 3, pady = 3)
# ----- The plot area -----
SSub = Frame(Sub, bd = 2, relief = SUNKEN)
SSSub = Frame(SSub)
# Don't specify the color here.
LCan = PROGCan["MF"] = Canvas(SSSub)
LCan.pack(side = LEFT, expand = YES, fill = BOTH)
LCan.bind("<Shift-Button-1>", plotMFZoomClick)
LCan.bind("<Control-Button-1>", Command(plotMFTimeRuleGrid, LCan))
# With Windows OS.
LCan.bind("<MouseWheel>", Command(mouseWheel, LCan))
# With Linux OS.
LCan.bind("<Button-4>", Command(mouseWheel, LCan))
LCan.bind("<Button-5>", Command(mouseWheel, LCan))
LSb = Scrollbar(SSSub, orient = VERTICAL, command = LCan.yview)
LSb.pack(side = RIGHT, fill = Y, expand = NO)
LCan.configure(yscrollcommand = LSb.set)
SSSub.pack(side = TOP, fill = BOTH, expand = YES)
LSb = Scrollbar(SSub, orient = HORIZONTAL, command = LCan.xview)
LSb.pack(side = BOTTOM, fill = X, expand = NO)
LCan.configure(xscrollcommand = LSb.set)
SSub.pack(side = RIGHT, fill = BOTH, expand = YES)
Sub.pack(side = TOP, fill = BOTH, expand = YES)
# ----- Status message field -----
Sub = Frame(SubRoot)
PROGMsg["MF"] = Text(Sub, cursor = "", font = PROGPropFont, height = 3, \
        wrap = WORD)
PROGMsg["MF"].pack(side = LEFT, fill = X, expand = YES)
Button(Sub, text = "Replot", command = plotMFReplot).pack(side = LEFT)
Sub.pack(side = TOP, fill = X, expand = NO)
# Begin startup sequence.
Ret = getPROGStarted(True, False, True)
# If the loaded PROGScreenWidthOrig (and Height) values are the same as they
# are now then use the PROGGeometryVar value that was last saved to set the
# window, otherwise set it to new values.
if PROGIgnoreGeometry == False:
    if PROGScreenHeightOrig.get() == PROGScreenHeightOrigNow and \
            PROGScreenWidthOrig.get() == PROGScreenWidthOrigNow and \
            PROGGeometryVar.get() != "":
        Root.geometry(PROGGeometryVar.get())
    else:
# We don't use center() here to keep center() simple.
# For people with two monitors, which are usually with Macs, which usually
# have a smaller screen than their external monitor, so change the height too.
# My 24" iMac.
        if PROGScreenWidth > 1920:
# My 13" MBP.
            PROGScreenWidth = 1280
            PROGScreenHeight = 800
        FW = PROGScreenWidth*.80
# 1920x.8 = 1563.
# Don't let the form get gigantic.
        if FW > 1600:
            FW = 1600
        FH = PROGScreenHeight*.80
        FX = PROGScreenWidth/2-FW/2
        FY = PROGScreenHeight/2-FH/2
# I don't think measurements include the size of the title bar, so the -20
# compensates for that a bit. Set this, but don't make it show up until we've
# checked PROGGeometryVar below, unless there is an error to display.
        Root.geometry("%ix%i+%i+%i"%(FW, FH, FX, FY-20))
# This is the same as above.
else:
    if PROGScreenWidth > 1920:
        PROGScreenWidth = 1280
        PROGScreenHeight = 800
    FW = PROGScreenWidth*.80
    if FW > 1600:
        FW = 1600
    FH = PROGScreenHeight*.80
    FX = PROGScreenWidth/2-FW/2
    FY = PROGScreenHeight/2-FH/2
    Root.geometry("%ix%i+%i+%i"%(FW, FH, FX, FY-20))
# Remember these for next time.
PROGScreenHeightOrig.set(PROGScreenHeightOrigNow)
PROGScreenWidthOrig.set(PROGScreenWidthOrigNow)
# Set these now that the setups have been loaded, but before we deiconify.
fontSetSize()
setColors()
# Now we can do this.
PROGCan["MF"].configure(bg = Clr[DClr["MF"]])
# If there is something wrong it will be caught later.
changeDateFormat(None)
# A warning message or the setups file could not be found.
if Ret[0] == 1:
    Root.deiconify()
    Root.lift()
    formMYD(Root, (("(OK)", TOP, "ok"), ), "ok", Ret[1], "Really?", Ret[2])
# Something really went wrong.
elif Ret[0] == 2:
    Root.deiconify()
    Root.lift()
    formMYD(Root, (("(OK)", TOP, "ok"), ), "ok", Ret[1], "Oh Oh.", Ret[2])
# Something is wrong so don't save the setups.
    progQuitter(False)
# If these got done above they will have no effect here.
Root.deiconify()
Root.lift()
# This will be true if there is no setups file.
if PROGDataDirVar.get() == "":
    Ret = getPROGStartDir(2)
    if Ret != "":
        PROGDataDirVar.set(Ret)
# If the user doesn't pick any place.
if PROGDataDirVar.get() == "":
    PROGDataDirVar.set(PROGSetupsDirVar.get())
# This really isn't necessary since the file name gets set when a file is
# selected, but it will keep the user out of trouble before anything is
# plotted.
if MFPSFilespecVar.get() == "":
    MFPSFilespecVar.set(PROGDataDirVar.get())
loadSourceFilesCmd(MFFiles, "MF")
formCPREFCurrName()
# PROFILE
#profile.run("Root.mainloop()")
# Turns on epoch time displaying for troubleshooting.
#OPTDateFormatRVar.set("")
# FINISHME - This can be taken out after a while (put in on 2013-01-04).
if OPTDateFormatRVar.get() == "YYYY:DDD":
    OPTDateFormatRVar.set("YYYY:DOY")
Root.mainloop()
# END: main
