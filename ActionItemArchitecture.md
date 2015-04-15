Architecture for how actionable items are put on the pop-up menu presented for each item.

# Introduction #

Each item listed out in the fileBrowser should have actionable items on it like move and tag. These actions are presented by some form of pop up list. Each action consists of three parts:
  * Matching regex - given a file name does this action apply to it.
  * Name - name provided in the pop up list.
  * Action - function that is called when the action is selected


# Implementation #

Each action should implement the iActionItem interface.