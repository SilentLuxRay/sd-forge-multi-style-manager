import os
import csv
import gradio as gr
from modules import scripts, script_callbacks

EXTENSION_DIR = scripts.basedir()
STYLES_DIR = os.path.join(EXTENSION_DIR, "styles")

def get_style_files():
    if not os.path.exists(STYLES_DIR): os.makedirs(STYLES_DIR)
    files = [f for f in os.listdir(STYLES_DIR) if f.endswith('.csv')]
    return files if files else []

def load_styles(filename):
    if not filename or filename == "Nessun file trovato": return []
    path = os.path.join(STYLES_DIR, filename)
    styles = []
    if not os.path.exists(path): return []
    try:
        with open(path, mode='r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.reader(f, quotechar='"', skipinitialspace=True)
            for row in reader:
                if len(row) >= 2:
                    name, p = row[0].strip(), row[1].strip()
                    if name.lower() in ["name", "style name"]: continue
                    n = row[2].strip() if len(row) > 2 else ""
                    styles.append([name, p, n])
    except Exception as e: print(f"Errore caricamento: {e}")
    return styles

def save_style(filename, name, prompt, neg):
    if not filename or not name: return "Errore: Nome o File mancante"
    path = os.path.join(STYLES_DIR, filename)
    data = load_styles(filename)
    
    updated = False
    new_data = []
    # Se il nome esiste già, aggiornalo, altrimenti tienilo
    for row in data:
        if row[0].lower() == name.lower():
            new_data.append([name, prompt, neg])
            updated = True
        else:
            new_data.append(row)
    
    # Se non è stato aggiornato, aggiungilo come nuovo
    if not updated:
        new_data.append([name, prompt, neg])

    try:
        with open(path, mode='w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(["name", "prompt", "negative_prompt"]) # Header
            writer.writerows(new_data)
        return f"Stile '{name}' salvato con successo in {filename}!"
    except Exception as e:
        return f"Errore durante il salvataggio: {e}"

def on_ui_tabs():
    files = get_style_files()
    default_f = files[0] if files else ""
    data = load_styles(default_f)
    names = [s[0] for s in data] if data else []

    with gr.Blocks(analytics_enabled=False) as ui:
        with gr.Row():
            # COLONNA SINISTRA: SELEZIONE E FILTRI
            with gr.Column(scale=1):
                gr.Markdown("### 🗂️ Gestione Stili")
                file_drop = gr.Dropdown(choices=files, label="File CSV", value=default_f)
                search = gr.Textbox(label="🔍 Cerca...", placeholder="Filtra stili...")
                style_drop = gr.Dropdown(choices=names, label="✨ Seleziona lo Stile", value=names[0] if names else None)
                mode = gr.Radio(choices=["Sostituisci", "Aggiungi"], value="Sostituisci", label="Modalità Invio")
                refresh = gr.Button("🔄 Aggiorna Lista File")
            
            # COLONNA CENTRALE: ANTEPRIMA E INVIO
            with gr.Column(scale=2):
                gr.Markdown("### 🚀 Anteprima e Invio")
                prev_p = gr.Textbox(label="Prompt", lines=6, interactive=True)
                prev_n = gr.Textbox(label="Negative Prompt", lines=3, interactive=True)
                with gr.Row():
                    btn_t2i = gr.Button("Invia a T2I 🚀", variant="primary")
                    btn_i2i = gr.Button("Invia a I2I 🖼️")
            
            # COLONNA DESTRA: EDITOR (SALVATAGGIO/MODIFICA)
            with gr.Column(scale=1):
                gr.Markdown("### 💾 Salva o Modifica")
                edit_name = gr.Textbox(label="Nome Stile", placeholder="Es: Mio Stile Cinematico")
                save_btn = gr.Button("💾 Salva Stile nel CSV", variant="secondary")
                status_msg = gr.Label(value="")
                gr.Markdown("*(Se il nome esiste già nel file, verrà sovrascritto)*")

        # --- LOGICA ---

        def filter_st(f, q):
            all_d = load_styles(f)
            filt = [r for r in all_d if q.lower() in r[0].lower()]
            if not filt: return gr.update(choices=[], value=None), "", "", ""
            return gr.update(choices=[r[0] for r in filt], value=filt[0][0]), filt[0][1], filt[0][2], filt[0][0]

        def upd_pr(f, n):
            all_d = load_styles(f)
            for r in all_d:
                if r[0] == n: return r[1], r[2], r[0]
            return "", "", ""

        def handle_save(f, n, p, neg):
            msg = save_style(f, n, p, neg)
            # Dopo il salvataggio, aggiorniamo la lista degli stili
            new_styles = load_styles(f)
            new_names = [s[0] for s in new_styles]
            return msg, gr.update(choices=new_names, value=n)

        # Eventi selezione
        file_drop.change(filter_st, [file_drop, search], [style_drop, prev_p, prev_n, edit_name])
        search.change(filter_st, [file_drop, search], [style_drop, prev_p, prev_n, edit_name])
        style_drop.change(upd_pr, [file_drop, style_drop], [prev_p, prev_n, edit_name])
        
        # Evento Salvataggio
        save_btn.click(handle_save, [file_drop, edit_name, prev_p, prev_n], [status_msg, style_drop])
        
        refresh.click(lambda: gr.update(choices=get_style_files()), outputs=[file_drop])

        # Chiamata JS (per compatibilità Physton)
        btn_t2i.click(None, [prev_p, prev_n, mode], _js="window.movePrompt(p, n, 'txt2img', m)")
        btn_i2i.click(None, [prev_p, prev_n, mode], _js="window.movePrompt(p, n, 'img2img', m)")

    return [(ui, "Style Manager", "style_manager")]

script_callbacks.on_ui_tabs(on_ui_tabs)