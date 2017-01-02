import urllib.request, re
from telegram.ext import Updater, CommandHandler

def bus(bot, update, args):
    numposte = ' '.join(args)
    if numposte=='':
        bot.sendMessage(chat_id=update.message.chat_id, text='Uso: /bus <númerodeposte>')
    else:
        url='http://www.zaragoza.es/api/recurso/urbanismo-infraestructuras/transporte-urbano/poste/tuzsa-'+numposte+'.json?rf=html&srsname=wgs84'
        try:
            f = urllib.request.urlopen(url)
        except Exception as e:
            bot.sendMessage(chat_id=update.message.chat_id, text='‼️<b>Error</b>‼️\nLa parada no existe o el servicio del ayuntamiento está caído.\n\nSi es de noche y el número de poste es correcto probablemente signifique que ya no pasan más buses por dicha parada hasta la mañana siguiente.', parse_mode='HTML')
        textoleido=''
        textoleido = str(f.read().decode('utf-8'))
        #Web scraping
        #textoleidocoord = re.sub(r'.*"coordinates":\[',r'', textoleido)
        #coordx = re.sub(r',.*',r'', textoleidocoord)
        #coordy = re.sub(r'].*',r'', textoleidocoord)
        #coordy = re.sub(r'.*,',r'', coordy)
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
        f.close()
        try:
            f = urllib.request.urlopen('http://overpass-api.de/api/interpreter?data=[out%3Ajson][timeout%3A25]%3B%0Aarea(3600345740)-%3E.searchArea%3B%0A%0A(%0A%20%20node[%22highway%22%3D%22bus_stop%22][%22operator%22~%22^[Aa]uzsa|[Aa]uzsa$%22][%22ref%22~%22^0*'+numposte+'$|^0*'+numposte+'\D|\D0*'+numposte+'$%22](area.searchArea)%3B%0A%20%20node[%22highway%22%3D%22bus_stop%22][%22operator%22~%22^[Aa]uzsa|[Aa]uzsa$%22][~%22ref:[Aa]uzsa%22~%22^0*'+numposte+'$|^0*'+numposte+'\D|\D0*'+numposte+'$%22](area.searchArea)%3B%0A%20%20relation[%22public_transport%22%3D%22stop_area%22][%22operator%22~%22^[Aa]uzsa|[Aa]uzsa$%22][%22ref%22~%22^0*'+numposte+'$|^0*'+numposte+'\D|\D0*'+numposte+'$%22](area.searchArea)%3B%0A%20%20node(r)%3B%0A%20%20node._[%22highway%22%3D%22bus_stop%22]%3B%0A%20%20relation[%22public_transport%22%3D%22stop_area%22][%22operator%22~%22^[Aa]uzsa|[Aa]uzsa$%22][~%22ref:[Aa]uzsa%22~%22^0*'+numposte+'$|^0*'+numposte+'\D|\D0*'+numposte+'$%22](area.searchArea)%3B%0A%20%20node(r)%3B%0A%20%20node._[%22highway%22%3D%22bus_stop%22]%3B%0A)%3B%0A%0Aout%20body%3B%0A%3E%3B%0Aout%20skel%20qt%3B')
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
            imagen='\n<a href="https://commons.wikimedia.org/wiki/'+imagen+'">Imagen</a>'
        else:
            if re.search('["]mapillary["]: ["]',overpassleido):
                imagen=re.sub(r'[\s\S]*["]mapillary["]: ["]',r'', overpassleido)
                imagen=re.sub(r'["][\s\S]*',r'', imagen)
                imagen='\n<a href="https://www.mapillary.com/app/?pKey='+imagen+'&focus=photo">Imagen</a>'
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
            elif tp=="no":
                tp='\n🚫🕶 Parada no dotada de pavimento táctil'
        br=''
        if re.search('["]information["]: ["]braille["]',overpassleido):
            br='\n🕶✋ Parada dotada de información en braille'
        ia=''
        if re.search('["]acoustic["]: ["]voice_description["]',overpassleido):
            br='\n🔊 Parada dotada de información acústica'
        #Enviar mensaje
        bot.sendMessage(chat_id=update.message.chat_id, text='Poste '+numposte+name+'\n<a href="http://overpass-turbo.eu/map.html?Q=[out%3Ajson][timeout%3A25]%3B%0Aarea(3600345740)-%3E.searchArea%3B%0A%0A(%0A%20%20node[%22highway%22%3D%22bus_stop%22][%22operator%22~%22^[Aa]uzsa|[Aa]uzsa$%22][%22ref%22~%22^0*'+numposte+'$|^0*'+numposte+'\D|\D0*'+numposte+'$%22](area.searchArea)%3B%0A%20%20node[%22highway%22%3D%22bus_stop%22][%22operator%22~%22^[Aa]uzsa|[Aa]uzsa$%22][~%22ref:[Aa]uzsa%22~%22^0*'+numposte+'$|^0*'+numposte+'\D|\D0*'+numposte+'$%22](area.searchArea)%3B%0A%20%20relation[%22public_transport%22%3D%22stop_area%22][%22operator%22~%22^[Aa]uzsa|[Aa]uzsa$%22][%22ref%22~%22^0*'+numposte+'$|^0*'+numposte+'\D|\D0*'+numposte+'$%22](area.searchArea)%3B%0A%20%20node(r)%3B%0A%20%20node._[%22highway%22%3D%22bus_stop%22]%3B%0A%20%20relation[%22public_transport%22%3D%22stop_area%22][%22operator%22~%22^[Aa]uzsa|[Aa]uzsa$%22][~%22ref:[Aa]uzsa%22~%22^0*'+numposte+'$|^0*'+numposte+'\D|\D0*'+numposte+'$%22](area.searchArea)%3B%0A%20%20node(r)%3B%0A%20%20node._[%22highway%22%3D%22bus_stop%22]%3B%0A)%3B%0A%0Aout%20body%3B%0A%3E%3B%0Aout%20skel%20qt%3B%0A%7B%7Bstyle%3A%20%20%0Arelation%5Bpublic_transport%3Dstop_area%5D%20node%5Bhighway%3Dbus_stop%5D%7B%0A%20%20icon-width%3A%2020%3B%0A%20%20icon-image%3A%20url(%27http%3A%2F%2Fwww.zaragoza.es%2Fcontenidos%2Ficonos%2Fbus.png%27)%3B%0A%20%20text%3A%20name%3B%0A%7D%0Anode%5Bhighway%3Dbus_stop%5D%7B%0A%20%20icon-width%3A%2020%3B%0A%20%20icon-image%3A%20url(%27http%3A%2F%2Fwww.zaragoza.es%2Fcontenidos%2Ficonos%2Fbus.png%27)%3B%0A%20%20text%3A%20name%3B%0A%7D%0Arelation%20node%5Bhighway!%3Dbus_stop%5D%7B%0A%20%20opacity%3A%200%3B%0A%20%20fill-opacity%3A%200%3B%0A%7D%0Anode%5Bhighway!%3Dbus_stop%5D%7B%0A%20%20opacity%3A%200%3B%0A%20%20fill-opacity%3A%200%3B%0A%7D%0Away%7B%0A%20%20opacity%3A%200%3B%0A%20%20fill-opacity%3A%200%3B%0A%7D%0A%20%20%7D%7D">Mapa</a>'+imagen+wh+tp+br+ia+'\n\n'+textoleido, parse_mode='HTML', disable_web_page_preview=True)
        f.close()

        #<a href="http://www.openstreetmap.org/?mlat='+coordy+'&mlon='+coordx+'#map=15/'+coordy+'/'+coordx+'">Mapa</a>

