warmstart.py -t mb15 -n 0
wsfv.py -t mb15 -n 1
wsreinit.py -t mb15 -n 1
haFastload.py -t mb15
fenceHA.py -t mb15 -c cpssfc003
fenceHA.py -t mb15 -c cpssfc033
fenceDA.py -t mb15 -c iss012
qrvraDA15.py -t mb15 -c vra026
fencevraDA15.py -t mb15 -c vra037
fofb.py -t mb15 -n 0
qrcec.py -t mb15 -n 1
dscliEssni.py -t mb15
