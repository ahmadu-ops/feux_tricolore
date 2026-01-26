"""
traffic_light.py - Logique des feux tricolores
Projet Feu Tricolore - Ville de Thiès
"""

import turtle
from typing import List, Callable, Optional, Dict
from scenarios import (
    EtatFeu, Scenario, Direction, 
    get_config, ConfigScenario,
    COULEURS, DIMENSIONS, get_positions_feux
)


class FeuTricolore:
    """
    Représente un feu tricolore individuel.
    Gère l'affichage graphique d'un feu avec ses 3 lampes.
    """
    
    def __init__(self, x: float, y: float, orientation: str, voie: int):
        """
        Initialise un feu tricolore.
        
        Args:
            x: Position X du feu
            y: Position Y du feu
            orientation: 'vertical' ou 'horizontal'
            voie: Numéro de la voie (1 pour N-S, 2 pour E-O)
        """
        self.x = x
        self.y = y
        self.orientation = orientation
        self.voie = voie
        self.etat = EtatFeu.ROUGE
        
        # Turtle principal pour le boîtier
        self.turtle = turtle.Turtle()
        self.turtle.hideturtle()
        self.turtle.speed(0)
        self.turtle.penup()
        
        # Turtles pour chaque lampe (pour mise à jour indépendante)
        self.lampes: Dict[str, turtle.Turtle] = {}
        self._init_lampes()
    
    def _init_lampes(self) -> None:
        """Initialise les turtles pour les 3 lampes"""
        for nom in ['rouge', 'orange', 'vert']:
            t = turtle.Turtle()
            t.hideturtle()
            t.speed(0)
            t.penup()
            self.lampes[nom] = t
    
    def dessiner(self) -> None:
        """Dessine le feu tricolore complet (boîtier + lampes)"""
        self._dessiner_support()
        self._dessiner_boitier()
        self._dessiner_lampes()
    
    def _dessiner_support(self) -> None:
        """Dessine le poteau de support du feu"""
        t = self.turtle
        
        # Poteau vertical
        t.pencolor(COULEURS.feu_support)
        t.pensize(6)
        t.goto(self.x, self.y - 50)
        t.pendown()
        t.goto(self.x, self.y - 10)
        t.penup()
    
    def _dessiner_boitier(self) -> None:
        """Dessine le boîtier du feu"""
        t = self.turtle
        
        largeur = DIMENSIONS.feu_largeur
        hauteur = DIMENSIONS.feu_hauteur
        
        # Inverser dimensions si horizontal
        if self.orientation == 'horizontal':
            largeur, hauteur = hauteur, largeur
        
        # Position coin inférieur gauche
        x0 = self.x - largeur / 2
        y0 = self.y - hauteur / 2
        
        # Fond du boîtier
        t.goto(x0, y0)
        t.pendown()
        t.pensize(2)
        t.pencolor('#000000')
        t.fillcolor(COULEURS.feu_cadre)
        t.begin_fill()
        
        for _ in range(2):
            t.forward(largeur)
            t.left(90)
            t.forward(hauteur)
            t.left(90)
        
        t.end_fill()
        t.penup()
        
        # Bordure extérieure (effet 3D)
        t.goto(x0 - 2, y0 - 2)
        t.pendown()
        t.pensize(3)
        t.pencolor('#333333')
        
        for _ in range(2):
            t.forward(largeur + 4)
            t.left(90)
            t.forward(hauteur + 4)
            t.left(90)
        
        t.penup()
    
    def _dessiner_lampes(self) -> None:
        """Dessine les 3 lampes du feu selon leur état"""
        rayon = DIMENSIONS.feu_rayon_lampe
        espacement = DIMENSIONS.feu_espacement_lampes
        
        # Calculer les positions des lampes selon l'orientation
        if self.orientation == 'vertical':
            positions = [
                ('rouge', self.x, self.y + espacement),
                ('orange', self.x, self.y),
                ('vert', self.x, self.y - espacement)
            ]
        else:
            positions = [
                ('rouge', self.x - espacement, self.y),
                ('orange', self.x, self.y),
                ('vert', self.x + espacement, self.y)
            ]
        
        # Dessiner chaque lampe
        for nom, lx, ly in positions:
            self._dessiner_lampe(nom, lx, ly, rayon)
    
    def _dessiner_lampe(self, nom: str, x: float, y: float, rayon: int) -> None:
        """
        Dessine une lampe individuelle.
        
        Args:
            nom: Nom de la lampe ('rouge', 'orange', 'vert')
            x: Position X
            y: Position Y
            rayon: Rayon de la lampe
        """
        t = self.lampes[nom]
        t.clear()
        
        # Déterminer si la lampe est allumée
        allumee = self._lampe_allumee(nom)
        
        # Choisir la couleur
        if allumee:
            couleur = getattr(COULEURS, nom)
        else:
            couleur = getattr(COULEURS, f"{nom}_eteint")
        
        # Dessiner le cercle
        t.goto(x, y - rayon)
        t.pendown()
        t.pensize(1)
        t.pencolor('#000000')
        t.fillcolor(couleur)
        t.begin_fill()
        t.circle(rayon)
        t.end_fill()
        t.penup()
        
        # Effet de brillance si allumée
        if allumee:
            self._dessiner_effet_brillance(t, x, y, rayon)
    
    def _lampe_allumee(self, nom: str) -> bool:
        """
        Vérifie si une lampe doit être allumée.
        
        Args:
            nom: Nom de la lampe
            
        Returns:
            True si la lampe doit être allumée
        """
        if self.etat == EtatFeu.ROUGE and nom == 'rouge':
            return True
        elif self.etat == EtatFeu.ORANGE and nom == 'orange':
            return True
        elif self.etat == EtatFeu.VERT and nom == 'vert':
            return True
        elif self.etat == EtatFeu.ORANGE_CLIGNOTANT and nom == 'orange':
            return True
        return False
    
    def _dessiner_effet_brillance(self, t: turtle.Turtle, 
                                   x: float, y: float, rayon: int) -> None:
        """Dessine un effet de brillance sur la lampe allumée"""
        # Petit cercle blanc pour l'effet de reflet
        t.goto(x - rayon/3, y + rayon/3)
        t.pendown()
        t.pencolor('white')
        t.fillcolor('white')
        t.begin_fill()
        t.circle(rayon/4)
        t.end_fill()
        t.penup()
    
    def changer_etat(self, nouvel_etat: EtatFeu) -> None:
        """
        Change l'état du feu.
        
        Args:
            nouvel_etat: Nouvel état à appliquer
        """
        ancien_etat = self.etat
        self.etat = nouvel_etat
        
        # Redessiner seulement les lampes (pas le boîtier)
        if ancien_etat != nouvel_etat:
            self._dessiner_lampes()
    
    def eteindre(self) -> None:
        """Éteint toutes les lampes du feu"""
        self.etat = EtatFeu.ETEINT
        self._dessiner_lampes()
    
    def effacer(self) -> None:
        """Efface complètement le feu"""
        self.turtle.clear()
        for lampe in self.lampes.values():
            lampe.clear()


