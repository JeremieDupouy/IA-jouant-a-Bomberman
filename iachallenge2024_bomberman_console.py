# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 13:52:48 2018

@author: Laurent
"""
TEMPS_BASE = 1
TEMPS_PROPAGATION = 0.001
TEMPS_EXPLOSION = 5.5
TEMPS_PARTIE = 400

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

from random import randrange, sample
from copy import deepcopy
import sys
import os
import subprocess
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
            #print("||||| trap at", i, j, "|||||")
       
        i, j = joueur[J_LIGNE], joueur[J_COLONNE]
        indicePiege = trouve_objet(i,j, pieges)
        penalite = 0
        if indicePiege != None:
            piege = pieges[indicePiege]
            if piege[P_JOUEUR] != indiceJoueur:
                penalite = 3
                #print("[CONSOLE]", indiceJoueur, "has triggered", piege[P_JOUEUR], "'s trap (at", i, j, "), time =", temps, ")")
                pieges.pop(indicePiege)

        ip,jp = prochain(i,j,direction)
        if plateau[ip][jp]==PLATEAU_VIDE and trouve_objet(ip, jp, bombes)==None and penalite==0:
            #print(joueur[J_LIGNE], joueur[J_COLONNE], "--->", ip, jp)
            joueur[J_LIGNE]=ip
            joueur[J_COLONNE]=jp
        #else:
            #print("still")
                     
        i, j = joueur[J_LIGNE], joueur[J_COLONNE]
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
                #print("[CONSOLE] DEATH (time =", evenement[0], "):", indiceJoueur, "\n")
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
        
NB_TROUS = 10
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

TIME_FACTOR = 7

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
        subprocess.run("rm sortie.txt && cat entrees.txt | timeout 2 "+programme+" > sortie.txt", shell=True)
    try:
        with open("sortie.txt", "r") as sortie:
            direction, action = sortie.readline().split()
            return int(direction), int(action)
    except:
        print(programme, "n'a pas répondu correctement")
        return 4, 0

def affiche_plateau(plateau, plateauCouleur, bombes, joueurs, powerups):
    symboles = {
        0: " ",  # Case vide
        1: "█",  # Mur incassable (█)
        2: "▒"   # Mur cassable (▓)
    }

    # Symboles pour les éléments dynamiques
    symbole_bombe = "B"
    symbole_joueur = "J"
    symbole_powerups = {
        0: "S",  # Vitesse (Speed)
        1: "N",  # Nombre de bombes (Number)
        2: "F",  # Longueur des flammes (Flames)
        3: "D",  # Dash
        4: "P"   # Piège (Trap)
    }

    # Couleurs pour les cases revendiquées
    couleurs_joueurs = [
        "\033[41m",  # Rouge pour le joueur 0
        "\033[42m",  # Vert pour le joueur 1
        "\033[44m",  # Bleu pour le joueur 2
        "\033[43m",  # Jaune pour le joueur 3
        "\033[45m"   # Magenta pour le joueur 4
    ]
    couleur_reset = "\033[0m"

    # Crée une copie du plateau pour y ajouter les éléments dynamiques
    plateau_affichage = [[symboles.get(case, "?") for case in ligne] for ligne in plateau]

    # Place les bombes
    if bombes:
        for bombe in bombes:
            if bombe!=None:
                ligne, colonne = bombe[:2]
                plateau_affichage[ligne][colonne] = symbole_bombe

    # Place les joueurs
    if joueurs:
        for joueur in joueurs:
            if joueur!=None:
                ligne, colonne = joueur[:2]
                plateau_affichage[ligne][colonne] = symbole_joueur

    # Place les power-ups
    if powerups:
        for powerup in powerups:
            ligne, colonne, type_powerup = powerup[:3]
            plateau_affichage[ligne][colonne] = symbole_powerups.get(type_powerup, "?")

    # Affiche le plateau avec bordures et couleurs des cases revendiquées
    print("\n" + "-" * (len(plateau[0]) * 2 + 1))  # Bordure supérieure
    for i, ligne in enumerate(plateau_affichage):
        print("|", end="")  # Bordure gauche
        for j, case in enumerate(ligne):
            if plateauCouleur[i][j] != -1 and plateau[i][j] == 0:  # Case vide revendiquée
                joueur = plateauCouleur[i][j]
                couleur = couleurs_joueurs[joueur % len(couleurs_joueurs)]
                print(f"{couleur}{case}{couleur_reset}", end=" ")
            else:
                print(case, end=" ")
        print("|")  # Bordure droite
    print("-" * (len(plateau[0]) * 2 + 1))  # Bordure inférieure
    
def simulation(strategies):
    dimensions = 13,21
    positionsInitiales=[(1, 1), (dimensions[0]-2, dimensions[1]-2), (1, dimensions[1]-2), (dimensions[0]-2, 1)]
    
    plateau = cree_plateau_initial(dimensions[0]-2, dimensions[1]-2, NB_TROUS)
    plateauCouleur = [[-1 for j in range(dimensions[1])] for i in range(dimensions[0])]
    
    evenements = []
    
    bombes = []
    joueurs = []
    powerups = []
    pieges = []
    
    joueurs = []
    
    for i in range(len(strategies)):
        joueur = [positionsInitiales[i][0], positionsInitiales[i][1], strategies[i], 0, 1, 1, 1, 0, 0, 0, 0]
        joueurs.append(joueur)
        ajoute_evenement(evenements, [0., EVENEMENT_TOUR_JOUEUR, i])
    
    while len(joueurs) - joueurs.count(None) > 0:
        evenement = evenements.pop(0)
        if evenement[0]>TEMPS_PARTIE:
            break
        execute_evenement(evenements, evenement, plateau, plateauCouleur, bombes, joueurs, powerups, pieges)
        if evenement[E_NATURE]==EVENEMENT_TOUR_JOUEUR:
            affiche_plateau(plateau, plateauCouleur, bombes, joueurs, powerups)
    
    scores = [0]*4
    for i in range(len(plateauCouleur)):
        for j in range(len(plateauCouleur[0])):
            if plateauCouleur[i][j]>=0:
                scores[plateauCouleur[i][j]]+=1
    return scores

simulation(["./ia_lj.py"]*2)

def proba_gain(ecart):
    return 1/(1+10**(-ecart/400))

def tournois(strategies, n=150):
    # attribution d'un dossard
    print(strategies)
    numeros = {strat:i for i, strat in enumerate(strategies)}
    
    # initialisation des scores pour le classement elo
    scores = [1000 for i in range(len(strategies))]
    manches = 0
    while manches < n:
        oldScores = scores.copy()
        manches += 1
        selection =sample(list(range(len(participants))),4)
        strats = [strategies[k] for k in selection]
        print("Participants :")
        print(*strats, sep="\n")
        
        scoresFinaux = simulation(strats)
        
        print("Scores :")
        print(*zip(strats, scoresFinaux), sep="\n")
                
        ecart = [[0 for j in range(4)] for i in range(4)]
        for i in range(len(selection)):
            for j in range(i):
                ecart[i][j] = (oldScores[selection[j]]-oldScores[selection[i]])
        for i in range(len(selection)):
            for j in range(i):
                if scoresFinaux[j] > scoresFinaux[i]:
                    resultat = 1
                elif scoresFinaux[j] < scoresFinaux[i]:
                    resultat = 0
                else:
                    resultat = 0.5
                gain =  10*(resultat - proba_gain(ecart[i][j]))
                scores[selection[i]]-= gain
                scores[selection[j]]+= gain

        print("Classement après", manches, "manches")
        print(*sorted([(scores[k],strategies[k]) for k in range(len(participants))]), sep="\n")

participants = [
    "./ia_alexandre",
    "./ia_arthur",
    "./ia_lj.py",
    "./ia_lj2.py",
    "./ia_alexian",
    "./ia_romain.py",
    "./ia_adrien",
    "./ia_evelyn"
    ]
#tournois(participants)
