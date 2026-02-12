class IntentgineCommandCard extends HTMLElement {
  setConfig(config) {
    if (!this.content) {
      this.innerHTML = `
        <ha-card>
          <div class="card-content">
            <h2>${config.title || 'Intentgine Command'}</h2>
            <div class="input-container">
              <input type="text" id="command-input" placeholder="${config.placeholder || 'Enter command...'}" />
              <button id="run-button">Run</button>
            </div>
            <div id="result" class="result"></div>
            ${config.show_history ? '<div id="history" class="history"></div>' : ''}
          </div>
        </ha-card>
        <style>
          .card-content { padding: 16px; }
          .input-container { display: flex; gap: 8px; margin: 16px 0; }
          #command-input { flex: 1; padding: 8px; border: 1px solid var(--divider-color); border-radius: 4px; }
          #run-button { padding: 8px 16px; background: var(--primary-color); color: white; border: none; border-radius: 4px; cursor: pointer; }
          #run-button:hover { opacity: 0.9; }
          #run-button:disabled { opacity: 0.5; cursor: not-allowed; }
          .result { padding: 8px; margin: 8px 0; border-radius: 4px; }
          .result.success { background: #4caf50; color: white; }
          .result.error { background: #f44336; color: white; }
          .result.loading { background: var(--primary-color); color: white; }
          .history { margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--divider-color); }
          .history-item { padding: 4px 0; font-size: 0.9em; color: var(--secondary-text-color); }
        </style>
      `;
      
      this.content = true;
      this._config = config;
      this._history = [];
      
      const input = this.querySelector('#command-input');
      const button = this.querySelector('#run-button');
      const result = this.querySelector('#result');
      
      const executeCommand = async () => {
        const query = input.value.trim();
        if (!query) return;
        
        button.disabled = true;
        result.className = 'result loading';
        result.textContent = 'Processing...';
        
        try {
          const response = await this._hass.callService('intentgine', 'execute_command', { query });
          
          if (response && response.success !== false) {
            result.className = 'result success';
            result.textContent = '✓ Command executed successfully';
            this._addToHistory(query, true);
          } else {
            result.className = 'result error';
            result.textContent = `✗ ${response?.error || 'Command failed'}`;
            this._addToHistory(query, false);
          }
        } catch (err) {
          result.className = 'result error';
          result.textContent = `✗ Error: ${err.message}`;
          this._addToHistory(query, false);
        }
        
        button.disabled = false;
        input.value = '';
      };
      
      button.addEventListener('click', executeCommand);
      input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') executeCommand();
      });
    }
  }
  
  _addToHistory(query, success) {
    if (!this._config.show_history) return;
    
    this._history.unshift({ query, success, time: new Date() });
    if (this._history.length > 5) this._history.pop();
    
    const historyEl = this.querySelector('#history');
    if (historyEl) {
      historyEl.innerHTML = '<h3>Recent Commands</h3>' + 
        this._history.map(h => 
          `<div class="history-item">${h.success ? '✓' : '✗'} ${h.query}</div>`
        ).join('');
    }
  }
  
  set hass(hass) {
    this._hass = hass;
  }
  
  getCardSize() {
    return 3;
  }
}

customElements.define('intentgine-command-card', IntentgineCommandCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'intentgine-command-card',
  name: 'Intentgine Command Card',
  description: 'Execute natural language commands via Intentgine'
});
