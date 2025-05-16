# coding: utf-8
# Copyright 2023 - 2025 Emil-18
# An add-on that enhances support for controls that normaly don't work well with NVDA
# This add-on is licensed under the same license as NVDA. See the copying.txt file for more information

#* imports
import addonHandler
addonHandler.initTranslation()
import api
import appModuleHandler
import ctypes
import config
import controlTypes
import copy
import displayModel
import editableText
import eventHandler
import globalPluginHandler
import globalVars
import gui
import IAccessibleHandler
import json
import locationHelper
import mouseHandler
import os
import sys
import textInfos
import threading
import tones
import ui
import UIAHandler
from watchdog import cancellableSendMessage
import winUser
import winKernel
import wx
from ctypes import *
from ctypes.wintypes import *
from globalVars import appPid
from gui.settingsDialogs import SettingsDialog
from NVDAObjects import *
from scriptHandler import script, getLastScriptRepeatCount
from time import sleep
from NVDAObjects.window import edit
def saveConfig():
	f = open(configPath, 'w+')
	json.dump(cfg, f, indent = 4)
	f.close()

#* global variables
path = config.getInstalledUserConfigPath()
configPath = os.path.join(path, 'controlConfig.ini')
disabled = False
oldFocus = None
canTrustFocusEvents = True
callLater = wx.CallLater(500, eventHandler.queueEvent)
callLater.Stop()
roles = (
	("list", controlTypes.Role.LIST, controlTypes.Role.LISTITEM),
	("grid", controlTypes.Role.DATAGRID, controlTypes.Role.DATAITEM),
	("statusbar", controlTypes.Role.STATUSBAR, controlTypes.Role.STATICTEXT),
	("tab", controlTypes.Role.TABCONTROL, controlTypes.Role.TAB),
	("tree", controlTypes.Role.TREEVIEW, controlTypes.Role.TREEVIEWITEM)
	
)
#* needed dlls
user32 = WinDLL("user32")
kernel32 = WinDLL("kernel32")
oleacc = WinDLL("oleacc")
#* dll function types
kernel32.VirtualAllocEx.restype = c_void_p
kernel32.VirtualAllocEx.argtypes = [HANDLE, c_void_p, c_void_p, DWORD, DWORD]
kernel32.WriteProcessMemory.argtypes = [HANDLE, c_void_p, c_void_p, c_longlong, c_void_p]
kernel32.ReadProcessMemory.argtypes = [HANDLE, c_void_p, c_void_p, c_longlong, c_void_p]

#* config
confSpec = {
	"trustEvents":"boolean(default=False)",
	"focusEnhancement": "boolean(default=False)"
}
config.conf.spec["enhancedControlSupport"] = confSpec
#* settings dialog
class EnhancedControlSupportSettingsPanel(gui.SettingsPanel):
	# Translators: the title of the enhanced control support settings panel
	title = _("Enhanced control support")
	def onValueChange(self, evt):
		self.focusEnhancement.Enable(not evt.IsChecked())
	def makeSettings(self, settingsSizer):
		settings = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: the label for a checkbox
		label = _("Rely on events by default")
		self.trustEvents = settings.addItem(wx.CheckBox(self, label = label))
		self.trustEvents.SetValue(config.conf["enhancedControlSupport"]["trustEvents"])
		self.trustEvents.Bind(wx.EVT_CHECKBOX, self.onValueChange)
		# Translators: the label for a checkbox
		label = _("Use enhanced methods to detect where the focus is located (experimental)")
		self.focusEnhancement = settings.addItem(wx.CheckBox(self, label = label))
		self.focusEnhancement.SetValue(config.conf["enhancedControlSupport"]["focusEnhancement"])
		self.focusEnhancement.Enable(not self.trustEvents.GetValue())
	def onSave(self):
		config.conf["enhancedControlSupport"]["trustEvents"] = self.trustEvents.GetValue()
		config.conf["enhancedControlSupport"]["focusEnhancement"] = self.focusEnhancement.GetValue()
#* helper functions
def shouldUseTimerMixin(conf, obj, clsList):

	for i in clsList:
		if issubclass(i, Complex) or (issubclass(i, Win32) and not conf):
			return(True)
	if conf and not conf[1]:
		return(True)
	if not config.conf["enhancedControlSupport"]["trustEvents"]:
		return(True)
	return(False)
def objectWithFocus():
	realFocus = NVDAObject.objectWithFocus()
	if realFocus.role in [
		controlTypes.Role.MENUBAR,
		controlTypes.Role.MENU,
		controlTypes.Role.POPUPMENU,
	]:
		for i in realFocus.children:
			states = set()
			try:
				states = i.states
			except:
				pass
			if controlTypes.State.FOCUSED in states:
				realFocus = i
				break
	return(realFocus)
def clientRectToScreenRect(window, rect):
	point1 = POINT(rect.left, rect.top)
	point2 = POINT(rect.right, rect.bottom)
	user32.ClientToScreen(window, c_void_p(addressof(point1)))
	user32.ClientToScreen(window, c_void_p(addressof(point2)))
	newRect = RECT(point1.x, point1.y, point2.x, point2.y)
	return(newRect)
