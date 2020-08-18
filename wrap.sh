#!/bin/bash
#$-cwd
#$-M minke.zhang@gmail.com
#$-m n
#$-S /bin/bash
#$-l h_data=4096M,h_rt=120:00:00
./hash.py -m "sim" -c "confs/default.conf"
