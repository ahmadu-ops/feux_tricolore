"""
main.py - Point d'entrée principal
Simulateur de Feu Tricolore - Ville de Thiès
"""

import turtle
import time
from typing import Optional

from database import DatabaseManager
from logger import Logger
from scenarios import Scenario, EtatFeu, COULEURS
from traffic_light import GestionnaireFeux
from vehicles import GestionnaireVoitures, Voiture
from turtle_scene import CarrefourScene, PanneauInfo
from gui import InterfaceGraphique


class SimulateurCarrefour:
    """Simulateur principal"""
    
    FPS = 20
    FRAME_MS = 1000 // FPS
    DT = 1.0 / FPS
    
    def __init__(self):
        print("=" * 50)
        print("🚦 SIMULATEUR DE CARREFOUR - THIÈS")
        print("=" * 50)
        
        # États
        self.en_cours = False
        self.en_pause = False
        self.scenario = Scenario.NORMAL
        self.temps_debut: Optional[float] = None
        self.timer_id: Optional[str] = None
        
        # Logger
        self.logger = Logger()
        
        # GUI
        self.gui = InterfaceGraphique()
        
        callbacks = {
            'play': self._play,
            'pause': self._pause,
            'stop': self._stop,
            'reset': self._reset,
            'scenario_change': self._scenario_change,
            'feu_manuel': self._feu_manuel
        }
        self.panneau = self.gui.initialiser_panneau(callbacks)
        
        # Turtle
        self._init_turtle()
        
        # Simulation
        self._init_simulation()
        
        # Dessiner
        self._dessiner()
        
        # Fermeture
        self.gui.set_on_close(self._fermer)
        
        print("\n✅ Prêt!")
        print("   F11 = Plein écran | Échap = Quitter plein écran")
        print("=" * 50)
    
    def _init_turtle(self) -> None:
        """Initialise Turtle dans le canvas"""
        canvas = self.gui.get_canvas()
        self.screen = turtle.TurtleScreen(canvas)
        self.screen.bgcolor(COULEURS.herbe)
        self.screen.tracer(0)
        
        # Coordonnées centrées
        size = self.gui.get_canvas_size()
        half = size // 2
        self.screen.setworldcoordinates(-half, -half, half, half)
    
    def _init_simulation(self) -> None:
        """Initialise les composants"""
        
        def on_feu(voie, etat):
            self.logger.log_feu_change(voie, etat.value, self.scenario.value)
            self._update_feux_ui()
        
        self.feux = GestionnaireFeux(self.screen, on_feu)
        self.voitures = GestionnaireVoitures(self.screen, self.feux)
        self.voitures.on_event_callback = self._on_voiture_event
        
        self.scene = CarrefourScene(self.screen)
        self.titre = PanneauInfo(self.screen)
    
    def _dessiner(self) -> None:
        """Dessine la scène"""
        self.scene.dessiner()
        self.feux.dessiner_tous()
        self.titre.dessiner_titre()
        self.screen.update()
        self._update_feux_ui()
    
    def _on_voiture_event(self, event: str, v: Voiture) -> None:
        """Callback événement voiture"""
        etat = self.feux.get_etat_pour_direction(v.direction)
        sc = self.scenario.value
        
        if event == 'apparition':
            self.logger.log_voiture_apparition(v.id, v.direction.value, v.x, v.y, etat.value, sc)
        elif event == 'arret':
            self.logger.log_voiture_arret(v.id, v.direction.value, v.x, v.y, etat.value, sc)
        elif event == 'redemarrage':
            self.logger.log_voiture_redemarrage(v.id, v.direction.value, v.x, v.y, v.vitesse, etat.value, sc)
        elif event == 'sortie':
            self.logger.log_voiture_sortie(v.id, v.direction.value, v.x, v.y, v.vitesse, etat.value, sc)
    
    # === CONTRÔLES ===
    
    def _play(self) -> None:
        if not self.en_cours:
            self.en_cours = True
            self.en_pause = False
            self.temps_debut = time.time()
            self.logger.start_session(self.scenario.value)
            self._boucle()
        elif self.en_pause:
            self.en_pause = False
            self.logger.resume_session(self.scenario.value)
            self._boucle()
        
        self.panneau.update_status(self.en_cours, self.en_pause)
    
    def _pause(self) -> None:
        if self.en_cours and not self.en_pause:
            self.en_pause = True
            if self.timer_id:
                self.gui.after_cancel(self.timer_id)
            self.logger.pause_session(self.scenario.value)
            self.panneau.update_status(self.en_cours, self.en_pause)
    
    def _stop(self) -> None:
        if self.en_cours:
            self.en_cours = False
            self.en_pause = False
            if self.timer_id:
                self.gui.after_cancel(self.timer_id)
            self.logger.end_session()
            self.panneau.update_status(self.en_cours, self.en_pause)
    
    def _reset(self) -> None:
        self._stop()
        self.voitures.reinitialiser()
        self.feux.reinitialiser()
        self.feux.changer_scenario(self.scenario)
        self.temps_debut = None
        self._dessiner()
        self.panneau.update_stats(0, 0)
    
    def _scenario_change(self, nom: str) -> None:
        ancien = self.scenario
        for s in Scenario:
            if s.value == nom:
                self.scenario = s
                break
        
        self.feux.changer_scenario(self.scenario)
        self.voitures.changer_scenario(self.scenario)
        self.logger.log_scenario_change(ancien.value, self.scenario.value)
        self._update_feux_ui()
    
    def _feu_manuel(self, voie: int, etat: EtatFeu) -> None:
        self.feux.forcer_etat(voie, etat)
        self.logger.log_feu_manuel(voie, etat.value, self.scenario.value)
        self._update_feux_ui()
    
    # === BOUCLE ===
    
    def _boucle(self) -> None:
        if not self.en_cours or self.en_pause:
            return
        
        # Update feux
        self.feux.update(self.DT)
        
        # Générer voitures
        nouvelle = self.voitures.generer_aleatoire()
        if nouvelle:
            self._on_voiture_event('apparition', nouvelle)
        
        # Update voitures
        self.voitures.update(self.DT)
        
        # Dessiner
        self.voitures.dessiner_toutes()
        self.screen.update()
        
        # UI
        self._update_stats()
        self._update_feux_ui()
        
        # Next
        self.timer_id = self.gui.after(self.FRAME_MS, self._boucle)
    
    def _update_feux_ui(self) -> None:
        self.panneau.update_etat_feux(self.feux.etat_voie1, self.feux.etat_voie2)
    
    def _update_stats(self) -> None:
        nb = self.voitures.get_nombre()
        temps = int(time.time() - self.temps_debut) if self.temps_debut else 0
        self.panneau.update_stats(nb, temps)
    
    def _fermer(self) -> None:
        print("\nFermeture...")
        if self.en_cours:
            self.logger.end_session()
        self.logger.close()
        self.gui.destroy()
    
    def run(self) -> None:
        print("\n🚀 Démarrage de l'interface...")
        self.gui.run()


def main():
    try:
        app = SimulateurCarrefour()
        app.run()
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    exit(main())