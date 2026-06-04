/**
 * CashUp Integration Dashboard — Frontend Logic
 */

const svgIcon = (path) => `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" width="18" height="18"><path stroke-linecap="round" stroke-linejoin="round" d="${path}" /></svg>`;

const ENTITY_ICONS = {
    clientes: svgIcon('M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z'),
    produtos: svgIcon('M21 7.5l-9-5.25L3 7.5m18 0l-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9'),
    estoque: svgIcon('M13.5 10.5V6.75a4.5 4.5 0 119 0v3.75M3.75 21.75h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H3.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z'),
    condicoes_pagto: svgIcon('M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-3.75 3h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5z'),
    naturezas: svgIcon('M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25zM6.75 12h.008v.008H6.75V12zm0 3h.008v.008H6.75V15zm0 3h.008v.008H6.75V18z'),
    equipes_comerciais: svgIcon('M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z'),
    tabelas_preco: svgIcon('M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z'),
    transportadoras: svgIcon('M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124a17.902 17.902 0 00-3.213-9.193 2.056 2.056 0 00-1.58-.86H14.25M16.5 18.75h-2.25m0-11.177v-.958c0-.568-.422-1.048-.987-1.106a48.554 48.554 0 00-10.026 0 1.106 1.106 0 00-.987 1.106v7.635m12-6.677v6.677m0 4.5v-4.5m0 0h-12'),
    fichas_financeiras: svgIcon('M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z'),
    produtos_clientes: svgIcon('M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244'),
    notas_fiscais: svgIcon('M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z'),
    pedidos_envio: svgIcon('M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5'),
};

const ENTITY_LABELS = {
    clientes: 'Clientes',
    produtos: 'Produtos',
    estoque: 'Estoque',
    condicoes_pagto: 'Cond. Pagamento',
    naturezas: 'Naturezas',
    equipes_comerciais: 'Equipes Comerciais',
    tabelas_preco: 'Tabelas de Preço',
    transportadoras: 'Transportadoras',
    fichas_financeiras: 'Fichas Financeiras',
    produtos_clientes: 'Prod. do Cliente',
    notas_fiscais: 'Notas Fiscais',
    pedidos_envio: 'Pedidos (Envio)',
    titulos_financeiros: 'Títulos Financeiros',
};

let refreshInterval = null;

// ─── Initialization ───────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    loadStatus();
    checkHealth();
    refreshInterval = setInterval(loadStatus, 15000);
    setInterval(checkHealth, 60000);
});

// ─── API Calls ─────────────────────────────────────────

async function loadStatus() {
    try {
        const resp = await fetch('/api/status');
        const data = await resp.json();
        renderEntities(data.entities);
        updateStats(data.entities);
        renderChart(data.entities);
    } catch (err) {
        addLog('error', `Erro ao carregar status: ${err.message}`);
    }
}

async function checkHealth() {
    try {
        const resp = await fetch('/api/health');
        const data = await resp.json();
        const dot = document.getElementById('healthDot');
        const text = document.getElementById('healthText');

        if (data.cashup_api?.status === 'online') {
            dot.classList.remove('offline');
            text.textContent = 'API Online';
        } else {
            dot.classList.add('offline');
            text.textContent = 'API Offline';
        }
    } catch {
        document.getElementById('healthDot').classList.add('offline');
        document.getElementById('healthText').textContent = 'Sem Conexão';
    }
}

