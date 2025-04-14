import requests
from bs4 import BeautifulSoup
import csv
import time

def obtener_noticias_portafolio(url="https://www.portafolio.co/"):
    """
    Obtiene los títulos y enlaces de las noticias de la sección de energía de Portafolio.

    Returns:
        list: Una lista de diccionarios, donde cada diccionario contiene el 'titulo' y la 'url' de una noticia.
              Retorna una lista vacía en caso de error al acceder al sitio web o si no se encuentran artículos.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP erróneos (4xx o 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error al acceder al sitio web: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    articulos = soup.find_all("article")

    noticias = []

    for articulo in articulos:
        enlace_tag = articulo.find("a")
        if enlace_tag:
            titulo = enlace_tag.get_text(strip=True)
            enlace = enlace_tag.get("href")
            if enlace and not enlace.startswith("http"):
                enlace = url + enlace
            noticias.append({
                "titulo": titulo,
                "url": enlace
            })

    return noticias

def guardar_noticias(noticias, archivo="noticias_portafolio.csv"):
    """
    Guarda los títulos y URLs de las noticias en un archivo CSV.

    Args:
        noticias (list): Una lista de diccionarios, donde cada diccionario contiene 'titulo' y 'url'.
        archivo (str, optional): El nombre del archivo CSV para guardar las noticias.
                                 Defaults to "noticias_portafolio.csv".
    """
    with open(archivo, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["titulo", "url"])
        writer.writeheader()
        writer.writerows(noticias)
    print(f"Noticias guardadas en {archivo}")

if __name__ == "__main__":
    noticias = obtener_noticias_portafolio()
    if noticias:
        guardar_noticias(noticias)
    else:
        print("No se encontraron noticias para guardar.")