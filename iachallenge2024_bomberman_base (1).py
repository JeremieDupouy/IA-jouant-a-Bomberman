#!/usr/bin/python3

# Les constantes du jeu
TEMPS_BASE = 1
TEMPS_PROPAGATION = 0.01
TEMPS_EXPLOSION = 5.5
TEMPS_PARTIE = 100

E_TEMPS = 0
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

# Lecture des entrées
instant = float(input())
indiceMoi = int(input())
hauteur, largeur = map(int, input().split())
grille = []
for i in range(hauteur):
    grille.append(list(map(int,input().split())))

nbBombes = int(input())
bombes = []
for i in range(nbBombes):
    ligne = input().split()
    bombes.append([int(ligne[0]), int(ligne[1]), int(ligne[2]), float(ligne[2])])

nbJoueurs = int(input())
joueurs = [None]*4
for i in range(nbJoueurs):
    joueur = list(map(int, input().split()))
    joueurs[joueur.pop(2)] = joueur

nbPowerups = int(input())
powerups = []
for i in range(nbPowerups):
    powerups.append(list(map(int,input().split())))

# Ecriture de la décision 
from random import randrange
print(randrange(5), 0)