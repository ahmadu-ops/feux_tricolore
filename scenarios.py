"""
scenarios.py - Configuration des scénarios de circulation
Projet Feu Tricolore - Ville de Thiès
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Tuple


class EtatFeu(Enum):
    """États possibles d'un feu tricolore"""
    ROUGE = "ROUGE"
    ORANGE = "ORANGE"
    VERT = "VERT"
    ORANGE_CLIGNOTANT = "ORANGE_CLIGNOTANT"
    ETEINT = "ETEINT"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def couleur_hex(self) -> str:
        """Retourne le code couleur hexadécimal"""
        couleurs = {
            EtatFeu.ROUGE: "#E74C3C",
            EtatFeu.ORANGE: "#F39C12",
            EtatFeu.VERT: "#2ECC71",
            EtatFeu.ORANGE_CLIGNOTANT: "#F39C12",
            EtatFeu.ETEINT: "#2C3E50"
        }
        return couleurs.get(self, "#FFFFFF")
    
    @property
    def couleur_eteinte(self) -> str:
        """Retourne le code couleur quand le feu est éteint"""
        couleurs = {
            EtatFeu.ROUGE: "#5D2A2A",
            EtatFeu.ORANGE: "#5D4A1A",
            EtatFeu.VERT: "#1A4A2A",
            EtatFeu.ORANGE_CLIGNOTANT: "#5D4A1A",
            EtatFeu.ETEINT: "#1A1A1A"
        }
        return couleurs.get(self, "#1A1A1A")
    
    @property
    def emoji(self) -> str:
        """Retourne l'emoji correspondant"""
        emojis = {
            EtatFeu.ROUGE: "🔴",
            EtatFeu.ORANGE: "🟡",
            EtatFeu.VERT: "🟢",
            EtatFeu.ORANGE_CLIGNOTANT: "🟡",
            EtatFeu.ETEINT: "⚫"
        }
        return emojis.get(self, "⚪")


class Scenario(Enum):
    """Scénarios de circulation disponibles"""
    NORMAL = "Circulation normale"
    HEURE_POINTE = "Heure de pointe"
    NUIT = "Mode nuit"
    MANUEL = "Mode manuel"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def emoji(self) -> str:
        """Retourne l'emoji correspondant au scénario"""
        emojis = {
            Scenario.NORMAL: "🚗",
            Scenario.HEURE_POINTE: "🚦",
            Scenario.NUIT: "🌙",
            Scenario.MANUEL: "🎮"
        }
        return emojis.get(self, "❓")
    
    @property
    def description(self) -> str:
        """Retourne une description du scénario"""
        descriptions = {
            Scenario.NORMAL: "Circulation fluide avec timing standard des feux",
            Scenario.HEURE_POINTE: "Trafic dense, feu vert prolongé, génération rapide",
            Scenario.NUIT: "Feu orange clignotant, peu de véhicules",
            Scenario.MANUEL: "Contrôle total des feux par l'utilisateur"
        }
        return descriptions.get(self, "")


class Direction(Enum):
    """Directions possibles des véhicules"""
    NORD = "NORD"      # Vient du sud, va vers le nord
    SUD = "SUD"        # Vient du nord, va vers le sud
    EST = "EST"        # Vient de l'ouest, va vers l'est
    OUEST = "OUEST"    # Vient de l'est, va vers l'ouest
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def angle(self) -> float:
        """Retourne l'angle de rotation en degrés"""
        angles = {
            Direction.NORD: 90,
            Direction.SUD: -90,
            Direction.EST: 0,
            Direction.OUEST: 180
        }
        return angles.get(self, 0)
    
    @property
    def vecteur(self) -> Tuple[int, int]:
        """Retourne le vecteur de déplacement (dx, dy)"""
        vecteurs = {
            Direction.NORD: (0, 1),
            Direction.SUD: (0, -1),
            Direction.EST: (1, 0),
            Direction.OUEST: (-1, 0)
        }
        return vecteurs.get(self, (0, 0))
    
    @property
    def voie(self) -> int:
        """Retourne le numéro de voie (1 pour N-S, 2 pour E-O)"""
        if self in [Direction.NORD, Direction.SUD]:
            return 1
        return 2
    
    @property
    def position_depart(self) -> Tuple[float, float]:
        """Retourne la position de départ pour cette direction"""
        positions = {
            Direction.NORD: (-30, -420),
            Direction.SUD: (30, 420),
            Direction.EST: (-420, 30),
            Direction.OUEST: (420, -30)
        }
        return positions.get(self, (0, 0))


