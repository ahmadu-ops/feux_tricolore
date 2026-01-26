"""
logger.py - Journalisation des événements de simulation
Projet Feu Tricolore - Ville de Thiès
"""

from datetime import datetime
from typing import Optional
from database import DatabaseManager, EvenementDAO, VehiculeEventDAO, SessionDAO


class Logger:
    """
    Classe principale de journalisation.
    Interface simplifiée pour enregistrer tous les événements de la simulation.
    """
    
    def __init__(self, db_path: str = "traffic_simulation.db"):
        """
        Initialise le logger.
        
        Args:
            db_path: Chemin vers la base de données SQLite
        """
        self.db = DatabaseManager(db_path)
        self.evt_dao = EvenementDAO(self.db)
        self.veh_dao = VehiculeEventDAO(self.db)
        self.session_dao = SessionDAO(self.db)
        
        # Session courante
        self.current_session_id: Optional[int] = None
        self.session_start_time: Optional[datetime] = None
        self.vehicle_count: int = 0
        
        print("[LOGGER] Logger initialisé")
    
    # ========================================================================
    # GESTION DES SESSIONS
    # ========================================================================
    
    def start_session(self, scenario: str) -> int:
        """
        Démarre une nouvelle session de simulation.
        
        Args:
            scenario: Nom du scénario initial
            
        Returns:
            ID de la session créée
        """
        self.session_start_time = datetime.now()
        self.vehicle_count = 0
        self.current_session_id = self.session_dao.start_session(scenario)
        
        # Log l'événement de démarrage
        self.evt_dao.insert(
            type_action="SIMULATION",
            action="Démarrage de la simulation",
            scenario=scenario,
            details=f"Session ID: {self.current_session_id}"
        )
        
        print(f"[LOGGER] Session {self.current_session_id} démarrée - Scénario: {scenario}")
        return self.current_session_id
    
    def end_session(self) -> None:
        """Termine la session courante"""
        if self.current_session_id is None:
            print("[LOGGER] Aucune session active à terminer")
            return
        
        # Calculer la durée
        duree = 0.0
        if self.session_start_time:
            duree = (datetime.now() - self.session_start_time).total_seconds()
        
        # Mettre à jour la session
        self.session_dao.end_session(
            self.current_session_id,
            duree,
            self.vehicle_count
        )
        
        # Log l'événement de fin
        self.evt_dao.insert(
            type_action="SIMULATION",
            action="Arrêt de la simulation",
            details=f"Durée: {duree:.1f}s, Voitures: {self.vehicle_count}"
        )
        
        print(f"[LOGGER] Session {self.current_session_id} terminée - "
              f"Durée: {duree:.1f}s, Voitures: {self.vehicle_count}")
        
        # Réinitialiser
        self.current_session_id = None
        self.session_start_time = None
    
    def pause_session(self, scenario: str) -> None:
        """
        Log la mise en pause de la simulation.
        
        Args:
            scenario: Scénario actif
        """
        self.evt_dao.insert(
            type_action="SIMULATION",
            action="Pause de la simulation",
            scenario=scenario
        )
        print("[LOGGER] Simulation en pause")
    
    def resume_session(self, scenario: str) -> None:
        """
        Log la reprise de la simulation.
        
        Args:
            scenario: Scénario actif
        """
        self.evt_dao.insert(
            type_action="SIMULATION",
            action="Reprise de la simulation",
            scenario=scenario
        )
        print("[LOGGER] Simulation reprise")
    
    def reset_session(self, scenario: str) -> None:
        """
        Log la réinitialisation de la simulation.
        
        Args:
            scenario: Scénario actif
        """
        self.evt_dao.insert(
            type_action="SIMULATION",
            action="Réinitialisation de la simulation",
            scenario=scenario
        )
        print("[LOGGER] Simulation réinitialisée")
    
    # ========================================================================
    # ÉVÉNEMENTS DES FEUX TRICOLORES
    # ========================================================================
    
    def log_feu_change(self, voie: int, nouvel_etat: str, 
                       scenario: str, ancien_etat: str = None) -> None:
        """
        Log un changement d'état du feu tricolore.
        
        Args:
            voie: Numéro de la voie (1 ou 2)
            nouvel_etat: Nouvel état du feu
            scenario: Scénario actif
            ancien_etat: Ancien état (optionnel)
        """
        details = None
        if ancien_etat:
            details = f"Transition: {ancien_etat} -> {nouvel_etat}"
        
        self.evt_dao.insert(
            type_action="FEU_TRICOLORE",
            action=f"Changement Voie {voie} -> {nouvel_etat}",
            etat_feu_voie1=nouvel_etat if voie == 1 else None,
            etat_feu_voie2=nouvel_etat if voie == 2 else None,
            scenario=scenario,
            details=details
        )
    
    def log_feu_clignotant(self, allume: bool, scenario: str) -> None:
        """
        Log l'état du clignotement en mode nuit.
        
        Args:
            allume: True si le feu est allumé
            scenario: Scénario actif
        """
        etat = "ALLUMÉ" if allume else "ÉTEINT"
        self.evt_dao.insert(
            type_action="FEU_TRICOLORE",
            action=f"Clignotement orange: {etat}",
            scenario=scenario
        )
    
    # ========================================================================
    # ÉVÉNEMENTS DES SCÉNARIOS
    # ========================================================================
    
    def log_scenario_change(self, ancien: str, nouveau: str) -> None:
        """
        Log un changement de scénario.
        
        Args:
            ancien: Ancien scénario
            nouveau: Nouveau scénario
        """
        self.evt_dao.insert(
            type_action="SCENARIO",
            action=f"Changement de scénario",
            scenario=nouveau,
            details=f"{ancien} -> {nouveau}"
        )
        print(f"[LOGGER] Scénario changé: {ancien} -> {nouveau}")
    
    # ========================================================================
    # ÉVÉNEMENTS DES VÉHICULES
    # ========================================================================
    
    def log_voiture_apparition(self, id_voiture: int, direction: str,
                                x: float, y: float,
                                etat_feu: str, scenario: str) -> None:
        """
        Log l'apparition d'une nouvelle voiture.
        
        Args:
            id_voiture: Identifiant unique de la voiture
            direction: Direction de la voiture
            x: Position X initiale
            y: Position Y initiale
            etat_feu: État du feu pour cette direction
            scenario: Scénario actif
        """
        self.vehicle_count += 1
        self.veh_dao.insert(
            action="Apparition",
            id_voiture=id_voiture,
            direction=direction,
            position_x=x,
            position_y=y,
            vitesse=0.0,
            etat_feu=etat_feu,
            scenario=scenario
        )
    
    def log_voiture_arret(self, id_voiture: int, direction: str,
                          x: float, y: float,
                          etat_feu: str, scenario: str) -> None:
        """
        Log l'arrêt d'une voiture au feu rouge.
        
        Args:
            id_voiture: Identifiant de la voiture
            direction: Direction de la voiture
            x: Position X
            y: Position Y
            etat_feu: État du feu
            scenario: Scénario actif
        """
        self.veh_dao.insert(
            action="Arrêt au feu rouge",
            id_voiture=id_voiture,
            direction=direction,
            position_x=x,
            position_y=y,
            vitesse=0.0,
            etat_feu=etat_feu,
            scenario=scenario
        )
    
    def log_voiture_redemarrage(self, id_voiture: int, direction: str,
                                 x: float, y: float, vitesse: float,
                                 etat_feu: str, scenario: str) -> None:
        """
        Log le redémarrage d'une voiture.
        
        Args:
            id_voiture: Identifiant de la voiture
            direction: Direction de la voiture
            x: Position X
            y: Position Y
            vitesse: Vitesse au redémarrage
            etat_feu: État du feu
            scenario: Scénario actif
        """
        self.veh_dao.insert(
            action="Redémarrage",
            id_voiture=id_voiture,
            direction=direction,
            position_x=x,
            position_y=y,
            vitesse=vitesse,
            etat_feu=etat_feu,
            scenario=scenario
        )
    
    def log_voiture_sortie(self, id_voiture: int, direction: str,
                           x: float, y: float, vitesse: float,
                           etat_feu: str, scenario: str) -> None:
        """
        Log la sortie d'une voiture de l'écran.
        
        Args:
            id_voiture: Identifiant de la voiture
            direction: Direction de la voiture
            x: Position X de sortie
            y: Position Y de sortie
            vitesse: Vitesse à la sortie
            etat_feu: État du feu
            scenario: Scénario actif
        """
        self.veh_dao.insert(
            action="Sortie écran",
            id_voiture=id_voiture,
            direction=direction,
            position_x=x,
            position_y=y,
            vitesse=vitesse,
            etat_feu=etat_feu,
            scenario=scenario
        )
    
    # ========================================================================
    # ACTIONS UTILISATEUR
    # ========================================================================
    
    def log_action_utilisateur(self, action: str, scenario: str,
                                details: str = None) -> None:
        """
        Log une action de l'utilisateur.
        
        Args:
            action: Description de l'action
            scenario: Scénario actif
            details: Détails supplémentaires
        """
        self.evt_dao.insert(
            type_action="UTILISATEUR",
            action=action,
            scenario=scenario,
            details=details
        )
        print(f"[LOGGER] Action utilisateur: {action}")
    
    def log_feu_manuel(self, voie: int, etat: str, scenario: str) -> None:
        """
        Log un changement manuel de feu.
        
        Args:
            voie: Numéro de la voie
            etat: Nouvel état forcé
            scenario: Scénario actif
        """
        self.evt_dao.insert(
            type_action="UTILISATEUR",
            action=f"Changement manuel Voie {voie} -> {etat}",
            etat_feu_voie1=etat if voie == 1 else None,
            etat_feu_voie2=etat if voie == 2 else None,
            scenario=scenario
        )
        print(f"[LOGGER] Feu manuel: Voie {voie} -> {etat}")
    
    # ========================================================================
    # UTILITAIRES
    # ========================================================================
    
    def get_recent_events(self, limit: int = 20) -> list:
        """
        Récupère les événements récents.
        
        Args:
            limit: Nombre maximum d'événements
            
        Returns:
            Liste des événements
        """
        return self.evt_dao.get_recent(limit)
    
    def get_vehicle_events(self, limit: int = 50) -> list:
        """
        Récupère les événements véhicules récents.
        
        Args:
            limit: Nombre maximum d'événements
            
        Returns:
            Liste des événements véhicules
        """
        return self.veh_dao.get_recent(limit)
    
    def get_session_history(self) -> list:
        """
        Récupère l'historique des sessions.
        
        Returns:
            Liste des sessions
        """
        return self.session_dao.get_all()
    
    def get_statistics(self) -> dict:
        """
        Récupère les statistiques de la base de données.
        
        Returns:
            Dictionnaire des statistiques
        """
        return self.db.get_statistics()
    
    def close(self) -> None:
        """Ferme le logger et la base de données"""
        if self.current_session_id:
            self.end_session()
        self.db.close()
        print("[LOGGER] Logger fermé")


