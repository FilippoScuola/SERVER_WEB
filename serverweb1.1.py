import socket
import threading
import yaml

PORT = 0
HOST = ""
CARTELLA = ""
routes = []
mime_types = {}
error_pages = {}


def carica_dati():
    
    try:
        with open("server_config.yaml","r") as file_configurazione:             
            dati = yaml.safe_load(file_configurazione)
            host = dati["server"]["host"]                           
            porta = dati["server"]["port"]                                      
            cartella = dati["static_dir"]                                        
            routes = dati["routes"]                                              
            mime_types = dati["mime_types"]
            error_pages = dati["error_pages"]
    except FileNotFoundError:                                                    
        print("Configurazione del server non trovata. Utilizzo valori base: host=any, porta=8080")
        host = ""                                                             
        porta = 8080                                                            

    return host,porta,cartella,routes,mime_types,error_pages   #restituisce i valori di 'host' e 'porta'

def get_mime(path):
    for estensione in mime_types.keys():                                         #itera tra le chiavi del dizionario 'mime_types' che sono le estensioni dei file
        if path.endswith(estensione):                                            #se il percorso del file ricercato termina con una delle estensioni presenti nel dizionario 'mime_types' 
            return mime_types[estensione]                                        #restituisce il valore associato a quella chiave che è il tipo mime del file

def gestisci_client(connessione):
    with connessione:                                                                     #gestisce la connessione
        messaggio = connessione.recv(1024).decode()                                       #messaggio inviato dal clien (GET / HTTP/1.1...)
       
        prima_riga = messaggio.split("\n")[0]                                             #prende la prima riga del messaggio che contiene il metodo(GET POST), il percorso(/, /about, /contatti) e la versione del protocollo(HTTP/1.1)
        path = prima_riga.split(" ")[1]                                                   #prende il percorso che è la seconda parola della prima riga del messaggio

        # cerca percorso del file richiesto nelle impostazioni del server
        file_richiesto = None
        for route in routes:
            if path == route["path"]:                                                   
                file_richiesto = route["file"]                                           
                break

        # caso in cui il percorso non esista perche l'utente ha richiesto un file non disponibile
        if file_richiesto is None:                                                            #se è stato trovato un file associato al percorso richiesto
            Not_found_404(connessione)
            return
        
        percorso = CARTELLA.lstrip("./") + "/" + file_richiesto                              #percorso del file completo es. 'public/contatti.html'

        #legge il file richiesto e lo invia
        try:
            with open(percorso, "rb") as f:
                contenuto = f.read()
            mime = get_mime(percorso)
            risposta = f"HTTP/1.1 200 OK\r\nContent-Type: {mime}\r\n\r\n".encode() + contenuto  #creazione della risposta
        except FileNotFoundError:
            Not_found_404(connessione)                               # file non trovato
            return
        
        connessione.sendall(risposta)                                                           #invia

def Not_found_404(connessione):
    percorso = CARTELLA.lstrip("./") + "/" + error_pages[404]
    
    with open(percorso,"rb" )as f:
        contenuto = f.read()
    mime = get_mime(percorso)
    risposta = f"HTTP/1.1 404 Not Found\r\nContent-Type: {mime}\r\n\r\n".encode() + contenuto
    connessione.sendall(risposta)
    
def main():
    global HOST, PORT, CARTELLA, routes, mime_types, error_pages
    HOST, PORT, CARTELLA, routes, mime_types, error_pages = carica_dati()                      #carica nella variabile globale 'HOST' e 'PORT' i valori restituiti dalla funzione 'carica_dati()'
 
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                    #creazione del socket del server
    server.bind((HOST,PORT))                                                      #associa il socket del server all'indirizzo e alla porta specificati
    server.listen(5)                                                              #accetta max 5 connessioni

    print(f"Server attivo su http://{HOST}:{PORT}")

    while True:
        connessione, indirizzo = server.accept()                              #gestisce la richiesta del client 
        print(f"Connessione da {indirizzo}")
        threading.Thread(target=gestisci_client, args=(connessione,), daemon=True).start() #processa la richiesta verso il client creando un thread

main()



