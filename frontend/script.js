document.addEventListener('DOMContentLoaded', () => {
    const totalReviewsEl = document.getElementById('totalReviews');
    const executionTimeEl = document.getElementById('executionTime');
    const gameCountEl = document.getElementById('gameCount');
    const gamesBody = document.getElementById('gamesBody');
    const gameSearch = document.getElementById('gameSearch');
    const wordCloudEl = document.getElementById('wordCloud');
    const loader = document.getElementById('loader');
    const reanalyzeBtn = document.getElementById('reanalyzeBtn');

    let allGames = [];
    let sentimentChart = null;
    let currentSort = { key: 'ratio', order: 'desc' };

    // API Verilerini Çek
    // Theme Toggle Logic
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');

    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('light-theme');
        const isLight = document.body.classList.contains('light-theme');
        themeIcon.textContent = isLight ? '☀️' : '🌙';
        themeText.textContent = isLight ? 'Aydınlık Mod' : 'Karanlık Mod';
        
        // Update Chart Colors if light mode
        if (sentimentChart) {
            sentimentChart.options.plugins.legend.labels.color = isLight ? '#64748b' : '#94a3b8';
            sentimentChart.update();
        }
    });

    async function fetchData(isNewAnalysis = false) {
        loader.classList.remove('hidden');
        try {
            const endpoint = isNewAnalysis ? '/api/analyze' : '/api/results';
            const response = await fetch(endpoint);
            const data = await response.json();

            if (data.error) {
                if (!isNewAnalysis) {
                    return fetchData(true);
                }
                alert("Hata: " + data.error);
                return;
            }

            renderDashboard(data);
        } catch (err) {
            console.error("Fetch hatası:", err);
        } finally {
            loader.classList.add('hidden');
        }
    }

    function renderDashboard(data) {
        totalReviewsEl.textContent = data.stats.total_reviews.toLocaleString();
        executionTimeEl.textContent = data.stats.execution_time + 's';
        gameCountEl.textContent = data.stats.game_count;

        renderChart(data.stats.total_pos, data.stats.total_neg);
        renderWordCloud(data.global_word_cloud);

        allGames = data.games;
        renderTable(allGames);
    }

    function renderChart(pos, neg) {
        const ctx = document.getElementById('sentimentChart').getContext('2d');
        const isLight = document.body.classList.contains('light-theme');
        
        if (sentimentChart) {
            sentimentChart.destroy();
        }

        sentimentChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Olumlu', 'Olumsuz'],
                datasets: [{
                    data: [pos, neg],
                    backgroundColor: ['#10b981', '#ef4444'],
                    borderColor: isLight ? '#f8fafc' : '#0b0e14',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { 
                            color: isLight ? '#64748b' : '#94a3b8', 
                            font: { family: 'Inter' } 
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }

    function renderWordCloud(words) {
        wordCloudEl.innerHTML = '';
        // Gösterilen kelime sayısını artırdık
        words.slice(0, 50).forEach(item => {
            const span = document.createElement('span');
            span.className = 'word-item';
            span.textContent = item.text;
            
            const fontSize = Math.max(0.8, Math.min(2.2, (item.value / words[0].value) * 3));
            span.style.fontSize = fontSize + 'rem';
            span.style.opacity = Math.max(0.4, item.value / words[0].value);
            
            wordCloudEl.appendChild(span);
        });
    }

    function renderTable(games) {
        gamesBody.innerHTML = '';
        games.forEach(game => {
            const row = document.createElement('tr');
            
            let ratioClass = 'ratio-mid';
            if (game.ratio >= 90) ratioClass = 'ratio-high';
            else if (game.ratio < 70) ratioClass = 'ratio-low';

            // Top words sayısını artırdık (20'ye kadar)
            const tags = Object.keys(game.top_words).slice(0, 20).map(word => 
                `<span class="mini-tag">${word}</span>`
            ).join('');

            row.innerHTML = `
                <td><strong>${game.name}</strong></td>
                <td style="color: #10b981">${game.pos}</td>
                <td style="color: #ef4444">${game.neg}</td>
                <td><span class="ratio-badge ${ratioClass}">${game.ratio}%</span></td>
                <td><div class="tag-list" style="max-width: 400px">${tags}</div></td>
            `;
            gamesBody.appendChild(row);
        });
    }

    // Sıralama İşlemi
    document.querySelectorAll('th[data-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const key = th.getAttribute('data-sort');
            currentSort.order = (currentSort.key === key && currentSort.order === 'desc') ? 'asc' : 'desc';
            currentSort.key = key;

            // Sort icons update
            document.querySelectorAll('.sort-icon').forEach(icon => icon.textContent = '↕');
            th.querySelector('.sort-icon').textContent = currentSort.order === 'desc' ? '↓' : '↑';

            const sortedGames = [...allGames].sort((a, b) => {
                let valA = a[key];
                let valB = b[key];
                if (key === 'name') {
                    return currentSort.order === 'desc' 
                        ? valB.localeCompare(valA) 
                        : valA.localeCompare(valB);
                }
                return currentSort.order === 'desc' ? valB - valA : valA - valB;
            });
            renderTable(sortedGames);
        });
    });

    gameSearch.addEventListener('input', (e) => {
        const term = e.target.value.toLowerCase();
        const filtered = allGames.filter(g => g.name.toLowerCase().includes(term));
        renderTable(filtered);
    });

    fetchData();
});
