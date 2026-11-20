document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('schedule-container');
    if (!container || !window.ACADEMIC_SCHEDULE) return;

    container.innerHTML = `
        <div class="schedule-grid" style="display: flex; gap: 20px;">
            <div class="schedule-col" id="col-F" style="flex: 1;">
                <h3>F班课讯</h3>
                <div class="list"></div>
            </div>
            <div class="schedule-col" id="col-C" style="flex: 1;">
                <h3>C班课讯</h3>
                <div class="list"></div>
            </div>
        </div>
    `;

    function render(group, selector) {
        const list = document.querySelector(selector + ' .list');
        const data = window.ACADEMIC_SCHEDULE[group];
        list.innerHTML = data.slice(-5).reverse().map(item => `
            <div class="class-card" style="background: var(--paper-warm); padding: 15px; margin-bottom: 15px; border: 1px solid var(--rule);">
                <div class="card-date" style="border-bottom: 1px solid var(--rule-strong); margin-bottom: 10px;">${item.date}</div>
                ${item.classInfo.map(c => `
                    <div class="class-item" style="padding: 5px 0;">
                        <strong>${c.name}</strong> <span>(${c.time})</span><br>
                        <small style="color: var(--muted);">${c.location}</small>
                    </div>
                `).join('')}
            </div>
        `).join('');
    }

    render('F', '#col-F');
    render('C', '#col-C');
});