document.addEventListener('DOMContentLoaded', () => {
    // Éléments du DOM
    const step1 = document.getElementById('step1-analyze');
    const step2 = document.getElementById('step2-context');
    const step3 = document.getElementById('step3-result');
    const loader = document.getElementById('loader');

    const analyzeBtn = document.getElementById('analyze-btn');
    const generateBtn = document.getElementById('generate-btn');
    const copyBtn = document.getElementById('copy-btn');
    const restartBtn = document.getElementById('restart-btn');

    // Pour stocker l'analyse entre les étapes
    let analysisData = {};

    // Événement au clic sur "Analyser"
    analyzeBtn.addEventListener('click', async () => {
        const userMessage = document.getElementById('user-message').value;
        if (userMessage.trim() === '') {
            alert('Veuillez coller un message à analyser.');
            return;
        }

        step1.classList.add('hidden');
        loader.classList.remove('hidden');

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMessage })
            });

            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }

            analysisData = await response.json();
            
            document.getElementById('analysis-result').innerText = `Intention: ${analysisData.intent.replace('_', ' ')} | Sentiment: ${analysisData.sentiment}`;

            loader.classList.add('hidden');
            step2.classList.remove('hidden');

        } catch (error) {
            console.error("Erreur lors de l'analyse:", error);
            alert("Une erreur est survenue. Vérifiez la console pour plus de détails.");
            loader.classList.add('hidden');
            step1.classList.remove('hidden');
        }
    });

    // Événement au clic sur "Générer"
    generateBtn.addEventListener('click', async () => {
        const details = document.getElementById('reply-details').value;
        const tone = document.getElementById('tone-select').value;
        const channel = document.getElementById('channel-select').value;

        step2.classList.add('hidden');
        loader.innerHTML = '<div class="spinner"></div><p>Rédaction en cours...</p>';
        loader.classList.remove('hidden');

        const payload = {
            ...analysisData,
            details,
            tone,
            channel
        };

        try {
            const response = await fetch('/generate_reply', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }

            const result = await response.json();
            document.getElementById('final-reply').value = result.reply;

            loader.classList.add('hidden');
            step3.classList.remove('hidden');

        } catch (error) {
            console.error("Erreur lors de la génération:", error);
            alert("Une erreur est survenue. Vérifiez la console pour plus de détails.");
            loader.classList.add('hidden');
            step2.classList.remove('hidden');
        }
    });

    // Événement pour copier le texte
    copyBtn.addEventListener('click', () => {
        const finalReply = document.getElementById('final-reply');
        finalReply.select();
        document.execCommand('copy');
        copyBtn.innerText = "Copié !";
        setTimeout(() => { copyBtn.innerText = "Copier le texte"; }, 2000);
    });

    // Événement pour recommencer
    restartBtn.addEventListener('click', () => {
        location.reload();
    });
});