#!usr/bin/env python3
import serial
import logging
from datetime import datetime
import subprocess

import toml
from flask import Response
from influxdb_client import InfluxDBClient, WriteOptions


def parse_music_string(music_bstr):
    # split on colon
    [bpm_str, phrase_str] = music_data.split(b':')
    # parse bpm
    bpm = int(bpm_str)
    # drop leading bracket from list
    phrase_str = phrase_str[2:]
    note_strs = phrase_str.split(b', ')
    # parse leading notes
    notes = [int(n) for n in note_strs[:-1]]
    # drop trailing bracket and append final note
    notes.append(int(note_strs[-1][:-3]))
    return (bpm, notes)

def generate_score(bpm, notes):
    lily_file = open("rhythm.ly", "w")
    # write source
    note_strs = [str(n) for n in notes]
    note_string = ' '.join(note_strs)
    source = (
        r'''\version "2.22.1"
        #(set-global-staff-size 26)
        \header {{ tagline = "" }}
        \relative {{
            \tempo 4 = {bpm}
            g'{phrase}
        }}''').format(bpm=bpm, phrase=note_string)
    lily_file.write(source)
    lily_file.close()
    # generate score with lilypond
    subprocess.run(["./generate_score.sh"])

def write_to_influx(fields):
    '''Write data to InfluxDB and return a Flask response'''
    # Attempt to load the config_file file
    try:
        config_file = toml.load('config.toml')['influxdb']
    except (FileNotFoundError, KeyError):
        logging.error('Config file not found.')

    influx_protocol = "http"
    if config_file['tls']:
        influx_protocol = "https"

    # Initalize database collection
    _client = InfluxDBClient(url=f"{influx_protocol}://{config_file['host']}:{config_file['port']}",
                             verify_ssl=config_file['verify_tls'], org=config_file['organization'],
                             token=config_file['token'])

    _write_client = _client.write_api(write_options=WriteOptions(batch_size=500, flush_interval=10_000, jitter_interval=2_000, retry_interval=5_000,
                                                                 max_retries=5, max_retry_delay=30_000, exponential_base=2))

    # Add the data in JSON format
    json_body = {
        "measurement": "rhythm_phrase",
        "tags": {},
        "time": datetime.utcnow().isoformat(),
        "fields": fields
    }

    # Attempt to write the list of datapoints to the database
    try:
        # Write the JSON object into the database
        _write_client.write(config_file['bucket'], config_file['organization'], json_body)
        _write_client.__del__()
        logging.info('Data written to DB (%d) items)', len(json_body))
        # Close the connection to InfluxDB
        _client.close()
    # pylint: disable=broad-except
    except Exception as err:
        logging.error('Error writing to DB - %s', err)
        # Close the connection to InfluxDB
        _client.close()

ser = serial.Serial('/dev/ttyACM0', baudrate=115200)
while True:
    #music_data = b'200 : [4, 4, 8, 8, 4]\r\n' # dummy test data
    music_data = ser.readline()
    (bpm, notes) = parse_music_string(music_data)
    generate_score(bpm, notes)

#rhythm_fields = {
#        "score": "http://localhost/scores/score.png"
#}

#write_to_influx(rhythm_fields)
