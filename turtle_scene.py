"""
turtle_scene.py - Dessin du carrefour routier avec Turtle
Projet Feu Tricolore - Ville de Thiès
"""

import turtle
from typing import List, Tuple
from scenarios import COULEURS, DIMENSIONS


class CarrefourScene:
    """
    Dessine et gère le carrefour routier.
    Crée un carrefour réaliste avec routes, marquages et passages piétons.
    """
    
    def __init__(self, screen: turtle.TurtleScreen):
        """
        Initialise la scène du carrefour.
        
        Args:
            screen: Écran Turtle sur lequel dessiner
        """
        self.screen = screen
        
        # Turtle principal pour le dessin
        self.drawer = turtle.RawTurtle(screen)
        self.drawer.hideturtle()
        self.drawer.speed(0)
        self.drawer.penup()
        
        # Dimensions
        self.largeur_route = DIMENSIONS.largeur_route
        self.largeur_voie = DIMENSIONS.largeur_voie
    
    def dessiner(self) -> None:
        """Dessine le carrefour complet"""
        self._dessiner_fond()
        self._dessiner_routes()
        self._dessiner_marquages()
        self._dessiner_passages_pietons()
        self._dessiner_ilot_central()
        self._dessiner_decorations()
    
    def _dessiner_fond(self) -> None:
        """Dessine le fond (herbe)"""
        t = self.drawer
        
        # Grande zone d'herbe
        t.goto(-400, -400)
        t.pendown()
        t.fillcolor(COULEURS.herbe)
        t.begin_fill()
        for _ in range(4):
            t.forward(800)
            t.left(90)
        t.end_fill()
        t.penup()
    
    def _dessiner_routes(self) -> None:
        """Dessine les routes du carrefour"""
        t = self.drawer
        l = self.largeur_route
        
        # Route verticale (Nord-Sud)
        t.fillcolor(COULEURS.route)
        t.goto(-l, -400)
        t.pendown()
        t.begin_fill()
        t.goto(-l, 400)
        t.goto(l, 400)
        t.goto(l, -400)
        t.goto(-l, -400)
        t.end_fill()
        t.penup()
        
        # Route horizontale (Est-Ouest)
        t.goto(-400, -l)
        t.pendown()
        t.begin_fill()
        t.goto(400, -l)
        t.goto(400, l)
        t.goto(-400, l)
        t.goto(-400, -l)
        t.end_fill()
        t.penup()
        
        # Bordures des routes (trottoirs)
        self._dessiner_bordures()
    
    def _dessiner_bordures(self) -> None:
        """Dessine les bordures/trottoirs le long des routes"""
        t = self.drawer
        l = self.largeur_route
        epaisseur = 5
        
        t.pencolor(COULEURS.trottoir)
        t.pensize(epaisseur)
        
        # Bordures verticales
        for x in [-l, l]:
            # Segment nord
            t.goto(x, l)
            t.pendown()
            t.goto(x, 400)
            t.penup()
            
            # Segment sud
            t.goto(x, -l)
            t.pendown()
            t.goto(x, -400)
            t.penup()
        
        # Bordures horizontales
        for y in [-l, l]:
            # Segment est
            t.goto(l, y)
            t.pendown()
            t.goto(400, y)
            t.penup()
            
            # Segment ouest
            t.goto(-l, y)
            t.pendown()
            t.goto(-400, y)
            t.penup()
    
    def _dessiner_marquages(self) -> None:
        """Dessine les marquages au sol (lignes)"""
        t = self.drawer
        l = self.largeur_route
        
        # Ligne centrale pointillée - Route verticale
        self._dessiner_ligne_pointillee(
            0, -400,
            0, -l,
            longueur_trait=25,
            espace=15
        )
        self._dessiner_ligne_pointillee(
            0, l,
            0, 400,
            longueur_trait=25,
            espace=15
        )
        
        # Ligne centrale pointillée - Route horizontale
        self._dessiner_ligne_pointillee(
            -400, 0,
            -l, 0,
            longueur_trait=25,
            espace=15,
            horizontal=True
        )
        self._dessiner_ligne_pointillee(
            l, 0,
            400, 0,
            longueur_trait=25,
            espace=15,
            horizontal=True
        )
        
        # Lignes de rive (continues)
        self._dessiner_lignes_rive()
        
        # Lignes d'arrêt (stop)
        self._dessiner_lignes_arret()
    
    def _dessiner_ligne_pointillee(self, x1: float, y1: float,
                                    x2: float, y2: float,
                                    longueur_trait: float = 20,
                                    espace: float = 10,
                                    horizontal: bool = False) -> None:
        """
        Dessine une ligne pointillée.
        
        Args:
            x1, y1: Point de départ
            x2, y2: Point d'arrivée
            longueur_trait: Longueur de chaque trait
            espace: Espace entre les traits
            horizontal: True si ligne horizontale
        """
        t = self.drawer
        t.pencolor(COULEURS.marquage)
        t.pensize(3)
        
        if horizontal:
            x = x1
            while x < x2:
                t.goto(x, y1)
                t.pendown()
                t.goto(min(x + longueur_trait, x2), y1)
                t.penup()
                x += longueur_trait + espace
        else:
            y = y1
            direction = 1 if y2 > y1 else -1
            while (direction == 1 and y < y2) or (direction == -1 and y > y2):
                t.goto(x1, y)
                t.pendown()
                t.goto(x1, y + direction * longueur_trait)
                t.penup()
                y += direction * (longueur_trait + espace)
    
    def _dessiner_lignes_rive(self) -> None:
        """Dessine les lignes de rive (bords de voie)"""
        t = self.drawer
        l = self.largeur_route - 8
        
        t.pencolor(COULEURS.marquage)
        t.pensize(2)
        
        # Lignes verticales
        for x in [-l, l]:
            t.goto(x, -400)
            t.pendown()
            t.goto(x, -self.largeur_route - 5)
            t.penup()
            
            t.goto(x, self.largeur_route + 5)
            t.pendown()
            t.goto(x, 400)
            t.penup()
        
        # Lignes horizontales
        for y in [-l, l]:
            t.goto(-400, y)
            t.pendown()
            t.goto(-self.largeur_route - 5, y)
            t.penup()
            
            t.goto(self.largeur_route + 5, y)
            t.pendown()
            t.goto(400, y)
            t.penup()
    
    def _dessiner_lignes_arret(self) -> None:
        """Dessine les lignes d'arrêt aux feux"""
        t = self.drawer
        l = self.largeur_route
        ligne_pos = DIMENSIONS.ligne_arret
        
        t.pencolor(COULEURS.marquage)
        t.pensize(4)
        
        # Ligne d'arrêt Sud (voitures allant vers le Nord)
        t.goto(-l + 10, -ligne_pos)
        t.pendown()
        t.goto(-5, -ligne_pos)
        t.penup()
        
        # Ligne d'arrêt Nord (voitures allant vers le Sud)
        t.goto(5, ligne_pos)
        t.pendown()
        t.goto(l - 10, ligne_pos)
        t.penup()
        
        # Ligne d'arrêt Ouest (voitures allant vers l'Est)
        t.goto(-ligne_pos, 5)
        t.pendown()
        t.goto(-ligne_pos, l - 10)
        t.penup()
        
        # Ligne d'arrêt Est (voitures allant vers l'Ouest)
        t.goto(ligne_pos, -l + 10)
        t.pendown()
        t.goto(ligne_pos, -5)
        t.penup()
    
    def _dessiner_passages_pietons(self) -> None:
        """Dessine les passages piétons (zèbres)"""
        l = self.largeur_route
        offset = l + 15
        
        # Passage Nord
        self._dessiner_zebre(0, offset, horizontal=True)
        
        # Passage Sud
        self._dessiner_zebre(0, -offset, horizontal=True)
        
        # Passage Est
        self._dessiner_zebre(offset, 0, horizontal=False)
        
        # Passage Ouest
        self._dessiner_zebre(-offset, 0, horizontal=False)
    
    def _dessiner_zebre(self, cx: float, cy: float, 
                        horizontal: bool = True) -> None:
        """
        Dessine un passage piéton zébré.
        
        Args:
            cx, cy: Centre du passage
            horizontal: True si le passage traverse horizontalement
        """
        t = self.drawer
        
        largeur_passage = 25
        longueur_bande = self.largeur_route * 2 - 20
        epaisseur_bande = 6
        espacement = 10
        
        t.fillcolor(COULEURS.marquage)
        
        if horizontal:
            # Bandes verticales
            n_bandes = int(longueur_bande / (epaisseur_bande + espacement))
            x_start = cx - longueur_bande / 2
            
            for i in range(n_bandes):
                x = x_start + i * (epaisseur_bande + espacement)
                y = cy - largeur_passage / 2
                
                t.goto(x, y)
                t.pendown()
                t.begin_fill()
                for _ in range(2):
                    t.forward(epaisseur_bande)
                    t.left(90)
                    t.forward(largeur_passage)
                    t.left(90)
                t.end_fill()
                t.penup()
        else:
            # Bandes horizontales
            n_bandes = int(longueur_bande / (epaisseur_bande + espacement))
            y_start = cy - longueur_bande / 2
            
            for i in range(n_bandes):
                x = cx - largeur_passage / 2
                y = y_start + i * (epaisseur_bande + espacement)
                
                t.goto(x, y)
                t.pendown()
                t.setheading(0)
                t.begin_fill()
                for _ in range(2):
                    t.forward(largeur_passage)
                    t.left(90)
                    t.forward(epaisseur_bande)
                    t.left(90)
                t.end_fill()
                t.penup()
    
    def _dessiner_ilot_central(self) -> None:
        """Dessine l'îlot central du carrefour"""
        t = self.drawer
        
        # Cercle central (herbe)
        t.goto(0, -18)
        t.pendown()
        t.fillcolor(COULEURS.herbe_fonce)
        t.begin_fill()
        t.circle(18)
        t.end_fill()
        t.penup()
        
        # Bordure de l'îlot
        t.goto(0, -22)
        t.pendown()
        t.pencolor(COULEURS.trottoir)
        t.pensize(4)
        t.circle(22)
        t.penup()
        
        # Petit cercle décoratif au centre
        t.goto(0, -5)
        t.pendown()
        t.fillcolor('#1E8449')
        t.begin_fill()
        t.circle(5)
        t.end_fill()
        t.penup()
    
    def _dessiner_decorations(self) -> None:
        """Dessine des éléments décoratifs"""
        t = self.drawer
        
        # Coins arrondis aux intersections route/trottoir
        self._dessiner_coins_arrondis()
        
        # Petits arbres/buissons dans les coins
        self._dessiner_vegetation()
    
    def _dessiner_coins_arrondis(self) -> None:
        """Dessine les coins arrondis du carrefour"""
        t = self.drawer
        l = self.largeur_route
        rayon = 15
        
        t.fillcolor(COULEURS.route)
        
        # Les 4 coins intérieurs
        coins = [
            (-l, l, 270),    # Nord-Ouest
            (l, l, 180),     # Nord-Est
            (l, -l, 90),     # Sud-Est
            (-l, -l, 0)      # Sud-Ouest
        ]
        
        for x, y, angle in coins:
            t.goto(x, y)
            t.setheading(angle)
            t.pendown()
            t.begin_fill()
            t.circle(rayon, 90)
            t.end_fill()
            t.penup()
    
    def _dessiner_vegetation(self) -> None:
        """Dessine la végétation décorative"""
        t = self.drawer
        l = self.largeur_route + 50
        
        # Positions des arbres (coins du carrefour)
        positions = [
            (-l - 60, l + 60),
            (l + 60, l + 60),
            (l + 60, -l - 60),
            (-l - 60, -l - 60)
        ]
        
        for x, y in positions:
            self._dessiner_arbre(x, y)
    
    def _dessiner_arbre(self, x: float, y: float) -> None:
        """
        Dessine un arbre simplifié.
        
        Args:
            x, y: Position de l'arbre
        """
        t = self.drawer
        
        # Tronc
        t.goto(x, y)
        t.pendown()
        t.fillcolor('#8B4513')
        t.begin_fill()
        for _ in range(2):
            t.forward(8)
            t.left(90)
            t.forward(20)
            t.left(90)
        t.end_fill()
        t.penup()
        
        # Feuillage (cercles verts)
        t.goto(x + 4, y + 20)
        t.pendown()
        t.fillcolor(COULEURS.herbe_fonce)
        t.begin_fill()
        t.circle(18)
        t.end_fill()
        t.penup()
        
        t.goto(x + 4, y + 28)
        t.pendown()
        t.fillcolor(COULEURS.herbe)
        t.begin_fill()
        t.circle(14)
        t.end_fill()
        t.penup()
    
    def effacer(self) -> None:
        """Efface la scène"""
        self.drawer.clear()
    
    def redessiner(self) -> None:
        """Redessine la scène complète"""
        self.effacer()
        self.dessiner()


