#!/usr/bin/env python 
# -*- coding: UTF-8 -*-

# Programme pour collecter la température ou/et l’humidité de 5 capteurs
# Sauvegarde des données dans un fichier txt et envoi le ficher par courriel

############################################################################

from types import *
import os
import sys
import time
import requests
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders

############################################################################

# Fonction pour collecter les informations d'un capteur en précisant son numéro

def collect(capteur, lieu):
  try:
    r = requests.get("http://192.168.1."+capteur+"/gettemp", timeout=2)
  except requests.exceptions.Timeout:
    tram = time.strftime("%d/%m/%Y;%H:%M:%S")+";capteur"+capteur+";"+lieu+";Noresponse;Noresponse;\n"
  except:
    tram = time.strftime("%d/%m/%Y;%H:%M:%S")+";capteur"+capteur+";"+lieu+";Error;Error;\n"
  else:
    r = r.content.rstrip()
    tram = time.strftime("%d/%m/%Y;%H:%M:%S")+";capteur"+capteur+";"+lieu+";"+r+";\n"
  
  return tram

############################################################################

############################################################################

# Fonction pour convertir la date

def convdate(mois , annee):
    
    convmois = {'1':'decembre' , '2':'janvier' , '3':'fevrier' , '4':'mars' , '5':'avril' , '6':'mai' , '7':'juin' , '8':'juillet' , '9':'aout' , '10':'septembre' , '11':'octobre' , '12':'novembre'}

    if mois == 1:
        annee = annee - 1
 
    mois = str(mois)
    mois = convmois[mois]

    texte = '_'+mois+str(annee)
  
    return texte

############################################################################

tempo = 59
heure = 0
jour = 32
mois = 13
annee = 1985
fromaddr = "mail1@gmail.com"
toaddr = "mail2@hotmail.fr"
motdepasse = "motdepasse"
addrdata = "/home/pi/data/data.txt" 

while 1:

  fichier = open(addrdata , "a")
  
  txt = collect('30', 'exterieur')
  print txt
  fichier.write(txt)
  
  time.sleep(tempo)

  txt = collect('31', 'rdc')
  print txt
  fichier.write(txt)
  
  time.sleep(tempo) 

  txt = collect('35', 'etage')
  print txt
  fichier.write(txt)
  
  time.sleep(tempo)

  txt = collect('36', 'veranda')
  print txt
  fichier.write(txt)
  
  time.sleep(tempo)

  txt = collect('37', 'garage')
  print txt
  fichier.write(txt)
  
  time.sleep(tempo)

  fichier.close()

  maintenant = time.localtime()

  print maintenant.tm_hour
  
  if heure == maintenant.tm_hour:

    print maintenant.tm_mday	

    if jour != maintenant.tm_mday:

      msg = MIMEMultipart()

      msg['From'] = fromaddr
      msg['To'] = toaddr
      msg['Subject'] = "BD temp et hum "+time.strftime("%d/%m/%Y")

      body = "Voir en piece jointe"

      msg.attach(MIMEText(body, 'plain'))

      filename = "data.txt"
      attachment = open(addrdata , "rb")

      part = MIMEBase('application', 'octet-stream')
      part.set_payload((attachment).read())
      encoders.encode_base64(part)
      part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

      msg.attach(part)

      server = smtplib.SMTP('smtp.gmail.com', 587)
      server.starttls()
      server.login(fromaddr, motdepasse)
      text = msg.as_string()
      server.sendmail(fromaddr, toaddr, text)
      server.quit()
      attachment.close()

      jour = maintenant.tm_mday

      print maintenant.tm_mon

      if mois != maintenant.tm_mon:

        mois = maintenant.tm_mon
        annee = maintenant.tm_year
            
        texte = convdate(mois , annee)

        newfichier = "data"+texte+".txt"
        os.rename(addrdata, newfichier.strip())
        fichier = open(addrdata, "a")
        fichier.close()

      else:

        print("Changement de nom déjà réalisé dans ce mois")

    else:

      print("Enregistrement déjà realisé aujourd'hui")

  else:

    print("Ce n'est pas le moment d'enregistrer")