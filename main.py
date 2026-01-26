"""
main.py - Point d'entrée principal de l'application
Simulateur de Feu Tricolore - Ville de Thiès

Ce module coordonne tous les composants de la simulation:
- Interface graphique (Tkinter + Turtle)
- Gestion des feux tricolores
- Gestion des véhicules
- Journalisation des événements
"""

import turtle
import time
from typing import Optional

# Import des modules du projet
from database import DatabaseManager
from logger import Logger
from scenarios import Scenario, EtatFeu, Direction, get_config, COULEURS
from traffic_light import GestionnaireFeux
from vehicles import GestionnaireVoitures, Voiture
from turtle_scene import CarrefourScene, PanneauInfo
from gui import InterfaceGraphique, PanneauControle


class SimulateurCarrefour:
    """
    Classe principale du simulateur de carrefour.
    Coordonne tous les composants et gère la boucle de simulation.
    """
    
    # Constantes de timing
    FRAME_DELAY_MS = 50  # 20 FPS
    DT = 0.05  # Temps par frame en secondes
    
    def __init__(self):
        """Initialise le simulateur"""
        print("=" * 60)
        print("🚦 SIMULATEUR DE CARREFOUR - VILLE DE THIÈS")
        print("=" * 60)
        print("\nInitialisation en cours...")
        
        # État de la simulation
        self.en_cours: bool = False
        self.en_pause: bool = False
        self.scenario_actuel: Scenario = Scenario.NORMAL
        self.temps_debut: Optional[float] = None
        self.timer_id: Optional[str] = None
        
        # Compteurs
        self.total_voitures_generees: int = 0
        
        # Logger
        self.logger = Logger()
        print("[INIT] Logger initialisé ✓")
        
        # Interface graphique
        self.gui = InterfaceGraphique()
        print("[INIT] Interface graphique créée ✓")
        
        # Initialiser les callbacks
        callbacks = {
            'play': self._on_play,
            'pause': self._on_pause,
            'stop': self._on_stop,
            'reset': self._on_reset,
            'scenario_change': self._on_scenario_change,
            'feu_manuel': self._on_feu_manuel
        }
        self.panneau = self.gui.initialiser_panneau_controle(callbacks)
        print("[INIT] Panneau de contrôle initialisé ✓")
        
        # Initialiser Turtle
        self._initialiser_turtle()
        print("[INIT] Canvas Turtle initialisé ✓")
        
        # Initialiser les composants de simulation
        self._initialiser_simulation()
        print("[INIT] Composants de simulation initialisés ✓")
        
        # Dessiner la scène initiale
        self._dessiner_scene()
        print("[INIT] Scène dessinée ✓")
        
        # Configurer la fermeture
        self.gui.set_on_close(self._on_fermeture)
        
        print("\n✅ Initialisation terminée!")
        print("=" * 60)
    
    def _initialiser_turtle(self) -> None:
        """Initialise le canvas Turtle intégré à Tkinter"""
        canvas = self.gui.get_canvas()
        self.screen = turtle.TurtleScreen(canvas)
        self.screen.bgcolor(COULEURS.herbe)
        self.screen.tracer(0)  # Désactiver l'animation automatique
    
    def _initialiser_simulation(self) -> None:
        """Initialise les composants de la simulation"""
        # Callback pour les changements de feux
        def on_feu_change(voie: int, etat: EtatFeu):
            self.logger.log_feu_change(voie, etat.value, self.scenario_actuel.value)
            self._update_affichage_feux()
        
        # Gestionnaire des feux
        self.gestionnaire_feux = GestionnaireFeux(on_change_callback=on_feu_change)
        
        # Gestionnaire des voitures
        self.gestionnaire_voitures = GestionnaireVoitures(self.gestionnaire_feux)
        self.gestionnaire_voitures.on_event_callback = self._on_vehicule_event
        
        # Scène du carrefour
        self.scene = CarrefourScene(self.screen)
        
        # Panneau d'info
        self.panneau_info = PanneauInfo(self.screen)
    
    def _dessiner_scene(self) -> None:
        """Dessine la scène complète"""
        self.scene.dessiner()
        self.gestionnaire_feux.dessiner_tous()
        self.panneau_info.dessiner_titre("Carrefour de Thiès")
        self.screen.update()
        self._update_affichage_feux()
    
    # ========================================================================
    # CALLBACKS DES ÉVÉNEMENTS VÉHICULES
    # ========================================================================
    
    def _on_vehicule_event(self, event_type: str, voiture: Voiture) -> None:
        """
        Gère les événements des véhicules pour le logging.
        
        Args:
            event_type: Type d'événement ('apparition', 'arret', 'redemarrage', 'sortie')
            voiture: Voiture concernée
        """
        etat_feu = self.gestionnaire_feux.get_etat_pour_direction(voiture.direction)
        scenario = self.scenario_actuel.value
        
        if event_type == 'apparition':
            self.total_voitures_generees += 1
            self.logger.log_voiture_apparition(
                voiture.id, voiture.direction.value,
                voiture.x, voiture.y,
                etat_feu.value, scenario
            )
        
        elif event_type == 'arret':
            self.logger.log_voiture_arret(
                voiture.id, voiture.direction.value,
                voiture.x, voiture.y,
                etat_feu.value, scenario
            )
        
        elif event_type == 'redemarrage':
            self.logger.log_voiture_redemarrage(
                voiture.id, voiture.direction.value,
                voiture.x, voiture.y, voiture.vitesse,
                etat_feu.value, scenario
            )
        
        elif event_type == 'sortie':
            self.logger.log_voiture_sortie(
                voiture.id, voiture.direction.value,
                voiture.x, voiture.y, voiture.vitesse,
                etat_feu.value, scenario
            )
    
    # ========================================================================
    # CALLBACKS DES BOUTONS
    # ========================================================================
    
    def _on_play(self) -> None:
        """Démarre ou reprend la simulation"""
        if not self.en_cours:
            # Démarrage
            self.en_cours = True
            self.en_pause = False
            self.temps_debut = time.time()
            self.total_voitures_generees = 0
            
            # Logger
            self.logger.start_session(self.scenario_actuel.value)
            self.logger.log_action_utilisateur(
                "Démarrage simulation",
                self.scenario_actuel.value
            )
            
            print(f"\n▶ Simulation démarrée - Scénario: {self.scenario_actuel.value}")
            
            # Lancer la boucle
            self._boucle_simulation()
        
        elif self.en_pause:
            # Reprise
            self.en_pause = False
            self.logger.resume_session(self.scenario_actuel.value)
            self.logger.log_action_utilisateur(
                "Reprise simulation",
                self.scenario_actuel.value
            )
            
            print("\n▶ Simulation reprise")
            
            # Relancer la boucle
            self._boucle_simulation()
        
        self.panneau.update_status("En cours", self.en_cours, self.en_pause)
    
    def _on_pause(self) -> None:
        """Met en pause la simulation"""
        if self.en_cours and not self.en_pause:
            self.en_pause = True
            
            # Annuler le timer
            if self.timer_id:
                self.gui.after_cancel(self.timer_id)
                self.timer_id = None
            
            # Logger
            self.logger.pause_session(self.scenario_actuel.value)
            self.logger.log_action_utilisateur(
                "Pause simulation",
                self.scenario_actuel.value
            )
            
            print("\n⏸ Simulation en pause")
            
            self.panneau.update_status("Pause", self.en_cours, self.en_pause)
    
    def _on_stop(self) -> None:
        """Arrête la simulation"""
        if self.en_cours:
            self.en_cours = False
            self.en_pause = False
            
            # Annuler le timer
            if self.timer_id:
                self.gui.after_cancel(self.timer_id)
                self.timer_id = None
            
            # Logger
            self.logger.log_action_utilisateur(
                "Arrêt simulation",
                self.scenario_actuel.value
            )
            self.logger.end_session()
            
            print("\n⏹ Simulation arrêtée")
            
            self.panneau.update_status("Arrêté", self.en_cours, self.en_pause)
    
    def _on_reset(self) -> None:
        """Réinitialise la simulation"""
        # Arrêter si en cours
        if self.en_cours:
            self._on_stop()
        
        # Logger
        self.logger.reset_session(self.scenario_actuel.value)
        self.logger.log_action_utilisateur(
            "Réinitialisation",
            self.scenario_actuel.value
        )
        
        # Supprimer toutes les voitures
        self.gestionnaire_voitures.reinitialiser()
        
        # Réinitialiser les feux
        self.gestionnaire_feux.reinitialiser()
        self.gestionnaire_feux.changer_scenario(self.scenario_actuel)
        
        # Réinitialiser les compteurs
        self.temps_debut = None
        self.total_voitures_generees = 0
        
        # Redessiner
        self._dessiner_scene()
        
        # Mettre à jour l'affichage
        self._update_affichage_feux()
        self.panneau.update_stats(0, 0, self.scenario_actuel.value)
        self.panneau.update_status("Arrêté", False, False)
        
        print("\n🔄 Simulation réinitialisée")
    
    def _on_scenario_change(self, scenario_name: str) -> None:
        """
        Gère le changement de scénario.
        
        Args:
            scenario_name: Nom du nouveau scénario
        """
        # Trouver le scénario correspondant
        ancien = self.scenario_actuel
        
        for s in Scenario:
            if s.value == scenario_name:
                self.scenario_actuel = s
                break
        
        # Appliquer le changement
        self.gestionnaire_feux.changer_scenario(self.scenario_actuel)
        self.gestionnaire_voitures.changer_scenario(self.scenario_actuel)
        
        # Logger
        self.logger.log_scenario_change(ancien.value, self.scenario_actuel.value)
        
        # Mettre à jour l'affichage
        self._update_affichage_feux()
        
        print(f"\n📋 Scénario changé: {ancien.value} → {self.scenario_actuel.value}")
    
    def _on_feu_manuel(self, voie: int, etat: EtatFeu) -> None:
        """
        Gère le contrôle manuel des feux.
        
        Args:
            voie: Numéro de la voie (1 ou 2)
            etat: État à forcer
        """
        self.gestionnaire_feux.forcer_etat(voie, etat)
        
        # Logger
        self.logger.log_feu_manuel(voie, etat.value, self.scenario_actuel.value)
        
        # Mettre à jour l'affichage
        self._update_affichage_feux()
        
        print(f"\n🎮 Feu manuel: Voie {voie} → {etat.value}")
    
    # ========================================================================
    # BOUCLE DE SIMULATION
    # ========================================================================
    
    def _boucle_simulation(self) -> None:
        """Boucle principale de la simulation"""
        if not self.en_cours or self.en_pause:
            return
        
        # Mettre à jour les feux
        self.gestionnaire_feux.update(self.DT)
        
        # Générer des voitures aléatoirement
        nouvelle_voiture = self.gestionnaire_voitures.generer_aleatoire()
        if nouvelle_voiture:
            self._on_vehicule_event('apparition', nouvelle_voiture)
        
        # Mettre à jour les voitures
        self.gestionnaire_voitures.update(self.DT)
        
        # Dessiner les voitures
        self.gestionnaire_voitures.dessiner_toutes()
        
        # Mettre à jour l'écran
        self.screen.update()
        
        # Mettre à jour les statistiques
        self._update_stats()
        
        # Mettre à jour l'affichage des feux
        self._update_affichage_feux()
        
        # Planifier la prochaine frame
        self.timer_id = self.gui.after(self.FRAME_DELAY_MS, self._boucle_simulation)
    
    # ========================================================================
    # MISES À JOUR DE L'AFFICHAGE
    # ========================================================================
    
    def _update_affichage_feux(self) -> None:
        """Met à jour l'affichage des états des feux"""
        etat_v1 = self.gestionnaire_feux.etat_voie1
        etat_v2 = self.gestionnaire_feux.etat_voie2
        self.panneau.update_etat_feux(etat_v1, etat_v2)
    
    def _update_stats(self) -> None:
        """Met à jour les statistiques affichées"""
        nb_voitures = self.gestionnaire_voitures.get_nombre_voitures()
        
        temps_ecoule = 0
        if self.temps_debut:
            temps_ecoule = int(time.time() - self.temps_debut)
        
        self.panneau.update_stats(
            nb_voitures,
            temps_ecoule,
            self.scenario_actuel.value
        )
    
    # ========================================================================
    # GESTION DE LA FERMETURE
    # ========================================================================
    
    def _on_fermeture(self) -> None:
        """Gère la fermeture propre de l'application"""
        print("\n" + "=" * 60)
        print("Fermeture de l'application...")
        
        # Arrêter la simulation si en cours
        if self.en_cours:
            self.en_cours = False
            self.logger.end_session()
        
        # Fermer le logger
        self.logger.close()
        
        # Afficher les statistiques finales
        try:
            stats = DatabaseManager().get_statistics()
            print("\n📊 Statistiques de la base de données:")
            for table, count in stats.items():
                print(f"   - {table}: {count} enregistrements")
        except:
            pass
        
        print("\n👋 Au revoir!")
        print("=" * 60)
        
        # Fermer la fenêtre
        self.gui.destroy()
    
    # ========================================================================
    # LANCEMENT
    # ========================================================================
    
    def run(self) -> None:
        """Lance l'application"""
        print("\n🚀 Lancement de l'interface graphique...")
        print("   Utilisez le panneau de contrôle pour gérer la simulation.")
        print("   Fermez la fenêtre pour quitter.\n")
        
        self.gui.run()


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

def main():
    """Point d'entrée principal"""
    try:
        app = SimulateurCarrefour()
        app.run()
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    exit(main())