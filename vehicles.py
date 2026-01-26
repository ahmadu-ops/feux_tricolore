"""
vehicles.py - Gestion des véhicules
Projet Feu Tricolore - Ville de Thiès
"""

import turtle
import random
import math
from typing import List, Optional, Callable, Tuple
from dataclasses import dataclass, field

from scenarios import (
    EtatFeu, Scenario, Direction,
    get_config, ConfigScenario,
    COULEURS, COULEURS_VOITURES, DIMENSIONS,
    get_position_depart
)


@dataclass
class Voiture:
    """Représente un véhicule"""
    
    screen: turtle.TurtleScreen = field(repr=False)
    id: int
    direction: Direction
    x: float
    y: float
    vitesse: float = 0.0
    vitesse_max: float = 2.5
    acceleration: float = 0.15
    deceleration: float = 0.25
    couleur: str = "#3498DB"
    
    # États
    en_arret: bool = False
    a_passe_feu: bool = False
    dans_intersection: bool = False
    
    # Flags logging
    logged_arret: bool = False
    logged_redemarrage: bool = False
    
    # Turtle
    _turtle: turtle.RawTurtle = field(default=None, repr=False, compare=False)
    
    # Dimensions
    largeur: float = DIMENSIONS.voiture_largeur
    longueur: float = DIMENSIONS.voiture_longueur
    
    def __post_init__(self):
        if self.screen:
            self._turtle = turtle.RawTurtle(self.screen)
            self._turtle.hideturtle()
            self._turtle.speed(0)
            self._turtle.penup()
    
    def dessiner(self) -> None:
        """Dessine la voiture"""
        if not self._turtle:
            return
        
        t = self._turtle
        t.clear()
        
        angle = self.direction.angle
        cos_a = math.cos(math.radians(angle))
        sin_a = math.sin(math.radians(angle))
        
        # Corps principal
        self._dessiner_rectangle(
            self.x, self.y,
            self.longueur, self.largeur,
            angle, self.couleur
        )
        
        # Toit / cabine
        self._dessiner_rectangle(
            self.x - 3 * cos_a,
            self.y - 3 * sin_a,
            self.longueur * 0.5,
            self.largeur * 0.7,
            angle, self._assombrir(self.couleur)
        )
        
        # Pare-brise
        offset = self.longueur * 0.15
        self._dessiner_rectangle(
            self.x + offset * cos_a,
            self.y + offset * sin_a,
            8, self.largeur * 0.6,
            angle, '#AED6F1'
        )
        
        # Phares avant
        self._dessiner_phares(angle, avant=True)
        
        # Feux arrière
        self._dessiner_phares(angle, avant=False)
    
    def _dessiner_rectangle(self, cx: float, cy: float, 
                            longueur: float, largeur: float,
                            angle: float, couleur: str) -> None:
        """Dessine un rectangle orienté"""
        t = self._turtle
        coins = self._calculer_coins(cx, cy, longueur, largeur, angle)
        
        t.fillcolor(couleur)
        t.pencolor('#1A1A1A')
        t.pensize(1)
        
        t.goto(coins[0])
        t.pendown()
        t.begin_fill()
        for coin in coins[1:]:
            t.goto(coin)
        t.goto(coins[0])
        t.end_fill()
        t.penup()
    
    def _dessiner_phares(self, angle: float, avant: bool = True) -> None:
        """Dessine les phares"""
        t = self._turtle
        cos_a = math.cos(math.radians(angle))
        sin_a = math.sin(math.radians(angle))
        
        offset = (self.longueur / 2 - 2) * (1 if avant else -1)
        couleur = '#F1C40F' if avant else '#E74C3C'
        
        for side in [-1, 1]:
            px = self.x + offset * cos_a + side * (self.largeur/2 - 3) * cos_a
            py = self.y + offset * sin_a + side * (self.largeur/2 - 3) * sin_a
            
            # Ajustement perpendiculaire
            px += side * (self.largeur/2 - 4) * math.cos(math.radians(angle + 90))
            py += side * (self.largeur/2 - 4) * math.sin(math.radians(angle + 90))
            
            t.goto(px, py - 2)
            t.pendown()
            t.fillcolor(couleur)
            t.begin_fill()
            t.circle(2)
            t.end_fill()
            t.penup()
    
    def _calculer_coins(self, cx: float, cy: float,
                        longueur: float, largeur: float,
                        angle: float) -> List[Tuple[float, float]]:
        """Calcule les coins d'un rectangle orienté"""
        cos_a = math.cos(math.radians(angle))
        sin_a = math.sin(math.radians(angle))
        
        l2, w2 = longueur / 2, largeur / 2
        
        coins_locaux = [(-l2, -w2), (l2, -w2), (l2, w2), (-l2, w2)]
        
        coins = []
        for lx, ly in coins_locaux:
            rx = lx * cos_a - ly * sin_a + cx
            ry = lx * sin_a + ly * cos_a + cy
            coins.append((rx, ry))
        
        return coins
    
    def _assombrir(self, hex_color: str) -> str:
        """Assombrit une couleur"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = int(r * 0.7), int(g * 0.7), int(b * 0.7)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def deplacer(self) -> None:
        """Déplace la voiture"""
        dx, dy = self.direction.vecteur
        self.x += dx * self.vitesse
        self.y += dy * self.vitesse
    
    def accelerer(self) -> None:
        self.vitesse = min(self.vitesse_max, self.vitesse + self.acceleration)
    
    def freiner(self) -> None:
        self.vitesse = max(0, self.vitesse - self.deceleration)
    
    def distance_a_ligne_arret(self) -> float:
        """
        Distance à la ligne d'arrêt.
        Retourne une valeur positive si AVANT la ligne,
        négative si APRÈS (dans/passé l'intersection).
        """
        ligne = DIMENSIONS.ligne_arret
        
        if self.direction == Direction.NORD:
            return -ligne - self.y  # Ligne au sud, voiture va vers nord
        elif self.direction == Direction.SUD:
            return self.y - ligne  # Ligne au nord, voiture va vers sud
        elif self.direction == Direction.EST:
            return -ligne - self.x  # Ligne à l'ouest, voiture va vers est
        elif self.direction == Direction.OUEST:
            return self.x - ligne  # Ligne à l'est, voiture va vers ouest
        
        return 0
    
    def est_avant_ligne(self) -> bool:
        """Vérifie si la voiture est avant la ligne d'arrêt"""
        return self.distance_a_ligne_arret() > 0
    
    def est_dans_intersection(self) -> bool:
        """Vérifie si la voiture est dans l'intersection"""
        zone = DIMENSIONS.zone_intersection
        return abs(self.x) < zone and abs(self.y) < zone
    
    def est_hors_ecran(self) -> bool:
        limite = DIMENSIONS.limite_ecran
        return abs(self.x) > limite or abs(self.y) > limite
    
    def effacer(self) -> None:
        if self._turtle:
            self._turtle.clear()


class GestionnaireVoitures:
    """Gère tous les véhicules"""
    
    def __init__(self, screen: turtle.TurtleScreen = None, gestionnaire_feux=None):
        self.screen = screen
        self.gestionnaire_feux = gestionnaire_feux
        self.voitures: List[Voiture] = []
        self.compteur_id = 0
        self.scenario = Scenario.NORMAL
        self.config = get_config(Scenario.NORMAL)
        self.on_event_callback: Optional[Callable] = None
    
    def set_screen(self, screen: turtle.TurtleScreen) -> None:
        self.screen = screen
    
    def set_gestionnaire_feux(self, gf) -> None:
        self.gestionnaire_feux = gf
    
    def changer_scenario(self, scenario: Scenario) -> None:
        self.scenario = scenario
        self.config = get_config(scenario)
    
    def creer_voiture(self, direction: Direction = None) -> Optional[Voiture]:
        """Crée une nouvelle voiture"""
        if not self.screen:
            return None
        
        if len(self.voitures) >= self.config.max_voitures:
            return None
        
        if direction is None:
            direction = random.choice(list(Direction))
        
        x, y = get_position_depart(direction)
        
        # Vérifier collision au spawn
        if self._collision_spawn(x, y, direction):
            return None
        
        self.compteur_id += 1
        
        vitesse_max = self.config.vitesse_base + random.uniform(
            -self.config.vitesse_variation,
            self.config.vitesse_variation
        )
        
        voiture = Voiture(
            screen=self.screen,
            id=self.compteur_id,
            direction=direction,
            x=x,
            y=y,
            vitesse_max=vitesse_max,
            couleur=random.choice(COULEURS_VOITURES)
        )
        
        self.voitures.append(voiture)
        return voiture
    
    def _collision_spawn(self, x: float, y: float, direction: Direction) -> bool:
        """Vérifie collision au point de spawn"""
        dist_min = DIMENSIONS.distance_securite + DIMENSIONS.voiture_longueur
        
        for v in self.voitures:
            if v.direction == direction:
                dist = math.sqrt((v.x - x)**2 + (v.y - y)**2)
                if dist < dist_min:
                    return True
        return False
    
    def generer_aleatoire(self) -> Optional[Voiture]:
        """Génère une voiture aléatoirement"""
        if random.random() < self.config.freq_apparition:
            return self.creer_voiture()
        return None
    
    def update(self, dt: float) -> None:
        """Met à jour toutes les voitures"""
        if not self.gestionnaire_feux:
            return
        
        a_supprimer = []
        
        for voiture in self.voitures:
            etat_feu = self.gestionnaire_feux.get_etat_pour_direction(voiture.direction)
            
            # Logique d'arrêt
            doit_sarreter = self._doit_sarreter(voiture, etat_feu)
            voiture_devant = self._voiture_devant(voiture)
            
            if doit_sarreter or voiture_devant:
                voiture.freiner()
                
                if voiture.vitesse == 0 and not voiture.en_arret:
                    voiture.en_arret = True
                    if not voiture.logged_arret:
                        self._notifier('arret', voiture)
                        voiture.logged_arret = True
                        voiture.logged_redemarrage = False
            else:
                if voiture.en_arret:
                    voiture.en_arret = False
                    if not voiture.logged_redemarrage:
                        self._notifier('redemarrage', voiture)
                        voiture.logged_redemarrage = True
                        voiture.logged_arret = False
                
                voiture.accelerer()
            
            voiture.deplacer()
            
            # Marquer si dans intersection
            if voiture.est_dans_intersection():
                voiture.dans_intersection = True
            
            # Hors écran
            if voiture.est_hors_ecran():
                self._notifier('sortie', voiture)
                a_supprimer.append(voiture)
        
        for v in a_supprimer:
            v.effacer()
            self.voitures.remove(v)
    
    def _doit_sarreter(self, voiture: Voiture, etat_feu: EtatFeu) -> bool:
        """Détermine si la voiture doit s'arrêter"""
        
        # Si déjà dans l'intersection, continuer !
        if voiture.dans_intersection or voiture.a_passe_feu:
            return False
        
        # Distance à la ligne d'arrêt
        distance = voiture.distance_a_ligne_arret()
        
        # Si passé la ligne (distance négative), marquer et continuer
        if distance <= 0:
            voiture.a_passe_feu = True
            return False
        
        # Zone d'arrêt : doit s'arrêter si proche de la ligne
        zone_decision = DIMENSIONS.distance_securite + voiture.longueur
        
        # Feu rouge : s'arrêter si dans la zone
        if etat_feu == EtatFeu.ROUGE:
            if distance < zone_decision:
                return True
        
        # Feu orange : s'arrêter seulement si assez loin pour freiner
        elif etat_feu == EtatFeu.ORANGE:
            # Si très proche, continuer (ne peut plus s'arrêter à temps)
            if distance < 40:
                voiture.a_passe_feu = True
                return False
            if distance < zone_decision:
                return True
        
        # Feu vert ou clignotant : pas d'arrêt
        return False
    
    def _voiture_devant(self, voiture: Voiture) -> bool:
        """Vérifie s'il y a une voiture devant"""
        dist_secu = DIMENSIONS.distance_securite
        
        for autre in self.voitures:
            if autre.id == voiture.id:
                continue
            if autre.direction != voiture.direction:
                continue
            
            devant = False
            dist = 0
            
            if voiture.direction == Direction.NORD:
                if autre.y > voiture.y:
                    devant = True
                    dist = autre.y - voiture.y
            elif voiture.direction == Direction.SUD:
                if autre.y < voiture.y:
                    devant = True
                    dist = voiture.y - autre.y
            elif voiture.direction == Direction.EST:
                if autre.x > voiture.x:
                    devant = True
                    dist = autre.x - voiture.x
            elif voiture.direction == Direction.OUEST:
                if autre.x < voiture.x:
                    devant = True
                    dist = voiture.x - autre.x
            
            if devant and dist < dist_secu:
                return True
        
        return False
    
    def _notifier(self, event: str, voiture: Voiture) -> None:
        if self.on_event_callback:
            self.on_event_callback(event, voiture)
    
    def dessiner_toutes(self) -> None:
        for v in self.voitures:
            v.dessiner()
    
    def supprimer_toutes(self) -> None:
        for v in self.voitures:
            v.effacer()
        self.voitures.clear()
    
    def get_nombre(self) -> int:
        return len(self.voitures)
    
    def reinitialiser(self) -> None:
        self.supprimer_toutes()
        self.compteur_id = 0