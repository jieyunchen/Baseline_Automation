warmstart.py -t mb12 -n 0
wsfv.py -t mb12 -n 1
wsreinit.py -t mb12 -n 1
haFastload.py -t mb12
fenceHA.py -t mb12 -c cpssfc010
fenceDA.py -t mb12 -c iss002
qrcec.py -t mb12 -n 1
qrvraDA.py -t mb12 -c vra026
fencevraDA.py -t mb12 -c vra037
fofb.py -t mb12 -n 0
dscliEssni.py -t mb12