async function triggerSync(entity, force = false) {
    if (force && !confirm(`Forçar sincronização completa de "${ENTITY_LABELS[entity] || entity}"?\n\nTodos os registros serão reenviados, ignorando o controle de ID_SINC.`)) return;

    const btn = document.querySelector(`[data-entity="${entity}"] .btn-entity-sync`);
    const btnForce = document.querySelector(`[data-entity="${entity}"] .btn-entity-force`);
    if (btn) { btn.disabled = true; btn.classList.add('syncing'); btn.innerHTML = '<span class="spinner"></span> Sincronizando...'; }
    if (btnForce) btnForce.disabled = true;

    addLog(force ? 'warning' : 'info', `${force ? '⚡ Forçando' : 'Iniciando'} sync: ${ENTITY_LABELS[entity] || entity}`);

    try {
        const url = force ? `/api/sync/${entity}?force=true` : `/api/sync/${entity}`;
        const resp = await fetch(url, { method: 'POST' });
        const data = await resp.json();

        if (data.result) {
            const r = data.result;
            if (r.status === 'success') {
                addLog('success', `✓ ${ENTITY_LABELS[entity]}: ${r.sent_records || r.processed || 0} registros sincronizados`);
                showToast('success', `${ENTITY_LABELS[entity]} sincronizado com sucesso!`);
            } else if (r.status === 'partial') {
                addLog('warning', `⚠ ${ENTITY_LABELS[entity]}: parcial — ${r.sent_records} ok, ${r.error_records} erros`);
                showToast('error', `${ENTITY_LABELS[entity]}: sync parcial com erros`);
            } else {
                addLog('error', `✗ ${ENTITY_LABELS[entity]}: ${r.errors?.[0] || 'Erro desconhecido'}`);
                showToast('error', `${ENTITY_LABELS[entity]}: falha na sincronização`);
            }
        }
    } catch (err) {
        addLog('error', `✗ ${ENTITY_LABELS[entity]}: ${err.message}`);
        showToast('error', `Erro ao sincronizar ${ENTITY_LABELS[entity]}`);
    } finally {
        if (btn) { btn.disabled = false; btn.classList.remove('syncing'); btn.innerHTML = '⟳ Sincronizar'; }
        if (btnForce) btnForce.disabled = false;
        loadStatus();
    }
}

async function triggerSyncAll() {
    const btn = document.getElementById('btnSyncAll');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Sincronizando Tudo...';

    addLog('info', '═══ Iniciando sincronização de TODAS as entidades ═══');

    try {
        const resp = await fetch('/api/sync/all', { method: 'POST' });
        const data = await resp.json();

        if (data.results) {
            let ok = 0, fail = 0;
            for (const [entity, result] of Object.entries(data.results)) {
                if (result.status === 'success') ok++;
                else fail++;
            }
            addLog('success', `Sync completo: ${ok} sucesso, ${fail} com erros`);
            showToast(fail === 0 ? 'success' : 'error', `Sync completo: ${ok} ok, ${fail} erros`);
        }
    } catch (err) {
        addLog('error', `Sync geral falhou: ${err.message}`);
        showToast('error', 'Falha no sync geral');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '⟳ Sincronizar Tudo';
        loadStatus();
    }
}

// ─── Rendering ─────────────────────────────────────────

function renderEntities(entities) {
    const grid = document.getElementById('entitiesGrid');
    if (!grid) return;

    grid.innerHTML = '';

    for (const [entity, info] of Object.entries(entities)) {
        const card = createEntityCard(entity, info);
        grid.appendChild(card);
    }
}

function createEntityCard(entity, info) {
    const card = document.createElement('div');
    card.className = 'entity-card';
    card.setAttribute('data-entity', entity);

    const icon = ENTITY_ICONS[entity] || '📁';
    const label = ENTITY_LABELS[entity] || entity;
    const status = info.last_status || 'never';
    const lastTime = info.last_time ? formatTime(info.last_time) : '—';
    const sentRecords = info.last_sync?.sent_records ?? info.last_sync?.processed ?? '—';
    const errorRecords = info.last_sync?.error_records ?? 0;
    const totalExec = info.total_executions || 0;

    card.innerHTML = `
        <div class="entity-header">
            <div>
                <div class="entity-name">
                    <span class="entity-icon" style="display:inline-flex;width:28px;height:28px;font-size:14px;margin-right:8px;vertical-align:middle">${icon}</span>
                    <span class="name-text">${label}</span>
                </div>
            </div>
            <span class="entity-status ${status}">
                ${status === 'running' ? '<span class="spinner"></span>' : ''}
                ${status === 'success' ? '✓' : status === 'error' ? '✗' : status === 'partial' ? '⚠' : '●'}
                ${status}
            </span>
        </div>
        <div class="entity-meta">
            <div class="meta-item">
                <div class="meta-label">Último Sync</div>
                <div class="meta-value">${lastTime}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Registros</div>
                <div class="meta-value">${sentRecords}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Erros</div>
                <div class="meta-value" style="color: ${errorRecords > 0 ? 'var(--accent-red)' : 'var(--accent-green)'}">${errorRecords}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Execuções</div>
                <div class="meta-value">${totalExec}</div>
            </div>
        </div>
        <div class="entity-actions">
            <button class="btn-entity-sync" onclick="triggerSync('${entity}')">⟳ Sincronizar</button>
            <button class="btn-entity-force" onclick="triggerSync('${entity}', true)" title="Reenviar todos os registros ignorando o ID_SINC">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" width="14" height="14" style="vertical-align:middle;margin-right:4px"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" /></svg>
                Forçar
            </button>
            <button class="btn-entity-history" onclick="showHistory('${entity}')" title="Histórico">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" width="16" height="16">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
                </svg>
            </button>
        </div>
    `;

    return card;
}

