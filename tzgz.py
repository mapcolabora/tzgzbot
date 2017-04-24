import urllib.request, re, json
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from settings import TOKEN

def bus(bot, update, args):
    numposte = ' '.join(args)
    if numposte=='':
        bot.sendMessage(chat_id=update.message.chat_id, text='Uso: /bus <númerodeposte>')
    else:
        try:#Consulta a overpass
            g = urllib.request.urlopen('https://overpass-api.de/api/interpreter?data=%5Bout%3Ajson%5D%5Btimeout%3A25%5D%3B%0A%28%0A%20%20node%5B%22network%22~%22%5EAUZ%3B%7C%5EAUZ%24%7C%3BAUZ%24%22%5D%5B~%22ref%7Cref%3AAUZ%22~%22%5E'+numposte+'%3B%7C%5E'+numposte+'%24%7C%3B'+numposte+'%24%22%5D%2841.553297150595185%2C-1.1501312255859375%2C41.832735062152615%2C-0.6351470947265625%29%3B%0A%20%20relation%5B%22network%22~%22%5EAUZ%3B%7C%5EAUZ%24%7C%3BAUZ%24%22%5D%5B~%22ref%7Cref%3AAUZ%22~%22%5E'+numposte+'%3B%7C%5E'+numposte+'%24%7C%3B'+numposte+'%24%22%5D%5B%22public_transport%22%3D%22stop_area%22%5D%2841.553297150595185%2C-1.1501312255859375%2C41.832735062152615%2C-0.6351470947265625%29-%3E.a%3B%0A%20%20node%28r.a%3A%22platform%22%29%3B%0A%20%20way%28r.a%3A%22platform%22%29%3B%0A%29%3B%0A%0Aout%20body%3B%0A%3E%3B%0Aout%20skel%20qt%3B')#http://overpass-turbo.eu/s/mId, reemplazar 472 por el poste deseado
        except Exception as e:
                bot.sendMessage(chat_id=update.message.chat_id, text='Error en la consulta a Overpass API')
        try:#Consulta al Ayuntamiento
            f = urllib.request.urlopen('http://www.zaragoza.es/api/recurso/urbanismo-infraestructuras/transporte-urbano/poste/tuzsa-'+numposte+'.json?rf=html&srsname=wgs84')
        except Exception as e:
            bot.sendMessage(chat_id=update.message.chat_id, text='‼️<b>Error</b>‼️\nLa parada no existe o el servicio del ayuntamiento está caído.\n\nSi es de noche y el número de poste es correcto probablemente signifique que ya no pasan más buses por dicha parada hasta la mañana siguiente.', parse_mode='HTML')
        textoleido = str(f.read().decode('utf-8'))#Leer de la consulta al Ayto.
        f.close()
        #Web scraping
        textoleido = re.sub(r'.*"destinos":',r'', textoleido)
        textoleido=re.sub(r'\[',r'', textoleido)
        textoleido=re.sub(r']}',r'', textoleido)
        textoleido=re.sub(r'{"linea":"',r'', textoleido)
        textoleido=re.sub(r'","destino":"',r' ', textoleido)
        textoleido=re.sub(r'.","primero":"',r'\n🚌 ', textoleido)
        textoleido=re.sub(r'.","segundo":"',r', ', textoleido)
        textoleido=re.sub(r'."},',r'\n\n', textoleido)
        textoleido=re.sub(r'."}',r'', textoleido)
        #Corregir errores
        textoleido=re.sub(r'Sin estimacin',r'Sin estimación', textoleido)
        textoleido=re.sub(r'CI1',r'Ci1', textoleido)
        textoleido=re.sub(r'CI2',r'Ci2', textoleido)
        textoleido=re.sub(r'PEAFLOR',r'PEÑAFLOR', textoleido)
        overpassleido = str(g.read().decode('utf-8'))#Leer de overpass
        g.close()
        name=''
        if re.search('["]name["]: ["]',overpassleido):
            name=re.sub(r'[\s\S]*["]name["]: ["]',r'', overpassleido)
            name=re.sub(r'["][\s\S]*',r'', name)
            name='\n'+name
        imagen=''
        if re.search('["]wikimedia_commons["]: ["]',overpassleido):
            imagen=re.sub(r'[\s\S]*["]wikimedia_commons["]: ["]',r'', overpassleido)
            imagen=re.sub(r'["][\s\S]*',r'', imagen)
            imagen=re.sub(r' ',r'_', imagen)
            imagen='\n<a href="https://commons.wikimedia.org/wiki/'+imagen+'">📷 Foto</a>'
        else:
            if re.search('["]mapillary["]: ["]',overpassleido):
                imagen=re.sub(r'[\s\S]*["]mapillary["]: ["]',r'', overpassleido)
                imagen=re.sub(r'["][\s\S]*',r'', imagen)
                imagen='\n<a href="https://www.mapillary.com/app/?pKey='+imagen+'&focus=photo">📷 Foto</a>'
        wh=''
        if re.search('["]wheelchair["]: ["]',overpassleido):
            wh=re.sub(r'[\s\S]*["]wheelchair["]: ["]',r'', overpassleido)
            wh=re.sub(r'["][\s\S]*',r'', wh)
            if wh=="yes":
                wh='\n♿ Parada accesible en silla de ruedas'
            elif wh=="designated":
                wh='\n♿ Parada accesible en silla de ruedas'
            elif wh=="limited":
                wh='\n⚠♿ Parada parcialmente accesible en silla de ruedas'
            elif wh=="no":
                wh='\n🚫♿ Parada no accesible en silla de ruedas'
        tp=''
        if re.search('["]tactile_paving["]: ["]',overpassleido):
            tp=re.sub(r'[\s\S]*["]tactile_paving["]: ["]',r'', overpassleido)
            tp=re.sub(r'["][\s\S]*',r'', tp)
            if tp=="yes":
                tp='\n🕶 Parada dotada de pavimento táctil'
            elif tp=="incorrect":
                tp='\n⚠🕶 Parada dotada de pavimento táctil incorrecto'
            elif tp=="no":
                tp='\n🚫🕶 Parada no dotada de pavimento táctil'
        br=''
        if re.search('["]information["]: ["]braille["]',overpassleido):
            br='\n🕶✋ Parada dotada de información en braille'
        ia=''
        if re.search('["]acoustic["]: ["]voice_description["]',overpassleido):
            br='\n🔊 Parada dotada de información acústica'
        #Enviar mensaje
        bot.sendMessage(chat_id=update.message.chat_id, text='Poste '+numposte+name+'\n<a href="https://overpass-turbo.eu/map.html?Q=%5Bout%3Ajson%5D%5Btimeout%3A25%5D%3B%0Arelation%5B%22network%22~%22%5EAUZ%3B%7C%5EAUZ%24%7C%3BAUZ%24%22%5D%5B~%22ref%7Cref%3AAUZ%22~%22%5E'+numposte+'%3B%7C%5E'+numposte+'%24%7C%3B'+numposte+'%24%22%5D%5B%22public_transport%22%3D%22stop_area%22%5D(41.553297150595185%2C-1.1501312255859375%2C41.832735062152615%2C-0.6351470947265625)-%3E.a%3B%0A(%0A%20%20node%5B%22network%22~%22%5EAUZ%3B%7C%5EAUZ%24%7C%3BAUZ%24%22%5D%5B~%22ref%7Cref%3AAUZ%22~%22%5E'+numposte+'%3B%7C%5E'+numposte+'%24%7C%3B'+numposte+'%24%22%5D%5Bhighway%3Dbus_stop%5D(41.553297150595185%2C-1.1501312255859375%2C41.832735062152615%2C-0.6351470947265625)%3B%0A%20%20node%5Bhighway%3Dbus_stop%5D(r.a)%3B%0A)%3B%0A%0Aout%20body%3B%0A%3E%3B%0Aout%20skel%20qt%3B%0A%0A%0A%0A%0A%0A%0A%0A%7B%7Bstyle%3A%20%0Anode%7B%0A%20%20icon-width%3A%2018%3B%0A%20%20icon-image%3A%20url(%27http%3A%2F%2Fwww.zaragoza.es%2Fcontenidos%2Ficonos%2Fbus.png%27)%3B%0A%20%20text%3Aname%3B%0A%7D%0A%20%7D%7D">🗺 Mapa</a>'+imagen+wh+tp+br+ia+'\n\n'+textoleido, parse_mode='HTML', disable_web_page_preview=True)#Query del mapa: http://overpass-turbo.eu/s/mIg, reemplazar 472 por el poste deseado

