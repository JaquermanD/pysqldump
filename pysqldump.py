import re
import os
import zipfile
import argparse

def dividir_sql_con_create_table(dump_file, nombre_tabla, instrucciones_por_archivo):
    """
    Divide un archivo SQL en partes con un número específico de instrucciones INSERT INTO,
    guarda el CREATE TABLE en un archivo separado y comprime los archivos resultantes.
    """
    with open(dump_file, "r", encoding="utf-8") as archivo:
        contenido = archivo.read()
    
    # Extraer el CREATE TABLE
    create_table = re.search(rf"CREATE TABLE `{nombre_tabla}`.*?;\n", contenido, re.DOTALL)
    if not create_table:
        raise ValueError(f"No se encontró el CREATE TABLE para la tabla {nombre_tabla}.")
    
    # Crear directorio para los archivos generados
    directorio = f"{nombre_tabla}_seccionado"
    os.makedirs(directorio, exist_ok=True)
    
    # Guardar el CREATE TABLE y comprimirlo
    archivo_create = os.path.join(directorio, f"{nombre_tabla}_create_table.sql")
    with open(archivo_create, "w", encoding="utf-8") as archivo:
        archivo.write(create_table.group())
    comprimir_archivo(archivo_create)
    print(f"Archivo creado y comprimido: {archivo_create}.zip")
    
    # Extraer todas las instrucciones INSERT INTO
    inserts = re.findall(rf"INSERT INTO `{nombre_tabla}`.*?;\n", contenido, re.DOTALL)
    if not inserts:
        raise ValueError(f"No se encontraron instrucciones INSERT INTO para la tabla {nombre_tabla}.")
    
    # Dividir y comprimir las instrucciones INSERT INTO
    for i in range(0, len(inserts), instrucciones_por_archivo):
        lote_inserts = inserts[i:i + instrucciones_por_archivo]
        archivo_salida = os.path.join(directorio, f"{nombre_tabla}_parte_{i // instrucciones_por_archivo + 1}.sql")
        
        with open(archivo_salida, "w", encoding="utf-8") as archivo:
            archivo.write("\n".join(lote_inserts))
        
        comprimir_archivo(archivo_salida)
        print(f"Archivo creado y comprimido: {archivo_salida}.zip")

def comprimir_archivo(ruta_archivo):
    """
    Comprime un archivo en formato ZIP.
    """
    ruta_zip = f"{ruta_archivo}.zip"
    with zipfile.ZipFile(ruta_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(ruta_archivo, os.path.basename(ruta_archivo))
    os.remove(ruta_archivo)  # Elimina el archivo original para ahorrar espacio

def main():
    # Configuración de argumentos de línea de comandos con ayuda personalizada
    parser = argparse.ArgumentParser(
        description="Script para dividir un archivo SQL en partes y comprimirlas.",
        epilog="Ejemplo de uso:\n"
               "  python pysqldump.py --dump tabla.sql --table mi_tabla --inserts 30\n\n"
               "Esto dividirá el archivo 'tabla.sql' en partes de 30 instrucciones INSERT INTO, "
               "y cada parte será comprimida en un archivo ZIP.\n\n"
               "Creado por Jaquerman para Cindy ita con amor\n\n"
               "Usenlo libremente <3",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument("--dump", required=True, help="Ruta al archivo SQL (e.g., tabla.sql).")
    parser.add_argument("--table", required=True, help="Nombre de la tabla a procesar (e.g., mi_tabla).")
    parser.add_argument("--inserts", type=int, required=True, help="Número de instrucciones INSERT INTO por archivo.")
    args = parser.parse_args()

    try:
        dividir_sql_con_create_table(args.dump, args.table, args.inserts)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {args.dump}.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
