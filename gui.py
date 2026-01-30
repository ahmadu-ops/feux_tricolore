"""
gui.py - Interface graphique moderne
Projet Feu Tricolore - Ville de Thiès
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Dict
from scenarios import Scenario, EtatFeu, COULEURS


class PanneauControle(tk.Frame):
    """Panneau de contrôle"""
    
    def __init__(self, parent: tk.Widget, callbacks: Dict[str, Callable]):
        super().__init__(parent, bg=COULEURS.bg_panel)
        
        self.callbacks = callbacks
        self.scenario_var = tk.StringVar(value=Scenario.NORMAL.value)
        
        self._creer_widgets()
    
    def _creer_widgets(self) -> None:
        """Crée tous les widgets"""
        self._creer_header()
        self._creer_section_simulation()
        self._creer_separateur()
        self._creer_section_scenarios()
        self._creer_separateur()
        self._creer_section_feux()
        self._creer_separateur()
        self._creer_section_stats()
        self._creer_separateur()
        self._creer_section_manuel()
    
    def _creer_header(self) -> None:
        """En-tête"""
        header = tk.Frame(self, bg='#0A1628')
        header.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            header, text="🚦", font=('Segoe UI Emoji', 28),
            bg='#0A1628', fg=COULEURS.accent
        ).pack(pady=(15, 5))
        
        tk.Label(
            header, text="THIÈS TRAFFIC", font=('Segoe UI', 12, 'bold'),
            bg='#0A1628', fg='white'
        ).pack()
        
        tk.Label(
            header, text="Système de contrôle", font=('Segoe UI', 8),
            bg='#0A1628', fg=COULEURS.text_secondary
        ).pack(pady=(0, 15))
    
    def _creer_section_simulation(self) -> None:
        """Boutons de simulation"""
        section = tk.Frame(self, bg=COULEURS.bg_panel)
        section.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(
            section, text="🎮  SIMULATION", font=('Segoe UI', 10, 'bold'),
            bg=COULEURS.bg_panel, fg=COULEURS.accent
        ).pack(anchor='w', pady=(0, 8))
        
        # Grille de boutons
        grid = tk.Frame(section, bg=COULEURS.bg_panel)
        grid.pack(fill=tk.X)
        
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)
        
        # Play
        self.btn_play = tk.Button(
            grid, text="▶  PLAY", font=('Segoe UI', 10, 'bold'),
            bg=COULEURS.success, fg='white', activebackground='#1FAA59',
            relief=tk.FLAT, cursor='hand2', height=2,
            command=self._on_play
        )
        self.btn_play.grid(row=0, column=0, padx=3, pady=3, sticky='ew')
        
        # Pause
        self.btn_pause = tk.Button(
            grid, text="⏸  PAUSE", font=('Segoe UI', 10, 'bold'),
            bg=COULEURS.warning, fg='white', activebackground='#E0A800',
            relief=tk.FLAT, cursor='hand2', height=2, state=tk.DISABLED,
            command=self._on_pause
        )
        self.btn_pause.grid(row=0, column=1, padx=3, pady=3, sticky='ew')
        
        # Stop
        self.btn_stop = tk.Button(
            grid, text="⏹  STOP", font=('Segoe UI', 10, 'bold'),
            bg=COULEURS.danger, fg='white', activebackground='#C0392B',
            relief=tk.FLAT, cursor='hand2', height=2, state=tk.DISABLED,
            command=self._on_stop
        )
        self.btn_stop.grid(row=1, column=0, padx=3, pady=3, sticky='ew')
        
        # Reset
        self.btn_reset = tk.Button(
            grid, text="🔄  RESET", font=('Segoe UI', 10, 'bold'),
            bg=COULEURS.accent, fg='white', activebackground='#0099CC',
            relief=tk.FLAT, cursor='hand2', height=2,
            command=self._on_reset
        )
        self.btn_reset.grid(row=1, column=1, padx=3, pady=3, sticky='ew')
    
    def _creer_section_scenarios(self) -> None:
        """Sélection de scénario"""
        section = tk.Frame(self, bg=COULEURS.bg_panel)
        section.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(
            section, text="📋  SCÉNARIO", font=('Segoe UI', 10, 'bold'),
            bg=COULEURS.bg_panel, fg=COULEURS.accent
        ).pack(anchor='w', pady=(0, 8))
        
        scenarios = [
            (Scenario.NORMAL, "🚗  Circulation normale"),
            (Scenario.HEURE_POINTE, "🚦  Heure de pointe"),
            (Scenario.NUIT, "🌙  Mode nuit"),
            (Scenario.MANUEL, "🎮  Mode manuel"),
        ]
        
        for scenario, texte in scenarios:
            rb = tk.Radiobutton(
                section, text=texte, variable=self.scenario_var,
                value=scenario.value, command=self._on_scenario_change,
                bg=COULEURS.bg_panel, fg=COULEURS.text_primary,
                selectcolor=COULEURS.bg_card, activebackground=COULEURS.bg_panel,
                activeforeground=COULEURS.accent, font=('Segoe UI', 10),
                anchor='w', cursor='hand2'
            )
            rb.pack(fill=tk.X, pady=2)
    
    def _creer_section_feux(self) -> None:
        """État des feux"""
        section = tk.Frame(self, bg=COULEURS.bg_panel)
        section.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(
            section, text="💡  ÉTAT DES FEUX", font=('Segoe UI', 10, 'bold'),
            bg=COULEURS.bg_panel, fg=COULEURS.accent
        ).pack(anchor='w', pady=(0, 8))
        
        # Card pour les feux
        card = tk.Frame(section, bg=COULEURS.bg_card, padx=15, pady=12)
        card.pack(fill=tk.X)
        
        # Voie 1
        tk.Label(
            card, text="Voie Nord ↔ Sud", font=('Segoe UI', 9),
            bg=COULEURS.bg_card, fg=COULEURS.text_secondary
        ).pack(anchor='w')
        
        self.label_feu_v1 = tk.Label(
            card, text="🟢  VERT", font=('Segoe UI', 14, 'bold'),
            bg=COULEURS.bg_card, fg=COULEURS.success
        )
        self.label_feu_v1.pack(anchor='w', pady=(2, 10))
        
        # Séparateur
        tk.Frame(card, bg='#555555', height=1).pack(fill=tk.X, pady=5)
        
        # Voie 2
        tk.Label(
            card, text="Voie Est ↔ Ouest", font=('Segoe UI', 9),
            bg=COULEURS.bg_card, fg=COULEURS.text_secondary
        ).pack(anchor='w', pady=(5, 0))
        
        self.label_feu_v2 = tk.Label(
            card, text="🔴  ROUGE", font=('Segoe UI', 14, 'bold'),
            bg=COULEURS.bg_card, fg=COULEURS.danger
        )
        self.label_feu_v2.pack(anchor='w', pady=(2, 10))
        
        # Séparateur
        tk.Frame(card, bg='#555555', height=1).pack(fill=tk.X, pady=5)
        
        # Status
        self.label_status = tk.Label(
            card, text="⏹  ARRÊTÉ", font=('Segoe UI', 12, 'bold'),
            bg=COULEURS.bg_card, fg=COULEURS.danger
        )
        self.label_status.pack(pady=(5, 0))
    
    def _creer_section_stats(self) -> None:
        """Statistiques"""
        section = tk.Frame(self, bg=COULEURS.bg_panel)
        section.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(
            section, text="📊  STATISTIQUES", font=('Segoe UI', 10, 'bold'),
            bg=COULEURS.bg_panel, fg=COULEURS.accent
        ).pack(anchor='w', pady=(0, 8))
        
        stats = tk.Frame(section, bg=COULEURS.bg_card, padx=15, pady=10)
        stats.pack(fill=tk.X)
        
        # Véhicules
        v_row = tk.Frame(stats, bg=COULEURS.bg_card)
        v_row.pack(fill=tk.X, pady=3)
        
        tk.Label(
            v_row, text="🚗", font=('Segoe UI Emoji', 14),
            bg=COULEURS.bg_card
        ).pack(side=tk.LEFT)
        
        self.label_voitures = tk.Label(
            v_row, text="0 véhicules", font=('Segoe UI', 11),
            bg=COULEURS.bg_card, fg='white'
        )
        self.label_voitures.pack(side=tk.LEFT, padx=(10, 0))
        
        # Temps
        t_row = tk.Frame(stats, bg=COULEURS.bg_card)
        t_row.pack(fill=tk.X, pady=3)
        
        tk.Label(
            t_row, text="⏱️", font=('Segoe UI Emoji', 14),
            bg=COULEURS.bg_card
        ).pack(side=tk.LEFT)
        
        self.label_temps = tk.Label(
            t_row, text="00:00", font=('Segoe UI', 11),
            bg=COULEURS.bg_card, fg='white'
        )
        self.label_temps.pack(side=tk.LEFT, padx=(10, 0))
    
    def _creer_section_manuel(self) -> None:
        """Contrôle manuel"""
        section = tk.Frame(self, bg=COULEURS.bg_panel)
        section.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(
            section, text="🎛️  CONTRÔLE MANUEL", font=('Segoe UI', 10, 'bold'),
            bg=COULEURS.bg_panel, fg=COULEURS.accent
        ).pack(anchor='w', pady=(0, 8))
        
        self.label_manuel = tk.Label(
            section, text="⚠️  Activez le mode manuel",
            font=('Segoe UI', 9), bg=COULEURS.bg_panel, fg=COULEURS.warning
        )
        self.label_manuel.pack(anchor='w', pady=(0, 8))
        
        # Voie 1
        v1 = tk.Frame(section, bg=COULEURS.bg_panel)
        v1.pack(fill=tk.X, pady=3)
        
        tk.Label(
            v1, text="Voie N↔S :", font=('Segoe UI', 9),
            bg=COULEURS.bg_panel, fg=COULEURS.text_secondary
        ).pack(side=tk.LEFT)
        
        for color, etat in [('#2ECC71', EtatFeu.VERT), ('#F39C12', EtatFeu.ORANGE), ('#E74C3C', EtatFeu.ROUGE)]:
            btn = tk.Button(
                v1, text="●", font=('Segoe UI', 16), fg=color,
                bg=COULEURS.bg_card, activebackground=color,
                relief=tk.FLAT, width=2, cursor='hand2',
                command=lambda v=1, e=etat: self._on_feu_manuel(v, e)
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # Voie 2
        v2 = tk.Frame(section, bg=COULEURS.bg_panel)
        v2.pack(fill=tk.X, pady=3)
        
        tk.Label(
            v2, text="Voie E↔O :", font=('Segoe UI', 9),
            bg=COULEURS.bg_panel, fg=COULEURS.text_secondary
        ).pack(side=tk.LEFT)
        
        for color, etat in [('#2ECC71', EtatFeu.VERT), ('#F39C12', EtatFeu.ORANGE), ('#E74C3C', EtatFeu.ROUGE)]:
            btn = tk.Button(
                v2, text="●", font=('Segoe UI', 16), fg=color,
                bg=COULEURS.bg_card, activebackground=color,
                relief=tk.FLAT, width=2, cursor='hand2',
                command=lambda v=2, e=etat: self._on_feu_manuel(v, e)
            )
            btn.pack(side=tk.LEFT, padx=2)
    
    def _creer_separateur(self) -> None:
        """Ligne de séparation"""
        tk.Frame(self, bg='#404040', height=1).pack(fill=tk.X, padx=20, pady=8)
    
    # === CALLBACKS ===
    
    def _on_play(self) -> None:
        if 'play' in self.callbacks:
            self.callbacks['play']()
    
    def _on_pause(self) -> None:
        if 'pause' in self.callbacks:
            self.callbacks['pause']()
    
    def _on_stop(self) -> None:
        if 'stop' in self.callbacks:
            self.callbacks['stop']()
    
    def _on_reset(self) -> None:
        if 'reset' in self.callbacks:
            self.callbacks['reset']()
    
    def _on_scenario_change(self) -> None:
        if 'scenario_change' in self.callbacks:
            self.callbacks['scenario_change'](self.scenario_var.get())
        
        is_manuel = self.scenario_var.get() == Scenario.MANUEL.value
        if is_manuel:
            self.label_manuel.config(text="✅  Mode manuel actif", fg=COULEURS.success)
        else:
            self.label_manuel.config(text="⚠️  Activez le mode manuel", fg=COULEURS.warning)
    
    def _on_feu_manuel(self, voie: int, etat: EtatFeu) -> None:
        if self.scenario_var.get() != Scenario.MANUEL.value:
            messagebox.showinfo("Mode manuel", "Activez d'abord le mode manuel.")
            return
        if 'feu_manuel' in self.callbacks:
            self.callbacks['feu_manuel'](voie, etat)
    
    # === MISES À JOUR ===
    
    def update_etat_feux(self, etat_v1: EtatFeu, etat_v2: EtatFeu) -> None:
        """Met à jour l'affichage des feux"""
        mapping = {
            EtatFeu.VERT: ('🟢  VERT', COULEURS.success),
            EtatFeu.ORANGE: ('🟡  ORANGE', COULEURS.warning),
            EtatFeu.ROUGE: ('🔴  ROUGE', COULEURS.danger),
            EtatFeu.ORANGE_CLIGNOTANT: ('🟡  CLIGNOTANT', COULEURS.warning),
            EtatFeu.ETEINT: ('⚫  ÉTEINT', COULEURS.text_secondary)
        }
        
        txt1, col1 = mapping.get(etat_v1, ('?', COULEURS.text_secondary))
        txt2, col2 = mapping.get(etat_v2, ('?', COULEURS.text_secondary))
        
        self.label_feu_v1.config(text=txt1, fg=col1)
        self.label_feu_v2.config(text=txt2, fg=col2)
    
    def update_status(self, en_cours: bool, en_pause: bool) -> None:
        """Met à jour le status de simulation"""
        if en_cours and not en_pause:
            self.label_status.config(text="▶  EN COURS", fg=COULEURS.success)
            self.btn_play.config(state=tk.DISABLED)
            self.btn_pause.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.NORMAL)
        elif en_cours and en_pause:
            self.label_status.config(text="⏸  EN PAUSE", fg=COULEURS.warning)
            self.btn_play.config(state=tk.NORMAL)
            self.btn_pause.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
        else:
            self.label_status.config(text="⏹  ARRÊTÉ", fg=COULEURS.danger)
            self.btn_play.config(state=tk.NORMAL)
            self.btn_pause.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.DISABLED)
    
    def update_stats(self, nb_voitures: int, temps_sec: int) -> None:
        """Met à jour les statistiques"""
        self.label_voitures.config(text=f"{nb_voitures} véhicule{'s' if nb_voitures != 1 else ''}")
        m, s = divmod(temps_sec, 60)
        self.label_temps.config(text=f"{m:02d}:{s:02d}")