def sendMessageInProcess(hwnd, msg, wParam, lParam, localBuffer, size, shouldTryWithLocalMemoryAddress = True, pointerToCheck = None, internalPointerToCheck = None):
	processHandle = oleacc.GetProcessHandleFromHwnd(hwnd)
	if not pointerToCheck:
		pointerToCheck = localBuffer
	
	failed = False
	if not processHandle:
		return
	# Alloc memory in the process owning hwnd
	internalBuff = kernel32.VirtualAllocEx(processHandle, 0, size, winKernel.MEM_COMMIT, winKernel.PAGE_READWRITE)
	if not internalPointerToCheck:
		internalPointerToCheck = internalBuff
	try:
		if not internalBuff:
			return
		# Write the given structure into the processes memory, in case it is needed.
		kernel32.WriteProcessMemory(processHandle, internalBuff, localBuffer, size, 0)
		# Send the message
		res = cancellableSendMessage(hwnd, msg, wParam if wParam != localBuffer else internalBuff, lParam if lParam != localBuffer else internalBuff)
		# Sometimes, SendMessage fails when it is given an address from none local memory.
		try:
			localBuffer2 = cdll.msvcrt.malloc(size)
			kernel32.ReadProcessMemory(processHandle, internalPointerToCheck, localBuffer2, size, 0)
			if shouldTryWithLocalMemoryAddress and not cdll.msvcrt.memcmp(pointerToCheck, localBuffer2, size):
				failed = True
				res = cancellableSendMessage(hwnd, msg,wParam, lParam)
		finally:
			cdll.msvcrt.free(localBuffer2)

		# Turn res into a signed value
		res = c_long(res).value
		# Read the structure back into the local buffer
		if not failed:
			kernel32.ReadProcessMemory(processHandle, internalBuff, localBuffer, size, 0)

		return(res)
	finally:
		# Free the memory in the finally block, so it always will be executed, regardless of the state of the function
		kernel32.VirtualFreeEx(processHandle, internalBuff, 0, winKernel.MEM_RELEASE)

cachedAppNames = {}
notWin32 = ('MSAA', 'UIA', "enhanced UIA", 'normal')
def getKeyFromWindow(windowHandle, bypassDisabled = False):
	if disabled and not bypassDisabled:
		return
	global cachedAppNames
	processID = winUser.getWindowThreadProcessID(windowHandle)[0]
	# calling the get app name from process ID function on every NVDAObject that gets instansiated causes a large drop in performence, so cache it.
	appName = cachedAppNames.get(processID)
	if not appName:
		appName = appModuleHandler.getAppNameFromProcessID(processID)
		cachedAppNames.update({processID: appName})
	className = winUser.getClassName(windowHandle)
	return(appName+className)
def getConfigFromWindow(windowHandle):
	key = getKeyFromWindow(windowHandle)
	c = cfg.get(key)
	return c
def shouldUseWin32(windowHandle):
	c = getConfigFromWindow(windowHandle)
	use = bool(c and not c[0] in notWin32)
	return(use)
def findSupportedClass(windowHandle):
	supported = []
	cls = None
	for i in supportedClasses:
		if i.isSupported(windowHandle):
			supported.append(i)
	length = len(supported)
	if length == 1:
		cls = supported[0]
		return(cls)
	# No class or multiple classes gave True, so look at their names if the class allows it and check if the window class include their name
	className = winUser.getClassName(windowHandle)
	supportedNames = []
	for i in supportedClasses:
		if i.__name__.lower() in className.lower() and i.shouldLookAtClassName:
			supportedNames.append(i)
	if len(supportedNames) == 1:
		cls = supportedNames[0]
	else:
		cls = Unknown
	return(cls)
	
#* redefinitions

oldIsUIAWindow = UIAHandler.UIAHandler.isUIAWindow
def newIsUIAWindow(self, windowHandle, *args, **kwargs):
	conf = getConfigFromWindow(windowHandle)
	if not conf or shouldUseWin32(windowHandle):
		return(oldIsUIAWindow(self, windowHandle, *args, **kwargs))
	if conf and conf[0] == "normal":
		return(oldIsUIAWindow(self, windowHandle, *args, **kwargs))
	cls = conf[0]
	if cls not in ["UIA", "enhanced UIA"]:
		return(False)
	return(True)

#* Additions
#** General structures
class SHORTPOINT(Structure):
	_fields_ = [
		("x", c_short),
		("y", c_short)
		]
class Win32(window.Window):
	'''
	Support for win32 controls that don't support IAccessible
	'''
	shouldLookAtClassName = True
	displayName = None
	isComplex = False # The control has other controls that NVDA should treat as NVDAObjects inside of it, such as a list.
	baseRole = controlTypes.Role.WINDOW
	subClass = None
	clicks = 1 # the number of clicks that normaly are required to activate a control
	def _get_role(self):
		return(self.baseRole)
	def _get_win32Name(self):
		return(self.windowText)

	def doWindowAction(self):
		pass
	def click(self):
		point = self.location.center
		obj = NVDAObject.objectFromPoint(*point)
		if obj != self:
			return(False)
		mousePos = winUser.getCursorPos()
		winUser.setCursorPos(*point)
		for i in range(self.clicks):
			mouseHandler.doPrimaryClick()
		winUser.setCursorPos(*mousePos)
		return(True)
	def _get_children(self):
		return(NVDAObject._get_children(self))
	def doAction(self, index = None):
		if not self.click():
			self.doWindowAction()
	@staticmethod
	def isSupported(windowHandle):
		return(False)
	def _get_name(self):
		name = self.displayText
		if not name or name.isspace() or len(name) >500:
			name = self.win32Name
		return(name)

	def _get_states(self):
		states = window.Window._get_states(self)
		# We assume that most win32 controls are focusable
		states.add(controlTypes.State.FOCUSABLE)
		focus = api.getFocusObject()
		if self == focus:
			states.add(controlTypes.State.FOCUSED)
		return(states)
	def _get_keyboardShortcut(self):
		shortcut = 'Alt+'
		letter = ''
		name = self.win32Name
		for i in range(len(name)):
			if name[i] == '&':
				try:
					letter = name[i+1]
					break
				except:
					pass
		if letter:
			return(shortcut+letter)
		return('')
	# Get rid of all the properties from the Accessibillity API that we don't need or use, so we only rely on the information fetched directly from the window.
	def _get_description(self):
		return("")
	def _get_location(self):
		return(window.Window._get_location(self))
	def _isEqual(self, other):
		return(window.Window)._isEqual(self, other)
	def _get_positionInfo(self):
		return(dict())
	def _get_next(self):
		if not getConfigFromWindow(self.windowHandle): # We do this so a user can navigate to things such as scrollbars, in a window that has been automaticly detected as another type
			return(super(Win32, self).next)
		return
	def _get_previous(self):
		if not getConfigFromWindow(self.windowHandle): # We do this so a user can navigate to things such as scrollbars, in a window that has been automaticly detected as another type
			return(super(Win32, self).previous)
		return

	def _get_firstChild(self):
		return(window.Window._get_firstChild(self))
	def _get_lastChild(self):
		return(window.Window._get_lastChild(self))
	def _get_parent(self):
		parent = window.Window(windowHandle = self.windowHandle)
		if parent == self:
			parent = window.Window._get_parent(self)
		return(parent)
	def _get_treeInterceptor(self):
		return
	def _get_value(self):
		return("")
	def _get_TextInfo(self):
		return(NVDAObjectTextInfo)
	# If we treat an object with a caret as an object type with no caret, it may cause errors.
	def event_caret(self):
		if self.TextInfo == NVDAObjectTextInfo:
			return
		super(Win32, self).event_caret()
	def _get_child(self, child):
		return(self.children[child])
	def setFocus(self):
		user32.SetForegroundWindow(self.windowHandle)
