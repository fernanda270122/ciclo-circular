import json
with open('app/fixtures/datos_iniciales.json', encoding='utf-8') as f:
    data = json.load(f)
print('OK, registros:', len(data))