@dataclass(frozen=True)
class ConfigScenario:
    """
    Configuration immuable d'un scénario.
    
    Attributes:
        duree_vert: Durée du feu vert en secondes
        duree_orange: Durée du feu orange en secondes
        freq_apparition: Probabilité d'apparition d'une voiture par tick (0.0 à 1.0)
        vitesse_base: Vitesse de base des véhicules
        vitesse_variation: Variation aléatoire de vitesse (+/-)
        max_voitures: Nombre maximum de voitures simultanées
        mode_clignotant: True si le mode clignotant est actif
        delai_clignotement: Durée d'un cycle de clignotement (allumé/éteint)
    """
    duree_vert: float
    duree_orange: float
    freq_apparition: float
    vitesse_base: float
    vitesse_variation: float
    max_voitures: int
    mode_clignotant: bool = False
    delai_clignotement: float = 0.5
    
    @property
    def duree_rouge(self) -> float:
        """
        Calcule la durée du feu rouge.
        Rouge = Vert opposé + Orange opposé
        """
        return self.duree_vert + self.duree_orange
    
    @property
    def duree_cycle_complet(self) -> float:
        """Calcule la durée d'un cycle complet de feux"""
        return 2 * (self.duree_vert + self.duree_orange)


# Configuration de chaque scénario
SCENARIOS_CONFIG: Dict[Scenario, ConfigScenario] = {
    Scenario.NORMAL: ConfigScenario(
        duree_vert=10.0,
        duree_orange=3.0,
        freq_apparition=0.03,
        vitesse_base=3.0,
        vitesse_variation=0.5,
        max_voitures=10,
        mode_clignotant=False
    ),
    Scenario.HEURE_POINTE: ConfigScenario(
        duree_vert=15.0,
        duree_orange=2.0,
        freq_apparition=0.08,
        vitesse_base=2.5,
        vitesse_variation=0.3,
        max_voitures=15,
        mode_clignotant=False
    ),
    Scenario.NUIT: ConfigScenario(
        duree_vert=0.0,  # Pas utilisé en mode nuit
        duree_orange=0.5,
        freq_apparition=0.01,
        vitesse_base=2.0,
        vitesse_variation=0.3,
        max_voitures=5,
        mode_clignotant=True,
        delai_clignotement=0.5
    ),
    Scenario.MANUEL: ConfigScenario(
        duree_vert=999999.0,  # Durée infinie (contrôle manuel)
        duree_orange=999999.0,
        freq_apparition=0.04,
        vitesse_base=3.0,
        vitesse_variation=0.5,
        max_voitures=12,
        mode_clignotant=False
    )
}


def get_config(scenario: Scenario) -> ConfigScenario:
    """
    Récupère la configuration d'un scénario.
    
    Args:
        scenario: Le scénario souhaité
        
    Returns:
        Configuration du scénario
    """
    return SCENARIOS_CONFIG.get(scenario, SCENARIOS_CONFIG[Scenario.NORMAL])


# ============================================================================
# COULEURS DU DESIGN
# ============================================================================

@dataclass(frozen=True)
class Couleurs:
    """Palette de couleurs pour le design du carrefour"""
    
    # Routes et marquages
    route: str = "#2C3E50"
    marquage: str = "#ECF0F1"
    marquage_jaune: str = "#F1C40F"
    
    # Environnement
    herbe: str = "#27AE60"
    herbe_fonce: str = "#1E8449"
    trottoir: str = "#7F8C8D"
    
    # Feux tricolores
    feu_support: str = "#2C3E50"
    feu_cadre: str = "#1A1A1A"
    rouge: str = "#E74C3C"
    orange: str = "#F39C12"
    vert: str = "#2ECC71"
    rouge_eteint: str = "#5D2A2A"
    orange_eteint: str = "#5D4A1A"
    vert_eteint: str = "#1A4A2A"
    
    # Interface
    bg_dark: str = "#1A1A2E"
    bg_panel: str = "#16213E"
    bg_card: str = "#0F3460"
    text_primary: str = "#ECF0F1"
    text_secondary: str = "#BDC3C7"
    accent: str = "#3498DB"