class ComplexParent(Win32):
	shouldLookAtClassName = False
	def isValid(self, index):
		childCount = self.childCount
		if childCount:
			if childCount > index:
				return(True)
			return(False)
		obj = self.subClass(windowHandle = self.windowHandle, parent = self, index = index)
		valid = bool(obj.name or obj.location and any(obj.location))
		return(valid)

	def _get_name(self):
		if not self.childCount:
			return(super(ComplexParent, self).name)
		return("")
	def _get_subClass(self):
		return(None)
	def _get_childCount(self):
		return(0)
	isComplex = True
	def _get_firstChild(self):

		if not self.isValid(0):
			return(window.Window._get_firstChild(self))
		obj = self.subClass(windowHandle = self.windowHandle, parent = self, index = 0)
		return(obj)
	def _get_lastChild(self):
		if not self.childCount:
			return(window.Window._get_lastChild(self))
		return(self.subClass(windowHandle = self.windowHandle, parent = self, index = self.childCount-1))
	def _get_focusIndex(self):
		return(-1)
	def _get_focusRedirect(self):
		index = self.focusIndex
		if not self.isValid(index):
			return
		obj = self.subClass(windowHandle = self.windowHandle, parent = self, index = index)
		return(obj)
	def getIndexFromPoint(self, x, y):
		return(-1)
	def objectFromPointRedirect(self, x, y):
		index = self.getIndexFromPoint(x, y)
		if not self.isValid(index):
			return
		obj = self.subClass(windowHandle = self.windowHandle, index = index, parent = self)
		return(obj)
class Complex(Win32):
	shouldLookAtClassName = False
	def _isEqual(self, other):
		eq = self.index == other.index and self.windowHandle == other.windowHandle
		return(eq)
	def __init__(self, windowHandle = None, parent = None, index = None):
		self.parent = parent
		self.index = index
		super(Complex, self).__init__(windowHandle = windowHandle)
	isComplex = True
	def _get_firstChild(self):
		return(None)
	def _get_lastChild(self):
		return(None)
	def _get_presentationType(self):
		return(self.presType_content)
	def _get_next(self):
		index = self.index+1
		parent = self.parent
		if not parent.isValid(self.index+1):
			return
		return(parent.subClass(windowHandle = self.windowHandle, parent = parent, index = index))
	def _get_previous(self):
		index = self.index
		if index <= 0:
			return
		return(self.parent.subClass(windowHandle = self.windowHandle, parent = self.parent, index = index-1))
	def _get_positionInfo(self):
		return({"indexInGroup": self.index+1, "similarItemsInGroup": self.parent.childCount})
	def doWindowAction(self):
		self.setFocus
class TimerMixin(NVDAObject):

	# Sometimes, accessibillity APIs considers the same onscreen object to not be equal to itself.
	# This causes the TimerMixin class to continuously fire focus events on the same object over and over.
	# So we implement more checks here
	# This implementation is bugged at the moment, and I don't know how to fix it.
	#def _isEqual(self, other): 
		#eq = super(TimerMixin, self)._isEqual(other)
		#if eq:
			#return(eq)
		#props = [
			#self.name == other.name,
			#self.role == other.role,
			#self.positionInfo == other.positionInfo,
			#self.location == other.location
		#]
		#return(all(props))
	def _get_shouldMonitorFocusEvents(self):
		if config.conf["enhancedControlSupport"]["focusEnhancement"]:
			return(True)
		if isinstance(self, DisplayChunk):
			return(True)
		if isinstance(self, Win32) and self.isComplex:
			return(True)
		return(False)
	shouldMonitorCaretEvents = False
	staticName = staticValue = ""
	staticStates = set()
	
	def initOverlayClass(self):
		self.staticName = self.name
		self.staticValue = self.value
		self.staticStates = self.states
		try:
			self.staticCaret = self.makeTextInfo(textInfos.POSITION_CARET)
		except:
			pass
	def event_gainFocus(self):
		timer.Start(50)
		if self.shouldMonitorFocusEvents:
			focusTimer.Start(50)
		super(TimerMixin, self).event_gainFocus()
	def event_loseFocus(self):
		timer.Stop()
		focusTimer.Stop()
		super(TimerMixin, self).event_loseFocus()
	def event_caret(self):
		try:
			caret = self.makeTextInfo(textInfos.POSITION_CARET)
		except:
			return
		self.staticCaret = caret
		super(TimerMixin, self).event_caret()
	def event_nameChange(self):
		self.staticName = self.name
		super(TimerMixin, self).event_nameChange()
	def event_valueChange(self):
		self.staticValue = self.value
		super(TimerMixin, self).event_valueChange()

	def event_stateChange(self):
		self.staticStates = self.states
		super(TimerMixin, self).event_stateChange()




