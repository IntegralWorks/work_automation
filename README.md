# pyautoscreenshot
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

---------------------------------------------------------------------------------------------------------------------------------------
# findmp4s.py
At work we now use a tool called Snaggit(TM) to take videos of the scope. Right now, pyautoscreenshot is somewhat shelved although there's a few features Snaggit does not have that I'm certain I could implement through pyautoscreenshot (basically I want to set profiles because we take the same kind of screenshot multiple times a day), but at work there are more pressing things to automate. Namely, recursively taking mp4 files and speeding them up fourfold. This handy little script cobbles together two SO answers and some special F'string sauce to tap into FFMPEG's tried-and-tested powers.

---------------------------------------------------------------------------------------------------------------------------------------
# delete_mp4s.py
I got an inspiration to make a general purpose script after realizing I needed to clean out all the files recursively from a parent dir and its children. "findmp4s" and "delete_mp4s" will be the foundation for the following:

* Use sysargv to ask user what type of file type they want to manipulate
* prompt a menu to ask if the user wants to speed up all mp4 files or delete them

I have some other ideas, but for now this is something we really need at work and I just don't want to lose this idea.
