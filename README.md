# 📈 DASHBOARD INTERACTIVO DEL COMPORTAMIENTO ACCIONARIO EN EL S&P 500 (ETL)

Un proyecto de **Extracción, Transformación y Carga (ETL)** para centralizar, procesar y visualizar el desempeño accionario del índice S&P 500, utilizando Python, Pandas, la GitHub API (o Dropbox API), y Power BI.

---

## 👥 Equipo de Proyecto

* **Ferney David Antolinez Tobo**
* **Erica Rocio Márquez Meneses**
* **John Mario Carmona David**
* **Sergio Duvan Mendoza Rojas**

---

## 💡 Contexto y Objetivo del Proyecto

El mercado accionario constituye uno de los pilares fundamentales del sistema financiero global. Los índices bursátiles, como el **S&P 500**, funcionan como un termómetro de la economía estadounidense y mundial, reflejando la evolución de las 500 compañías más representativas.

Este proyecto desarrolla un proceso **ETL** que centraliza información de **Wikipedia** (composición del índice) y **Yahoo Finance** (precios históricos diarios). El objetivo es construir un **dashboard interactivo en Power BI** que permita analizar de manera visual y dinámica el desempeño accionario, incluyendo métricas como el **Retorno Acumulado (YTD)** y la variación porcentual.

El proyecto tiene un enfoque **metodológico** y **analítico**, buscando fomentar el uso de analítica avanzada para la toma de decisiones basada en datos (*data-driven decisions*).

---

## 📊 Conjunto de Datos

El conjunto de datos procesado incluye más de 500 tickers, con series históricas diarias de precios comprendidas entre **enero de 2020 y octubre de 2025** (un rango de 5 años), totalizando aproximadamente **715.294 registros**.

* **Wikipedia:** Fuente de la lista oficial y actualizada de compañías.
* **Yahoo Finance:** Fuente para precios ajustados (**"Adjusted Close"**), esenciales para calcular retornos precisos.

**Nota sobre la Composición:** Aunque el índice se refiere a 500 empresas, el conjunto de datos incluye **503 tickers**. Esto se debe a que algunas compañías (ej., Alphabet Inc.) poseen más de una clase de acción cotizada.

### Fuentes Principales

| Fuente | Tipo | Descripción | Formato |
| :--- | :--- | :--- | :--- |
| **Wikipedia** | Web Scraping | Lista oficial de empresas del S&P 500 con símbolo bursátil, nombre y sector (GICS). | HTML |
| **Yahoo Finance** (yfinance API) | API no oficial | Precios históricos diarios (últimos 5 años) de cada acción del índice. | JSON → DataFrame Pandas |

### Variables Finales

| Tabla 1: `sp500_Empresas.csv` | Descripción |
| :--- | :--- |
| **Simbolo** | Ticker bursátil de la acción (AAPL, MSFT, etc.) |
| **Nombre** | Nombre de la empresa |
| **Sector** | Sector económico (GICS Sector) |

| Tabla 2: `sp500_ytd_Empresa.csv` | Descripción |
| :--- | :--- |
| **Year** | Año |
| **Simbolo** | Identificador bursátil |
| **YTD Return %** | Retorno acumulado en el año en curso |

| Tabla 3: `sp500_ytd_Sector.csv` | Descripción |
| :--- | :--- |
| **Year** | Año |
| **Sector** | Categoría económica |
| **YTD Return %** | Promedio de rentabilidad del sector |

| Tabla 4: `sp500_Precio_Accion.csv` | Descripción |
| :--- | :--- |
| **Fecha** | Día de cotización |
| **Simbolo (Ticker)** | Código único que identifica a cada acción. |
| **Adj Close** | Precio de cierre ajustado diario |
| **Precio_Final** | Precio de cierre final considerado para el cálculo de retornos acumulados |

---

## ⚙️ Proceso ETL

El script implementa el siguiente flujo completo:

### Extracción (Extract)

* Web scraping de **Wikipedia** para composición.
* Descarga de precios históricos y actuales usando la API de **`yfinance`**.
* Lectura de la base de datos histórica (almacenada en Dropbox) para verificar si existen nuevas compañías y complementar la información.

### Transformación (Transform)

* **Limpieza y Estandarización:** Se renombran columnas, se ajustan los símbolos bursátiles (`.` $\rightarrow$ `-`), se ajusta el formato de fechas y se eliminan duplicados.
* **Cálculo de Métricas:** Se calcula el **YTD Return** por empresa y por sector, consolidando las distintas fuentes en un formato coherente.

### Carga (Load)

* **Almacenamiento:** Los datos transformados se guardan de forma centralizada en **Dropbox** utilizando la librería oficial de Python y un **token de autenticación** para seguridad.
* **Visualización:** Los archivos CSV en Dropbox son consumidos directamente por **Power BI** a través de sus URLs públicas, permitiendo una visualización diaria y actualizada.

> 📝 **Automatización:** El flujo es orquestado mediante el **Administrador de tareas de Windows**, que ejecuta el script ETL periódicamente.

---

## 📈 Resultados Principales

1.  **Automatización Exitosa del Proceso ETL:** Integración reproducible de datos desde fuentes abiertas, garantizando la vigencia del análisis.
2.  **Dashboard Interactivo en Power BI:** El tablero facilita el análisis por empresa, sector y año con métricas clave (*YTD Return*, variación porcentual).
3.  **Gestión de Calidad de Datos:** Tratamiento adecuado de valores faltantes, duplicados y formatos incompatibles, asegurando la integridad del conjunto de datos.
4.  **Análisis Sectorial Agregado:** Identificación de patrones de comportamiento colectivo para apoyar estrategias de inversión diversificada.

---

## 🔗 Enlaces y Acceso

### Repositorio de Datos (Dropbox)
El código fuente y los datos finales procesados se encuentran en:
[**Acceder al Repositorio de Trabajo (Dropbox)**](https://www.dropbox.com/scl/fo/3dajlwga2dvucsm0kkd29/AMG_jIkWyRF44Uh7X7wV3hU?rlkey=n1jay3rvl888qgxvgeldvhiup&st=kdduwrqd&dl=0)

### Visor del Dashboard (Power BI)
**⚠️ NOTA:** Para acceder al visor es importante que se debe usar una **cuenta de la UAO**.
[**Ver Dashboard Interactivo (Power BI)**](https://app.powerbi.com/groups/me/reports/9703bcf9-e91d-4c17-836a-b67ba2c1185d/e839eb8716db7e281367?ctid=693cbea0-4ef9-4254-8977-76e05cb5f556&experience=power-bi)