# ============================================================================
# TEST DU MODULE
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE logger.py")
    print("=" * 60)
    
    # Créer un logger de test
    logger = Logger("test_logger.db")
    
    # Test session
    logger.start_session("Circulation normale")
    
    # Test événements feux
    logger.log_feu_change(1, "VERT", "Circulation normale")
    logger.log_feu_change(2, "ROUGE", "Circulation normale")
    
    # Test événements véhicules
    logger.log_voiture_apparition(1, "NORD", -30, -400, "VERT", "Circulation normale")
    logger.log_voiture_arret(1, "NORD", -30, -70, "ROUGE", "Circulation normale")
    logger.log_voiture_redemarrage(1, "NORD", -30, -70, 2.5, "VERT", "Circulation normale")
    logger.log_voiture_sortie(1, "NORD", -30, 450, 3.0, "VERT", "Circulation normale")
    
    # Test changement scénario
    logger.log_scenario_change("Circulation normale", "Heure de pointe")
    
    # Test actions utilisateur
    logger.log_action_utilisateur("Clic sur Pause", "Heure de pointe")
    logger.log_feu_manuel(1, "ROUGE", "Mode manuel")
    
    # Afficher les statistiques
    print("\n[TEST] Statistiques:")
    stats = logger.get_statistics()
    for table, count in stats.items():
        print(f"  - {table}: {count} enregistrements")
    
    # Afficher les événements récents
    print("\n[TEST] Événements récents:")
    events = logger.get_recent_events(5)
    for evt in events:
        print(f"  - [{evt['type_action']}] {evt['action']}")
    
    # Terminer la session
    logger.end_session()
    
    # Fermer
    logger.close()
    
    # Nettoyage
    import os
    if os.path.exists("test_logger.db"):
        os.remove("test_logger.db")
    
    print("\n[TEST] Tests terminés avec succès ✅")