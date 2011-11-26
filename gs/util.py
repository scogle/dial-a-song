# util
# helper functions for boxee functionality

#from mc import ActivateWindow, GetWindow, GetApp, ShowDialogNotification, GetInfoString
#from xbmc import executebuiltin
from simplejson import loads, dumps
from datetime import datetime

from sys import path
path.append(r'u:\apps\grooveshark\\')

from definitions import *

def setVisible(controlID, visible):
    try:
        if controlID == 0:
            return # hiding 0 sets the screen to black. who knew?
        GetWindow(WINDOW_ID).GetControl(controlID).SetVisible(visible)
    except:
        pass

def show(*ids):
    """ Set visibility to many controls True """
    for id in ids:
        if type(id) is tuple:
            for i in id:
                setVisible(i, True)
        else:
            setVisible(id, True) 

def hide(*ids):
    """ Set visibility to many controls False """
    for id in ids:
        if type(id) is tuple:
            for i in id:
                setVisible(i, False)
        else:
            setVisible(id, False)

def goto(controlID):
    """ Jump cursor to given control """
    try:
        GetWindow(WINDOW_ID).GetControl(controlID).SetFocus()
    except:
        pass

def setToggle(*ids, **opts):
    selected = opts.get('selected', True)
    try: 
        for id in ids:
            if type(id) is tuple:
                for i in id:
                    if i == 0: continue
                    GetWindow(WINDOW_ID).GetToggleButton(i).SetSelected(selected)
            else:
                if id == 0: continue
                GetWindow(WINDOW_ID).GetToggleButton(id).SetSelected(selected)
    except:
        pass

def safe_str(obj):
    try:
        return str(obj)
    except UnicodeEncodeError:
        #return unicode(obj).encode('unicode_escape')
        return obj.encode('utf-8')
        #return obj.encode('ascii', 'ignore')

def recall(key, default=''):
    value = GetApp().GetLocalConfig().GetValue(key)
    if not value:
        value = default
    return value

def store(key, value):
    GetApp().GetLocalConfig().SetValue(key, safe_str(value))

def recallJSON(key, default=None):
    try:
        value = recall(key)
        return loads(value)
    except:
        return default
    
def storeJSON(key, value):
    try:
        encoded = dumps(value)
        store(key, encoded)
        return True
    except Exception, e:
        return False

def reset():
    config = GetApp().GetLocalConfig()
    config.ResetAll()
    config.Reset('')
 
def notify(message, icon=""):
    if icon is not "":
        ShowDialogNotification(message, icon)
    else:
        ShowDialogNotification(message)


def setCountryCode(code):
    global _countryCode
    _countryCode = code

def getCountryCode():
    """ Improper utility method to retrieve CC code quicker,
        i.e., let User not instantiate in play.py for quicker streaming. """
    global _countryCode
    countryCode = {}
    try:
        if _countryCode and _countryCode != {}:
            countryCode = _countryCode
        else:
            countryCode = recallJSON('CountryCode', {})
    except:
        countryCode = {}
    if not countryCode or countryCode == {}:
        from gs import user
        u = user.getUser()
        u.recallUser()
        countryCode = u.generateCountryCode()
        setCountryCode(countryCode)
    return countryCode
          
def generateTimeStamp():
    d = datetime.now()
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def getBoxeeID():
    #try:
    #    return mc.GetDeviceId()
    #except:
        return GetInfoString('System.ProfileName').lower().replace(' ', '')

def replaceWindow(windowID):
    executebuiltin("ReplaceWindow(%s)" % windowID)
    ActivateWindow(windowID)
