import subprocess
import json
from ipaddress import ip_network, ip_address

command = [
    "tshark",
    "-r", "./1.pcap",
    "-T", "fields",
    "-e", "ip.src",
    "-e", "ip.dst",
    "-e", "frame.time_epoch",
    "udp",

]

def imprimir_comunicaciones(comunicaciones):
    n = 0
    for i in comunicaciones:
        print('Comunicación ', n)
        print('     IP origen -> ', i["ip_origen"])
        print('     Subred origen -> ', i["subred_origen"])
        print('     IP destino -> ', i["ip_destino"])
        print('     Subred destino -> ', i["subred_destino"])
        print('     Nº veces -> ', i["veces"])
        print('     frecuencia -> ', i["frecuencia"])
        print('')
        n += 1

try:
    result = subprocess.run(command, capture_output=True, text=True, check=True)

    comunicaciones = []

    for i in result.stdout.strip().split('\n'):
        ip_src, ip_dst, timestamp = i.split()
        existe = False
        for comunicacion in comunicaciones:
            if comunicacion["ip_origen"] == ip_src and comunicacion["ip_destino"] == ip_dst:
                comunicacion["veces"] += 1
                existe = True
                comunicacion["ultima_comunicacion"] = timestamp
        if not existe:
            comunicaciones.append({
                "ip_origen": ip_src, 
                "ip_destino": ip_dst, 
                "veces": 0, 
                "primera_comunicacion": timestamp, 
                "ultima_comunicacion": timestamp, 
                "subred_origen": ip_network(f"{ip_src}/24", strict=False),
                "subred_destino": ip_network(f"{ip_dst}/24", strict=False)
            })

    # Calculamos cada cuanto tiempo se mandan mensajes en milisegundos
    for i in comunicaciones:
        frecuencia = (float(i["ultima_comunicacion"]) - float(i["primera_comunicacion"])) / float(i["veces"])
        i["frecuencia"] = frecuencia

    imprimir_comunicaciones(comunicaciones)


except subprocess.CalledProcessError as e:
    print("error")