def timerFunc(self):
	focus = api.getFocusObject()
	if not isinstance(focus, TimerMixin): return
	if focus.staticName != focus.name:
		eventHandler.queueEvent('nameChange', focus)
	if focus.staticValue != focus.value: 
		eventHandler.queueEvent('valueChange', focus)
	if focus.staticStates != focus.states:
		eventHandler.queueEvent('stateChange', focus)
	if focus.shouldMonitorCaretEvents:
		try:
			caret = focus.makeTextInfo(textInfos.POSITION_CARET)
		except:
			return
		if caret != focus.staticCaret:
			eventHandler.queueEvent('caret', focus)
def focusTimerFunc(self):
	global oldFocus
	focus = api.getFocusObject()
	realFocus = objectWithFocus()
	
	oldFocus = realFocus
	t = 500 if canTrustFocusEvents else 0
	realFocus.trustFocusEvents = False
	if not (callLater.IsRunning() or realFocus == api.getFocusObject()):
		callLater.Start(t, "gainFocus", realFocus)

timer = wx.Timer(gui.mainFrame)
gui.mainFrame.Bind(wx.EVT_TIMER, handler = timerFunc, source = timer)
focusTimer = wx.Timer(gui.mainFrame)
gui.mainFrame.Bind(wx.EVT_TIMER, handler = focusTimerFunc, source = focusTimer)

class EnhancedUIATextInfo(UIA.UIATextInfo):
	# To fix issues when NVDA tries to interact with the text field in Windows PowerShell ISE
	def _getFormatFieldAtRange(self, rangeObj, formatConfig, ignoreMixedValues = False):
		old = None
		try:
			old = super(EnhancedUIATextInfo, self)._getFormatFieldAtRange(rangeObj, formatConfig, ignoreMixedValues = ignoreMixedValues)
			return(old)
		except:
			pass
		return(None)

class EnhancedUIASupport(UIA.UIA):
	def event_UIA_elementSelected(self):
		obj = api.getFocusObject()
		conf = getConfigFromWindow(obj.windowHandle)
		if conf and conf[0] == "enhanced UIA" and isinstance(obj, behaviors.EditableTextBase):
			speech.speech.cancelSpeech()
			api.setNavigatorObject(self)
			speech.speech.speakObject(self, reason = controlTypes.OutputReason.FOCUS)
		super(EnhancedUIASupport, self).event_UIA_elementSelected()
	def _get_states(self):
		try:
			states = super(EnhancedUIASupport, self).states
		except:
			states = set()
		return(states)
	def _get_TextInfo(self):
		TextInfo = super(EnhancedUIASupport, self).TextInfo
		if issubclass(TextInfo, UIA.UIATextInfo):
			TextInfo = EnhancedUIATextInfo
		return(TextInfo)

class EnhancedTypingMixin():
	def script_caret_backspaceCharacter(self, gesture):
		info = api.getCaretPosition().copy()
		info.move(textInfos.UNIT_CHARACTER, -1)
		info.expand(textInfos.UNIT_CHARACTER)
		speech.speech.speakSpelling(info.text)
		gesture.send()
		braille.handler.handleUpdate(api.getFocusObject())
	def script_caret_backspaceWord(self, gesture):
		info = api.getCaretPosition().copy()
		info.move(textInfos.UNIT_CHARACTER, -1)
		info.expand(textInfos.UNIT_WORD)
		speech.speech.speakMessage(info.text)
		gesture.send()
		braille.handler.handleUpdate(api.getFocusObject())
	def script_caret_deleteCharacter(self, gesture):
		info = api.getCaretPosition().copy()
		info.move(textInfos.UNIT_CHARACTER, +1)
		info.expand(textInfos.UNIT_CHARACTER)
		speech.speech.speakSpelling(info.text)
		gesture.send()
		braille.handler.handleUpdate(api.getFocusObject())
	def script_caret_deleteWord(self, gesture):
		info = api.getCaretPosition().copy()
		info.move(textInfos.UNIT_CHARACTER, +1)
		info.expand(textInfos.UNIT_WORD)
		speech.speech.speakMessage(info.text)
		gesture.send()
		braille.handler.handleUpdate(api.getFocusObject())

	def event_typedCharacter(self, ch = None):
		super(EnhancedTypingMixin, self).event_typedCharacter(ch = ch)
		braille.handler.handleUpdate(api.getFocusObject())
#* slider support
#** slider messages
TBM_GETPOS = 1024
TBM_GETRANGEMAX = 1026
class Slider(Win32):
	baseRole = controlTypes.Role.SLIDER
	def _get_value(self):
		res = (winUser.sendMessage(self.windowHandle, TBM_GETPOS, 0, 0))
		return(str(res))
	@staticmethod
	def isSupported(windowHandle):
		res = winUser.sendMessage(windowHandle, TBM_GETRANGEMAX, 0, 0)
		return(bool(res))

#* edit support
#** edit messages
EM_GETLINECOUNT = 186
class NewEditTextInfo(window.edit.EditTextInfo):
	def _getTextRange(self, *args, **kwargs):
		try:
			return(super(NewEditTextInfo, self)._getTextRange(*args, **kwargs))
		except:
			return('')
class Edit(edit.UnidentifiedEdit, Win32):
	baseRole = controlTypes.Role.EDITABLETEXT
	def _get_name(self):
		return(winUser.getWindowText(self.windowHandle))
	def _get_TextInfo(self):
		info = super(Edit, self).TextInfo
		if info == edit.EditTextInfo:
			return(NewEditTextInfo)
		return(info)
	@staticmethod
	def isSupported(windowHandle):
		res = winUser.sendMessage(windowHandle, EM_GETLINECOUNT, 0, 0)
		return(bool(res))

class DisplayModelEdit(Edit):
	shouldLookAtClassName = False
	# Translators: an option in a combo box
	displayName = _("display text edit")
	def _get_TextInfo(self):
		return(displayModel.EditableTextDisplayModelTextInfo)
	@staticmethod
	def isSupported(windowHandle):
		return(False)
#* button support
#** button messages.
BM_GETCHECK = 240
BM_CLICK = 245
class Button(Win32):
	baseRole = controlTypes.Role.BUTTON
	def getActionName(self, index = None):
		# Translators: the default action message for a button
		string = _('Press')
		return(string)
	def doWindowAction(self, index = None):
		winUser.sendMessage(self.windowHandle, BM_CLICK, 0, 0)

