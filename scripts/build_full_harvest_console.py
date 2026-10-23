"""Script to integrate full Harvest Lot Management, Admin Trash modal, and Unlimited QR into producer_wizard.js."""

import os
import re
import shutil

src_path = "backend/apps/publicview/static/publicview/js/producer_wizard.js"
with open(src_path, "r", encoding="utf-8") as f:
    js = f.read()

# 1. Update filterAdminQueue and renderAdminConsoleUI to include TRASH
admin_ui_patch = """
  function renderAdminConsoleUI(container) {
    const t = getI18n();
    const activeFilter = wizardState.adminFilterStatus || 'ALL';
    const items = wizardState.adminEntities || [];
    const inspected = wizardState.adminInspectedEntity;

    const filters = [
      { key: 'ALL', label: t.filterAll },
      { key: 'SUBMITTED', label: t.filterSubmitted },
      { key: 'VERIFIED', label: t.filterVerified },
      { key: 'DRAFT', label: t.filterDraft },
      { key: 'NEEDS_CHANGES', label: t.filterChanges },
      { key: 'REJECTED', label: t.filterRejected },
      { key: 'TRASH', label: t.tabTrash || 'Trash' }
    ];
"""

old_admin_filters = re.search(r"  function renderAdminConsoleUI\(container\) \{[\s\S]*?const filters = \[[\s\S]*?\];", js)
if old_admin_filters:
    js = js[:old_admin_filters.start()] + admin_ui_patch.strip() + js[old_admin_filters.end():]
    print("Admin filter tabs updated with TRASH")

# 2. Add TRASH to statusColors in table
old_status_colors = """                const statusColors = {
                  VERIFIED: { bg: '#ecfdf5', text: '#065f46', border: '#86efac' },
                  SUBMITTED: { bg: '#fffbeb', text: '#92400e', border: '#fde68a' },
                  DRAFT: { bg: '#f1f5f9', text: '#475569', border: '#cbd5e1' },
                  NEEDS_CHANGES: { bg: '#fff7ed', text: '#9a3412', border: '#fed7aa' },
                  REJECTED: { bg: '#fef2f2', text: '#991b1b', border: '#fecaca' }
                };"""

new_status_colors = """                const statusColors = {
                  VERIFIED: { bg: '#ecfdf5', text: '#065f46', border: '#86efac' },
                  SUBMITTED: { bg: '#fffbeb', text: '#92400e', border: '#fde68a' },
                  DRAFT: { bg: '#f1f5f9', text: '#475569', border: '#cbd5e1' },
                  NEEDS_CHANGES: { bg: '#fff7ed', text: '#9a3412', border: '#fed7aa' },
                  REJECTED: { bg: '#fef2f2', text: '#991b1b', border: '#fecaca' },
                  TRASH: { bg: '#fef2f2', text: '#b91c1c', border: '#fca5a5' }
                };"""

if old_status_colors in js:
    js = js.replace(old_status_colors, new_status_colors)

# 3. Add Delete Producer Data button in renderAdminEntityInspector
old_inspector_actions = """        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
          <button type="button" class="btn-wizard-action btn-wizard-submit" onclick="submitAdminDecision('${ent.entity_id}', 'APPROVED')">
            <span>${getIcon('check', 14, '#ffffff', 2.8)}</span> <span>${escapeHtml(t.btnApproveEntity)}</span>
          </button>
          <button type="button" class="btn-wizard-action btn-wizard-draft" onclick="submitAdminDecision('${ent.entity_id}', 'NEEDS_CHANGES')">
            ${escapeHtml(t.btnRequestChanges)}
          </button>
          <button type="button" class="btn-wizard-action btn-wizard-prev" style="color: #dc2626; border-color: #fca5a5;" onclick="submitAdminDecision('${ent.entity_id}', 'REJECTED')">
            ${escapeHtml(t.btnRejectEntity)}
          </button>
        </div>"""

new_inspector_actions = """        <div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: center;">
          ${ent.status === 'TRASH' ? `
            <div style="width: 100%; background: #fee2e2; border: 1px solid #f87171; border-radius: 8px; padding: 10px 14px; color: #991b1b; font-size: 13px; font-weight: 700; margin-bottom: 8px;">
              <span>${getIcon('alert', 16, '#dc2626')}</span> <span>This producer is currently in Admin Trash.</span>
            </div>
            <button type="button" class="btn-wizard-action btn-wizard-submit" onclick="restoreAdminProducer('${ent.entity_id}')">
              <span>${getIcon('check', 14, '#ffffff')}</span> <span>${escapeHtml(t.btnRestoreProducer || 'Restore Producer')}</span>
            </button>
            <button type="button" class="btn-wizard-action" style="color: #ffffff; background: #991b1b; border: 1.5px solid #7f1d1d; font-weight: 700;" onclick="openDeleteProducerModal('${ent.entity_id}', '${escapeHtml(ent.organisation_name || ent.full_name)}', true)">
              <span>${getIcon('trash', 14, '#ffffff')}</span> <span>${escapeHtml(t.btnPurgeProducer || 'Purge Permanently')}</span>
            </button>
          ` : `
            <button type="button" class="btn-wizard-action btn-wizard-submit" onclick="submitAdminDecision('${ent.entity_id}', 'APPROVED')">
              <span>${getIcon('check', 14, '#ffffff', 2.8)}</span> <span>${escapeHtml(t.btnApproveEntity)}</span>
            </button>
            <button type="button" class="btn-wizard-action btn-wizard-draft" onclick="submitAdminDecision('${ent.entity_id}', 'NEEDS_CHANGES')">
              ${escapeHtml(t.btnRequestChanges)}
            </button>
            <button type="button" class="btn-wizard-action btn-wizard-prev" style="color: #dc2626; border-color: #fca5a5;" onclick="submitAdminDecision('${ent.entity_id}', 'REJECTED')">
              ${escapeHtml(t.btnRejectEntity)}
            </button>
            <button type="button" class="btn-wizard-action" style="color: #ffffff; background: #dc2626; border: 1.5px solid #b91c1c; font-weight: 700; display: inline-flex; align-items: center; gap: 6px;" onclick="openDeleteProducerModal('${ent.entity_id}', '${escapeHtml(ent.organisation_name || ent.full_name)}', false)">
              <span>${getIcon('trash', 14, '#ffffff')}</span> <span>${escapeHtml(t.btnDeleteProducer || 'Delete Producer Data')}</span>
            </button>
          `}
        </div>"""

if old_inspector_actions in js:
    js = js.replace(old_inspector_actions, new_inspector_actions)
    print("Admin inspect and decide actions updated with Delete Producer Data")

