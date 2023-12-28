# Enhanced Control Support
* Author: Emil-18
* NVDA compatibility: 2023.1 and beyond
* Download: [Stable version](https://github.com/emil-18/enhanced-control-support/releases/download/v0.1/enhanced-control-support.nvda-addon)
This add-on allows NVDA to recognize some custom controls that are based on standard ones such as buttons, check boxes, and sliders and read them properly. When NVDA incounters an unknown control, it will try to find out what type of control it actualy is. If found, the control wil be reported as normal.
You can also make NVDA interpret a control as if it is something else. This is useful if a control gives itself out to be for example a pane, when it actualy is a button. 
## Gestures:
* NVDA+ALT+C: Open the dialog used to change control type for the focused control.
* NVDA+ALT+SHIFT+C: Open the dialog used to change control type for the control where the navigator object is located.
## settings of the select control type dialog
* Control type combo box:
This is a combo box that lists all the control types you can select from. You can also force NVDA to use MSAA or UIA to access the control
* rely on events check box:
This is a check box that allows you to choose if NVDA should rely on events sent by the control to report things such as state changes. Most custom controls do not implement these events correctly, so it is off by default