def linbus(bot, update, args):
    numlinea = ' '.join(args)
    if numlinea=='':
        bot.sendMessage(chat_id=update.message.chat_id, text='Uso: /linbus <númerodelínea>')
    else:
        bot.sendMessage(chat_id=update.message.chat_id, text='<a href="http://overpass-turbo.eu/map.html?Q=%5Bout%3Ajson%5D%5Btimeout%3A25%5D%3B%0Aarea(3600345740)-%3E.searchArea%3B%0Arelation%5B%22route%22%3D%22bus%22%5D%5B%22ref%22%3D%22'+numlinea+'%22%5D(area.searchArea)%3B%0A%20%20way(r)%3B%0A%20%20way._%5B%22highway%22!%3D%22footway%22%5D%5B%22highway%22~%22^%22%5D%3B%0A%20%20out%20body%20geom%3B%0Arelation%5B%22route%22%3D%22bus%22%5D%5B%22ref%22%3D%22'+numlinea+'%22%5D(area.searchArea)%3B%0A%20%20node(r)%3B%0A%20%20node._%5B%22public_transport%22%3D%22stop_position%22%5D%3B%0A%20%20out%20body%20geom%3B%0A%0A%0A%0A%0A%0A%0A%0A%0A%0A%0A%0A%0A%0A%0A%0A%7B%7Bstyle%3A%20%0Anode%5Bpublic_transport%3Dstop_position%5D%7B%0A%20%20icon-width%3A%2012%3B%0A%20%20icon-image%3A%20url(%27http%3A%2F%2Fwww.zaragoza.es%2Fcontenidos%2Ficonos%2Fbus.png%27)%3B%0A%7D%0Away%7B%0A%20%20color%3Ared%3B%0A%20%20opacity%3A1%3B%0A%7D%0Away%3Aplaceholder%20%7B%0A%20%20color%3Ared%3B%0A%20%20opacity%3A1%3B%0A%7D%0A%20%7D%7D">Plano de la línea</a>', parse_mode='HTML')