# Instance globale des couleurs
COULEURS = Couleurs()


# ============================================================================
# COULEURS DES VOITURES
# ============================================================================

COULEURS_VOITURES = [
    "#E74C3C",  # Rouge
    "#3498DB",  # Bleu
    "#2ECC71",  # Vert
    "#F39C12",  # Orange
    "#9B59B6",  # Violet
    "#1ABC9C",  # Turquoise
    "#E67E22",  # Orange foncé
    "#34495E",  # Gris foncé
    "#7F8C8D",  # Gris
    "#C0392B",  # Rouge foncé
    "#2980B9",  # Bleu foncé
    "#27AE60",  # Vert foncé
    "#8E44AD",  # Violet foncé
    "#F1C40F",  # Jaune
    "#1ABC9C",  # Cyan
]


# ============================================================================
# DIMENSIONS DU CARREFOUR
# ============================================================================

@dataclass(frozen=True)
class DimensionsCarrefour:
    """Dimensions du carrefour et des éléments"""
    
    # Canvas
    canvas_width: int = 750
    canvas_height: int = 750
    
    # Routes
    largeur_route: int = 80
    largeur_voie: int = 40
    
    # Feux
    feu_largeur: int = 25
    feu_hauteur: int = 70
    feu_rayon_lampe: int = 8
    feu_espacement_lampes: int = 20
    
    # Voitures
    voiture_largeur: int = 20
    voiture_longueur: int = 35
    
    # Distances
    ligne_arret: int = 70  # Distance du centre à la ligne d'arrêt
    distance_securite: int = 45  # Distance minimale entre voitures
    limite_ecran: int = 450  # Limite pour considérer une voiture hors écran
    
    # Passages piétons
    passage_largeur: int = 20
    passage_bande: int = 8
    passage_espacement: int = 15


# Instance globale des dimensions
DIMENSIONS = DimensionsCarrefour()


# ============================================================================
# POSITIONS DES FEUX
# ============================================================================

def get_positions_feux() -> Dict[str, Tuple[float, float, str, int]]:
    """
    Retourne les positions des 4 feux tricolores.
    
    Returns:
        Dictionnaire avec (x, y, orientation, voie) pour chaque feu
    """
    offset = DIMENSIONS.largeur_route + 5
    
    return {
        "nord_ouest": (-offset, offset, "vertical", 1),
        "sud_est": (offset, -offset, "vertical", 1),
        "sud_ouest": (-offset, -offset, "horizontal", 2),
        "nord_est": (offset, offset, "horizontal", 2)
    }


# ============================================================================
# TEST DU MODULE
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE scenarios.py")
    print("=" * 60)
    
    # Test des énumérations
    print("\n[TEST] États des feux:")
    for etat in EtatFeu:
        print(f"  {etat.emoji} {etat.value} - Couleur: {etat.couleur_hex}")
    
    print("\n[TEST] Scénarios:")
    for scenario in Scenario:
        config = get_config(scenario)
        print(f"  {scenario.emoji} {scenario.value}")
        print(f"      Description: {scenario.description}")
        print(f"      Vert: {config.duree_vert}s, Orange: {config.duree_orange}s")
        print(f"      Fréquence: {config.freq_apparition}, Max voitures: {config.max_voitures}")
    
    print("\n[TEST] Directions:")
    for direction in Direction:
        print(f"  {direction.value}: Angle={direction.angle}°, "
              f"Voie={direction.voie}, Départ={direction.position_depart}")
    
    print("\n[TEST] Couleurs:")
    print(f"  Route: {COULEURS.route}")
    print(f"  Herbe: {COULEURS.herbe}")
    print(f"  Feu rouge: {COULEURS.rouge}")
    
    print("\n[TEST] Dimensions:")
    print(f"  Canvas: {DIMENSIONS.canvas_width}x{DIMENSIONS.canvas_height}")
    print(f"  Route: {DIMENSIONS.largeur_route}px")
    print(f"  Voiture: {DIMENSIONS.voiture_longueur}x{DIMENSIONS.voiture_largeur}px")
    
    print("\n[TEST] Positions des feux:")
    positions = get_positions_feux()
    for nom, (x, y, orientation, voie) in positions.items():
        print(f"  {nom}: ({x}, {y}) - {orientation} - Voie {voie}")
    
    print("\n[TEST] Tests terminés avec succès ✅")