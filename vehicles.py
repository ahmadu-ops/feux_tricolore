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
    COULEURS, COULEURS_VOITURES, DIMENSIONS
)
from traffic_light import GestionnaireFeux


@dataclass
class Voiture:
    """
    Représente un véhicule dans la simulation.
    Gère la position, le mouvement et l'affichage d'une voiture.
    """
    
    # Identifiants
    id: int
    direction: Direction
    
    # Position et mouvement
    x: float
    y: float
    vitesse: float = 0.0
    vitesse_max: float = 3.0
    acceleration: float = 0.2
    deceleration: float = 0.3
    
    # Apparence
    couleur: str = "#3498DB"
    largeur: float = field(default_factory=lambda: DIMENSIONS.voiture_largeur)
    longueur: float = field(default_factory=lambda: DIMENSIONS.voiture_longueur)
    
    # États
    en_arret: bool = False
    a_passe_feu: bool = False
    
    # Flags pour le logging (éviter les doublons)
    logged_arret: bool = False
    logged_redemarrage: bool = False
    
    # Turtle pour le dessin (initialisé après création)
    _turtle: turtle.Turtle = field(default=None, repr=False, compare=False)
    
    def __post_init__(self):
        """Initialise le turtle après création de l'objet"""
        self._turtle = turtle.Turtle()
        self._turtle.hideturtle()
        self._turtle.speed(0)
        self._turtle.penup()
    
    @property
    def turtle(self) -> turtle.Turtle:
        """Retourne le turtle de la voiture"""
        return self._turtle
    
    def dessiner(self) -> None:
        """Dessine la voiture à sa position actuelle"""
        t = self._turtle
        t.clear()
        
        # Angle selon la direction
        angle = self.direction.angle
        
        # Dessiner le corps
        self._dessiner_corps(angle)
        
        # Dessiner les détails
        self._dessiner_vitres(angle)
        self._dessiner_phares(angle)
    
    def _dessiner_corps(self, angle: float) -> None:
        """Dessine le corps principal de la voiture"""
        t = self._turtle
        
        # Calculer les coins du rectangle orienté
        coins = self._calculer_coins(
            self.x, self.y,
            self.longueur, self.largeur,
            angle
        )
        
        # Dessiner le rectangle
        t.pensize(1)
        t.pencolor('#1A1A1A')
        t.fillcolor(self.couleur)
        
        t.goto(coins[0])
        t.pendown()
        t.begin_fill()
        for coin in coins[1:]:
            t.goto(coin)
        t.goto(coins[0])
        t.end_fill()
        t.penup()
    
    def _dessiner_vitres(self, angle: float) -> None:
        """Dessine les vitres de la voiture"""
        t = self._turtle
        
        # Vitre avant (pare-brise)
        offset_avant = self.longueur / 4
        vx = self.x + offset_avant * math.cos(math.radians(angle))
        vy = self.y + offset_avant * math.sin(math.radians(angle))
        
        coins_vitre = self._calculer_coins(
            vx, vy,
            8, self.largeur - 6,
            angle
        )
        
        t.fillcolor('#85C1E9')  # Bleu clair pour les vitres
        t.goto(coins_vitre[0])
        t.pendown()
        t.begin_fill()
        for coin in coins_vitre[1:]:
            t.goto(coin)
        t.goto(coins_vitre[0])
        t.end_fill()
        t.penup()
        
        # Vitre arrière
        offset_arriere = -self.longueur / 4
        vx = self.x + offset_arriere * math.cos(math.radians(angle))
        vy = self.y + offset_arriere * math.sin(math.radians(angle))
        
        coins_vitre = self._calculer_coins(
            vx, vy,
            6, self.largeur - 8,
            angle
        )
        
        t.goto(coins_vitre[0])
        t.pendown()
        t.begin_fill()
        for coin in coins_vitre[1:]:
            t.goto(coin)
        t.goto(coins_vitre[0])
        t.end_fill()
        t.penup()
    
    def _dessiner_phares(self, angle: float) -> None:
        """Dessine les phares de la voiture"""
        t = self._turtle
        
        # Phares avant (jaunes)
        offset = self.longueur / 2 - 3
        largeur_phare = self.largeur / 2 - 2
        
        for cote in [-1, 1]:
            px = self.x + offset * math.cos(math.radians(angle))
            py = self.y + offset * math.sin(math.radians(angle))
            
            # Décalage latéral
            px += cote * largeur_phare * math.cos(math.radians(angle + 90))
            py += cote * largeur_phare * math.sin(math.radians(angle + 90))
            
            t.goto(px, py - 2)
            t.pendown()
            t.fillcolor('#F1C40F')
            t.begin_fill()
            t.circle(2)
            t.end_fill()
            t.penup()
        
        # Feux arrière (rouges)
        offset = -self.longueur / 2 + 3
        
        for cote in [-1, 1]:
            px = self.x + offset * math.cos(math.radians(angle))
            py = self.y + offset * math.sin(math.radians(angle))
            
            px += cote * largeur_phare * math.cos(math.radians(angle + 90))
            py += cote * largeur_phare * math.sin(math.radians(angle + 90))
            
            t.goto(px, py - 2)
            t.pendown()
            t.fillcolor('#E74C3C')
            t.begin_fill()
            t.circle(2)
            t.end_fill()
            t.penup()
    
    def _calculer_coins(self, cx: float, cy: float, 
                        longueur: float, largeur: float,
                        angle: float) -> List[Tuple[float, float]]:
        """
        Calcule les 4 coins d'un rectangle orienté.
        
        Args:
            cx, cy: Centre du rectangle
            longueur: Longueur (direction du mouvement)
            largeur: Largeur
            angle: Angle de rotation en degrés
            
        Returns:
            Liste des 4 coins [(x1,y1), (x2,y2), ...]
        """
        cos_a = math.cos(math.radians(angle))
        sin_a = math.sin(math.radians(angle))
        
        l2, w2 = longueur / 2, largeur / 2
        
        # Coins locaux (avant rotation)
        coins_locaux = [
            (-l2, -w2),
            (l2, -w2),
            (l2, w2),
            (-l2, w2)
        ]
        
        # Appliquer rotation et translation
        coins = []
        for lx, ly in coins_locaux:
            rx = lx * cos_a - ly * sin_a + cx
            ry = lx * sin_a + ly * cos_a + cy
            coins.append((rx, ry))
        
        return coins
    
    def deplacer(self, vitesse: float) -> None:
        """
        Déplace la voiture selon sa direction.
        
        Args:
            vitesse: Vitesse de déplacement
        """
        self.vitesse = vitesse
        dx, dy = self.direction.vecteur
        self.x += dx * vitesse
        self.y += dy * vitesse
    
    def accelerer(self) -> None:
        """Accélère la voiture progressivement"""
        self.vitesse = min(self.vitesse_max, self.vitesse + self.acceleration)
    
    def freiner(self) -> None:
        """Freine la voiture progressivement"""
        self.vitesse = max(0, self.vitesse - self.deceleration)
    
    def arreter(self) -> None:
        """Arrête complètement la voiture"""
        self.vitesse = 0
        self.en_arret = True
    
    def distance_au_feu(self) -> float:
        """
        Calcule la distance à la ligne d'arrêt.
        
        Returns:
            Distance en pixels, -1 si déjà passé
        """
        ligne = DIMENSIONS.ligne_arret
        
        if self.direction == Direction.NORD:
            return ligne - self.y if self.y < ligne else -1
        elif self.direction == Direction.SUD:
            return self.y - (-ligne) if self.y > -ligne else -1
        elif self.direction == Direction.EST:
            return ligne - self.x if self.x < ligne else -1
        elif self.direction == Direction.OUEST:
            return self.x - (-ligne) if self.x > -ligne else -1
        
        return -1
    
    def est_hors_ecran(self) -> bool:
        """Vérifie si la voiture est sortie de l'écran"""
        limite = DIMENSIONS.limite_ecran
        return abs(self.x) > limite or abs(self.y) > limite
    
    def effacer(self) -> None:
        """Efface la voiture de l'écran"""
        if self._turtle:
            self._turtle.clear()
    
    def __del__(self):
        """Destructeur - nettoie le turtle"""
        self.effacer()


