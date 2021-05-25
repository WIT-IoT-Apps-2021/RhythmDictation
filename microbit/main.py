from microbit import *
import utime
import music

last_beat = utime.ticks_ms()    # the last beat that was received
bpm = 0

# capture next four beats and try to infer bpm
def capture_bpm():
    #print("Trying to set bpm")
    global bpm
    # collect next four beats
    beats = []
    while (len(beats) < 4):
        beats.append(next_beat())
    #print(str(beats))
    # time between four beats are the last three deltas
    deltas = beats[1:]
    # calculate mean time delta
    avg_delta = round(sum(deltas) / 3)
    # ensure all deltas are within threshold of average
    beats_valid = all((abs(d - avg_delta) < 50) for d in deltas)
    if not beats_valid:
        #print("Failed")
        return False
    # calculate bpm (number of times avg_delta goes into 60,000 ms)
    bpm = round(60000/avg_delta)
    #print("Success!")
    return True

# capture beats until timeout and parse resulting phrase
def capture_phrase():
    # collect beats until timeout occurs
    beats = []
    while True:
        new_beat = next_beat(timeout=True)
        # if timeout occurred
        if new_beat == -1:
            break
        beats.append(new_beat)
    #print(beats)
    # parse phrase
    return parse_phrase(beats)

# quantise millisecond durations and convert into note encoding
def parse_phrase(beats):
    # create quantised durations for half, quarter and eighth note
    quantise_vals = [round((60000/bpm)*x) for x in [2,1,0.5]]
    # replace each delta with closest matching quantised value
    deltas = beats[1:]
    quantised_deltas = [min(quantise_vals, key=lambda q:abs(q-d)) for d in deltas]
    # convert into note encoding
    # 2 for half note, 4 for quarter, 8 for eighth
    notes = [2**(quantise_vals.index(d)+1) for d in quantised_deltas]
    # last note is always a quarter
    notes.append(4)
    return notes

# play phrase using microbit speaker
def play_phrase(phrase):
    global last_beat
    # convert note encoding to microbit music
    notes = []
    for p in phrase:
        notes.extend(microbit_music_encoding(p))
    music.set_tempo(ticks=4, bpm=bpm)
    # wait until next beat to stay in time 
    beat_length_ms = round(60000/bpm)
    while (utime.ticks_diff(utime.ticks_ms(), last_beat) < beat_length_ms):
        pass
    # play notes
    music.play(notes)
    # dummy beat to reset timeout
    last_beat = utime.ticks_ms() - 500

# play cue for user to begin entering a phrase
def play_cue():
    # create list of four quarter notes
    cue = [4] * 4
    play_phrase(cue)

# convert note encoding to microbit music format
def microbit_music_encoding(note):
    mapping = {2:4, 4:2, 8:1}
    return ['c1:'+str(mapping[note]), 'r']

# wait until next beat and return duration in milliseconds
def next_beat(timeout=False):
    global last_beat
    while True:
        if (pin_high() and cooldown_finished()):
            # get time elapsed
            now = utime.ticks_ms()
            diff_ms = utime.ticks_diff(now, last_beat)
            # update global
            last_beat = now
            #print("Got a beat: " + str(diff_ms))
            return diff_ms
        if (timeout and timeout_expired()):
            return -1

# if user is currently pressing button
def pin_high():
    return pin_logo.is_touched()

# if minimum cooldown time has elapsed since last beat (for debouncing)
def cooldown_finished():
    now = utime.ticks_ms()
    return (utime.ticks_diff(now, last_beat) > 200)

# if one bar of silence has elapsed since last beat
def timeout_expired():
    # timeout is one bar of silence (4 beats)
    timeout = round(4*(60000/bpm))
    now = utime.ticks_ms()
    return (utime.ticks_diff(now, last_beat) > timeout)

# main loop
while True:
    #print("Hello!")
    # try to set bpm
    bpm_set = False
    while not bpm_set:
        bpm_set = capture_bpm()
    #print("BPM: " + str(bpm))
    play_cue()
    phrase = capture_phrase()
    # print information over serial
    print(str(bpm) + " : " + str(phrase))
    play_phrase(phrase)
