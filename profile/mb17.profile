warmstart.py -t mb17 -n 0
wsfv.py -t mb17 -n 1
wsreinit.py -t mb17 -n 1
haFastload.py -t mb17
fenceHA.py -t mb17 -c cpssfc003
fenceHA.py -t mb17 -c cpssfc053
fenceDA.py -t mb17 -c iss012
fenceDA.py -t mb17 -c iss005
fofb.py -t mb17 -n 0
qrcec.py -t mb17 -n 1
dscliEssni.py -t mb17
