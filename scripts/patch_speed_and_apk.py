"""
Patch AnnaSutra for:
1. Zero-delay instant load (Stale-While-Revalidate caching + parallel fetching).
2. Android APK direct download link with downward arrow in locked footer.
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# -------------------------------------------------------------
# 1. Update backend/apps/publicview/views.py with download_apk_view
# -------------------------------------------------------------
pv_views_path = os.path.join(BASE_DIR, 'backend', 'apps', 'publicview', 'views.py')
with open(pv_views_path, 'r', encoding='utf-8') as f:
    views_code = f.read()

if 'def download_apk_view' not in views_code:
    apk_view_code = """

def download_apk_view(request):
    \"\"\"Direct download redirect for the latest AnnaSutra Android Mobile APK.\"\"\"
    from django.http import HttpResponseRedirect
    apk_url = "https://github.com/DevnetraConsultancy/annasutra/releases/download/v1.0.0/app-debug.apk"
    return HttpResponseRedirect(apk_url)
"""
    views_code += apk_view_code
    with open(pv_views_path, 'w', encoding='utf-8') as f:
        f.write(views_code)
    print("Added download_apk_view to publicview/views.py")

# -------------------------------------------------------------
# 2. Update backend/config/urls.py with /download/apk routes
# -------------------------------------------------------------
urls_path = os.path.join(BASE_DIR, 'backend', 'config', 'urls.py')
with open(urls_path, 'r', encoding='utf-8') as f:
    urls_code = f.read()

if 'download_apk_view' not in urls_code:
    urls_code = urls_code.replace(
        "from apps.publicview.views import landing_page_view, public_lot_html_view, serve_static_asset",
        "from apps.publicview.views import landing_page_view, public_lot_html_view, serve_static_asset, download_apk_view"
    )
    routes_insert = """    path("download/apk", download_apk_view, name="download_apk"),
    path("download/apk/", download_apk_view, name="download_apk_slash"),
    path("download/android", download_apk_view, name="download_android"),
    path("download/android/", download_apk_view, name="download_android_slash"),
