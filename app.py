import ee
import flask
from flask_cors import CORS

app = flask.Flask(__name__)
CORS(app) # Permite a conversa com o HTML

# --- CONFIGURAÇÃO ---
GEE_EMAIL = 'SEU-EMAIL-AQUI@PROJETO.iam.gserviceaccount.com'
JSON_CHAVE = 'chave-gee.json'

try:
    credentials = ee.ServiceAccountCredentials(GEE_EMAIL, JSON_CHAVE)
    ee.Initialize(credentials)
    print("✅ Sucesso: Rede CLIMGEO conectada ao Google Earth Engine!")
except Exception as e:
    print(f"❌ Erro na conexão: {e}")

@app.route('/get_map')
def get_map():
    ano = int(flask.request.args.get('ano', 2000))
    aoi = ee.FeatureCollection("projects/ee-lucaspsgeo/assets/PA_UF_2024")
    
    # Processamento LST MODIS
    img = ee.ImageCollection("MODIS/061/MOD11A1") \
        .filterBounds(aoi) \
        .filterDate(f'{ano}-01-01', f'{ano}-12-31') \
        .select('LST_Day_1km') \
        .mean() \
        .multiply(0.02).subtract(273.15) \
        .clip(aoi)

    # Paleta Climática
    vis_params = {
        'min': 20, 'max': 40,
        'palette': ['0000ff', '00ff00', 'ffff00', 'ff7f00', 'ff0000']
    }

    map_id_dict = ee.data.getMapId({'image': img.visualize(**vis_params)})
    return flask.jsonify({'url': map_id_dict['tile_fetcher'].url_format})

if __name__ == '__main__':
    app.run(port=5000)

if __name__ == '__main__':
    # O host '0.0.0.0' ajuda o Windows a não bloquear a conexão local
    app.run(host='0.0.0.0', port=5000, debug=False)