#!/bin/bash

cd ../recog

echo "recog 1"
#for i in {0..7}
i=0
#do
    DB="/ramdisk/$i.db"
    HILB="../splitParallel/$i.hilb"
    SPIKES="../splitParallel/$i.spikes"
    SINGLEFISH="../splitParallel/$i.singlefish"
    PROBS="../splitParallel/$i.prob"
    TS="/ramdisk/$i.timestamps"
    ./recog iterate --direction=1 $DB $HILB $SPIKES $SINGLEFISH $PROBS $TS &
#done

wait

echo "recog -1"
#for i in {0..7}
#do
    DB="/ramdisk/$i.db"
    HILB="../splitParallel/$i.hilb"
    SPIKES="../splitParallel/$i.spikes"
    SINGLEFISH="../splitParallel/$i.singlefish"
    PROBS="../splitParallel/$i.prob"
    TS="/ramdisk/$i.timestamps"
    ./recog iterate --direction=-1 $DB $HILB $SPIKES $SINGLEFISH $PROBS $TS &
#done

wait
