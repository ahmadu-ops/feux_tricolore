"""
turtle_scene.py - Carrefour réaliste (sans ombres)
Projet Feu Tricolore - Ville de Thiès
"""

import turtle
from scenarios import COULEURS, DIMENSIONS


class CarrefourScene:
    """Carrefour routier"""
    
    def __init__(self, screen: turtle.TurtleScreen):
        self.screen = screen
        self.t = turtle.RawTurtle(screen)
        self.t.hideturtle()
        self.t.speed(0)
        self.t.penup()
        
        self.L = DIMENSIONS.largeur_route
    
    def dessiner(self) -> None:
        """Dessine le carrefour complet"""
        self._fond_herbe()
        self._trottoirs()
        self._routes()
        self._marquages()
        self._passages_pietons()
        self._lignes_arret()
        self._ilot_central()
        self._arbres()
    
    def _fond_herbe(self) -> None:
        """Fond vert"""
        t = self.t
        t.goto(-400, -400)
        t.fillcolor('#2E8B2E')
        t.pendown()
        t.begin_fill()
        for _ in range(4):
            t.forward(800)
            t.left(90)
        t.end_fill()
        t.penup()
    
    def _trottoirs(self) -> None:
        """Trottoirs autour des routes"""
        t = self.t
        L = self.L
        W = 12  # Largeur trottoir
        
        t.fillcolor('#909090')
        t.pencolor('#707070')
        t.pensize(1)
        
        # Trottoirs verticaux (gauche et droite)
        for x_base in [-L - W, L]:
            for y_range in [(-400, -L - W), (L + W, 400)]:
                t.goto(x_base, y_range[0])
                t.pendown()
                t.begin_fill()
                t.goto(x_base + W, y_range[0])
                t.goto(x_base + W, y_range[1])
                t.goto(x_base, y_range[1])
                t.goto(x_base, y_range[0])
                t.end_fill()
                t.penup()
        
        # Trottoirs horizontaux (haut et bas)
        for y_base in [-L - W, L]:
            t.goto(-L - W, y_base)
            t.pendown()
            t.begin_fill()
            t.goto(L + W, y_base)
            t.goto(L + W, y_base + W)
            t.goto(-L - W, y_base + W)
            t.goto(-L - W, y_base)
            t.end_fill()
            t.penup()
    
    def _routes(self) -> None:
        """Routes principales"""
        t = self.t
        L = self.L
        
        t.fillcolor('#333333')
        t.pencolor('#222222')
        t.pensize(2)
        
        # Route verticale
        t.goto(-L, -400)
        t.pendown()
        t.begin_fill()
        t.goto(-L, 400)
        t.goto(L, 400)
        t.goto(L, -400)
        t.goto(-L, -400)
        t.end_fill()
        t.penup()
        
        # Route horizontale
        t.goto(-400, -L)
        t.pendown()
        t.begin_fill()
        t.goto(400, -L)
        t.goto(400, L)
        t.goto(-400, L)
        t.goto(-400, -L)
        t.end_fill()
        t.penup()
    
    def _marquages(self) -> None:
        """Lignes de marquage"""
        t = self.t
        L = self.L
        
        t.pencolor('#FFFFFF')
        t.pensize(3)
        
        # Lignes centrales verticales (pointillées)
        for y_start, y_end in [(-400, -L - 20), (L + 20, 400)]:
            y = y_start
            while y < y_end:
                t.goto(0, y)
                t.pendown()
                t.goto(0, min(y + 25, y_end))
                t.penup()
                y += 40
        
        # Lignes centrales horizontales (pointillées)
        for x_start, x_end in [(-400, -L - 20), (L + 20, 400)]:
            x = x_start
            while x < x_end:
                t.goto(x, 0)
                t.pendown()
                t.goto(min(x + 25, x_end), 0)
                t.penup()
                x += 40
    
    def _passages_pietons(self) -> None:
        """Passages piétons zébrés"""
        t = self.t
        L = self.L
        
        t.fillcolor('#FFFFFF')
        t.pencolor('#FFFFFF')
        
        # Passages Nord et Sud
        for y_pos in [L + 5, -L - 5]:
            x = -L + 10
            direction = 1 if y_pos > 0 else -1
            while x < L - 10:
                t.goto(x, y_pos)
                t.pendown()
                t.begin_fill()
                t.goto(x + 8, y_pos)
                t.goto(x + 8, y_pos + direction * 18)
                t.goto(x, y_pos + direction * 18)
                t.goto(x, y_pos)
                t.end_fill()
                t.penup()
                x += 14
        
        # Passages Est et Ouest
        for x_pos in [L + 5, -L - 5]:
            y = -L + 10
            direction = 1 if x_pos > 0 else -1
            while y < L - 10:
                t.goto(x_pos, y)
                t.pendown()
                t.begin_fill()
                t.goto(x_pos + direction * 18, y)
                t.goto(x_pos + direction * 18, y + 8)
                t.goto(x_pos, y + 8)
                t.goto(x_pos, y)
                t.end_fill()
                t.penup()
                y += 14
    
    def _lignes_arret(self) -> None:
        """Lignes d'arrêt blanches épaisses"""
        t = self.t
        L = self.L
        ligne = DIMENSIONS.ligne_arret
        
        t.pencolor('#FFFFFF')
        t.pensize(5)
        
        # Sud (voitures allant vers Nord)
        t.goto(-L + 5, -ligne)
        t.pendown()
        t.goto(-5, -ligne)
        t.penup()
        
        # Nord (voitures allant vers Sud)
        t.goto(5, ligne)
        t.pendown()
        t.goto(L - 5, ligne)
        t.penup()
        
        # Ouest (voitures allant vers Est)
        t.goto(-ligne, 5)
        t.pendown()
        t.goto(-ligne, L - 5)
        t.penup()
        
        # Est (voitures allant vers Ouest)
        t.goto(ligne, -L + 5)
        t.pendown()
        t.goto(ligne, -5)
        t.penup()
    
    def _ilot_central(self) -> None:
        """Îlot central rond"""
        t = self.t
        
        # Bordure
        t.goto(0, -25)
        t.fillcolor('#505050')
        t.pencolor('#404040')
        t.pensize(2)
        t.pendown()
        t.begin_fill()
        t.circle(25)
        t.end_fill()
        t.penup()
        
        # Herbe
        t.goto(0, -20)
        t.fillcolor('#228B22')
        t.pencolor('#1E7B1E')
        t.pendown()
        t.begin_fill()
        t.circle(20)
        t.end_fill()
        t.penup()
        
        # Centre
        t.goto(0, -8)
        t.fillcolor('#1E5631')
        t.pendown()
        t.begin_fill()
        t.circle(8)
        t.end_fill()
        t.penup()
    
    def _arbres(self) -> None:
        """Arbres décoratifs aux coins"""
        positions = [
            (-280, 280),
            (280, 280),
            (-280, -280),
            (280, -280),
        ]
        
        for x, y in positions:
            self._dessiner_arbre(x, y)
    
    def _dessiner_arbre(self, x: float, y: float) -> None:
        """Dessine un arbre simple"""
        t = self.t
        
        # Tronc
        t.goto(x - 4, y - 10)
        t.fillcolor('#8B4513')
        t.pencolor('#654321')
        t.pensize(1)
        t.pendown()
        t.begin_fill()
        t.goto(x + 4, y - 10)
        t.goto(x + 4, y + 5)
        t.goto(x - 4, y + 5)
        t.goto(x - 4, y - 10)
        t.end_fill()
        t.penup()
        
        # Feuillage
        t.goto(x, y + 5)
        t.fillcolor('#228B22')
        t.pencolor('#1E6B1E')
        t.pendown()
        t.begin_fill()
        t.circle(15)
        t.end_fill()
        t.penup()
    
    def effacer(self) -> None:
        self.t.clear()


class PanneauInfo:
    """Titre du carrefour"""
    
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