def linbus(bot, update, args):
    numlinea = ' '.join(args)
    if numlinea=='':
        bot.sendMessage(chat_id=update.message.chat_id, text='Uso: /linbus <númerodelínea>')
    else:
        bot.sendMessage(chat_id=update.message.chat_id, text='<a href="http://overpass-turbo.eu/map.html?Q=%5Bout%3Ajson%5D%5Btimeout%3A25%5D%3B%0Aarea(3600345740)-%3E.searchArea%3B%0Arelation%5B%22route%22%3D%22bus%22%5D%5B%22ref%22%3D%22'+numlinea+'%22%5D(area.searchArea)%3B%0A%20%20way(r)%3B%0A%20%20way._%5B%22highway%22!%3D%22footway%22%5D%5B%22highway%22~%22^%22%5D%3B%0A%20%20out%20body%20geom%3B%0Arelation%5B%22route%22%3D%22bus%22%5D%5B%22ref%22%3D%22'+numlinea+'%22%5D(area.searchArea)%3B%0A%20%20node(r)%3B%0A%20%20node._%5B%22public_transport%22%3D%22stop_position%22%5D%3B%0A%20%20out%20body%20geom%3B%0A%0A%0A%0A%0A%0A%0A%0A%0A%0A%0A%0A%0A%0A%0A%0A%7B%7Bstyle%3A%20%0Anode%5Bpublic_transport%3Dstop_position%5D%7B%0A%20%20icon-width%3A%2012%3B%0A%20%20icon-image%3A%20url(%27http%3A%2F%2Fwww.zaragoza.es%2Fcontenidos%2Ficonos%2Fbus.png%27)%3B%0A%20%20text%3A%20name%3B%0A%7D%0Away%7B%0A%20%20color%3Ared%3B%0A%20%20opacity%3A1%3B%0A%7D%0Away%3Aplaceholder%20%7B%0A%20%20color%3Ared%3B%0A%20%20opacity%3A1%3B%0A%7D%0A%20%7D%7D">Plano de la línea</a>', parse_mode='HTML')


