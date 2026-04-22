requireAuth()

const EMOTION_EMOJIS = {
    joy: '😄', sadness: '😢', anger: '😠',
    fear: '😨', love: '❤️', surprise: '😲', neutral: '😐'
};

const EMOTION_COLORS = {
    joy: '#f59e0b', sadness: '#3b82f6', anger: '#ef4444',
    fear: '#8b5cf6', love: '#ec4899', surprise: '#10b981', neutral: '#6b7280'
};

async function loadEmotionResult() {
    const params = new URLSearchParams(window.location.search);
    const entryId = params.get('entry_id');

    if (!entryId) {
        window.location.href = 'dashboard.html';
        return;
    }

    // Get emotion analysis
    const analysisRes = await api.get(`/nlp/analysis/${entryId}/`);
    if (!analysisRes || analysisRes.status !== 200) {
        // Not analyzed yet — analyze now
        const analyzeRes = await api.post(`/nlp/analyze/${entryId}/`, {});
        if (analyzeRes && analyzeRes.status === 200) {
            displayAnalysis(analyzeRes.data.analysis);
        }
    } else {
        displayAnalysis(analysisRes.data);
    }

    // Get recommendations
    const recRes = await api.get(`/recommendations/entries/${entryId}/`);
    if (recRes && recRes.status === 200) {
        displayRecommendations(recRes.data.recommendations, recRes.data.is_crisis);
    }
}

function displayAnalysis(analysis) {
    const emotion = analysis.dominant_emotion;
    const confidence = Math.round(analysis.confidence_score * 100);

    // Update emotion circle
    document.getElementById('emotion-emoji').textContent = EMOTION_EMOJIS[emotion] || '🧠';
    document.getElementById('emotion-label').textContent = emotion;
    document.getElementById('confidence-score').textContent = `${confidence}%`;

    // Update emotion circle color
    const circle = document.querySelector('.emotion-circle');
    if (circle) {
        const color = EMOTION_COLORS[emotion] || '#667eea';
        circle.style.background = `linear-gradient(135deg, ${color}, ${color}aa)`;
    }

    // Show crisis banner
    if (analysis.is_crisis) {
        document.getElementById('crisis-banner').classList.remove('hidden');
    }

    // Emotion bars
    const bars = document.getElementById('emotion-bars');
    const scores = {
        joy: analysis.joy_score,
        sadness: analysis.sadness_score,
        anger: analysis.anger_score,
        fear: analysis.fear_score,
        love: analysis.love_score,
        surprise: analysis.surprise_score
    };

    bars.innerHTML = Object.entries(scores).map(([emotion, score]) => {
        const pct = Math.round(score * 100);
        const color = EMOTION_COLORS[emotion];
        return `
            <div class="mb-3">
                <div class="flex justify-between text-sm mb-1">
                    <span class="capitalize text-gray-600">${EMOTION_EMOJIS[emotion]} ${emotion}</span>
                    <span class="font-semibold text-gray-800">${pct}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width:${pct}%; background:${color}"></div>
                </div>
            </div>`;
    }).join('');
}

function displayRecommendations(recommendations, isCrisis) {
    const container = document.getElementById('recommendations-container');
    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = '<p class="text-gray-400 text-center py-4">No recommendations available.</p>';
        return;
    }

    container.innerHTML = recommendations.map(rec => `
        <div class="rec-card mb-4 ${rec.is_crisis_recommendation ? 'border-red-200 bg-red-50' : ''}">
            <div class="flex items-start gap-3">
                <span class="text-2xl">${getCategoryEmoji(rec.category)}</span>
                <div class="flex-1">
                    <h4 class="font-semibold text-gray-800 mb-1">${rec.title}</h4>
                    <p class="text-gray-600 text-sm mb-3">${rec.description}</p>
                    <div class="bg-gray-50 rounded-lg p-3">
                        <p class="text-sm font-medium text-gray-700 mb-2">Action Steps:</p>
                        <p class="text-sm text-gray-600 whitespace-pre-line">${rec.action_steps}</p>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function getCategoryEmoji(category) {
    const emojis = {
        breathing: '🫁', motivation: '💪', calming: '🧘',
        gratitude: '🙏', physical: '🏃', social: '👥', professional: '🏥'
    };
    return emojis[category] || '💡';
}

loadEmotionResult();