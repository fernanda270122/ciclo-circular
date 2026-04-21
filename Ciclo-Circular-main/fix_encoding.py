import json

with open('app/fixtures/datos_iniciales.json', 'rb') as f:
    content = f.read()

# Decodificar y encontrar donde empieza el JSON
text = content.decode('latin-1')
start = text.find('[')
text = text[start:]

# Verificar que es JSON válido
data = json.loads(text)

# Guardar correctamente en UTF-8
with open('app/fixtures/datos_iniciales.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Listo")