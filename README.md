# autoscreenshotpy (depreciated)

Was a clever script while it lasted, but Snaggit ended up taking care of "record the scope" needs at the time. Now, I am shifting the team to use matplotlib more and eventually we will only need cursory screenshots of waveforms complementing mostly matplotlib videos/images.

---------------------------------------------------------------------------------------------------------------------------------------
# findmp4s.py
At work we now use a tool called Snaggit(TM) to take videos of the scope. Right now, pyautoscreenshot is somewhat shelved although there's a few features Snaggit does not have that I'm certain I could implement through pyautoscreenshot (basically I want to set profiles because we take the same kind of screenshot multiple times a day), but at work there are more pressing things to automate. Namely, recursively taking mp4 files and speeding them up fourfold. This handy little script cobbles together two SO answers and some special F'string sauce to tap into FFMPEG's tried-and-tested powers.

---------------------------------------------------------------------------------------------------------------------------------------
# delete_mp4s.py
I got an inspiration to make a general purpose script after realizing I needed to clean out all the files recursively from a parent dir and its children. "findmp4s" and "delete_mp4s" will be the foundation for the following:

* Use sysargv to ask user what type of file type they want to manipulate
* prompt a menu to ask if the user wants to speed up all mp4 files or delete them

I have some other ideas, but for now this is something we really need at work and I just don't want to lose this idea.

---------------------------------------------------------------------------------------------------------------------------------------
# trc_to_csv.py (version ~.0.2)
Tentative title
Takes .trc CAN bus data and vectorizes to numpy, plots to mplt, exports plots to excel
