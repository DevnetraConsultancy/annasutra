"""
Full script to integrate Dual-Tab Producer Console and the 4-Chart Harvest Lot Analytics Dashboard into producer_wizard.js.
"""
import os
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
js_path = os.path.join(BASE_DIR, 'backend', 'apps', 'publicview', 'static', 'publicview', 'js', 'producer_wizard.js')

with open(js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update renderVerifiedOperationalConsole template to include the dual tab bar and two containers
old_console_markup = """        <!-- Quick Metrics Row -->
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
        </div>"""

new_console_markup = """        <!-- Dual-Tab Navigation Bar -->
        <div style="display: flex; gap: 6px; border-bottom: 2px solid #e2e8f0; margin-bottom: 22px;">
          <button type="button" id="tabBtnLedger" onclick="window.switchProducerConsoleTab('ledger')" style="padding: 11px 22px; font-size: 13.5px; font-weight: 800; border: none; border-bottom: 3px solid #047857; background: #ecfdf5; color: #065f46; border-radius: 8px 8px 0 0; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; transition: all 0.2s;">
            <span>${getIcon('sprout', 16, '#047857')}</span> <span>${escapeHtml(t.tabHarvestLedger || 'Harvest Lots & Custody Ledger')}</span>
          </button>
          <button type="button" id="tabBtnAnalytics" onclick="window.switchProducerConsoleTab('analytics')" style="padding: 11px 22px; font-size: 13.5px; font-weight: 800; border: none; border-bottom: 3px solid transparent; background: transparent; color: #64748b; border-radius: 8px 8px 0 0; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; transition: all 0.2s;">
            <span>${getIcon('activity', 16, '#64748b')}</span> <span>${escapeHtml(t.tabAnalytics || 'Analytics & Farm Insights')}</span>
          </button>
        </div>

        <!-- TAB 1: Harvest Lots & Custody Ledger -->
        <div id="consoleTabContentLedger" style="display: block;">
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

        <!-- TAB 2: Analytics & Farm Insights -->
        <div id="consoleTabContentAnalytics" style="display: none;">
          <!-- Analytics Toolbar -->
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 20px; padding-bottom: 14px; border-bottom: 1px solid #f1f5f9;">
            <div>
              <h4 style="margin: 0; font-size: 17px; font-weight: 800; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                <span>${getIcon('activity', 20, '#047857')}</span> <span>${escapeHtml(t.tabAnalytics || 'Analytics & Farm Insights')}</span>
              </h4>
              <p style="margin: 3px 0 0; font-size: 12.5px; color: #64748b;">Real-time yield analytics, crop valuation, custody velocity, and settlement audit.</p>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <select id="analytics_period_filter" class="form-select" style="background: #fff; font-size: 12px; font-weight: 700; padding: 6px 12px;" onchange="renderProducerAnalytics()">
                <option value="ALL">${escapeHtml(t.periodAllLots || 'All Recorded Lots')}</option>
                <option value="30">${escapeHtml(t.periodLast30 || 'Last 30 Days')}</option>
                <option value="90">${escapeHtml(t.periodLast90 || 'Last 90 Days')}</option>
                <option value="SEASON">${escapeHtml(t.periodSeason || 'Current Season (Rabi 2026-27)')}</option>
              </select>
            </div>
          </div>

          <!-- Analytics Container Render Target -->
          <div id="producerAnalyticsRoot">
            <div style="text-align: center; padding: 40px; color: #64748b;">
              <div style="width: 28px; height: 28px; border: 2.5px solid #cbd5e1; border-top-color: #047857; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 12px;"></div>
              <span>Aggregating ledger yield and valuation telemetry...</span>
            </div>
          </div>
        </div>"""

content = content.replace(old_console_markup, new_console_markup)

# 2. Add the complete Analytics generation engine functions at the bottom before closing tag
analytics_engine_js = """
  /* --------------------------------------------------------------------------
     PRODUCER HARVEST LOT ANALYTICS & STATISTICAL VISUALIZATION ENGINE
     -------------------------------------------------------------------------- */
  window._analyticsDonutMode = 'weight'; // 'weight' or 'value'

  window.switchProducerConsoleTab = function (tabName) {
    const tabLedgerBtn = document.getElementById('tabBtnLedger');
    const tabAnalyticsBtn = document.getElementById('tabBtnAnalytics');
    const contentLedger = document.getElementById('consoleTabContentLedger');
    const contentAnalytics = document.getElementById('consoleTabContentAnalytics');

    if (!tabLedgerBtn || !tabAnalyticsBtn || !contentLedger || !contentAnalytics) return;

    if (tabName === 'ledger') {
      tabLedgerBtn.style.color = '#065f46';
      tabLedgerBtn.style.borderBottom = '3px solid #047857';
      tabLedgerBtn.style.background = '#ecfdf5';

      tabAnalyticsBtn.style.color = '#64748b';
      tabAnalyticsBtn.style.borderBottom = '3px solid transparent';
      tabAnalyticsBtn.style.background = 'transparent';

      contentLedger.style.display = 'block';
      contentAnalytics.style.display = 'none';
    } else {
      tabAnalyticsBtn.style.color = '#065f46';
      tabAnalyticsBtn.style.borderBottom = '3px solid #047857';
      tabAnalyticsBtn.style.background = '#ecfdf5';

      tabLedgerBtn.style.color = '#64748b';
      tabLedgerBtn.style.borderBottom = '3px solid transparent';
      tabLedgerBtn.style.background = 'transparent';

      contentLedger.style.display = 'none';
      contentAnalytics.style.display = 'block';
      renderProducerAnalytics();
    }
  };

  window.setAnalyticsDonutMode = function (mode) {
    window._analyticsDonutMode = mode;
    renderProducerAnalytics();
  };

  window.renderProducerAnalytics = function () {
    const root = document.getElementById('producerAnalyticsRoot');
    if (!root) return;
    const t = getI18n();

    const lots = window._producerLots || [];
    if (!lots || lots.length === 0) {
      root.innerHTML = `
        <div style="background: #f8fafc; border: 1.5px dashed #cbd5e1; border-radius: 16px; padding: 48px 24px; text-align: center;">
          <div style="width: 56px; height: 56px; background: #ecfdf5; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px;">
            ${getIcon('sprout', 28, '#047857')}
          </div>
          <h4 style="margin: 0 0 8px; font-size: 18px; font-weight: 800; color: #0f172a;">${escapeHtml(t.noAnalyticsLots || 'No harvest lots recorded yet.')}</h4>
          <p style="margin: 0 auto 20px; font-size: 13.5px; color: #64748b; max-width: 440px;">
            Register your harvest batches to automatically generate yield distribution charts, monthly harvest cadence trends, and commercial cashflow graphs.
          </p>
          <button type="button" class="btn-wizard-action btn-wizard-submit" style="padding: 10px 22px; font-weight: 800;" onclick="switchProducerConsoleTab('ledger'); openHarvestLotModal(null);">
            + ${escapeHtml(t.btnRegisterLot || 'Register New Harvest Lot')}
          </button>
        </div>
      `;
      return;
    }

    // 1. KPI Statistics Computations
    let totalWeight = 0;
    let totalValuation = 0;
    let realizedRevenue = 0;
    let gradeACount = 0;
    let inCustodyCount = 0;
    let inCustodyWeight = 0;
    let inTransitCount = 0;
    let deliveredCount = 0;
    let closedCount = 0;

    const cropMap = {}; // { cropName: { weight, value, count } }
    const paymentMap = { FULLY_PAID: 0, ADVANCE_PAID: 0, ESCROW_LOCKED: 0, UNPAID: 0 };
    const timelineMap = {}; // { dateKey: weight }

    lots.forEach(lot => {
      const wt = parseFloat(lot.net_qty_kg || lot.on_hand_kg || 0) || 0;
      const val = parseFloat(lot.estimated_value || 0) || 0;
      totalWeight += wt;
      totalValuation += val;

      // Grade A ratio
      const gr = (lot.quality_grade || lot.grade || '').toUpperCase();
      if (gr === 'GRADE_A' || gr.includes('A')) gradeACount++;

      // Custody state
      const st = (lot.state || 'IN_CUSTODY').toUpperCase();
      if (st === 'IN_CUSTODY' || st === 'CREATED') {
        inCustodyCount++;
        inCustodyWeight += wt;
      } else if (st === 'IN_TRANSIT') {
        inTransitCount++;
      } else if (st === 'DELIVERED') {
        deliveredCount++;
      } else if (st === 'CLOSED' || st === 'TRANSFERRED') {
        closedCount++;
      }

      // Payment Settlement
      const pay = (lot.payment_status || 'UNPAID').toUpperCase();
      if (pay === 'SETTLED' || pay === 'FULLY_PAID') {
        realizedRevenue += val;
        paymentMap.FULLY_PAID += val;
      } else if (pay === 'ADVANCE' || pay === 'ADVANCE_PAID') {
        realizedRevenue += (val * 0.5);
        paymentMap.ADVANCE_PAID += val;
      } else if (pay === 'ESCROW_LOCKED') {
        paymentMap.ESCROW_LOCKED += val;
      } else {
        paymentMap.UNPAID += val;
      }

      // Crop aggregation
      const cropName = lot.crop || 'Produce';
      if (!cropMap[cropName]) cropMap[cropName] = { weight: 0, value: 0, count: 0 };
      cropMap[cropName].weight += wt;
      cropMap[cropName].value += val;
      cropMap[cropName].count += 1;

      // Timeline aggregation
      const d = (lot.harvest_date || lot.created_at || '').substring(0, 10);
      if (d) {
        timelineMap[d] = (timelineMap[d] || 0) + wt;
      }
    });

    const gradeAPct = lots.length > 0 ? ((gradeACount / lots.length) * 100).toFixed(1) : 0;
    const avgPricePerKg = totalWeight > 0 ? (totalValuation / totalWeight).toFixed(1) : 0;

    // Palette for charts
    const PALETTE = ['#047857', '#10b981', '#f59e0b', '#3b82f6', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

    // 2. Prepare Donut Slices
    const isWeightMode = window._analyticsDonutMode === 'weight';
    const donutSlices = Object.keys(cropMap).map((k, idx) => ({
      label: getCropLabel(k),
      value: isWeightMode ? cropMap[k].weight : cropMap[k].value,
      color: PALETTE[idx % PALETTE.length],
      rawCrop: k
    })).sort((a, b) => b.value - a.value);

    const donutSvg = generateSvgDonut(donutSlices, isWeightMode ? totalWeight : totalValuation, isWeightMode ? 'Kg' : '₹');

    // 3. Prepare Timeline Points
    const sortedDates = Object.keys(timelineMap).sort();
    const timelinePoints = sortedDates.slice(-7).map(d => {
      const parts = d.split('-');
      const label = parts.length === 3 ? `${parts[2]}/${parts[1]}` : d;
      return { date: d, label: label, qty: timelineMap[d] };
    });
    const timelineSvg = generateSvgTimeline(timelinePoints);

    // 4. Custody Stages
    const custodyStages = [
      { name: 'In Farm Custody', count: inCustodyCount, color: '#10b981', weight: inCustodyWeight, pct: totalWeight > 0 ? ((inCustodyWeight / totalWeight) * 100).toFixed(1) : 0 },
      { name: 'In Transit (Locked)', count: inTransitCount, color: '#f59e0b', weight: 0, pct: lots.length > 0 ? ((inTransitCount / lots.length) * 100).toFixed(1) : 0 },
      { name: 'Delivered to Mandi / Hub', count: deliveredCount, color: '#3b82f6', weight: 0, pct: lots.length > 0 ? ((deliveredCount / lots.length) * 100).toFixed(1) : 0 },
      { name: 'Transferred / Custody Closed', count: closedCount, color: '#64748b', weight: 0, pct: lots.length > 0 ? ((closedCount / lots.length) * 100).toFixed(1) : 0 }
    ];

    root.innerHTML = `
      <!-- 6 High-Impact Stat Tiles -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 24px;">
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px; border-radius: 12px;">
          <div style="font-size: 11.5px; color: #64748b; font-weight: 700; text-transform: uppercase;">Total Harvest Volume</div>
          <div style="font-size: 22px; font-weight: 900; color: #0b3d2e; margin: 4px 0;">${totalWeight.toLocaleString('en-IN', { maximumFractionDigits: 1 })} Kg</div>
          <div style="font-size: 11px; color: #059669; font-weight: 600;">${(totalWeight / 100).toFixed(1)} Quintals recorded</div>
        </div>

        <div style="background: #ecfdf5; border: 1.5px solid #a7f3d0; padding: 14px; border-radius: 12px;">
          <div style="font-size: 11.5px; color: #065f46; font-weight: 700; text-transform: uppercase;">Gross Crop Valuation</div>
          <div style="font-size: 22px; font-weight: 900; color: #047857; margin: 4px 0;">₹ ${totalValuation.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
          <div style="font-size: 11px; color: #047857; font-weight: 600;">Across ${lots.length} harvest lots</div>
        </div>

        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 14px; border-radius: 12px;">
          <div style="font-size: 11.5px; color: #166534; font-weight: 700; text-transform: uppercase;">Realized Revenue</div>
          <div style="font-size: 22px; font-weight: 900; color: #15803d; margin: 4px 0;">₹ ${realizedRevenue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
          <div style="font-size: 11px; color: #16a34a; font-weight: 600;">Settled & Advance funds</div>
        </div>

        <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px; border-radius: 12px;">
          <div style="font-size: 11.5px; color: #64748b; font-weight: 700; text-transform: uppercase;">Grade A Quality Ratio</div>
          <div style="font-size: 22px; font-weight: 900; color: #0b3d2e; margin: 4px 0;">${gradeAPct}%</div>
          <div style="font-size: 11px; color: #059669; font-weight: 600;">${gradeACount} of ${lots.length} Grade A lots</div>
        </div>

        <div style="background: #fffbeb; border: 1.5px solid #fde68a; padding: 14px; border-radius: 12px;">
          <div style="font-size: 11.5px; color: #92400e; font-weight: 700; text-transform: uppercase;">Active Farm Custody</div>
          <div style="font-size: 22px; font-weight: 900; color: #b45309; margin: 4px 0;">${inCustodyCount} Lots</div>
          <div style="font-size: 11px; color: #d97706; font-weight: 600;">${inCustodyWeight.toLocaleString('en-IN', { maximumFractionDigits: 0 })} Kg on farm</div>
        </div>

        <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px; border-radius: 12px;">
          <div style="font-size: 11.5px; color: #64748b; font-weight: 700; text-transform: uppercase;">Avg Realized Base Price</div>
          <div style="font-size: 22px; font-weight: 900; color: #0b3d2e; margin: 4px 0;">₹ ${avgPricePerKg} / Kg</div>
          <div style="font-size: 11px; color: #64748b; font-weight: 600;">Weighted average price</div>
        </div>
      </div>

      <!-- 4-Chart Grid (2x2) -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 18px;">
        <!-- GRAPH 1: Crop Volume & Valuation Share -->
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 8px;">
            <div>
              <h5 style="margin: 0; font-size: 15px; font-weight: 800; color: #0f172a;">${escapeHtml(t.chartCropShare || 'Crop Volume & Valuation Share')}</h5>
              <div style="font-size: 12px; color: #64748b;">Distribution of produce yield and valuation across crops</div>
            </div>
            <div style="display: flex; gap: 4px; background: #f1f5f9; padding: 3px; border-radius: 8px;">
              <button type="button" onclick="setAnalyticsDonutMode('weight')" style="border: none; padding: 4px 10px; font-size: 11.5px; font-weight: 700; border-radius: 6px; cursor: pointer; ${isWeightMode ? 'background: #ffffff; color: #047857; box-shadow: 0 1px 3px rgba(0,0,0,0.1);' : 'background: transparent; color: #64748b;'}">
                ${escapeHtml(t.btnToggleWeight || 'Weight (Kg)')}
              </button>
              <button type="button" onclick="setAnalyticsDonutMode('value')" style="border: none; padding: 4px 10px; font-size: 11.5px; font-weight: 700; border-radius: 6px; cursor: pointer; ${!isWeightMode ? 'background: #ffffff; color: #047857; box-shadow: 0 1px 3px rgba(0,0,0,0.1);' : 'background: transparent; color: #64748b;'}">
                ${escapeHtml(t.btnToggleValue || 'Value (₹)')}
              </button>
            </div>
          </div>
          
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; align-items: center;">
            <div>${donutSvg}</div>
            <div style="display: flex; flex-direction: column; gap: 8px; max-height: 240px; overflow-y: auto; padding-right: 4px;">
              ${donutSlices.map(s => `
                <div style="display: flex; align-items: center; justify-content: space-between; font-size: 12px; padding: 6px 8px; background: #f8fafc; border-radius: 6px;">
                  <span style="display: flex; align-items: center; gap: 6px; font-weight: 700; color: #334155;">
                    <span style="width: 10px; height: 10px; border-radius: 50%; background: ${s.color}; display: inline-block;"></span>
                    <span>${escapeHtml(s.label)}</span>
                  </span>
                  <span style="font-weight: 800; color: #0f172a;">${s.value.toLocaleString('en-IN', { maximumFractionDigits: 1 })} ${isWeightMode ? 'Kg' : '₹'}</span>
                </div>
              `).join('')}
            </div>
          </div>
        </div>

        <!-- GRAPH 2: Monthly Harvest Cadence Timeline -->
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
          <div style="margin-bottom: 16px;">
            <h5 style="margin: 0; font-size: 15px; font-weight: 800; color: #0f172a;">${escapeHtml(t.chartYieldTimeline || 'Harvest Yield Cadence Timeline')}</h5>
            <div style="font-size: 12px; color: #64748b;">Chronological harvest batches logged on sovereign chain</div>
          </div>
          <div>${timelineSvg}</div>
        </div>

        <!-- GRAPH 3: Custody Logistics & Sales Pipeline Flow -->
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
          <div style="margin-bottom: 16px;">
            <h5 style="margin: 0; font-size: 15px; font-weight: 800; color: #0f172a;">${escapeHtml(t.chartCustodyPipeline || 'Custody & Logistics Pipeline Flow')}</h5>
            <div style="font-size: 12px; color: #64748b;">Supply-chain transit velocity from farm genesis to mandi/retail</div>
          </div>

          <div style="display: flex; flex-direction: column; gap: 14px;">
            ${custodyStages.map(st => `
              <div>
                <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 700; margin-bottom: 4px;">
                  <span style="color: #334155;">${escapeHtml(st.name)}</span>
                  <span style="color: #0f172a;">${st.count} Lots (${st.pct}%)</span>
                </div>
                <div style="height: 10px; background: #f1f5f9; border-radius: 6px; overflow: hidden;">
                  <div style="height: 100%; width: ${Math.max(2, st.pct)}%; background: ${st.color}; border-radius: 6px; transition: width 0.5s ease;"></div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- GRAPH 4: Commercial Payment & Settlement Health -->
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
          <div style="margin-bottom: 16px;">
            <h5 style="margin: 0; font-size: 15px; font-weight: 800; color: #0f172a;">${escapeHtml(t.chartPaymentHealth || 'Commercial Payment & Settlement Health')}</h5>
            <div style="font-size: 12px; color: #64748b;">Farmer trade settlement breakdown and outstanding escrow telemetry</div>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px;">
            <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 10px; padding: 12px;">
              <div style="font-size: 11px; font-weight: 700; color: #065f46; text-transform: uppercase;">Fully Settled</div>
              <div style="font-size: 18px; font-weight: 900; color: #047857; margin-top: 2px;">₹ ${paymentMap.FULLY_PAID.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
            </div>
            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 12px;">
              <div style="font-size: 11px; font-weight: 700; color: #166534; text-transform: uppercase;">Advance Received</div>
              <div style="font-size: 18px; font-weight: 900; color: #16a34a; margin-top: 2px;">₹ ${paymentMap.ADVANCE_PAID.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
            </div>
            <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 10px; padding: 12px;">
              <div style="font-size: 11px; font-weight: 700; color: #92400e; text-transform: uppercase;">Escrow Locked</div>
              <div style="font-size: 18px; font-weight: 900; color: #b45309; margin-top: 2px;">₹ ${paymentMap.ESCROW_LOCKED.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
            </div>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px;">
              <div style="font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase;">Pending Settlement</div>
              <div style="font-size: 18px; font-weight: 900; color: #dc2626; margin-top: 2px;">₹ ${paymentMap.UNPAID.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
            </div>
          </div>

          <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; font-size: 12px; color: #475569; display: flex; justify-content: space-between; align-items: center;">
            <span>Payment Assurance Rate:</span>
            <strong style="color: #047857;">${totalValuation > 0 ? (((paymentMap.FULLY_PAID + paymentMap.ADVANCE_PAID) / totalValuation) * 100).toFixed(1) : 100}% guaranteed</strong>
          </div>
        </div>
      </div>
    `;
  };

  // Helper: SVG Donut Generator
  function generateSvgDonut(slices, totalNum, unitLabel) {
    const cx = 110, cy = 110, rOuter = 95, rInner = 60;
    const total = slices.reduce((acc, s) => acc + s.value, 0) || 1;
    let currentAngle = -90.0;
    const paths = [];

    slices.forEach(s => {
      if (s.value <= 0) return;
      let sliceAngle = (s.value / total) * 360.0;
      if (sliceAngle >= 359.9) sliceAngle = 359.9;

      const startRad = (currentAngle * Math.PI) / 180.0;
      const endRad = ((currentAngle + sliceAngle) * Math.PI) / 180.0;

      const x1Out = cx + rOuter * Math.cos(startRad);
      const y1Out = cy + rOuter * Math.sin(startRad);
      const x2Out = cx + rOuter * Math.cos(endRad);
      const y2Out = cy + rOuter * Math.sin(endRad);

      const x1In = cx + rInner * Math.cos(endRad);
      const y1In = cy + rInner * Math.sin(endRad);
      const x2In = cx + rInner * Math.cos(startRad);
      const y2In = cy + rInner * Math.sin(startRad);

      const largeArc = sliceAngle > 180 ? 1 : 0;
      const d = `M ${x1Out.toFixed(1)} ${y1Out.toFixed(1)} A ${rOuter} ${rOuter} 0 ${largeArc} 1 ${x2Out.toFixed(1)} ${y2Out.toFixed(1)} L ${x1In.toFixed(1)} ${y1In.toFixed(1)} A ${rInner} ${rInner} 0 ${largeArc} 0 ${x2In.toFixed(1)} ${y2In.toFixed(1)} Z`;
      const pct = ((s.value / total) * 100).toFixed(1);
      const tooltip = `${s.label}: ${s.value.toLocaleString('en-IN', { maximumFractionDigits: 1 })} ${unitLabel} (${pct}%)`;

      paths.push(`<path d="${d}" fill="${s.color}" stroke="#ffffff" stroke-width="2.5"><title>${escapeHtml(tooltip)}</title></path>`);
      currentAngle += sliceAngle;
    });

    return `
      <svg viewBox="0 0 220 220" width="100%" height="220" style="overflow: visible; display: block; margin: 0 auto;">
        ${paths.join('')}
        <circle cx="${cx}" cy="${cy}" r="${rInner - 2}" fill="#ffffff"/>
        <text x="${cx}" y="${cy - 4}" font-size="17" font-weight="900" fill="#0b3d2e" text-anchor="middle">${totalNum.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</text>
        <text x="${cx}" y="${cy + 14}" font-size="11" font-weight="700" fill="#64748b" text-anchor="middle">${unitLabel}</text>
      </svg>
    `;
  }

  // Helper: SVG Timeline Generator
  function generateSvgTimeline(dataPoints) {
    const w = 440, h = 190;
    const padL = 40, padR = 20, padT = 20, padB = 30;
    const pw = w - padL - padR;
    const ph = h - padT - padB;

    if (!dataPoints || dataPoints.length === 0) {
      return `<svg viewBox="0 0 ${w} ${h}" width="100%" height="${h}"><text x="${w / 2}" y="${h / 2}" fill="#94a3b8" font-size="12" text-anchor="middle">No harvest date timeline available</text></svg>`;
    }

    const maxVal = Math.max(...dataPoints.map(p => p.qty), 1);
    const maxY = maxVal * 1.25;
    const n = dataPoints.length;

    const coords = dataPoints.map((p, idx) => {
      const x = padL + (n > 1 ? (idx / (n - 1)) * pw : pw / 2);
      const y = padT + ph - (p.qty / maxY) * ph;
      return { x, y, p };
    });

    const lineParts = [`M ${coords[0].x.toFixed(1)} ${coords[0].y.toFixed(1)}`];
    for (let i = 1; i < coords.length; i++) {
      const prev = coords[i - 1];
      const curr = coords[i];
      const cx1 = prev.x + (curr.x - prev.x) / 2;
      const cx2 = cx1;
      lineParts.push(`C ${cx1.toFixed(1)} ${prev.y.toFixed(1)}, ${cx2.toFixed(1)} ${curr.y.toFixed(1)}, ${curr.x.toFixed(1)} ${curr.y.toFixed(1)}`);
    }
    const lineD = lineParts.join(' ');
    const areaD = `${lineD} L ${coords[coords.length - 1].x.toFixed(1)} ${padT + ph} L ${coords[0].x.toFixed(1)} ${padT + ph} Z`;

    const gridLines = [];
    for (let s = 0; s < 4; s++) {
      const gy = padT + (s / 3) * ph;
      const gval = maxY * (1 - s / 3);
      gridLines.push(`<line x1="${padL}" y1="${gy.toFixed(1)}" x2="${w - padR}" y2="${gy.toFixed(1)}" stroke="#f1f5f9" stroke-width="1" stroke-dasharray="3,3"/>`);
      gridLines.push(`<text x="${padL - 6}" y="${gy + 3.5}" font-size="9" fill="#94a3b8" text-anchor="end">${gval.toFixed(0)}</text>`);
    }

    const markers = coords.map(c => `
      <circle cx="${c.x.toFixed(1)}" cy="${c.y.toFixed(1)}" r="4.5" fill="#ffffff" stroke="#047857" stroke-width="2.5">
        <title>${c.p.label}: ${c.p.qty.toFixed(1)} Kg</title>
      </circle>
      <text x="${c.x.toFixed(1)}" y="${padT + ph + 16}" font-size="9.5" font-weight="600" fill="#64748b" text-anchor="middle">${c.p.label}</text>
    `);

    return `
      <svg viewBox="0 0 ${w} ${h}" width="100%" height="${h}" style="overflow: visible;">
        <defs>
          <linearGradient id="yieldAreaGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#047857" stop-opacity="0.32"/>
            <stop offset="100%" stop-color="#10b981" stop-opacity="0.02"/>
          </linearGradient>
        </defs>
        ${gridLines.join('')}
        <path d="${areaD}" fill="url(#yieldAreaGrad)"/>
        <path d="${lineD}" fill="none" stroke="#047857" stroke-width="2.8" stroke-linecap="round"/>
        ${markers.join('')}
      </svg>
    `;
  }
"""

content = content + "\n" + analytics_engine_js

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Sync to static/ and staticfiles/
shutil.copyfile(js_path, os.path.join(BASE_DIR, 'static', 'publicview', 'js', 'producer_wizard.js'))
shutil.copyfile(js_path, os.path.join(BASE_DIR, 'staticfiles', 'publicview', 'js', 'producer_wizard.js'))

print("Producer Analytics Dashboard and Dual-Tab UI successfully integrated into producer_wizard.js!")
