(function () {
  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    const root = document.getElementById('cb-root');
    const toggle = document.getElementById('cb-toggle');    // FAB 💬
    if (!root || !toggle) return;

    const minimizeBtn = root.querySelector('.cb-minimize');
    const messages = document.getElementById('cb-messages');
    const input = document.getElementById('cb-input');
    const send = document.getElementById('cb-send');
    const quickWrap = document.getElementById('cb-quick');

    const STORAGE_KEY = 'cb_state'; // 'open' | 'min' | 'hidden'

    function setState(state){
      root.classList.remove('cb-hidden', 'cb-min');
      if (state === 'open'){
        // Caja visible; el FAB se oculta por CSS
      } else if (state === 'min'){
        // Minimiza (oculta la caja, deja visible el FAB)
        root.classList.add('cb-min');
      } else {
        // Oculto (igual que min, pero semánticamente cerrado)
        root.classList.add('cb-hidden');
        root.classList.add('cb-min');
      }
      localStorage.setItem(STORAGE_KEY, state);
    }
    function getState(){ return localStorage.getItem(STORAGE_KEY) || 'hidden'; }

    // Estado inicial
    setState(getState());

    function scrollBottom(){ messages.scrollTop = messages.scrollHeight; }

    function bubble(text, who){
      const row = document.createElement('div');
      row.className = `cb-msg ${who === 'bot' ? 'cb-bot' : 'cb-user'}`;
      const b = document.createElement('div');
      b.className = 'cb-bubble';
      b.textContent = text;
      row.appendChild(b);
      messages.appendChild(row);
      scrollBottom();
    }

    function renderQuick(list){
      quickWrap.innerHTML = '';
      (list || []).forEach((q) => {
        const chip = document.createElement('button');
        chip.className = 'cb-chip';
        chip.type = 'button';
        chip.textContent = q;
        chip.addEventListener('click', (e) => {
          e.preventDefault();
          input.value = q;
          sendMessage();
        });
        quickWrap.appendChild(chip);
      });
    }

    async function askAPI(message){
      const res = await fetch('/chatbot/ask/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });
      if (!res.ok) throw new Error('Network/Server error');
      return res.json();
    }

    async function sendMessage(e){
      if (e && e.preventDefault) e.preventDefault();
      const text = (input.value || '').trim();
      if (!text) return;
      bubble(text, 'user');
      input.value = '';
      try {
        const data = await askAPI(text);
        bubble(data.reply, 'bot');
        renderQuick(data.quick);
      } catch (err){
        console.error(err);
        bubble('Lo siento, hubo un problema al responder. Intenta nuevamente.', 'bot');
      }
    }

    // FAB abre el chat completo
    toggle.addEventListener('click', (e) => { e.preventDefault(); setState('open'); });

    // Minimizar (–) -> solo FAB visible
    if (minimizeBtn){
      minimizeBtn.addEventListener('click', (e) => { e.preventDefault(); setState('min'); });
    }

    // Enviar
    if (send) send.addEventListener('click', sendMessage);
    if (input){
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter'){ e.preventDefault(); sendMessage(e); }
      });
    }

    // Chips iniciales
    renderQuick([
      "¿tienes algun contacto de venta?",
      "¿como puedo cancelar mi pedido?",
      "informacion de envio",
      "¿poseen correo?",
      "¿donde encuentro informacion del producto?",
      "olvide mi contraseña."
    ]);
  });
})();
