# work_automation
Automation scripts for work. autoscreenshot.py is version .8; all names tentative. Planned features are: 
  * PySimpleGUI interface
  * The option to set profiles for: 
    - the area of a given monitor to screenshot
    - number of screenshots and the delay in milliseconds between them
  * A check for the directory name chosen is already made
    - if it has files in: provide warning asking to double check before deletion
    - if it doesn't have files in: delete it and continue the task
    

Planned program: some background: I work with an oscilloscope at work often. we always need the frequency, min, max, and high_average, low_average of a given waveform. 
All this information can actually be captured in one screenshot, but because of certain hardware limitations, we can only automate data gathering from our scopes using screenshots from a browser application.
Therefore, I want to implement a program "interpretText.py" that will scan specify areas of all screenshots, and use one of those "recognition" libraries to extract the text.
The text will then autonomously be exported to a nicely organized spreadsheet.

Development process: 
I. CLI-only app is ver 0.x and *must* contain the core functionality needed to save time at work. The program should work well enough that the worst-case scenario--being that there is not enough time to stop testing to develop automation software--the script will still save sizeable time.
II. First ver at 1.x will have a basic GUI. Should continue to save time while being non-developer friendly.
III. Scripts or programs that make it to 2.0.x mean that only bug fixes apply, 2.x.y or z.x.y means it is a more generally extensible program that I aim to add proper licensing to and open source to its own repository.

ROADMAP:
I. Added "minimal viable" support for .gif and .mp4 files (fufilled feature request at work).
II. Next up is probably basic GUI.
