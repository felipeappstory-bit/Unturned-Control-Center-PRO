# -*- coding: utf-8 -*-
"""Editor das chaves existentes em arquivos Config_*Difficulty.txt de diferentes mundos."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
from datetime import datetime
import shutil, re, json, hashlib, os

SECTIONS=["Items","Vehicles","Zombies","Animals","Barricades","Structures","Players","Objects","Events","Gameplay"]
TRADUCOES = {'Can_Target_Barricades': 'Zumbis podem atacar barricadas', 'Can_Target_Structures': 'Zumbis podem atacar construções', 'Can_Target_Vehicles': 'Zumbis podem atacar veículos', 'Can_Target_Objects': 'Zumbis podem atacar objetos', 'Respawn_Time': 'Tempo para reaparecer (segundos)', 'Max_Instances_Tiny': 'Máximo de animais: mapa minúsculo', 'Max_Instances_Small': 'Máximo de animais: mapa pequeno', 'Max_Instances_Medium': 'Máximo de animais: mapa médio', 'Max_Instances_Large': 'Máximo de animais: mapa grande', 'Max_Instances_Insane': 'Máximo de animais: mapa enorme', 'Armor_Lowtier_Multiplier': 'Multiplicador de proteção: nível baixo', 'Armor_Hightier_Multiplier': 'Multiplicador de proteção: nível alto', 'Gun_Lowcal_Damage_Multiplier': 'Dano de armas de baixo calibre', 'Gun_Highcal_Damage_Multiplier': 'Dano de armas de alto calibre', 'Melee_Damage_Multiplier': 'Dano corpo a corpo', 'Spawn_With_Max_Skills': 'Nascer com habilidades máximas', 'Lose_Skills_PvP': 'Perda de habilidades no PvP', 'Lose_Skills_PvE': 'Perda de habilidades no PvE', 'Lose_Skill_Levels_PvP': 'Perda de níveis de habilidade no PvP', 'Lose_Skill_Levels_PvE': 'Perda de níveis de habilidade no PvE', 'Lose_Experience_PvP': 'Perda de experiência no PvP', 'Lose_Experience_PvE': 'Perda de experiência no PvE'}

import json
import threading
import urllib.parse
import urllib.request

CACHE_FILE = Path(__file__).with_name("traducoes_cache.json")
try:
    CACHE = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
except (OSError, ValueError):
    CACHE = {}
TRADUCOES.update(CACHE)
translation_pending = set()

def auto_translate_keys():
    missing = set()
    for options in sections.values():
        missing.update(k for k in options if k not in TRADUCOES and k not in translation_pending)
    if not missing:
        return
    translation_pending.update(missing)
    notice.set("Traduzindo novas opções... requer internet.")
    def worker(keys):
        results = {}
        for key in sorted(keys):
            try:
                phrase = key.replace("_", " ")
                params = urllib.parse.urlencode({"client":"gtx","sl":"en","tl":"pt","dt":"t","q":phrase})
                req = urllib.request.Request(
                    "https://translate.googleapis.com/translate_a/single?" + params,
                    headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5) as response:
                    data=json.loads(response.read().decode("utf-8"))
                translated="".join(part[0] for part in data[0] if part and part[0])
                if translated.strip():
                    results[key]=translated.strip()
            except Exception:
                pass
        def finish():
            TRADUCOES.update(results)
            CACHE.update(results)
            translation_pending.difference_update(keys)
            if results:
                try:
                    CACHE_FILE.write_text(json.dumps(CACHE,ensure_ascii=False,indent=2),encoding="utf-8")
                except OSError:
                    pass
            refresh()
            notice.set(f"Tradução automática: {len(results)} nova(s) opção(ões). "
                       "Sem tradução? Confira a internet ou use o nome original.")
        app.after(0, finish)
    threading.Thread(target=worker,args=(missing,),daemon=True).start()

def atualizar_pela_internet():
    """Atualiza traduções das chaves presentes; não altera mundos nem executáveis."""
    if not path.get() or not sections or not any(sections.values()):
        messagebox.showinfo("Atualização", "Primeiro abra o arquivo de configuração de um mundo.")
        return
    if not messagebox.askyesno("Atualizar traduções", "Consultar a internet para atualizar as traduções das opções deste mundo?\n\nO arquivo do jogo não será modificado."):
        return
    keys = sorted({k for opts in sections.values() for k in opts})
    notice.set(f"Consultando traduções pela internet: {len(keys)} opções...")
    def worker():
        results = {}
        errors = 0
        for key in keys:
            try:
                params = urllib.parse.urlencode({"client":"gtx", "sl":"en", "tl":"pt", "dt":"t", "q":key.replace("_", " ")})
                req = urllib.request.Request("https://translate.googleapis.com/translate_a/single?" + params, headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=4) as response:
                    data = json.loads(response.read().decode("utf-8"))
                translated = "".join(part[0] for part in data[0] if part and part[0]).strip()
                if translated: results[key] = translated
            except Exception:
                errors += 1
        def finish():
            # Traduções revisadas manualmente têm prioridade sobre traduções automáticas.
            CACHE.update(results)
            for k, v in results.items():
                if k not in TRADUCOES or k in CACHE_ANTERIOR:
                    TRADUCOES[k] = v
            try:
                CACHE_FILE.write_text(json.dumps(CACHE, ensure_ascii=False, indent=2), encoding="utf-8")
            except OSError:
                messagebox.showwarning("Cache", "Traduções recebidas, mas não foi possível salvar o cache na pasta do programa.")
            refresh()
            notice.set(f"Internet: {len(results)} traduções recebidas; {errors} falhas. Arquivo do mundo preservado.")
            messagebox.showinfo("Atualização concluída", f"Traduções recebidas: {len(results)}\nFalhas de conexão: {errors}\n\nNenhum arquivo do jogo foi alterado.\nAs opções disponíveis continuam dependendo da versão instalada do Unturned.")
        app.after(0, finish)
    threading.Thread(target=worker, daemon=True).start()

CACHE_ANTERIOR = set(CACHE)

def ver_novidades_unturned():
    import webbrowser
    webbrowser.open("https://store.steampowered.com/news/app/304930")

NOMES_ABAS = {"Items":"Itens", "Vehicles":"Veículos", "Zombies":"Zumbis", "Animals":"Animais", "Barricades":"Barricadas", "Structures":"Construções", "Players":"Jogador", "Objects":"Objetos", "Events":"Eventos", "Gameplay":"Jogabilidade"}

EXPLICACOES = {
    "Respawn_Time": "Tempo, em segundos, para reaparecimento de animais.",
    "Spawn_With_Max_Skills": "Habilita o nascimento com habilidades máximas quando o jogo aplicar essa regra.",
    "Can_Target_Barricades": "Permite ou impede que zumbis escolham barricadas como alvo.",
    "Can_Target_Structures": "Permite ou impede que zumbis escolham estruturas como alvo.",
    "Gun_Lowcal_Damage_Multiplier": "Multiplica o dano de armas de baixo calibre. Zero reduz esse dano a zero.",
    "Gun_Highcal_Damage_Multiplier": "Multiplica o dano de armas de alto calibre. Zero reduz esse dano a zero.",
    "Melee_Damage_Multiplier": "Multiplica o dano corpo a corpo. Zero reduz esse dano a zero.",
}

def editar_valor(s, key, value):
    dialog=tk.Toplevel(app)
    dialog.title("Editar configuração")
    dialog.geometry("520x280")
    dialog.transient(app)
    dialog.grab_set()
    content=ttk.Frame(dialog,padding=18)
    content.pack(fill="both",expand=True)
    ttk.Label(content,text=TRADUCOES.get(key,key),font=("Segoe UI",13,"bold"),wraplength=470).pack(anchor="w")
    ttk.Label(content,text=f"Nome original: {key}",wraplength=470).pack(anchor="w",pady=(4,8))
    ttk.Label(content,text=EXPLICACOES.get(key,"Altere o valor com cuidado. A tradução é apenas informativa; o jogo usa o nome original."),wraplength=470).pack(anchor="w",pady=(0,12))
    selected=tk.StringVar(value=value)
    if value.lower() in ("true","false"):
        ttk.Radiobutton(content,text="Sim / Ativado",variable=selected,value="true").pack(anchor="w")
        ttk.Radiobutton(content,text="Não / Desativado",variable=selected,value="false").pack(anchor="w")
    else:
        ttk.Entry(content,textvariable=selected,width=24).pack(anchor="w")
        ttk.Label(content,text="Digite um número ou valor aceito pelo Unturned.").pack(anchor="w",pady=5)
    def confirm():
        v=selected.get().strip()
        if not v or any(c.isspace() for c in v):
            messagebox.showwarning("Valor inválido","Use um valor sem espaços.",parent=dialog)
            return
        sections[s][key]=v
        refresh()
        dialog.destroy()
    ttk.Button(content,text="✓ Confirmar alteração",command=confirm).pack(anchor="e",pady=(12,0))

app=tk.Tk()
app.title("UNTURNED CONTROL CENTER PRO")
app.geometry("1150x750")
app.minsize(820,580)
path=tk.StringVar()
notice=tk.StringVar(value="Abra um arquivo de dificuldade para editar todas as opções existentes.")
original=""
sections={}
order=[]
def parse(text):
    # Captura seções simples, preserva comentários e texto original na gravação
    result={}
    for m in re.finditer(r"(?m)^([A-Za-z_]\w*)[ \t]*\r?\n\{[ \t]*\r?\n(.*?)^\}",text,re.S|re.M):
        name=m.group(1)
        entries={}
        for line in m.group(2).splitlines():
            match=re.match(r"^\s*([A-Za-z_]\w*)\s+(\S+)",line)
            if match: entries[match.group(1)]=match.group(2)
        result[name]=entries
    return result
def pick():
    p=filedialog.askopenfilename(title="Escolha a configuração do mundo (Easy, Normal ou Hard)",filetypes=[("Configuração de dificuldade","Config_*Difficulty.txt"),("TXT","*.txt"),("Todos","*.*")])
    if p: path.set(p); load()
def load():
    global original,sections
    try:
        original=Path(path.get()).read_text(encoding="utf-8-sig")
        sections=parse(original)
        for s in SECTIONS: sections.setdefault(s,{})
        refresh()
        notice.set(f"Carregado: {Path(path.get()).parent.name} / {Path(path.get()).stem}. Exibindo {sum(map(len, sections.values()))} opções presentes no arquivo.")
        auto_translate_keys()
    except Exception as e: messagebox.showerror("Erro",str(e))
def refresh():
    for s,tree in trees.items():
        for item in tree.get_children():tree.delete(item)
        for key,val in sorted(sections.get(s,{}).items()):
            tree.insert("","end",values=(key,TRADUCOES.get(key,"Tradução não disponível"),"☑ Sim" if str(val).lower()=="true" else "☐ Não" if str(val).lower()=="false" else val))
def change(s):
    tree=trees[s]
    sel=tree.selection()
    if not sel:return
    key,traducao,val=tree.item(sel[0],"values")
    editar_valor(s,key,sections[s][key])

def add(s):
    k=simpledialog.askstring("Adicionar chave",f"Nome EXATO da opção em {s}:",parent=app)
    if k is None:return
    k=k.strip()
    if not re.fullmatch(r"[A-Za-z_]\w*",k):
        messagebox.showwarning("Nome inválido","Use apenas letras, números e _.");return
    v=simpledialog.askstring("Valor",f"Valor para {k}:",parent=app)
    if v is None:return
    v=v.strip()
    if not v or any(c.isspace() for c in v):
        messagebox.showwarning("Valor inválido","Informe um valor sem espaços.");return
    sections[s][k]=v;refresh();auto_translate_keys()
def remove(s):
    tree=trees[s];sel=tree.selection()
    if not sel:return
    k=tree.item(sel[0],"values")[0]
    if messagebox.askyesno("Remover",f"Remover {k} de {s}?"):
        sections[s].pop(k,None);refresh()
def apply_to_text(text):
    for name,values in sections.items():
        pattern=re.compile(r"(?m)^("+re.escape(name)+r"[ \t]*\r?\n\{[ \t]*\r?\n)(.*?)(^\})",re.S|re.M)
        match=pattern.search(text)
        if not match:
            text+="\n"+name+"\n{\n}\n"
            match=pattern.search(text)
        body=match.group(2)
        existing=set()
        newlines=[]
        for line in body.splitlines(keepends=True):
            m=re.match(r"^(\s*)([A-Za-z_]\w*)(\s+)(\S+)(.*?)(\r?\n|$)",line)
            if m:
                key=m.group(2)
                if key not in values:continue
                existing.add(key)
                newlines.append(m.group(1)+key+m.group(3)+values[key]+m.group(5)+m.group(6))
            else:newlines.append(line)
        body="".join(newlines)
        if body and not body.endswith(("\n","\r")):body+="\n"
        for k,v in values.items():
            if k not in existing:body+=f"\t{k} {v}\n"
        text=text[:match.start(2)]+body+text[match.end(2):]
    return text
def save():
    p=Path(path.get())
    if not p.is_file():
        messagebox.showwarning("Arquivo","Selecione um arquivo de dificuldade primeiro.");return
    try:
        current=p.read_text(encoding="utf-8-sig")
        if current != original and not messagebox.askyesno("Arquivo mudou", "O arquivo foi alterado fora do configurador desde que você o abriu. Salvar pode substituir alterações recentes. Continuar?"):
            return
        backup=p.with_name(p.stem+"_backup_"+datetime.now().strftime("%Y%m%d_%H%M%S")+p.suffix)
        shutil.copy2(p,backup)
        p.write_text(apply_to_text(original),encoding="utf-8-sig")
        notice.set(f"Salvo. Backup: {backup.name}")
        messagebox.showinfo("Salvo","Arquivo atualizado.\nBackup criado em:\n"+str(backup)+"\n\nReinicie o mundo para aplicar.")
        load()
    except Exception as e:messagebox.showerror("Erro ao salvar",str(e))
def profile_path():
    # Um perfil separado para cada arquivo de mundo/dificuldade.
    key=hashlib.sha256(str(Path(path.get()).resolve()).lower().encode("utf-8")).hexdigest()[:20]
    root=Path(os.environ.get("LOCALAPPDATA",str(Path.home()))) / "UnturnedConfigurador" / "perfis"
    root.mkdir(parents=True,exist_ok=True)
    return root / (key+".json")
def store_profile():
    if not Path(path.get()).is_file():
        messagebox.showwarning("Arquivo", "Abra seu Config_HardDifficulty.txt primeiro.");return
    try:
        profile=profile_path()
        if profile.exists() and not messagebox.askyesno("Substituir perfil", "Você já tem um perfil guardado para este mundo. Substituir pelo que está na tela agora?"):
            return
        data={"source":str(Path(path.get()).resolve()),"sections":sections,"saved_at":datetime.now().isoformat()}
        profile.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
        notice.set("Preferências guardadas! Use Restaurar quando quiser.")
        messagebox.showinfo("Perfil salvo", "Suas configurações foram guardadas. Você pode restaurá-las mais tarde.")
    except Exception as e:messagebox.showerror("Erro ao guardar",str(e))
def restore_profile():
    global sections
    if not Path(path.get()).is_file():
        messagebox.showwarning("Arquivo", "Abra seu Config_HardDifficulty.txt primeiro.");return
    profile=profile_path()
    if not profile.exists():
        messagebox.showinfo("Nenhum perfil salvo", "Clique primeiro em GUARDAR MINHAS CONFIGURAÇÕES para criar seu perfil.")
        return
    try:
        data=json.loads(profile.read_text(encoding="utf-8"))
        if str(Path(path.get()).resolve()) != data.get("source"):
            raise ValueError("Este perfil pertence a outro arquivo.")
        if not messagebox.askyesno("Restaurar", "Restaurar as configurações guardadas para este mundo?\n\nAs mudanças aparecerão na tela. Clique em SALVAR para aplicá-las no jogo."):
            return
        sections={k:dict(v) for k,v in data["sections"].items()}
        for name in SECTIONS:sections.setdefault(name,{})
        refresh()
        notice.set("Perfil restaurado na tela. Clique SALVAR para aplicar ao jogo.")
    except Exception as e:messagebox.showerror("Erro ao restaurar",str(e))
def preset():
    if not sections:
        messagebox.showwarning("Abra um arquivo","Selecione seu arquivo primeiro.");return
    if not messagebox.askyesno("Aplicar perfil","Aplicar suas preferências HARD?\n\nConstruções protegidas, zumbis sem atacar construções, mais animais e nascer com habilidades máximas.\n\nOutras opções existentes serão preservadas."):return
    for name in ("Barricades","Structures"):
        for k in ("Armor_Lowtier_Multiplier","Armor_Hightier_Multiplier","Gun_Lowcal_Damage_Multiplier","Gun_Highcal_Damage_Multiplier","Melee_Damage_Multiplier"):
            sections[name][k]="0"
    for k in ("Can_Target_Barricades","Can_Target_Structures","Can_Target_Vehicles","Can_Target_Objects"):
        sections["Zombies"][k]="false"
    sections["Animals"].update({"Respawn_Time":"45","Max_Instances_Tiny":"12","Max_Instances_Small":"24","Max_Instances_Medium":"48","Max_Instances_Large":"96","Max_Instances_Insane":"128"})
    sections["Players"]["Spawn_With_Max_Skills"]="true"
    refresh();notice.set("Perfil aplicado na tela. Clique em SALVAR para gravar.")
def search():
    q=search_var.get().lower().strip()
    if not q:return
    for s in SECTIONS:
        for k,v in sections.get(s,{}).items():
            if q in k.lower() or q in str(v).lower() or q in TRADUCOES.get(k,"").lower():
                notebook.select(tabs[s])
                tree=trees[s]
                for item in tree.get_children():
                    if tree.item(item,"values")[0]==k:
                        tree.selection_set(item);tree.see(item);return
    messagebox.showinfo("Busca","Não encontrada nas opções presentes no arquivo.")

def detect_configs():
    """Busca em locais comuns e nas bibliotecas Steam sem exigir caminho manual."""
    import os
    bases = []
    home = Path.home()
    bases += [home/"AppData"/"Local"/"Unturned", home/"Documents"/"Unturned"]
    for drive in "CDEFGHIJ":
        bases += [Path(f"{drive}:/Program Files (x86)/Steam"),
                  Path(f"{drive}:/Program Files/Steam"),
                  Path(f"{drive}:/Steam"),
                  Path(f"{drive}:/SteamLibrary")]
    steamdirs = []
    for base in bases:
        if (base/"steamapps").is_dir(): steamdirs.append(base)
        vdf=base/"steamapps"/"libraryfolders.vdf"
        if vdf.is_file():
            try:
                import re
                for lib in re.findall(r'"path"\s+"([^"]+)"',vdf.read_text(encoding="utf-8-sig")):
                    steamdirs.append(Path(lib.replace("\\\\","\\")))
            except Exception: pass
    roots=[d/"steamapps"/"common"/"Unturned" for d in steamdirs]
    roots += [d/"steamapps"/"common"/"Unturned"/"Unturned" for d in steamdirs]
    roots += [home/"AppData"/"LocalLow"/"Smartly Dressed Games"/"Unturned"]
    candidates=[]
    for root in roots+bases[:2]:
        if not root.is_dir(): continue
        for rel in ("Worlds",""):
            folder=root/rel
            if not folder.is_dir(): continue
            try:
                for p in folder.glob("Singleplayer_*/Config_*Difficulty.txt"):
                    candidates.append(p)
                for p in folder.glob("**/Config_*Difficulty.txt"):
                    candidates.append(p)
            except (PermissionError,OSError): pass
    return list(dict.fromkeys(map(str,candidates)))
def auto_find():
    candidates=detect_configs()
    if not candidates:
        messagebox.showinfo("Busca automática",
            "Não encontrei arquivos de dificuldade automaticamente.\n"
            "Clique em 'Abrir arquivo' e selecione um Config_*Difficulty.txt do mundo desejado.")
        return
    if len(candidates)==1:
        path.set(candidates[0]);load();return
    win=tk.Toplevel(app);win.title("Escolha seu mundo e dificuldade");win.geometry("800x310")
    ttk.Label(win,text="Encontrei estes arquivos. Escolha o mundo que deseja editar:").pack(anchor="w",padx=12,pady=12)
    lb=tk.Listbox(win);lb.pack(fill="both",expand=True,padx=12)
    for p in candidates:lb.insert("end",p)
    lb.selection_set(0)
    def choose():
        if not lb.curselection():return
        path.set(candidates[lb.curselection()[0]]);win.destroy();load()
    ttk.Button(win,text="Usar arquivo selecionado",command=choose).pack(pady=10)


# Ferramentas adicionais reunidas em uma única janela.
def central_ferramentas():
    win=tk.Toplevel(app)
    win.title("Central de ferramentas | Unturned")
    win.geometry("850x620")
    nb=ttk.Notebook(win);nb.pack(fill="both",expand=True,padx=12,pady=12)
    def page(title):
        frame=ttk.Frame(nb,padding=18);nb.add(frame,text=title);return frame
    presets=page("Perfis de jogo")
    ttk.Label(presets,text="Escolha um perfil para alterar valores na tela. Depois salve no painel principal.",wraplength=750).pack(anchor="w",pady=8)
    def apply_profile(which):
        if not Path(path.get()).is_file():
            messagebox.showwarning("Arquivo","Abra um mundo HARD antes de aplicar um perfil.",parent=win);return
        if not messagebox.askyesno("Confirmar","Aplicar perfil às configurações em edição? As alterações só vão ao jogo quando você salvar.",parent=win):return
        if which=="criativo":
            for category in ("Barricades","Structures"):
                for key in ("Armor_Lowtier_Multiplier","Armor_Hightier_Multiplier","Gun_Lowcal_Damage_Multiplier","Gun_Highcal_Damage_Multiplier","Melee_Damage_Multiplier"):
                    sections[category][key]="0"
            sections["Players"]["Spawn_With_Max_Skills"]="true"
            sections["Zombies"]["Can_Target_Barricades"]="false"
            sections["Zombies"]["Can_Target_Structures"]="false"
        elif which=="apocalipse":
            sections["Zombies"].update({"Spawn_Chance":"0.9","Damage_Multiplier":"1.5"})
            sections["Items"]["Spawn_Chance"]="0.3"
        elif which=="sobrevivencia":
            sections["Zombies"].update({"Spawn_Chance":"0.5","Damage_Multiplier":"1"})
            sections["Items"]["Spawn_Chance"]="0.5"
        refresh();notice.set("Perfil aplicado na tela. Salve para aplicar no jogo.")
        messagebox.showinfo("Perfil preparado","Revise as opções alteradas e clique em SALVAR no painel principal. Algumas chaves dependem da versão do jogo.",parent=win)
    for label,key in (("🏠 Criativo: proteção e habilidades","criativo"),("🧟 Apocalipse: mais zumbis, menos itens","apocalipse"),("🌿 Sobrevivência: valores equilibrados","sobrevivencia")):
        ttk.Button(presets,text=label,command=lambda k=key:apply_profile(k)).pack(fill="x",pady=7)
    ttk.Label(presets,text="Perfis são sugestões. Nem todas as chaves são suportadas por todas as versões do Unturned.",wraplength=740).pack(anchor="w",pady=12)
    commands=page("Comandos de itens")
    ttk.Label(commands,text="Gerador de texto de comando. Não executa comandos no jogo.").pack(anchor="w",pady=7)
    item=tk.StringVar();qty=tk.StringVar(value="1")
    ttk.Label(commands,text="ID numérico do item:").pack(anchor="w")
    ttk.Entry(commands,textvariable=item).pack(fill="x",pady=4)
    ttk.Label(commands,text="Quantidade:").pack(anchor="w")
    ttk.Entry(commands,textvariable=qty).pack(fill="x",pady=4)
    output=tk.StringVar(value="")
    ttk.Entry(commands,textvariable=output,state="readonly").pack(fill="x",pady=8)
    def generate():
        if not item.get().isdigit() or not qty.get().isdigit() or int(qty.get())<1:
            messagebox.showwarning("Valores inválidos","Digite um ID numérico e uma quantidade positiva.",parent=win);return
        output.set(f"/give {item.get()}/{qty.get()}")
        win.clipboard_clear();win.clipboard_append(output.get())
        messagebox.showinfo("Copiado","Comando copiado. O uso depende das permissões e comandos disponíveis no seu jogo.",parent=win)
    ttk.Button(commands,text="Gerar e copiar comando",command=generate).pack(anchor="w",pady=8)
    backups=page("Backups")
    ttk.Label(backups,text="Backups automáticos criados ao salvar o arquivo atual:",wraplength=750).pack(anchor="w")
    box=tk.Listbox(backups,height=13);box.pack(fill="both",expand=True,pady=8)
    paths=[]
    def reload_backups():
        box.delete(0,"end");paths.clear()
        p=Path(path.get())
        if not p.is_file():return
        paths.extend(sorted(p.parent.glob(p.stem+"_backup_*"+p.suffix),reverse=True))
        for backup in paths:box.insert("end",backup.name)
    def restore_backup():
        if not box.curselection():return
        p=Path(path.get());selected=paths[box.curselection()[0]]
        if not messagebox.askyesno("Restaurar backup",f"Substituir {p.name} pelo backup {selected.name}? Uma cópia de segurança será feita primeiro.",parent=win):return
        try:
            safety=p.with_name(p.stem+"_antes_restauracao_"+datetime.now().strftime("%Y%m%d_%H%M%S%f")+p.suffix)
            shutil.copy2(p,safety);shutil.copy2(selected,p);load();reload_backups()
            messagebox.showinfo("Restaurado",f"Backup restaurado. Cópia anterior: {safety.name}",parent=win)
        except Exception as exc:messagebox.showerror("Erro",str(exc),parent=win)
    ttk.Button(backups,text="Atualizar lista",command=reload_backups).pack(side="left",padx=5)
    ttk.Button(backups,text="Restaurar backup selecionado",command=restore_backup).pack(side="left",padx=5)
    reload_backups()
    mods=page("Gerenciador de mods")
    ttk.Label(mods,text="Mods separados por origem. Workshop: cancelar inscrição pela Steam. Locais: desativar e restaurar com segurança.",wraplength=850).pack(anchor="w",pady=6)
    modtree=ttk.Treeview(mods,columns=("origem","nome","local"),show="headings",selectmode="browse")
    for col,label,width in (("origem","Origem",145),("nome","Mod / ID",230),("local","Pasta",530)):
        modtree.heading(col,text=label);modtree.column(col,width=width)
    modtree.pack(fill="both",expand=True,pady=6)
    mods_found={}
    quarantine=Path.home()/"Documents"/"Unturned_Control_Center_PRO"/"Mods_Desativados"
    def roots_mods():
        steamroots=[];gameroots=[]
        p=Path(path.get())
        if p.is_file():
            for parent in p.parents:
                if parent.name.lower()=="unturned":
                    gameroots.append(parent);break
        for drive in "CDEFGHIJ":
            for stem in ("Program Files (x86)/Steam","Program Files/Steam","Steam","SteamLibrary"):
                base=Path(f"{drive}:/{stem}")
                if (base/"steamapps").is_dir():steamroots.append(base)
                vdf=base/"steamapps"/"libraryfolders.vdf"
                if vdf.is_file():
                    try:
                        for lib in re.findall(r'"path"\s+"([^"]+)"',vdf.read_text(encoding="utf-8-sig")):
                            steamroots.append(Path(lib.replace("\\\\","\\")))
                    except (OSError,UnicodeError):pass
        for root in steamroots:
            gameroots.append(root/"steamapps"/"common"/"Unturned")
        return list(dict.fromkeys(steamroots)),list(dict.fromkeys(gameroots))
    def add_mod(origin,folder):
        if not folder.is_dir():return
        label=folder.name
        meta=folder/"English.dat"
        if meta.is_file():
            try:
                match=re.search(r'^Name\s+(.+)$',meta.read_text(encoding="utf-8-sig",errors="replace"),re.M)
                if match:label=match.group(1).strip()+" ("+folder.name+")"
            except OSError:pass
        iid=modtree.insert("", "end",values=(origin,label,str(folder)))
        mods_found[iid]=(origin,folder)
    def scan_mods():
        modtree.delete(*modtree.get_children());mods_found.clear()
        steamroots,gameroots=roots_mods()
        targets=[]
        for root in steamroots:targets.append(("Steam Workshop",root/"steamapps"/"workshop"/"content"/"304930"))
        for root in gameroots:
            targets.extend([("Local",root/"Bundles"/"Workshop"),("Local",root/"Workshop"),("Local",root/"Modules")])
        targets.append(("Desativado",quarantine))
        seen=set()
        for origin,base in targets:
            if not base.is_dir():continue
            try:
                for folder in sorted(base.iterdir(),key=lambda x:x.name.lower()):
                    if folder.is_dir() and str(folder).lower() not in seen:
                        seen.add(str(folder).lower());add_mod(origin,folder)
            except OSError:pass
        if not mods_found:messagebox.showinfo("Mods","Nenhuma pasta de mod encontrada. Se necessário, abra o arquivo do seu mundo para ajudar na localização.",parent=win)
    def selected_mod():
        selection=modtree.selection()
        if not selection:
            messagebox.showwarning("Selecione","Selecione um mod na lista.",parent=win);return None
        return mods_found.get(selection[0])
    def open_folder():
        item=selected_mod()
        if item:os.startfile(str(item[1]))
    def workshop_page():
        import webbrowser
        item=selected_mod()
        if not item:return
        origin,folder=item
        if origin!="Steam Workshop" or not folder.name.isdigit():
            messagebox.showinfo("Workshop","Selecione um mod da Steam Workshop identificado pelo ID numérico.",parent=win);return
        webbrowser.open("https://steamcommunity.com/sharedfiles/filedetails/?id="+folder.name)
        messagebox.showinfo("Steam","Na página aberta, cancele a inscrição do mod. A Steam gerencia a remoção dos arquivos.",parent=win)
    def disable_mod():
        item=selected_mod()
        if not item:return
        origin,folder=item
        if origin!="Local":
            messagebox.showwarning("Proteção","Somente mods locais podem ser desativados aqui. Para mods da Steam, use 'Abrir na Steam'.",parent=win);return
        if not messagebox.askyesno("Desativar mod",f"Mover este mod para uma pasta de segurança?\n\n{folder}\n\nFeche o Unturned antes de continuar. Mundos que usam o mod podem perder conteúdo enquanto ele estiver desativado.",parent=win):return
        try:
            quarantine.mkdir(parents=True,exist_ok=True)
            dest=quarantine/(datetime.now().strftime("%Y%m%d_%H%M%S_%f")+"_"+folder.name)
            shutil.move(str(folder),str(dest))
            (dest/".ucc_origem.json").write_text(json.dumps({"original":str(folder)},ensure_ascii=False),encoding="utf-8")
            scan_mods()
        except Exception as exc:messagebox.showerror("Erro",str(exc),parent=win)
    def restore_mod():
        item=selected_mod()
        if not item:return
        origin,folder=item
        if origin!="Desativado":messagebox.showinfo("Restaurar","Selecione um mod desativado.",parent=win);return
        try:
            metadata=folder/".ucc_origem.json"
            if not metadata.is_file():raise ValueError("Este mod não possui registro de origem.")
            dest=Path(json.loads(metadata.read_text(encoding="utf-8"))["original"])
            if dest.exists():raise ValueError("A pasta de destino já existe. Nenhum arquivo foi substituído.")
            if not messagebox.askyesno("Restaurar",f"Restaurar para:\n{dest}",parent=win):return
            metadata.unlink()
            dest.parent.mkdir(parents=True,exist_ok=True)
            try:shutil.move(str(folder),str(dest))
            except Exception:
                metadata.write_text(json.dumps({"original":str(dest)},ensure_ascii=False),encoding="utf-8")
                raise
            scan_mods()
        except Exception as exc:messagebox.showerror("Erro",str(exc),parent=win)
    def delete_disabled():
        item=selected_mod()
        if not item:return
        origin,folder=item
        if origin!="Desativado":
            messagebox.showwarning("Segurança","Só é possível excluir definitivamente um mod já desativado. Mods da Steam devem ser removidos pela Steam.",parent=win);return
        if messagebox.askyesno("EXCLUSÃO DEFINITIVA",f"Apagar permanentemente esta pasta e todo seu conteúdo?\n\n{folder}\n\nEsta ação NÃO pode ser desfeita.",parent=win):
            try:shutil.rmtree(folder);scan_mods()
            except Exception as exc:messagebox.showerror("Erro",str(exc),parent=win)
    row=ttk.Frame(mods);row.pack(fill="x",pady=5)
    for label,action in (("🔎 Procurar todos",scan_mods),("📁 Abrir pasta",open_folder),("🌐 Abrir na Steam",workshop_page),("⏸ Desativar local",disable_mod),("↩ Restaurar",restore_mod),("🗑 Excluir desativado",delete_disabled)):
        ttk.Button(row,text=label,command=action).pack(side="left",padx=3)
    ttk.Label(mods,text="Nota: a busca cobre bibliotecas Steam comuns e pastas locais conhecidas. Projetos guardados em outros lugares não são detectados automaticamente.",wraplength=850).pack(anchor="w",pady=4)
    scan_mods()

main=ttk.Frame(app,padding=12);main.pack(fill="both",expand=True)
ttk.Label(main,text="🎮 UNTURNED CONTROL CENTER PRO",font=("Segoe UI",18,"bold")).pack(anchor="w")
ttk.Label(main,text="Edite todas as opções existentes no arquivo, por categoria. Opções ausentes podem ser adicionadas manualmente.").pack(anchor="w",pady=(0,12))
top=ttk.Frame(main);top.pack(fill="x",pady=4)
ttk.Entry(top,textvariable=path).pack(side="left",fill="x",expand=True,padx=(0,6))
ttk.Button(top,text="🔎 Encontrar Unturned",command=auto_find).pack(side="left",padx=5)
ttk.Button(top,text="📂 Abrir arquivo",command=pick).pack(side="left")
ttk.Button(top,text="↻ Recarregar",command=load).pack(side="left",padx=5)
ttk.Button(top,text="🌐 Atualizar traduções",command=atualizar_pela_internet).pack(side="left",padx=5)
ttk.Button(top,text="📰 Novidades do jogo",command=ver_novidades_unturned).pack(side="left",padx=5)
actions=ttk.Frame(main);actions.pack(fill="x",pady=(5,8))
ttk.Button(actions,text="🧰 CENTRAL DE FERRAMENTAS",command=central_ferramentas).pack(side="left",padx=2)
ttk.Button(actions,text="⭐ Aplicar HARD",command=preset).pack(side="left",padx=2)
ttk.Button(actions,text="💾 Guardar minhas configurações",command=store_profile).pack(side="left",padx=2)
ttk.Button(actions,text="↩ Restaurar minhas configurações",command=restore_profile).pack(side="left",padx=2)
search_var=tk.StringVar()
ttk.Entry(actions,textvariable=search_var,width=28).pack(side="right")
ttk.Button(actions,text="🔎 Buscar opção",command=search).pack(side="right",padx=5)
notebook=ttk.Notebook(main);notebook.pack(fill="both",expand=True)
trees={};tabs={}
for s in SECTIONS:
    tab=ttk.Frame(notebook,padding=8);tabs[s]=tab
    notebook.add(tab,text=NOMES_ABAS.get(s,s))
    t=ttk.Treeview(tab,columns=("key","translation","value"),show="headings",selectmode="browse")
    t.heading("key",text="Nome original");t.heading("translation",text="Tradução em português");t.heading("value",text="Valor")
    t.column("key",width=250);t.column("translation",width=450);t.column("value",width=100)
    bar=ttk.Scrollbar(tab,orient="vertical",command=t.yview)
    t.configure(yscrollcommand=bar.set)
    bar.pack(side="right",fill="y");t.pack(fill="both",expand=True)
    t.bind("<Double-1>",lambda ev,s=s:change(s))
    trees[s]=t
    row=ttk.Frame(tab);row.pack(fill="x",pady=5)
    ttk.Button(row,text="✏️ Editar valor",command=lambda s=s:change(s)).pack(side="left",padx=3)
    ttk.Button(row,text="＋ Adicionar configuração",command=lambda s=s:add(s)).pack(side="left",padx=3)
    ttk.Button(row,text="− Remover configuração",command=lambda s=s:remove(s)).pack(side="left",padx=3)
ttk.Label(main,text="As opções são lidas do arquivo do mundo escolhido. O botão Internet atualiza traduções, não instala atualizações do jogo ou do programa. Arquivos antigos podem não conter todas as opções novas. Traduções apenas na tela. Ao salvar, os nomes originais são preservados. Opções desconhecidas podem exigir consulta à documentação do jogo.",wraplength=950).pack(anchor="w",pady=(8,5))
ttk.Button(main,text="💾 SALVAR ALTERAÇÕES E CRIAR BACKUP",command=save).pack(fill="x",ipady=7)
ttk.Label(main,textvariable=notice).pack(anchor="w",pady=(6,0))
app.after(350, auto_find)
app.mainloop()
