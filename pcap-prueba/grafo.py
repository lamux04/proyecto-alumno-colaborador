############ PARA EJECUTAR: python3 grafo.py "ruta/relativa/a/pcap"
############ Una vez ejecutado, el script creará un html con un grafo interactivo 
############ con las conexiones que se producen en la red.

from pyvis.network import Network
import networkx as nx
import matplotlib.pyplot as plt
import subprocess
from ipaddress import ip_network
import sys

# Configuración del comando tshark
TSHARK_COMMAND = [
    "tshark",
    "-r", sys.argv[1],
    "-T", "fields",
    "-e", "ip.src",
    "-e", "ip.dst",
    "-e", "frame.time_epoch",
    "udp",
]


def ejecutar_tshark(command):
    """
    Ejecuta el comando tshark y devuelve la salida como lista de líneas.
    """
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar tshark: {e}")
        return []


def procesar_comunicaciones(salida_tshark):
    """
    Procesa la salida de tshark y devuelve una lista de comunicaciones.
    """
    comunicaciones = []

    for linea in salida_tshark:
        if len(linea.split()) < 3:
            continue
        ip_origen, ip_destino, timestamp = linea.split()

        # Buscar si ya existe una comunicación
        existe = False
        for comunicacion in comunicaciones:
            if comunicacion["ip_origen"] == ip_origen and comunicacion["ip_destino"] == ip_destino:
                comunicacion["veces"] += 1
                comunicacion["ultima_comunicacion"] = float(timestamp)
                existe = True
                break

        # Si no existe, agregar una nueva
        if not existe:
            comunicaciones.append({
                "ip_origen": ip_origen,
                "subred_origen": str(ip_network(f"{ip_origen.split(',')[0]}/24", strict=False)),
                "ip_destino": ip_destino,
                "subred_destino": str(ip_network(f"{ip_destino.split(',')[0]}/24", strict=False)),
                "primera_comunicacion": float(timestamp),
                "ultima_comunicacion": float(timestamp),
                "veces": 1
            })

    # Calcular la frecuencia de comunicación
    for comunicacion in comunicaciones:
        tiempo_total = comunicacion["ultima_comunicacion"] - comunicacion["primera_comunicacion"]
        comunicacion["frecuencia"] = tiempo_total / comunicacion["veces"] if comunicacion["veces"] > 1 else 0.0

    return comunicaciones

def obtener_conexiones(comunicaciones):
    '''
    Procesa el array de comunicaciones y obtiene las diferentes conexiones
    '''
    conexiones = {}

    # Obtenemos las diferentes conexiones que se producen
    for com in comunicaciones:
        ip_origen = com["ip_origen"]
        if ip_origen in conexiones:
            conexiones[ip_origen].add(com["ip_destino"])
        else:
            conexiones[ip_origen] = set([com["ip_destino"]])

    return conexiones


def imprimir_comunicaciones(comunicaciones):
    """
    Imprime en consola las comunicaciones procesadas.
    """
    print("\nResumen de comunicaciones UDP:")
    for idx, comunicacion in enumerate(comunicaciones):
        print(f"Comunicación {idx + 1}:")
        print(f"  IP Origen: {comunicacion['ip_origen']}")
        print(f"  Subred Origen: {comunicacion['subred_origen']}")
        print(f"  IP Destino: {comunicacion['ip_destino']}")
        print(f"  Subred Destino: {comunicacion['subred_destino']}")
        print(f"  Veces: {comunicacion['veces']}")
        print(f"  Frecuencia: {comunicacion['frecuencia']:.2f} segundos")
        print("")

def imprimir_conexiones(conexiones):
    """
    Imprime en consola las conexiones que se realizan
    """
    print("\nConexiones que se realizan")
    for ip_origen in conexiones.keys():
        print(f"\nORIGEN {ip_origen}")
        for ip_destino in conexiones[ip_origen]:
            print(f"    - {ip_destino}")

def obtener_subred(ip, mascara="/24"):
    '''
    Calcula la subred de una IP dada.
    '''
    return str(ip_network(ip.split(',')[0] + mascara, strict=False))

def asignar_colores_por_subred(conexiones):
    '''
    Asigna un color a cada nodo en función de la subred a la que pertenece.
    Devuelve un diccionario con el nodo como clave y el color como valor.
    '''
    colores = {}
    colores_subred = {}
    subred_counter = 0
    lista_colores = [
        "skyblue", "lightgreen", "salmon", "yellow", "orange", "violet", "pink", "gold"
    ]

    # Iteramos sobre las conexiones y asignamos colores por subred
    for ip_origen in conexiones.keys():
        subred = obtener_subred(ip_origen)
        if subred not in colores_subred:
            colores_subred[subred] = lista_colores[subred_counter % len(lista_colores)]
            subred_counter += 1
        colores[ip_origen] = colores_subred[subred]

        for ip_destino in conexiones[ip_origen]:
            subred = obtener_subred(ip_destino)
            if subred not in colores_subred:
                colores_subred[subred] = lista_colores[subred_counter % len(lista_colores)]
                subred_counter += 1
            colores[ip_destino] = colores_subred[subred]

    return colores_subred

def grafo_interactivo(conexiones):
    net = Network(notebook=False, height="95vh", width="100%", bgcolor="white", font_color="black", directed=True)
    net.barnes_hut()  # Utiliza un algoritmo optimizado para grandes grafos
    
    # Asignamos colores a los nodos según la subred
    colores_subred = asignar_colores_por_subred(conexiones)

    dibujados = []

    # Agregar nodos y aristas
    for origen, destinos in conexiones.items():
        if origen not in dibujados:
            net.add_node(origen, label=origen, color=colores_subred[obtener_subred(origen)], size=150, font={'size': 20})
            dibujados.append(origen)
        for destino in destinos:
            if destino not in dibujados:
                net.add_node(destino, label=destino, color=colores_subred[obtener_subred(destino)], size=155, font={'size': 20})
                dibujados.append(destino)
            net.add_edge(origen, destino)

    # Genera y abre un archivo HTML interactivo
    net.show("grafo_interactivo.html", notebook=False)

def main():
    """
    Función principal para ejecutar y analizar las comunicaciones UDP.
    """
    salida_tshark = ejecutar_tshark(TSHARK_COMMAND)

    if not salida_tshark:
        print("No se pudo obtener la salida de tshark.")
        return

    comunicaciones = procesar_comunicaciones(salida_tshark)
    # imprimir_comunicaciones(comunicaciones)

    conexiones = obtener_conexiones(comunicaciones)
    # imprimir_conexiones(conexiones)
    grafo_interactivo(conexiones)

if __name__ == "__main__":
    main()
