#include <HTU21D.h>
#include <Wire.h>

const char* ssid = "Livebox-91a0";
const char* password = "342CCA469A9239DC967227DA6A";


HTU21D mySI7021;

// Créé le serveur Web en spécifiant le port TCP/IP
// 80 est le port par défaut pour HTTP
WiFiServer server(80);

// démarrage
void setup() {
  uint8_t mac[WL_MAC_ADDR_LENGTH];
  float temp;
  float humidity;

  // communication série 115200
  Serial.begin(115200);
  // petit pause
  delay(10);

  // Deux sauts de ligne pour faire le ménage car
  // le module au démarrage envoi des caractères sur le port série
  Serial.println();
  Serial.println();

  if (!mySI7021.begin(2, 0)) {
    Serial.println("Impossible de trouver un capteur SI7021 valide, vérifiez le câblage!");
    while (1);
  }
  
  humidity = mySI7021.readHumidity();          // Lecture de l'humidité en Pourcents
  Serial.print("Humidité: ");
  Serial.println(humidity);
  
  temp = mySI7021.readTemperature();     // Lecture de la température en Celsius
  Serial.print("Temperature: ");
  Serial.println(temp);
    
  if(WiFi.macAddress(mac) != 0) {
    for(int i=0; i<WL_MAC_ADDR_LENGTH; i++) {
//      Serial.print(mac[i],HEX);
      if(mac[i]<16) Serial.print ("0");
      Serial.print(mac[i],HEX);
      Serial.print((i < WL_MAC_ADDR_LENGTH-1) ? ":" : "\n");
    }
  }

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);

  Serial.print("Connexion a : ");
  Serial.println(ssid);  
  // Connexion au point d'accès
  WiFi.begin(ssid, password);
  
  // On boucle en attendant une connexion
  // Si l'état est WL_CONNECTED la connexion est acceptée
  // et on a obtenu une adresse IP
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  
  // Démarrage du serveur Web
  server.begin();
  Serial.println("Server started");

  // On affiche notre adresse IP
  Serial.println(WiFi.localIP());
}

// boucle principale
void loop() {
  float temp;
  float humidity;
  char strbuffertemp[10];
  char strbufferhum[10];
  
  // Est-ce qu'un client Web est connecté ?
  WiFiClient client = server.available();
  if (!client) {
    // non, on abandonne ici et on repart dans un tour de loop
    return;
  }
  
  // Un client est connecté
  Serial.println("new client");
  // On attend qu'il envoi des données
  while(!client.available()){
    delay(1);
  }
  
  // On récupère la ligne qu'il envoi jusqu'au premier retour chariot (CR)
  String req = client.readStringUntil('\r');
  // On affiche la ligne obtenue pour information
  Serial.println(req);
  // La ligne est récupérée, on purge 
  client.flush();
  
  // Test de la requête
  int val;
  // est-ce que le chemin dans la requête est "/gettemp" ?
  if (req.indexOf("/gettemp") != -1) {
    humidity = mySI7021.readHumidity();          // Lecture de l'humidité en Pourcents
  Serial.print("Humidité: ");
  Serial.println(humidity);
  
  temp = mySI7021.readHumidity();     // Lecture de la température en Celsus
  Serial.print("Temperature: ");
  Serial.println(temp);

  // C'est un autre chemin qui est demandé et il ne correspond à rien
  } else {
    // On signal que cette demande est invalide
    Serial.println("invalid request");
    // et on déconnecte le client du serveur Web
    client.stop();
    // et on repart dans un tour de boucle
    return;
  }

  // Peut-être le client a-t-il envoyé d'autres données,
  // mais nous purgeons la mémoire avant d'envoyer notre réponse
  client.flush();

  // Composition de la réponse à envoyer au client
  String s = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n";
  dtostrf(temp, 4, 3, strbuffertemp);
  dtostrf(humidity, 4, 3, strbufferhum);

  s += strbuffertemp;
  s += ";";
  s += strbufferhum;
  s += "\n";
  client.print(s);
  
  // petite pause
  delay(1);
  // et on le déconnecte du serveur Web
  Serial.println("Client disonnected");

}
