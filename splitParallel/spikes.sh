#!/bin/bash

echo "spikes"
cd ../spikes
#for i in {0..7}
i=0
#do
    NAME="../splitParallel/$i.f32"
    HILB="../splitParallel/$i.hilb"
    OUT="../splitParallel/$i.spikes"
    ./spikes --numtaps=20001 $NAME $HILB $OUT 
#done