class InterfaceGraphique:
    """Interface principale"""
    
    PANEL_WIDTH = 300
    
    def __init__(self, titre: str = "Simulateur de Carrefour - Thiès"):
        self.canvas_size = 700
        self.panneau = None
        self.is_fullscreen = False
        
        self.root = tk.Tk()
        self.root.title(f"🚦 {titre}")
        self.root.configure(bg=COULEURS.bg_dark)
        
        # Taille fenêtre
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        
        w, h = int(sw * 0.9), int(sh * 0.85)
        x, y = (sw - w) // 2, (sh - h) // 2 - 20
        
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.minsize(1000, 700)
        
        # Raccourcis
        self.root.bind('<F11>', lambda e: self._toggle_fullscreen())
        self.root.bind('<Escape>', lambda e: self._exit_fullscreen())
        
        self._creer_layout()
    
    def _toggle_fullscreen(self) -> None:
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
    
    def _exit_fullscreen(self) -> None:
        self.is_fullscreen = False
        self.root.attributes('-fullscreen', False)
    
    def _creer_layout(self) -> None:
        """Crée la disposition"""
        self.main = tk.Frame(self.root, bg=COULEURS.bg_dark)
        self.main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Gauche : Canvas
        self.left = tk.Frame(self.main, bg=COULEURS.bg_dark)
        self.left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas_frame = tk.Frame(self.left, bg=COULEURS.bg_dark)
        self.canvas_frame.pack(expand=True)
        
        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=self.canvas_size,
            height=self.canvas_size,
            bg='#1A5A1A',
            highlightthickness=3,
            highlightbackground=COULEURS.accent
        )
        self.canvas.pack()
        
        # Droite : Panneau
        self.right = tk.Frame(self.main, bg=COULEURS.bg_panel, width=self.PANEL_WIDTH)
        self.right.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        self.right.pack_propagate(False)
        
        # Resize
        self.root.bind('<Configure>', self._on_resize)
    
    def _on_resize(self, event=None) -> None:
        if event and event.widget == self.root:
            self.root.after(100, self._update_canvas)
    
    def _update_canvas(self) -> None:
        try:
            w = self.root.winfo_width() - self.PANEL_WIDTH - 50
            h = self.root.winfo_height() - 40
            size = min(w, h, 800)
            size = max(500, size)
            
            if abs(size - self.canvas_size) > 20:
                self.canvas_size = size
                self.canvas.config(width=size, height=size)
        except:
            pass
    
    def initialiser_panneau(self, callbacks: Dict[str, Callable]) -> PanneauControle:
        """Initialise le panneau de contrôle"""
        self.panneau = PanneauControle(self.right, callbacks)
        self.panneau.pack(fill=tk.BOTH, expand=True)
        return self.panneau
    
    def get_canvas(self) -> tk.Canvas:
        return self.canvas
    
    def get_canvas_size(self) -> int:
        return self.canvas_size
    
    def set_on_close(self, callback: Callable) -> None:
        self.root.protocol("WM_DELETE_WINDOW", callback)
    
    def after(self, ms: int, callback: Callable) -> str:
        return self.root.after(ms, callback)
    
    def after_cancel(self, id: str) -> None:
        self.root.after_cancel(id)
    
    def run(self) -> None:
        self.root.mainloop()
    
    def destroy(self) -> None:
        self.root.destroy()


if __name__ == "__main__":
    def dummy(*args):
        print(f"Callback: {args}")
    
    gui = InterfaceGraphique()
    panneau = gui.initialiser_panneau({
        'play': dummy, 'pause': dummy, 'stop': dummy,
        'reset': dummy, 'scenario_change': dummy, 'feu_manuel': dummy
    })
    
    # Test affichage
    panneau.update_etat_feux(EtatFeu.VERT, EtatFeu.ROUGE)
    panneau.update_status(False, False)
    panneau.update_stats(5, 125)
    
    gui.run()