"""
gui.py - Interface graphique moderne
Projet Feu Tricolore - Ville de Thiès
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict
from scenarios import Scenario, EtatFeu, COULEURS


class PanneauControle(tk.Frame):
    """Panneau de contrôle moderne"""
    
    def __init__(self, parent: tk.Widget, callbacks: Dict[str, Callable]):
        super().__init__(parent, bg=COULEURS.bg_panel)
        
        self.callbacks = callbacks
        self.scenario_var = tk.StringVar(value=Scenario.NORMAL.value)
        
        self._creer_widgets()
    
    def _creer_widgets(self) -> None:
        """Crée tous les widgets"""
        self._creer_header()
        self._creer_section_simulation()
        self._creer_section_scenarios()
        self._creer_section_feux_manuels()
        self._creer_section_status()
        self._creer_section_stats()
    
    def _creer_header(self) -> None:
        """En-tête du panneau"""
        header = tk.Frame(self, bg=COULEURS.bg_dark, height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg=COULEURS.bg_dark)
        title_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(
            title_frame,
            text="🚦",
            font=('Segoe UI Emoji', 24),
            bg=COULEURS.bg_dark,
            fg=COULEURS.accent
        ).pack()
        
        tk.Label(
            title_frame,
            text="CONTRÔLE",
            font=('Segoe UI', 11, 'bold'),
            bg=COULEURS.bg_dark,
            fg=COULEURS.text_primary
        ).pack()
    
    def _creer_section_simulation(self) -> None:
        """Section boutons de simulation"""
        section = self._creer_section("SIMULATION")
        
        btn_grid = tk.Frame(section, bg=COULEURS.bg_panel)
        btn_grid.pack(fill=tk.X, pady=5)
        
        btn_grid.columnconfigure(0, weight=1)
        btn_grid.columnconfigure(1, weight=1)
        
        self.btn_play = self._creer_bouton(
            btn_grid, "▶  PLAY", COULEURS.success, self._on_play
        )
        self.btn_play.grid(row=0, column=0, padx=3, pady=3, sticky='ew')
        
        self.btn_pause = self._creer_bouton(
            btn_grid, "⏸  PAUSE", COULEURS.warning, self._on_pause, state=tk.DISABLED
        )
        self.btn_pause.grid(row=0, column=1, padx=3, pady=3, sticky='ew')
        
        self.btn_stop = self._creer_bouton(
            btn_grid, "⏹  STOP", COULEURS.danger, self._on_stop, state=tk.DISABLED
        )
        self.btn_stop.grid(row=1, column=0, padx=3, pady=3, sticky='ew')
        
        self.btn_reset = self._creer_bouton(
            btn_grid, "🔄  RESET", COULEURS.accent, self._on_reset
        )
        self.btn_reset.grid(row=1, column=1, padx=3, pady=3, sticky='ew')
    
    def _creer_section_scenarios(self) -> None:
        """Section sélection scénario"""
        section = self._creer_section("SCÉNARIO")
        
        for scenario in Scenario:
            frame = tk.Frame(section, bg=COULEURS.bg_panel)
            frame.pack(fill=tk.X, pady=2)
            
            rb = tk.Radiobutton(
                frame,
                text=f"  {scenario.emoji}  {scenario.value}",
                variable=self.scenario_var,
                value=scenario.value,
                command=self._on_scenario_change,
                bg=COULEURS.bg_panel,
                fg=COULEURS.text_primary,
                selectcolor=COULEURS.bg_card,
                activebackground=COULEURS.bg_panel,
                activeforeground=COULEURS.accent,
                font=('Segoe UI', 10),
                cursor='hand2',
                anchor='w',
                indicatoron=True,
                bd=0,
                highlightthickness=0
            )
            rb.pack(fill=tk.X, padx=5)
    
    def _creer_section_feux_manuels(self) -> None:
        """Section contrôle manuel des feux"""
        section = self._creer_section("CONTRÔLE MANUEL")
        
        self.label_manuel = tk.Label(
            section,
            text="Sélectionnez 'Mode manuel' pour activer",
            font=('Segoe UI', 8),
            bg=COULEURS.bg_panel,
            fg=COULEURS.text_secondary
        )
        self.label_manuel.pack(anchor='w', pady=(0, 8))
        
        # Voie 1
        v1_frame = tk.Frame(section, bg=COULEURS.bg_panel)
        v1_frame.pack(fill=tk.X, pady=3)
        
        tk.Label(
            v1_frame,
            text="Voie N↔S :",
            font=('Segoe UI', 9),
            bg=COULEURS.bg_panel,
            fg=COULEURS.text_secondary,
            width=10,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self._creer_boutons_feu(v1_frame, 1)
        
        # Voie 2
        v2_frame = tk.Frame(section, bg=COULEURS.bg_panel)
        v2_frame.pack(fill=tk.X, pady=3)
        
        tk.Label(
            v2_frame,
            text="Voie E↔O :",
            font=('Segoe UI', 9),
            bg=COULEURS.bg_panel,
            fg=COULEURS.text_secondary,
            width=10,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self._creer_boutons_feu(v2_frame, 2)
    
    def _creer_section_status(self) -> None:
        """Section status des feux"""
        section = self._creer_section("ÉTAT DES FEUX")
        
        card = tk.Frame(section, bg=COULEURS.bg_card, padx=15, pady=10)
        card.pack(fill=tk.X)
        
        self.label_feu_v1 = tk.Label(
            card,
            text="Voie N↔S : 🟢 VERT",
            font=('Segoe UI', 11, 'bold'),
            bg=COULEURS.bg_card,
            fg=COULEURS.success
        )
        self.label_feu_v1.pack(anchor='w', pady=2)
        
        self.label_feu_v2 = tk.Label(
            card,
            text="Voie E↔O : 🔴 ROUGE",
            font=('Segoe UI', 11, 'bold'),
            bg=COULEURS.bg_card,
            fg=COULEURS.danger
        )
        self.label_feu_v2.pack(anchor='w', pady=2)
        
        tk.Frame(card, bg=COULEURS.text_secondary, height=1).pack(fill=tk.X, pady=8)
        
        self.label_status = tk.Label(
            card,
            text="⏹  ARRÊTÉ",
            font=('Segoe UI', 14, 'bold'),
            bg=COULEURS.bg_card,
            fg=COULEURS.danger
        )
        self.label_status.pack(pady=5)
    
    def _creer_section_stats(self) -> None:
        """Section statistiques"""
        section = self._creer_section("STATISTIQUES")
        
        stats_frame = tk.Frame(section, bg=COULEURS.bg_panel)
        stats_frame.pack(fill=tk.X)
        
        self.label_voitures = tk.Label(
            stats_frame,
            text="🚗  Véhicules : 0",
            font=('Segoe UI', 10),
            bg=COULEURS.bg_panel,
            fg=COULEURS.text_primary
        )
        self.label_voitures.pack(anchor='w', pady=1)
        
        self.label_temps = tk.Label(
            stats_frame,
            text="⏱  Temps : 00:00",
            font=('Segoe UI', 10),
            bg=COULEURS.bg_panel,
            fg=COULEURS.text_primary
        )
        self.label_temps.pack(anchor='w', pady=1)
    
    def _creer_section(self, titre: str) -> tk.Frame:
        """Crée une section avec titre"""
        container = tk.Frame(self, bg=COULEURS.bg_panel)
        container.pack(fill=tk.X, padx=15, pady=10)
        
        title_label = tk.Label(
            container,
            text=titre,
            font=('Segoe UI', 9, 'bold'),
            bg=COULEURS.bg_panel,
            fg=COULEURS.accent
        )
        title_label.pack(anchor='w', pady=(0, 8))
        
        return container
    
    def _creer_bouton(self, parent, text: str, color: str, 
                      command: Callable, state=tk.NORMAL) -> tk.Button:
        """Crée un bouton stylisé"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=('Segoe UI', 10, 'bold'),
            bg=color,
            fg='white',
            activebackground=color,
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            height=2,
            state=state,
            bd=0
        )
        
        original_color = color
        
        def on_enter(e):
            if btn['state'] != tk.DISABLED:
                btn.configure(bg=self._lighten_color(original_color))
        
        def on_leave(e):
            if btn['state'] != tk.DISABLED:
                btn.configure(bg=original_color)
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def _lighten_color(self, hex_color: str) -> str:
        """Éclaircit une couleur hex"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r * 1.2))
        g = min(255, int(g * 1.2))
        b = min(255, int(b * 1.2))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _creer_boutons_feu(self, parent: tk.Widget, voie: int) -> None:
        """Crée les boutons de feu pour une voie"""
        feux = [
            ('🟢', EtatFeu.VERT, '#27AE60'),
            ('🟡', EtatFeu.ORANGE, '#F39C12'),
            ('🔴', EtatFeu.ROUGE, '#E74C3C')
        ]
        
        for emoji, etat, color in feux:
            btn = tk.Button(
                parent,
                text=emoji,
                command=lambda v=voie, e=etat: self._on_feu_manuel(v, e),
                font=('Segoe UI Emoji', 16),
                bg=COULEURS.bg_card,
                activebackground=color,
                relief=tk.FLAT,
                cursor='hand2',
                width=3,
                height=1,
                bd=0
            )
            btn.pack(side=tk.LEFT, padx=3)
    
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
            self.label_manuel.config(text="✓ Mode manuel actif", fg=COULEURS.success)
        else:
            self.label_manuel.config(
                text="Sélectionnez 'Mode manuel' pour activer",
                fg=COULEURS.text_secondary
            )
    
    def _on_feu_manuel(self, voie: int, etat: EtatFeu) -> None:
        if self.scenario_var.get() != Scenario.MANUEL.value:
            messagebox.showinfo(
                "Mode manuel",
                "Activez d'abord le mode manuel\npour contrôler les feux."
            )
            return
        
        if 'feu_manuel' in self.callbacks:
            self.callbacks['feu_manuel'](voie, etat)
    
    # === MISES À JOUR ===
    
    def update_etat_feux(self, etat_v1: EtatFeu, etat_v2: EtatFeu) -> None:
        """Met à jour l'affichage des feux"""
        mapping = {
            EtatFeu.VERT: ('🟢 VERT', COULEURS.success),
            EtatFeu.ORANGE: ('🟡 ORANGE', COULEURS.warning),
            EtatFeu.ROUGE: ('🔴 ROUGE', COULEURS.danger),
            EtatFeu.ORANGE_CLIGNOTANT: ('🟡 CLIGNOTANT', COULEURS.warning),
            EtatFeu.ETEINT: ('⚫ ÉTEINT', COULEURS.text_secondary)
        }
        
        txt1, col1 = mapping.get(etat_v1, ('?', COULEURS.text_secondary))
        txt2, col2 = mapping.get(etat_v2, ('?', COULEURS.text_secondary))
        
        self.label_feu_v1.config(text=f"Voie N↔S : {txt1}", fg=col1)
        self.label_feu_v2.config(text=f"Voie E↔O : {txt2}", fg=col2)
    
    def update_status(self, en_cours: bool, en_pause: bool) -> None:
        """Met à jour le status"""
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
        self.label_voitures.config(text=f"🚗  Véhicules : {nb_voitures}")
        m, s = divmod(temps_sec, 60)
        self.label_temps.config(text=f"⏱  Temps : {m:02d}:{s:02d}")