"""
    urls_code = urls_code.replace('path("q/<str:code>/", public_lot_html_view, name="qr_short_link_slash"),',
                                  'path("q/<str:code>/", public_lot_html_view, name="qr_short_link_slash"),\n' + routes_insert)
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(urls_code)
    print("Added download routes to backend/config/urls.py")

# -------------------------------------------------------------
# 3. Update producer_wizard.js for 0ms SWR instant loading
# -------------------------------------------------------------
wiz_path = os.path.join(BASE_DIR, 'backend', 'apps', 'publicview', 'static', 'publicview', 'js', 'producer_wizard.js')
with open(wiz_path, 'r', encoding='utf-8') as f:
    wiz_code = f.read()

# Replace window.renderCurrentWorkspace with SWR implementation
old_render_ws = """  window.renderCurrentWorkspace = async function () {
    const container = document.getElementById('confinedWorkspace');
    if (!container) return;

    if (typeof currentRole !== 'undefined' && currentRole !== 'PRODUCER' && currentRole !== 'ADMIN') {
      const dynamicArea = document.getElementById('workspaceDynamicContent');
      if (dynamicArea) dynamicArea.style.display = 'none';

      const toolsGrid = document.getElementById('workspaceTools');
      const batchesList = document.getElementById('workspaceBatchesList');
      if (toolsGrid) toolsGrid.style.display = 'grid';
      if (batchesList && batchesList.parentNode) batchesList.parentNode.style.display = 'block';

      if (typeof window.renderDefaultWorkspace === 'function') {
        window.renderDefaultWorkspace();
      }
      return;
    }

    const toolsGrid = document.getElementById('workspaceTools');
    const batchesList = document.getElementById('workspaceBatchesList');
    if (toolsGrid) toolsGrid.style.display = 'none';
    if (batchesList && batchesList.parentNode) batchesList.parentNode.style.display = 'none';

    let contentArea = document.getElementById('workspaceDynamicContent');
    if (!contentArea) {
      contentArea = document.createElement('div');
      contentArea.id = 'workspaceDynamicContent';
      contentArea.style.minHeight = '350px';
      container.appendChild(contentArea);
    }
    contentArea.style.display = 'block';

    const t = getI18n();
    contentArea.innerHTML = `
      <div style="text-align: center; padding: 48px 16px;">
        <div style="width: 36px; height: 36px; border: 3px solid #cbd5e1; border-top-color: #0b3d2e; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px;"></div>
        <p style="color: #64748b; font-size: 14px; font-weight: 600;">${escapeHtml(t.loadingRegistry)}</p>
      </div>
    `;

    if (typeof currentRole !== 'undefined' && currentRole === 'ADMIN') {
      updateRegisteredHeaderBanner({ organisation_name: t.workspaceTitleAdmin });
      await loadAdminQueueAndRender(contentArea);
      return;
    }

    try {
      const res = await fetch('/api/v1/me/profile', { headers: getAuthHeader() });
      if (res.status === 401 || res.status === 403) {
        wizardState.profile = { status: 'DRAFT', role: 'PRODUCER', version: 1 };
        updateRegisteredHeaderBanner(wizardState.profile);
        renderWizardInterface(contentArea);
        return;
      }

      const data = await res.json();
      wizardState.profile = data.profile || data;

      if (wizardState.profile.role_details && wizardState.profile.role_details.commodities) {
        wizardState.selectedCrops = wizardState.profile.role_details.commodities;
      }

      try {
        const [sensRes, plotsRes] = await Promise.all([
          fetch('/api/v1/me/sensitive', { headers: getAuthHeader() }),
          fetch('/api/v1/me/plots', { headers: getAuthHeader() })
        ]);
        if (sensRes.ok) {
          wizardState.sensitive = await sensRes.json();
        }
        if (plotsRes.ok) {
          const pData = await plotsRes.json();
          wizardState.plots = pData.plots || [];
        }
      } catch (e) {}

      updateRegisteredHeaderBanner(wizardState.profile);

      const pStatus = wizardState.profile.status;
      if (pStatus === 'SUBMITTED') {
        renderUnderReviewCard(contentArea);
      } else if (pStatus === 'VERIFIED') {
        renderVerifiedOperationalConsole(contentArea);
      } else {
        renderWizardInterface(contentArea);
      }
    } catch (err) {
      updateRegisteredHeaderBanner(wizardState.profile);
      renderWizardInterface(contentArea);
    }
  };"""

new_render_ws = """  window.renderCurrentWorkspace = async function () {
    const container = document.getElementById('confinedWorkspace');
    if (!container) return;

    if (typeof currentRole !== 'undefined' && currentRole !== 'PRODUCER' && currentRole !== 'ADMIN') {
      const dynamicArea = document.getElementById('workspaceDynamicContent');
      if (dynamicArea) dynamicArea.style.display = 'none';

      const toolsGrid = document.getElementById('workspaceTools');
      const batchesList = document.getElementById('workspaceBatchesList');
      if (toolsGrid) toolsGrid.style.display = 'grid';
      if (batchesList && batchesList.parentNode) batchesList.parentNode.style.display = 'block';

      if (typeof window.renderDefaultWorkspace === 'function') {
        window.renderDefaultWorkspace();
      }
      return;
    }

    const toolsGrid = document.getElementById('workspaceTools');
    const batchesList = document.getElementById('workspaceBatchesList');
    if (toolsGrid) toolsGrid.style.display = 'none';
    if (batchesList && batchesList.parentNode) batchesList.parentNode.style.display = 'none';

    let contentArea = document.getElementById('workspaceDynamicContent');
    if (!contentArea) {
      contentArea = document.createElement('div');
      contentArea.id = 'workspaceDynamicContent';
      contentArea.style.minHeight = '350px';
      container.appendChild(contentArea);
    }
    contentArea.style.display = 'block';

    const t = getI18n();

    // SWR STEP 1: Check for cached profile in localStorage for 0ms INSTANT HYDRATION!
    let hasRenderedCached = false;
    let cachedProfile = null;
    try {
      cachedProfile = JSON.parse(localStorage.getItem('annasutra_cached_profile'));
    } catch (e) {}

    if (cachedProfile && currentRole === 'PRODUCER') {
      wizardState.profile = cachedProfile;
      if (cachedProfile.role_details && cachedProfile.role_details.commodities) {
        wizardState.selectedCrops = cachedProfile.role_details.commodities;
      }
      try {
        const cachedPlots = JSON.parse(localStorage.getItem('annasutra_cached_plots') || '[]');
        if (Array.isArray(cachedPlots)) wizardState.plots = cachedPlots;
      } catch (e) {}
      try {
        const cachedLots = JSON.parse(localStorage.getItem('annasutra_cached_lots') || '[]');
        if (Array.isArray(cachedLots)) window._producerLots = cachedLots;
      } catch (e) {}

      updateRegisteredHeaderBanner(wizardState.profile);

      if (cachedProfile.status === 'VERIFIED') {
        renderVerifiedOperationalConsole(contentArea);
        updateLotMetrics();
        applyLotFilters();
        hasRenderedCached = true;
      } else if (cachedProfile.status === 'SUBMITTED') {
        renderUnderReviewCard(contentArea);
        hasRenderedCached = true;
      }
    }

    // Only show loading spinner if we didn't have cached data to render immediately
    if (!hasRenderedCached) {
      contentArea.innerHTML = `
        <div style="text-align: center; padding: 48px 16px;">
          <div style="width: 36px; height: 36px; border: 3px solid #cbd5e1; border-top-color: #0b3d2e; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px;"></div>
          <p style="color: #64748b; font-size: 14px; font-weight: 600;">${escapeHtml(t.loadingRegistry)}</p>
        </div>
      `;
    }

    if (typeof currentRole !== 'undefined' && currentRole === 'ADMIN') {
      updateRegisteredHeaderBanner({ organisation_name: t.workspaceTitleAdmin });
      await loadAdminQueueAndRender(contentArea);
      return;
    }

    // SWR STEP 2: Parallel Background Revalidation (No waterfall, no blocking)
    try {
      const [profileRes, lotsRes, plotsRes] = await Promise.all([
        fetch('/api/v1/me/profile', { headers: getAuthHeader() }),
        fetch('/api/v1/lots/', { headers: getAuthHeader() }),
        fetch('/api/v1/me/plots', { headers: getAuthHeader() })
      ]);

      if (profileRes.status === 401 || profileRes.status === 403) {
        localStorage.removeItem('annasutra_cached_profile');
        localStorage.removeItem('annasutra_cached_lots');
        localStorage.removeItem('annasutra_cached_plots');
        wizardState.profile = { status: 'DRAFT', role: 'PRODUCER', version: 1 };
        updateRegisteredHeaderBanner(wizardState.profile);
        renderWizardInterface(contentArea);
        return;
      }

      const data = await profileRes.json();
      wizardState.profile = data.profile || data;
      try {
        localStorage.setItem('annasutra_cached_profile', JSON.stringify(wizardState.profile));
      } catch (e) {}

      if (wizardState.profile.role_details && wizardState.profile.role_details.commodities) {
        wizardState.selectedCrops = wizardState.profile.role_details.commodities;
      }

      if (plotsRes && plotsRes.ok) {
        const pData = await plotsRes.json();
        wizardState.plots = pData.plots || [];
        try {
          localStorage.setItem('annasutra_cached_plots', JSON.stringify(wizardState.plots));
        } catch (e) {}
      }

      if (lotsRes && lotsRes.ok) {
        const lData = await lotsRes.json();
        window._producerLots = lData.items || [];
        try {
          localStorage.setItem('annasutra_cached_lots', JSON.stringify(window._producerLots));
        } catch (e) {}
      }

      updateRegisteredHeaderBanner(wizardState.profile);

      const pStatus = wizardState.profile.status;
      if (pStatus === 'SUBMITTED') {
        renderUnderReviewCard(contentArea);
      } else if (pStatus === 'VERIFIED') {
        if (!hasRenderedCached) {
          renderVerifiedOperationalConsole(contentArea);
        }
        updateLotMetrics();
        applyLotFilters();
        if (document.getElementById('consoleTabContentAnalytics')?.style.display !== 'none') {
          renderProducerAnalytics();
        }
      } else {
        renderWizardInterface(contentArea);
      }
    } catch (err) {
      if (!hasRenderedCached) {
        updateRegisteredHeaderBanner(wizardState.profile);
        renderWizardInterface(contentArea);
      }
    }
  };"""

if old_render_ws in wiz_code:
    wiz_code = wiz_code.replace(old_render_ws, new_render_ws)
    print("Replaced renderCurrentWorkspace with SWR instant load")
else:
    print("WARNING: old_render_ws exact block not found, doing regex replacement")
    pattern = r"window\.renderCurrentWorkspace\s*=\s*async function\s*\(\)\s*\{[\s\S]*?updateRegisteredHeaderBanner\(wizardState\.profile\);\s*renderWizardInterface\(contentArea\);\s*\}\s*\};"
    wiz_code = re.sub(pattern, new_render_ws.strip(), wiz_code, count=1)
    print("Regex replaced renderCurrentWorkspace")

# Also cache lots in loadProducerLots
old_load_lots = """    try {
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
    applyLotFilters();"""

new_load_lots = """    try {
      const res = await fetch('/api/v1/lots/', { headers: getAuthHeader() });
      if (res.ok) {
        const data = await res.json();
        window._producerLots = data.items || [];
        try {
          localStorage.setItem('annasutra_cached_lots', JSON.stringify(window._producerLots));
        } catch (e) {}
      } else {
        window._producerLots = [];
      }
    } catch (e) {
      window._producerLots = [];
    }
    updateLotMetrics();
    applyLotFilters();
    if (document.getElementById('consoleTabContentAnalytics')?.style.display !== 'none') {
      renderProducerAnalytics();
    }"""

wiz_code = wiz_code.replace(old_load_lots, new_load_lots)

# Also update logoutEntitySession to clear cache
old_logout = """  window.logoutEntitySession = function () {
    localStorage.removeItem('annasutra_access_token');
    localStorage.removeItem('annasutra_role');
    localStorage.removeItem('annasutra_phone');
    window.location.href = '/';
  };"""

new_logout = """  window.logoutEntitySession = function () {
    localStorage.removeItem('annasutra_access_token');
    localStorage.removeItem('annasutra_role');
    localStorage.removeItem('annasutra_phone');
    localStorage.removeItem('annasutra_cached_profile');
    localStorage.removeItem('annasutra_cached_lots');
    localStorage.removeItem('annasutra_cached_plots');
    window.location.href = '/';
  };"""

wiz_code = wiz_code.replace(old_logout, new_logout)

with open(wiz_path, 'w', encoding='utf-8') as f:
    f.write(wiz_code)
print("Updated producer_wizard.js")

# -------------------------------------------------------------
# 4. Update landing.html locked footer with Android APK Download
# -------------------------------------------------------------
landing_path = os.path.join(BASE_DIR, 'backend', 'apps', 'publicview', 'templates', 'publicview', 'landing.html')
with open(landing_path, 'r', encoding='utf-8') as f:
    land_code = f.read()

# Clear cache on logout in landing.html
land_code = land_code.replace(
    """      localStorage.removeItem('annasutra_access_token');
      localStorage.removeItem('annasutra_role');
      localStorage.removeItem('annasutra_phone');""",
    """      localStorage.removeItem('annasutra_access_token');
      localStorage.removeItem('annasutra_role');
      localStorage.removeItem('annasutra_phone');
      localStorage.removeItem('annasutra_cached_profile');
      localStorage.removeItem('annasutra_cached_lots');
      localStorage.removeItem('annasutra_cached_plots');"""
)

# Add Android APK Direct Download Card to Col 1 in footer
apk_footer_card = """          <!-- Android APK Direct Download Card (Professional Locked Footer Component) -->
          <div class="footer-apk-card" style="margin: 16px 0; background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(6, 78, 59, 0.35) 100%); border: 1.5px solid #10b981; border-radius: 12px; padding: 14px 16px; display: flex; align-items: center; justify-content: space-between; gap: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.25);">
            <div style="display: flex; align-items: center; gap: 12px;">
              <div style="width: 42px; height: 42px; background: #10b981; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35);">
                <!-- Official Android SVG -->
                <svg width="24" height="24" viewBox="0 0 24 24" fill="#064e3b">
                  <path d="M17.523 15.3414c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.551 0 .9996.4482.9996.9993.0001.5511-.4485.9997-.9996.9997m-11.046 0c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9996.4482.9996.9993 0 .5511-.4485.9997-.9996.9997m11.4045-6.02l1.9973-3.4592a.416.416 0 00-.1521-.5676.416.416 0 00-.5676.1521l-2.0223 3.503C15.5902 8.411 13.8567 8.134 12 8.134c-1.8567 0-3.5902.277-5.1378.8157L4.8399 5.4467a.416.416 0 00-.5676-.1521.416.416 0 00-.1521.5676l1.9973 3.4592C2.6889 10.9443 0 14.5422 0 18.7778h24c0-4.2356-2.6889-7.8335-6.1185-9.4564"/>
                </svg>
              </div>
              <div>
                <div style="font-size: 11px; font-weight: 700; color: #a7f3d0; text-transform: uppercase; letter-spacing: 0.5px;" id="lblApkSub">Official Android Application</div>
                <div style="font-size: 14.5px; font-weight: 800; color: #ffffff;" id="lblApkTitle">AnnaSutra Mobile APK</div>
                <div style="font-size: 11.5px; color: #cbd5e1;" id="lblApkMeta">Direct Install • v1.0.0 (Android 8.0+)</div>
              </div>
            </div>
            <a href="/download/apk" class="btn-download-apk" style="display: inline-flex; align-items: center; gap: 8px; background: #10b981; color: #064e3b; font-weight: 800; font-size: 13px; padding: 10px 18px; border-radius: 8px; text-decoration: none; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4); flex-shrink: 0; transition: transform 0.15s ease;" title="Direct Download AnnaSutra Android APK (v1.0.0)">
              <!-- Downward Download Arrow SVG -->
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
              </svg>
              <span id="btnDownloadApkText">Download APK</span>
            </a>
          </div>"""

# Insert right after ataraxis-maker-pill
maker_pill_target = """          <div class="ataraxis-maker-pill">
            <img src="{{ cdac_logo|default:'/static/publicview/images/cdac_logo.png' }}" alt="C-DAC" class="cdac-footer-emblem" />
            <div class="ataraxis-maker-info">
              <div class="ataraxis-maker-org" id="footerOrgTitle">Centre for Development of Advanced Computing (C-DAC)</div>
              <div class="ataraxis-maker-gov" id="footerGovTitle">Ministry of Electronics & Information Technology, Government of India</div>
            </div>
          </div>"""

if maker_pill_target in land_code and 'footer-apk-card' not in land_code:
    land_code = land_code.replace(maker_pill_target, maker_pill_target + "\n\n" + apk_footer_card)
    print("Added APK card to landing.html footer")

# Also add in Col 2 EXPLORE link list
apk_link_item = """            <li>
              <a href="/download/apk" title="Download Android Mobile APK" style="color: #6ee7b7; font-weight: 700; display: inline-flex; align-items: center; gap: 6px;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="7 10 12 15 17 10"></polyline>
                  <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                <span id="footerLinkApk">Android APK Download (v1.0.0)</span>
              </a>
            </li>"""

if '<span id="footerLinkHome">National Homepage</span>' in land_code and 'footerLinkApk' not in land_code:
    target_link = """            <li>
              <a href="/" title="National Homepage">
                <span class="ataraxis-link-arrow">›</span>
                <span id="footerLinkHome">National Homepage</span>
              </a>
            </li>"""
    land_code = land_code.replace(target_link, target_link + "\n" + apk_link_item)
    print("Added APK link to Col 2 explore list in landing.html")

# Bump script version
land_code = re.sub(r'producer_wizard\.js\?v=\w+', 'producer_wizard.js?v=20261026v1', land_code)

with open(landing_path, 'w', encoding='utf-8') as f:
    f.write(land_code)
print("Updated landing.html")

# -------------------------------------------------------------
# 5. Update lot_summary.html and lot_not_found.html footers
# -------------------------------------------------------------
for fname in ['lot_summary.html', 'lot_not_found.html']:
    p = os.path.join(BASE_DIR, 'backend', 'apps', 'publicview', 'templates', 'publicview', fname)
    if not os.path.exists(p):
        continue
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()
    if maker_pill_target in c and 'footer-apk-card' not in c:
        c = c.replace(maker_pill_target, maker_pill_target + "\n\n" + apk_footer_card)
    if '<span id="footerLinkHome">National Homepage</span>' in c and 'footerLinkApk' not in c:
        target_link = """            <li>
              <a href="/" title="National Homepage">
                <span class="ataraxis-link-arrow">›</span>
                <span id="footerLinkHome">National Homepage</span>
              </a>
            </li>"""
        c = c.replace(target_link, target_link + "\n" + apk_link_item)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(c)
    print(f"Updated {fname} footer")

# -------------------------------------------------------------
# 6. Update annasutra_i18n.js with APK translations
# -------------------------------------------------------------
for rel in [
    os.path.join('backend', 'apps', 'publicview', 'static', 'publicview', 'js', 'annasutra_i18n.js'),
    os.path.join('static', 'publicview', 'js', 'annasutra_i18n.js')
]:
    p = os.path.join(BASE_DIR, rel)
    if not os.path.exists(p):
        continue
    with open(p, 'r', encoding='utf-8') as f:
        s = f.read()

    # EN
    if 'lblApkTitle:' not in s:
        s = s.replace(
            "footerLinkQuality: \"Agricultural Quality Standards\",",
            "footerLinkQuality: \"Agricultural Quality Standards\",\n      lblApkSub: \"Official Android Application\",\n      lblApkTitle: \"AnnaSutra Mobile APK\",\n      lblApkMeta: \"Direct Download • v1.0.0 (Android 8.0+)\",\n      btnDownloadApkText: \"Download APK\",\n      footerLinkApk: \"Android APK Download (v1.0.0)\","
        )
    # BN
    if 'অন্নসূত্র মোবাইল এপিকে' not in s:
        s = s.replace(
            "footerLinkQuality: \"কৃষি গুণমান মানদণ্ড ও এপিএমসি\",",
            "footerLinkQuality: \"কৃষি গুণমান মানদণ্ড ও এপিএমসি\",\n      lblApkSub: \"অফিসিয়াল অ্যান্ড্রয়েড অ্যাপ্লিকেশন\",\n      lblApkTitle: \"অন্নসূত্র মোবাইল এপিকে\",\n      lblApkMeta: \"সরাসরি ডাউনলোড • v1.0.0 (অ্যান্ড্রয়েড ৮.০+)\",\n      btnDownloadApkText: \"এপিকে ডাউনলোড করুন\",\n      footerLinkApk: \"অ্যান্ড্রয়েড এপিকে ডাউনলোড (v1.0.0)\","
        )
    # HI
    if 'अन्नसूत्र मोबाइल एपीके' not in s:
        s = s.replace(
            "\"footerLinkQuality\": \"कृषि गुणवत्ता मानक एवं एपीएमसी\",",
            "\"footerLinkQuality\": \"कृषि गुणवत्ता मानक एवं एपीएमसी\",\n      lblApkSub: \"आधिकारिक एंड्रॉइड एप्लिकेशन\",\n      lblApkTitle: \"अन्नसूत्र मोबाइल एपीके\",\n      lblApkMeta: \"सीधा डाउनलोड • v1.0.0 (एंड्रॉइड 8.0+)\",\n      btnDownloadApkText: \"एपीके डाउनलोड करें\",\n      footerLinkApk: \"एंड्रॉइड एपीके डाउनलोड (v1.0.0)\","
        )
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s)
    print(f"Updated i18n in {rel}")

# -------------------------------------------------------------
# 7. Sync static files
# -------------------------------------------------------------
src_js = os.path.join(BASE_DIR, 'backend', 'apps', 'publicview', 'static', 'publicview', 'js', 'producer_wizard.js')
shutil.copyfile(src_js, os.path.join(BASE_DIR, 'static', 'publicview', 'js', 'producer_wizard.js'))
shutil.copyfile(src_js, os.path.join(BASE_DIR, 'staticfiles', 'publicview', 'js', 'producer_wizard.js'))
print("Synced producer_wizard.js to static and staticfiles.")
print("All patches completed successfully.")
