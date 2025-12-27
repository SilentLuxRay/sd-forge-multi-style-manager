window.movePrompt = function(newP, newN, target, mode) {
    console.log("Style Manager: Invio dati a " + target + " con modalità " + mode);

    const prompt_el = document.querySelector(`#${target}_prompt textarea`);
    const neg_el = document.querySelector(`#${target}_neg_prompt textarea`);

    if (!prompt_el || !neg_el) {
        console.error("Style Manager: Campi non trovati!");
        return;
    }

    const isAppend = mode.toLowerCase().includes("aggiungi");

    const updateText = (el, styleText) => {
        if (!styleText) return;
        
        let currentText = el.value.trim();
        let style = styleText.trim();
        let finalValue = "";

        if (isAppend && currentText.length > 0) {
            // Controlla se lo stile contiene il tag {prompt}
            if (style.includes("{prompt}")) {
                // Sostituisce tutte le occorrenze di {prompt} con il testo attuale
                finalValue = style.replaceAll("{prompt}", currentText);
            } else {
                // Se non c'è il tag, aggiunge semplicemente in coda con una virgola
                finalValue = currentText + ", " + style;
            }
        } else {
            // Modalità Sostituisci (o casella vuota): 
            // Rimuoviamo il tag {prompt} se presente per pulizia, 
            // dato che non c'è un prompt precedente da inserire.
            finalValue = style.replaceAll("{prompt}", "");
        }

        // Pulizia virgole doppie che potrebbero crearsi
        finalValue = finalValue.replace(/,\s*,/g, ',').replace(/^,\s*/, '').trim();

        el.value = finalValue;

        // Notifica a Forge/Physton del cambiamento
        const event = new Event('input', { bubbles: true });
        el.dispatchEvent(event);
    };

    updateText(prompt_el, newP);
    updateText(neg_el, newN);

    // Cambia Tab
    const buttons = document.querySelectorAll('#tabs button');
    for (let btn of buttons) {
        if (btn.innerText.trim().toLowerCase() === target.toLowerCase()) {
            btn.click();
            break;
        }
    }
};