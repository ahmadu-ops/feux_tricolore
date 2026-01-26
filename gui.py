"""
gui.py - Interface graphique Tkinter
Projet Feu Tricolore - Ville de Thiès
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, Dict
from scenarios import Scenario, EtatFeu, COULEURS


class BoutonStyle:
    """Styles prédéfinis pour les boutons"""
    
    PLAY = {
        'bg': '#27AE60',
        'fg': 'white',
        'activebackground': '#2ECC71',
        'activeforeground': 'white'
    }
    
    PAUSE = {
        'bg': '#F39C12',
        'fg': 'white',
        'activebackground': '#F1C40F',
        'activeforeground': 'white'
    }
    
    STOP = {
        'bg': '#E74C3C',
        'fg': 'white',
        'activebackground': '#C0392B',
        'activeforeground': 'white'
    }
    
    RESET = {
        'bg': '#9B59B6',
        'fg': 'white',
        'activebackground': '#8E44AD',
        'activeforeground': 'white'
    }
    
    FEU = {
        'bg': '#2C3E50',
        'fg': 'white',
        'activebackground': '#34495E',
        'activeforeground': 'white'
    }


class PanneauControle(tk.Frame):
    """
    Panneau de contrôle principal de l'interface.
    Contient tous les boutons et contrôles de la simulation.
    """
    
    def __init__(self, parent: tk.Widget, callbacks: Dict[str, Callable]):
        """
        Initialise le panneau de contrôle.
        
        Args:
            parent: Widget parent
            callbacks: Dictionnaire des fonctions de callback
                - 'play': Fonction pour démarrer
                - 'pause': Fonction pour pause
                - 'stop': Fonction pour arrêter
                - 'reset': Fonction pour réinitialiser
                - 'scenario_change': Fonction pour changement de scénario
                - 'feu_manuel': Fonction pour contrôle manuel des feux
        """
        super().__init__(parent, bg=COULEURS.bg_panel, width=280)
        self.pack_propagate(False)
        
        self.callbacks = callbacks
        
        # Variables
        self.scenario_var = tk.StringVar(value=Scenario.NORMAL.value)
        
        # Créer les sections
        self._creer_titre()
        self._creer_section_simulation()
        self._creer_separateur()
        self._creer_section_scenarios()
        self._creer_separateur()
        self._creer_section_manuel()
        self._creer_separateur()
        self._creer_section_etat()
        self._creer_section_stats()
    
    def _creer_titre(self) -> None:
        """Crée le titre du panneau"""
        titre_frame = tk.Frame(self, bg=COULEURS.bg_panel)
        titre_frame.pack(fill=tk.X, pady=(15, 20))
        
        # Icône et titre
        titre = tk.Label(
            titre_frame,
            text="🚦 PANNEAU DE CONTRÔLE",
            font=('Helvetica', 13, 'bold'),
            bg=COULEURS.bg_panel,
            fg=COULEURS.accent
        )
        titre.pack()
        
        # Sous-titre
        sous_titre = tk.Label(
            titre_frame,
            text="Ville de Thiès",
            font=('Helvetica', 9, 'italic'),
            bg=COULEURS.bg_panel,
            fg=COULEURS.text_secondary
        )
        sous_titre.pack()
    
    def _creer_section_simulation(self) -> None:
        """Crée la section des boutons de simulation"""
        frame = tk.Frame(self, bg=COULEURS.bg_panel)
        frame.pack(fill=tk.X, padx=15, pady=5)
        
        # Titre de section
        tk.Label(
            frame,
            text="SIMULATION",
            font=('Helvetica', 10, 'bold'),
            bg=COULEURS.bg_panel,
            fg=COULEURS.text_primary
        ).pack(anchor='w', pady=(0, 8))
        
        # Ligne 1: Play et Pause
        btn_frame1 = tk.Frame(frame, bg=COULEURS.bg_panel)
        btn_frame1.pack(fill=tk.X, pady=2)
        
        self.btn_play = tk.Button(
            btn_frame1,
            text="▶ PLAY",
            command=self._on_play,
            font=('Helvetica', 10, 'bold'),
            width=11,
            height=2,
            relief=tk.FLAT,
            cursor='hand2',
            **BoutonStyle.PLAY
        )
        self.btn_play.pack(side=tk.LEFT, padx=(0, 5))
        
        self.btn_pause = tk.Button(
            btn_frame1,
            text="⏸ PAUSE",
            command=self._on_pause,
            font=('Helvetica', 10, 'bold'),
            width=11,
            height=2,
            relief=tk.FLAT,
            cursor='hand2',
            state=tk.DISABLED,
            **BoutonStyle.PAUSE
        )
        self.btn_pause.pack(side=tk.LEFT)
        
        # Ligne 2: Stop et Reset
        btn_frame2 = tk.Frame(frame, bg=COULEURS.bg_panel)
        btn_frame2.pack(fill=tk.X, pady=2)
        
        self.btn_stop = tk.Button(
            btn_frame2,
            text="⏹ STOP",
            command=self._on_stop,
            font=('Helvetica', 10, 'bold'),
            width=11,
            height=2,
            relief=tk.FLAT,
            cursor='hand2',
            state=tk.DISABLED,
            **BoutonStyle.STOP
        )
        self.btn_stop.pack(side=tk.LEFT, padx=(0, 5))
        
        self.btn_reset = tk.Button(
            btn_frame2,
            text="🔄 RESET",
            command=self._on_reset,
            font=('Helvetica', 10, 'bold'),
            width=11,
            height=2,
            relief=tk.FLAT,
            cursor='hand2',
            **BoutonStyle.RESET
        )
        self.btn_reset.pack(side=tk.LEFT)
    
    def _creer_section_scenarios(self) -> None:
        """Crée la section de sélection des scénarios"""
        frame = tk.Frame(self, bg=COULEURS.bg_panel)
        frame.pack(fill=tk.X, padx=15, pady=5)
        
        # Titre de section
        tk.Label(
            frame,
            text="SCÉNARIOS",
            font=('Helvetica', 10, 'bold'),
            bg=COULEURS.bg_panel,
            fg=COULEURS.text_primary
        ).pack(anchor='w', pady=(0, 8))
        
        # Boutons radio pour chaque scénario
        scenarios_info = [
            (Scenario.NORMAL, "🚗", "Flux régulier"),
            (Scenario.HEURE_POINTE, "🚦", "Trafic dense"),
            (Scenario.NUIT, "🌙", "Clignotant"),
            (Scenario.MANUEL, "🎮", "Contrôle total")
        ]
        
        for scenario, emoji, desc in scenarios_info:
            rb_frame = tk.Frame(frame, bg=COULEURS.bg_panel)
            rb_frame.pack(fill=tk.X, pady=1)
            
            rb = tk.Radiobutton(
                rb_frame,
                text=f"{emoji} {scenario.value}",
                variable=self.scenario_var,
                value=scenario.value,
                command=self._on_scenario_change,
                bg=COULEURS.bg_panel,
                fg=COULEURS.text_secondary,
                selectcolor=COULEURS.bg_card,
                activebackground=COULEURS.bg_panel,
                activeforeground=COULEURS.text_primary,
                font=('Helvetica', 9),
                cursor='hand2',
                anchor='w'
            )
            rb.pack(side=tk.LEFT)
            
            # Description
            tk.Label(
                rb_frame,
                text=f"({desc})",
                font=('Helvetica', 8),
                bg=COULEURS.bg_panel,
                fg='#7F8C8D'
            ).pack(side=tk.LEFT, padx=(5, 0))
    
    def _creer_section_manuel(self) -> None:
        """Crée la section de contrôle manuel des feux"""
        frame = tk.Frame(self, bg=COULEURS.bg_panel)
        frame.pack(fill=tk.X, padx=15, pady=5)
        
        # Titre de section
        tk.Label(
            frame,
            text="CONTRÔLE MANUEL DES FEUX",
            font=('Helvetica', 10, 'bold'),
            bg=COULEURS.bg_panel,
            fg=COULEURS.text_primary
        ).pack(anchor='w', pady=(0, 8))
        
        # Info
        self.label_manuel_info = tk.Label(
            frame,
            text="⚠️ Activez le mode manuel",
            font=('Helvetica', 8, 'italic'),
            bg=COULEURS.bg_panel,
            fg='#F39C12'
        )
        self.label_manuel_info.pack(anchor='w', pady=(0, 5))
        
        # Voie 1 (Nord-Sud)
        v1_frame = tk.Frame(frame, bg=COULEURS.bg_panel)
        v1_frame.pack(fill=tk.X, pady=3)
        
        tk.Label(
            v1_frame,
            text="Voie 1 (N↔S):",
            font=('Helvetica', 9),
            bg=COULEURS.bg_panel,
            fg=COULEURS.text_secondary,
            width=12,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.btns_v1 = self._creer_boutons_feu(v1_frame, 1)
        
        # Voie 2 (Est-Ouest)
        v2_frame = tk.Frame(frame, bg=COULEURS.bg_panel)
        v2_frame.pack(fill=tk.X, pady=3)
        
        tk.Label(
            v2_frame,
            text="Voie 2 (E↔O):",
            font=('Helvetica', 9),
            bg=COULEURS.bg_panel,
            fg=COULEURS.text_secondary,
            width=12,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.btns_v2 = self._creer_boutons_feu(v2_frame, 2)
    
    def _creer_boutons_feu(self, parent: tk.Widget, voie: int) -> Dict[str, tk.Button]:
        """
        Crée les boutons de contrôle de feu pour une voie.
        
        Args:
            parent: Widget parent
            voie: Numéro de la voie
            
        Returns:
            Dictionnaire des boutons créés
        """
        btns = {}
        
        couleurs_feu = [
            ('vert', '🟢', EtatFeu.VERT),
            ('orange', '🟡', EtatFeu.ORANGE),
            ('rouge', '🔴', EtatFeu.ROUGE)
        ]
        
        for nom, emoji, etat in couleurs_feu:
            btn = tk.Button(
                parent,
                text=emoji,
                command=lambda v=voie, e=etat: self._on_feu_manuel(v, e),
                font=('Helvetica', 14),
                width=2,
                height=1,
                relief=tk.FLAT,
                cursor='hand2',
                bg=COULEURS.bg_card,
                activebackground=COULEURS.bg_dark
            )
            btn.pack(side=tk.LEFT, padx=2)
            btns[nom] = btn
        
        return btns
    
    def _creer_section_etat(self) -> None:
        """Crée la section d'affichage de l'état actuel"""
        frame = tk.Frame(self, bg=COULEURS.bg_card, relief=tk.RIDGE, bd=1)
        frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Titre
        tk.Label(
            frame,
            text="ÉTAT ACTUEL",
            font=('Helvetica', 10, 'bold'),
            bg=COULEURS.bg_card,
            fg=COULEURS.text_primary
        ).pack(anchor='w', padx=10, pady=(8, 5))
        
        # État des feux
        feux_frame = tk.Frame(frame, bg=COULEURS.bg_card)
        feux_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.label_feu_v1 = tk.Label(
            feux_frame,
            text="Voie 1: 🟢 VERT",
            font=('Helvetica', 10),
            bg=COULEURS.bg_card,
            fg='#2ECC71'
        )
        self.label_feu_v1.pack(anchor='w')
        
        self.label_feu_v2 = tk.Label(
            feux_frame,
            text="Voie 2: 🔴 ROUGE",
            font=('Helvetica', 10),
            bg=COULEURS.bg_card,
            fg='#E74C3C'
        )
        self.label_feu_v2.pack(anchor='w')
        
        # Séparateur
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, padx=10, pady=5)
        
        # Status de la simulation
        self.label_status = tk.Label(
            frame,
            text="⏹ ARRÊTÉ",
            font=('Helvetica', 12, 'bold'),
            bg=COULEURS.bg_card,
            fg='#E74C3C'
        )
        self.label_status.pack(pady=(0, 8))
    
    def _creer_section_stats(self) -> None:
        """Crée la section des statistiques"""
        frame = tk.Frame(self, bg=COULEURS.bg_panel)
        frame.pack(fill=tk.X, padx=15, pady=5)
        
        # Compteur de voitures
        self.label_voitures = tk.Label(
            frame,
            text="🚗 Voitures: 0",
            font=('Helvetica', 10),
            bg=COULEURS.bg_panel,
            fg=COULEURS.text_secondary
        )
        self.label_voitures.pack(anchor='w', pady=2)
        
        # Temps écoulé
        self.label_temps = tk.Label(
            frame,
            text="⏱ Temps: 00:00",
            font=('Helvetica', 10),
            bg=COULEURS.bg_panel,
            fg=COULEURS.text_secondary
        )
        self.label_temps.pack(anchor='w', pady=2)
        
        # Scénario actif
        self.label_scenario = tk.Label(
            frame,
            text="📋 Scénario: Normal",
            font=('Helvetica', 10),
            bg=COULEURS.bg_panel,
            fg=COULEURS.text_secondary
        )
        self.label_scenario.pack(anchor='w', pady=2)
    
    def _creer_separateur(self) -> None:
        """Crée un séparateur horizontal"""
        sep = ttk.Separator(self, orient='horizontal')
        sep.pack(fill=tk.X, padx=20, pady=10)
    
    # ========================================================================
    # CALLBACKS DES BOUTONS
    # ========================================================================
    
    def _on_play(self) -> None:
        """Callback du bouton Play"""
        if 'play' in self.callbacks:
            self.callbacks['play']()
    
    def _on_pause(self) -> None:
        """Callback du bouton Pause"""
        if 'pause' in self.callbacks:
            self.callbacks['pause']()
    
    def _on_stop(self) -> None:
        """Callback du bouton Stop"""
        if 'stop' in self.callbacks:
            self.callbacks['stop']()
    
    def _on_reset(self) -> None:
        """Callback du bouton Reset"""
        if 'reset' in self.callbacks:
            self.callbacks['reset']()
    
    def _on_scenario_change(self) -> None:
        """Callback du changement de scénario"""
        if 'scenario_change' in self.callbacks:
            self.callbacks['scenario_change'](self.scenario_var.get())
        
        # Mettre à jour l'affichage du mode manuel
        is_manuel = self.scenario_var.get() == Scenario.MANUEL.value
        if is_manuel:
            self.label_manuel_info.config(
                text="✅ Mode manuel actif",
                fg='#2ECC71'
            )
        else:
            self.label_manuel_info.config(
                text="⚠️ Activez le mode manuel",
                fg='#F39C12'
            )
    
    def _on_feu_manuel(self, voie: int, etat: EtatFeu) -> None:
        """
        Callback du contrôle manuel des feux.
        
        Args:
            voie: Numéro de la voie
            etat: État à forcer
        """
        # Vérifier si en mode manuel
        if self.scenario_var.get() != Scenario.MANUEL.value:
            messagebox.showwarning(
                "Mode manuel requis",
                "Veuillez d'abord sélectionner le mode manuel\n"
                "pour contrôler les feux manuellement."
            )
            return
        
        if 'feu_manuel' in self.callbacks:
            self.callbacks['feu_manuel'](voie, etat)
    
    # ========================================================================
    # MÉTHODES DE MISE À JOUR
    # ========================================================================
    
    def update_etat_feux(self, etat_v1: EtatFeu, etat_v2: EtatFeu) -> None:
        """
        Met à jour l'affichage des états des feux.
        
        Args:
            etat_v1: État du feu voie 1
            etat_v2: État du feu voie 2
        """
        # Mapping état -> (texte, couleur)
        etats_affichage = {
            EtatFeu.VERT: ('🟢 VERT', '#2ECC71'),
            EtatFeu.ORANGE: ('🟡 ORANGE', '#F39C12'),
            EtatFeu.ROUGE: ('🔴 ROUGE', '#E74C3C'),
            EtatFeu.ORANGE_CLIGNOTANT: ('🟡 CLIGNOTANT', '#F39C12'),
            EtatFeu.ETEINT: ('⚫ ÉTEINT', '#7F8C8D')
        }
        
        texte_v1, couleur_v1 = etats_affichage.get(
            etat_v1, ('❓ INCONNU', '#BDC3C7')
        )
        texte_v2, couleur_v2 = etats_affichage.get(
            etat_v2, ('❓ INCONNU', '#BDC3C7')
        )
        
        self.label_feu_v1.config(text=f"Voie 1: {texte_v1}", fg=couleur_v1)
        self.label_feu_v2.config(text=f"Voie 2: {texte_v2}", fg=couleur_v2)
    
    def update_status(self, status: str, en_cours: bool, en_pause: bool) -> None:
        """
        Met à jour le status de la simulation.
        
        Args:
            status: Texte du status
            en_cours: True si simulation en cours
            en_pause: True si simulation en pause
        """
        if en_cours and not en_pause:
            self.label_status.config(text="▶ EN COURS", fg='#2ECC71')
            self.btn_play.config(state=tk.DISABLED)
            self.btn_pause.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.NORMAL)
        elif en_cours and en_pause:
            self.label_status.config(text="⏸ EN PAUSE", fg='#F39C12')
            self.btn_play.config(state=tk.NORMAL)
            self.btn_pause.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
        else:
            self.label_status.config(text="⏹ ARRÊTÉ", fg='#E74C3C')
            self.btn_play.config(state=tk.NORMAL)
            self.btn_pause.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.DISABLED)
    
    def update_stats(self, nb_voitures: int, temps_secondes: int,
                     scenario: str) -> None:
        """
        Met à jour les statistiques affichées.
        
        Args:
            nb_voitures: Nombre de voitures actuelles
            temps_secondes: Temps écoulé en secondes
            scenario: Nom du scénario actif
        """
        # Voitures
        self.label_voitures.config(text=f"🚗 Voitures: {nb_voitures}")
        
        # Temps formaté
        minutes = temps_secondes // 60
        secondes = temps_secondes % 60
        self.label_temps.config(text=f"⏱ Temps: {minutes:02d}:{secondes:02d}")
        
        # Scénario
        self.label_scenario.config(text=f"📋 Scénario: {scenario}")
    
    def get_scenario_selectionne(self) -> str:
        """Retourne le scénario actuellement sélectionné"""
        return self.scenario_var.get()


class InterfaceGraphique:
    """
    Interface graphique principale de l'application.
    Coordonne le canvas Turtle et le panneau de contrôle.
    """
    
    def __init__(self, titre: str = "Simulateur de Carrefour - Ville de Thiès"):
        """
        Initialise l'interface graphique.
        
        Args:
            titre: Titre de la fenêtre
        """
        # Fenêtre principale
        self.root = tk.Tk()
        self.root.title(f"🚦 {titre}")
        self.root.geometry("1050x800")
        self.root.resizable(False, False)
        self.root.configure(bg=COULEURS.bg_dark)
        
        # Callbacks (à définir par l'application principale)
        self.callbacks: Dict[str, Callable] = {}
        
        # Créer l'interface
        self._creer_interface()
        
        # Référence au screen Turtle (sera initialisé plus tard)
        self.turtle_screen = None
    
    def _creer_interface(self) -> None:
        """Crée la structure de l'interface"""
        # Frame principal
        self.main_frame = tk.Frame(self.root, bg=COULEURS.bg_dark)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame gauche pour le canvas Turtle
        self.left_frame = tk.Frame(self.main_frame, bg=COULEURS.bg_dark)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Canvas pour Turtle
        self.canvas = tk.Canvas(
            self.left_frame,
            width=730,
            height=730,
            bg='#27AE60',
            highlightthickness=3,
            highlightbackground=COULEURS.accent
        )
        self.canvas.pack(padx=5, pady=5)
        
        # Frame droite pour les contrôles (sera créé avec les callbacks)
        self.right_frame = tk.Frame(self.main_frame, bg=COULEURS.bg_dark)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
    
    def initialiser_panneau_controle(self, callbacks: Dict[str, Callable]) -> PanneauControle:
        """
        Initialise le panneau de contrôle avec les callbacks.
        
        Args:
            callbacks: Dictionnaire des fonctions de callback
            
        Returns:
            Instance du panneau de contrôle
        """
        self.callbacks = callbacks
        self.panneau = PanneauControle(self.right_frame, callbacks)
        self.panneau.pack(fill=tk.Y, expand=True)
        return self.panneau
    
    def get_canvas(self) -> tk.Canvas:
        """Retourne le canvas Tkinter pour Turtle"""
        return self.canvas
    
    def set_on_close(self, callback: Callable) -> None:
        """
        Définit le callback de fermeture de fenêtre.
        
        Args:
            callback: Fonction à appeler à la fermeture
        """
        self.root.protocol("WM_DELETE_WINDOW", callback)
    
    def run(self) -> None:
        """Lance la boucle principale Tkinter"""
        self.root.mainloop()
    
    def after(self, delay_ms: int, callback: Callable) -> str:
        """
        Planifie l'exécution d'une fonction.
        
        Args:
            delay_ms: Délai en millisecondes
            callback: Fonction à exécuter
            
        Returns:
            ID du timer
        """
        return self.root.after(delay_ms, callback)
    
    def after_cancel(self, timer_id: str) -> None:
        """
        Annule un timer planifié.
        
        Args:
            timer_id: ID du timer à annuler
        """
        self.root.after_cancel(timer_id)
    
    def destroy(self) -> None:
        """Détruit la fenêtre"""
        self.root.destroy()


# ============================================================================
# TEST DU MODULE
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE gui.py")
    print("=" * 60)
    
    # Callbacks de test
    def test_callback(name):
        def callback(*args):
            print(f"[TEST] Callback '{name}' appelé avec args: {args}")
        return callback
    
    callbacks = {
        'play': test_callback('play'),
        'pause': test_callback('pause'),
        'stop': test_callback('stop'),
        'reset': test_callback('reset'),
        'scenario_change': test_callback('scenario_change'),
        'feu_manuel': test_callback('feu_manuel')
    }
    
    # Créer l'interface
    gui = InterfaceGraphique("Test GUI")
    panneau = gui.initialiser_panneau_controle(callbacks)
    
    # Test des mises à jour
    def test_updates():
        panneau.update_etat_feux(EtatFeu.VERT, EtatFeu.ROUGE)
        panneau.update_stats(5, 125, "Circulation normale")
        panneau.update_status("En cours", True, False)
    
    gui.after(1000, test_updates)
    
    print("\n[TEST] Interface créée. Fermez la fenêtre pour terminer.")
    gui.run()
    
    print("\n[TEST] Tests terminés avec succès ✅")