const API_BASE = '/api/v1';
const userId = 1;

async function sendChatMessage(message, language = 'english') {
  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, user_id: userId, language })
    });
    return await response.json();
  } catch (error) {
    console.error('Chat API error:', error);
    return { response: 'Sorry, I am having trouble connecting. Please try again.' };
  }
}

async function loadUserData() {
  try {
    const [income, stress, emergency, spending, recommendations] = await Promise.all([
      fetch(`${API_BASE}/analysis/income/${userId}`).then(r => r.json()),
      fetch(`${API_BASE}/analysis/stress/${userId}`).then(r => r.json()),
      fetch(`${API_BASE}/analysis/emergency/${userId}`).then(r => r.json()),
      fetch(`${API_BASE}/analysis/spending/${userId}`).then(r => r.json()),
      fetch(`${API_BASE}/recommendations/${userId}`).then(r => r.json())
    ]);
    
    console.log('📊 Financial Data Loaded:', { income, stress, emergency, spending, recommendations });
    
    // Display income analysis
    if (income) {
      const incomeCard = document.querySelector('.insight-card:nth-child(1) .insight-value');
      if (incomeCard) incomeCard.textContent = `${income.stability_score}/100`;
      const incomeDesc = document.querySelector('.insight-card:nth-child(1) .insight-desc');
      if (incomeDesc) incomeDesc.textContent = `Strategy: ${income.recommended_sip_strategy}`;
    }
    
    // Display stress score
    if (stress) {
      const stressCard = document.querySelector('.insight-card:nth-child(2) .insight-value');
      if (stressCard) {
        stressCard.textContent = `${stress.score}/100`;
        const riskColor = stress.risk_level === 'LOW' ? '#10b981' : stress.risk_level === 'MEDIUM' ? '#f59e0b' : '#ef4444';
        stressCard.style.color = riskColor;
      }
      const stressDesc = document.querySelector('.insight-card:nth-child(2) .insight-desc');
      if (stressDesc) stressDesc.textContent = `Risk: ${stress.risk_level}`;
    }
    
    // Display emergency fund
    if (emergency && emergency.emergency_status) {
      const emergencyCard = document.querySelector('.insight-card:nth-child(3) .insight-value');
      if (emergencyCard) {
        const status = emergency.emergency_status.adequate ? '✅ Adequate' : '⚠️ Build Fund';
        emergencyCard.textContent = status;
        emergencyCard.style.fontSize = '18px';
      }
      const emergencyDesc = document.querySelector('.insight-card:nth-child(3) .insight-desc');
      if (emergencyDesc) {
        const months = emergency.emergency_status.months_covered || 0;
        emergencyDesc.textContent = `${months.toFixed(1)} months covered`;
      }
    }
    
    // Display spending analysis
    if (spending && spending.spending_analysis) {
      const spendCard = document.querySelector('.insight-card:nth-child(4) .insight-value');
      if (spendCard) {
        const totalSpend = Object.values(spending.spending_analysis).reduce((a, b) => a + (typeof b === 'number' ? b : 0), 0);
        spendCard.textContent = `₹${totalSpend.toLocaleString('en-IN')}`;
      }
      const spendDesc = document.querySelector('.insight-card:nth-child(4) .insight-desc');
      if (spendDesc && spending.savings_opportunities && spending.savings_opportunities.length > 0) {
        spendDesc.textContent = `${spending.savings_opportunities.length} savings opportunities`;
      }
    }
    
    return { income, stress, emergency, spending, recommendations };
  } catch (error) {
    console.error('❌ Load error:', error);
  }
}

loadUserData();