# 4. Replace renderVerifiedOperationalConsole with the full Harvest Lot Console
harvest_console_code = """
  /* --------------------------------------------------------------------------
     VERIFIED PRODUCER CONSOLE: ONE-PAGE HARVEST LOT MANAGEMENT & CUSTODY LEDGER
     -------------------------------------------------------------------------- */
  window._producerLots = [];
  window._producerPlots = [];
  window._lotFilterState = {
    search: '',
    crop: 'ALL',
    plot: 'ALL',
    custody: 'ALL',
    payment: 'ALL',
    sort: '-created_at'
  };

  async function renderVerifiedOperationalConsole(container) {
    const t = getI18n();
    const p = wizardState.profile || {};
    const eCode = p.entity_code || '';
    const orgDisplayName = p.organisation_name || [p.first_name, p.last_name].filter(Boolean).join(' ') || 'Farmer Producer Node';

    // Permanently hide the 6 legacy tool cards and dummy batches list
    const toolsGrid = document.getElementById('workspaceTools');
    const batchesList = document.getElementById('workspaceBatchesList');
    if (toolsGrid) toolsGrid.style.display = 'none';
    if (batchesList && batchesList.parentNode) batchesList.parentNode.style.display = 'none';

    container.innerHTML = `
      <div style="background: #ffffff; border-radius: 16px; border: 1.5px solid #10b981; padding: 24px; margin: 12px 0; box-shadow: 0 4px 16px rgba(16, 185, 129, 0.08);">
        <!-- Top Entity Header Bar -->
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; padding-bottom: 14px; margin-bottom: 20px; flex-wrap: wrap; gap: 12px;">
          <div>
            <div style="display: inline-flex; align-items: center; gap: 6px; background: #ecfdf5; border: 1px solid #86efac; color: #065f46; font-size: 12px; font-weight: 800; padding: 4px 10px; border-radius: 20px; margin-bottom: 6px;">
              <span>${getIcon('check', 14, '#15803d', 2.8)}</span> <span>${escapeHtml(t.verifiedNodeBadge || 'VERIFIED PRODUCER NODE')}</span>
            </div>
            <h3 style="margin: 0; font-size: 22px; font-weight: 800; color: #0f172a;">${escapeHtml(orgDisplayName)}</h3>
            <span style="font-size: 13px; color: #64748b;">${escapeHtml([p.village_town, p.district, getStateLabel(p.state)].filter(Boolean).join(', '))}</span>
          </div>
          <div style="text-align: right; display: flex; align-items: center; gap: 14px;">
            <div>
              <div style="font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase;">${escapeHtml(t.lblSovereignCode || 'Sovereign Code')}</div>
              <div style="font-family: monospace; font-size: 19px; font-weight: 900; color: #0b3d2e; letter-spacing: 1px;">${escapeHtml(eCode)}</div>
            </div>
            <button type="button" class="btn-wizard-action btn-wizard-draft" style="padding: 7px 14px; font-size: 12px; color: #dc2626; border-color: #fca5a5;" onclick="window.logoutEntitySession()">
              ${escapeHtml(t.btnLogOut || 'Log Out')}
            </button>
          </div>
        </div>

        <!-- Quick Metrics Row -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 22px;">
          <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px 16px; border-radius: 12px;">
            <div style="font-size: 12px; color: #64748b; font-weight: 700;">${escapeHtml(t.statTotalLots || 'Total Harvest Lots')}</div>
            <div style="font-size: 24px; font-weight: 900; color: #0b3d2e;" id="metricTotalLots">0</div>
            <div style="font-size: 11.5px; color: #10b981;">${escapeHtml(t.statInLedger || 'Recorded on Sovereign Chain')}</div>
          </div>
          <div style="background: #ecfdf5; border: 1.5px solid #a7f3d0; padding: 14px 16px; border-radius: 12px;">
            <div style="font-size: 12px; color: #065f46; font-weight: 700;">${escapeHtml(t.statusInCustody || 'In Farm Custody')}</div>
            <div style="font-size: 24px; font-weight: 900; color: #047857;" id="metricInCustody">0</div>
            <div style="font-size: 11.5px; color: #059669;">${escapeHtml(t.statEditable || 'Editable (Pre-Handover)')}</div>
          </div>
          <div style="background: #fffbeb; border: 1.5px solid #fde68a; padding: 14px 16px; border-radius: 12px;">
            <div style="font-size: 12px; color: #92400e; font-weight: 700;">${escapeHtml(t.statusInTransit || 'In Transit (Locked)')}</div>
            <div style="font-size: 24px; font-weight: 900; color: #b45309;" id="metricInTransit">0</div>
            <div style="font-size: 11.5px; color: #d97706;">${escapeHtml(t.statImmutable || 'Immutable Custody Transfer')}</div>
          </div>
          <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px 16px; border-radius: 12px;">
            <div style="font-size: 12px; color: #64748b; font-weight: 700;">${escapeHtml(t.statTotalQty || 'Total Harvest Weight')}</div>
            <div style="font-size: 24px; font-weight: 900; color: #0b3d2e;" id="metricTotalWeight">0.0 Kg</div>
            <div style="font-size: 11.5px; color: #64748b;">${escapeHtml(t.statCumulative || 'Cumulative Yield')}</div>
          </div>
        </div>

        <!-- Action Bar: Register Lot CTA Button -->
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 18px; padding-bottom: 12px; border-bottom: 1px solid #f1f5f9;">
          <div>
            <h4 style="margin: 0; font-size: 17px; font-weight: 800; color: #0f172a; display: flex; align-items: center; gap: 8px;">
              <span>${getIcon('sprout', 20, '#047857')}</span> <span>${escapeHtml(t.consoleHeading || 'Harvest Lot & Custody Ledger Console')}</span>
            </h4>
          </div>
          <button type="button" class="btn-wizard-action btn-wizard-submit" style="padding: 10px 20px; font-size: 13.5px; font-weight: 800; box-shadow: 0 4px 12px rgba(4, 120, 87, 0.25);" onclick="openHarvestLotModal(null)">
            <span style="font-size: 17px; line-height: 1; margin-right: 4px;">+</span> <span>${escapeHtml(t.btnRegisterLot || '+ Register New Harvest Lot')}</span>
          </button>
        </div>

        <!-- Search & Filter Controls Toolbar -->
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; margin-bottom: 18px; display: grid; grid-template-columns: 2fr repeat(4, 1fr) 1.2fr; gap: 10px; align-items: center;">
          <input type="text" id="filter_search" class="form-input" style="background: #fff; font-size: 12.5px;" placeholder="${escapeHtml(t.searchLotPh || 'Search lot code, crop, variety, or plot...')}" oninput="applyLotFilters()" />
          
          <select id="filter_crop" class="form-select" style="background: #fff; font-size: 12px;" onchange="applyLotFilters()">
            <option value="ALL">${escapeHtml(t.filterAllCrops || 'All Crops')}</option>
            ${(wizardState.selectedCrops || []).map(c => `<option value="${escapeHtml(c)}">${escapeHtml(getCropLabel(c))}</option>`).join('')}
          </select>

          <select id="filter_plot" class="form-select" style="background: #fff; font-size: 12px;" onchange="applyLotFilters()">
            <option value="ALL">${escapeHtml(t.filterAllPlots || 'All Plots / Land')}</option>
            ${(wizardState.plots || []).map(pl => `<option value="${escapeHtml(pl.plot_id)}">${escapeHtml(pl.plot_name || 'Plot')} (${pl.area_acres || 0} Ac)</option>`).join('')}
          </select>

          <select id="filter_custody" class="form-select" style="background: #fff; font-size: 12px;" onchange="applyLotFilters()">
            <option value="ALL">${escapeHtml(t.filterAllCustody || 'All Custody States')}</option>
            <option value="IN_CUSTODY">${escapeHtml(t.statusInCustody || 'In Farm Custody (Editable)')}</option>
            <option value="IN_TRANSIT">${escapeHtml(t.statusInTransit || 'In Transit (Locked)')}</option>
            <option value="CLOSED">${escapeHtml(t.statusHandoverDone || 'Handover Approved')}</option>
          </select>

          <select id="filter_payment" class="form-select" style="background: #fff; font-size: 12px;" onchange="applyLotFilters()">
            <option value="ALL">${escapeHtml(t.filterAllPayment || 'All Payment Statuses')}</option>
            <option value="PENDING">${escapeHtml(t.paymentPending || 'Pending Settlement')}</option>
            <option value="ADVANCE">${escapeHtml(t.paymentAdvance || 'Advance Received')}</option>
            <option value="SETTLED">${escapeHtml(t.paymentSettled || 'Fully Settled')}</option>
          </select>

          <select id="filter_sort" class="form-select" style="background: #fff; font-size: 12px; font-weight: 700;" onchange="applyLotFilters()">
            <option value="-created_at">${escapeHtml(t.sortLatest || 'Latest to Oldest')}</option>
            <option value="created_at">${escapeHtml(t.sortOldest || 'Oldest to Latest')}</option>
            <option value="-qty">${escapeHtml(t.sortQtyHigh || 'Quantity: High to Low')}</option>
            <option value="qty">${escapeHtml(t.sortQtyLow || 'Quantity: Low to High')}</option>
          </select>
        </div>

        <!-- Harvest Lots List Container -->
        <div id="producerHarvestLotsList">
          <div style="text-align: center; padding: 40px; color: #64748b;">
            <div style="width: 28px; height: 28px; border: 2.5px solid #cbd5e1; border-top-color: #047857; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 12px;"></div>
            <span>Loading registered harvest lots from ledger...</span>
          </div>
        </div>
      </div>
    `;

    await loadProducerLots();
  }

  async function loadProducerLots() {
    try {
      const res = await fetch('/api/v1/lots/', { headers: getAuthHeader() });
      if (res.ok) {
        const data = await res.json();
        window._producerLots = data.items || [];
      } else {
        window._producerLots = [];
      }
    } catch (e) {
      window._producerLots = [];
    }
    updateLotMetrics();
    applyLotFilters();
  }

  function updateLotMetrics() {
    const lots = window._producerLots || [];
    const totalEl = document.getElementById('metricTotalLots');
    const inCustodyEl = document.getElementById('metricInCustody');
    const inTransitEl = document.getElementById('metricInTransit');
    const weightEl = document.getElementById('metricTotalWeight');

    if (totalEl) totalEl.innerText = lots.length;
    const custodyCount = lots.filter(l => l.state === 'CREATED' || l.state === 'IN_CUSTODY').length;
    const transitCount = lots.filter(l => l.state === 'IN_TRANSIT').length;
    const totalWeight = lots.reduce((acc, l) => acc + (parseFloat(l.net_qty_kg || l.on_hand_kg || 0) || 0), 0);

    if (inCustodyEl) inCustodyEl.innerText = custodyCount;
    if (inTransitEl) inTransitEl.innerText = transitCount;
    if (weightEl) weightEl.innerText = totalWeight.toLocaleString('en-IN', { maximumFractionDigits: 1 }) + ' Kg';
  }

  window.applyLotFilters = function () {
    const t = getI18n();
    const lots = window._producerLots || [];
    const searchVal = (document.getElementById('filter_search')?.value || '').trim().toLowerCase();
    const cropVal = document.getElementById('filter_crop')?.value || 'ALL';
    const plotVal = document.getElementById('filter_plot')?.value || 'ALL';
    const custodyVal = document.getElementById('filter_custody')?.value || 'ALL';
    const paymentVal = document.getElementById('filter_payment')?.value || 'ALL';
    const sortVal = document.getElementById('filter_sort')?.value || '-created_at';

    let filtered = lots.filter(lot => {
      if (searchVal) {
        const text = [lot.public_code, lot.crop, lot.variety, lot.origin_plot_name, lot.remarks].filter(Boolean).join(' ').toLowerCase();
        if (!text.includes(searchVal)) return false;
      }
      if (cropVal !== 'ALL' && String(lot.crop).toLowerCase() !== cropVal.toLowerCase()) return false;
      if (plotVal !== 'ALL' && String(lot.origin_plot_id) !== plotVal) return false;
      if (custodyVal !== 'ALL') {
        if (custodyVal === 'IN_CUSTODY' && !(lot.state === 'CREATED' || lot.state === 'IN_CUSTODY')) return false;
        if (custodyVal === 'IN_TRANSIT' && lot.state !== 'IN_TRANSIT') return false;
        if (custodyVal === 'CLOSED' && lot.state !== 'CLOSED') return false;
      }
      if (paymentVal !== 'ALL' && (lot.payment_status || 'PENDING') !== paymentVal) return false;
      return true;
    });

    // Sorting
    filtered.sort((a, b) => {
      const dateA = new Date(a.created_at || a.harvest_date || 0).getTime();
      const dateB = new Date(b.created_at || b.harvest_date || 0).getTime();
      const qtyA = parseFloat(a.net_qty_kg || a.on_hand_kg || 0);
      const qtyB = parseFloat(b.net_qty_kg || b.on_hand_kg || 0);

      if (sortVal === 'created_at') return dateA - dateB;
      if (sortVal === '-qty') return qtyB - qtyA;
      if (sortVal === 'qty') return qtyA - qtyB;
      return dateB - dateA; // default -created_at
    });

    renderFilteredLotsList(filtered, t);
  };

  function renderFilteredLotsList(list, t) {
    const listContainer = document.getElementById('producerHarvestLotsList');
    if (!listContainer) return;

    if (!list || list.length === 0) {
      listContainer.innerHTML = `
        <div style="background: #f8fafc; border: 1.5px dashed #cbd5e1; border-radius: 12px; padding: 48px 20px; text-align: center;">
          <div style="width: 48px; height: 48px; background: #ecfdf5; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px;">
            ${getIcon('sprout', 24, '#047857')}
          </div>
          <h4 style="margin: 0 0 6px; font-size: 16px; color: #0f172a; font-weight: 800;">${escapeHtml(t.emptyLotsTitle || 'No harvest lots recorded in custody yet')}</h4>
          <p style="margin: 0 0 16px; font-size: 13px; color: #64748b; max-width: 460px; margin-left: auto; margin-right: auto;">${escapeHtml(t.emptyLotsSub || 'Click the button above to register your first harvest lot and generate unique QR labels.')}</p>
          <button type="button" class="btn-wizard-action btn-wizard-submit" style="padding: 9px 18px; font-size: 13px;" onclick="openHarvestLotModal(null)">
            <span>+</span> <span>${escapeHtml(t.btnRegisterLot || '+ Register New Harvest Lot')}</span>
          </button>
        </div>
      `;
      return;
    }

    listContainer.innerHTML = list.map(lot => {
      const isEditable = lot.is_editable !== false && (lot.state === 'CREATED' || lot.state === 'IN_CUSTODY');
      const pStatus = lot.payment_status || 'PENDING';
      const paymentStyles = {
        PENDING: { label: t.paymentPending || 'Pending Settlement', bg: '#fffbeb', text: '#92400e', border: '#fde68a' },
        ADVANCE: { label: t.paymentAdvance || 'Advance Received', bg: '#eff6ff', text: '#1e40af', border: '#bfdbfe' },
        SETTLED: { label: t.paymentSettled || 'Fully Settled', bg: '#ecfdf5', text: '#065f46', border: '#86efac' }
      };
      const ps = paymentStyles[pStatus] || paymentStyles.PENDING;

      const weightDisplay = (parseFloat(lot.net_qty_kg || lot.on_hand_kg || 0)).toLocaleString('en-IN') + ' ' + (lot.unit || 'Kg');
      const harvestDateDisplay = lot.harvest_date ? new Date(lot.harvest_date).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' }) : 'Recent';

      return `
        <div class="harvest-lot-row-card" style="background: #ffffff; border: 1.5px solid ${isEditable ? '#e2e8f0' : '#fed7aa'}; border-radius: 12px; padding: 18px; margin-bottom: 12px; transition: all 0.15s ease-in-out; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
          <!-- Top Row: Public Code, Crop & Variety, Custody Status -->
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 14px; border-bottom: 1px solid #f1f5f9; padding-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
              <span style="font-family: monospace; font-size: 14px; font-weight: 800; color: #047857; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 4px 10px; border-radius: 6px; letter-spacing: 0.5px;">
                ${escapeHtml(lot.public_code)}
              </span>
              <strong style="font-size: 16px; color: #0f172a;">${escapeHtml(getCropLabel(lot.crop))}</strong>
              ${lot.variety ? `<span style="font-size: 13.5px; color: #475569; font-weight: 600;">• ${escapeHtml(lot.variety)}</span>` : ''}
              ${lot.grade ? `<span style="font-size: 11px; font-weight: 800; color: #1e40af; background: #eff6ff; border: 1px solid #bfdbfe; padding: 2px 8px; border-radius: 12px;">${escapeHtml(lot.grade)}</span>` : ''}
              <span style="font-size: 11px; font-weight: 700; color: ${ps.text}; background: ${ps.bg}; border: 1px solid ${ps.border}; padding: 2px 8px; border-radius: 12px;">
                ${escapeHtml(ps.label)}
              </span>
            </div>

            <!-- Right-hand custody status & Lock/Edit action -->
            <div style="display: flex; align-items: center; gap: 10px;">
              ${isEditable ? `
                <span style="display: inline-flex; align-items: center; gap: 5px; font-size: 12px; font-weight: 800; color: #065f46; background: #ecfdf5; border: 1px solid #86efac; padding: 4px 10px; border-radius: 20px;">
                  <span>${getIcon('check', 13, '#10b981')}</span> <span>${escapeHtml(t.statusInCustody || 'In Farm Custody')}</span>
                </span>
                <button type="button" class="btn-wizard-action btn-wizard-draft" style="padding: 6px 12px; font-size: 12px; display: inline-flex; align-items: center; gap: 5px;" onclick="openHarvestLotModal('${lot.public_code}')" title="Edit Harvest Lot">
                  <span>${getIcon('edit', 14, '#047857')}</span> <span>${escapeHtml(t.btnEditLot || 'Edit')}</span>
                </button>
              ` : `
                <span style="display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 800; color: #9a3412; background: #fff7ed; border: 1.5px solid #fdba74; padding: 4px 12px; border-radius: 20px;" title="${escapeHtml(t.lblLockedNotice || 'Locked: Custody handover active. Immutability enforced.')}">
                  <span>${getIcon('lock', 14, '#c2410c')}</span> <span>${escapeHtml(lot.state === 'IN_TRANSIT' ? (t.statusInTransit || 'In Transit (Locked)') : (t.statusHandoverDone || 'Handover Approved (Locked)'))}</span>
                </span>
              `}
            </div>
          </div>

          <!-- Body Grid: Harvest Info, Land/Origin, Commercials -->
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; font-size: 13px; color: #334155; margin-bottom: 14px;">
            <div>
              <div style="font-size: 11.5px; color: #64748b; font-weight: 700; text-transform: uppercase;">Harvest Quantity</div>
              <div style="font-size: 15px; font-weight: 800; color: #0b3d2e;">${escapeHtml(weightDisplay)}</div>
              <div style="font-size: 12px; color: #64748b;">${lot.packages_count ? `${lot.packages_count} ${lot.package_type || 'Crates'}` : 'Bulk Harvest'}</div>
            </div>

            <div>
              <div style="font-size: 11.5px; color: #64748b; font-weight: 700; text-transform: uppercase;">Origin Plot & Land</div>
              <div style="font-size: 13.5px; font-weight: 700; color: #0f172a;">${escapeHtml(lot.origin_plot_name || 'Registered Farm Parcel')}</div>
              <div style="font-size: 12px; color: #64748b;">${lot.plot_area_acres ? `${lot.plot_area_acres} Acres • ` : ''}${escapeHtml(lot.farming_method || 'Conventional')}</div>
            </div>

            <div>
              <div style="font-size: 11.5px; color: #64748b; font-weight: 700; text-transform: uppercase;">Harvest Timestamp</div>
              <div style="font-size: 13px; font-weight: 600; color: #334155;">${escapeHtml(harvestDateDisplay)}</div>
              <div style="font-size: 12px; color: #047857; font-weight: 600;">${lot.shelf_life_days ? `Shelf-Life: ~${lot.shelf_life_days} Days` : ''}</div>
            </div>

            <div>
              <div style="font-size: 11.5px; color: #64748b; font-weight: 700; text-transform: uppercase;">Valuation & Buyer</div>
              <div style="font-size: 13.5px; font-weight: 700; color: #0f172a;">
                ${lot.base_price_per_unit ? `₹${parseFloat(lot.base_price_per_unit).toFixed(2)} / ${lot.unit || 'Kg'}` : 'Market Price'}
                ${lot.estimated_value ? `<span style="color: #047857;"> (₹${parseFloat(lot.estimated_value).toLocaleString('en-IN')})</span>` : ''}
              </div>
              <div style="font-size: 12px; color: #64748b;">Target: ${escapeHtml(lot.intended_buyer || 'APMC Mandi')}</div>
            </div>
          </div>

          <!-- Bottom Action Buttons: Print QR Labels & Public Trace -->
          <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px dashed #e2e8f0; padding-top: 10px; flex-wrap: wrap; gap: 8px;">
            <div style="display: flex; gap: 8px;">
              <button type="button" class="btn-wizard-action btn-wizard-draft" style="padding: 6px 14px; font-size: 12px; font-weight: 700; display: inline-flex; align-items: center; gap: 6px;" onclick="openUnlimitedQrPrintModal('${lot.public_code}', '${escapeHtml(lot.crop)}', '${escapeHtml(lot.variety || '')}', '${escapeHtml(weightDisplay)}')">
                <span>${getIcon('printer', 14, '#047857')}</span> <span>${escapeHtml(t.btnPrintQr || 'Print QR Labels (Unlimited)')}</span>
              </button>
              <a href="/l/${encodeURIComponent(lot.public_code)}" target="_blank" style="padding: 6px 12px; font-size: 12px; font-weight: 700; color: #047857; text-decoration: none; border: 1px solid #cbd5e1; border-radius: 8px; display: inline-flex; align-items: center; gap: 5px; background: #fff;">
                <span>${getIcon('globe', 13, '#047857')}</span> <span>Public Trace Page</span>
              </a>
            </div>

            ${isEditable ? `
              <button type="button" class="btn-wizard-action btn-wizard-submit" style="padding: 6px 16px; font-size: 12px; font-weight: 700;" onclick="openQuickDispatchModal('${lot.public_code}', '${escapeHtml(lot.crop)}', ${parseFloat(lot.net_qty_kg || lot.on_hand_kg || 0)})">
                <span>Dispatch to Mandi / Buyer &rarr;</span>
              </button>
            ` : ''}
          </div>
        </div>
      `;
    }).join('');
  }

  /* --------------------------------------------------------------------------
     LOT CREATION & EDIT MODAL (ALL POSSIBLE AGRICULTURAL & COMMERCIAL FIELDS)
     -------------------------------------------------------------------------- */
  window.openHarvestLotModal = function (lotCode) {
    const t = getI18n();
    const isEdit = !!lotCode;
    const existing = isEdit ? (window._producerLots || []).find(l => l.public_code === lotCode) : null;

    let modal = document.getElementById('harvestLotModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'harvestLotModal';
      modal.className = 'wizard-modal-backdrop';
      modal.style.cssText = 'position: fixed; inset: 0; background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(4px); z-index: 99999; display: flex; align-items: center; justify-content: center; padding: 16px;';
      document.body.appendChild(modal);
    }

    const plots = wizardState.plots || [];
    const registeredCrops = wizardState.selectedCrops || [];
    const nowIso = new Date().toISOString().slice(0, 16);

    modal.innerHTML = `
      <div style="background: #ffffff; border-radius: 16px; max-width: 820px; width: 100%; max-height: 90vh; overflow-y: auto; padding: 26px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 14px; margin-bottom: 20px;">
          <div>
            <h3 style="margin: 0; font-size: 20px; font-weight: 800; color: #0b3d2e; display: flex; align-items: center; gap: 8px;">
              <span>${getIcon(isEdit ? 'edit' : 'sprout', 20, '#047857')}</span>
              <span>${isEdit ? `Edit Harvest Lot #${lotCode}` : 'Register New Harvest Lot'}</span>
            </h3>
            <span style="font-size: 12.5px; color: #64748b;">Collect and sign all agricultural traceability, quality, and commercial settlement parameters.</span>
          </div>
          <button type="button" onclick="closeHarvestLotModal()" style="background: #f1f5f9; border: none; font-size: 18px; width: 32px; height: 32px; border-radius: 50%; cursor: pointer; color: #64748b; line-height: 1;">&times;</button>
        </div>

        <form id="form_harvest_lot" onsubmit="submitHarvestLotForm(event, '${lotCode || ''}')">
          <!-- 1. Commodity & Crop Identity -->
          <fieldset style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; margin-bottom: 16px;">
            <legend style="font-size: 13px; font-weight: 800; color: #047857; padding: 0 6px;">1. Produce & Crop Identity</legend>
            <div class="form-grid-3" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
              <div class="form-group">
                <label class="form-label">Crop / Commodity <span class="req">*</span></label>
                <select class="form-select" id="lot_inp_crop" required>
                  ${registeredCrops.map(c => `<option value="${escapeHtml(c)}" ${existing && existing.crop === c ? 'selected' : ''}>${escapeHtml(getCropLabel(c))}</option>`).join('')}
                  ${CROPS_LIST.filter(c => !registeredCrops.includes(c.id)).map(c => `<option value="${escapeHtml(c.id)}" ${existing && existing.crop === c.id ? 'selected' : ''}>${escapeHtml(getCropLabel(c.id))}</option>`).join('')}
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">Variety / Cultivar</label>
                <input type="text" class="form-input" id="lot_inp_variety" value="${escapeHtml(existing?.variety || '')}" placeholder="e.g. Hybrid Red 105, Jyoti, Alphonso" />
              </div>

              <div class="form-group">
                <label class="form-label">Produce Category</label>
                <select class="form-select" id="lot_inp_category">
                  <option value="Vegetable" ${existing?.category === 'Vegetable' ? 'selected' : ''}>Vegetable</option>
                  <option value="Fruit" ${existing?.category === 'Fruit' ? 'selected' : ''}>Fruit</option>
                  <option value="Grain/Cereal" ${existing?.category === 'Grain/Cereal' ? 'selected' : ''}>Grain / Cereal</option>
                  <option value="Pulse" ${existing?.category === 'Pulse' ? 'selected' : ''}>Pulse</option>
                  <option value="Spice" ${existing?.category === 'Spice' ? 'selected' : ''}>Spice</option>
                  <option value="Oilseed" ${existing?.category === 'Oilseed' ? 'selected' : ''}>Oilseed</option>
                  <option value="Horticulture" ${existing?.category === 'Horticulture' ? 'selected' : ''}>Horticulture</option>
                </select>
              </div>
            </div>

            <div class="form-grid-3" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 10px;">
              <div class="form-group">
                <label class="form-label">Harvest Date & Time <span class="req">*</span></label>
                <input type="datetime-local" class="form-input" id="lot_inp_harvest_date" value="${existing?.harvest_date ? existing.harvest_date.slice(0, 16) : nowIso}" required />
              </div>
              <div class="form-group">
                <label class="form-label">Sowing Date</label>
                <input type="date" class="form-input" id="lot_inp_sowing_date" value="${existing?.sowing_date || ''}" />
              </div>
              <div class="form-group">
                <label class="form-label">Estimated Shelf-Life (Days)</label>
                <input type="number" class="form-input" id="lot_inp_shelf_life" value="${existing?.shelf_life_days || 14}" min="1" max="365" />
              </div>
            </div>
          </fieldset>

          <!-- 2. Land & Origin Traceability -->
          <fieldset style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; margin-bottom: 16px;">
            <legend style="font-size: 13px; font-weight: 800; color: #047857; padding: 0 6px;">2. Land & Origin Traceability</legend>
            <div class="form-grid-3" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
              <div class="form-group">
                <label class="form-label">Origin Plot / Land Parcel</label>
                <select class="form-select" id="lot_inp_plot">
                  <option value="">Farm Cluster / Yard (Default)</option>
                  ${plots.map(pl => `<option value="${escapeHtml(pl.plot_id)}" ${existing && existing.origin_plot_id === pl.plot_id ? 'selected' : ''}>${escapeHtml(pl.plot_name || 'Plot')} (${pl.area_acres || 0} Acres)</option>`).join('')}
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Field / Cluster Yard Location</label>
                <input type="text" class="form-input" id="lot_inp_yard" value="${escapeHtml(existing?.plot_name || 'Cluster Yard #4')}" placeholder="e.g. Cluster Yard #4" />
              </div>
              <div class="form-group">
                <label class="form-label">Soil & Irrigation Source</label>
                <select class="form-select" id="lot_inp_irrigation">
                  <option value="Drip Micro" ${existing?.irrigation_type === 'Drip Micro' ? 'selected' : ''}>Drip / Micro-Irrigation</option>
                  <option value="Rainfed" ${existing?.irrigation_type === 'Rainfed' ? 'selected' : ''}>Rainfed</option>
                  <option value="Canal / River" ${existing?.irrigation_type === 'Canal / River' ? 'selected' : ''}>Canal / River</option>
                  <option value="Borewell" ${existing?.irrigation_type === 'Borewell' ? 'selected' : ''}>Borewell</option>
                </select>
              </div>
            </div>
          </fieldset>

          <!-- 3. Quantity, Packaging & Crate Serialization -->
          <fieldset style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; margin-bottom: 16px;">
            <legend style="font-size: 13px; font-weight: 800; color: #047857; padding: 0 6px;">3. Quantity, Packaging & Crates</legend>
            <div class="form-grid-4" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;">
              <div class="form-group">
                <label class="form-label">Net Harvest Weight <span class="req">*</span></label>
                <input type="number" step="0.1" class="form-input" id="lot_inp_qty" value="${existing?.net_qty_kg || existing?.on_hand_kg || 500}" required min="0.1" oninput="calculateLotValuation()" />
              </div>
              <div class="form-group">
                <label class="form-label">Unit of Measure</label>
                <select class="form-select" id="lot_inp_unit" onchange="calculateLotValuation()">
                  <option value="Kg" ${existing?.unit === 'Kg' ? 'selected' : ''}>Kilograms (Kg)</option>
                  <option value="Quintals" ${existing?.unit === 'Quintals' ? 'selected' : ''}>Quintals (Qtl)</option>
                  <option value="Metric Tons" ${existing?.unit === 'Metric Tons' ? 'selected' : ''}>Metric Tons (MT)</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Crates / Bags Count</label>
                <input type="number" class="form-input" id="lot_inp_packages" value="${existing?.packages_count || 20}" min="1" />
              </div>
              <div class="form-group">
                <label class="form-label">Packaging Material</label>
                <select class="form-select" id="lot_inp_package_type">
                  <option value="Plastic Crates" ${existing?.package_type === 'Plastic Crates' ? 'selected' : ''}>Plastic Crates (Standard)</option>
                  <option value="Jute Bags" ${existing?.package_type === 'Jute Bags' ? 'selected' : ''}>Jute Gunny Bags</option>
                  <option value="Corrugated Boxes" ${existing?.package_type === 'Corrugated Boxes' ? 'selected' : ''}>Corrugated Paper Cartons</option>
                  <option value="Bulk Loose" ${existing?.package_type === 'Bulk Loose' ? 'selected' : ''}>Bulk Loose Vehicle</option>
                </select>
              </div>
            </div>
          </fieldset>

          <!-- 4. Quality, Grade & Farming Inputs -->
          <fieldset style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; margin-bottom: 16px;">
            <legend style="font-size: 13px; font-weight: 800; color: #047857; padding: 0 6px;">4. Quality Grade & Inputs</legend>
            <div class="form-grid-3" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
              <div class="form-group">
                <label class="form-label">Produce Grade</label>
                <select class="form-select" id="lot_inp_grade">
                  <option value="Grade A" ${existing?.grade === 'Grade A' ? 'selected' : ''}>Grade A (Premium Commercial)</option>
                  <option value="Grade B" ${existing?.grade === 'Grade B' ? 'selected' : ''}>Grade B (Standard Market)</option>
                  <option value="Grade C" ${existing?.grade === 'Grade C' ? 'selected' : ''}>Grade C (Processing / Economy)</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Farming Method</label>
                <select class="form-select" id="lot_inp_method">
                  <option value="Organic NPOP" ${existing?.farming_method === 'Organic NPOP' ? 'selected' : ''}>Organic (Certified NPOP)</option>
                  <option value="PGS-India" ${existing?.farming_method === 'PGS-India' ? 'selected' : ''}>PGS-India Natural</option>
                  <option value="Good Agri Practices" ${existing?.farming_method === 'Good Agri Practices' ? 'selected' : ''}>GAP Certified</option>
                  <option value="Conventional" ${existing?.farming_method === 'Conventional' ? 'selected' : ''}>Conventional</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Moisture Content (%)</label>
                <input type="number" step="0.1" class="form-input" id="lot_inp_moisture" value="${existing?.moisture_pct || 11.5}" />
              </div>
            </div>
            <div style="margin-top: 10px;">
              <label class="form-label">Fertilizers / Amendments Used</label>
              <input type="text" class="form-input" id="lot_inp_fertilizers" value="${escapeHtml(existing?.fertilizers || 'Vermicompost, Neem Cake, Bio-fertilizer')}" placeholder="e.g. Vermicompost, Neem Cake, Trichoderma" />
            </div>
          </fieldset>

          <!-- 5. Commercials, Pricing & Payment Details -->
          <fieldset style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; margin-bottom: 16px;">
            <legend style="font-size: 13px; font-weight: 800; color: #047857; padding: 0 6px;">5. Commercial Valuation & Payment Details</legend>
            <div class="form-grid-3" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
              <div class="form-group">
                <label class="form-label">Expected Base Price (₹)</label>
                <input type="number" step="0.5" class="form-input" id="lot_inp_price" value="${existing?.base_price_per_unit || 25.0}" oninput="calculateLotValuation()" />
              </div>
              <div class="form-group">
                <label class="form-label">Estimated Lot Valuation (₹)</label>
                <input type="number" step="1" class="form-input" id="lot_inp_valuation" value="${existing?.estimated_value || 12500}" readonly style="background: #f8fafc; font-weight: 800; color: #047857;" />
              </div>
              <div class="form-group">
                <label class="form-label">Payment / Settlement Status</label>
                <select class="form-select" id="lot_inp_payment">
                  <option value="PENDING" ${existing?.payment_status === 'PENDING' ? 'selected' : ''}>Pending Settlement</option>
                  <option value="ADVANCE" ${existing?.payment_status === 'ADVANCE' ? 'selected' : ''}>Advance Received</option>
                  <option value="SETTLED" ${existing?.payment_status === 'SETTLED' ? 'selected' : ''}>Fully Settled</option>
                </select>
              </div>
            </div>
            <div style="margin-top: 10px;">
              <label class="form-label">Intended Buyer / Distribution Channel</label>
              <select class="form-select" id="lot_inp_buyer">
                <option value="APMC Mandi Aggregator" ${existing?.intended_buyer === 'APMC Mandi Aggregator' ? 'selected' : ''}>APMC Mandi Aggregator (Auction)</option>
                <option value="Direct Retailer" ${existing?.intended_buyer === 'Direct Retailer' ? 'selected' : ''}>Direct Retailer / Supermarket</option>
                <option value="Cold Storage Warehouse" ${existing?.intended_buyer === 'Cold Storage Warehouse' ? 'selected' : ''}>Cold Storage Terminal</option>
                <option value="Food Processing Unit" ${existing?.intended_buyer === 'Food Processing Unit' ? 'selected' : ''}>Food Processing Company</option>
              </select>
            </div>
          </fieldset>

          <!-- 6. Remarks & Statutory Attestation -->
          <div class="form-group" style="margin-bottom: 16px;">
            <label class="form-label">Farmer Remarks & Quality Notes</label>
            <textarea class="form-input" id="lot_inp_remarks" rows="2" placeholder="Early morning harvest, sorted and washed.">${escapeHtml(existing?.remarks || '')}</textarea>
          </div>

          <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; border-top: 1.5px solid #e2e8f0; padding-top: 16px;">
            <button type="button" class="btn-wizard-action btn-wizard-draft" onclick="closeHarvestLotModal()">Cancel</button>
            <button type="submit" class="btn-wizard-action btn-wizard-submit" style="padding: 10px 24px; font-weight: 800;">
              <span>${getIcon('check', 14, '#ffffff')}</span> <span>${isEdit ? 'Save Changes' : 'Confirm & Mint Harvest Lot'}</span>
            </button>
          </div>
        </form>
      </div>
    `;
    modal.style.display = 'flex';
  };

  window.closeHarvestLotModal = function () {
    const modal = document.getElementById('harvestLotModal');
    if (modal) modal.style.display = 'none';
  };

  window.calculateLotValuation = function () {
    const qty = parseFloat(document.getElementById('lot_inp_qty')?.value || 0);
    const price = parseFloat(document.getElementById('lot_inp_price')?.value || 0);
    const valEl = document.getElementById('lot_inp_valuation');
    if (valEl) valEl.value = Math.round(qty * price);
  };

  window.submitHarvestLotForm = async function (e, lotCode) {
    e.preventDefault();
    const isEdit = !!lotCode;
    const crop = document.getElementById('lot_inp_crop')?.value;
    const variety = document.getElementById('lot_inp_variety')?.value;
    const category = document.getElementById('lot_inp_category')?.value;
    const harvestDate = document.getElementById('lot_inp_harvest_date')?.value;
    const sowingDate = document.getElementById('lot_inp_sowing_date')?.value;
    const shelfLife = parseInt(document.getElementById('lot_inp_shelf_life')?.value || 14);
    const plotId = document.getElementById('lot_inp_plot')?.value || null;
    const yard = document.getElementById('lot_inp_yard')?.value;
    const irrigation = document.getElementById('lot_inp_irrigation')?.value;
    const qty = parseFloat(document.getElementById('lot_inp_qty')?.value);
    const unit = document.getElementById('lot_inp_unit')?.value;
    const packages = parseInt(document.getElementById('lot_inp_packages')?.value || 1);
    const packageType = document.getElementById('lot_inp_package_type')?.value;
    const grade = document.getElementById('lot_inp_grade')?.value;
    const method = document.getElementById('lot_inp_method')?.value;
    const moisture = parseFloat(document.getElementById('lot_inp_moisture')?.value || 0);
    const fertilizers = document.getElementById('lot_inp_fertilizers')?.value;
    const price = parseFloat(document.getElementById('lot_inp_price')?.value || 0);
    const valuation = parseFloat(document.getElementById('lot_inp_valuation')?.value || 0);
    const paymentStatus = document.getElementById('lot_inp_payment')?.value;
    const buyer = document.getElementById('lot_inp_buyer')?.value;
    const remarks = document.getElementById('lot_inp_remarks')?.value;

    const payload = {
      crop,
      product: { name: crop, variety, category },
      variety,
      category,
      harvest_date: harvestDate,
      sowing_date: sowingDate,
      shelf_life_days: shelfLife,
      origin_plot_id: plotId,
      plot_id: plotId,
      plot_name: yard,
      irrigation_type: irrigation,
      net_qty_kg: qty,
      unit,
      packages_count: packages,
      package_type: packageType,
      grade,
      farming_method: method,
      moisture_pct: moisture,
      fertilizers,
      base_price_per_unit: price,
      estimated_value: valuation,
      payment_status: paymentStatus,
      intended_buyer: buyer,
      remarks
    };

    try {
      const url = isEdit ? `/api/v1/lots/${encodeURIComponent(lotCode)}` : '/api/v1/lots/';
      const methodHttp = isEdit ? 'PUT' : 'POST';
      const res = await fetch(url, {
        method: methodHttp,
        headers: Object.assign({}, getAuthHeader(), { 'Content-Type': 'application/json' }),
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const err = await res.json();
        alert(err.detail || 'Failed to save harvest lot.');
        return;
      }

      closeHarvestLotModal();
      showToast(isEdit ? 'Harvest lot updated successfully.' : 'New harvest lot registered and signed into ledger.', 'success');
      await loadProducerLots();
    } catch (err) {
      alert('Network error while saving harvest lot.');
    }
  };

  /* --------------------------------------------------------------------------
     UNLIMITED QR CODE LABEL PRINTING & DOWNLOAD MODAL
     -------------------------------------------------------------------------- */
  window.openUnlimitedQrPrintModal = function (lotCode, cropName, variety, weightDisplay) {
    let modal = document.getElementById('unlimitedQrModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'unlimitedQrModal';
      modal.className = 'wizard-modal-backdrop';
      modal.style.cssText = 'position: fixed; inset: 0; background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(4px); z-index: 99999; display: flex; align-items: center; justify-content: center; padding: 16px;';
      document.body.appendChild(modal);
    }

    const orgName = wizardState.profile?.organisation_name || 'AnnaSutra Verified Producer';
    const qrUrl = `${window.location.origin}/l/${encodeURIComponent(lotCode)}`;

    modal.innerHTML = `
      <div style="background: #ffffff; border-radius: 16px; max-width: 680px; width: 100%; max-height: 90vh; overflow-y: auto; padding: 26px;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 14px; margin-bottom: 18px;">
          <div>
            <h3 style="margin: 0; font-size: 19px; font-weight: 800; color: #0b3d2e;">Generate & Print Crate QR Labels</h3>
            <span style="font-size: 12.5px; color: #64748b;">Unlimited QR issuance for Lot #${escapeHtml(lotCode)}. Print on standard sticker sheets.</span>
          </div>
          <button type="button" onclick="document.getElementById('unlimitedQrModal').style.display='none'" style="background: #f1f5f9; border: none; font-size: 18px; width: 32px; height: 32px; border-radius: 50%; cursor: pointer;">&times;</button>
        </div>

        <div style="display: flex; gap: 12px; align-items: center; margin-bottom: 16px; background: #f8fafc; padding: 12px 16px; border-radius: 10px;">
          <label style="font-size: 13px; font-weight: 700; color: #334155;">Quantity of Labels to Print:</label>
          <select id="qr_print_count" class="form-select" style="width: 140px; background: #fff;" onchange="renderQrStickersPreview('${lotCode}', '${escapeHtml(cropName)}', '${escapeHtml(variety)}', '${escapeHtml(weightDisplay)}')">
            <option value="1">1 Sticker</option>
            <option value="6" selected>6 Stickers (1 Sheet)</option>
            <option value="12">12 Stickers</option>
            <option value="24">24 Stickers</option>
            <option value="48">48 Stickers</option>
            <option value="100">100 Stickers</option>
          </select>
          <span style="font-size: 12px; color: #047857; font-weight: 700;">Zero QR Limits • Instant Generator</span>
        </div>

        <!-- Preview Sheet Area -->
        <div id="qrStickersPreviewContainer" style="border: 1px solid #cbd5e1; border-radius: 10px; padding: 16px; max-height: 380px; overflow-y: auto; background: #f1f5f9; display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 18px; border-top: 1.5px solid #e2e8f0; padding-top: 14px;">
          <button type="button" class="btn-wizard-action btn-wizard-draft" onclick="document.getElementById('unlimitedQrModal').style.display='none'">Close</button>
          <button type="button" class="btn-wizard-action btn-wizard-submit" style="padding: 10px 22px; font-weight: 800;" onclick="window.print()">
            <span>${getIcon('printer', 15, '#ffffff')}</span> <span>Print Labels</span>
          </button>
        </div>
      </div>
    `;

    modal.style.display = 'flex';
    renderQrStickersPreview(lotCode, cropName, variety, weightDisplay);
  };

  function renderQrStickersPreview(lotCode, cropName, variety, weightDisplay) {
    const container = document.getElementById('qrStickersPreviewContainer');
    if (!container) return;
    const count = parseInt(document.getElementById('qr_print_count')?.value || 6);
    const orgName = wizardState.profile?.organisation_name || 'AnnaSutra Producer';
    const qrTargetUrl = `${window.location.origin}/l/${encodeURIComponent(lotCode)}`;

    let html = '';
    for (let i = 1; i <= count; i++) {
      html += `
        <div style="background: #ffffff; border: 1.5px solid #0b3d2e; border-radius: 8px; padding: 10px; display: flex; gap: 10px; align-items: center;">
          <div style="width: 72px; height: 72px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
            <img src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=${encodeURIComponent(qrTargetUrl)}" alt="QR" style="width: 64px; height: 64px;" />
          </div>
          <div style="flex: 1; overflow: hidden;">
            <div style="font-size: 9.5px; font-weight: 800; color: #047857; text-transform: uppercase; letter-spacing: 0.5px;">National Traceability C-DAC</div>
            <div style="font-size: 13px; font-weight: 800; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${escapeHtml(cropName)} ${variety ? `• ${escapeHtml(variety)}` : ''}</div>
            <div style="font-family: monospace; font-size: 11.5px; font-weight: 900; color: #0b3d2e;">${escapeHtml(lotCode)}</div>
            <div style="font-size: 10px; color: #64748b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${escapeHtml(orgName)} • #${i}</div>
          </div>
        </div>
      `;
    }
    container.innerHTML = html;
  }

  /* --------------------------------------------------------------------------
     ADMIN TRASH & CONFIRMATION MECHANISM
     -------------------------------------------------------------------------- */
  window.openDeleteProducerModal = function (entityId, entityName, isPurge) {
    const t = getI18n();
    let modal = document.getElementById('adminDeleteConfirmModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'adminDeleteConfirmModal';
      modal.className = 'wizard-modal-backdrop';
      modal.style.cssText = 'position: fixed; inset: 0; background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(4px); z-index: 999999; display: flex; align-items: center; justify-content: center; padding: 16px;';
      document.body.appendChild(modal);
    }

    modal.innerHTML = `
      <div style="background: #ffffff; border-radius: 16px; max-width: 520px; width: 100%; padding: 26px; border: 2px solid ${isPurge ? '#7f1d1d' : '#dc2626'}; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
          <div style="width: 40px; height: 40px; background: #fee2e2; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
            ${getIcon('alert', 22, '#dc2626')}
          </div>
          <div>
            <h3 style="margin: 0; font-size: 18px; font-weight: 800; color: #991b1b;">
              ${isPurge ? 'Permanent Producer Purge' : 'Move Producer to Trash'}
            </h3>
            <span style="font-size: 12px; color: #64748b;">${escapeHtml(entityName)}</span>
          </div>
        </div>

        <p style="font-size: 13.5px; color: #334155; line-height: 1.5; margin-bottom: 16px;">
          ${isPurge ? `
            <strong>DANGER:</strong> This action is permanent and cannot be reversed. All KYC documents, plots, and sensitive records for <strong>${escapeHtml(entityName)}</strong> will be wiped.
          ` : `
            This producer will be moved to the <strong>Admin Trash</strong>. Their sovereign code access will be suspended immediately. You can restore them anytime from the Trash tab.
          `}
        </p>

        <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 10px; padding: 14px; margin-bottom: 18px;">
          <label style="display: block; font-size: 12.5px; font-weight: 800; color: #991b1b; margin-bottom: 6px;">
            ${escapeHtml(t.confirmDeletePrompt || 'To confirm, type DELETE in capital letters below:')}
          </label>
          <input type="text" id="inp_del_word_confirm" class="form-input" style="font-family: monospace; font-size: 14px; font-weight: 800; text-transform: uppercase; border-color: #f87171;" placeholder="DELETE" oninput="checkDeleteWordConfirm(this, '${isPurge ? 'PURGE' : 'TRASH'}')" />
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 10px;">
          <button type="button" class="btn-wizard-action btn-wizard-draft" onclick="document.getElementById('adminDeleteConfirmModal').style.display='none'">Cancel</button>
          <button type="button" id="btn_admin_exec_delete" class="btn-wizard-action" style="color: #ffffff; background: #94a3b8; border-color: #94a3b8; cursor: not-allowed; font-weight: 800;" disabled onclick="executeAdminProducerDeletion('${entityId}', ${isPurge})">
            ${isPurge ? 'Permanently Purge Data' : 'Confirm Move to Trash'}
          </button>
        </div>
      </div>
    `;

    modal.style.display = 'flex';
  };

  window.checkDeleteWordConfirm = function (input, mode) {
    const val = input.value.trim().toUpperCase();
    const btn = document.getElementById('btn_admin_exec_delete');
    if (!btn) return;
    if (val === 'DELETE') {
      btn.disabled = false;
      btn.style.background = '#dc2626';
      btn.style.borderColor = '#b91c1c';
      btn.style.cursor = 'pointer';
    } else {
      btn.disabled = true;
      btn.style.background = '#94a3b8';
      btn.style.borderColor = '#94a3b8';
      btn.style.cursor = 'not-allowed';
    }
  };

  window.executeAdminProducerDeletion = async function (entityId, isPurge) {
    const modal = document.getElementById('adminDeleteConfirmModal');
    try {
      if (isPurge) {
        const res = await fetch(`/api/v1/admin/entities/${entityId}/purge`, {
          method: 'POST',
          headers: Object.assign({}, getAuthHeader(), { 'Content-Type': 'application/json' }),
          body: JSON.stringify({ confirmation: 'DELETE' })
        });
        if (!res.ok) {
          const err = await res.json();
          alert(err.detail || 'Failed to purge producer.');
          return;
        }
        showToast('Producer data permanently purged.', 'success');
      } else {
        const res = await fetch(`/api/v1/admin/entities/${entityId}/decision`, {
          method: 'POST',
          headers: Object.assign({}, getAuthHeader(), { 'Content-Type': 'application/json' }),
          body: JSON.stringify({ decision: 'TRASH', reason: 'Moved to trash by administrator.' })
        });
        if (!res.ok) {
          const err = await res.json();
          alert(err.detail || 'Failed to move producer to trash.');
          return;
        }
        showToast('Producer moved to trash successfully.', 'success');
      }

      if (modal) modal.style.display = 'none';
      wizardState.adminInspectedEntity = null;
      const contentArea = document.getElementById('workspaceDynamicContent');
      if (contentArea) await loadAdminQueueAndRender(contentArea);
    } catch (err) {
      alert('Network error while processing deletion.');
    }
  };

  window.restoreAdminProducer = async function (entityId) {
    try {
      const res = await fetch(`/api/v1/admin/entities/${entityId}/restore`, {
        method: 'POST',
        headers: getAuthHeader()
      });
      if (res.ok) {
        showToast('Producer restored successfully from Trash.', 'success');
        wizardState.adminInspectedEntity = null;
        const contentArea = document.getElementById('workspaceDynamicContent');
        if (contentArea) await loadAdminQueueAndRender(contentArea);
      } else {
        const err = await res.json();
        alert(err.detail || 'Failed to restore producer.');
      }
    } catch (e) {
      alert('Network error while restoring producer.');
    }
  };

  window.openQuickDispatchModal = function (lotCode, cropName, maxQty) {
    const qty = prompt(`Dispatch Lot #${lotCode} (${cropName}): Enter dispatch quantity in Kg (Max: ${maxQty} Kg):`, maxQty);
    if (!qty) return;
    const qtyNum = parseFloat(qty);
    if (isNaN(qtyNum) || qtyNum <= 0 || qtyNum > maxQty) {
      alert('Invalid dispatch quantity.');
      return;
    }
    const receiver = prompt('Enter Destination APMC Mandi / Buyer Name:', 'Hooghly APMC Aggregator Yard');
    if (!receiver) return;

    fetch(`/api/v1/lots/${encodeURIComponent(lotCode)}/dispatch`, {
      method: 'POST',
      headers: Object.assign({}, getAuthHeader(), { 'Content-Type': 'application/json' }),
      body: JSON.stringify({ declared_qty_kg: qtyNum, destination_name: receiver })
    }).then(async res => {
      if (res.ok) {
        showToast(`Lot #${lotCode} successfully dispatched to ${receiver}. Custody locked.`, 'success');
        await loadProducerLots();
      } else {
        const err = await res.json();
        alert(err.detail || 'Failed to dispatch lot.');
      }
    }).catch(() => alert('Network error during dispatch.'));
  };
"""

# Replace the old renderVerifiedOperationalConsole
old_verified_console = re.search(r"  async function renderVerifiedOperationalConsole\(container\) \{[\s\S]*?window\.downloadMyQrPdfSheet = async function \(\) \{", js)
if old_verified_console:
    js = js[:old_verified_console.start()] + harvest_console_code.strip() + "\n\n  window.downloadMyQrPdfSheet = async function () {" + js[old_verified_console.end():]
    print("renderVerifiedOperationalConsole replaced with full Harvest Lot Management & Admin Trash")

# Write out to backend static
with open(src_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(js)

# Also synchronize to static/ and staticfiles/
dest1 = "static/publicview/js/producer_wizard.js"
dest2 = "staticfiles/publicview/js/producer_wizard.js"

if os.path.exists("static/publicview/js"):
    shutil.copy2(src_path, dest1)
    print(f"Copied to {dest1}")

if os.path.exists("staticfiles/publicview/js"):
    shutil.copy2(src_path, dest2)
    print(f"Copied to {dest2}")

print("All static locations synchronized successfully!")
