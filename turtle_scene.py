"""
turtle_scene.py - Dessin du carrefour
Projet Feu Tricolore - Ville de Thiès
"""

import turtle
from scenarios import COULEURS, DIMENSIONS


class CarrefourScene:
    """Dessine le carrefour routier"""
    
    def __init__(self, screen: turtle.TurtleScreen):
        self.screen = screen
        self.t = turtle.RawTurtle(screen)
        self.t.hideturtle()
        self.t.speed(0)
        self.t.penup()
        
        self.L = DIMENSIONS.largeur_route  # Largeur route
    
    def dessiner(self) -> None:
        """Dessine le carrefour complet"""
        self._fond()
        self._routes()
        self._marquages()
        self._passages_pietons()
        self._lignes_arret()
        self._ilot_central()
    
    def _fond(self) -> None:
        """Fond vert (herbe)"""
        t = self.t
        t.goto(-400, -400)
        t.fillcolor(COULEURS.herbe)
        t.pendown()
        t.begin_fill()
        for _ in range(4):
            t.forward(800)
            t.left(90)
        t.end_fill()
        t.penup()
    
    def _routes(self) -> None:
        """Dessine les routes"""
        t = self.t
        L = self.L
        
        t.fillcolor(COULEURS.route)
        
        # Route verticale
        t.goto(-L, -400)
        t.pendown()
        t.begin_fill()
        for size in [2*L, 800, 2*L, 800]:
            t.forward(size)
            t.left(90)
        t.end_fill()
        t.penup()
        
        # Route horizontale
        t.goto(-400, -L)
        t.pendown()
        t.begin_fill()
        for size in [800, 2*L, 800, 2*L]:
            t.forward(size)
            t.left(90)
        t.end_fill()
        t.penup()
        
        # Bordures
        t.pencolor(COULEURS.route_bordure)
        t.pensize(3)
        
        for x in [-L, L]:
            t.goto(x, -400)
            t.pendown()
            t.goto(x, -L)
            t.penup()
            t.goto(x, L)
            t.pendown()
            t.goto(x, 400)
            t.penup()
        
        for y in [-L, L]:
            t.goto(-400, y)
            t.pendown()
            t.goto(-L, y)
            t.penup()
            t.goto(L, y)
            t.pendown()
            t.goto(400, y)
            t.penup()
    
    def _marquages(self) -> None:
        """Lignes centrales pointillées"""
        t = self.t
        L = self.L
        
        t.pencolor(COULEURS.marquage)
        t.pensize(3)
        
        # Verticales
        for y_start, y_end in [(-400, -L - 20), (L + 20, 400)]:
            y = y_start
            while y < y_end:
                t.goto(0, y)
                t.pendown()
                t.goto(0, min(y + 30, y_end))
                t.penup()
                y += 50
        
        # Horizontales
        for x_start, x_end in [(-400, -L - 20), (L + 20, 400)]:
            x = x_start
            while x < x_end:
                t.goto(x, 0)
                t.pendown()
                t.goto(min(x + 30, x_end), 0)
                t.penup()
                x += 50
    
    def _passages_pietons(self) -> None:
        """Passages piétons zébrés"""
        t = self.t
        L = self.L
        
        t.fillcolor(COULEURS.marquage)
        
        # Nord et Sud
        for y_center in [L + 15, -L - 15]:
            x = -L + 10
            while x < L - 10:
                t.goto(x, y_center - 12)
                t.pendown()
                t.begin_fill()
                for _ in range(2):
                    t.forward(10)
                    t.left(90)
                    t.forward(24)
                    t.left(90)
                t.end_fill()
                t.penup()
                x += 18
        
        # Est et Ouest
        for x_center in [L + 15, -L - 15]:
            y = -L + 10
            while y < L - 10:
                t.goto(x_center - 12, y)
                t.pendown()
                t.begin_fill()
                for _ in range(2):
                    t.forward(24)
                    t.left(90)
                    t.forward(10)
                    t.left(90)
                t.end_fill()
                t.penup()
                y += 18
    
    def _lignes_arret(self) -> None:
        """Lignes d'arrêt épaisses"""
        t = self.t
        L = self.L
        ligne = DIMENSIONS.ligne_arret
        
        t.pencolor(COULEURS.marquage)
        t.pensize(5)
        
        # Ligne Sud (pour voitures allant vers Nord)
        t.goto(-L + 5, -ligne)
        t.pendown()
        t.goto(-5, -ligne)
        t.penup()
        
        # Ligne Nord (pour voitures allant vers Sud)
        t.goto(5, ligne)
        t.pendown()
        t.goto(L - 5, ligne)
        t.penup()
        
        # Ligne Ouest (pour voitures allant vers Est)
        t.goto(-ligne, 5)
        t.pendown()
        t.goto(-ligne, L - 5)
        t.penup()
        
        # Ligne Est (pour voitures allant vers Ouest)
        t.goto(ligne, -L + 5)
        t.pendown()
        t.goto(ligne, -5)
        t.penup()
    
    def _ilot_central(self) -> None:
        """Îlot central décoratif"""
        t = self.t
        
        # Cercle extérieur
        t.goto(0, -25)
        t.fillcolor(COULEURS.herbe_fonce)
        t.pencolor(COULEURS.trottoir)
        t.pensize(4)
        t.pendown()
        t.begin_fill()
        t.circle(25)
        t.end_fill()
        t.penup()
        
        # Cercle intérieur
        t.goto(0, -12)
        t.fillcolor('#1E8449')
        t.pendown()
        t.begin_fill()
        t.circle(12)
        t.end_fill()
        t.penup()
    
    def effacer(self) -> None:
        self.t.clear()


class PanneauInfo:
    """Affiche le titre"""
    
    def __init__(self, screen: turtle.TurtleScreen):
        self.screen = screen
        self.t = turtle.RawTurtle(screen)
        self.t.hideturtle()
        self.t.speed(0)
        self.t.penup()
    
    def dessiner_titre(self, texte: str = "Carrefour de Thiès") -> None:
        self.t.goto(0, 360)
        self.t.pencolor('#FFFFFF')
        self.t.write(texte, align='center', font=('Segoe UI', 14, 'bold'))
    
    def effacer(self) -> None:
        self.t.clear()