class InterfaceGraphique:
    """Interface principale redimensionnable"""
    
    PANEL_WIDTH = 280
    
    def __init__(self, titre: str = "Simulateur de Carrefour - Thiès"):
        # Initialiser canvas_size AVANT tout le reste
        self.canvas_size = 700
        self.panneau = None
        self.callbacks = {}
        self.is_fullscreen = False
        
        # Créer la fenêtre
        self.root = tk.Tk()
        self.root.title(f"🚦 {titre}")
        self.root.configure(bg=COULEURS.bg_dark)
        
        # Dimensions écran
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        
        # Taille initiale (90% de l'écran)
        w = int(screen_w * 0.9)
        h = int(screen_h * 0.85)
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2 - 30
        
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.minsize(1000, 700)
        
        # Fullscreen
        self.root.bind('<F11>', lambda e: self._toggle_fullscreen())
        self.root.bind('<Escape>', lambda e: self._exit_fullscreen())
        
        # Créer le layout
        self._creer_layout()
    
    def _toggle_fullscreen(self) -> None:
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
    
    def _exit_fullscreen(self) -> None:
        self.is_fullscreen = False
        self.root.attributes('-fullscreen', False)
    
    def _creer_layout(self) -> None:
        """Crée le layout principal"""
        # Container principal
        self.main = tk.Frame(self.root, bg=COULEURS.bg_dark)
        self.main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame gauche pour canvas
        self.left_frame = tk.Frame(self.main, bg=COULEURS.bg_dark)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Container pour centrer le canvas
        self.canvas_container = tk.Frame(self.left_frame, bg=COULEURS.bg_dark)
        self.canvas_container.pack(expand=True)
        
        # Canvas Turtle
        self.canvas = tk.Canvas(
            self.canvas_container,
            width=self.canvas_size,
            height=self.canvas_size,
            bg='#27AE60',
            highlightthickness=2,
            highlightbackground=COULEURS.accent
        )
        self.canvas.pack()
        
        # Frame droite pour panneau
        self.right_frame = tk.Frame(
            self.main,
            bg=COULEURS.bg_panel,
            width=self.PANEL_WIDTH
        )
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        self.right_frame.pack_propagate(False)
        
        # Bind resize
        self.root.bind('<Configure>', self._on_resize)
    
    def _on_resize(self, event=None) -> None:
        """Gère le redimensionnement"""
        if event and event.widget == self.root:
            self.root.after(100, self._update_canvas_size)
    
    def _update_canvas_size(self) -> None:
        """Met à jour la taille du canvas"""
        try:
            avail_w = self.root.winfo_width() - self.PANEL_WIDTH - 50
            avail_h = self.root.winfo_height() - 50
            
            size = min(avail_w, avail_h)
            size = max(500, min(size, 800))
            
            if abs(size - self.canvas_size) > 20:
                self.canvas_size = size
                self.canvas.config(width=size, height=size)
        except:
            pass
    
    def initialiser_panneau(self, callbacks: Dict[str, Callable]) -> PanneauControle:
        """Initialise le panneau de contrôle avec les callbacks"""
        self.callbacks = callbacks
        self.panneau = PanneauControle(self.right_frame, callbacks)
        self.panneau.pack(fill=tk.BOTH, expand=True)
        return self.panneau
    
    def get_canvas(self) -> tk.Canvas:
        """Retourne le canvas Tkinter"""
        return self.canvas
    
    def get_canvas_size(self) -> int:
        """Retourne la taille du canvas"""
        return self.canvas_size
    
    def set_on_close(self, callback: Callable) -> None:
        """Définit le callback de fermeture"""
        self.root.protocol("WM_DELETE_WINDOW", callback)
    
    def after(self, ms: int, callback: Callable) -> str:
        """Planifie une exécution"""
        return self.root.after(ms, callback)
    
    def after_cancel(self, id: str) -> None:
        """Annule un timer"""
        self.root.after_cancel(id)
    
    def run(self) -> None:
        """Lance la boucle principale"""
        self.root.mainloop()
    
    def destroy(self) -> None:
        """Ferme la fenêtre"""
        self.root.destroy()


if __name__ == "__main__":
    print("Test GUI...")
    
    def dummy(*args):
        print(f"Callback: {args}")
    
    gui = InterfaceGraphique()
    gui.initialiser_panneau({
        'play': dummy,
        'pause': dummy,
        'stop': dummy,
        'reset': dummy,
        'scenario_change': dummy,
        'feu_manuel': dummy
    })
    
    gui.run()