import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ================= BANCO DE DADOS ==================
conn = sqlite3.connect("rede_social.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS conexoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario1 TEXT NOT NULL,
    usuario2 TEXT NOT NULL
)
""")
conn.commit()

# ================= DFS, BFS E GRAFO ==================
def carregar_grafo():
    graph = {}
    cursor.execute("SELECT nome FROM usuarios")
    usuarios = [row[0] for row in cursor.fetchall()]
    for u in usuarios:
        graph[u] = []
    cursor.execute("SELECT usuario1, usuario2 FROM conexoes")
    for u1, u2 in cursor.fetchall():
        graph[u1].append(u2)
        graph[u2].append(u1)
    return graph

def dfs(node, visited, comp, graph):
    visited.add(node)
    comp.append(node)
    for vizinho in graph[node]:
        if vizinho not in visited:
            dfs(vizinho, visited, comp, graph)

def encontrar_componentes(graph):
    visited = set()
    comps = []
    for node in graph:
        if node not in visited:
            comp = []
            dfs(node, visited, comp, graph)
            comps.append(comp)
    return comps

def encontrar_caminho(u1, u2, graph):
    if u1 not in graph or u2 not in graph:
        return None
    visitados = {u1: None}
    fila = [u1]
    while fila:
        atual = fila.pop(0)
        if atual == u2:
            caminho = []
            while atual is not None:
                caminho.append(atual)
                atual = visitados[atual]
            return list(reversed(caminho))
        for viz in graph[atual]:
            if viz not in visitados:
                visitados[viz] = atual
                fila.append(viz)
    return None

# ================= FUNÇÕES DB ==================
def adicionar_usuario():
    nome = entry_usuario.get().strip()
    if not nome:
        messagebox.showerror("Erro", "Digite um nome")
        return
    try:
        cursor.execute("INSERT INTO usuarios (nome) VALUES (?)", (nome,))
        conn.commit()
        atualizar_selects()
        entry_usuario.delete(0, tk.END)
        atualizar_visualizacao()
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "Usuário já existe")

def remover_usuario():
    nome = combo_remove_usuario.get()
    if not nome:
        return
    cursor.execute("DELETE FROM usuarios WHERE nome=?", (nome,))
    cursor.execute("DELETE FROM conexoes WHERE usuario1=? OR usuario2=?", (nome, nome))
    conn.commit()
    atualizar_selects()
    atualizar_visualizacao()

def adicionar_conexao():
    u1 = combo_conexao1.get()
    u2 = combo_conexao2.get()
    if not u1 or not u2 or u1 == u2:
        messagebox.showerror("Erro", "Selecione dois usuários diferentes")
        return
    cursor.execute("INSERT INTO conexoes (usuario1, usuario2) VALUES (?, ?)", (u1, u2))
    conn.commit()
    atualizar_visualizacao()

def limpar_conexoes():
    cursor.execute("DELETE FROM conexoes")
    conn.commit()
    atualizar_visualizacao()

def verificar_conexao():
    u1 = combo_check1.get()
    u2 = combo_check2.get()
    if not u1 or not u2:
        messagebox.showerror("Erro", "Selecione dois usuários")
        return
    graph = carregar_grafo()
    caminho = encontrar_caminho(u1, u2, graph)
    if caminho:
        messagebox.showinfo(
            "Resultado",
            f"{u1} e {u2} estão conectados\n\n"
            f"Caminho percorrido:\n{' → '.join(caminho)}"
        )
    else:
        messagebox.showinfo("Resultado", f"{u1} e {u2} NÃO estão conectados")

# ================= INTERFACE ==================
root = tk.Tk()
root.title("Rede Social - DFS & BFS")
root.geometry("900x500")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", padding=6, relief="flat", background="#4CAF50", foreground="white")
style.map("TButton", background=[("active", "#45a049")])

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

frame_left = tk.Frame(main_frame)
frame_left.pack(side="left", fill="y", padx=10)

lf_usuario = ttk.LabelFrame(frame_left, text="Gerenciar Usuários")
lf_usuario.pack(fill="x", pady=5)
entry_usuario = ttk.Entry(lf_usuario)
entry_usuario.pack(side="left", padx=5, pady=5, expand=True, fill="x")
ttk.Button(lf_usuario, text="Adicionar", command=adicionar_usuario).pack(side="left", padx=5)
combo_remove_usuario = ttk.Combobox(lf_usuario)
combo_remove_usuario.pack(side="left", padx=5)
ttk.Button(lf_usuario, text="Remover", command=remover_usuario).pack(side="left", padx=5)

lf_conexao = ttk.LabelFrame(frame_left, text="Gerenciar Conexões")
lf_conexao.pack(fill="x", pady=5)
combo_conexao1 = ttk.Combobox(lf_conexao)
combo_conexao2 = ttk.Combobox(lf_conexao)
combo_conexao1.pack(side="left", padx=5, pady=5, expand=True, fill="x")
combo_conexao2.pack(side="left", padx=5, pady=5, expand=True, fill="x")
ttk.Button(lf_conexao, text="Conectar", command=adicionar_conexao).pack(side="left", padx=5)
ttk.Button(lf_conexao, text="Limpar conexões", command=limpar_conexoes).pack(side="left", padx=5)

lf_check = ttk.LabelFrame(frame_left, text="Verificar Conexão")
lf_check.pack(fill="x", pady=5)
combo_check1 = ttk.Combobox(lf_check)
combo_check2 = ttk.Combobox(lf_check)
combo_check1.pack(side="left", padx=5, pady=5, expand=True, fill="x")
combo_check2.pack(side="left", padx=5, pady=5, expand=True, fill="x")
ttk.Button(lf_check, text="Verificar", command=verificar_conexao).pack(side="left", padx=5)

frame_right = tk.Frame(main_frame)
frame_right.pack(side="left", fill="both", expand=True, padx=10)

lf_visual = ttk.LabelFrame(frame_right, text="Visualização da Rede")
lf_visual.pack(fill="both", expand=True, padx=5, pady=5)

fig, ax = plt.subplots(figsize=(5, 4))
canvas = FigureCanvasTkAgg(fig, master=lf_visual)
canvas.get_tk_widget().pack(fill="both", expand=True)

lf_info = ttk.LabelFrame(frame_right, text="Grupos e Conexões")
lf_info.pack(fill="both", expand=True, padx=5, pady=5)
txt_info = tk.Text(lf_info, height=10)
txt_info.pack(fill="both", expand=True)

# ================= FUNÇÕES DE ATUALIZAÇÃO ==================
def atualizar_selects():
    cursor.execute("SELECT nome FROM usuarios")
    usuarios = [row[0] for row in cursor.fetchall()]
    combo_conexao1["values"] = usuarios
    combo_conexao2["values"] = usuarios
    combo_check1["values"] = usuarios
    combo_check2["values"] = usuarios
    combo_remove_usuario["values"] = usuarios

def atualizar_visualizacao():
    graph = carregar_grafo()

    txt_info.delete("1.0", tk.END)
    comps = encontrar_componentes(graph)
    txt_info.insert(tk.END, "Grupos encontrados:\n")
    for i, comp in enumerate(comps, 1):
        txt_info.insert(tk.END, f"Grupo {i}: {', '.join(comp)}\n")
    txt_info.insert(tk.END, "\nConexões:\n")
    cursor.execute("SELECT usuario1, usuario2 FROM conexoes")
    for u1, u2 in cursor.fetchall():
        txt_info.insert(tk.END, f"{u1} ↔ {u2}\n")

    ax.clear()
    G = nx.Graph()
    for u in graph:
        G.add_node(u)
    cursor.execute("SELECT usuario1, usuario2 FROM conexoes")
    for u1, u2 in cursor.fetchall():
        G.add_edge(u1, u2)
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=800, font_size=10, ax=ax)
    canvas.draw()

atualizar_selects()
atualizar_visualizacao()
root.mainloop()
