"""
database.py - Gestion de la base de données SQLite
Projet Feu Tricolore - Ville de Thiès
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
import threading


class DatabaseManager:
    """
    Gestionnaire de base de données SQLite.
    Implémente le pattern Singleton pour une connexion unique.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, db_path: str = "traffic_simulation.db"):
        """Pattern Singleton thread-safe"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path: str = "traffic_simulation.db"):
        """
        Initialise la connexion à la base de données.
        
        Args:
            db_path: Chemin vers le fichier SQLite
        """
        if self._initialized:
            return
            
        self._initialized = True
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self._connect()
        self._create_tables()
    
    def _connect(self) -> None:
        """Établit la connexion à la base de données"""
        try:
            self.connection = sqlite3.connect(
                self.db_path, 
                check_same_thread=False
            )
            self.connection.row_factory = sqlite3.Row
            print(f"[DATABASE] Connexion établie : {self.db_path}")
        except sqlite3.Error as e:
            print(f"[DATABASE] Erreur de connexion : {e}")
            raise
    
    def _create_tables(self) -> None:
        """Crée les tables nécessaires si elles n'existent pas"""
        try:
            cursor = self.connection.cursor()
            
            # Table des événements généraux (simulation, feux, scénarios)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS evenements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    type_action TEXT NOT NULL,
                    action TEXT NOT NULL,
                    etat_feu_voie1 TEXT,
                    etat_feu_voie2 TEXT,
                    scenario TEXT,
                    details TEXT
                )
            ''')
            
            # Table des événements véhicules
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS evenements_vehicules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    type_action TEXT NOT NULL,
                    action TEXT NOT NULL,
                    etat_feu TEXT,
                    scenario TEXT,
                    id_voiture INTEGER,
                    direction TEXT,
                    position_x REAL,
                    position_y REAL,
                    vitesse REAL
                )
            ''')
            
            # Table des sessions de simulation
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    debut TEXT NOT NULL,
                    fin TEXT,
                    scenario_initial TEXT,
                    duree_secondes REAL,
                    nb_voitures_total INTEGER DEFAULT 0
                )
            ''')
            
            self.connection.commit()
            print("[DATABASE] Tables créées/vérifiées avec succès")
            
        except sqlite3.Error as e:
            print(f"[DATABASE] Erreur création tables : {e}")
            raise
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """
        Exécute une requête SQL.
        
        Args:
            query: Requête SQL
            params: Paramètres de la requête
            
        Returns:
            Curseur SQLite
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor
        except sqlite3.Error as e:
            print(f"[DATABASE] Erreur requête : {e}")
            print(f"[DATABASE] Requête : {query}")
            raise
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """
        Exécute une requête SELECT et retourne tous les résultats.
        
        Args:
            query: Requête SQL SELECT
            params: Paramètres de la requête
            
        Returns:
            Liste des résultats
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[DATABASE] Erreur fetch : {e}")
            return []
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """
        Exécute une requête SELECT et retourne un seul résultat.
        
        Args:
            query: Requête SQL SELECT
            params: Paramètres de la requête
            
        Returns:
            Résultat unique ou None
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"[DATABASE] Erreur fetch_one : {e}")
            return None
    
    def get_last_insert_id(self) -> int:
        """Retourne l'ID du dernier enregistrement inséré"""
        cursor = self.connection.cursor()
        return cursor.lastrowid
    
    def clear_table(self, table_name: str) -> None:
        """
        Vide une table.
        
        Args:
            table_name: Nom de la table à vider
        """
        try:
            self.execute(f"DELETE FROM {table_name}")
            print(f"[DATABASE] Table '{table_name}' vidée")
        except sqlite3.Error as e:
            print(f"[DATABASE] Erreur clear_table : {e}")
    
    def clear_all(self) -> None:
        """Vide toutes les tables"""
        tables = ['evenements', 'evenements_vehicules', 'sessions']
        for table in tables:
            self.clear_table(table)
        print("[DATABASE] Toutes les tables vidées")
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Retourne des statistiques sur la base de données.
        
        Returns:
            Dictionnaire avec les statistiques
        """
        stats = {}
        tables = ['evenements', 'evenements_vehicules', 'sessions']
        
        for table in tables:
            result = self.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
            stats[table] = result['count'] if result else 0
        
        return stats
    
    def close(self) -> None:
        """Ferme la connexion à la base de données"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self._initialized = False
            DatabaseManager._instance = None
            print("[DATABASE] Connexion fermée")
    
    def __del__(self):
        """Destructeur - ferme la connexion"""
        self.close()


# ============================================================================
# CLASSES POUR LES OPÉRATIONS SPÉCIFIQUES
# ============================================================================

class EvenementDAO:
    """
    Data Access Object pour les événements généraux.
    Gère les opérations CRUD sur la table 'evenements'.
    """
    
    def __init__(self, db: DatabaseManager):
        """
        Initialise le DAO.
        
        Args:
            db: Instance du gestionnaire de base de données
        """
        self.db = db
    
    @staticmethod
    def _get_timestamp() -> str:
        """Retourne le timestamp actuel formaté"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def insert(self, type_action: str, action: str,
               etat_feu_voie1: str = None, etat_feu_voie2: str = None,
               scenario: str = None, details: str = None) -> int:
        """
        Insère un nouvel événement.
        
        Args:
            type_action: Type d'action (SIMULATION, FEU, SCENARIO, UTILISATEUR)
            action: Description de l'action
            etat_feu_voie1: État du feu voie 1
            etat_feu_voie2: État du feu voie 2
            scenario: Scénario actif
            details: Détails supplémentaires
            
        Returns:
            ID de l'événement créé
        """
        query = '''
            INSERT INTO evenements 
            (timestamp, type_action, action, etat_feu_voie1, etat_feu_voie2, scenario, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        cursor = self.db.execute(
            query,
            (self._get_timestamp(), type_action, action,
             etat_feu_voie1, etat_feu_voie2, scenario, details)
        )
        return cursor.lastrowid
    
    def get_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Récupère les événements récents.
        
        Args:
            limit: Nombre maximum d'événements
            
        Returns:
            Liste des événements
        """
        query = "SELECT * FROM evenements ORDER BY id DESC LIMIT ?"
        rows = self.db.fetch_all(query, (limit,))
        return [dict(row) for row in rows]
    
    def get_by_type(self, type_action: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Récupère les événements par type.
        
        Args:
            type_action: Type d'action à filtrer
            limit: Nombre maximum d'événements
            
        Returns:
            Liste des événements filtrés
        """
        query = "SELECT * FROM evenements WHERE type_action = ? ORDER BY id DESC LIMIT ?"
        rows = self.db.fetch_all(query, (type_action, limit))
        return [dict(row) for row in rows]


class VehiculeEventDAO:
    """
    Data Access Object pour les événements véhicules.
    Gère les opérations CRUD sur la table 'evenements_vehicules'.
    """
    
    def __init__(self, db: DatabaseManager):
        """
        Initialise le DAO.
        
        Args:
            db: Instance du gestionnaire de base de données
        """
        self.db = db
    
    @staticmethod
    def _get_timestamp() -> str:
        """Retourne le timestamp actuel formaté"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def insert(self, action: str, id_voiture: int, direction: str,
               position_x: float, position_y: float, vitesse: float,
               etat_feu: str, scenario: str) -> int:
        """
        Insère un événement véhicule.
        
        Args:
            action: Type d'action (Apparition, Arrêt, Redémarrage, Sortie)
            id_voiture: Identifiant de la voiture
            direction: Direction (NORD, SUD, EST, OUEST)
            position_x: Position X
            position_y: Position Y
            vitesse: Vitesse actuelle
            etat_feu: État du feu
            scenario: Scénario actif
            
        Returns:
            ID de l'événement créé
        """
        query = '''
            INSERT INTO evenements_vehicules 
            (timestamp, type_action, action, etat_feu, scenario,
             id_voiture, direction, position_x, position_y, vitesse)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor = self.db.execute(
            query,
            (self._get_timestamp(), "VOITURE", action, etat_feu, scenario,
             id_voiture, direction, position_x, position_y, vitesse)
        )
        return cursor.lastrowid
    
    def get_recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Récupère les événements véhicules récents.
        
        Args:
            limit: Nombre maximum d'événements
            
        Returns:
            Liste des événements
        """
        query = "SELECT * FROM evenements_vehicules ORDER BY id DESC LIMIT ?"
        rows = self.db.fetch_all(query, (limit,))
        return [dict(row) for row in rows]
    
    def get_by_vehicle(self, id_voiture: int) -> List[Dict[str, Any]]:
        """
        Récupère tous les événements d'un véhicule spécifique.
        
        Args:
            id_voiture: Identifiant de la voiture
            
        Returns:
            Liste des événements du véhicule
        """
        query = "SELECT * FROM evenements_vehicules WHERE id_voiture = ? ORDER BY id"
        rows = self.db.fetch_all(query, (id_voiture,))
        return [dict(row) for row in rows]


class SessionDAO:
    """
    Data Access Object pour les sessions de simulation.
    Gère les opérations CRUD sur la table 'sessions'.
    """
    
    def __init__(self, db: DatabaseManager):
        """
        Initialise le DAO.
        
        Args:
            db: Instance du gestionnaire de base de données
        """
        self.db = db
    
    @staticmethod
    def _get_timestamp() -> str:
        """Retourne le timestamp actuel formaté"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def start_session(self, scenario: str) -> int:
        """
        Démarre une nouvelle session.
        
        Args:
            scenario: Scénario initial
            
        Returns:
            ID de la session créée
        """
        query = "INSERT INTO sessions (debut, scenario_initial) VALUES (?, ?)"
        cursor = self.db.execute(query, (self._get_timestamp(), scenario))
        return cursor.lastrowid
    
    def end_session(self, session_id: int, duree: float, nb_voitures: int = 0) -> None:
        """
        Termine une session.
        
        Args:
            session_id: ID de la session
            duree: Durée en secondes
            nb_voitures: Nombre total de voitures générées
        """
        query = '''
            UPDATE sessions 
            SET fin = ?, duree_secondes = ?, nb_voitures_total = ?
            WHERE id = ?
        '''
        self.db.execute(
            query,
            (self._get_timestamp(), duree, nb_voitures, session_id)
        )
    
    def get_all(self) -> List[Dict[str, Any]]:
        """
        Récupère toutes les sessions.
        
        Returns:
            Liste des sessions
        """
        query = "SELECT * FROM sessions ORDER BY id DESC"
        rows = self.db.fetch_all(query)
        return [dict(row) for row in rows]
    
    def get_last(self) -> Optional[Dict[str, Any]]:
        """
        Récupère la dernière session.
        
        Returns:
            Dernière session ou None
        """
        query = "SELECT * FROM sessions ORDER BY id DESC LIMIT 1"
        row = self.db.fetch_one(query)
        return dict(row) if row else None


# ============================================================================
# TEST DU MODULE
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE database.py")
    print("=" * 60)
    
    # Test de connexion
    db = DatabaseManager("test_traffic.db")
    
    # Test des DAOs
    evt_dao = EvenementDAO(db)
    veh_dao = VehiculeEventDAO(db)
    session_dao = SessionDAO(db)
    
    # Test insertion événement
    evt_id = evt_dao.insert(
        type_action="TEST",
        action="Test de fonctionnement",
        scenario="Normal",
        details="Ceci est un test"
    )
    print(f"[TEST] Événement créé avec ID: {evt_id}")
    
    # Test insertion véhicule
    veh_id = veh_dao.insert(
        action="Apparition",
        id_voiture=1,
        direction="NORD",
        position_x=-30.0,
        position_y=-400.0,
        vitesse=0.0,
        etat_feu="VERT",
        scenario="Normal"
    )
    print(f"[TEST] Événement véhicule créé avec ID: {veh_id}")
    
    # Test session
    session_id = session_dao.start_session("Normal")
    print(f"[TEST] Session démarrée avec ID: {session_id}")
    session_dao.end_session(session_id, 120.5, 15)
    print("[TEST] Session terminée")
    
    # Afficher les statistiques
    stats = db.get_statistics()
    print(f"[TEST] Statistiques: {stats}")
    
    # Nettoyage
    db.clear_all()
    db.close()
    
    # Supprimer le fichier de test
    import os
    if os.path.exists("test_traffic.db"):
        os.remove("test_traffic.db")
    
    print("[TEST] Tests terminés avec succès ✅")