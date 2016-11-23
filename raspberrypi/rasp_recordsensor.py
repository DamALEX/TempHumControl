#!/usr/bin/env python 
# -*- coding: UTF-8 -*-

# collecter les informations d'un capteur en précisant son numéro

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

#########################################################################

tempo = 59
heure = 3
jour = 32
fromaddr = « mail1@gmail.com"
toaddr = « mail2@hotmail.fr"

while 1:

  fichier = open("/home/pi/data/data.txt", "a")
  
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
  print maintenant.tm_mday
  
  if heure == maintenant.tm_hour:

    if jour != maintenant.tm_mday:

      msg = MIMEMultipart()

      msg['From'] = fromaddr
      msg['To'] = toaddr
      msg['Subject'] = "BD temp et hum "+time.strftime("%d/%m/%Y")

      body = "Voir en piece jointe"

      msg.attach(MIMEText(body, 'plain'))

      filename = "data.txt"
      attachment = open("/home/pi/data/data.txt", "rb")

      part = MIMEBase('application', 'octet-stream')
      part.set_payload((attachment).read())
      encoders.encode_base64(part)
      part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

      msg.attach(part)

      server = smtplib.SMTP('smtp.gmail.com', 587)
      server.starttls()
      server.login(fromaddr, "MotDePasse")
      text = msg.as_string()
      server.sendmail(fromaddr, toaddr, text)
      server.quit()

      jour = maintenant.tm_mday

      #newfichier = "/home/pi/data/data"+jour+".txt"
      #os.rename("/home/pi/data/data.txt", newfichier.strip())
      #os.remove("data.txt")

    else:

      print("Enregistrement déjà realisé aujourd'hui")

  else:

    print("Se n'est pas le moment d'enregistrer")