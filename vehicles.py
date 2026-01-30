"""
vehicles.py - Véhicules réalistes (sans ombres)
Projet Feu Tricolore - Ville de Thiès
"""

import turtle
import random
import math
from typing import List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum

from scenarios import (
    EtatFeu, Scenario, Direction,
    get_config,
    COULEURS_VOITURES, DIMENSIONS,
    get_position_depart
)


class TypeVehicule(Enum):
    """Types de véhicules"""
    BERLINE = "berline"
    SUV = "suv"
    COMPACT = "compact"


@dataclass
class Voiture:
    """Véhicule réaliste"""
    
    screen: turtle.TurtleScreen = field(repr=False)
    id: int
    direction: Direction
    x: float
    y: float
    
    type_vehicule: TypeVehicule = TypeVehicule.BERLINE
    couleur: str = "#3498DB"
    
    vitesse: float = 0.0
    vitesse_max: float = 2.5
    acceleration: float = 0.12
    deceleration: float = 0.20
    
    en_arret: bool = False
    a_passe_feu: bool = False
    dans_intersection: bool = False
    
    logged_arret: bool = False
    logged_redemarrage: bool = False
    
    _turtle: turtle.RawTurtle = field(default=None, repr=False, compare=False)
    
    def __post_init__(self):
        if self.screen:
            self._turtle = turtle.RawTurtle(self.screen)
            self._turtle.hideturtle()
            self._turtle.speed(0)
            self._turtle.penup()
        
        self._set_dimensions()
    
    def _set_dimensions(self) -> None:
        """Dimensions selon le type"""
        dims = {
            TypeVehicule.BERLINE: (42, 22),
            TypeVehicule.SUV: (48, 26),
            TypeVehicule.COMPACT: (35, 20),
        }
        self.longueur, self.largeur = dims.get(self.type_vehicule, (42, 22))
    
    def dessiner(self) -> None:
        """Dessine le véhicule"""
        if not self._turtle:
            return
        
        angle = self.direction.angle
        self._turtle.clear()
        
        self._dessiner_corps(angle)
        self._dessiner_toit(angle)
        self._dessiner_vitres(angle)
        self._dessiner_phares(angle)
    
    def _dessiner_corps(self, angle: float) -> None:
        """Corps principal"""
        t = self._turtle
        
        coins = self._calculer_coins(self.x, self.y, self.longueur, self.largeur, angle)
        
        t.fillcolor(self.couleur)
        t.pencolor('#1A1A1A')
        t.pensize(2)
        
        t.goto(coins[0])
        t.pendown()
        t.begin_fill()
        for coin in coins[1:]:
            t.goto(coin)
        t.goto(coins[0])
        t.end_fill()
        t.penup()
    
    def _dessiner_toit(self, angle: float) -> None:
        """Toit / cabine"""
        t = self._turtle
        cos_a = math.cos(math.radians(angle))
        sin_a = math.sin(math.radians(angle))
        
        toit_offset = -self.longueur * 0.08
        toit_x = self.x + toit_offset * cos_a
        toit_y = self.y + toit_offset * sin_a
        
        toit_longueur = self.longueur * 0.4
        toit_largeur = self.largeur * 0.7
        
        coins = self._calculer_coins(toit_x, toit_y, toit_longueur, toit_largeur, angle)
        
        t.fillcolor(self._assombrir(self.couleur, 0.75))
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
    
    def _dessiner_vitres(self, angle: float) -> None:
        """Vitres avant et arrière"""
        t = self._turtle
        cos_a = math.cos(math.radians(angle))
        sin_a = math.sin(math.radians(angle))
        
        # Pare-brise
        offset = self.longueur * 0.15
        vx = self.x + offset * cos_a
        vy = self.y + offset * sin_a
        
        coins = self._calculer_coins(vx, vy, 5, self.largeur * 0.55, angle)
        
        t.fillcolor('#87CEEB')
        t.pencolor('#5DADE2')
        t.pensize(1)
        
        t.goto(coins[0])
        t.pendown()
        t.begin_fill()
        for coin in coins[1:]:
            t.goto(coin)
        t.goto(coins[0])
        t.end_fill()
        t.penup()
        
        # Vitre arrière
        offset = -self.longueur * 0.25
        vx = self.x + offset * cos_a
        vy = self.y + offset * sin_a
        
        coins = self._calculer_coins(vx, vy, 4, self.largeur * 0.5, angle)
        
        t.goto(coins[0])
        t.pendown()
        t.begin_fill()
        for coin in coins[1:]:
            t.goto(coin)
        t.goto(coins[0])
        t.end_fill()
        t.penup()
    
    def _dessiner_phares(self, angle: float) -> None:
        """Phares et feux arrière"""
        t = self._turtle
        cos_a = math.cos(math.radians(angle))
        sin_a = math.sin(math.radians(angle))
        
        # Phares avant (jaunes)
        offset = self.longueur / 2 - 2
        for side in [-1, 1]:
            px = self.x + offset * cos_a
            py = self.y + offset * sin_a
            
            lateral = self.largeur / 2 - 4
            px += side * lateral * math.cos(math.radians(angle + 90))
            py += side * lateral * math.sin(math.radians(angle + 90))
            
            t.goto(px, py - 2)
            t.fillcolor('#FFFF99')
            t.pencolor('#CCCC00')
            t.pensize(1)
            t.pendown()
            t.begin_fill()
            t.circle(2)
            t.end_fill()
            t.penup()
        
        # Feux arrière (rouges)
        offset = -self.longueur / 2 + 2
        for side in [-1, 1]:
            px = self.x + offset * cos_a
            py = self.y + offset * sin_a
            
            lateral = self.largeur / 2 - 4
            px += side * lateral * math.cos(math.radians(angle + 90))
            py += side * lateral * math.sin(math.radians(angle + 90))
            
            # Plus lumineux si à l'arrêt (freinage)
            feu_color = '#FF4444' if self.en_arret else '#CC0000'
            
            t.goto(px, py - 2)
            t.fillcolor(feu_color)
            t.pencolor('#990000')
            t.pensize(1)
            t.pendown()
            t.begin_fill()
            t.circle(2)
            t.end_fill()
            t.penup()
    
    def _calculer_coins(self, cx: float, cy: float, longueur: float, 
                        largeur: float, angle: float) -> List[Tuple[float, float]]:
        """Calcule les coins d'un rectangle orienté"""
        cos_a = math.cos(math.radians(angle))
        sin_a = math.sin(math.radians(angle))
        
        l2, w2 = longueur / 2, largeur / 2
        coins_locaux = [(-l2, -w2), (l2, -w2), (l2, w2), (-l2, w2)]
        
        return [
            (lx * cos_a - ly * sin_a + cx, lx * sin_a + ly * cos_a + cy)
            for lx, ly in coins_locaux
        ]
    
    def _assombrir(self, hex_color: str, factor: float = 0.7) -> str:
        """Assombrit une couleur"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) < 6:
            return '#333333'
        try:
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            r, g, b = int(r * factor), int(g * factor), int(b * factor)
            return f'#{r:02x}{g:02x}{b:02x}'
        except:
            return '#333333'
    
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
        """Distance à la ligne d'arrêt"""
        ligne = DIMENSIONS.ligne_arret
        
        if self.direction == Direction.NORD:
            return -ligne - self.y
        elif self.direction == Direction.SUD:
            return self.y - ligne
        elif self.direction == Direction.EST:
            return -ligne - self.x
        elif self.direction == Direction.OUEST:
            return self.x - ligne
        return 0
    
    def est_dans_intersection(self) -> bool:
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
        """Crée un nouveau véhicule"""
        if not self.screen or len(self.voitures) >= self.config.max_voitures:
            return None
        
        if direction is None:
            direction = random.choice(list(Direction))
        
        x, y = get_position_depart(direction)
        
        if self._collision_spawn(x, y, direction):
            return None
        
        self.compteur_id += 1
        
        type_v = random.choice(list(TypeVehicule))
        
        vitesse_mult = {
            TypeVehicule.BERLINE: 1.0,
            TypeVehicule.SUV: 0.9,
            TypeVehicule.COMPACT: 1.1,
        }
        
        vitesse_max = self.config.vitesse_base * vitesse_mult[type_v]
        vitesse_max += random.uniform(-self.config.vitesse_variation, self.config.vitesse_variation)
        
        voiture = Voiture(
            screen=self.screen,
            id=self.compteur_id,
            direction=direction,
            x=x, y=y,
            type_vehicule=type_v,
            vitesse_max=vitesse_max,
            couleur=random.choice(COULEURS_VOITURES)
        )
        
        self.voitures.append(voiture)
        return voiture
    
    def _collision_spawn(self, x: float, y: float, direction: Direction) -> bool:
        """Vérifie collision au spawn"""
        dist_min = DIMENSIONS.distance_securite + 50
        
        for v in self.voitures:
            if v.direction == direction:
                if math.sqrt((v.x - x)**2 + (v.y - y)**2) < dist_min:
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
            
            if voiture.est_dans_intersection():
                voiture.dans_intersection = True
            
            if voiture.est_hors_ecran():
                self._notifier('sortie', voiture)
                a_supprimer.append(voiture)
        
        for v in a_supprimer:
            v.effacer()
            self.voitures.remove(v)
    
    def _doit_sarreter(self, voiture: Voiture, etat_feu: EtatFeu) -> bool:
        """Détermine si la voiture doit s'arrêter"""
        if voiture.dans_intersection or voiture.a_passe_feu:
            return False
        
        distance = voiture.distance_a_ligne_arret()
        
        if distance <= 0:
            voiture.a_passe_feu = True
            return False
        
        zone = DIMENSIONS.distance_securite + voiture.longueur
        
        if etat_feu == EtatFeu.ROUGE:
            return distance < zone
        elif etat_feu == EtatFeu.ORANGE:
            if distance < 35:
                voiture.a_passe_feu = True
                return False
            return distance < zone
        
        return False
    
    def _voiture_devant(self, voiture: Voiture) -> bool:
        """Vérifie s'il y a une voiture devant"""
        dist_secu = DIMENSIONS.distance_securite
        
        for autre in self.voitures:
            if autre.id == voiture.id or autre.direction != voiture.direction:
                continue
            
            if voiture.direction == Direction.NORD and autre.y > voiture.y:
                if autre.y - voiture.y < dist_secu:
                    return True
            elif voiture.direction == Direction.SUD and autre.y < voiture.y:
                if voiture.y - autre.y < dist_secu:
                    return True
            elif voiture.direction == Direction.EST and autre.x > voiture.x:
                if autre.x - voiture.x < dist_secu:
                    return True
            elif voiture.direction == Direction.OUEST and autre.x < voiture.x:
                if voiture.x - autre.x < dist_secu:
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