class LectorYALex:
    """Lee y procesa un archivo .yal, aislando operadores literales y limpiando espacios."""
    
    def __init__(self, ruta_archivo):
        self.ruta_archivo = ruta_archivo
        self.lets = {}      
        self.rules = []     
        self.procesar_archivo()

    def procesar_archivo(self):
        with open(self.ruta_archivo, 'r', encoding='utf-8') as file:
            contenido = file.read()

        # 1. Eliminar comentarios (* ... *)
        mientras_tenga_comentarios = True
        while mientras_tenga_comentarios:
            inicio = contenido.find('(*')
            if inicio != -1:
                fin = contenido.find('*)', inicio)
                if fin != -1:
                    contenido = contenido[:inicio] + contenido[fin+2:]
                else:
                    mientras_tenga_comentarios = False
            else:
                mientras_tenga_comentarios = False

        lineas = contenido.split('\n')
        leyendo_rules = False

        for linea in lineas:
            linea = linea.strip()
            if not linea: continue

            # 2. Capturar variables 'let'
            if linea.startswith('let '):
                linea_sin_let = linea[4:].strip()
                if '=' in linea_sin_let:
                    partes = linea_sin_let.split('=', 1)
                    nombre = partes[0].strip()
                    valor = partes[1].strip()
                    
                    valor = self.expandir_valor(valor)
                    valor = self.limpiar_regex(valor)
                    valor = self.reemplazar_lets_en_string(valor)
                    self.lets[nombre] = valor

            # 3. Detectar inicio de 'rule'
            elif linea.startswith('rule '):
                leyendo_rules = True
                continue

            # 4. Capturar reglas
            elif leyendo_rules:
                if linea.startswith('|'):
                    linea = linea[1:].strip()
                
                # Buscar la primera '{' que NO esté dentro de comillas
                idx_llave_abre = -1
                en_comillas_d = False
                en_comillas_s = False
                
                for i, char in enumerate(linea):
                    if char == '"' and not en_comillas_s:
                        en_comillas_d = not en_comillas_d
                    elif char == "'" and not en_comillas_d:
                        en_comillas_s = not en_comillas_s
                    elif char == '{' and not en_comillas_d and not en_comillas_s:
                        idx_llave_abre = i
                        break
                        
                idx_llave_cierra = linea.rfind('}')
                
                if idx_llave_abre != -1 and idx_llave_cierra != -1:
                    regex_regla = linea[:idx_llave_abre].strip()
                    accion = linea[idx_llave_abre+1:idx_llave_cierra].strip()
                    
                    regex_regla = self.expandir_valor(regex_regla)
                    regex_regla = self.limpiar_regex(regex_regla)
                    regex_regla = self.reemplazar_lets_en_string(regex_regla)
                    self.rules.append((regex_regla, accion))

    def limpiar_regex(self, texto):
        """Elimina espacios de formato, quita comillas y disfraza operadores literales."""
        resultado = ""
        en_comillas_dobles = False
        en_comillas_simples = False
        
        mapa_seguro = {'+': 'þ', '*': 'ÿ', '?': 'ß', '|': 'æ', '(': 'ð', ')': 'ñ', '.': 'ø', '#': '§'}
        
        for char in texto:
            if char == '"' and not en_comillas_simples:
                en_comillas_dobles = not en_comillas_dobles
                continue 
            if char == "'" and not en_comillas_dobles:
                en_comillas_simples = not en_comillas_simples
                continue 
                
            if en_comillas_dobles or en_comillas_simples:
                # Si es un operador literal dentro de comillas, lo disfrazamos
                if char in mapa_seguro:
                    resultado += mapa_seguro[char]
                else:
                    resultado += char
            else:
                # Fuera de comillas, ignoramos los espacios de formato
                if char not in [' ', '\t', '\n', '\r']:
                    resultado += char
                    
        return resultado

    def expandir_valor(self, valor):
        """Convierte sintaxis YALex [a-z] a Regex pura."""
        while '[' in valor and ']' in valor:
            idx_abre = valor.find('[')
            idx_cierra = valor.find(']')
            contenido_corchetes = valor[idx_abre+1:idx_cierra]
            
            if '-' in contenido_corchetes:
                partes = contenido_corchetes.split('-')
                if len(partes) == 2:
                    ini = partes[0].replace("'", "").replace('"', '').strip()
                    fin = partes[1].replace("'", "").replace('"', '').strip()
                    if len(ini) == 1 and len(fin) == 1:
                        caracteres = [chr(i) for i in range(ord(ini), ord(fin) + 1)]
                        expansion = "(" + "|".join(caracteres) + ")"
                        valor = valor[:idx_abre] + expansion + valor[idx_cierra+1:]
                    else:
                        break 
            else:
                break 
        return valor

    def reemplazar_lets_en_string(self, texto):
        """Sustituye el nombre de las variables asegurando bordes de palabra."""
        claves_ordenadas = sorted(self.lets.keys(), key=len, reverse=True)
        for nombre in claves_ordenadas:
            if nombre not in texto: continue
            valor = self.lets[nombre]
            
            resultado = ""
            i = 0
            while i < len(texto):
                if texto[i:i+len(nombre)] == nombre:
                    char_previo = texto[i-1] if i > 0 else ' '
                    char_siguiente = texto[i+len(nombre)] if i+len(nombre) < len(texto) else ' '
                    es_palabra_completa = not (char_previo.isalnum() or char_previo == '_') and not (char_siguiente.isalnum() or char_siguiente == '_')
                    
                    if es_palabra_completa:
                        resultado += f"({valor})"
                        i += len(nombre)
                        continue
                resultado += texto[i]
                i += 1
            texto = resultado
        return texto