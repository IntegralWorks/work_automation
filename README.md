# VISA_AUTOMATION
Progress: Following tasks are automated:

* Find the "crosses" (see: https://en.wikipedia.org/wiki/Zero_crossing) of 2-4 waveforms and display the following in an Excel workbook:
  * Zoomed-in matplotlib screenshots on one Excel worksheet
  * A dataframe of all the crosses and their deltas on another worksheet
* Set labels and voltage scalings, plus backup said scalings from the computer as opposed to using a keyboard/mouse on the scope (reduces the need for clutter and speeds up process)

TO-DO:
* Improve "captureScopeData.py" as so:

  I. Make a -nocompare/-noXC argument that disables the x-cross comparisions and simply graphs the data.
  
  II. Abstract system arguments into a config file.
  
  III. A test mode where the scope is converted to a "fast format" (will need to performance test numpy arrays vs sqlite)
  
  IV. Testing for when different channels are used in different contexts
  
  V. Might make a GUI.
  
* Document "Fluke Automation"
---------------------------------------------------------------------------------------------------------------------------------------
# generalDataScience
I have some "throwaway" scripts laying around my company device (who doesn't) the ones that are particularly useful, noteworthy, or liable to get lost go here. Will need to put a table of contents here since some are highly contextual (ex. processData.py makes zero sense unless you know it's extremely specific to ".csv output from Tektronix MDO3000 series oscilloscopes").

---------------------------------------------------------------------------------------------------------------------------------------
# FFMPEG_Scripts
Could also be called "mp4 scripts". Scripts for routine operations (muting/speeding up/deletion).

---------------------------------------------------------------------------------------------------------------------------------------
# LTSpice_scripts
Currently a lone script, upon receiving more LTSpice tasks will write some more code. 

---------------------------------------------------------------------------------------------------------------------------------------
# CAN_bus
Another lone script. In the future we will be crunching tons of CAN data and will need to write a data science program.

---------------------------------------------------------------------------------------------------------------------------------------
# ~~autoscreenshotpy~~ (depreciated)

Was a clever script while it lasted (there was a period where the only available computer was an xp laptop running python 3.3), but Snaggit ended up taking care of "record the scope" needs at the time. Now, I am shifting the team to use matplotlib more and eventually we will only need cursory screenshots of waveforms complementing mostly matplotlib videos/images.

Update(09/08/2020): I am going to refit this with VISA so that I can autonomously take pictures of each part of the waveform given some condition.

---------------------------------------------------------------------------------------------------------------------------------------

# ~~zero-cross-automation~~ (depreciated)
Seeks out the zero-crosses of sinusoidal and/or square wave voltage waveforms. Upon further review of oscilloscope documentation it was determined that using the scope's built-in search functionality was a superior approach. Not much code was reused *but* many important lessons, design do's/don'ts, and goals were developed from the making of this script.

---------------------------------------------------------------------------------------------------------------------------------------