def lintram(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='<a href="http://umap.openstreetmap.fr/es/map/tranvia-de-zaragoza_104444#13/41.6560/-0.9028">Plano de la línea</a>', parse_mode='HTML')


def tram(bot, update, args):
    numposte = ' '.join(args)
    if numposte=='':
        bot.sendMessage(chat_id=update.message.chat_id, text="Uso: /tram &lt;númerodeposte&gt;\n\nEl número de poste se saca de la siguiente manera:\nSe pone el código de la parada y seguido el sentido (1 sentido Mago de Oz, 2 sentido Av. de la Academia).\n\nEjemplo: Gran Vía sentido Mago de Oz: 140<b>1</b>\n\nCódigos de parada:\nAvenida de la Academia: <b>10</b>\nParque Goya: <b>20</b>\nJuslibol: <b>30</b>\nCampus Río Ebro: <b>40</b>\nMargarita Xirgú/Antón García Abril: <b>50</b>\nLegaz Lacambra/Adolfo Aznar: <b>60</b>\nClara Campoamor/Pablo Neruda: <b>70</b>\nRosalía de Castro/León Felipe: <b>80</b>\nMartínez Soria/María Montessori: <b>90</b>\nLa Chimenea: <b>100</b>\nPlaza del Pilar-Murallas: <b>110</b>\nCésar Augusto: <b>120</b>\nPlaza España: <b>130</b>\nPlaza Aragón: <b>131</b>\nGran Vía: <b>140</b>\nFernando el Católico-Goya: <b>150</b>\nPlaza San Francisco: <b>160</b>\nPlaza Emperador Carlos V: <b>170</b>\nRomareda: <b>180</b>\nCasablanca: <b>190</b>\nArgualas: <b>200</b>\nLos Olvidados: <b>210</b>\nLos Pájaros: <b>230</b>\nLa Ventana Indiscreta: <b>232</b>\nCantando Bajo la Lluvia: <b>240</b>\nUn Americano en París: <b>242</b>\nMago de Oz: <b>250</b>", parse_mode='HTML')
    else:
        url='http://www.zaragoza.es/api/recurso/urbanismo-infraestructuras/tranvia/'+numposte+'.json?rf=html&srsname=wgs84'
        textoleido=''
        try:
            f = urllib.request.urlopen(url)
        except Exception as e:
            bot.sendMessage(chat_id=update.message.chat_id, text='‼️<b>Error</b>‼️\nLa parada no existe o el servicio del ayuntamiento está caído.\n\nSi es de noche y el número de poste es correcto probablemente signifique que ya no pasan más tranvías por dicha parada hasta la mañana siguiente.', parse_mode='HTML')
        textoleido = str(f.read().decode('utf-8'))
        #Web scraping
        #textoleidocoord = re.sub(r'.*"coordinates":\[',r'', textoleido)
        #coordx = re.sub(r',.*',r'', textoleidocoord)
        #coordy = re.sub(r'].*',r'', textoleidocoord)
        #coordy = re.sub(r'.*,',r'', coordy)
        textoleido = re.sub(r'ESPAA',r'ESPAÑA', textoleido)#Corregir error ESPAA -> ESPAÑA
        textoleido = re.sub(r'GRAN VA',r'GRAN VÍA', textoleido)#Corregir error GRAN VA -> GRAN VÍA
        infotram = re.sub(r'.*"mensajes":\["',r'\n', textoleido)
        infotram = re.sub(r'","',r'\n', infotram)
        infotram = re.sub(r'"](\s|\S)*',r'', infotram)
        infotram = re.sub(r'\s?www.tranviasdezaragoza.es\s*Telefono Atencion al Cliente: 900 920 700',r'', infotram)
        textoleido = re.sub(r'.*"destinos":',r'', textoleido)
        textoleido=re.sub(r'\[',r'', textoleido)
        textoleido=re.sub(r']}',r'', textoleido)
        textoleido=re.sub(r'{"linea":"',r'🚊 ', textoleido)
        textoleido=re.sub(r'","destino":"',r' ', textoleido)
        textoleido=re.sub(r'","minutos":',r' ', textoleido)
        textoleido=re.sub(r'},',r'\n', textoleido)
        textoleido=re.sub(r'}].*',r'', textoleido)
        if infotram!='':
            infotram='\n\n⚠️ <b>Incidencias del servicio</b> ⚠️'+infotram
        f.close()
        try:
            f = urllib.request.urlopen('https://overpass-api.de/api/interpreter?data=%5Bout%3Ajson%5D%5Btimeout%3A25%5D%3B%28node%5B%22railway%22%3D%22tram%5Fstop%22%5D%5B%22ref%22%3D%22'+numposte+'%22%5D%2841%2E61030862727467%2C%2D0%2E9607887268066406%2C41%2E70214000452559%2C%2D0%2E8320426940917968%29%3B%29%3Bout%20body%3B%3E%3Bout%20skel%20qt%3B%0A')#http://overpass-turbo.eu/s/mNk, cambiar 1311 por el poste correspondiente
            overpassleido = str(f.read().decode('utf-8'))
        except Exception as e:
                bot.sendMessage(chat_id=update.message.chat_id, text='Error en la consulta a Overpass API')
        name=''
        if re.search('["]name["]: ["]',overpassleido):
            name=re.sub(r'[\s\S]*["]name["]: ["]',r'', overpassleido)
            name=re.sub(r'["][\s\S]*',r'', name)
            name='\n'+name
        imagen=''
        if re.search('["]wikimedia_commons["]: ["]',overpassleido):
            imagen=re.sub(r'[\s\S]*["]wikimedia_commons["]: ["]',r'', overpassleido)
            imagen=re.sub(r'["][\s\S]*',r'', imagen)
            imagen=re.sub(r' ',r'_', imagen)
            imagen='\n<a href="https://commons.wikimedia.org/wiki/'+imagen+'">📷 Foto</a>'
        else:
            if re.search('["]mapillary["]: ["]',overpassleido):
                imagen=re.sub(r'[\s\S]*["]mapillary["]: ["]',r'', overpassleido)
                imagen=re.sub(r'["][\s\S]*',r'', imagen)
                imagen='\n<a href="https://www.mapillary.com/app/?pKey='+imagen+'&focus=photo">📷 Foto</a>'
        #Enviar mensaje
        bot.sendMessage(chat_id=update.message.chat_id, text='Parada '+numposte+name+'\n<a href="http://overpass-turbo.eu/map.html?Q=[out%3Ajson][timeout%3A25]%3B%0Aarea(3600345740)-%3E.searchArea%3B%0A%0A(%0A%20%20node[%22railway%22%3D%22tram_stop%22][%22ref%22~%22^0*'+numposte+'$|^0*'+numposte+'\D|\D0*'+numposte+'$%22](area.searchArea)%3B)%3Bout%20body%3B%0A%3E%3B%0Aout%20skel%20qt%3B%0A%7B%7Bstyle%3A%20%20%0Anode%5Brailway%3Dtram_stop%5D%7B%0A%20%20icon-width%3A%2020%3B%0A%20%20icon-image%3A%20url(%27http%3A%2F%2Fwww.zaragoza.es%2Fcontenidos%2Ficonos%2Ftranvia.png%27)%3B%0A%20%20text%3A%20name%3B%7D%20%20%7D%7D">🗺 Mapa</a>'+imagen+'\n\n'+textoleido+infotram, parse_mode='HTML', disable_web_page_preview=True)
        f.close()

