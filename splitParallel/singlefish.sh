#!/bin/bash

echo "singlefish"
cd ../singlefish
#for i in {0..7}
i=0;
#do
    NAME="../splitParallel/$i.f32"
    SPIKES="../splitParallel/$i.spikes"
    SCALE="/home/exp/Rafael/Data/Steatogynes/20170905_B23Training/B22B23.scale"
    FILTER="/home/exp/Rafael/Data/Steatogynes/20170905_B23Training/B22B23.filter"
    SVM="/home/exp/Rafael/Data/Steatogynes/20170905_B23Training/B22B23.svmmodel"
    SINGLEFISH="../splitParallel/$i.singlefish"
    PROBS="../splitParallel/$i.prob"
    python2 singlefish --minwins=1 --minprob=0.99 --onlyabove=0.300 $NAME $SPIKES $SCALE $FILTER $SVM $SINGLEFISH $PROBS &
#done

wait