class PanneauInfo:
    """
    Dessine un panneau d'information sur la scène.
    Affiche le nom de la ville et autres informations.
    """
    
    def __init__(self, screen: turtle.TurtleScreen):
        """
        Initialise le panneau d'info.
        
        Args:
            screen: Écran Turtle
        """
        self.screen = screen
        self.writer = turtle.RawTurtle(screen)
        self.writer.hideturtle()
        self.writer.speed(0)
        self.writer.penup()
    
    def dessiner_titre(self, texte: str = "Carrefour de Thiès") -> None:
        """
        Dessine le titre en haut de la scène.
        
        Args:
            texte: Texte du titre
        """
        self.writer.goto(0, 350)
        self.writer.pencolor(COULEURS.text_primary)
        self.writer.write(
            texte,
            align="center",
            font=("Arial", 16, "bold")
        )
    
    def effacer(self) -> None:
        """Efface le panneau"""
        self.writer.clear()


# ============================================================================
# TEST DU MODULE
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE turtle_scene.py")
    print("=" * 60)
    
    # Test visuel
    print("\nLancement du test visuel...")
    
    # Créer une fenêtre de test
    screen = turtle.Screen()
    screen.setup(800, 800)
    screen.bgcolor(COULEURS.herbe)
    screen.title("Test - Carrefour de Thiès")
    screen.tracer(0)
    
    # Dessiner la scène
    scene = CarrefourScene(screen)
    scene.dessiner()
    
    # Ajouter le titre
    panneau = PanneauInfo(screen)
    panneau.dessiner_titre()
    
    screen.update()
    
    print("[TEST] Scène dessinée avec succès ✅")
    print("\nCliquez sur la fenêtre pour fermer...")
    
    screen.exitonclick()