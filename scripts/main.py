import os
import csv
import gradio as gr
from modules import scripts, script_callbacks

EXTENSION_DIR = scripts.basedir()
STYLES_DIR = os.path.join(EXTENSION_DIR, "styles")

def get_style_files():
    if not os.path.exists(STYLES_DIR): 
        os.makedirs(STYLES_DIR)
    files = [f for f in os.listdir(STYLES_DIR) if f.endswith('.csv')]
    return files if len(files) > 0 else []

def load_styles(filename):
    if not filename or filename == "Nessun file trovato":
        return []
    path = os.path.join(STYLES_DIR, filename)
    if not os.path.exists(path):
        return []
    styles = []
    try:
        with open(path, mode='r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.reader(f, quotechar='"', skipinitialspace=True)
            for row in reader:
                if len(row) >= 2:
                    name = row[0].strip()
                    if name.lower() in ["name", "style name", ""]: continue
                    prompt = row[1].strip()
                    neg = row[2].strip() if len(row) > 2 else ""
                    styles.append([name, prompt, neg])
    except Exception as e:
        print(f"[Style Manager] Errore critico: {e}")
    return styles

def on_ui_tabs():
    files = get_style_files()
    
    # Se non ci sono file, creiamo una situazione di fallback sicura
    if not files:
        default_f = "Nessun file trovato"
        initial_data = [["Esempio", "Prompt di esempio", "Negative di esempio"]]
        initial_names = ["Esempio"]
    else:
        default_f = files[0]
        initial_data = load_styles(default_f)
        if not initial_data:
            initial_data = [["Vuoto", "", ""]]
        initial_names = [s[0] for s in initial_data]

    with gr.Blocks(analytics_enabled=False) as ui:
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🗂️ Gestione")
                file_drop = gr.Dropdown(choices=files if files else ["Nessun file trovato"], label="File CSV", value=default_f)
                search = gr.Textbox(label="🔍 Cerca...", placeholder="Filtra...")
                style_drop = gr.Dropdown(choices=initial_names, label="✨ Stile", value=initial_names[0] if initial_names else None)
                mode = gr.Radio(choices=["Sostituisci", "Aggiungi"], value="Sostituisci", label="Metodo")
                refresh = gr.Button("🔄 Aggiorna")
            
            with gr.Column(scale=2):
                gr.Markdown("### 🚀 Anteprima")
                prev_p = gr.Textbox(label="Prompt", lines=6, value=initial_data[0][1] if initial_data else "")
                prev_n = gr.Textbox(label="Negative", lines=3, value=initial_data[0][2] if initial_data else "")
                with gr.Row():
                    btn_t2i = gr.Button("Invia a T2I", variant="primary")
                    btn_i2i = gr.Button("Invia a I2I")
            
            with gr.Column(scale=1):
                gr.Markdown("### 💾 Editor")
                edit_name = gr.Textbox(label="Nome Stile", value=initial_names[0] if initial_names else "")
                save_btn = gr.Button("💾 Salva/Modifica", variant="secondary")
                status = gr.Markdown("")

        # Logica
        def filter_fn(f, q):
            data = load_styles(f)
            filt = [r for r in data if q.lower() in r[0].lower()]
            if not filt: return gr.update(choices=[], value=None), "", "", ""
            return gr.update(choices=[r[0] for r in filt], value=filt[0][0]), filt[0][1], filt[0][2], filt[0][0]

        def update_fn(f, n):
            data = load_styles(f)
            for r in data:
                if r[0] == n: return r[1], r[2], r[0]
            return "", "", ""

        def save_fn(f, n, p, neg):
            if f == "Nessun file trovato" or not n: return "Errore nome/file", gr.update()
            path = os.path.join(STYLES_DIR, f)
            data = load_styles(f)
            new_data = []
            found = False
            for r in data:
                if r[0].lower() == n.lower():
                    new_data.append([n, p, neg])
                    found = True
                else: new_data.append(r)
            if not found: new_data.append([n, p, neg])
            
            with open(path, mode='w', encoding='utf-8-sig', newline='') as file:
                writer = csv.writer(file, quotechar='"', quoting=csv.QUOTE_ALL)
                writer.writerow(["name", "prompt", "negative_prompt"])
                writer.writerows(new_data)
            
            updated_names = [r[0] for r in new_data]
            return f"✅ '{n}' salvato!", gr.update(choices=updated_names, value=n)

        file_drop.change(filter_fn, [file_drop, search], [style_drop, prev_p, prev_n, edit_name])
        search.change(filter_fn, [file_drop, search], [style_drop, prev_p, prev_n, edit_name])
        style_drop.change(update_fn, [file_drop, style_drop], [prev_p, prev_n, edit_name])
        save_btn.click(save_fn, [file_drop, edit_name, prev_p, prev_n], [status, style_drop])
        refresh.click(lambda: gr.update(choices=get_style_files()), outputs=[file_drop])

        btn_t2i.click(None, [prev_p, prev_n, mode], _js="(p, n, m) => { window.movePrompt(p, n, 'txt2img', m) }")
        btn_i2i.click(None, [prev_p, prev_n, mode], _js="(p, n, m) => { window.movePrompt(p, n, 'img2img', m) }")

    return [(ui, "Style Manager", "style_manager")]

script_callbacks.on_ui_tabs(on_ui_tabs)