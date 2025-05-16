# Enhanced Control Support.
* Author: Emil-18.
* NVDA compatibility: 2024.4 and beyond.
* Download: [Stable version](https://github.com/Emil-18/enhanced-control-support/releases/download/v1.2/enhancedControlSupport-1.2.nvda-addon).

This add-on allows you to use some controls that normally don't work with NVDA. You can force NVDA to interpret a control as another type, for example, a pane can be interpreted as a check box. This may enhance the reporting of that control, for example let NVDA report the checked/unchecked state. In some cases, NVDA will also recognise more controls on its own.

Note:

When this add-on refers to controls, it does not refer to individual objects. You can not, for instance, change only the list items of a list into buttons, the whole list will be treated as one button.

What is defined as a control is application specific. The buttons of the run dialog, for instance, is eatch defined as one control. In contrast, everything in the windows 10 calculator is  part of one control, the window itself.

For now, the add-on supports:

* Buttons.
* Check boxes.
* Edit controls.
* Display text edit controls. A type of edit control where NVDA will get the text and caret from what the application has written to the screen, as supposed to using accessibility APIs. Screen review must function in the control for this to work.
* Radio buttons.
* Sliders.
* Text controls.
* list boxes.
* tab controls.
## Automatic control type recognition.

When NVDA encounters an unknown control, it will automaticly try to find out what type of control it is. If found, it will be reported as closely as possible to what NVDA normally reports when interacting with that type of control.

## Manually changing control type.

Sometimes, when NVDA doesn't report a control as unknown, but instead as pane, it is impossible to determine if the control actually is a pane or not. Because of this, the add-on implements functionality to force NVDA to interpret the control as another type.

You can also force NVDA to use MSAA or UIA to access the control. This is useful if NVDA behaves poorly with the accessibility API it selects on its own.

NVDA normaly uses either MSAA or UIA to access controls, so one of these will be identical to normal NVDA behavior.

Try to change accessibillity API if:

* NVDA's object navigation doesn't work as it should.
* NVDA fails to follow the focus, but the control works partially or fully with object navigation and/or mouse tracking.
* NVDA reports wrong information about the control.

You can do both of these things using the control type combo box (see below).

## Working with unknown controls.

If NVDA can't find out what a control is, it will determine the controls type by checking the controls class name. For example, if the class name contains the word "list", NVDA will report the control as a list, and any underlying controls as list items. NVDA will try to find out where the focus is by looking at the text colors. Note that the control must support screen review for this to work.

NVDA will treat the text that has the least recurring color in the control as where the focus is located.

You can use object navigation to navigate between pieces of text inside the control.

Any control can be treated as unknown by selecting "unknown" in the control type combo box (see below).



Note:

When this add-on is enabled, you can not read all the visual text in the control in object review mode when landing in an unknown control like you can normally.

To restore normal NVDA behavior for the current control, select "Use normal NVDA behavior" in the control type combo box (see below).

## Enhanced UIA.

When this is selected from the control type combo box (see below), and if you are in a text field, NVDA will move the navigator object to selected suggestions when they appear.
Note that this may overwrite NVDA's custom support for some controls.

## Enhanced typing support.

In some controls, NVDA behaves strangely when typing or deleting text, e.g, not speaking the deleted character/word, or not updating braille. One example include the main edit control in visual studio. Enhanced typing support attempts to fix these issues.
Enhanced typing support will be enabled automaticly in some controls, but you can always turn it on by checking the "Use enhanced typing support" check box in the select control type dialog (see below).

## Gestures:

* NVDA+ALT+C: Open the dialog used to change control type for the focused control.
* NVDA+ALT+SHIFT+C: Open the dialog used to change control type for the control where the navigator object is located.
* NVDA+alt+r: Reports the type of control where the focus, if pressed once, or the navigator object, if pressed twice, is located.
## settings of the select control type dialog.

* Control type combo box:
This is a combo box that lists all the control types you can select from.
What you select here will only affect controls in the application you interacted with when opening the dialog.
It will also only affect controls that is similar to the control you interacted with before opening the dialog.
Let's say you changed the OK button in the run dialog to be treated as a check box.
Now, the cancel and browse buttons will also be reported as check boxes, but the edit field will still be reported as an edit field, because it is a different type of control.
Same if you for example open the save dialog in word pad. The buttons there will still be treated as buttons, because they are in a different program then the run dialog.
Note that when you select "Use normal add-on behavior", every modification you have done to the control via this add-on will be deleted.
This is not the case when you select "use normal NVDA behavior". You can, for instance, make the control use normal NVDA behavior, and still choose to not rely on events.
* rely on events check box:
This is a check box that allows you to choose if NVDA should rely on events, notifications sent by controls to screen readers to notify them about things such as name changes, when interacting with the control. Most custom controls do not implement events correctly, so it is off by default.
It will also be treated as off when NVDA automaticly recognises a custom control. If unchecked, NVDA will continuously ask the focused object for its name, states, etc. If the information is different from the last time NVDA asked for it, the new information will be reported.
* Use enhanced typing support check box
This is a check box that allows you to choose if NVDA should use enhanced typing support when interacting with the control.
This is useful if NVDA behaves strangely when typing or deleting text.
* Temporarily use normal add-on behavior for all controls check box:
if checked, NVDA will use normal add-on behavior for all controls until NVDA is restarted or the check box is un checked again. This is useful if you have changed a control but it breaks NVDA to the point where it is impossible to change the control back.
## add-on settings

* Rely on events by default: This is a check box that determines if NVDA should rely on events. If unchecked, NVDA will continuously ask the focused object for its name, states, etc. If the information is different from the last time NVDA asked for it, the new information will be reported. This setting is off by default.
* Use enhanced methods to detect where the focus is located (experimental): same as above, just for focus instead. This setting is off by default.
## Changelog
### v 1.2
* Added compatibility with NVDA 2025
* Added support for list boxes, tab controls, and display text edit controls.
* Fixed a bug that broke NVDA's support with word when UIA is enabled.
* When Enhanced UIA is selected and  a selected suggestion appears, the navigator object will be moved to it, rather then the focus.
* The support for unknown controls has been redone
    * You can now use object navigation to go between each piece of text in the control.
    * NVDA will now treat the text that has the least recurring colors as an object of its own, rather then the name of the control.
* Added a settings panel with the following settings. For detailed information of what these settings do, check the relevant section of the documentation.
    * Rely on events by default
    * Use enhanced methods to detect where the focus is located (experimental)

### v1.1

* Added a new option called "enhanced UIA"
* Added a new Enhanced typed character support setting. This can be toggled in any control via the select control type dialog, but will be enabled by default for certain controls
* Fixed some UIAutomation errors present in NVDA.
### v1.0.1

The add-on should no longer play error sounds when changing accessibillity API
### v1.0
Initial release.