class CheckBox(Button):
	baseRole = controlTypes.Role.CHECKBOX
	def _get_states(self):
		states = super(CheckBox, self)._get_states()
		states.add(controlTypes.State.CHECKABLE)
		res = winUser.sendMessage(self.windowHandle, BM_GETCHECK, 0, 0)
		if res == 1:
			states.add(controlTypes.State.CHECKED)
		elif res == 2:
			states.add(controlTypes.State.HALFCHECKED)
		return(states)

class RadioButton(CheckBox):
	baseRole = controlTypes.Role.RADIOBUTTON
class Text(Win32):
	baseRole = controlTypes.Role.STATICTEXT
	def _get_states(self):
		states = super(Text, self).states
		focusable = controlTypes.State.FOCUSABLE
		if focusable in states:
			states.remove(focusable)
		return(states)
	def setFocus(self):
		pass
#* Tab control support
#** tab control messages
TCM_FIRST = 0x1300
TCM_GETITEMRECT = TCM_FIRST+10
TCM_GETCURFOCUS = TCM_FIRST+47
TCM_GETCURSEL = TCM_FIRST+11
TCM_GETITEMCOUNT = TCM_FIRST+4
TCM_HITTEST = TCM_FIRST+13
TCM_SETCURFOCUS = TCM_FIRST+48
TCM_GETITEMA = TCM_FIRST+5
TCM_GETITEMW = TCM_FIRST+60
#** tab control structures
TCIF_TEXT = 0x0001
class TCITEMW32(Structure):
	_fields_ = [
		("mask", c_uint),
		("state", DWORD),
		("stateMask", DWORD),
		("text", c_ulong),
		("textMax", c_int),
		("image", c_int),
		("lParam", LPARAM)
	]
class TCITEMW64(Structure):
	_fields_ = [
		("mask", c_uint),
		("state", DWORD),
		("stateMask", DWORD),
		("text", c_ulonglong),
		("textMax", c_int),
		("image", c_int),
		("lParam", LPARAM)
	]
class TCHHITTESTINFO (Structure):
	_fields_ = [
		("point", POINT),
		("flags", c_uint)
	]
class Tab(ComplexParent):
	baseRole = controlTypes.Role.TABCONTROL
	@staticmethod
	def isSupported(windowHandle):
		return(bool(user32.SendMessageW(windowHandle, TCM_GETITEMCOUNT, 0, 0)))
	def _get_childCount(self):
		return(user32.SendMessageW(self.windowHandle, TCM_GETITEMCOUNT, 0, 0))
	def _get_subClass(self):
		return(TabItem)
	def _get_focusIndex(self):
		return(user32.SendMessageW(self.windowHandle, TCM_GETCURFOCUS, 0, 0))
	def getIndexFromPoint(self, x, y):
		point = POINT(x, y)
		user32.ScreenToClient(self.windowHandle, addressof(point))
		info = TCHHITTESTINFO(point, 0)
		tabIndex = sendMessageInProcess(self.windowHandle, TCM_HITTEST, 0, addressof(info), addressof(info), sizeof(info), shouldTryWithLocalMemoryAddress = False)
		return(tabIndex)
class TabItem(Complex):
	baseRole = controlTypes.Role.TAB
	def _get_win32Name(self):
		buffer = create_unicode_buffer(255)
		maxTextLen = 255*sizeof(c_wchar)
		internalBuffer = kernel32.VirtualAllocEx(self.processHandle, 0, maxTextLen, winKernel.MEM_COMMIT, winKernel.PAGE_READWRITE)
		if self.appModule.is64BitProcess:
			tabInfo = TCITEMW64(TCIF_TEXT, 0, 0, internalBuffer, maxTextLen, 0, 0)
		else:
			tabInfo = TCITEMW32(TCIF_TEXT, 0, 0, internalBuffer, maxTextLen, 0, 0)
		sendMessageInProcess(self.windowHandle, TCM_GETITEMW, self.index, addressof(tabInfo), addressof(tabInfo), sizeof(tabInfo), pointerToCheck = buffer, internalPointerToCheck = internalBuffer)
		kernel32.ReadProcessMemory(self.processHandle, internalBuffer, buffer, 255*sizeof(c_wchar), 0)
		kernel32.VirtualFreeEx(self.processHandle, internalBuffer, 0, winKernel.MEM_RELEASE)
		return(buffer.value)
	def _get_location(self):
		rect = RECT()
		sendMessageInProcess(self.windowHandle, TCM_GETITEMRECT, self.index, addressof(rect), addressof(rect), sizeof(rect))
		if not (rect.top or rect.bottom or rect.left or rect.right):
			return
		rect = clientRectToScreenRect(self.windowHandle, rect)
		return(locationHelper.RectLTWH.fromCompatibleType(rect))
	def setFocus(self):
		super(TabItem, self).setFocus()
		user32.SendMessageW(self.windowHandle, TCM_SETCURFOCUS, self.index, 0)
	def _get_states(self):
		states = super(TabItem, self).states
		states.add(controlTypes.State.SELECTABLE)
		if self.index == user32.SendMessageW(self.windowHandle, TCM_GETCURSEL, 0, 0):
			states.add(controlTypes.State.SELECTED)
		return(states)