function updateStats(entities) {
    let total = 0, success = 0, errors = 0, never = 0;

    for (const info of Object.values(entities)) {
        total++;
        const st = info.last_status;
        if (st === 'success') success++;
        else if (st === 'error' || st === 'partial') errors++;
        else if (st === 'never') never++;
    }

    setText('statTotal', total);
    setText('statSuccess', success);
    setText('statErrors', errors);
    setText('statNever', never);
}

// ─── Chart.js ──────────────────────────────────────────

let syncChartInstance = null;

function renderChart(entities) {
    const ctx = document.getElementById('syncChart');
    if (!ctx) return;
    
    const labels = [];
    const successData = [];
    const errorData = [];
    
    // Filtra apenas as entidades que já rodaram pelo menos 1 vez
    for (const [entity, info] of Object.entries(entities)) {
        if (info.total_executions > 0) {
            labels.push(ENTITY_LABELS[entity] || entity);
            successData.push(info.last_sync?.sent_records || info.last_sync?.processed || 0);
            errorData.push(info.last_sync?.error_records || 0);
        }
    }
    
    if (labels.length === 0) return; // Nada para desenhar ainda
    
    if (syncChartInstance) {
        syncChartInstance.data.labels = labels;
        syncChartInstance.data.datasets[0].data = successData;
        syncChartInstance.data.datasets[1].data = errorData;
        syncChartInstance.update();
        return;
    }
    
    syncChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Sucessos (Último Sync)',
                    data: successData,
                    backgroundColor: 'rgba(36, 161, 72, 0.8)',
                    borderColor: '#24a148',
                    borderWidth: 1,
                    borderRadius: 4
                },
                {
                    label: 'Erros (Último Sync)',
                    data: errorData,
                    backgroundColor: 'rgba(218, 30, 40, 0.8)',
                    borderColor: '#da1e28',
                    borderWidth: 1,
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            color: '#f4f4f4',
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: '#c6c6c6', precision: 0 }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#c6c6c6' }
                }
            },
            plugins: {
                legend: { labels: { color: '#f4f4f4' } }
            },
            animation: {
                duration: 800,
                easing: 'easeOutQuart'
            }
        }
    });
}

// ─── History Modal ─────────────────────────────────────

async function showHistory(entity) {
    try {
        const resp = await fetch(`/api/history/${entity}?limit=10`);
        const data = await resp.json();

        let msg = `═══ Histórico: ${ENTITY_LABELS[entity]} ═══\n`;
        if (!data.history?.length) {
            msg += 'Nenhuma execução registrada.';
        } else {
            for (const h of data.history) {
                msg += `\n[${h.status}] ${h.started_at} — `;
                msg += `${h.sent_records || h.processed || 0} reg, ${h.error_records || 0} erros`;
                if (h.duration_seconds) msg += ` (${h.duration_seconds}s)`;
            }
        }
        addLog('info', msg);
    } catch (err) {
        addLog('error', `Erro ao buscar histórico: ${err.message}`);
    }
}

// ─── Log Panel ─────────────────────────────────────────

function addLog(level, message) {
    const container = document.getElementById('logContent');
    if (!container) return;

    const entry = document.createElement('div');
    entry.className = 'log-entry';
    const time = new Date().toLocaleTimeString('pt-BR');
    entry.innerHTML = `<span class="log-time">${time}</span><span class="log-${level}">${message}</span>`;

    container.insertBefore(entry, container.firstChild);

    // Limit log entries
    while (container.children.length > 200) {
        container.removeChild(container.lastChild);
    }
}

function clearLog() {
    const container = document.getElementById('logContent');
    if (container) container.innerHTML = '';
}

// ─── Toast ─────────────────────────────────────────────

function showToast(type, message) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 4000);
}

// ─── Utilities ─────────────────────────────────────────

function formatTime(isoString) {
    if (!isoString) return '—';
    try {
        const date = new Date(isoString);
        return date.toLocaleString('pt-BR', {
            day: '2-digit', month: '2-digit',
            hour: '2-digit', minute: '2-digit',
        });
    } catch {
        return isoString;
    }
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}
