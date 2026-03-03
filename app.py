import ee
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

# ============================================================
# 1. CONFIGURAÇÕES DO AMBIENTE (FLASK E SEGURANÇA)
# ============================================================
app = Flask(__name__)
CORS(app)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'chave-gee.json'

# ============================================================
# 2. INICIALIZAÇÃO DO GOOGLE EARTH ENGINE (GEE)
# ============================================================
try:
    ee.Initialize(project='ee-lucaspsgeo')
    print("✅ Conexão LAGECLIM -> GEE: OK!")
except Exception as e:
    print(f"❌ Erro na conexão GEE: {e}")

# ============================================================
# 3. ROTA DE DADOS: TEMPERATURA (TST / MODIS)
# ============================================================
@app.route('/get_map', methods=['GET'])
def get_map():
    try:
        year = int(request.args.get('year', 2000))
        region = ee.FeatureCollection("projects/ee-lucaspsgeo/assets/PA_UF_2024")
        dataset = ee.ImageCollection("MODIS/061/MOD11A1") \
                    .filterDate(f'{year}-01-01', f'{year}-12-31') \
                    .select('LST_Day_1km') \
                    .mean() \
                    .clip(region)
        lst_celsius = dataset.multiply(0.02).subtract(273.15)
        vis_params = {'min': 20, 'max': 40, 'palette': ['0000FF', '00FF00', 'FFFF00', 'FF7F00', 'FF0000']}
        map_info = lst_celsius.getMapId(vis_params)
        return jsonify({'url': map_info['tile_fetcher'].url_format})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# 4. ROTA DE VETORES: DIVISÃO MUNICIPAL
# ============================================================
@app.route('/get_bounds', methods=['GET'])
def get_bounds():
    try:
        municipios = ee.FeatureCollection("projects/ee-lucaspsgeo/assets/PA_Municipios_2024")
        empty = ee.Image().byte()
        outline = empty.paint(featureCollection=municipios, color=1, width=1)
        map_info = outline.getMapId({'palette': '000000'})
        return jsonify({'url': map_info['tile_fetcher'].url_format})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# 5. ROTA DE VETORES: LIMITE ESTADUAL (UF)
# ============================================================
@app.route('/get_state_bounds', methods=['GET'])
def get_state_bounds():
    try:
        estado = ee.FeatureCollection("projects/ee-lucaspsgeo/assets/PA_UF_2024")
        empty = ee.Image().byte()
        outline = empty.paint(featureCollection=estado, color=1, width=2)
        map_info = outline.getMapId({'palette': '333333'})
        return jsonify({'url': map_info['tile_fetcher'].url_format})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# 6. EXECUÇÃO DO SERVIDOR (MODO PRODUÇÃO)
# ============================================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
