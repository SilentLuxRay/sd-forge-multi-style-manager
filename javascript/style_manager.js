window.movePrompt = function(newP, newN, target, mode) {
    console.log("Style Manager: Invio dati a " + target + " con modalità " + mode);

    const prompt_el = document.querySelector(`#${target}_prompt textarea`);
    const neg_el = document.querySelector(`#${target}_neg_prompt textarea`);

    if (!prompt_el || !neg_el) {
        console.error("Style Manager: Campi non trovati!");
        return;
    }

    const isAppend = mode.toLowerCase().includes("aggiungi");

    // Funzione interna per aggiornare il testo
    const updateText = (el, newText) => {
        if (!newText) return;
        
        let finalValue = newText.trim();
        if (isAppend && el.value.trim().length > 0) {
            finalValue = el.value.trim() + ", " + newText.trim();
        }

        // Metodo standard per cambiare il valore
        el.value = finalValue;

        // Scateniamo l'evento 'input' che è quello che Physton ascolta
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