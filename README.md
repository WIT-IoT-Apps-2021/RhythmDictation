# RhythmDictation
A rhythm dictation tool for the BBC micro:bit.

By tapping the micro:bit's touch sensor, a rhythm can be input which is played back via the onboard speaker and communicated to a desktop.
A music score is then generated and displayed to the user.
[Video Demo](https://drive.google.com/file/d/1Q4iKzDscS2v_hw8JoCD7HdMdL5sUYNvL/view?usp=sharing).

## Components
The microbit directory contains the Python source file and a precompiled HEX file.  
The code was developed using the micro:bit MicroPython editor [here](https://python.microbit.org).

The micro:bit should be connected via USB to allow the captured rhythm data to be communicated over serial.  
The supplied Python script `serial_to_influx.py` is set up to poll `/dev/ttyACM0` and do operations on the data.

Upon reading a line of rhythm data, a LilyPond source file is generated and the bash script `generate_score.sh`
is called to process it.
The bash script generates the score PNG using LilyPond, crops it using ImageMagick and moves it to the directory
where Apache HTTPd serves the file locally.
The score can then be viewed by accessing the appropriate link, here achieved through a simple Markdown panel on Grafana (`grafanapanel.md`).

Due to time constraints it was not possible to implement all of the desired data presentation,
as such the data transmitted to InfluxDB is underdeveloped.
Further development would involve storing rhythm data so that it could be presented visually, possibly using a time series graph.
It would also be preferable to host score images in the cloud, in an AWS S3 bucket for example.
