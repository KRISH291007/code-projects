import tkinter as tk
import math
import random
import time
import threading

class ConnectFourState:
    def __init__(self, board=None, current_player='Red'):
        self.rows = 6
        self.cols = 7
        self.current_player = current_player
        if board is None:
            self.board = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        else:
            self.board = board

    def get_legal_moves(self):
        return [c for c in range(self.cols) if self.board[0][c] == ' ']

    def make_move(self, column):
        new_board = [row[:] for row in self.board]
        for r in range(self.rows - 1, -1, -1):
            if new_board[r][column] == ' ':
                new_board[r][column] = self.current_player
                break
        next_player = 'White' if self.current_player == 'Red' else 'Red'
        return ConnectFourState(new_board, next_player)

    def check_winner(self):
        for r in range(self.rows):
            for c in range(self.cols - 3):
                if self.board[r][c] != ' ' and self.board[r][c] == self.board[r][c+1] == self.board[r][c+2] == self.board[r][c+3]:
                    return self.board[r][c]
        for r in range(self.rows - 3):
            for c in range(self.cols):
                if self.board[r][c] != ' ' and self.board[r][c] == self.board[r+1][c] == self.board[r+2][c] == self.board[r+3][c]:
                    return self.board[r][c]
        for r in range(3, self.rows):
            for c in range(self.cols - 3):
                if self.board[r][c] != ' ' and self.board[r][c] == self.board[r-1][c+1] == self.board[r-2][c+2] == self.board[r-3][c+3]:
                    return self.board[r][c]
        for r in range(self.rows - 3):
            for c in range(self.cols - 3):
                if self.board[r][c] != ' ' and self.board[r][c] == self.board[r+1][c+1] == self.board[r+2][c+2] == self.board[r+3][c+3]:
                    return self.board[r][c]
        if len(self.get_legal_moves()) == 0:
            return 'Tie'
        return None

    def is_terminal(self):
        return self.check_winner() is not None


class MCTSNode:
    def __init__(self, state, parent=None, move_taken=None):
        self.state = state
        self.parent = parent
        self.move_taken = move_taken
        self.children = []
        self.visits = 0
        self.wins = 0.0

    def is_fully_expanded(self):
        return len(self.children) == len(self.state.get_legal_moves())

    def get_best_child(self, exploration_weight):
        best_value = -float('inf')
        best_nodes = []
        for child in self.children:
            if child.visits == 0:
                uct_value = float('inf')
            else:
                if self.state.current_player == 'White':
                    exploitation = child.wins / child.visits
                else:
                    exploitation = 1.0 - (child.wins / child.visits)
                exploration = exploration_weight * math.sqrt(math.log(self.visits) / child.visits)
                uct_value = exploitation + exploration
            
            if uct_value > best_value:
                best_value = uct_value
                best_nodes = [child]
            elif uct_value == best_value:
                best_nodes.append(child)
        return random.choice(best_nodes)

def run_mcts(root_state, iterations, uct_constant):
    start_time = time.perf_counter()
    root_node = MCTSNode(state=root_state)
    
    for _ in range(int(iterations)):
        node = root_node
        while node.is_fully_expanded() and not node.state.is_terminal():
            node = node.get_best_child(uct_constant)
            
        if not node.state.is_terminal():
            legal_moves = node.state.get_legal_moves()
            tried_moves = [child.move_taken for child in node.children]
            untried_moves = [m for m in legal_moves if m not in tried_moves]
            move = random.choice(untried_moves)
            new_state = node.state.make_move(move)
            child_node = MCTSNode(state=new_state, parent=node, move_taken=move)
            node.children.append(child_node)
            node = child_node
            
        sim_state = node.state
        while not sim_state.is_terminal():
            sim_state = sim_state.make_move(random.choice(sim_state.get_legal_moves()))
            
        result = sim_state.check_winner()
        score = 1.0 if result == 'White' else 0.5 if result == 'Tie' else 0.0
        
        while node is not None:
            node.visits += 1
            node.wins += score
            node = node.parent

    end_time = time.perf_counter()
    time_ms = (end_time - start_time) * 1000

    best_child = max(root_node.children, key=lambda c: c.visits)
    confidence = (best_child.wins / best_child.visits * 100) if best_child.visits > 0 else 0
    
    distribution = {}
    for c in range(7):
        child = next((child for child in root_node.children if child.move_taken == c), None)
        if child and child.visits > 0:
            distribution[c] = {
                'visits': child.visits,
                'win_pct': (child.wins / child.visits) * 100
            }
        else:
            distribution[c] = {'visits': 0, 'win_pct': 0}

    return best_child.move_taken, time_ms, confidence, distribution



class ConnectFourGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MCTS Connect Four Arena")
        self.root.configure(bg="#1e2124")
        
        try:
            self.is_fullscreen = True
            self.root.attributes("-fullscreen", self.is_fullscreen)
        except:
            self.is_fullscreen = False
            self.root.geometry("1024x768")
            
        self.root.bind("<Escape>", self.toggle_fullscreen)
        self.root.bind("<F11>", self.toggle_fullscreen)

        self.colors = {
            'bg': '#1e2124',
            'panel': '#2b2d31',
            'board': '#3b82f6',
            'empty': '#1e2124',
            'Red': '#ef4444',
            'White': '#f8fafc',
            'text_primary': '#f8fafc',
            'text_secondary': '#94a3b8',
            'accent': '#3b82f6',
            'button_hover': '#4b5563'
        }

        self.font_title = ("Segoe UI", 16, "bold")
        self.font_heading = ("Segoe UI", 10, "bold")
        self.font_data = ("Segoe UI", 12, "bold")
        self.font_body = ("Segoe UI", 9)

        self.state = ConnectFourState()
        self.is_ai_thinking = False
        
        self.cell_size = 55 
        self.padding = 20

        self.build_ui()
        self.reset_game()

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        return "break"

    def build_ui(self):
        self.bg_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.bg_frame.pack(fill="both", expand=True)
        
        self.main_container = tk.Frame(self.bg_frame, bg=self.colors['bg'])
        self.main_container.place(relx=0.5, rely=0.5, anchor="center")

    
        header_frame = tk.Frame(self.main_container, bg=self.colors['bg'])
        header_frame.pack(fill="x", pady=(0, 15))
        tk.Label(header_frame, text="Try the MCTS Connect Four Arena", 
                 font=self.font_title, bg=self.colors['bg'], fg=self.colors['text_primary']).pack(side="left")
        
        
        tk.Label(header_frame, text="(Press ESC to exit Fullscreen)", 
                 font=self.font_body, bg=self.colors['bg'], fg=self.colors['text_secondary']).pack(side="right", anchor="s")

       
        self.status_frame = tk.Frame(self.main_container, bg=self.colors['panel'], bd=0)
        self.status_frame.pack(fill="x", pady=(0, 15))
        
        self.lbl_status_val = self._create_stat_block(self.status_frame, "Status", "Your Turn", 0)
        self.lbl_time_val = self._create_stat_block(self.status_frame, "MCTS Time", "0.0ms", 1)
        self.lbl_conf_val = self._create_stat_block(self.status_frame, "Best Confidence", "0%", 2)
        
        for i in range(3): self.status_frame.grid_columnconfigure(i, weight=1)

       
        self.board_frame = tk.Frame(self.main_container, bg=self.colors['panel'], bd=0)
        self.board_frame.pack(pady=0)
        
        cw = 7 * self.cell_size + (self.padding * 2)
        ch = 6 * self.cell_size + (self.padding * 2)
        self.canvas = tk.Canvas(self.board_frame, width=cw, height=ch, 
                                bg=self.colors['panel'], highlightthickness=0)
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.handle_click)

       
        self.stats_frame = tk.Frame(self.main_container, bg=self.colors['panel'], bd=0)
        self.stats_frame.pack(fill="x", pady=15)
        
        tk.Label(self.stats_frame, text="MCTS Root Branch Distribution", font=self.font_heading, 
                 bg=self.colors['panel'], fg=self.colors['text_secondary']).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.dist_bars = {}
        for i in range(7):
            row_frame = tk.Frame(self.stats_frame, bg=self.colors['panel'])
            row_frame.pack(fill="x", padx=20, pady=2)
            
            tk.Label(row_frame, text=f"Col {i+1}", font=self.font_heading, width=5, anchor="w", 
                     bg=self.colors['panel'], fg=self.colors['text_primary']).pack(side="left")
            
            bar_canvas = tk.Canvas(row_frame, height=6, bg=self.colors['panel'], highlightthickness=0)
            bar_canvas.pack(side="left", fill="x", expand=True, padx=15)
            
            lbl_stat = tk.Label(row_frame, text="0 visits - 0% win", font=self.font_body, width=16, anchor="e", 
                                bg=self.colors['panel'], fg=self.colors['text_secondary'])
            lbl_stat.pack(side="right")
            
            self.dist_bars[i] = {'canvas': bar_canvas, 'lbl': lbl_stat}

       
        self.control_frame = tk.Frame(self.main_container, bg=self.colors['panel'], bd=0)
        self.control_frame.pack(fill="x", pady=(0, 0))
        
      
        iter_frame = tk.Frame(self.control_frame, bg=self.colors['panel'])
        iter_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 5))
        tk.Label(iter_frame, text="Simulation Iterations", bg=self.colors['panel'], fg=self.colors['text_secondary'], font=self.font_body).pack(anchor="w")
        
        slider_iter_wrap = tk.Frame(iter_frame, bg=self.colors['panel'])
        slider_iter_wrap.pack(fill="x", pady=2)
        
        self.lbl_iter_val = tk.Label(slider_iter_wrap, text="400", bg=self.colors['panel'], fg=self.colors['text_primary'], font=self.font_heading, width=5, anchor="e")
        self.scale_iters = tk.Scale(slider_iter_wrap, from_=100, to=5000, orient="horizontal", bg=self.colors['panel'], 
                                    fg=self.colors['text_primary'], highlightthickness=0, bd=0, showvalue=False, sliderlength=15, command=self._update_iter_lbl)
        self.scale_iters.set(400)
        self.scale_iters.pack(side="left", fill="x", expand=True)
        self.lbl_iter_val.pack(side="right")

        
        uct_frame = tk.Frame(self.control_frame, bg=self.colors['panel'])
        uct_frame.grid(row=0, column=1, sticky="ew", padx=20, pady=(10, 5))
        tk.Label(uct_frame, text="Exploration Constant (UCT)", bg=self.colors['panel'], fg=self.colors['text_secondary'], font=self.font_body).pack(anchor="w")
        
        slider_uct_wrap = tk.Frame(uct_frame, bg=self.colors['panel'])
        slider_uct_wrap.pack(fill="x", pady=2)
        
        self.lbl_uct_val = tk.Label(slider_uct_wrap, text="1.4", bg=self.colors['panel'], fg=self.colors['text_primary'], font=self.font_heading, width=4, anchor="e")
        self.scale_uct = tk.Scale(slider_uct_wrap, from_=0.1, to=3.0, resolution=0.1, orient="horizontal", bg=self.colors['panel'], 
                                  fg=self.colors['text_primary'], highlightthickness=0, bd=0, showvalue=False, sliderlength=15, command=self._update_uct_lbl)
        self.scale_uct.set(1.4)
        self.scale_uct.pack(side="left", fill="x", expand=True)
        self.lbl_uct_val.pack(side="right")

        self.control_frame.grid_columnconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(1, weight=1)

       
        self.btn_reset = tk.Button(self.control_frame, text="Reset Game", command=self.reset_game, 
                                   bg=self.colors['bg'], fg=self.colors['text_primary'], bd=0, 
                                   activebackground=self.colors['button_hover'], activeforeground=self.colors['text_primary'],
                                   padx=20, pady=6, font=self.font_heading, cursor="hand2")
        self.btn_reset.grid(row=1, column=1, sticky="e", padx=20, pady=(0, 15))
        
        self.btn_reset.bind("<Enter>", lambda e: self.btn_reset.config(bg=self.colors['button_hover']))
        self.btn_reset.bind("<Leave>", lambda e: self.btn_reset.config(bg=self.colors['bg']))

    def _create_stat_block(self, parent, title, val, col):
        frame = tk.Frame(parent, bg=self.colors['panel'])
        frame.grid(row=0, column=col, pady=12)
        tk.Label(frame, text=title, font=self.font_body, bg=self.colors['panel'], fg=self.colors['text_secondary']).pack()
        val_lbl = tk.Label(frame, text=val, font=self.font_data, bg=self.colors['panel'], fg=self.colors['text_primary'])
        val_lbl.pack(pady=(2, 0))
        return val_lbl

    def _update_iter_lbl(self, val):
        if hasattr(self, 'lbl_iter_val'):
            self.lbl_iter_val.config(text=str(int(float(val))))
        
    def _update_uct_lbl(self, val):
        if hasattr(self, 'lbl_uct_val'):
            self.lbl_uct_val.config(text=f"{float(val):.1f}")

    def reset_game(self):
        self.state = ConnectFourState()
        self.is_ai_thinking = False
        self.lbl_status_val.config(text="Your Turn", fg=self.colors['text_primary'])
        self.lbl_time_val.config(text="0.0ms")
        self.lbl_conf_val.config(text="0%")
        self.root.update_idletasks()
        self.draw_board()
        self._clear_distribution()

    def draw_board(self):
        self.canvas.delete("all")
        w = 7 * self.cell_size + (self.padding * 2)
        h = 6 * self.cell_size + (self.padding * 2)
        
        self.canvas.create_rectangle(0, 0, w, h, fill=self.colors['board'], outline="")
        
        for r in range(6):
            for c in range(7):
                x0 = self.padding + c * self.cell_size + 5
                y0 = self.padding + r * self.cell_size + 5
                x1 = x0 + self.cell_size - 10
                y1 = y0 + self.cell_size - 10
                
                piece = self.state.board[r][c]
                color = self.colors['empty'] if piece == ' ' else self.colors[piece]
                self.canvas.create_oval(x0, y0, x1, y1, fill=color, outline="")

    def handle_click(self, event):
        if self.is_ai_thinking or self.state.is_terminal() or self.state.current_player != 'Red':
            return
            
        col = (event.x - self.padding) // self.cell_size
        if 0 <= col < 7 and col in self.state.get_legal_moves():
            self.state = self.state.make_move(col)
            self.draw_board()
            
            if self.check_game_over(): return
            self.trigger_ai()

    def trigger_ai(self):
        self.is_ai_thinking = True
        self.lbl_status_val.config(text="AI Thinking...", fg=self.colors['text_secondary'])
        
        iters = self.scale_iters.get()
        uct = self.scale_uct.get()
        
        threading.Thread(target=self._ai_worker, args=(iters, uct), daemon=True).start()

    def _ai_worker(self, iters, uct):
        best_col, time_ms, conf, dist = run_mcts(self.state, iters, uct)
        self.root.after(0, self._apply_ai_move, best_col, time_ms, conf, dist)

    def _apply_ai_move(self, best_col, time_ms, conf, dist):
        self.state = self.state.make_move(best_col)
        self.draw_board()
        self.update_stats(time_ms, conf, dist)
        self.is_ai_thinking = False
        
        if not self.check_game_over():
            self.lbl_status_val.config(text="Your Turn", fg=self.colors['text_primary'])

    def check_game_over(self):
        winner = self.state.check_winner()
        if winner:
            if winner == 'Tie':
                self.lbl_status_val.config(text="Match Drawn", fg=self.colors['text_secondary'])
            else:
                color = self.colors['text_primary'] if winner == 'White' else self.colors['Red']
                text = "AI Won!" if winner == 'White' else "You Won!"
                self.lbl_status_val.config(text=text, fg=color)
            return True
        return False

    def update_stats(self, time_ms, conf, dist):
        self.lbl_time_val.config(text=f"{time_ms:.1f}ms")
        self.lbl_conf_val.config(text=f"{conf:.0f}%")
        
        max_visits = max((d['visits'] for d in dist.values()), default=1)
        if max_visits == 0: max_visits = 1

        for col, data in dist.items():
            canvas = self.dist_bars[col]['canvas']
            canvas.delete("all")
            width = max(canvas.winfo_width(), 100)
            
            canvas.create_rectangle(0, 0, width, 6, fill=self.colors['bg'], outline="", width=0)
            
            v, w_pct = data['visits'], data['win_pct']
            self.dist_bars[col]['lbl'].config(text=f"{v} visits - {w_pct:.0f}% win")
            
            if v > 0:
                bar_len = (v / max_visits) * width
                canvas.create_rectangle(0, 0, bar_len, 6, fill=self.colors['accent'], outline="", width=0)

    def _clear_distribution(self):
        for col in range(7):
            canvas = self.dist_bars[col]['canvas']
            canvas.delete("all")
            width = max(canvas.winfo_width(), 100)
            canvas.create_rectangle(0, 0, width, 6, fill=self.colors['bg'], outline="", width=0)
            self.dist_bars[col]['lbl'].config(text="0 visits - 0% win")


if __name__ == "__main__":
    root = tk.Tk()
    app = ConnectFourGUI(root)
    root.mainloop()
