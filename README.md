# 🧠 Generador de Análisis del Sector Energético Colombiano

Este proyecto automatiza la generación de un análisis estratégico del sector energético colombiano a partir de resúmenes de noticias. Utiliza un modelo local de lenguaje (`mistral` vía Ollama), genera un informe en formato Word y lo envía automáticamente por correo electrónico.

---

## 🚀 ¿Qué hace este proyecto?

1. Lee un archivo `.csv` con resúmenes de noticias.
2. Genera un análisis estratégico usando un modelo de lenguaje local (como `mistral` vía Ollama).
3. Crea un documento `.docx` con el análisis generado.
4. Envía el documento por correo electrónico al destinatario que elijas.

---

## 🧰 Requisitos

- Python 3.10 o superior
- [Ollama](https://ollama.com/) instalado y corriendo
- Modelo `mistral` descargado con Ollama (`ollama pull mistral`)
- Cuenta Gmail habilitada con contraseña de aplicación

### 📦 Librerías necesarias

Instala las dependencias necesarias con:

```bash
pip install python-docx