class GestionnaireVoitures:
    """
    Gère l'ensemble des véhicules de la simulation.
    Contrôle la création, le mouvement et la suppression des voitures.
    """
    
    def __init__(self, gestionnaire_feux: GestionnaireFeux):
        """
        Initialise le gestionnaire de voitures.
        
        Args:
            gestionnaire_feux: Référence au gestionnaire des feux
        """
        self.voitures: List[Voiture] = []
        self.gestionnaire_feux = gestionnaire_feux
        
        # Compteur d'ID unique
        self.compteur_id: int = 0
        
        # Configuration
        self.scenario = Scenario.NORMAL
        self.config: ConfigScenario = get_config(Scenario.NORMAL)
        
        # Callback pour les événements
        self.on_event_callback: Optional[Callable] = None
    
    def changer_scenario(self, scenario: Scenario) -> None:
        """
        Change le scénario actif.
        
        Args:
            scenario: Nouveau scénario
        """
        self.scenario = scenario
        self.config = get_config(scenario)
    
    def creer_voiture(self, direction: Direction = None) -> Optional[Voiture]:
        """
        Crée une nouvelle voiture.
        
        Args:
            direction: Direction de la voiture (aléatoire si None)
            
        Returns:
            Nouvelle voiture ou None si impossible
        """
        # Vérifier la limite
        if len(self.voitures) >= self.config.max_voitures:
            return None
        
        # Direction aléatoire si non spécifiée
        if direction is None:
            direction = random.choice(list(Direction))
        
        # Position de départ
        x, y = direction.position_depart
        
        # Vérifier les collisions avec les voitures existantes
        if self._collision_au_spawn(x, y, direction):
            return None
        
        # Créer la voiture
        self.compteur_id += 1
        
        vitesse_max = self.config.vitesse_base + random.uniform(
            -self.config.vitesse_variation,
            self.config.vitesse_variation
        )
        
        voiture = Voiture(
            id=self.compteur_id,
            direction=direction,
            x=x,
            y=y,
            vitesse_max=vitesse_max,
            couleur=random.choice(COULEURS_VOITURES)
        )
        
        self.voitures.append(voiture)
        return voiture
    
    def _collision_au_spawn(self, x: float, y: float, 
                            direction: Direction) -> bool:
        """
        Vérifie s'il y a collision au point de spawn.
        
        Args:
            x, y: Position de spawn
            direction: Direction de la nouvelle voiture
            
        Returns:
            True s'il y a collision
        """
        distance_min = DIMENSIONS.distance_securite + DIMENSIONS.voiture_longueur
        
        for voiture in self.voitures:
            if voiture.direction != direction:
                continue
            
            dist = math.sqrt((voiture.x - x)**2 + (voiture.y - y)**2)
            if dist < distance_min:
                return True
        
        return False
    
    def generer_aleatoire(self) -> Optional[Voiture]:
        """
        Génère une voiture aléatoirement selon la probabilité du scénario.
        
        Returns:
            Nouvelle voiture ou None
        """
        if random.random() < self.config.freq_apparition:
            return self.creer_voiture()
        return None
    
    def update(self, dt: float) -> None:
        """
        Met à jour toutes les voitures.
        
        Args:
            dt: Temps écoulé depuis la dernière mise à jour
        """
        voitures_a_supprimer: List[Voiture] = []
        
        for voiture in self.voitures:
            # Obtenir l'état du feu pour cette direction
            etat_feu = self.gestionnaire_feux.get_etat_pour_direction(voiture.direction)
            
            # Vérifier si doit s'arrêter
            doit_sarreter = self._doit_sarreter(voiture, etat_feu)
            
            # Vérifier collision avec voiture devant
            voiture_devant = self._voiture_devant(voiture)
            
            if doit_sarreter or voiture_devant:
                # Freiner
                voiture.freiner()
                
                if voiture.vitesse == 0 and not voiture.en_arret:
                    voiture.en_arret = True
                    
                    # Log l'arrêt (une seule fois)
                    if not voiture.logged_arret:
                        self._notifier_event('arret', voiture)
                        voiture.logged_arret = True
                        voiture.logged_redemarrage = False
            else:
                # Redémarrer si était à l'arrêt
                if voiture.en_arret:
                    voiture.en_arret = False
                    
                    if not voiture.logged_redemarrage:
                        self._notifier_event('redemarrage', voiture)
                        voiture.logged_redemarrage = True
                        voiture.logged_arret = False
                
                # Accélérer
                voiture.accelerer()
            
            # Déplacer
            voiture.deplacer(voiture.vitesse)
            
            # Vérifier si hors écran
            if voiture.est_hors_ecran():
                self._notifier_event('sortie', voiture)
                voitures_a_supprimer.append(voiture)
        
        # Supprimer les voitures sorties
        for voiture in voitures_a_supprimer:
            self._supprimer_voiture(voiture)
    
    def _doit_sarreter(self, voiture: Voiture, etat_feu: EtatFeu) -> bool:
        """
        Détermine si une voiture doit s'arrêter.
        
        Args:
            voiture: La voiture à vérifier
            etat_feu: État du feu pour cette direction
            
        Returns:
            True si la voiture doit s'arrêter
        """
        # Si déjà passé le feu, ne pas s'arrêter
        if voiture.a_passe_feu:
            return False
        
        distance = voiture.distance_au_feu()
        
        # A passé le feu
        if distance < 0:
            voiture.a_passe_feu = True
            return False
        
        # Zone d'arrêt (avant la ligne)
        zone_arret = DIMENSIONS.distance_securite + voiture.longueur / 2
        
        # Feu rouge: s'arrêter si dans la zone
        if etat_feu == EtatFeu.ROUGE:
            return distance < zone_arret
        
        # Feu orange: s'arrêter si assez loin, sinon continuer
        elif etat_feu == EtatFeu.ORANGE:
            # Si proche du feu, continuer
            if distance < 30:
                return False
            return distance < zone_arret
        
        # Feu orange clignotant (mode nuit): ralentir mais pas s'arrêter
        elif etat_feu == EtatFeu.ORANGE_CLIGNOTANT:
            return False
        
        # Feu vert: ne pas s'arrêter
        return False
    
    def _voiture_devant(self, voiture: Voiture) -> bool:
        """
        Vérifie s'il y a une voiture devant.
        
        Args:
            voiture: La voiture à vérifier
            
        Returns:
            True s'il y a une voiture devant à distance de sécurité
        """
        distance_securite = DIMENSIONS.distance_securite
        
        for autre in self.voitures:
            # Ignorer la même voiture
            if autre.id == voiture.id:
                continue
            
            # Ignorer les voitures d'autres directions
            if autre.direction != voiture.direction:
                continue
            
            # Vérifier si l'autre est devant
            devant = False
            distance = 0
            
            if voiture.direction == Direction.NORD:
                if autre.y > voiture.y:
                    devant = True
                    distance = autre.y - voiture.y
            elif voiture.direction == Direction.SUD:
                if autre.y < voiture.y:
                    devant = True
                    distance = voiture.y - autre.y
            elif voiture.direction == Direction.EST:
                if autre.x > voiture.x:
                    devant = True
                    distance = autre.x - voiture.x
            elif voiture.direction == Direction.OUEST:
                if autre.x < voiture.x:
                    devant = True
                    distance = voiture.x - autre.x
            
            if devant and distance < distance_securite:
                return True
        
        return False
    
    def _notifier_event(self, event_type: str, voiture: Voiture) -> None:
        """
        Notifie un événement via le callback.
        
        Args:
            event_type: Type d'événement
            voiture: Voiture concernée
        """
        if self.on_event_callback:
            self.on_event_callback(event_type, voiture)
    
    def _supprimer_voiture(self, voiture: Voiture) -> None:
        """
        Supprime une voiture de la simulation.
        
        Args:
            voiture: Voiture à supprimer
        """
        voiture.effacer()
        if voiture in self.voitures:
            self.voitures.remove(voiture)
    
    def dessiner_toutes(self) -> None:
        """Dessine toutes les voitures"""
        for voiture in self.voitures:
            voiture.dessiner()
    
    def supprimer_toutes(self) -> None:
        """Supprime toutes les voitures"""
        for voiture in self.voitures:
            voiture.effacer()
        self.voitures.clear()
    
    def get_nombre_voitures(self) -> int:
        """Retourne le nombre de voitures actuelles"""
        return len(self.voitures)
    
    def reinitialiser(self) -> None:
        """Réinitialise le gestionnaire"""
        self.supprimer_toutes()
        self.compteur_id = 0


# ============================================================================
# TEST DU MODULE
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE vehicles.py")
    print("=" * 60)
    print("\nCe module nécessite un environnement graphique.")
    print("Il sera testé via main.py")
    print("\n[TEST] Import réussi ✅")