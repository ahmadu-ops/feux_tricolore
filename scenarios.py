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
        emojis = {
            Scenario.NORMAL: "🚗",
            Scenario.HEURE_POINTE: "🚦",
            Scenario.NUIT: "🌙",
            Scenario.MANUEL: "🎮"
        }
        return emojis.get(self, "❓")
    
    @property
    def description(self) -> str:
        descriptions = {
            Scenario.NORMAL: "Flux régulier, timing standard",
            Scenario.HEURE_POINTE: "Trafic dense, feu vert prolongé",
            Scenario.NUIT: "Feu orange clignotant",
            Scenario.MANUEL: "Contrôle total par l'utilisateur"
        }
        return descriptions.get(self, "")


class Direction(Enum):
    """Directions possibles des véhicules"""
    NORD = "NORD"
    SUD = "SUD"
    EST = "EST"
    OUEST = "OUEST"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def angle(self) -> float:
        angles = {
            Direction.NORD: 90,
            Direction.SUD: -90,
            Direction.EST: 0,
            Direction.OUEST: 180
        }
        return angles.get(self, 0)
    
    @property
    def vecteur(self) -> Tuple[int, int]:
        vecteurs = {
            Direction.NORD: (0, 1),
            Direction.SUD: (0, -1),
            Direction.EST: (1, 0),
            Direction.OUEST: (-1, 0)
        }
        return vecteurs.get(self, (0, 0))
    
    @property
    def voie(self) -> int:
        """1 pour Nord-Sud, 2 pour Est-Ouest"""
        if self in [Direction.NORD, Direction.SUD]:
            return 1
        return 2


@dataclass(frozen=True)
class ConfigScenario:
    """Configuration d'un scénario"""
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
        return self.duree_vert + self.duree_orange


SCENARIOS_CONFIG: Dict[Scenario, ConfigScenario] = {
    Scenario.NORMAL: ConfigScenario(
        duree_vert=10.0,
        duree_orange=3.0,
        freq_apparition=0.025,
        vitesse_base=2.5,
        vitesse_variation=0.5,
        max_voitures=12
    ),
    Scenario.HEURE_POINTE: ConfigScenario(
        duree_vert=15.0,
        duree_orange=2.0,
        freq_apparition=0.06,
        vitesse_base=2.0,
        vitesse_variation=0.3,
        max_voitures=15
    ),
    Scenario.NUIT: ConfigScenario(
        duree_vert=0.0,
        duree_orange=0.5,
        freq_apparition=0.008,
        vitesse_base=2.0,
        vitesse_variation=0.3,
        max_voitures=5,
        mode_clignotant=True,
        delai_clignotement=0.5
    ),
    Scenario.MANUEL: ConfigScenario(
        duree_vert=999999.0,
        duree_orange=999999.0,
        freq_apparition=0.03,
        vitesse_base=2.5,
        vitesse_variation=0.5,
        max_voitures=12
    )
}


def get_config(scenario: Scenario) -> ConfigScenario:
    return SCENARIOS_CONFIG.get(scenario, SCENARIOS_CONFIG[Scenario.NORMAL])


@dataclass(frozen=True)
class Couleurs:
    """Palette de couleurs"""
    # Routes
    route: str = "#34495E"
    route_bordure: str = "#2C3E50"
    marquage: str = "#FFFFFF"
    marquage_jaune: str = "#F1C40F"
    
    # Environnement
    herbe: str = "#2ECC71"
    herbe_fonce: str = "#27AE60"
    trottoir: str = "#95A5A6"
    
    # Feux
    feu_support: str = "#2C3E50"
    feu_cadre: str = "#1A1A1A"
    rouge: str = "#E74C3C"
    orange: str = "#F39C12"
    vert: str = "#2ECC71"
    rouge_eteint: str = "#4A1A1A"
    orange_eteint: str = "#4A3A0A"
    vert_eteint: str = "#0A3A1A"
    
    # Interface
    bg_dark: str = "#0D1B2A"
    bg_panel: str = "#1B263B"
    bg_card: str = "#415A77"
    bg_button: str = "#778DA9"
    text_primary: str = "#E0E1DD"
    text_secondary: str = "#778DA9"
    accent: str = "#00B4D8"
    success: str = "#06D6A0"
    warning: str = "#FFD166"
    danger: str = "#EF476F"


COULEURS = Couleurs()


COULEURS_VOITURES = [
    "#E74C3C", "#3498DB", "#2ECC71", "#F39C12", "#9B59B6",
    "#1ABC9C", "#E67E22", "#34495E", "#E91E63", "#00BCD4",
    "#8BC34A", "#FF5722", "#607D8B", "#9C27B0", "#3F51B5"
]


@dataclass(frozen=True)
class DimensionsCarrefour:
    """Dimensions du carrefour"""
    # Routes
    largeur_route: int = 65
    largeur_voie: int = 50
    
    # Feux
    feu_largeur: int = 30
    feu_hauteur: int = 80
    feu_rayon_lampe: int = 10
    feu_espacement_lampes: int = 22
    
    # Voitures
    voiture_largeur: int = 22
    voiture_longueur: int = 35
    
    # Distances - IMPORTANT pour l'arrêt
    ligne_arret: int = 20  # Distance du centre à la ligne d'arrêt
    zone_intersection: int = 100  # Zone centrale du carrefour
    distance_securite: int = 70  # Distance entre voitures
    limite_ecran: int = 380  # Limite pour sortie


DIMENSIONS = DimensionsCarrefour()


def get_positions_feux() -> Dict[str, Tuple[float, float, str, int]]:
    """Retourne les positions des 4 feux"""
    offset = DIMENSIONS.largeur_route + 20
    
    return {
        "nord_ouest": (-offset, offset, "vertical", 1),
        "sud_est": (offset, -offset, "vertical", 1),
        "sud_ouest": (-offset, -offset, "horizontal", 2),
        "nord_est": (offset, offset, "horizontal", 2)
    }


def get_position_depart(direction: Direction) -> Tuple[float, float]:
    """Retourne la position de départ pour une direction"""
    offset_voie = 25  # Décalage pour être sur la bonne voie
    depart = 350  # Distance du centre
    
    positions = {
        Direction.NORD: (-offset_voie, -depart),
        Direction.SUD: (offset_voie, depart),
        Direction.EST: (-depart, offset_voie),
        Direction.OUEST: (depart, -offset_voie)
    }
    return positions.get(direction, (0, 0))


if __name__ == "__main__":
    print("=" * 60)
    print("TEST scenarios.py")
    print("=" * 60)
    
    for scenario in Scenario:
        config = get_config(scenario)
        print(f"\n{scenario.emoji} {scenario.value}")
        print(f"   {scenario.description}")
    
    print("\n✅ Module OK")