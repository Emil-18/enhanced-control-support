# Enhanced Control Support
* Author: Emil-18
* NVDA compatibility: 2023.1 and beyond
* Download: [Stable version](https://github.com/emil-18/enhanced-control-support/releases/download/v0.1/enhanced-control-support.nvda-addon)

This add-on allows NVDA to recognize some custom controls that are based on standard ones such as buttons, check boxes, and sliders and read them properly.
For now, the add-on supports:

* Buttons
* Check boxes
* Edit controls
* Radio buttons
* Sliders
* Text controls

If NVDA doesn't recognise a control, it will read the visual text on the screen where it thinks the focus is located. The controll has to support screen review for this to work.


You can also make NVDA interpret a control as if it is something else. This is useful if  NVDA reports a control as for example a pane, when it actualy is a button. This may result in more information being reported, such as the checked state of checkboxes, or the position of sliders.
Note:

When this add-on refers to controls, it does not refer to individual objects. You can not, for instance, change only the list items of a list into buttons, the hole list will be treated as one button.
What is defined as a control is application specific. The buttons of the run dialog, for instance, is eatch defined as one control. In contrast, everything in the windows 10 calculator is  part of one control, the window itself

## Gestures:
* NVDA+ALT+C: Open the dialog used to change control type for the focused control.
* NVDA+ALT+SHIFT+C: Open the dialog used to change control type for the control where the navigator object is located.
* NVDA+alt+r: Reports the type of control where the focus, if pressed once, or the navigator object, if pressed twice, is located
## settings of the select control type dialog
* Control type combo box:
This is a combo box that lists all the control types you can select from. You can also force NVDA to use MSAA or UIA to access the control
* rely on events check box:
This is a check box that allows you to choose if NVDA should rely on events sent by the control to report things such as state changes. Most custom controls do not implement these events correctly, so it is off by default
* Temporarily use normal add-on behavior for all controls checkbox
if checked, NVDA will use normal add-on behavior for all controls until NVDA is restarted or the check box is un checked again. This is useful if you have changed a control but it breaks NVDA to the point where it is impossible to change the control back