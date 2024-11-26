import subprocess
import json

command = [
    "tshark",
    "-r", "/home/lamux/Documentos/Repositorios/proyecto-alumno-colaborador/pcap-prueba/1.pcap",
    "-T", "fields",
    "-e", "ip.src",
    "-e", "ip.dst",
    "-e", "frame.time_epoch",
    "udp",

]

try:
    result = subprocess.run(command, capture_output=True, text=True, check=True)

    packets = []
    comunicaciones = []

    for i in result.stdout.strip().split('\n'):
        ip_src, ip_dst, timestamp = i.split()
        existe = False
        for comunicacion in comunicaciones:
            if comunicacion["ip_src"] == ip_src and comunicacion["ip_dst"] == ip_dst:
                comunicacion["veces"] += 1
                existe = True
                comunicacion["ultima_comunicacion"] = timestamp
        if not existe:
            comunicaciones.append({"ip_src": ip_src, "ip_dst": ip_dst, "veces": 0, "primera_comunicacion": timestamp, "ultima_comunicacion": timestamp})
        packet_info = {
            "ip_src": ip_src,
            "ip_dst": ip_dst,
            "timestamp": timestamp
        }
        packets.append(packet_info)

    # Calculamos cada cuanto tiempo se mandan mensajes en milisegundos
    for i in comunicaciones:
        frecuencia = (float(i["ultima_comunicacion"]) - float(i["primera_comunicacion"])) / float(i["veces"])
        i["frecuencia"] = frecuencia

    print(comunicaciones)


except subprocess.CalledProcessError as e:
    print("error")