#* list box support
#** list box messages
LB_GETCOUNT = 395
LB_GETCARETINDEX = 415
LB_GETITEMRECT = 408
LB_GETSEL = 391
LB_GETTEXT = 393
LB_GETTEXTLEN = 394
LB_ITEMFROMPOINT = 425
LB_SETCARETINDEX = 414
class ListBox(ComplexParent):
	# Translators: The name of an item in the select control type combo box
	displayName = _("list box")
	baseRole = controlTypes.Role.LIST
	@staticmethod
	def isSupported(windowHandle):
		res = user32.SendMessageW(windowHandle, LB_GETCOUNT, 0, 0)
		return(bool(res))
	def _get_focusIndex(self):
		return(user32.SendMessageW(self.windowHandle, LB_GETCARETINDEX, 0, 0))
	def getIndexFromPoint(self, x, y):
		point = POINT(x, y)
		user32.ScreenToClient(self.windowHandle, addressof(point))
		shortPoint = SHORTPOINT(point.x, point.y)
		# Using the shortPoint directly in SendMessageW works fine, but convert it to a normal python integer just in case
		lParam = c_long.from_address(addressof(shortPoint)).value
		res = user32.SendMessageW(self.windowHandle, LB_ITEMFROMPOINT, 0, lParam)
		return(res)
	def _get_childCount(self):
		return(user32.SendMessageW(self.windowHandle, LB_GETCOUNT, 0, 0))
	def _get_subClass(self):
		return(ListBoxItem)
class ListBoxItem(Complex):
	baseRole = controlTypes.Role.LISTITEM
	def _get_win32Name(self):
		textLength = user32.SendMessageW(self.windowHandle, LB_GETTEXTLEN, self.index, 0)
		if textLength <= 0:
			return("")
		size = textLength*sizeof(c_wchar)+1
		buffer = create_unicode_buffer(size)
		sendMessageInProcess(self.windowHandle, LB_GETTEXT, self.index, buffer, buffer, size)
		return(buffer.value)
	def _get_states(self):
		states = super(ListBoxItem, self).states
		states.add(controlTypes.State.SELECTABLE)
		if user32.SendMessageW(self.windowHandle, LB_GETSEL, self.index, 0):
			states.add(controlTypes.State.SELECTED)
		return(states)
	def _get_location(self):
		rect = RECT()
		res = sendMessageInProcess(self.windowHandle, LB_GETITEMRECT, self.index, addressof(rect), addressof(rect), sizeof(rect))
		if not (rect.left or rect.top or rect.right or rect.bottom):
			return
		rect = clientRectToScreenRect(self.windowHandle, rect)
		location = locationHelper.RectLTWH.fromCompatibleType(rect)
		return(location)
	def setFocus(self):
		super(ListBoxItem, self).setFocus()
		user32.SendMessageW(self.windowHandle, LB_SETCARETINDEX, self.index, 0)
	

#* support for unknown controls
class DisplayChunk(Win32):
	def _get_presentationType(self):
		return(self.presType_content)
	def __init__(self, windowHandle = None, info = None, parent = None, unit = displayModel.UNIT_DISPLAYCHUNK):
		super(DisplayChunk, self).__init__(windowHandle = windowHandle)
		if info.isCollapsed:
			info.expand(unit)
		self.textInfo = info
		self.unit = unit
		self.parent = parent
	def _get_name(self):
		return(self.textInfo.text)
	def _isEqual(self, other):
		return(self.textInfo == other.textInfo)
	def _get_role(self):
		windowClassName = self.windowClassName.lower()
		for i in roles:
			if i[0] in windowClassName:
				return(i[2])
		return(controlTypes.Role.UNKNOWN)

	def _get_location(self):
		startLocation = self.textInfo._getBoundingRectFromOffset(self.textInfo._startOffset)
		endOffset = self.textInfo._endOffset
		rect = None
		for i in range(endOffset, 0, -1):
		# one of the end locations is sometimes lesser than the start location.
		# I think this happens because the application draws a new line in the same operation it drew the text.
		#so move the offset back 1 character at the time until it works
			try:
				endLocation = self.textInfo._getBoundingRectFromOffset(i).toLTRB()
				rect = locationHelper.RectLTRB(startLocation.left, startLocation.top, endLocation.right, endLocation.bottom).toLTWH()
				break
			except:

				pass
		return(rect)
	def _move(self, direction):
		info = self.textInfo.copy()
		moved = False
		while info.move(self.unit, direction):
			info.expand(self.unit)
			if info.text and not info.text.isspace():
				moved = True
				break
		if moved:
			obj = DisplayChunk(windowHandle = self.windowHandle, info = info, parent = self.parent)
			return(obj)
	def _get_next(self):
		return(self._move(1))
	def _get_previous(self):
		return(self._move(-1))
class Unknown(Win32):
	baseRole = controlTypes.Role.UNKNOWN
	def objectFromPointRedirect(self, x, y):
		if not self.displayText:
			return
		try:
			info = DynamicSelectionTextInfo(self, locationHelper.Point(x, y))
		except:
			return
		obj = DisplayChunk(windowHandle = self.windowHandle, info = info, parent = self)
		if not obj.name:
			return
		return(obj)
	def _get_role(self):
		windowClassName = self.windowClassName.lower()
		for i in roles:
			if i[0] in windowClassName:
				return(i[1])
		for i in controlTypes.Role:
			if i.name.lower() in windowClassName:
				return(i)
		return(controlTypes.Role.UNKNOWN)
	cachedSelectionColor = None
	cachedBGSelectionColor = None
	isComplex = True
	def _get_name(self):
		if not self.displayText:
			return(super(Unknown, self).name)
		return("")
	def _get_selectionTextInfo(self):
		info = None
		try:
			info = displayModel.DisplayModelTextInfo(self, textInfos.POSITION_SELECTION)
		except:
			pass
		try:
			info = DynamicSelectionTextInfo(self, textInfos.POSITION_SELECTION)
		except:
			pass
		return(info)
	def _get_focusRedirect(self):
		info = self.selectionTextInfo
		if info:
			obj = DisplayChunk(windowHandle = self.windowHandle, info = info, parent = self)
			return(obj)
	def _get_firstChild(self):
		if not self.displayText:
			return
		info = DynamicSelectionTextInfo(self, textInfos.POSITION_FIRST)
		obj = DisplayChunk(windowHandle = self.windowHandle, info = info, parent = self)
		return(obj)
	def _get_lastChild(self):
		if not self.displayText:
			return
		info = DynamicSelectionTextInfo(self, textInfos.POSITION_LAST)
		obj = DisplayChunk(windowHandle = self.windowHandle, info = info, parent = self)
		return(obj)

	def _get_presentationType(self):
		return(self.presType_content)

	#def event_textChange(self):
		#eventHandler.executeEvent('nameChange', self)

