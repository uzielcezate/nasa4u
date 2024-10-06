# Backend: Flask App
from flask import Flask, render_template, jsonify, request
import pandas as pd

app = Flask(__name__)

# Cargar la base de datos CSV
exoplanetas_df = pd.read_csv('exoplanets_data.csv')

# Verificar las columnas disponibles y seleccionar solo las que existen
columnas_disponibles = exoplanetas_df.columns.tolist()
columnas_relevantes = [
    'pl_name', 'hostname', 'pl_orbper', 'pl_orbsmax', 'pl_eqt',
    'discoverymethod', 'disc_year', 'pl_rade', 'pl_massestr', 'st_teff', 'st_rad', 'st_lum', 'sy_dist'
]
columnas_existentes = [col for col in columnas_relevantes if col in columnas_disponibles]

# Filtrar las columnas relevantes y eliminar filas con valores faltantes
exoplanetas_df = exoplanetas_df[columnas_existentes].dropna()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/exoplanetas', methods=['GET'])
def get_exoplanetas():
    # Convertir los datos del DataFrame en una lista de diccionarios con columnas relevantes
    exoplanetas = exoplanetas_df.to_dict(orient='records')
    return jsonify(exoplanetas)

@app.route('/exoplaneta/<nombre>', methods=['GET'])
def get_exoplaneta(nombre):
    # Buscar los datos del exoplaneta por nombre (ignorando mayúsculas)
    exoplaneta = exoplanetas_df[exoplanetas_df['pl_name'].str.lower() == nombre.lower()].to_dict(orient='records')
    if exoplaneta:
        return jsonify(exoplaneta[0])
    return jsonify({'error': 'Exoplaneta no encontrado'}), 404

# Ruta para filtrar exoplanetas por parámetros específicos
@app.route('/filtrar', methods=['GET'])
def filtrar_exoplanetas():
    # Obtener los parámetros de filtrado desde la solicitud
    distancia = request.args.get('distancia', type=float)
    min_radio = request.args.get('min_radio', type=float)
    max_radio = request.args.get('max_radio', type=float)
    min_masa = request.args.get('min_masa', type=float)
    max_masa = request.args.get('max_masa', type=float)
    min_lum = request.args.get('min_lum', type=float)
    max_lum = request.args.get('max_lum', type=float)

    # Filtrar el DataFrame según los parámetros proporcionados
    filtrado = exoplanetas_df
    if 'sy_dist' in filtrado.columns and distancia is not None:
        filtrado = filtrado[filtrado['sy_dist'] <= distancia]
    if 'pl_rade' in filtrado.columns:
        if min_radio is not None:
            filtrado = filtrado[filtrado['pl_rade'] >= min_radio]
        if max_radio is not None:
            filtrado = filtrado[filtrado['pl_rade'] <= max_radio]
    if 'pl_massestr' in filtrado.columns:
        if min_masa is not None:
            filtrado = filtrado[filtrado['pl_massestr'] >= min_masa]
        if max_masa is not None:
            filtrado = filtrado[filtrado['pl_massestr'] <= max_masa]
    if 'st_lum' in filtrado.columns:
        if min_lum is not None:
            filtrado = filtrado[filtrado['st_lum'] >= min_lum]
        if max_lum is not None:
            filtrado = filtrado[filtrado['st_lum'] <= max_lum]

    # Convertir el resultado filtrado en una lista de diccionarios
    exoplanetas_filtrados = filtrado.to_dict(orient='records')
    return jsonify(exoplanetas_filtrados)

if __name__ == '__main__':
    app.run(debug=True)