def mapatransporte(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='<a href="http://bit.ly/buszaragoza">Mapa del transporte público en Zaragoza</a>', parse_mode='HTML', disable_web_page_preview=True)

def mapabici(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='<a href="http://www.mapcolabora.org/Ziclabilidad">Mapa de la infraestructura ciclista en Zaragoza</a>', parse_mode='HTML', disable_web_page_preview=True)

def ruta(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='<a href="http://node1.idezar.es/RutometroIDEZarApp/rutometro.jsp?language=ES">Usar el calculador de rutas del Ayuntamiento</a>', parse_mode='HTML', disable_web_page_preview=True)

def busquedaParadas(bot, update):
    MAXELEMENTOS = 3#Máximo de paradas cercanas por medio de transporte, tiene que ser como mínimo 1
    DISTANCIA = '200'#Distancia en metros desde la posición enviada, lo ponemos como string para evitarnos conversiones luego
    latitud=format(update.message.location.latitude)
    longitud=format(update.message.location.longitude)
    url='http://www.zaragoza.es/api/recurso/urbanismo-infraestructuras/transporte-urbano/poste.json?rf=html&results_only=false&srsname=wgs84&rows='+str(MAXELEMENTOS)+'&point='+longitud+','+latitud+'&distance='+DISTANCIA
    try:
        f = urllib.request.urlopen(url)
        url='http://www.zaragoza.es/api/recurso/urbanismo-infraestructuras/tranvia.json?rf=html&results_only=false&srsname=wgs84&rows='+str(MAXELEMENTOS)+'&point='+longitud+','+latitud+'&distance='+DISTANCIA
        try:
            g = urllib.request.urlopen(url)
            url='http://www.zaragoza.es/api/recurso/urbanismo-infraestructuras/estacion-bicicleta.json?rf=html&results_only=false&srsname=wgs84&rows='+str(MAXELEMENTOS)+'&point='+longitud+','+latitud+'&distance='+DISTANCIA
            try:
                h = urllib.request.urlopen(url)
            except Exception as e:
                bot.sendMessage(chat_id=update.message.chat_id, text='‼️<b>Error</b>‼️\nImposible contactar con el servicio del Ayuntamiento.', parse_mode='HTML')
        except Exception as e:
            bot.sendMessage(chat_id=update.message.chat_id, text='‼️<b>Error</b>‼️\nImposible contactar con el servicio del Ayuntamiento.', parse_mode='HTML')
    except Exception as e:
        bot.sendMessage(chat_id=update.message.chat_id, text='‼️<b>Error</b>‼️\nImposible contactar con el servicio del Ayuntamiento.', parse_mode='HTML')
    #BUS
    jsonleidobus = json.loads(str(f.read().decode('utf-8')))
    f.close()
    nElementosbus = jsonleidobus["totalCount"]
    textobus = ''
    if nElementosbus==0:
        textobus='No hay paradas de bus a '+DISTANCIA+' metros de la ubicación\n\n'
    else:
        if nElementosbus>MAXELEMENTOS:
            nElementosbus=MAXELEMENTOS#Limitamos a MAXELEMENTOS los resultados por medio de transporte
        for i in range(nElementosbus):
            textobus = textobus + jsonleidobus["result"][i]["id"] + '\n' + jsonleidobus["result"][i]["title"] + '\n\n'
        textobus = re.sub('\n\(\d+\) ',r'\n', textobus)
        textobus = re.sub('Líneas',r'\nLíneas', textobus)
        textobus = re.sub('tuzsa-',r'/bus ', textobus)
        textobus = re.sub('rural-',r'CTAZ ', textobus)
    #TRANVÍA
    jsonleidotram = json.loads(str(g.read().decode('utf-8')))
    g.close()
    nElementostram = jsonleidotram["totalCount"]
    textotram = ''
    if nElementostram==0:
        textotram='No hay paradas de tranvía a '+DISTANCIA+' metros de la ubicación\n\n'
    else:
        if nElementostram>MAXELEMENTOS:
            nElementostram=MAXELEMENTOS#Limitamos a 5 los resultados por medio de transporte
        for i in range(nElementostram):
            if int(jsonleidotram["result"][i]["id"])%2==0:
                sentido='\n(Sentido Av. Academia)'
            else:
                sentido='\n(Sentido Mago de Oz)'
            textotram = textotram + '/tram '+ jsonleidotram["result"][i]["id"] + '\n' + jsonleidotram["result"][i]["title"] + sentido + '\n\n'
    #BIZI
    jsonleidobizi = json.loads(str(h.read().decode('utf-8')))
    h.close()
    nElementosbizi = jsonleidobizi["totalCount"]
    textobizi = ''
    if nElementosbizi==0:
        textobizi='No hay estaciones BiZi a '+DISTANCIA+' metros de la ubicación\n\n'
    else:
        if nElementosbizi>MAXELEMENTOS:
            nElementosbizi=MAXELEMENTOS#Limitamos a 5 los resultados por medio de transporte
        for i in range(nElementosbizi):
            textobizi = textobizi + '/bizi '+ jsonleidobizi["result"][i]["id"] + '\n' + jsonleidobizi["result"][i]["title"] + '\n\n'

    bot.sendMessage(chat_id=update.message.chat_id, text='🚌 <b>Paradas de bus cercanas:</b>\n'+textobus+'🚊 <b>Paradas de tranvía cercanas:</b>\n'+textotram+'<b>🚲 Estaciones BiZi cercanas:</b>\n'+textobizi, parse_mode='HTML', disable_web_page_preview=True)

