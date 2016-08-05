#!/bin/bash

for i in `seq $1`; do
    echo $i
    sed "s/pv000/pv00$i/g" pv.yaml > pv/pv0$i.yaml
done
