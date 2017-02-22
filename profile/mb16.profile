warmstart.py -t mb16 -n 0
wsfv.py -t mb16 -n 1
wsreinit.py -t mb16 -n 1
haFastload.py -t mb16
fenceHA.py -t mb16 -c cpssfc030
fenceDA.py -t mb16 -c iss022
qrcec.py -t mb16 -n 1
qrvraDA.py -t mb16 -c vra017
fencevraDA.py -t mb16 -c vra026
fofb.py -t mb16 -n 0
dscliEssni.py -t mb16
