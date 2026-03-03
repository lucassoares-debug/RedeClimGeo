import ee
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Resolve o problema de bloqueio do navegador

# Autenticação Google Earth Engine
# Certifique-se que o arquivo chave-gee.json está na mesma pasta
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'chave-gee.json'
ee.Initialize(project='ee-lucaspsgeo')

@app.route('/get_map', methods=['GET'])
def get_map():
    try:
        year = int(request.args.get('year', 2023))
        
        # Carregando Asset do Pará e MODIS LST
        region = ee.FeatureCollection("projects/ee-seu-usuario/assets/PA_UF_2024")
        dataset = ee.ImageCollection("MODIS/061/MOD11A1") \
                    .filterDate(f'{year}-01-01', f'{year}-12-31') \
                    .select('LST_Day_1km') \
                    .mean() \
                    .clip(region)

        # Conversão Kelvin para Celsius
        lst_celsius = dataset.multiply(0.02).subtract(273.15)

        # Configuração de Visualização
        vis_params = {
            'min': 20,
            'max': 40,
            'palette': ['0000FF', '00FF00', 'FFFF00', 'FF7F00', 'FF0000']
        }

        map_info = lst_celsius.getMapId(vis_params)
        return jsonify({'url': map_info['tile_fetcher'].url_format})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Rodando na porta 5001 para evitar conflitos de firewall do IFPA
    print("✅ Servidor RedeClimGeo Ativo em http://localhost:5001")
    app.run(port=5001, debug=True)
