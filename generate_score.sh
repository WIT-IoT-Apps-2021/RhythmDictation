#!/bin/bash
# generate score
lilypond --png -o page rhythm.ly

# crop with imagemagick
convert page.png -colorspace LinearGray -background white -alpha remove -alpha off \
	-trim -bordercolor white -border 10 score.png

# move to grafana path
mv score.png /srv/http/scores/score.png
