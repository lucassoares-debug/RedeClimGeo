import ee
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

# ============================================================
# 1. CONFIGURAÇÕES DO AMBIENTE (FLASK E SEGURANÇA)
# ============================================================
app = Flask(__name__)
CORS(app)  # Libera o acesso para o mapa no navegador

# Caminho da credencial (Certifique-se de que o arquivo está na pasta)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'chave-gee.json'

# ============================================================
# 2. INICIALIZAÇÃO DO GOOGLE EARTH ENGINE (GEE)
# ============================================================
try:
    # Vincula o código ao seu projeto oficial no Google Cloud
    ee.Initialize(project='ee-lucaspsgeo')
    print("✅ Conexão LAGECLIM -> Google Earth Engine: OK!")
except Exception as e:
    print(f"❌ Erro na conexão GEE: {e}")

# ============================================================
# 3. ROTA DE DADOS: PROCESSAMENTO DE TEMPERATURA (TST)
# ============================================================
@app.route('/get_map', methods=['GET'])
def get_map():
    try:
        # A. Parâmetros de Entrada (Ano do Slider)
        year = int(request.args.get('year', 2000))
        
        # B. Área de Estudo (Asset do Estado do Pará)
        region = ee.FeatureCollection("projects/ee-lucaspsgeo/assets/PA_UF_2024")

        # C. Coleção de Dados (MODIS LST - 1km Diário)
        dataset = ee.ImageCollection("MODIS/061/MOD11A1") \
                    .filterDate(f'{year}-01-01', f'{year}-12-31') \
                    .select('LST_Day_1km') \
                    .mean() \
                    .clip(region)

        # D. Processamento Físico (Conversão Kelvin para Celsius)
        lst_celsius = dataset.multiply(0.02).subtract(273.15)

        # E. Configuração Visual (Paleta Térmica)
        vis_params = {
            'min': 20,
            'max': 40,
            'palette': ['0000FF', '00FF00', 'FFFF00', '#FF7F00', 'FF0000']
        }

        # F. Geração do ID de Visualização
        map_info = lst_celsius.getMapId(vis_params)
        
        return jsonify({'url': map_info['tile_fetcher'].url_format})
    
    except Exception as e:
        print(f"⚠️ Erro no processamento: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================
# 4. EXECUÇÃO DO SERVIDOR (MODO DE PRODUÇÃO)
# ============================================================
if __name__ == '__main__':
    # Configurações para o servidor do IFPA:
    # host='0.0.0.0' -> Aceita conexões de fora (Internet/Rede)
    # port=5001      -> Porta padrão RedeClimGeo
    # debug=False    -> Modo estável (Produção)
    
    print("🚀 Servidor RedeClimGeo Iniciado!")
    app.run(host='0.0.0.0', port=5001, debug=False)