def lintram(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='<a href="http://umap.openstreetmap.fr/es/map/tranvia-de-zaragoza_104444#13/41.6560/-0.9028">Plano de la línea</a>', parse_mode='HTML')


def tram(bot, update, args):
    numposte = ' '.join(args)
    if numposte=='':
        bot.sendMessage(chat_id=update.message.chat_id, text="Uso: /tram &lt;númerodeposte&gt;\n\nEl número de poste se saca de la siguiente manera:\nSe pone el código de la parada y seguido el sentido (1 sentido Mago de Oz, 2 sentido Av. de la Academia).\n\nCódigos de parada:\nAvenida de la Academia: <b>10</b>\nParque Goya: <b>20</b>\nJuslibol: <b>30</b>\nCampus Río Ebro: <b>40</b>\nMargarita Xirgú/Antón García Abril: <b>50</b>\nLegaz Lacambra/Adolfo Aznar: <b>60</b>\nClara Campoamor/Pablo Neruda: <b>70</b>\nRosalía de Castro/León Felipe: <b>80</b>\nMartínez Soria/María Montessori: <b>90</b>\nLa Chimenea: <b>100</b>\nPlaza del Pilar-Murallas: <b>110</b>\nCésar Augusto: <b>120</b>\nPlaza España: <b>130</b>\nPlaza Aragón: <b>131</b>\nGran Vía: <b>140</b>\nFernando el Católico-Goya: <b>150</b>\nPlaza San Francisco: <b>160</b>\nPlaza Emperador Carlos V: <b>170</b>\nRomareda: <b>180</b>\nCasablanca: <b>190</b>\nArgualas: <b>200</b>\nLos Olvidados: <b>210</b>\nLos Pájaros: <b>230</b>\nLa Ventana Indiscreta: <b>232</b>\nCantando Bajo la Lluvia: <b>240</b>\nUn Americano en París: <b>242</b>\nMago de Oz: <b>250</b>", parse_mode='HTML')
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
        infotram = re.sub(r'.*"mensajes":\["',r'\n', textoleido)
        infotram = re.sub(r'","',r'\n', infotram)
        infotram = re.sub(r'"](\s|\S)*',r'', infotram)
        infotram = re.sub(r'\s?www.tranviasdezaragoza.es\s*Telefono Atencion al Cliente: 902 20 50 10',r'', infotram)
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
            f = urllib.request.urlopen('http://overpass-api.de/api/interpreter?data=[out%3Ajson][timeout%3A25]%3B%0Aarea(3600345740)-%3E.searchArea%3B%0A%0A(%0A%20%20node[%22railway%22%3D%22tram_stop%22][%22ref%22~%22^0*'+numposte+'$|^0*'+numposte+'\D|\D0*'+numposte+'$%22](area.searchArea)%3B)%3Bout%20body%3B%0A%3E%3B%0Aout%20skel%20qt%3B')
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
            imagen='\n<a href="https://commons.wikimedia.org/wiki/'+imagen+'">Imagen</a>'
        else:
            if re.search('["]mapillary["]: ["]',overpassleido):
                imagen=re.sub(r'[\s\S]*["]mapillary["]: ["]',r'', overpassleido)
                imagen=re.sub(r'["][\s\S]*',r'', imagen)
                imagen='\n<a href="https://www.mapillary.com/app/?pKey='+imagen+'&focus=photo">Imagen</a>'
        #Enviar mensaje
        bot.sendMessage(chat_id=update.message.chat_id, text='Parada '+numposte+name+imagen+'\n<a href="http://overpass-turbo.eu/map.html?Q=[out%3Ajson][timeout%3A25]%3B%0Aarea(3600345740)-%3E.searchArea%3B%0A%0A(%0A%20%20node[%22railway%22%3D%22tram_stop%22][%22ref%22~%22^0*'+numposte+'$|^0*'+numposte+'\D|\D0*'+numposte+'$%22](area.searchArea)%3B)%3Bout%20body%3B%0A%3E%3B%0Aout%20skel%20qt%3B%0A%7B%7Bstyle%3A%20%20%0Anode%5Brailway%3Dtram_stop%5D%7B%0A%20%20icon-width%3A%2020%3B%0A%20%20icon-image%3A%20url(%27http%3A%2F%2Fwww.zaragoza.es%2Fcontenidos%2Ficonos%2Ftranvia.png%27)%3B%0A%20%20text%3A%20name%3B%7D%20%20%7D%7D">Mapa</a>\n\n'+textoleido+infotram, parse_mode='HTML', disable_web_page_preview=True)
        f.close()

