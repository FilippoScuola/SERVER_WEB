import http.server
import socketserver
import threading
import yaml

PORT = 0
HOST = ""
CARTELLA = ""
routes = []


def carica_dati():
    
    try:
        
        with open("server_config.yaml","r") as file_configurazione:              #apre il file 'server_config.yaml' in modalità lettura come 'file_configurazione'
            dati = yaml.safe_load(file_configurazione)                           #carica i 'dati' del file yaml nella variabile 'dati' che è di type dizionario
            host = dati["server"]["host"]                                        #carica nella variabile 'host' il valore dell'host specificato nel file yaml
            porta = dati["server"]["port"]                                       #carica nella variabile 'porta' il valore della porta specificata nel file yaml
            cartella = dati["static_dir"]                                        #carica nella variabile 'cartella' il valore della cartella specificata nel file yaml
            routes = dati["routes"]                                              #carica nella variabile 'routes' la lista dei percorsi specificate nel file yaml
    
    except FileNotFoundError:                                                    #gestisce l'eccezzione nel caso il file 'server_config.yaml' non venga trovato e assegna dei valori di default a host e porta in modo che il server possa funzionare comunque
        print("Configurazione del server non trovata. Utilizzo valori base: host=any, porta=8080")
        host = ""                                                                #assegna alla variabile 'host' una valore della porta qualsiasi
        porta = 8080                                                             #assegna alla variabile 'porta' il valore 8080

    return host,porta,cartella,routes   #restituisce i valori di 'host' e 'porta'

def handler(CARTELLA,routes):
    
    class CustomHandler(http.server.SimpleHTTPRequestHandler):                     #crea una classe derivata ereditata dalla classe 'SimpleHTTPRequestHandler' che gestisce le richieste HTTP 
        def do_GET(self):                                                          #sovrascrive il metodo 'do_GET' della classe 'SimpleHTTPRequestHandler' in modo da poter gestire le richieste delle pagine about e contatti
            for route in routes:                                                   #itera la lista di dizionari delle routes
                if self.path == route["path"]:                                     #quando trova la route che corrisponde al percorso richiesto dal client
                    self.path = "/" + CARTELLA.lstrip("./") + "/" + route["file"]  #crea il percorso del file di tipo /public/pagina_richiesta
                    super().do_GET()                                               #chiama il metodo 'do_GET' della classe 'SimpleHTTPRequestHandler' 
                    return                                                         #esce dal ciclo for perche ha soddisfatto la richiesta
            self.send_error(404, "File non trovato")                               #se non trova la pagina invia una errore
    return CustomHandler

def main():
    
    HOST, PORT, CARTELLA, routes = carica_dati()                                   #carica nella variabile globale 'HOST' e 'PORT' i valori restituiti dalla funzione 'carica_dati()'
 
    
    Handler = handler(CARTELLA,routes)                                             #gestisce cosa fare quando arriva una richiesta
    httpd = socketserver.TCPServer((HOST,PORT), Handler)                          #creazione del server su porta 8080 e su indirizzo qualsiasi
    
    print(f"Server attivo su http://{HOST}:{PORT}")

    while True:
        richiesta, indirizzo = httpd.get_request()                                 #gestisce la richiesta del client 
        print(f"Connessione da {indirizzo}")
        threading.Thread(target=httpd.process_request, args=(richiesta, indirizzo), daemon=True).start() #processa la richiesta verso il client creando un thread




main()




#implementare interruzione con ctrl c