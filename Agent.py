import os
import pandas as pd
from datetime import datetime
from openai import AzureOpenAI
import re
from io import StringIO
import random

# --- CONFIGURACIÓN AZURE ---
endpoint = "https://openai-2025pp.openai.azure.com/"
deployment = "o3-mini"
subscription_key = "AZpZ6chFFbcaxVd2dNiCkP4q9gkzKbsVCg1hvZTr3orULhamJWumJQQJ99BDACHYHv6XJ3w3AAABACOGbwAg"
api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

# --- FIRMAS BENITO ---
firmas_benito = [
    "Quedo atento a cualquier ajuste que quieras hacer. — Benito 👨‍💼",
    "Listo para lo que necesites. Seguimos avanzando. — Benito 👨‍💼",
    "Aquí tienes el análisis claro y al punto. Me cuentas si algo más se requiere. — Benito 👨‍💼",
    "Gracias por confiar en mí para este análisis. Seguimos en equipo. — Benito 👨‍💼"
]

# --- FUNCIONES ---
def cargar_datos(path_excel):
    df = pd.read_excel(path_excel)
    df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)
    df['Fecha de término planeada'] = pd.to_datetime(df['Fecha de término planeada'], errors='coerce')
    df = df.dropna(subset=['Fecha de término planeada', 'Entidad propietaria'])
    return df

def preparar_contexto(df):
    df_ctx = df[['Nombre Local', 'Entidad propietaria', 'Fecha de término planeada', 'Estatus Actual del Flujo de Trabajo']].copy()
    df_ctx.rename(columns={
        'Nombre Local': 'Nombre Acción',
        'Entidad propietaria': 'Dueño',
        'Fecha de término planeada': 'Fecha Compromiso',
        'Estatus Actual del Flujo de Trabajo': 'Estado'
    }, inplace=True)
    df_ctx['Fecha Compromiso'] = df_ctx['Fecha Compromiso'].dt.strftime('%Y-%m-%d')
    return df_ctx.to_string(index=False)

def analizar_con_ia(contexto_str):
    hoy = datetime.today().strftime('%Y-%m-%d')
    firma = random.choice(firmas_benito)
    messages = [
        {
            "role": "system",
            "content": (
                "Hola, soy Benito. Formo parte del equipo de Estrategia y Gestión de Riesgos en ISAGEN. "
                "Me encargo de revisar, cada trimestre, las acciones de mejora para asegurar que estemos avanzando según lo planeado. "
                "Analizo los compromisos vigentes, identifico riesgos por vencimientos y mantengo todo bien organizado para que la toma de decisiones sea clara y oportuna. "
                "Puedes contar conmigo como un compañero atento, proactivo y siempre listo para aportar al equipo."
            )
        },
        {
            "role": "user",
            "content": f"""Aquí están las acciones:

{contexto_str}

Hoy es {hoy}.
Identifica:
1. Acciones VENCIDAS (fecha compromiso < hoy)
2. Acciones PRÓXIMAS A VENCER (fecha compromiso entre el Q de hoy y el proximo Q que comprende cada 3 meses. 
   Encárgate de analizar bien en cuál Q estamos y cuál Q viene teniendo como referencia el hoy. Un "Q" es un cuatrimestre:
   Q1 = Enero, Febrero, Marzo;
   Q2 = Abril, Mayo, Junio;
   Q3 = Julio, Agosto, Septiembre;
   Q4 = Octubre, Noviembre, Diciembre.
3. Solo necesito los que tienen Estado: En progreso y lo entregues ordenado ascendente por Q
4. Agrega una nueva columna que me diga a cuál "Q" pertenece cada acción.
5. Para la presentación de la información, QUITA la palabra "SIMULACRO" de cada acción y deja el resto del nombre.
6. Garantiza que la primera letra de cada acción sea en mayúscula
7. Analiza las fechas, lo relevante es del año en curso. Si detectas de años anteriores haz una alerta y tambien las resaltas

Para cada grupo, muestra: Nombre Acción, Dueño, Fecha Compromiso, Estado y Q.
Preséntalo como dos tablas Markdown (una para VENCIDAS y otra para PRÓXIMAS).
Al final, agrega una breve firma amable como: {firma}
"""
        }
    ]

    response = client.chat.completions.create(
        model=deployment,
        messages=messages,
        max_completion_tokens=100000
    )
    return response.choices[0].message.content

def extraer_tablas(respuesta):
    print("\n🔍 Extrayendo tablas de la respuesta del modelo...")

    bloques = re.findall(r'((?:\|.+\|\n)+)', respuesta)
    print(f"✅ Se encontraron {len(bloques)} posibles tablas.")

    dfs = []

    for i, bloque in enumerate(bloques):
        try:
            lineas = bloque.strip().split("\n")
            if len(lineas) < 2:
                continue

            tabla_sin_guiones = "\n".join([lineas[0]] + [l for l in lineas[1:] if not re.match(r'^\|[-\s|]+$', l)])
            df = pd.read_csv(StringIO(tabla_sin_guiones), sep="|", engine="python", skipinitialspace=True)
            df = df.dropna(axis=1, how='all')
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            df.columns = df.columns.str.strip()
            dfs.append(df)
        except Exception as e:
            print(f"⚠️ No se pudo procesar la tabla {i+1}. Error: {e}")

    return dfs

def guardar_excel(vencidas, proximas, salida="acciones_analizadas.xlsx"):
    with pd.ExcelWriter(salida, engine='openpyxl') as writer:
        vencidas.to_excel(writer, index=False, sheet_name='Vencidas')
        proximas.to_excel(writer, index=False, sheet_name='Proximas')
    print(f"\n✅ Archivo generado: {salida}")

# --- EJECUCIÓN ---
if __name__ == "__main__":
    archivo = "Simulacros.xlsx"

    df = cargar_datos(archivo)
    contexto = preparar_contexto(df)
    respuesta = analizar_con_ia(contexto)

    print("\n--- ANÁLISIS DE BENITO ---\n")
    print(respuesta)

    tablas = extraer_tablas(respuesta)

    if len(tablas) >= 2:
        vencidas_df, proximas_df = tablas[:2]
        guardar_excel(vencidas_df, proximas_df)
    else:
        print("\n⚠️ No se encontraron al menos dos tablas válidas en la respuesta.")
        for i, df in enumerate(tablas):
            print(f"\nTabla {i+1} (mostrando las primeras filas):")
            print(df.head())