def bizi(bot, update, args):
    numposte = ' '.join(args)
    if numposte=='':
        bot.sendMessage(chat_id=update.message.chat_id, text="Uso: /bizi &lt;númerodeestación&gt;", parse_mode='HTML')
    else:
        url='http://www.zaragoza.es/api/recurso/urbanismo-infraestructuras/estacion-bicicleta/'+numposte+'.json?rf=html&srsname=wgs84'
        try:
            f = urllib.request.urlopen(url)
        except Exception as e:
            bot.sendMessage(chat_id=update.message.chat_id, text='‼️<b>Error</b>‼️\nImposible contactar con el servicio del Ayuntamiento.', parse_mode='HTML')
        jsonleido = json.loads(str(f.read().decode('utf-8')))
        foto = ''
        try:
            g = urllib.request.urlopen('http://overpass-api.de/api/interpreter?data=%5Bout%3Ajson%5D%5Btimeout%3A25%5D%3Barea%283600345740%29%2D%3E%2EsearchArea%3B%28node%5B%22amenity%22%3D%22bicycle%5Frental%22%5D%5B%22network%22%3D%22BiZi%22%5D%5B%22ref%22%3D%22'+numposte+'%22%5D%28area%2EsearchArea%29%3B%29%3Bout%20body%3B%3E%3Bout%20skel%20qt%3B%0A')#Overpass request para la estación BiZi
            overpassleido = json.loads(str(g.read().decode('utf-8')))
            g.close()
            foto = '\n<a href="https://www.mapillary.com/app/?pKey='+overpassleido["elements"][0]["tags"]["mapillary"]+'&focus=photo">📷 Foto</a>'
        except:
            print('No se ha encontrado en Overpass API: /bizi '+numposte)
        estado=jsonleido["estado"]
        if estado=='OPN':
            estado=' ✅'
        elif estado=='':#TODO averiguar qué estado se pone cuando una estación no está operativa
            estado=' ⚠️'
        bot.sendMessage(chat_id=update.message.chat_id, text='Estación número '+jsonleido["id"]+estado+'\n'+jsonleido["title"]+'\n<a href="http://overpass-turbo.eu/map.html?Q=%5Bout%3Ajson%5D%5Btimeout%3A25%5D%3B%0Aarea(3600345740)-%3E.searchArea%3B%0A(%0A%20%20node%5B%22amenity%22%3D%22bicycle_rental%22%5D%5B%22network%22%3D%22BiZi%22%5D%5B%22ref%22%3D%22'+numposte+'%22%5D(area.searchArea)%3B%0A)%3B%0Aout%20body%3B%0A%3E%3B%0Aout%20skel%20qt%3B%0A%0A%0A%0A%7B%7Bstyle%3A%20%0A%20%20node%20%7B%20color%3Ared%3B%20fill-color%3Ared%3B%20fill-opacity%3A1%3B%20text%3A%20name%3B%20%20%7D%0A%20%7D%7D">🗺 Mapa</a>'+foto+'\n\n🚲Bicis disponibles: '+str(jsonleido["bicisDisponibles"])+'\n🚴Anclajes disponibles: '+str(jsonleido["anclajesDisponibles"]), parse_mode='HTML', disable_web_page_preview=True)#el link del mapa hace esta query overpass (cambiar 66 por el número de poste deseado): http://overpass-turbo.eu/s/lhL
        if estado==' ⚠️':
            paradasBiziCercanas(bot,update,str(jsonleido["geometry"]["coordinates"][0]),str(jsonleido["geometry"]["coordinates"][1]),'La estación BiZi '+jsonleido["id"]+' no está operativa',numposte)
        elif jsonleido["bicisDisponibles"]==0:
            paradasBiziCercanas(bot,update,str(jsonleido["geometry"]["coordinates"][0]),str(jsonleido["geometry"]["coordinates"][1]),'No quedan bicis disponibles',numposte)
        elif jsonleido["anclajesDisponibles"]==0:
            paradasBiziCercanas(bot,update,str(jsonleido["geometry"]["coordinates"][0]),str(jsonleido["geometry"]["coordinates"][1]),'No quedan huecos disponibles',numposte)
        
