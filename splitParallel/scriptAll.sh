#!/bin/bash

#python split.py /home/exp/Rafael/Data/Steatogynes/20170906-07-B22B23/20170906-191404_rchan_filt.f32
./spikes.sh
./singlefish.sh
./recog.sh
cp -r /ramdisk/* .
python merge.py /home/exp/Rafael/Data/Steatogynes/20170906-07-B22B23/20170906-191404_rchan_filt.f32