def mapatransporte(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='<a href="https://öpnvkarte.de/#-0.9033;41.6584;12">Mapa del transporte público en Zaragoza</a>', parse_mode='HTML', disable_web_page_preview=True)

def mapabici(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='<a href="http://bit.ly/Ziclabilidad">Mapa de la infraestructura ciclista en Zaragoza</a>', parse_mode='HTML', disable_web_page_preview=True)

def mapataxi(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='<a href="http://www.zaragoza.es/monitorTaxis/index.html">Mapa de las paradas de Taxi y taxis en tiempo real</a>', parse_mode='HTML', disable_web_page_preview=True)

def ruta(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='<a href="http://node1.idezar.es/RutometroIDEZarApp/rutometro.jsp?language=ES">Usar el calculador de rutas del Ayuntamiento</a>', parse_mode='HTML', disable_web_page_preview=True)


updater = Updater(#PONER TOKEN AQUÍ)#token de @tzgzbot para la API de Telegram

updater.dispatcher.add_handler(CommandHandler('bus', bus, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('tram', tram, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('linbus', linbus, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('lintram', lintram))
updater.dispatcher.add_handler(CommandHandler('mapatransporte', mapatransporte))
updater.dispatcher.add_handler(CommandHandler('mapabici', mapabici))
updater.dispatcher.add_handler(CommandHandler('mapataxi', mapataxi))
updater.dispatcher.add_handler(CommandHandler('ruta', ruta))

updater.start_polling()
updater.idle()