class GestionnaireFeux:
    """
    Gère l'ensemble des 4 feux tricolores du carrefour.
    Synchronise les feux des deux voies et gère les cycles automatiques.
    """
    
    def __init__(self, on_change_callback: Callable = None):
        """
        Initialise le gestionnaire de feux.
        
        Args:
            on_change_callback: Fonction appelée lors d'un changement d'état
                               Signature: callback(voie: int, etat: EtatFeu)
        """
        # Feux par voie
        self.feux_voie1: List[FeuTricolore] = []  # Nord-Sud
        self.feux_voie2: List[FeuTricolore] = []  # Est-Ouest
        
        # États actuels
        self.etat_voie1 = EtatFeu.VERT
        self.etat_voie2 = EtatFeu.ROUGE
        
        # Configuration
        self.scenario = Scenario.NORMAL
        self.config: ConfigScenario = get_config(Scenario.NORMAL)
        
        # Timing
        self.temps_etat: float = 0.0
        self.clignotant_allume: bool = True
        
        # Callback
        self.on_change_callback = on_change_callback
        
        # Créer les feux
        self._creer_feux()
    
    def _creer_feux(self) -> None:
        """Crée les 4 feux aux positions définies"""
        positions = get_positions_feux()
        
        for nom, (x, y, orientation, voie) in positions.items():
            feu = FeuTricolore(x, y, orientation, voie)
            
            if voie == 1:
                self.feux_voie1.append(feu)
            else:
                self.feux_voie2.append(feu)
    
    def dessiner_tous(self) -> None:
        """Dessine tous les feux du carrefour"""
        for feu in self.feux_voie1:
            feu.dessiner()
        for feu in self.feux_voie2:
            feu.dessiner()
        
        # Appliquer les états initiaux
        self._appliquer_etats()
    
    def _appliquer_etats(self) -> None:
        """Applique les états actuels à tous les feux"""
        for feu in self.feux_voie1:
            feu.changer_etat(self.etat_voie1)
        for feu in self.feux_voie2:
            feu.changer_etat(self.etat_voie2)
    
    def changer_scenario(self, scenario: Scenario) -> None:
        """
        Change le scénario actif.
        
        Args:
            scenario: Nouveau scénario à appliquer
        """
        self.scenario = scenario
        self.config = get_config(scenario)
        self.temps_etat = 0.0
        
        # Configurer les états initiaux selon le scénario
        if scenario == Scenario.NUIT:
            self.etat_voie1 = EtatFeu.ORANGE_CLIGNOTANT
            self.etat_voie2 = EtatFeu.ORANGE_CLIGNOTANT
            self.clignotant_allume = True
        else:
            self.etat_voie1 = EtatFeu.VERT
            self.etat_voie2 = EtatFeu.ROUGE
        
        self._appliquer_etats()
    
    def forcer_etat(self, voie: int, etat: EtatFeu) -> None:
        """
        Force l'état d'une voie (mode manuel).
        
        Args:
            voie: Numéro de la voie (1 ou 2)
            etat: État à forcer
        """
        if voie == 1:
            self.etat_voie1 = etat
            # Si on met vert ou orange sur voie 1, voie 2 passe au rouge
            if etat in [EtatFeu.VERT, EtatFeu.ORANGE]:
                self.etat_voie2 = EtatFeu.ROUGE
        else:
            self.etat_voie2 = etat
            # Si on met vert ou orange sur voie 2, voie 1 passe au rouge
            if etat in [EtatFeu.VERT, EtatFeu.ORANGE]:
                self.etat_voie1 = EtatFeu.ROUGE
        
        self._appliquer_etats()
        
        # Notifier le changement
        if self.on_change_callback:
            self.on_change_callback(voie, etat)
    
    def update(self, dt: float) -> None:
        """
        Met à jour les feux selon le temps écoulé.
        
        Args:
            dt: Temps écoulé depuis la dernière mise à jour (en secondes)
        """
        # Pas de mise à jour en mode manuel
        if self.scenario == Scenario.MANUEL:
            return
        
        self.temps_etat += dt
        
        # Mode nuit: clignotement
        if self.scenario == Scenario.NUIT:
            self._update_clignotement()
            return
        
        # Mode normal: cycle des feux
        self._update_cycle_normal()
    
    def _update_clignotement(self) -> None:
        """Gère le clignotement du feu orange en mode nuit"""
        if self.temps_etat >= self.config.delai_clignotement:
            self.temps_etat = 0.0
            self.clignotant_allume = not self.clignotant_allume
            
            if self.clignotant_allume:
                self.etat_voie1 = EtatFeu.ORANGE_CLIGNOTANT
                self.etat_voie2 = EtatFeu.ORANGE_CLIGNOTANT
            else:
                self.etat_voie1 = EtatFeu.ETEINT
                self.etat_voie2 = EtatFeu.ETEINT
            
            self._appliquer_etats()
    
    def _update_cycle_normal(self) -> None:
        """Gère le cycle normal des feux (vert -> orange -> rouge)"""
        
        # Phase: Voie 1 verte
        if self.etat_voie1 == EtatFeu.VERT:
            if self.temps_etat >= self.config.duree_vert:
                self._transition(1, EtatFeu.ORANGE)
        
        # Phase: Voie 1 orange
        elif self.etat_voie1 == EtatFeu.ORANGE:
            if self.temps_etat >= self.config.duree_orange:
                self._transition_complete(1)
        
        # Phase: Voie 2 verte
        elif self.etat_voie2 == EtatFeu.VERT:
            if self.temps_etat >= self.config.duree_vert:
                self._transition(2, EtatFeu.ORANGE)
        
        # Phase: Voie 2 orange
        elif self.etat_voie2 == EtatFeu.ORANGE:
            if self.temps_etat >= self.config.duree_orange:
                self._transition_complete(2)
    
    def _transition(self, voie: int, nouvel_etat: EtatFeu) -> None:
        """
        Effectue une transition simple d'état.
        
        Args:
            voie: Numéro de la voie
            nouvel_etat: Nouvel état
        """
        self.temps_etat = 0.0
        
        if voie == 1:
            self.etat_voie1 = nouvel_etat
        else:
            self.etat_voie2 = nouvel_etat
        
        self._appliquer_etats()
        
        if self.on_change_callback:
            self.on_change_callback(voie, nouvel_etat)
    
    def _transition_complete(self, voie_actuelle: int) -> None:
        """
        Effectue une transition complète (change de voie active).
        
        Args:
            voie_actuelle: Voie qui vient de terminer son cycle
        """
        self.temps_etat = 0.0
        
        if voie_actuelle == 1:
            self.etat_voie1 = EtatFeu.ROUGE
            self.etat_voie2 = EtatFeu.VERT
        else:
            self.etat_voie2 = EtatFeu.ROUGE
            self.etat_voie1 = EtatFeu.VERT
        
        self._appliquer_etats()
        
        if self.on_change_callback:
            self.on_change_callback(voie_actuelle, EtatFeu.ROUGE)
            autre_voie = 2 if voie_actuelle == 1 else 1
            self.on_change_callback(autre_voie, EtatFeu.VERT)
    
    def get_etat_pour_direction(self, direction: Direction) -> EtatFeu:
        """
        Retourne l'état du feu pour une direction donnée.
        
        Args:
            direction: Direction du véhicule
            
        Returns:
            État du feu correspondant
        """
        if direction.voie == 1:
            return self.etat_voie1
        return self.etat_voie2
    
    def get_etat_voie(self, voie: int) -> EtatFeu:
        """
        Retourne l'état d'une voie.
        
        Args:
            voie: Numéro de la voie
            
        Returns:
            État du feu
        """
        return self.etat_voie1 if voie == 1 else self.etat_voie2
    
    def effacer_tous(self) -> None:
        """Efface tous les feux"""
        for feu in self.feux_voie1 + self.feux_voie2:
            feu.effacer()
    
    def reinitialiser(self) -> None:
        """Réinitialise les feux à l'état initial"""
        self.temps_etat = 0.0
        self.etat_voie1 = EtatFeu.VERT
        self.etat_voie2 = EtatFeu.ROUGE
        self.clignotant_allume = True
        self._appliquer_etats()


# ============================================================================
# TEST DU MODULE
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE traffic_light.py")
    print("=" * 60)
    print("\nCe module nécessite un environnement graphique.")
    print("Il sera testé via main.py")
    print("\n[TEST] Import réussi ✅")