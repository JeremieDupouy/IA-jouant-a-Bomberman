# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 13:52:48 2018

@author: Laurent
"""
TEMPS_BASE = 1
TEMPS_PROPAGATION = 0.01
TEMPS_EXPLOSION = 5.5
TEMPS_PARTIE = 1000

E_INSTANT = 0
E_NATURE = 1

EVENEMENT_TOUR_JOUEUR = 1
EVENEMENT_EXPLOSION_BOMBE = 2
EVENEMENT_PROPAGATION = 3

PLATEAU_VIDE = 0
PLATEAU_PIERRE = 1
PLATEAU_BOIS = 2

DIRECTION_NORD = 0
DIRECTION_EST = 1
DIRECTION_SUD = 2
DIRECTION_OUEST = 3
DIRECTION_ATTENTE = 4

B_LIGNE = 0
B_COLONNE = 1
B_LONGUEURFLAMMES = 2
B_JOUEUR = 3
B_INSTANT = 4

J_LIGNE = 0
J_COLONNE = 1
J_DECISION = 2
J_VITESSE = 3
J_NOMBREBOMBES = 4
J_LONGUEURFLAMMES = 5
J_BOMBESRESTANTES = 6
J_DASHSRESTANTS = 7
J_PIEGESRESTANTS = 8
J_TOURSDASH = 9
J_PENALITE = 10

A_BOMBE = 1
A_DASH = 2
A_PIEGE = 3

POWERUP_VITESSE = 0
POWERUP_NOMBREBOMBES = 1
POWERUP_LONGUEURFLAMMES = 2
POWERUP_DASH = 3
POWERUP_PIEGE = 4

PU_LIGNE = 0
PU_COLONNE = 1
PU_NATURE = 2

P_LIGNE = 0
P_COLONNE = 1
P_JOUEUR = 2

from random import randrange
from copy import deepcopy
import subprocess
from tkinter import *
import os
try:
    from playsound import playsound
except ModuleNotFoundError:
    playsound = lambda _:()
from threading import Thread
import sys
import time

def attente(vitesse):
    return TEMPS_BASE * 0.9**vitesse
    
def cree_plateau_initial(lignes, colonnes, nombreDeTrous):
    plateau = [[PLATEAU_BOIS for i in range(colonnes+2)] for j in range(lignes+2)]
    for i in range(2, lignes+1,2):
        for j in range(2, colonnes+1, 2):
            plateau[i][j]=PLATEAU_PIERRE
    for i in range(0, lignes+2):
        plateau[i][0] = PLATEAU_PIERRE
        plateau[i][-1] = PLATEAU_PIERRE
        
    for j in range(0, colonnes+2):
        plateau[0][j] = PLATEAU_PIERRE
        plateau[-1][j] = PLATEAU_PIERRE
        
    plateau[1][1] = plateau[1][2] = plateau[2][1] = PLATEAU_VIDE
    plateau[1][-2] = plateau[1][-3] = plateau[2][-2] = PLATEAU_VIDE
    plateau[-2][1] = plateau[-2][2] = plateau[-3][1] = PLATEAU_VIDE
    plateau[-2][-2] = plateau[-2][-3] = plateau[-3][-2] = PLATEAU_VIDE
    
    for i in range(nombreDeTrous):
        i,j=0,0
        while plateau[i][j] != PLATEAU_BOIS:
            i=1+randrange(lignes)
            j=1+randrange(colonnes)
        plateau[i][j] = PLATEAU_VIDE
    return plateau

def affiche_powerup(canvas, couleurPowerup, j, k):
    # COULEURS_POWERUPS = ["cyan", "orangered", "red", "magenta", "purple"]
    if couleurPowerup == "orangered":
        canvas.create_oval(j*TAILLE_TUILE+TAILLE_TUILE*1/5, k*TAILLE_TUILE+TAILLE_TUILE*2/5, j*TAILLE_TUILE+TAILLE_TUILE-TAILLE_TUILE*1/5, k*TAILLE_TUILE+TAILLE_TUILE, fill=couleurPowerup)
        canvas.create_polygon(
            j*TAILLE_TUILE+TAILLE_TUILE/2-TAILLE_TUILE/15, k*TAILLE_TUILE+TAILLE_TUILE*7/10,
            j*TAILLE_TUILE+TAILLE_TUILE/2+TAILLE_TUILE/15, k*TAILLE_TUILE+TAILLE_TUILE*7/10,
            j*TAILLE_TUILE+TAILLE_TUILE/2+TAILLE_TUILE/15, k*TAILLE_TUILE+TAILLE_TUILE/15,
            j*TAILLE_TUILE+TAILLE_TUILE/2-TAILLE_TUILE/15, k*TAILLE_TUILE+TAILLE_TUILE/15,
            fill=couleurPowerup)
        #canvas.create_text((j+1)*TAILLE_TUILE+TAILLE_TUILE/2, (k+0.5)*TAILLE_TUILE, text=joueurs[i][J_NOMBREBOMBES])
    elif couleurPowerup == "red":
        canvas.create_polygon(
            j*TAILLE_TUILE+TAILLE_TUILE, k*TAILLE_TUILE+TAILLE_TUILE,
            j*TAILLE_TUILE, k*TAILLE_TUILE+TAILLE_TUILE,
            j*TAILLE_TUILE, k*TAILLE_TUILE+TAILLE_TUILE*(randrange(7))/10,
            j*TAILLE_TUILE+1*TAILLE_TUILE/6, k*TAILLE_TUILE+TAILLE_TUILE*(randrange(7))/10,
            j*TAILLE_TUILE+2*TAILLE_TUILE/6, k*TAILLE_TUILE+TAILLE_TUILE*(randrange(7))/10,
            j*TAILLE_TUILE+3*TAILLE_TUILE/6, k*TAILLE_TUILE+TAILLE_TUILE*(randrange(7))/10,
            j*TAILLE_TUILE+4*TAILLE_TUILE/6, k*TAILLE_TUILE+TAILLE_TUILE*(randrange(7))/10,
            j*TAILLE_TUILE+5*TAILLE_TUILE/6, k*TAILLE_TUILE+TAILLE_TUILE*(randrange(7))/10,
            j*TAILLE_TUILE+6*TAILLE_TUILE/6, k*TAILLE_TUILE+TAILLE_TUILE*(randrange(7))/10,
            outline="black", fill=couleurPowerup)
        #canvas.create_text((j+1)*TAILLE_TUILE+TAILLE_TUILE/2, (k+0.5)*TAILLE_TUILE, text=joueurs[i][J_LONGUEURFLAMMES])
    elif couleurPowerup == "cyan":
        canvas.create_polygon(
            j*TAILLE_TUILE+TAILLE_TUILE/10, k*TAILLE_TUILE+TAILLE_TUILE/10,
            j*TAILLE_TUILE+TAILLE_TUILE*2/5, k*TAILLE_TUILE+TAILLE_TUILE/10,
            j*TAILLE_TUILE+TAILLE_TUILE*2/5, k*TAILLE_TUILE+TAILLE_TUILE/2,
            j*TAILLE_TUILE+TAILLE_TUILE*9/10, k*TAILLE_TUILE+TAILLE_TUILE*7/10,
            j*TAILLE_TUILE+TAILLE_TUILE, k*TAILLE_TUILE+TAILLE_TUILE*9/10,
            j*TAILLE_TUILE+TAILLE_TUILE/10, k*TAILLE_TUILE+TAILLE_TUILE*9/10,
            outline="black", fill=couleurPowerup)
            #canvas.create_text((j+1)*TAILLE_TUILE+TAILLE_TUILE/2, (k+0.5)*TAILLE_TUILE, text=joueurs[i][J_VITESSE])
    elif couleurPowerup == "magenta":
        canvas.create_polygon(
            j*TAILLE_TUILE, k*TAILLE_TUILE,
            j*TAILLE_TUILE+TAILLE_TUILE*6/10, k*TAILLE_TUILE+TAILLE_TUILE/2,
            j*TAILLE_TUILE, k*TAILLE_TUILE+TAILLE_TUILE,
            fill=couleurPowerup)
        canvas.create_polygon(
            j*TAILLE_TUILE+TAILLE_TUILE*4/10, k*TAILLE_TUILE,
            j*TAILLE_TUILE+TAILLE_TUILE, k*TAILLE_TUILE+TAILLE_TUILE/2,
            j*TAILLE_TUILE+TAILLE_TUILE*4/10, k*TAILLE_TUILE+TAILLE_TUILE,
            fill=couleurPowerup)
        #canvas.create_text((j+1)*TAILLE_TUILE+TAILLE_TUILE/2, (k+0.5)*TAILLE_TUILE, text=joueurs[i][J_DASHSRESTANTS])             
    elif couleurPowerup == "purple":
        canvas.create_polygon(
            j*TAILLE_TUILE+TAILLE_TUILE*1/10, k*TAILLE_TUILE+TAILLE_TUILE*7/10,
            j*TAILLE_TUILE+TAILLE_TUILE*3/20, k*TAILLE_TUILE+TAILLE_TUILE*6/10,
            j*TAILLE_TUILE+TAILLE_TUILE/2, k*TAILLE_TUILE+TAILLE_TUILE*8/10,
            j*TAILLE_TUILE+TAILLE_TUILE*17/20, k*TAILLE_TUILE+TAILLE_TUILE*6/10,
            j*TAILLE_TUILE+TAILLE_TUILE*9/10, k*TAILLE_TUILE+TAILLE_TUILE*7/10,
            j*TAILLE_TUILE+TAILLE_TUILE/2, k*TAILLE_TUILE+TAILLE_TUILE*9/10,
            fill=couleurPowerup)

    canvas.create_polygon(j*TAILLE_TUILE, k*TAILLE_TUILE, j*TAILLE_TUILE+TAILLE_TUILE/(TAILLE_OVERLAY), k*TAILLE_TUILE, j*TAILLE_TUILE+TAILLE_TUILE/(TAILLE_OVERLAY), k*TAILLE_TUILE+TAILLE_TUILE, j*TAILLE_TUILE, k*TAILLE_TUILE+TAILLE_TUILE, fill="black")
    canvas.create_polygon(j*TAILLE_TUILE, k*TAILLE_TUILE, j*TAILLE_TUILE+TAILLE_TUILE, k*TAILLE_TUILE, j*TAILLE_TUILE+TAILLE_TUILE, k*TAILLE_TUILE+TAILLE_TUILE/(TAILLE_OVERLAY), j*TAILLE_TUILE, k*TAILLE_TUILE+TAILLE_TUILE/(TAILLE_OVERLAY), fill="black")
    canvas.create_polygon(j*TAILLE_TUILE+TAILLE_TUILE*(TAILLE_OVERLAY-1)/(TAILLE_OVERLAY), k*TAILLE_TUILE, j*TAILLE_TUILE+TAILLE_TUILE, k*TAILLE_TUILE, j*TAILLE_TUILE+TAILLE_TUILE, k*TAILLE_TUILE+TAILLE_TUILE, j*TAILLE_TUILE+TAILLE_TUILE*(TAILLE_OVERLAY-1)/(TAILLE_OVERLAY), k*TAILLE_TUILE+TAILLE_TUILE, fill="black")
    canvas.create_polygon(j*TAILLE_TUILE, k*TAILLE_TUILE+TAILLE_TUILE*(TAILLE_OVERLAY-1)/(TAILLE_OVERLAY), j*TAILLE_TUILE+TAILLE_TUILE, k*TAILLE_TUILE+TAILLE_TUILE*(TAILLE_OVERLAY-1)/(TAILLE_OVERLAY), j*TAILLE_TUILE+TAILLE_TUILE, k*TAILLE_TUILE+TAILLE_TUILE, j*TAILLE_TUILE, k*TAILLE_TUILE+TAILLE_TUILE, fill="black")

    for s in range(NOMBRE_SPARKS):
        xr = randrange(1, SIZE_SPARKS-1)
        yr = randrange(1, SIZE_SPARKS-1)
        canvas.create_polygon(
            j*TAILLE_TUILE+TAILLE_TUILE*xr/SIZE_SPARKS, k*TAILLE_TUILE+TAILLE_TUILE*yr/SIZE_SPARKS, 
            j*TAILLE_TUILE+TAILLE_TUILE*(xr+1)/SIZE_SPARKS, k*TAILLE_TUILE+TAILLE_TUILE*yr/SIZE_SPARKS, 
            j*TAILLE_TUILE+TAILLE_TUILE*(xr+1)/SIZE_SPARKS, k*TAILLE_TUILE+TAILLE_TUILE*(yr+1)/SIZE_SPARKS, 
            j*TAILLE_TUILE+TAILLE_TUILE*xr/SIZE_SPARKS, k*TAILLE_TUILE+TAILLE_TUILE*(yr+1)/SIZE_SPARKS, 
            fill="yellow")

def affiche_plateau(canvas, plateau, plateauCouleur, bombes, joueurs, powerups):
    #print('---------IN---------', file=sys.stderr)
    canvas.delete(ALL)
    
    for i in range(len(plateau)):
        for j in range(len(plateau[0])):
            if plateau[i][j]==PLATEAU_PIERRE:
                canvas.create_rectangle(j*TAILLE_TUILE, i*TAILLE_TUILE, j*TAILLE_TUILE+TAILLE_TUILE, i*TAILLE_TUILE+TAILLE_TUILE, fill="black")
            elif plateau[i][j]==PLATEAU_BOIS:
                canvas.create_rectangle(j*TAILLE_TUILE, i*TAILLE_TUILE, j*TAILLE_TUILE+TAILLE_TUILE, i*TAILLE_TUILE+TAILLE_TUILE, outline="black", fill="brown")
                canvas.create_polygon(
                    j*TAILLE_TUILE+OFFSET_CRATE, i*TAILLE_TUILE,
                    j*TAILLE_TUILE, i*TAILLE_TUILE,
                    j*TAILLE_TUILE, i*TAILLE_TUILE+OFFSET_CRATE,

                    j*TAILLE_TUILE+TAILLE_TUILE-OFFSET_CRATE, i*TAILLE_TUILE+TAILLE_TUILE,
                    j*TAILLE_TUILE+TAILLE_TUILE, i*TAILLE_TUILE+TAILLE_TUILE,
                    j*TAILLE_TUILE+TAILLE_TUILE, i*TAILLE_TUILE+TAILLE_TUILE-OFFSET_CRATE,
                    outline="black", fill="#94643E")
                canvas.create_polygon(
                    j*TAILLE_TUILE+TAILLE_TUILE-OFFSET_CRATE, i*TAILLE_TUILE,
                    j*TAILLE_TUILE+TAILLE_TUILE, i*TAILLE_TUILE,
                    j*TAILLE_TUILE+TAILLE_TUILE, i*TAILLE_TUILE+OFFSET_CRATE,

                    j*TAILLE_TUILE+OFFSET_CRATE, i*TAILLE_TUILE+TAILLE_TUILE,
                    j*TAILLE_TUILE, i*TAILLE_TUILE+TAILLE_TUILE,
                    j*TAILLE_TUILE, i*TAILLE_TUILE+TAILLE_TUILE-OFFSET_CRATE,
                    outline="black", fill="#94643E")
            else:
                if plateauCouleur[i][j]!=-1:
                    couleurJoueur = COULEURS_JOUEURS[plateauCouleur[i][j]]
                    canvas.create_rectangle(j*TAILLE_TUILE, i*TAILLE_TUILE, j*TAILLE_TUILE+TAILLE_TUILE, i*TAILLE_TUILE+TAILLE_TUILE, fill=couleurJoueur, outline = couleurJoueur)
                if trouve_objet(i,j, bombes)!=None:
                    canvas.create_oval(j*TAILLE_TUILE+5, i*TAILLE_TUILE+5, j*TAILLE_TUILE+TAILLE_TUILE-5, i*TAILLE_TUILE+TAILLE_TUILE-5, fill="cyan")
                if trouve_objet(i,j, joueurs)!=None:
                    couleurJoueur = COULEURS_JOUEURS[trouve_objet(i,j, joueurs)]
                    trace_bomberman(canvas, j*TAILLE_TUILE, i*TAILLE_TUILE, couleurJoueur)
                if trouve_objet(i,j, powerups)!=None:
                    couleurPowerup = COULEURS_POWERUPS[powerups[trouve_objet(i,j, powerups)][PU_NATURE]]
                    affiche_powerup(canvas, couleurPowerup, j, i)
                    #canvas.create_polygon(j*TAILLE_TUILE+TAILLE_TUILE/2, i*TAILLE_TUILE, j*TAILLE_TUILE, i*TAILLE_TUILE+TAILLE_TUILE/2, j*TAILLE_TUILE+TAILLE_TUILE/2, (i+1)*TAILLE_TUILE, (j+1)*TAILLE_TUILE, i*TAILLE_TUILE + TAILLE_TUILE/2, fill=couleurPowerup)
    #print('---------OUT---------', file=sys.stderr)

def trace_bomberman(canvas, x, y, couleur):
    canvas.create_oval(x+15, y+15, x+TAILLE_TUILE-15, y+TAILLE_TUILE, fill=couleur)
    canvas.create_oval(x+10, y, x+TAILLE_TUILE-10, y+TAILLE_TUILE-20, fill=couleur)
    canvas.create_oval(x+13, y+5, x+TAILLE_TUILE-13, y+TAILLE_TUILE-26, fill="pink")

def compte_couleur(grille, nbJoueurs):
    compteurs = [0 for i in range(nbJoueurs)]
    for ligne in grille:
        for couleur in ligne:
            if couleur >= 0:
                compteurs[couleur]+=1
    return compteurs

def ln_b(n, b):
    if(n < b):
        return 0
    else:
        return 1 + ln_b(n/b, b)

def affiche_empires(canvas, joueurs, plateauCouleur):
    scores = compte_couleur(plateauCouleur, len(joueurs))
    canvas.create_polygon(
        X0_EMPIRES, Y0_EMPIRES - Y_STEP_CLAIMS,
        X0_EMPIRES + X_LARGEUR_EMPIRES, Y0_EMPIRES - Y_STEP_CLAIMS,
        X0_EMPIRES + X_LARGEUR_EMPIRES, Y0_EMPIRES + Y_LARGEUR_EMPIRES,
        X0_EMPIRES, Y0_EMPIRES + Y_LARGEUR_EMPIRES,
    fill="black")
    for k in range(len(scores)):
        canvas.create_text(X0_EMPIRES + X_LARGEUR_EMPIRES/2, Y0_EMPIRES + k*Y_STEP_CLAIMS, text=str(scores[k]), fill=COULEURS_JOUEURS[k])

def affiche_infos(canvas, joueurs, plateauCouleur):
    #print('---------IN2---------', file=sys.stderr)
    canvas.delete(ALL)
    scores = list(reversed((sorted(zip(compte_couleur(plateauCouleur, len(joueurs)), range(len(joueurs)))))))
    for k in range(len(scores)):
        i = scores[k][1]
        if joueurs[i]!=None:
            couleur = COULEURS_JOUEURS[i]
            j=2
            couleurPowerup = COULEURS_POWERUPS[POWERUP_NOMBREBOMBES]
            canvas.create_oval(j*TAILLE_TUILE+TAILLE_TUILE*1/5, k*TAILLE_TUILE+TAILLE_TUILE*2/5, j*TAILLE_TUILE+TAILLE_TUILE-TAILLE_TUILE*1/5, k*TAILLE_TUILE+TAILLE_TUILE, fill=couleurPowerup)
            canvas.create_polygon(
                j*TAILLE_TUILE+TAILLE_TUILE/2-TAILLE_TUILE/15, k*TAILLE_TUILE+TAILLE_TUILE*7/10,
                j*TAILLE_TUILE+TAILLE_TUILE/2+TAILLE_TUILE/15, k*TAILLE_TUILE+TAILLE_TUILE*7/10,
                j*TAILLE_TUILE+TAILLE_TUILE/2+TAILLE_TUILE/15, k*TAILLE_TUILE+TAILLE_TUILE/15,
                j*TAILLE_TUILE+TAILLE_TUILE/2-TAILLE_TUILE/15, k*TAILLE_TUILE+TAILLE_TUILE/15,
                fill=couleurPowerup)
            canvas.create_text((j+1)*TAILLE_TUILE+TAILLE_TUILE/2, (k+0.5)*TAILLE_TUILE, text=joueurs[i][J_NOMBREBOMBES])
            j=4
            couleurPowerup = COULEURS_POWERUPS[POWERUP_LONGUEURFLAMMES]
            canvas.create_polygon(
                j*TAILLE_TUILE+TAILLE_TUILE, k*TAILLE_TUILE+TAILLE_TUILE,
                j*TAILLE_TUILE, k*TAILLE_TUILE+TAILLE_TUILE,
                j*TAILLE_TUILE, k*TAILLE_TUILE+TAILLE_TUILE*(randrange(7))/10,
                j*TAILLE_TUILE+1*TAILLE_TUILE/6, k*TAILLE_TUILE+TAILLE_TUILE*(randrange(7))/10,
                j*TAILLE_TUILE+2*TAILLE_TUILE/6, k*TAILLE_TUILE+TAILLE_TUILE*(randrange(7))/10,
                j*TAILLE_TUILE+3*TAILLE_TUILE/6, k*TAILLE_TUILE+TAILLE_TUILE*(randrange(7))/10,
                j*TAILLE_TUILE+4*TAILLE_TUILE/6, k*TAILLE_TUILE+TAILLE_TUILE*(randrange(7))/10,
                j*TAILLE_TUILE+5*TAILLE_TUILE/6, k*TAILLE_TUILE+TAILLE_TUILE*(randrange(7))/10,
                j*TAILLE_TUILE+6*TAILLE_TUILE/6, k*TAILLE_TUILE+TAILLE_TUILE*(randrange(7))/10,
                outline="black", fill=couleurPowerup)
            canvas.create_text((j+1)*TAILLE_TUILE+TAILLE_TUILE/2, (k+0.5)*TAILLE_TUILE, text=joueurs[i][J_LONGUEURFLAMMES])
            
            j=6
            couleurPowerup = COULEURS_POWERUPS[POWERUP_VITESSE]
            canvas.create_polygon(
                j*TAILLE_TUILE+TAILLE_TUILE/10, k*TAILLE_TUILE+TAILLE_TUILE/10,
                j*TAILLE_TUILE+TAILLE_TUILE*2/5, k*TAILLE_TUILE+TAILLE_TUILE/10,
                j*TAILLE_TUILE+TAILLE_TUILE*2/5, k*TAILLE_TUILE+TAILLE_TUILE/2,
                j*TAILLE_TUILE+TAILLE_TUILE*9/10, k*TAILLE_TUILE+TAILLE_TUILE*7/10,
                j*TAILLE_TUILE+TAILLE_TUILE, k*TAILLE_TUILE+TAILLE_TUILE*9/10,
                j*TAILLE_TUILE+TAILLE_TUILE/10, k*TAILLE_TUILE+TAILLE_TUILE*9/10,
                outline="black", fill=couleurPowerup)
            canvas.create_text((j+1)*TAILLE_TUILE+TAILLE_TUILE/2, (k+0.5)*TAILLE_TUILE, text=joueurs[i][J_VITESSE])
            
            j=8
            couleurPowerup = COULEURS_POWERUPS[POWERUP_DASH]
            canvas.create_polygon(
                j*TAILLE_TUILE, k*TAILLE_TUILE,
                j*TAILLE_TUILE+TAILLE_TUILE*6/10, k*TAILLE_TUILE+TAILLE_TUILE/2,
                j*TAILLE_TUILE, k*TAILLE_TUILE+TAILLE_TUILE,
                fill=couleurPowerup)
            canvas.create_polygon(
                j*TAILLE_TUILE+TAILLE_TUILE*4/10, k*TAILLE_TUILE,
                j*TAILLE_TUILE+TAILLE_TUILE, k*TAILLE_TUILE+TAILLE_TUILE/2,
                j*TAILLE_TUILE+TAILLE_TUILE*4/10, k*TAILLE_TUILE+TAILLE_TUILE,
                fill=couleurPowerup)
            canvas.create_text((j+1)*TAILLE_TUILE+TAILLE_TUILE/2, (k+0.5)*TAILLE_TUILE, text=joueurs[i][J_DASHSRESTANTS])             
            
            
            j=10
            couleurPowerup = COULEURS_POWERUPS[POWERUP_PIEGE]
            canvas.create_polygon(
                j*TAILLE_TUILE+TAILLE_TUILE*1/10, k*TAILLE_TUILE+TAILLE_TUILE*7/10,
                j*TAILLE_TUILE+TAILLE_TUILE*3/20, k*TAILLE_TUILE+TAILLE_TUILE*6/10,
                j*TAILLE_TUILE+TAILLE_TUILE/2, k*TAILLE_TUILE+TAILLE_TUILE*8/10,
                j*TAILLE_TUILE+TAILLE_TUILE*17/20, k*TAILLE_TUILE+TAILLE_TUILE*6/10,
                j*TAILLE_TUILE+TAILLE_TUILE*9/10, k*TAILLE_TUILE+TAILLE_TUILE*7/10,
                j*TAILLE_TUILE+TAILLE_TUILE/2, k*TAILLE_TUILE+TAILLE_TUILE*9/10,
                fill=couleurPowerup)
            canvas.create_text((j+1)*TAILLE_TUILE+TAILLE_TUILE/2, (k+0.5)*TAILLE_TUILE, text=joueurs[i][J_PIEGESRESTANTS])             
            
            j = 12
            canvas.create_text((j+1)*TAILLE_TUILE+TAILLE_TUILE/2, (k+0.5)*TAILLE_TUILE, text=joueurs[i][J_DECISION])             
        else:
            couleur = "gray"
        trace_bomberman(canvas, 0, HAUTEUR_JOUEUR*k,couleur)
    #print('---------OUT2---------', file=sys.stderr)


def ajoute_evenement(evenements, evenement):
    for i in range(0,len(evenements)):
        if evenement[0]<evenements[i][0]:
            evenements.insert(i,evenement)
            return
    evenements.append(evenement)
        
def prochain(i,j,direction):
    if direction == DIRECTION_NORD:
        i-=1
    elif direction == DIRECTION_SUD:
        i+=1
    elif direction == DIRECTION_OUEST:
        j-=1
    elif direction == DIRECTION_EST:
        j+=1
    return i,j

def trouve_objet(i,j, liste):
    for indice in range(len(liste)):
        if liste[indice]!=None and liste[indice][0]==i and liste[indice][1]==j:
            return indice

def casse(plateau, powerups, i,j):
    plateau[i][j]=PLATEAU_VIDE
    if randrange(0,BONUS_RANDMAX)==0:
        powerups.append([i,j, randrange(5)])
    return

def play_planks():
    try:
        playsound('./audio/wood.mp3')
    except:
        return
   
def execute_evenement(evenements, evenement, plateau, plateauCouleur, bombes, joueurs, powerups, pieges):
    if evenement[E_NATURE]==EVENEMENT_TOUR_JOUEUR:
        temps, nature, indiceJoueur = evenement
        joueur = joueurs[indiceJoueur]
        if joueur == None:
            return
        i, j = joueur[J_LIGNE], joueur[J_COLONNE]
        # en cas d'erreur quelconque, on considère que le joueur "passe" son tour
        direction,action = decision(joueur[J_DECISION],indiceJoueur, deepcopy(plateau), deepcopy(plateauCouleur), deepcopy(bombes), deepcopy(joueurs), deepcopy(powerups), evenement[E_INSTANT])
            
        if joueurs[indiceJoueur][J_BOMBESRESTANTES]>0 and action == A_BOMBE:
            joueur[J_BOMBESRESTANTES]-=1
            bombes.append([i,j,joueur[J_LONGUEURFLAMMES],indiceJoueur,evenement[0]+TEMPS_EXPLOSION])
            ajoute_evenement(evenements, [evenement[0]+TEMPS_EXPLOSION, EVENEMENT_EXPLOSION_BOMBE, len(bombes)-1])
        elif joueurs[indiceJoueur][J_DASHSRESTANTS]>0 and action == A_DASH:
            joueur[J_DASHSRESTANTS]-=1
            joueur[J_TOURSDASH]+=3
        elif joueurs[indiceJoueur][J_PIEGESRESTANTS]>0 and action == A_PIEGE:
            joueur[J_PIEGESRESTANTS]-=1
            pieges.append([i,j,indiceJoueur])
        ip,jp = prochain(i,j,direction)
        if plateau[ip][jp]==PLATEAU_VIDE and trouve_objet(ip, jp, bombes)==None:
            joueur[J_LIGNE]=ip
            joueur[J_COLONNE]=jp
        
        i, j = joueur[J_LIGNE], joueur[J_COLONNE]
        indicePiege = trouve_objet(i,j, pieges)
        penalite = 0
        if indicePiege != None:
            piege = pieges[indicePiege]
            if piege[P_JOUEUR] != indiceJoueur:
                penalite = 3
                pieges.pop(indicePiege)
                     
        indicePowerup = trouve_objet(i,j,powerups)
        if indicePowerup != None:
            powerup = powerups.pop(indicePowerup)
            if powerup[PU_NATURE]==POWERUP_LONGUEURFLAMMES:
                joueur[J_LONGUEURFLAMMES]+=1
            elif powerup[PU_NATURE]==POWERUP_NOMBREBOMBES:
                joueur[J_NOMBREBOMBES]+=1
                joueur[J_BOMBESRESTANTES]+=1
            elif powerup[PU_NATURE]==POWERUP_VITESSE:
                joueur[J_VITESSE]+=1
            elif powerup[PU_NATURE]==POWERUP_DASH:
                joueur[J_DASHSRESTANTS]+=1
            elif powerup[PU_NATURE]==POWERUP_PIEGE:
                joueur[J_PIEGESRESTANTS]+=1
        
        ajoute_evenement(evenements, [temps+attente(joueur[J_VITESSE])*(joueur[J_TOURSDASH]==0)+penalite, EVENEMENT_TOUR_JOUEUR, indiceJoueur])
        if joueur[J_TOURSDASH]>0:
            joueur[J_TOURSDASH]-=1
    elif evenement[E_NATURE]==EVENEMENT_EXPLOSION_BOMBE:
        temps, nature, indiceBombe = evenement
        if bombes[indiceBombe]==None:
            return
        
        
        i,j,longueurFlammes, indiceJoueur, instant = bombes[indiceBombe]
        indJoueur = bombes[indiceBombe][B_JOUEUR]
        bombes[indiceBombe] = None
        
        for direction in [DIRECTION_NORD, DIRECTION_SUD, DIRECTION_EST, DIRECTION_OUEST]:
            ajoute_evenement(evenements, [evenement[0], EVENEMENT_PROPAGATION, i, j, direction, longueurFlammes, indJoueur])
        if joueurs[indiceJoueur]!=None:
            joueurs[indiceJoueur][J_BOMBESRESTANTES]+=1
    elif evenement[E_NATURE]==EVENEMENT_PROPAGATION:
        temps, nature, i, j, direction, longueurFlammes, indJoueur = evenement
        if plateau[i][j]==PLATEAU_PIERRE:
            # Pierre : indestuctible donc pas d'effet
            return
        elif plateau[i][j]==PLATEAU_BOIS:
            # Bois : destructible, on détruit
            (Thread(target=play_planks)).start()
            casse(plateau, powerups, i,j)
            return
        else:
            # On colore la case avec la couleur du joueur
            plateauCouleur[i][j] = indJoueur
            # On détruit le powerup s'il y en a un                
            indicePowerup = trouve_objet(i,j,powerups)
            if indicePowerup != None:
                powerups.pop(indicePowerup)
                
            # On tue tous les joueurs qui sont à cet endroit
            indiceJoueur = trouve_objet(i,j,joueurs)
            while indiceJoueur != None:
                joueurs[indiceJoueur] = None
                print("\n--------------------------------------------------------------------------------------------------------\n\nDEATH (at time =", evenement[0], "):", indiceJoueur, "\n\n--------------------------------------------------------------------------------------------------------\n")
                #assert(false)
                indiceJoueur = trouve_objet(i,j,joueurs)
            
            # On fait exploser la bombe s'il y en a une
            indiceBombe = trouve_objet(i,j,bombes)            
            if indiceBombe != None:
                ajoute_evenement(evenements, [evenement[0],EVENEMENT_EXPLOSION_BOMBE, indiceBombe])
                longueurFlammes = 0
                
            # Si on est pas au bout de la flamme, on propage
            elif longueurFlammes>0:
                ip, jp = prochain(i,j,direction)
                ajoute_evenement(evenements, [evenement[0]+TEMPS_PROPAGATION, EVENEMENT_PROPAGATION, ip, jp, direction, longueurFlammes-1, indJoueur])
        
NB_TROUS = 120
BONUS_RANDMAX = 3 
# >0

TAILLE_TUILE = 40
HAUTEUR_JOUEUR = TAILLE_TUILE
LARGEUR_INFOS = 800
COULEURS_JOUEURS = ["red", "blue", "green", "yellow"]
COULEURS_POWERUPS = ["cyan", "orangered", "red", "magenta", "purple"]

OFFSET_CRATE = TAILLE_TUILE/25
TAILLE_OVERLAY = 15
NOMBRE_SPARKS = 10
SIZE_SPARKS = 12

X0_EMPIRES = 600
Y0_EMPIRES = 20
Y_STEP_CLAIMS = 40

X_LARGEUR_EMPIRES = 60
Y_LARGEUR_EMPIRES = 180

TIME_FACTOR = 15

def decision(programme, indiceJoueur, plateau, plateauCouleur, bombes, joueurs, powerups, instant):
    with open("entrees.txt", "w") as entrees:
        print(instant, file=entrees)
        print(indiceJoueur, file=entrees)
        print(len(plateau), len(plateau[0]), file=entrees)
        plateauTotal = [[plateau[i][j] if plateau[i][j]!=0 or plateauCouleur[i][j]==-1 else 3+plateauCouleur[i][j] for j in range(len(plateau[0]))] for i in range(len(plateau))]
        
        for ligne in plateauTotal:
            for val in ligne:
                print(val, end=" ", file=entrees)
            print(file=entrees)
        print(len(bombes)-bombes.count(None), file=entrees)
        for bombe in bombes:
            if bombe!=None:
                print(bombe[B_LIGNE], bombe[B_COLONNE], bombe[B_LONGUEURFLAMMES], bombe[B_INSTANT], file=entrees)
        print(len(joueurs)-joueurs.count(None), file=entrees)
        for j, joueur in enumerate(joueurs):
            if joueur!=None:
                print(joueur[J_LIGNE], joueur[J_COLONNE], j, joueur[J_VITESSE], joueur[J_BOMBESRESTANTES], joueur[J_LONGUEURFLAMMES], joueur[J_DASHSRESTANTS], joueur[J_PIEGESRESTANTS], file=entrees)
        print(len(powerups), file=entrees)
        for pu in powerups:
            print(pu[PU_LIGNE], pu[PU_COLONNE], pu[PU_NATURE], file=entrees)
    if os.name == "posix":
        #os.system("cat entrees.txt | "+programme+" > sortie.txt")
        subprocess.run("cat entrees.txt | "+programme+" > sortie.txt", shell=True)
    elif os.name =="nt":
        #os.system('type entrees.txt | python '+programme[2:]+ ' >sortie.txt')
        subprocess.run('type entrees.txt | python '+programme[2:]+ ' >sortie.txt', shell=True)

    with open("sortie.txt", "r") as sortie:
        direction, b = sortie.readline().split()
        action = int(b)

    with open("signal.txt", "w") as sign:
        print("1", file=sign)

    return int(direction), action

def graphing():
    try:
        subprocess.run("./graphs")
    except:
        pass

def simulation(strategies):
    def pas_de_jeu():
        if len(joueurs) - joueurs.count(None) > 0:
            #st = time.time()
            evenement = evenements.pop(0)
            if evenement[0]>TEMPS_PARTIE:
                return
            execute_evenement(evenements, evenement, plateau, plateauCouleur, bombes, joueurs, powerups, pieges)
            affiche_plateau(canvas, plateau, plateauCouleur, bombes, joueurs, powerups)
            affiche_infos(canvasInfosJoueurs, joueurs, plateauCouleur)
            #affiche_empires(canvasInfosJoueurs, joueurs, plateauCouleur) # very laggy for some reason # not anymore
            temps = int(1000*(evenements[0][0]-evenement[0])/TIME_FACTOR)
            #print(1000*(evenements[0][0]-evenement[0])/TIME_FACTOR, " <--> ", temps)
            # not here
            if temps != 0:
                fenetre.after(temps, pas_de_jeu)
                #en = time.time()
                #print("------------------- : ", en-st) 
            else:
                canvas.pack()
                pas_de_jeu()
                
    dimensions = 13,21
    positionsInitiales=[(1, 1), (dimensions[0]-2, dimensions[1]-2), (1, dimensions[1]-2), (dimensions[0]-2, 1)]
    
    plateau = cree_plateau_initial(dimensions[0]-2, dimensions[1]-2, NB_TROUS)
    plateauCouleur = [[-1 for j in range(dimensions[1])] for i in range(dimensions[0])]
    
    evenements = []
    
    bombes = []
    joueurs = []
    powerups = []
    pieges = []
    
    fenetre = Tk()
    canvas = Canvas(width=dimensions[1]*TAILLE_TUILE, height=dimensions[0]*TAILLE_TUILE)
    canvas.pack()
    
    joueurs = []
    
    for i in range(len(strategies)):
        joueur = [positionsInitiales[i][0], positionsInitiales[i][1], strategies[i], 0, 1, 1, 1, 1, 0, 0, 0]
        joueurs.append(joueur)
        ajoute_evenement(evenements, [0., EVENEMENT_TOUR_JOUEUR, i])
    
    canvasInfosJoueurs = Canvas(width = LARGEUR_INFOS, height=len(joueurs)*HAUTEUR_JOUEUR)
    canvasInfosJoueurs.pack()

    (Thread(target=graphing)).start()
    
    pas_de_jeu()

    fenetre.mainloop()
    return 

#simulation(["./again"])
#simulation(["./again", "./again"])
simulation(["./iachallenge2024_bomberman_base.py", "./iachallenge2024_bomberman_base.py", "./iachallenge2024_bomberman_base.py", "./iachallenge2024_bomberman_base.py"])
