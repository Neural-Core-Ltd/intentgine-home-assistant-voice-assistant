class IntentgineChatCard extends HTMLElement {
  setConfig(config) {
    if (!this.content) {
      this.innerHTML = `
        <ha-card>
          <div class="card-content">
            <h2>${config.title || 'Home Assistant Chat'}</h2>
            <div id="messages" class="messages"></div>
            <div class="input-container">
              <input type="text" id="chat-input" placeholder="Type a command..." />
              <button id="send-button">Send</button>
            </div>
          </div>
        </ha-card>
        <style>
          .card-content { padding: 16px; display: flex; flex-direction: column; height: 400px; }
          .messages { flex: 1; overflow-y: auto; margin: 16px 0; }
          .message { margin: 8px 0; padding: 8px 12px; border-radius: 8px; max-width: 80%; }
          .message.user { background: var(--primary-color); color: white; margin-left: auto; }
          .message.assistant { background: var(--card-background-color); border: 1px solid var(--divider-color); }
          .message.action { background: #4caf50; color: white; font-size: 0.9em; margin-left: auto; }
          .input-container { display: flex; gap: 8px; }
          #chat-input { flex: 1; padding: 8px; border: 1px solid var(--divider-color); border-radius: 4px; }
          #send-button { padding: 8px 16px; background: var(--primary-color); color: white; border: none; border-radius: 4px; cursor: pointer; }
          #send-button:disabled { opacity: 0.5; cursor: not-allowed; }
        </style>
      `;
      
      this.content = true;
      this._config = config;
      
      const input = this.querySelector('#chat-input');
      const button = this.querySelector('#send-button');
      const messages = this.querySelector('#messages');
      
      const sendMessage = async () => {
        const query = input.value.trim();
        if (!query) return;
        
        this._addMessage('user', query);
        input.value = '';
        button.disabled = true;
        
        try {
          await this._hass.callService('intentgine', 'execute_command', { query });
          this._addMessage('action', `✓ Command executed`);
        } catch (err) {
          this._addMessage('assistant', `Error: ${err.message}`);
        }
        
        button.disabled = false;
      };
      
      button.addEventListener('click', sendMessage);
      input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
      });
    }
  }
  
  _addMessage(type, text) {
    const messages = this.querySelector('#messages');
    const msg = document.createElement('div');
    msg.className = `message ${type}`;
    msg.textContent = text;
    messages.appendChild(msg);
    messages.scrollTop = messages.scrollHeight;
  }
  
  set hass(hass) {
    this._hass = hass;
  }
  
  getCardSize() {
    return 6;
  }
}

customElements.define('intentgine-chat-card', IntentgineChatCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'intentgine-chat-card',
  name: 'Intentgine Chat Card',
  description: 'Conversational interface for home control'
});