class DynamicSelectionTextInfo(displayModel.DisplayModelTextInfo):
	def _getColor(self, background = False):
		if not background:
			selectionColor = self.obj.cachedSelectionColor
		else:
			selectionColor = self.obj.cachedBGSelectionColor
		if selectionColor:
			return(selectionColor)
		info = DynamicSelectionTextInfo(self.obj, textInfos.POSITION_ALL)
		text = info.getTextWithFields()
		if not text: return
		values = {}
		for i in text:
			if isinstance(i, textInfos.FieldCommand):
				if not background:
					newRgbValue = i.field.get('color')
				else:
					newRgbValue = i.field.get('background-color')
				if newRgbValue:
					rgbValue = newRgbValue
				if not rgbValue in values.keys():
					values.update({rgbValue: 0})
			elif isinstance(i, str):
				values[rgbValue] += len(i)
		keyList = list(values.keys())
		def sort(v):
			return(values[v])
		keyList.sort(key = sort)
		if len(keyList) == 1:
			return(keyList[0])
		if not background:
			self.obj.cachedSelectionColor = keyList[0]
		else:
			self.obj.cachedBGSelectionColor = keyList[0]
		return(keyList[0])

	def _get_foregroundSelectionColor(self):
		return(self._getColor())
	def _get_backgroundSelectionColor(self):
		return(self._getColor(background = True))
cfg = {}
supportedControls = []
classNamesToNVDAControlTypeNames = {}
supportedClasses = [
	Slider,
	Edit,
	Button,
	CheckBox,
	RadioButton,
	Text,
	Tab,
	ListBox,
	DisplayModelEdit,
	Unknown
]
configNamesToClasses = {}
for i in supportedClasses:
	configNamesToClasses.update({i.__name__: i})
	supportedControls.append(i.baseRole.displayString if not i.displayName else i.displayName)
	classNamesToNVDAControlTypeNames.update({i.__name__: i.baseRole.displayString if not i.displayName else i.displayName})