def paradasBiziCercanas(bot,update,longitud,latitud,estado,numposte):
    DISTANCIA = '350'#Distancia en metros desde la posición enviada, lo ponemos como string para evitarnos conversiones luego. Por contrato la más cercana tiene que estar como mucho a 300 metros, así que al poner 350 nos aseguramos de que haya al menos otra
    url='http://www.zaragoza.es/api/recurso/urbanismo-infraestructuras/estacion-bicicleta.json?rf=html&results_only=false&srsname=wgs84&point='+longitud+','+latitud+'&distance='+DISTANCIA
    try:
        h = urllib.request.urlopen(url)
    except Exception as e:
        bot.sendMessage(chat_id=update.message.chat_id, text='‼️<b>Error</b>‼️\nImposible contactar con el servicio del Ayuntamiento.', parse_mode='HTML')
    #BIZI
    jsonleidobizi = json.loads(str(h.read().decode('utf-8')))
    h.close()
    nElementosbizi = jsonleidobizi["totalCount"]
    textobizi = ''
    if nElementosbizi==0:
        textobizi='No hay estaciones BiZi a '+DISTANCIA+' metros de la ubicación\n\n'
    else:
        for i in range(nElementosbizi):
            if(jsonleidobizi["result"][i]["id"]!=numposte):#no enseñar la parada desde la que se invoca
                textobizi = textobizi + '/bizi '+ jsonleidobizi["result"][i]["id"] + '\n' + jsonleidobizi["result"][i]["title"] + '\n\n'
    bot.sendMessage(chat_id=update.message.chat_id, text='<b>'+estado+', quizás te interesen otras estaciones cercanas (a &lt'+DISTANCIA+'m):</b>\n'+textobizi, parse_mode='HTML', disable_web_page_preview=True)
        
