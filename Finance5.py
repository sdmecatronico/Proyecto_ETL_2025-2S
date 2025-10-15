# -*- coding: utf-8 -*-
"""
Created on Tue Aug 26 21:43:11 2025

@author: FDAT
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
from datetime import datetime
import logging
import os
import io
from io import BytesIO, StringIO
import numpy as np
import dropbox
from dropbox.files import WriteMode
from dropbox import Dropbox, files, exceptions
import traceback

# =================================
# Configuracion de Token de Dropbox
# ==================================


APP_KEY = 'kj0vlpru0j0yrko'
APP_SECRET = 'fg7tcv4pqywp6ts'
REFRESH_TOKEN = 'ZgxpKkmKuEsAAAAAAAAAAYlOIw_QKoT4XPBcbfLg-qLn550CxgPEFw_WFEXIAjyt'

#conectarse a dropbox
dbx = dropbox.Dropbox(
    oauth2_refresh_token=REFRESH_TOKEN,
    app_key=APP_KEY,
    app_secret=APP_SECRET
)


# =================================
# Rutas de los archivos en dropbox
# =================================
dropbox_path_csv_empresas = "/sp500_Empresas.csv"
dropbox_path_csv_precio = "/sp500_Precio_Accion.csv"
dropbox_path_csv_ytd_empresa = "/sp500_ytd_Empresa.csv"
dropbox_path_csv_ytd_sector = "/sp500_ytd_Sector.csv"
dropbox_path_log = "/sp500_log.txt"


# =================================
# Configuración del logging
# =================================

# -----------------------------
# Loggin local
# -----------------------------
# Carpeta donde se guarda el log (carpeta del script)
log_file = os.path.join(os.getcwd(), "sp500_log.txt")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_file,
    filemode='w',   # sobrescribe cada ejecución
    force=True       # fuerza la configuración incluso si ya hay logging inicializado
)



# ========================
# Funciones Auxiliares de lectura y escritura de datos en Dropbox
# ========================
def upload_log_to_dropbox():
    """Sube el log local a Dropbox, sobrescribiendo si existe."""
    try:
        with open(log_file, "rb") as f:
            dbx.files_upload(f.read(), dropbox_path_log, mode=dropbox.files.WriteMode.overwrite)
        print("Log subido a Dropbox correctamente.")
    except Exception as e:
        print("Error subiendo log a Dropbox:", e)

def read_csv_dropbox(path):
    try:
        _, res = dbx.files_download(path)
        df = pd.read_csv(io.StringIO(res.content.decode('utf-8')))
        return df
    except dropbox.exceptions.ApiError as e:
        # Si el archivo no existe, retornamos df vacío
        if isinstance(e.error, dropbox.files.DownloadError) and e.error.is_path() and e.error.get_path().is_not_found():
            return pd.DataFrame()
        else:
            logging.error(f"Error leyendo {path} de Dropbox: {e}")
            raise

def save_csv_dropbox(df, path, mode='overwrite'):
    try:
        if mode == 'overwrite':
            dbx.files_upload(df.to_csv(index=False).encode('utf-8'), path, mode=dropbox.files.WriteMode.overwrite)
        elif mode == 'append':
            df_exist = read_csv_dropbox(path)
            df_concat = pd.concat([df_exist, df], ignore_index=True)
            dbx.files_upload(df_concat.to_csv(index=False).encode('utf-8'), path, mode=dropbox.files.WriteMode.overwrite)
    except Exception as e:
        logging.error(f"Error guardando {path} en Dropbox: {e}")
        raise




try:
    #========================
    # Leer datos de Wikipedia
    #=======================
    logging.info("=== Inicio del proceso de extracción de Empresas S&P 500 ===")
    
    

    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    
    #se agregan headers para evitar error 403.
    headers_req = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
                      'AppleWebKit/537.36 (KHTML, like Gecko) ' +
                      'Chrome/140.0.0.0 Safari/537.36'
    }
    
    # Descarga de la página
    logging.info("Descargando la página de Wikipedia...")
    try:
        response = requests.get(url, headers=headers_req)
        response.encoding = 'utf-8'
        logging.info("Página descargada correctamente.")
    except Exception as e:
        logging.error(f"Error al descargar la página: {e}")
        raise
    
    # Parseo HTML
    logging.info("Parseando el HTML con BeautifulSoup...")
    soup = BeautifulSoup(response.text, 'html.parser')
    logging.info("HTML parseado correctamente.")
    
    # Localizar tabla principal
    logging.info("Buscando la tabla principal de empresas...")
    #id de la tabla = 'constituents'
    sp500_table = soup.find('table', {'id':'constituents'})
    if sp500_table:
        logging.info("Tabla de empresas encontrada.")
    else:
        logging.error("No se encontró la tabla de empresas en la página.")
        raise ValueError("Tabla no encontrada")
    
    # Extraer encabezados de la tabla
    logging.info("Extrayendo encabezados de la tabla...")
    headers = [th.get_text(strip=True) for th in sp500_table.find('tr').find_all('th')]
    logging.info(f"Encabezados extraídos: {headers}")
    
    # Extraer filas
    logging.info("Extrayendo filas de la tabla...")
    rows_list = []
    #ciclo para extraer los datos de la tabla
    for i, row in enumerate(sp500_table.find_all('tr')[1:], start=1):
        cols = row.find_all('td')
        if cols:
            rows_list.append([td.get_text(strip=True) for td in cols])
            if i % 50 == 0:
                logging.info(f"{i} filas procesadas...")
    
    logging.info(f"Se extrajeron {len(rows_list)} filas.")
    
    # Crear DataFrame
    logging.info("Creando DataFrame con pandas...")
    df_sp500 = pd.DataFrame(rows_list, columns=headers)
    logging.info(f"DataFrame creado con {len(df_sp500)} empresas.")
    
    # Solo columnas requeridas
    df_sp500 = df_sp500.loc[:, ['Symbol','Security','GICSSector']]
    
    
    #cambiar nombre a las columnas
    df_sp500.columns = ['Simbolo','Nombre','Sector']
    #eliminar nan
    df_sp500=df_sp500.dropna(subset=['Simbolo'])
    # reemplazar . por - para evitar luego problemas al usar y yf.download
    df_sp500['Simbolo'] = df_sp500['Simbolo'].str.replace(".", "-", regex=False)
    
    logging.info("Columnas seleccionadas y renombradas.")
    
    
    
    #============================================
    #Comparar CSV con la bd y los datos traidos por scrapping y actualiza si es necesario
    #============================================
    #leer CSV con los nombres de las empresas
    logging.info("Leyendo DB CSV de nombres...")
    df_sp500_nombreDB = read_csv_dropbox(dropbox_path_csv_empresas)
    
    # Filtrar filas de df2 que NO están en df1 según esa columna
    nuevas_filas = df_sp500[~df_sp500['Simbolo'].isin(df_sp500_nombreDB['Simbolo'])]
    
    # Si hay filas nuevas, agregar al CSV
    if not nuevas_filas.empty:
        # Agregar al CSV existente
        try:
            #agrear filas con las empresas que faltan cargar
            save_csv_dropbox(nuevas_filas, dropbox_path_csv_empresas, mode='append')
            # Nombres agregados
            nombres_agregados = nuevas_filas['Nombre'].tolist()
            logging.info(f"Se agregaron {len(nuevas_filas)} nuevas filas al CSV: {nombres_agregados}")
        except Exception as e:
            logging.error(f"Error al actualizar archivo CSV con nombre de las empresas del S&P500: {e}")
            raise   
            
    else:
        logging.info("No hay datos de nuevas empresas en el S%P500. El CSV no se modificó.")
    
    
    #========================
    # Leer datos de Yahoo Finance
    #=======================
    #tomar simbolo de las empresas
    tickers = df_sp500['Simbolo'].tolist()
    
    #correr desde el principio del año
    inicio_year = datetime(datetime.now().year, 1, 1)
    
    
    logging.info("Descargando precios desde Yahoo Finance...")
    try:
        dfprecios = yf.download(
            tickers,
            start=inicio_year.strftime("%Y-%m-%d"),
            group_by="ticker"
        )
        logging.info("Precios descargados correctamente.")
    except Exception as e:
        logging.error(f"Error al descargar precios: {e}")
        raise
    
    
    #==================================
    # Transformar tabla precios (aplanarla porque viene en multiindex)
    #=============================
    
    # Si las columnas tienen MultiIndex (varios tickers)
    if isinstance(dfprecios.columns, pd.MultiIndex):
        # 'stack' transforma el nivel de ticker en una columna
        dfprecios = dfprecios.stack(level=0).reset_index()
    
        # Los nombres reales de las columnas vienen del segundo nivel del MultiIndex
        # Tomamos ese orden exacto del DataFrame original
        columnas_nivel_1 = dfprecios.columns[2:].tolist()  # todas las columnas de datos 
        dfprecios.columns = ['Fecha', 'Simbolo'] + columnas_nivel_1
    
    else:
        # Si solo hay un ticker
        dfprecios = dfprecios.reset_index()
        dfprecios['Simbolo'] = tickers[0]
    
    # Si no existe la columna 'Adj Close', crearla llena de NaN
    if 'Adj Close' not in dfprecios.columns:
        dfprecios['Adj Close'] = np.nan
        
    #Agregar columna con precio final (adj close o close segun el caso)
    dfprecios["Precio_Final"] = dfprecios["Adj Close"].fillna(dfprecios["Close"])
    #confirmar valores a numero y redondear
    for col in ["Open", "High", "Low", "Precio_Final"]:
        dfprecios[col] = pd.to_numeric(dfprecios[col], errors='coerce').round(4)
    
    logging.info("Precios normalizados")
    
    #actualizar precios con la fecha actual
    #tomar fecha actual
    diaact = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    #diaact=datetime(datetime.now().year, 10, 13)
    
    
    #tomar solo los precios del dia actual
    dfprecios_act=dfprecios[dfprecios['Fecha']==diaact]
    
    if len(dfprecios_act)>0:
        
        try:
            #convertir fecha a guiones
            dfprecios_act["Fecha"] = pd.to_datetime(dfprecios_act["Fecha"]).dt.strftime("%m/%d/%Y")
            #llevar valores al df
            save_csv_dropbox(dfprecios_act, dropbox_path_csv_precio, mode='append')
            logging.info("Se agregan precios del dia actual a la BD")
            
            
            # ===============================
            # Calcular YTD Return
            # ===============================
            logging.info("Calculando YTD Return de cada acción...")
            #ordenar por fecha
            dfprecios = dfprecios.sort_values(["Simbolo", "Fecha"])
            ytd_returns = dfprecios.groupby("Simbolo")["Precio_Final"].apply(
                lambda x: (x.iloc[-1] / x.iloc[0] - 1) * 100)
        
            #pasar a df
            df_ytd = pd.DataFrame({'Simbolo': ytd_returns.index, "YTD Return %": ytd_returns.values})
            #insertar columna año
            yea = pd.to_datetime(dfprecios["Fecha"].iloc[0]).year
            df_ytd.insert(0,'Year',yea)
            #confirmar valores de YTD return a numero y redondear
            df_ytd["YTD Return %"]=pd.to_numeric(df_ytd["YTD Return %"], errors='coerce').round(2)
            logging.info("YTD Return calculado para cada empresa")
            
            #leer sp500_ytd_Empresa.csv para confirmar datos a actualizar
            df_ytd_BD = read_csv_dropbox(dropbox_path_csv_ytd_empresa)
            # Unir y reemplazar registros existentes manteniendo los ultimos
            df_ytd_actualizar = pd.concat([df_ytd_BD, df_ytd], ignore_index=True)
            df_ytd_actualizar= df_ytd_actualizar.drop_duplicates(subset=["Year", "Simbolo"], keep="last")
            # Sobrescribir el CSV (reemplazando el contenido anterior)
            save_csv_dropbox(df_ytd_actualizar, dropbox_path_csv_ytd_empresa, mode='overwrite')
            logging.info("Se actualiza YTD Return por empresa a la BD")
        
        
            #unir tablas para tener el sector 
            df_union = df_sp500.merge(df_ytd, on='Simbolo', how="inner")
        
            #calcuar YTD Return por sector
            df_sector = df_union .groupby('Sector')["YTD Return %"].mean().reset_index()
            #insertar columna año
            df_sector.insert(0,'Year',yea)
            #confirmar valores de YTD return a numero y redondear
            df_sector["YTD Return %"]=pd.to_numeric(df_sector["YTD Return %"], errors='coerce').round(2)
            logging.info("YTD Return calculado por sector")
            
            
            #leer sp500_ytd_Sector.csv para confirmar datos a actualizar
            df_sector_BD = read_csv_dropbox(dropbox_path_csv_ytd_sector)
            # Unir y reemplazar registros existentes manteniendo los ultimos
            df_sector_actualizar = pd.concat([df_sector_BD, df_sector], ignore_index=True)
            df_sector_actualizar= df_sector_actualizar.drop_duplicates(subset=["Year", "Sector"], keep="last")
            # Sobrescribir el CSV (reemplazando el contenido anterior)
            save_csv_dropbox(df_sector_actualizar, dropbox_path_csv_ytd_sector, mode='overwrite')
            logging.info("Se actualiza YTD Return por sector a la BD")
            
            
            
        except Exception as e:
            logging.error(f"Error al guardar archivos CSV: {e}")
            raise
        
    else:
        logging.info("No hay datos nuevos de precios en el dia actual. No se actualizan los CSV")
    
    
    logging.info("=== Proceso completado ===")
    
    

except Exception as e:
    logging.error("Ocurrió un error en el script: %s", e)
    logging.error(traceback.format_exc())

finally:
    # Siempre subimos el log a Dropbox
    upload_log_to_dropbox()
    
    