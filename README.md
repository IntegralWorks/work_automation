# VISA_AUTOMATION
Progress:Can now trigger a scope and gather all channel data in seconds (or gather all channel data from a scope that is already triggered). Feature to-do list: simultaneous triggering, automated instrument detection, and a basic GUI in either PySimpleGUI or Dear PyGui.

Also need to implement GUI for setLabelandScale.py

---------------------------------------------------------------------------------------------------------------------------------------
# generalDataScience
I have some "throwaway" scripts laying around my company device (who doesn't) the ones that are particularly useful, noteworthy, or liable to get lost go here. Will need to put a table of contents here since some are highly contextual (ex. processData.py makes zero sense unless you know it's extremely specific to ".csv output from Tektronix MDO3000 series oscilloscopes").

---------------------------------------------------------------------------------------------------------------------------------------
# FFMPEG_Scripts
Could also be called "mp4 scripts". Scripts for routine operations (muting/speeding up/deletion).

---------------------------------------------------------------------------------------------------------------------------------------
# zero-cross-automation
Seeks out the zero-crosses of sinusoidal and/or square wave voltage waveforms. WIP and the latest version is on company device.

---------------------------------------------------------------------------------------------------------------------------------------
# LTSpice_scripts
Currently a lone script, upon receiving more LTSpice tasks will write some more code. 

---------------------------------------------------------------------------------------------------------------------------------------
#CAN_bus
Another lone script. In the future we will be crunching tons of CAN data and will need to write a data science program.

---------------------------------------------------------------------------------------------------------------------------------------
# autoscreenshotpy ~~(depreciated)

Was a clever script while it lasted (there was a period where the only available computer was an xp laptop running python 3.3), but Snaggit ended up taking care of "record the scope" needs at the time. Now, I am shifting the team to use matplotlib more and eventually we will only need cursory screenshots of waveforms complementing mostly matplotlib videos/images.

Update(09/08/2020): I am going to refit this with VISA so that I can autonomously take pictures of each part of the waveform given some condition.

---------------------------------------------------------------------------------------------------------------------------------------