def help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='Bot sobre el transporte público en Zaragoza, "powered by" contribuidores de <a href="https://www.openstreetmap.org/">OpenStreetMap</a> y <a href="http://www.zaragoza.es/ciudad/risp/api.htm">datos abiertos del Ayuntamiento de Zaragoza</a>. Programado por @Robot8A.\n\n<a href="https://github.com/mapcolabora/tzgzbot">Código fuente</a>, licencia GPLv3+\n\nImagen de perfil por @Robot8A, <a href="https://commons.wikimedia.org/wiki/File:Parada_bus_Balc%C3%B3n_San_L%C3%A1zaro.jpg">ver original</a>, CC-BY.\n\nAgradecimientos a <a href="http://pulsar.unizar.es/">Púlsar</a> por el hosting del bot.\n\n\n<b>FUNCIONES DEL BOT:</b>\n<b>Mandar ubicación</b> - Te devuelve un listado de las paradas a 200 metros de la ubicación\n<b>/bus &lt;númerodeposte&gt;</b> - Tiempo real de los postes de bus\n<b>/linbus &lt;númerodelínea&gt;</b> - Plano de la línea de bus correspondiente\n<b>/tram &lt;númerodeposte&gt;</b> - Tiempo real de los postes del tranvía\n<b>/lintram</b> - Plano de la línea de tranvía\n<b>/bizi &lt;númerodeestación&gt;</b> - Estado en tiempo real de las estaciones de BiZi\n<b>/mapatransporte</b> - Mapa con todos los medios de transporte\n<b>/mapabici</b> - Mapa de la infraestructura ciclista en Zaragoza\n<b>/ruta</b> - Usar el calculador de rutas del Ayuntamiento\n<b>/faq</b> - Muestra la respuesta a las preguntas más frecuentes sobre el bot\n<b>/help</b> - Muestra este mensaje', parse_mode='HTML', disable_web_page_preview=True)