supportedControls.sort()
# Translators: an option in a combo box
supportedControls.insert(0, _('Use normal add-on behavior'))
supportedControls.append('MSAA')
supportedControls.append('UIA')
# Translators: an option in a combo box
enhancedUIA = _("enhanced UIA")
supportedControls.append(enhancedUIA)
# Translators: an option in a combo box
normal = _('Use normal NVDA behavior')
supportedControls.append(normal)
classNamesToNVDAControlTypeNames.update({'MSAA': 'MSAA', 'UIA': 'UIA', "enhanced UIA": enhancedUIA, 'normal': normal})
class ControlDialog(SettingsDialog):
	# Translators: The title for the control type selection dialog
	title = _("Select control type")
	helpId = None
	def __init__(self, *args, obj, name, role, **kwargs):

		self.obj = obj
		self.key = getKeyFromWindow(self.obj.windowHandle, bypassDisabled = True)
		self.name = name
		self.role = role
		super(ControlDialog, self).__init__(*args, **kwargs)

	def makeSettings(self, settingsSizer):
		helper = gui.guiHelper.BoxSizerHelper(self, sizer = settingsSizer)
		obj = self.obj
		name = self.name
		if not name:
			# Translators: a part of the text in a dialog box
			name = _('unlabeled')
		role = self.role.displayString
		
		# Translators: The start of a text in a dialog box
		start = _('Select a control type. NVDA will behave as if')
		middle = f' {name} {role} '
		# Translators: the end of a text in a dialog box
		end = _('and all similar controls in the same program are the control type you selected, for example, if you select button, all similar controls will be treated as buttons')
		text = start+middle+end
		self.StaticText = helper.addItem(wx.StaticText(self, label = text))
		# Translators: A label for a combo box
		label = _('Control type:')
		self.choice = helper.addLabeledControl(label, wx.Choice, choices = supportedControls)
		# Translators: the label for a check box
		label2 = _('rely on events. Only change if you know what you are doing')
		self.checkBox = wx.CheckBox(self, label = label2)
		helper.addItem(self.checkBox)
		# Translators: The label for a check box
		label = _("Use enhanced typing support")
		self.enhancedTyping = wx.CheckBox(self, label = label)
		helper.addItem(self.enhancedTyping)
		# Translators: The label for a check box
		label = _('Temporarily use normal add-on behavior for all controls')
		self.disable = wx.CheckBox(self, label = label)
		helper.addItem(self.disable)
		self.disable.SetValue(disabled)
	def postInit(self):

		conf = cfg.get(self.key)
		if not conf:
			self.choice.SetSelection(0)
		else:
			className = conf[0]
			type = classNamesToNVDAControlTypeNames.get(className)
			index = supportedControls.index(type)
			self.choice.SetSelection(index)
			eventSupport = conf[1]
			self.checkBox.SetValue(eventSupport)
			# Backword compatibility with erlier versions of the addon
			if len(conf) <= 2:
				conf.append(False)
			enhancedTyping = conf[2]
			self.enhancedTyping.SetValue(enhancedTyping)
		
		self.choice.SetFocus()
	def onOk(self, *args, **kwargs):
		global disabled
		disabled = self.disable.GetValue()
		global cfg
		if cfg.get(self.key):
			cfg.pop(self.key)
		selection = self.choice.GetSelection()
		if not selection: # The user wants to use the control as normal, so return here.
			return(super(ControlDialog, self).onOk(*args, **kwargs))
		conf = {}
		name = supportedControls[selection]
		for i in classNamesToNVDAControlTypeNames.keys():
			if classNamesToNVDAControlTypeNames.get(i) == name:
				name = i
		checked = self.checkBox.GetValue()
		enhancedTyping = self.enhancedTyping.GetValue()
		conf = [name, checked, enhancedTyping]
		cfg.update({self.key: conf})
		return(super(ControlDialog, self).onOk(*args, **kwargs))
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(GlobalPlugin, self).__init__()
		UIAHandler.UIAHandler.isUIAWindow = newIsUIAWindow
		global cfg
		try:
			open(configPath, 'x')
		except:
			pass
		f = open(configPath, )
		try:
			cfg = json.load(f)
		except:
			pass
		f.close()
		self.displayObj = None
		config.post_configSave.register(saveConfig)
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(EnhancedControlSupportSettingsPanel)
	def terminate(self):
		super(GlobalPlugin, self).terminate()
		UIAHandler.UIAHandler.isUIAWindow = oldIsUIAWindow
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(EnhancedControlSupportSettingsPanel)
	def event_gainFocus(self, obj, nextHandler, trustFocusEvents = True):
		global oldFocus
		global canTrustFocusEvents
		oldFocus = objectWithFocus()
		canTrustFocusEvents = not hasattr(obj, "trustFocusEvents")
		if canTrustFocusEvents:
			callLater.Stop()
		nextHandler()
	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if not isinstance(obj, window.Window):
			return
		conf = getConfigFromWindow(obj.windowHandle)
		# Check if any of the classes in clsList is a subclass of Complex
		# If they are, we are in an unknown control, and should not rely on events

		if not issubclass(obj.APIClass, Win32) and not "kwargsFromSuper" in obj.APIClass.__dict__:
			return
		newCls = None

		if IAccessible.WindowRoot in clsList:
			return
		isEditable = False

		if conf or IAccessible.ContentGenericClient in clsList:
			
			if shouldUseWin32(obj.windowHandle) and not issubclass(obj.APIClass, Win32):
				newCls = configNamesToClasses[conf[0]]
			elif IAccessible.ContentGenericClient in clsList and not conf:
				newCls = findSupportedClass(obj.windowHandle)
			if newCls:
				for i in clsList.copy():
					if i == obj.APIClass or i in obj.APIClass.mro():
						continue
					clsList.remove(i)
				clsList.insert(0, Win32)
				clsList.insert(0, newCls)
				# Since all classes from global plugins that was in clsList are now removed,
				# go through each global plugin that earlier added classes to clsList and let it evaluate the object again.
				for i in globalPluginHandler.runningPlugins:
					if isinstance(i, GlobalPlugin): break

					try:
						i.chooseNVDAObjectOverlayClasses(obj, clsList)
					except:
						pass
		for i in clsList:
			if issubclass(i, editableText.EditableText):
				isEditable = True
		if isEditable and conf and conf[2]:
			clsList.insert(0, EnhancedTypingMixin)
		if obj.windowClassName.startswith("HwndWrapper") and isEditable and not conf:
			clsList.insert(0, EnhancedTypingMixin)
		if issubclass(obj.APIClass, UIA.UIA) and UIA.UIA in clsList:
			if conf and conf[0] == "enhanced UIA":
				index = 0
			else:
				index = clsList.index(UIA.UIA)
			if not (conf and conf[0] == "normal"):
				clsList.insert(index, EnhancedUIASupport)
		copyList = clsList.copy()

		if conf and conf[0] in ["UIA", "enhancedUIA"]:
			for i in copyList:
				if issubclass(i, IAccessible.IAccessible) and i != IAccessible.IAccessible:
					clsList.remove(i)
		if conf and conf[0] == 'MSAA':
			for i in copyList:
				if issubclass(i, UIA.UIA) and i != UIA.UIA:
					clsList.remove(i)
		if shouldUseTimerMixin(conf, obj, clsList):
			clsList.insert(0, TimerMixin)


	@script(
		# Translators: Describes the select control type script
		description = _('Lets you choose from a list of controls how NVDA will treat the control with focus. For example, choos \'button\' To tell NVDA to treat it as a button.'),
		gesture = 'kb:nvda+alt+c'
	)
	def script_selectControlType(self, gesture, obj = None):
		if not obj:
			obj = api.getFocusObject()
		message = None
		if not isinstance(obj, window.Window):
			# Translators: The message that is reported when the NVDAObject is a custom object, that has no assosiation with a control in Windows.
			message = _('You can not assign another control type to this object, because it has no assosiation with a control in Windows')
		elif obj.processID == appPid:
			#Translators: The message reported when the object belongs to the NVDA process
			message = _('You can not assign another control type to any object contained within NVDA, because if done wrong, you may not be able to reverse the changes you have made')
		if message:
			ui.message(message)
			return
		obj = window.Window(windowHandle = obj.windowHandle)
		try:
			name = obj.name
		except:
			name = ''
		try:
			role = obj.role
		except:
			role = controlTypes.Role.UNKNOWN
		gui.mainFrame._popupSettingsDialog(ControlDialog, obj = obj, name = name, role = role)
	@script(
		# Translators: describes the select control from navigator script:
		description = _('Lets you choose from a list of controls how NVDA will treat the control where the navigator object is located. For example, choos \'button\' To tell NVDA to treat it as a button.'),
		gesture = 'kb:nvda+shift+alt+c'
	)
	def script_selectControlFromNavigator(self, gesture):
		nav = api.getNavigatorObject()
		if not nav:
			ui.message(translate('no navigator object'))
			return
		self.script_selectControlType(gesture, obj = nav)
	@script(
		# Translators: Describes the find control type script
		description = _('Tries to find out an report the type of the  control with focus. If pressed twice, information about the control where the navigator object is located will be reported instead'),
		gesture = 'kb:nvda+alt+r'
	)
	def script_findControlType(self, gesture):
		
		if not getLastScriptRepeatCount():
			windowHandle = api.getFocusObject().windowHandle
		else:
			windowHandle = api.getNavigatorObject().windowHandle
		cls = findSupportedClass(windowHandle)
		if not cls:
			# Translators: The message reported when NVDA can't find out what type of control it is
			message = _('Unable to find control type')
			ui.message(message)
			return
		ui.message(cls.baseRole.displayString if not cls.displayName else cls.displayName)