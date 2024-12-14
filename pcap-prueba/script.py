import subprocess
import sys
def representar_diccionario(diccionario):
    resultado = []
    for clave, valor in diccionario.items():
        resultado.append(f"{clave}: {valor}")
    return "\n".join(resultado)


def Conexiones(ruta):
    command = ["tshark", "-r", ruta, "-T", "fields", "-e", "ip.src", "-e", "ip.dst"]
    ips = subprocess.run(command,capture_output=True,text=True)    
    
    ips = ips.stdout.split("\n")
    All_ips = set()
    for i in ips:
        if(len(i) > 2):
            i = i.split("\t")
            All_ips.add(i[0])
    print(All_ips)
    conexiones = dict()
    for i in All_ips:
        conexiones.setdefault(i,set())

    for i in ips:
        if len(i) > 2:
            i = i.split("\t")
            conexiones[i[0]].add(i[1])

    print(representar_diccionario(conexiones))

if __name__ == "__main__":
    if(len(sys.argv) == 0):
        print("Falta el primer argumento")
    else:
        ruta = sys.argv[1]
        print("ruta: ",ruta)
        Conexiones(ruta)