def faq(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='<b>El mapa no me enseña nada</b>\nEsto es posiblemente porque la parada no esté o esté mal etiquetada en <a href="https://www.openstreetmap.org/">OpenStreetMap</a>. Puedes ayudar y poner la parada tú mismo, es muy fácil. Si no sabes cómo o prefieres no hacerlo, también puedes contactar conmigo para que lo haga: @Robot8A\n\n<b>¿Qué es eso de OpenStreetMap?</b>\nEs un proyecto colaborativo de datos geográficos libres, algo así como "la Wikipedia de los mapas" describiéndolo en pocas palabras.\nLos datos son introducidos por voluntarios (todo el mundo puede participar 😉), y luego se pueden exportar en una licencia libre (<a href="https://www.openstreetmap.org/copyright">ODbL</a>).\nPara más información sobre el proyecto:\nwww.openstreetmap.org\nwiki.openstreetmap.org\nes.wikipedia.org/wiki/OpenStreetMap\n\n<b>¿De dónde sacáis los datos?</b>\nLos datos se sacan de <a href="https://www.openstreetmap.org/">OpenStreetMap</a> (nombre de paradas, link a imagen, accesibilidad) y <a href="http://www.zaragoza.es/ciudad/risp/api.htm">datos abiertos del Ayuntamiento de Zaragoza</a> (nombre de paradas, líneas de las paradas, datos en tiempo real). El resto son links a otros servicios, que se basan mayoritariamente también en datos de OSM y/o el Ayuntamiento de Zaragoza.\n\n<b>El bot tarda bastante en darme una respuesta, ¿es esto normal?</b>\nPor desgracia, sí, sobre todo en /bus y /tram. Hay que tener en cuenta que el bot se encuentra aún en desarrollo, y estoy trabajando en mejorar el código.\n\n<b>¿El bot guarda algún dato personal sobre mí?</b>\nAbsolutamente ninguno, si no te fias puedes echarle un vistazo al código fuente: https://github.com/mapcolabora/tzgzbot\n\n<b>¿Tienes pensado añadirle más funciones?</b>\nSí, por el momento tengo en mente añadir una función de paradas favoritas.\nTambién tengo que mejorar el código para hacerlo más eficiente y versátil.\nEn cualquier caso, puedes pasarte por mi blog, dónde voy poniendo las actualizaciones: tzgzbot.wordpress.com', parse_mode='HTML', disable_web_page_preview=True)

updater = Updater(TOKEN)#token de @tzgzbot para la API de Telegram

updater.dispatcher.add_handler(CommandHandler('bus', bus, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('tram', tram, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('bizi', bizi, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('linbus', linbus, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('lintram', lintram))
updater.dispatcher.add_handler(CommandHandler('mapatransporte', mapatransporte))
updater.dispatcher.add_handler(CommandHandler('mapabici', mapabici))
updater.dispatcher.add_handler(CommandHandler('ruta', ruta))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('ayuda', help))#Hace lo mismo que /help
updater.dispatcher.add_handler(CommandHandler('faq', faq))
updater.dispatcher.add_handler(CommandHandler('start', help))
updater.dispatcher.add_handler(MessageHandler(Filters.location|Filters.venue, busquedaParadas))

updater.start_polling()
updater.idle()
