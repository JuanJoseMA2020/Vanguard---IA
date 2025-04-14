from newspaper import Article
import subprocess
import time
import csv
import shutil

if shutil.which("ollama") is None:
    print("Ollama no está instalado o no está en el PATH.")
    exit()

def extraer_contenido(url):
    try:
        article = Article(url, language='es')
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"Error al extraer contenido de {url}: {e}")
        return ""

def resumir_con_ollama(texto, modelo="llama2"):
    prompt = f"Resume en 4 líneas el siguiente texto de una noticia del sector energético:\n\n{texto}\n\nResumen:"
    print(f"Prompt sent to Ollama:\n{prompt}")  # Debugging output
    try:
        resultado = subprocess.run(
            ["ollama", "run", modelo],
            input=prompt,
            capture_output=True,
            text=True
        )
        print(f"Ollama stdout:\n{resultado.stdout}")  # Debugging output
        print(f"Ollama stderr:\n{resultado.stderr}")  # Debugging output
        return resultado.stdout.strip()
    except subprocess.TimeoutExpired:
        print(f"Tiempo de espera agotado al resumir con {modelo}.")
        return "Resumen no disponible (timeout)."
    except FileNotFoundError:
        print("Error: El comando 'ollama' no se encontró. Asegúrate de que Ollama esté instalado y en el PATH.")
        exit()
    except Exception as e:
        print(f"Error al resumir con Ollama ({modelo}): {e}")
        return "Resumen no disponible."

def guardar_noticias_con_resumen(archivo_entrada="noticias_portafolio.csv", archivo_salida="noticias_portafolio_resumen_llama2.csv", modelo="llama2"):
    try:
        with open(archivo_entrada, mode="r", encoding="utf-8") as infile, \
             open(archivo_salida, mode="w", encoding="utf-8", newline="") as outfile:
            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=["titulo", "url", "resumen"])
            writer.writeheader()

            for row in reader:
                titulo = row["titulo"]
                url = row["url"]
                print(f"Procesando y resumiendo: {titulo}")
                contenido = extraer_contenido(url)
                if len(contenido) < 200:
                    print("Contenido muy corto, saltando.")
                    writer.writerow({"titulo": titulo, "url": url, "resumen": "Contenido muy corto para resumir."})
                    continue
                resumen = resumir_con_ollama(contenido, modelo=modelo)
                writer.writerow({"titulo": titulo, "url": url, "resumen": resumen})
                time.sleep(3)  # Para evitar bloqueos
        print(f"Resúmenes guardados en {archivo_salida}")
    except FileNotFoundError:
        print(f"Error: El archivo de entrada '{archivo_entrada}' no fue encontrado.")
    except Exception as e:
        print(f"Ocurrió un error durante el procesamiento: {e}")

if __name__ == "__main__":
    guardar_noticias_con_resumen(modelo="llama2")  # o "gemma"