"""Generate interactive, authentic AnnaSutra Mobile App simulator template without iframes.
Eliminates 'refused to connect' X-Frame-Options/CSP restrictions entirely.
"""

import sys
from pathlib import Path

TEMPLATE_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>AnnaSutra Mobile App • Live Development Simulator & Testing Portal</title>
  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary-green: #064e3b;
      --primary-dark: #022c22;
      --accent-saffron: #e67e22;
      --emerald-accent: #10b981;
      --emerald-dark: #047857;
      --slate-dark: #0f172a;
      --slate-muted: #64748b;
      --border-light: #e2e8f0;
      --bg-surface: #f8fafc;
      --phone-bg: #091a14;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: #091a14;
      color: #f8fafc;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
    }

    /* TOP INSTITUTIONAL BAR */
    .top-bar {
      background: #05140f;
      border-bottom: 1px solid #144d3b;
      padding: 10px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
    }
    .top-brand {
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
      color: #fff;
    }
    .brand-logo-img {
      height: 34px;
      border-radius: 6px;
    }
    .brand-title-wrap strong {
      font-size: 16px;
      letter-spacing: 0.5px;
      font-weight: 800;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .gov-badge {
      background: var(--accent-saffron);
      color: #fff;
      font-size: 10px;
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 800;
    }
    .top-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .btn-action-pill {
      background: #114232;
      border: 1px solid #23654e;
      color: #fff;
      padding: 7px 14px;
      border-radius: 8px;
      font-size: 12.5px;
      font-weight: 700;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s ease;
      cursor: pointer;
    }
    .btn-action-pill:hover {
      background: #195843;
      border-color: #34886b;
      transform: translateY(-1px);
    }
    .btn-action-pill.primary {
      background: #047857;
      border-color: #10b981;
    }
    .btn-action-pill.primary:hover {
      background: #059669;
    }

    /* MAIN STAGE */
    .simulator-container {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 30px 20px;
      gap: 40px;
      flex-wrap: wrap;
    }

    /* SMARTPHONE DEVICE FRAME */
    .device-shell {
      position: relative;
      width: 400px;
      height: 840px;
      background: #000;
      border-radius: 54px;
      box-shadow:
        0 0 0 12px #1e293b,
        0 0 0 14px #334155,
        0 25px 60px -15px rgba(0,0,0,0.8),
        0 0 80px rgba(16, 185, 129, 0.15);
      overflow: hidden;
      display: flex;
      flex-direction: column;
      border: 4px solid #000;
    }
    .device-speaker-notch {
      position: absolute;
      top: 10px;
      left: 50%;
      transform: translateX(-50%);
      width: 120px;
      height: 26px;
      background: #000;
      border-radius: 18px;
      z-index: 9999;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }
    .notch-camera {
      width: 10px;
      height: 10px;
      background: #111;
      border-radius: 50%;
      border: 1px solid #222;
    }
    .notch-sensor {
      width: 5px;
      height: 5px;
      background: #1a1a2e;
      border-radius: 50%;
    }

    /* PHONE SCREEN CONTAINER */
    .device-screen {
      flex: 1;
      width: 100%;
      background: #0b1f17;
      overflow: hidden;
      position: relative;
      display: flex;
      flex-direction: column;
      font-size: 13px;
      color: #f1f5f9;
      user-select: none;
    }

    /* PHONE STATUS BAR */
    .phone-status-bar {
      height: 42px;
      padding: 10px 20px 0;
      background: #064e3b;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
      font-weight: 700;
      color: #fff;
      z-index: 10;
    }
    .status-icons {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    /* MOBILE APP VIEWPORT (SCROLLABLE APP BODY) */
    .mobile-app-viewport {
      flex: 1;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      background: #062319;
      scrollbar-width: thin;
      scrollbar-color: #10b981 #062319;
    }
    .mobile-app-viewport::-webkit-scrollbar {
      width: 4px;
    }
    .mobile-app-viewport::-webkit-scrollbar-thumb {
      background: #10b981;
      border-radius: 4px;
    }

    /* MOBILE APP HEADER */
    .m-header {
      background: linear-gradient(180deg, #064e3b 0%, #06392b 100%);
      padding: 12px 16px 14px;
      border-bottom: 1px solid #0d5c46;
    }
    .m-header-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }
    .m-brand-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 17px;
      font-weight: 800;
      color: #fff;
    }
    .m-brand-logo {
      width: 26px;
      height: 26px;
      border-radius: 6px;
    }
    .m-sync-badge {
      background: #022c22;
      color: #34d399;
      border: 1px solid #059669;
      font-size: 10px;
      font-weight: 800;
      padding: 3px 8px;
      border-radius: 12px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .m-entity-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: rgba(0, 0, 0, 0.25);
      padding: 8px 12px;
      border-radius: 10px;
      border: 1px solid rgba(16, 185, 129, 0.25);
    }
    .m-entity-info strong {
      display: block;
      color: #ecfdf5;
      font-size: 13px;
      font-weight: 800;
    }
    .m-entity-info span {
      font-size: 11px;
      color: #a7f3d0;
      font-family: 'JetBrains Mono', monospace;
    }
    .m-lang-select {
      background: #022c22;
      border: 1px solid #10b981;
      color: #6ee7b7;
      font-size: 11px;
      font-weight: 700;
      padding: 4px 8px;
      border-radius: 6px;
      outline: none;
      cursor: pointer;
    }

    /* 4 MOBILE KPI CARDS */
    .m-kpi-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
      padding: 12px 14px;
    }
    .m-kpi-card {
      background: rgba(15, 45, 35, 0.8);
      border: 1px solid #134e3a;
      border-radius: 10px;
      padding: 10px 12px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .m-kpi-label {
      font-size: 11px;
      font-weight: 700;
      color: #94a3b8;
    }
    .m-kpi-value {
      font-size: 16px;
      font-weight: 900;
      color: #fff;
      font-family: 'JetBrains Mono', monospace;
    }
    .m-kpi-badge {
      font-size: 9.5px;
      font-weight: 800;
      padding: 2px 6px;
      border-radius: 4px;
      align-self: flex-start;
      margin-top: 2px;
    }

    /* DUAL TABS */
    .m-tab-bar {
      display: flex;
      border-bottom: 2px solid #0d5c46;
      background: #042419;
      position: sticky;
      top: 0;
      z-index: 5;
    }
    .m-tab-btn {
      flex: 1;
      padding: 11px 8px;
      background: transparent;
      border: none;
      color: #94a3b8;
      font-size: 12px;
      font-weight: 800;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: all 0.2s ease;
      position: relative;
    }
    .m-tab-btn.active {
      color: #34d399;
      background: rgba(16, 185, 129, 0.1);
    }
    .m-tab-btn.active::after {
      content: '';
      position: absolute;
      bottom: -2px;
      left: 0;
      right: 0;
      height: 3px;
      background: #10b981;
      border-radius: 3px 3px 0 0;
    }

    /* ACTION & FILTER BAR */
    .m-filter-bar {
      padding: 10px 14px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      background: #052a1e;
      border-bottom: 1px solid #0e4c3a;
    }
    .m-search-box {
      width: 100%;
      background: #021a12;
      border: 1px solid #134e3a;
      border-radius: 8px;
      padding: 7px 12px;
      color: #fff;
      font-size: 12px;
      outline: none;
    }
    .m-search-box:focus {
      border-color: #10b981;
    }
    .m-filters-row {
      display: flex;
      gap: 6px;
      align-items: center;
      justify-content: space-between;
    }
    .m-filter-select {
      flex: 1;
      background: #021a12;
      border: 1px solid #134e3a;
      color: #d1fae5;
      font-size: 11px;
      padding: 6px 8px;
      border-radius: 6px;
      outline: none;
    }
    .m-btn-add-lot {
      background: #10b981;
      color: #064e3b;
      font-weight: 800;
      font-size: 11.5px;
      padding: 7px 12px;
      border-radius: 6px;
      border: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      white-space: nowrap;
      transition: all 0.2s ease;
    }
    .m-btn-add-lot:hover {
      background: #34d399;
    }

    /* HARVEST LOTS LIST */
    .m-lot-list {
      padding: 12px 14px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .m-lot-card {
      background: #04241a;
      border: 1px solid #0f523c;
      border-radius: 12px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      transition: all 0.2s ease;
      box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    }
    .m-lot-card:hover {
      border-color: #10b981;
    }
    .m-lot-card-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 8px;
    }
    .m-lot-code-pill {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11.5px;
      font-weight: 800;
      color: #6ee7b7;
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid rgba(16, 185, 129, 0.3);
      padding: 2px 7px;
      border-radius: 5px;
    }
    .m-custody-pill {
      font-size: 10.5px;
      font-weight: 800;
      padding: 3px 8px;
      border-radius: 6px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .m-custody-pill.custody-farm {
      background: #064e3b;
      color: #a7f3d0;
      border: 1px solid #059669;
    }
    .m-custody-pill.custody-transit {
      background: #78350f;
      color: #fde68a;
      border: 1px solid #d97706;
    }
    .m-lot-title {
      font-size: 14px;
      font-weight: 800;
      color: #fff;
    }
    .m-lot-details-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 6px;
      font-size: 11.5px;
      color: #94a3b8;
      background: rgba(0, 0, 0, 0.2);
      padding: 8px;
      border-radius: 6px;
    }
    .m-lot-details-grid span strong {
      color: #e2e8f0;
    }
    .m-lot-actions-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 4px;
      padding-top: 8px;
      border-top: 1px dashed #0d4633;
    }
    .m-btn-action {
      background: #06392b;
      border: 1px solid #135d45;
      color: #ecfdf5;
      font-size: 11px;
      font-weight: 700;
      padding: 6px 10px;
      border-radius: 6px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .m-btn-action:hover {
      background: #0b4e3a;
      border-color: #10b981;
    }
    .m-btn-action.locked {
      background: rgba(120, 53, 15, 0.25);
      border-color: #92400e;
      color: #fcd34d;
      cursor: not-allowed;
      opacity: 0.9;
    }
    .m-btn-qr {
      background: #10b981;
      border: 1px solid #34d399;
      color: #064e3b;
      font-weight: 800;
      font-size: 11px;
      padding: 6px 12px;
      border-radius: 6px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .m-btn-qr:hover {
      background: #34d399;
    }

    /* ANALYTICS TAB CONTENT */
    .m-analytics-view {
      display: none;
      padding: 12px 14px;
      flex-direction: column;
      gap: 14px;
    }
    .m-analytics-card {
      background: #04241a;
      border: 1px solid #0f523c;
      border-radius: 12px;
      padding: 14px;
    }
    .m-analytics-card h4 {
      font-size: 13.5px;
      font-weight: 800;
      color: #fff;
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    /* MOBILE BOTTOM NAV */
    .m-bottom-nav {
      height: 58px;
      background: #041c14;
      border-top: 1px solid #0d5c46;
      display: flex;
      align-items: center;
      justify-content: space-around;
      position: sticky;
      bottom: 0;
      z-index: 20;
    }
    .m-nav-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 3px;
      color: #64748b;
      font-size: 10px;
      font-weight: 700;
      background: none;
      border: none;
      cursor: pointer;
      transition: color 0.15s ease;
    }
    .m-nav-item.active {
      color: #10b981;
    }
    .m-nav-item svg {
      width: 18px;
      height: 18px;
    }

    /* MODALS & OVERLAYS */
    .m-modal-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.85);
      backdrop-filter: blur(4px);
      z-index: 1000;
      display: none;
      flex-direction: column;
      justify-content: flex-end;
    }
    .m-modal-sheet {
      background: #062b20;
      border-top: 2px solid #10b981;
      border-radius: 20px 20px 0 0;
      padding: 18px 16px 24px;
      max-height: 88%;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .m-modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #0f523c;
      padding-bottom: 10px;
    }
    .m-modal-title {
      font-size: 15px;
      font-weight: 800;
      color: #fff;
    }
    .m-btn-close {
      background: #0f3d2f;
      border: 1px solid #1a624d;
      color: #fff;
      width: 28px;
      height: 28px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
    }
    .m-form-group {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .m-form-group label {
      font-size: 11px;
      font-weight: 700;
      color: #a7f3d0;
    }
    .m-form-input, .m-form-select {
      background: #021a12;
      border: 1px solid #134e3a;
      border-radius: 6px;
      padding: 8px 10px;
      color: #fff;
      font-size: 12px;
      outline: none;
    }
    .m-form-input:focus, .m-form-select:focus {
      border-color: #10b981;
    }
    .m-form-section-title {
      font-size: 12px;
      font-weight: 800;
      color: #34d399;
      margin-top: 6px;
      border-bottom: 1px dashed #135d45;
      padding-bottom: 4px;
    }

    /* QR MODAL SPECIFIC */
    .qr-preview-box {
      background: #fff;
      padding: 16px;
      border-radius: 12px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      margin: 8px 0;
    }
    .qr-canonical-code {
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      font-weight: 800;
      color: #064e3b;
      letter-spacing: 0.5px;
    }

    /* SIDEBAR INFO & CONTROLS */
    .controls-panel {
      max-width: 440px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .panel-card {
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid #1e293b;
      backdrop-filter: blur(12px);
      border-radius: 16px;
      padding: 24px;
    }
    .panel-card h3 {
      font-size: 18px;
      font-weight: 800;
      color: #fff;
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .panel-card p {
      font-size: 13.5px;
      color: #94a3b8;
      line-height: 1.6;
      margin-bottom: 16px;
    }
    .badge-sub50 {
      background: #064e3b;
      color: #6ee7b7;
      border: 1px solid #059669;
      font-size: 12px;
      font-weight: 800;
      padding: 3px 8px;
      border-radius: 6px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }

    /* DIRECT APK DOWNLOAD BLOCK */
    .download-card {
      background: linear-gradient(135deg, #064e3b 0%, #047857 100%);
      border: 1px solid #10b981;
      border-radius: 16px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    .btn-download-apk {
      background: #fff;
      color: #064e3b;
      font-weight: 800;
      font-size: 15px;
      padding: 14px 20px;
      border-radius: 12px;
      text-decoration: none;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.2);
      transition: all 0.2s ease;
    }
    .btn-download-apk:hover {
      background: #f1f5f9;
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(0,0,0,0.3);
    }
    .apk-variants-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
      font-size: 12.5px;
      color: #d1fae5;
    }
    .apk-variant-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: rgba(0,0,0,0.15);
      padding: 8px 12px;
      border-radius: 8px;
    }

    /* FOOTER */
    .footer-bar {
      background: #05140f;
      border-top: 1px solid #144d3b;
      padding: 14px 20px;
      text-align: center;
      font-size: 12px;
      color: #64748b;
    }

    @media (max-width: 600px) {
      .device-shell {
        width: 100vw;
        height: 100vh;
        border-radius: 0;
        box-shadow: none;
        border: none;
      }
      .controls-panel {
        display: none;
      }
      .top-bar {
        display: none;
      }
      .simulator-container {
        padding: 0;
      }
    }
  </style>
</head>
<body>

  <!-- TOP BAR -->
  <header class="top-bar">
    <a href="/" class="top-brand">
      <img src="{{ brand_logo }}" alt="AnnaSutra" class="brand-logo-img">
      <div class="brand-title-wrap">
        <strong>AnnaSutra Mobile <span class="gov-badge">LIVE SIMULATOR</span></strong>
      </div>
    </a>
    <div class="top-actions">
      <a href="/" class="btn-action-pill">&larr; Return to Web Portal</a>
      <a href="/download/apk" class="btn-action-pill primary" download>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
        Download Android APK (&lt;50MB)
      </a>
    </div>
  </header>

  <!-- MAIN STAGE -->
  <main class="simulator-container">

    <!-- SMARTPHONE DEVICE FRAME -->
    <div class="device-shell">
      <div class="device-speaker-notch">
        <div class="notch-sensor"></div>
        <div class="notch-camera"></div>
      </div>

      <div class="device-screen">

        <!-- PHONE STATUS BAR -->
        <div class="phone-status-bar">
          <span id="statusClock">12:45</span>
          <div class="status-icons">
            <span style="font-size: 10px; font-weight: 800; background: #047857; padding: 1px 4px; border-radius: 3px;">5G</span>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12.55a11 11 0 0 1 14.08 0"></path><path d="M1.42 9a16 16 0 0 1 21.16 0"></path><path d="M8.53 16.11a6 6 0 0 1 6.95 0"></path><line x1="12" y1="20" x2="12.01" y2="20"></line></svg>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="2" y="7" width="16" height="10" rx="2" ry="2"></rect><line x1="22" y1="11" x2="22" y2="13"></line><line x1="6" y1="10" x2="6" y2="14" stroke="#10b981" stroke-width="3"></line><line x1="10" y1="10" x2="10" y2="14" stroke="#10b981" stroke-width="3"></line><line x1="14" y1="10" x2="14" y2="14" stroke="#10b981" stroke-width="3"></line></svg>
          </div>
        </div>

        <!-- MOBILE APP VIEWPORT (SCROLLABLE APP BODY) -->
        <div class="mobile-app-viewport" id="mobileAppViewport">

          <!-- APP HEADER -->
          <div class="m-header">
            <div class="m-header-top">
              <div class="m-brand-title">
                <img src="{{ brand_logo }}" alt="AnnaSutra" class="m-brand-logo">
                <span>AnnaSutra</span>
              </div>
              <div class="m-sync-badge">
                <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #34d399;"></span>
                <span>In Sync</span>
              </div>
            </div>

            <div class="m-entity-bar">
              <div class="m-entity-info">
                <strong>Dr. Niladri's Farm</strong>
                <span>Producer (X7803)</span>
              </div>
              <select id="mobileLangSelect" class="m-lang-select" onchange="changeMobileLang(this.value)">
                <option value="en">English</option>
                <option value="hi">हिंदी</option>
                <option value="bn">বাংলা</option>
              </select>
            </div>
          </div>

          <!-- 4 KPI SUMMARY CARDS -->
          <div class="m-kpi-grid">
            <div class="m-kpi-card">
              <span class="m-kpi-label" data-i18n="farmCustody">Farm Custody</span>
              <span class="m-kpi-value" id="kpiFarm">2,450 kg</span>
              <span class="m-kpi-badge" style="background: rgba(16, 185, 129, 0.2); color: #6ee7b7;">Active Store</span>
            </div>
            <div class="m-kpi-card">
              <span class="m-kpi-label" data-i18n="inTransit">In Transit</span>
              <span class="m-kpi-value" id="kpiTransit" style="color: #fde68a;">1,200 kg</span>
              <span class="m-kpi-badge" style="background: rgba(245, 158, 11, 0.2); color: #fcd34d;">En Route Mandi</span>
            </div>
            <div class="m-kpi-card">
              <span class="m-kpi-label" data-i18n="dispatched">Dispatched</span>
              <span class="m-kpi-value" id="kpiDispatched" style="color: #93c5fd;">5,800 kg</span>
              <span class="m-kpi-badge" style="background: rgba(59, 130, 246, 0.2); color: #bfdbfe;">Mandi Settled</span>
            </div>
            <div class="m-kpi-card">
              <span class="m-kpi-label" data-i18n="lotValuation">Lot Valuation</span>
              <span class="m-kpi-value" id="kpiValuation" style="color: #a7f3d0;">₹ 1,84,500</span>
              <span class="m-kpi-badge" style="background: rgba(16, 185, 129, 0.2); color: #6ee7b7;">Market Value</span>
            </div>
          </div>

          <!-- DUAL TAB SWITCHER -->
          <div class="m-tab-bar">
            <button class="m-tab-btn active" id="tabBtnLedger" onclick="switchMobileTab('ledger')">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
              <span data-i18n="tabLedger">Harvest Lots &amp; Ledger</span>
            </button>
            <button class="m-tab-btn" id="tabBtnAnalytics" onclick="switchMobileTab('analytics')">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
              <span data-i18n="tabAnalytics">Analytics &amp; Insights</span>
            </button>
          </div>

          <!-- TAB 1: HARVEST LOTS & CUSTODY LEDGER -->
          <div id="tabContentLedger">

            <!-- FILTER BAR -->
            <div class="m-filter-bar">
              <input type="text" id="lotSearchInput" class="m-search-box" placeholder="Search lot code, crop, variety..." onkeyup="filterLots()">
              <div class="m-filters-row">
                <select id="filterCrop" class="m-filter-select" onchange="filterLots()">
                  <option value="ALL">All Crops</option>
                  <option value="Tomato">Tomato</option>
                  <option value="Potato">Potato</option>
                  <option value="Cauliflower">Cauliflower</option>
                  <option value="Paddy">Paddy</option>
                  <option value="Wheat">Wheat</option>
                  <option value="Mango">Mango</option>
                </select>
                <select id="filterPlot" class="m-filter-select" onchange="filterLots()">
                  <option value="ALL">All Plots</option>
                  <option value="Plot #1">Plot #1 (North Acre)</option>
                  <option value="Plot #2">Plot #2 (East Yard)</option>
                  <option value="Plot #3">Plot #3 (South Green)</option>
                </select>
                <button class="m-btn-add-lot" onclick="openNewLotModal()">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                  <span data-i18n="newLot">+ Lot</span>
                </button>
              </div>
            </div>

            <!-- LOT LIST (LATEST TO OLDEST) -->
            <div class="m-lot-list" id="mHarvestLotContainer">
              <!-- Dynamically populated via JS -->
            </div>

          </div>

          <!-- TAB 2: ANALYTICS & INSIGHTS -->
          <div id="tabContentAnalytics" class="m-analytics-view">

            <!-- MONTHLY HARVEST & VALUATION CHART -->
            <div class="m-analytics-card">
              <h4>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
                <span data-i18n="chartTitle">Monthly Harvest Volume vs Valuation</span>
              </h4>
              <p style="font-size: 11px; color: #94a3b8; margin-bottom: 10px;">Yield output (kg) compared to total realized valuation (₹).</p>

              <!-- SVG CHART -->
              <svg viewBox="0 0 320 160" style="width: 100%; height: auto; background: #021a12; border-radius: 8px; border: 1px solid #0f523c; padding: 6px;">
                <!-- Grid Lines -->
                <line x1="30" y1="20" x2="310" y2="20" stroke="#0f3d2f" stroke-width="1" stroke-dasharray="3,3"></line>
                <line x1="30" y1="60" x2="310" y2="60" stroke="#0f3d2f" stroke-width="1" stroke-dasharray="3,3"></line>
                <line x1="30" y1="100" x2="310" y2="100" stroke="#0f3d2f" stroke-width="1" stroke-dasharray="3,3"></line>
                <line x1="30" y1="135" x2="310" y2="135" stroke="#134e3a" stroke-width="1"></line>

                <!-- Bars (Volume in kg) -->
                <!-- Oct -->
                <rect x="45" y="65" width="22" height="70" fill="#059669" rx="3"></rect>
                <text x="56" y="150" fill="#94a3b8" font-size="9" text-anchor="middle">Oct</text>

                <!-- Nov -->
                <rect x="105" y="45" width="22" height="90" fill="#059669" rx="3"></rect>
                <text x="116" y="150" fill="#94a3b8" font-size="9" text-anchor="middle">Nov</text>

                <!-- Dec -->
                <rect x="165" y="30" width="22" height="105" fill="#059669" rx="3"></rect>
                <text x="176" y="150" fill="#94a3b8" font-size="9" text-anchor="middle">Dec</text>

                <!-- Jan -->
                <rect x="225" y="50" width="22" height="85" fill="#059669" rx="3"></rect>
                <text x="236" y="150" fill="#94a3b8" font-size="9" text-anchor="middle">Jan</text>

                <!-- Feb -->
                <rect x="275" y="40" width="22" height="95" fill="#10b981" rx="3"></rect>
                <text x="286" y="150" fill="#34d399" font-size="9" font-weight="bold" text-anchor="middle">Feb</text>

                <!-- Line (Valuation in thousands) -->
                <polyline points="56,70 116,50 176,35 236,55 286,42" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round"></polyline>
                <circle cx="56" cy="70" r="3.5" fill="#f59e0b"></circle>
                <circle cx="116" cy="50" r="3.5" fill="#f59e0b"></circle>
                <circle cx="176" cy="35" r="3.5" fill="#f59e0b"></circle>
                <circle cx="236" cy="55" r="3.5" fill="#f59e0b"></circle>
                <circle cx="286" cy="42" r="3.5" fill="#f59e0b"></circle>
              </svg>

              <div style="display: flex; justify-content: center; gap: 16px; margin-top: 10px; font-size: 11px;">
                <span style="display: flex; align-items: center; gap: 6px; color: #a7f3d0;">
                  <span style="width: 10px; height: 10px; background: #059669; border-radius: 2px;"></span>
                  Harvest Volume (kg)
                </span>
                <span style="display: flex; align-items: center; gap: 6px; color: #fde68a;">
                  <span style="width: 10px; height: 3px; background: #f59e0b; border-radius: 2px;"></span>
                  Realized Value (₹)
                </span>
              </div>
            </div>

            <!-- CROP DISTRIBUTION -->
            <div class="m-analytics-card">
              <h4>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path><path d="M22 12A10 10 0 0 0 12 2v10z"></path></svg>
                <span data-i18n="cropShare">Crop Production Share</span>
              </h4>

              <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 6px;">
                <div>
                  <div style="display: flex; justify-content: space-between; font-size: 11.5px; margin-bottom: 4px;">
                    <span>Tomato (Hybrid Red)</span>
                    <strong style="color: #6ee7b7;">42% (2,850 kg)</strong>
                  </div>
                  <div style="width: 100%; height: 6px; background: #021a12; border-radius: 3px; overflow: hidden;">
                    <div style="width: 42%; height: 100%; background: #10b981;"></div>
                  </div>
                </div>

                <div>
                  <div style="display: flex; justify-content: space-between; font-size: 11.5px; margin-bottom: 4px;">
                    <span>Potato (Kufri Jyoti)</span>
                    <strong style="color: #fde68a;">36% (2,400 kg)</strong>
                  </div>
                  <div style="width: 100%; height: 6px; background: #021a12; border-radius: 3px; overflow: hidden;">
                    <div style="width: 36%; height: 100%; background: #f59e0b;"></div>
                  </div>
                </div>

                <div>
                  <div style="display: flex; justify-content: space-between; font-size: 11.5px; margin-bottom: 4px;">
                    <span>Cauliflower (Snowball)</span>
                    <strong style="color: #93c5fd;">22% (1,500 kg)</strong>
                  </div>
                  <div style="width: 100%; height: 6px; background: #021a12; border-radius: 3px; overflow: hidden;">
                    <div style="width: 22%; height: 100%; background: #3b82f6;"></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- AUDIT & VERIFICATION INTEGRITY -->
            <div class="m-analytics-card" style="background: linear-gradient(135deg, #06392b 0%, #04241a 100%); border-color: #10b981;">
              <h4>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                <span>C-DAC Cryptographic Verification</span>
              </h4>
              <p style="font-size: 11.5px; color: #a7f3d0; margin-bottom: 6px;">All active harvest lots are cryptographically anchored with append-only Merkle ledger hashes.</p>
              <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 6px;">
                <span class="m-kpi-badge" style="background: rgba(16, 185, 129, 0.25); color: #34d399;">&check; Zero Discrepancies</span>
                <span class="m-kpi-badge" style="background: rgba(16, 185, 129, 0.25); color: #34d399;">&check; GPS Geo-fenced</span>
                <span class="m-kpi-badge" style="background: rgba(16, 185, 129, 0.25); color: #34d399;">&check; Unlimited Sovereign QR</span>
              </div>
            </div>

          </div>

        </div>

        <!-- MOBILE BOTTOM NAVIGATION -->
        <div class="m-bottom-nav">
          <button class="m-nav-item active" id="navItemLedger" onclick="switchMobileTab('ledger')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
            <span data-i18n="navLedger">Ledger</span>
          </button>
          <button class="m-nav-item" id="navItemAnalytics" onclick="switchMobileTab('analytics')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
            <span data-i18n="navAnalytics">Analytics</span>
          </button>
          <button class="m-nav-item" onclick="openDispatchModal()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>
            <span data-i18n="navDispatch">Dispatch</span>
          </button>
          <button class="m-nav-item" onclick="openProfileModal()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            <span data-i18n="navProfile">Profile</span>
          </button>
        </div>

        <!-- MODAL 1: 29-ATTRIBUTE NEW LOT INTAKE -->
        <div class="m-modal-overlay" id="modalNewLot">
          <div class="m-modal-sheet">
            <div class="m-modal-header">
              <span class="m-modal-title">Register New Harvest Lot</span>
              <button class="m-btn-close" onclick="closeModal('modalNewLot')">&times;</button>
            </div>

            <!-- SECTION A: BASIC CROP INFO -->
            <div class="m-form-section-title">1. Crop &amp; Variety Information</div>
            <div class="m-form-group">
              <label>Crop Name *</label>
              <select id="formCrop" class="m-form-select">
                <option value="Tomato">Tomato (Hybrid Red)</option>
                <option value="Potato">Potato (Kufri Jyoti)</option>
                <option value="Cauliflower">Cauliflower (Snowball)</option>
                <option value="Paddy">Paddy / Rice (Basmati)</option>
                <option value="Wheat">Wheat (Sharbati)</option>
                <option value="Mango">Mango (Alphonso)</option>
              </select>
            </div>
            <div class="m-form-group">
              <label>Variety / Cultivar *</label>
              <input type="text" id="formVariety" class="m-form-input" placeholder="e.g. Hybrid Red F1">
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
              <div class="m-form-group">
                <label>Harvest Date *</label>
                <input type="date" id="formHarvestDate" class="m-form-input" value="2026-10-26">
              </div>
              <div class="m-form-group">
                <label>Harvest Time</label>
                <input type="time" id="formHarvestTime" class="m-form-input" value="08:30">
              </div>
            </div>

            <!-- SECTION B: LAND & GEOGRAPHY -->
            <div class="m-form-section-title">2. Land Plot &amp; Geo-Coordinates</div>
            <div class="m-form-group">
              <label>Land Plot / Farm Parcel *</label>
              <select id="formPlot" class="m-form-select">
                <option value="Plot #1 (North Acre)">Plot #1 (North Acre - 2.5 Ha)</option>
                <option value="Plot #2 (East Yard)">Plot #2 (East Yard - 3.2 Ha)</option>
                <option value="Plot #3 (South Greenhouse)">Plot #3 (South Greenhouse - 1.0 Ha)</option>
              </select>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
              <div class="m-form-group">
                <label>GPS Latitude</label>
                <input type="text" id="formLat" class="m-form-input" value="22.5726">
              </div>
              <div class="m-form-group">
                <label>GPS Longitude</label>
                <input type="text" id="formLng" class="m-form-input" value="88.3639">
              </div>
            </div>
            <div class="m-form-group">
              <label>Khasra / Survey Number</label>
              <input type="text" id="formKhasra" class="m-form-input" placeholder="e.g. KH-412/2026">
            </div>

            <!-- SECTION C: WEIGHT & MASS -->
            <div class="m-form-section-title">3. Mass &amp; Weight Specifications</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
              <div class="m-form-group">
                <label>Gross Weight (kg) *</label>
                <input type="number" id="formGross" class="m-form-input" placeholder="e.g. 520" oninput="calcNetWeight()">
              </div>
              <div class="m-form-group">
                <label>Tare Weight (kg)</label>
                <input type="number" id="formTare" class="m-form-input" value="20" oninput="calcNetWeight()">
              </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
              <div class="m-form-group">
                <label>Net Quantity (kg) *</label>
                <input type="number" id="formNet" class="m-form-input" placeholder="500" readonly style="background: #06392b; color: #34d399; font-weight: 800;">
              </div>
              <div class="m-form-group">
                <label>Moisture %</label>
                <input type="number" id="formMoisture" class="m-form-input" value="12.5" step="0.1">
              </div>
            </div>
            <div class="m-form-group">
              <label>Quality Grade</label>
              <select id="formGrade" class="m-form-select">
                <option value="Grade A">Grade A (Premium Export Quality)</option>
                <option value="Grade B">Grade B (Standard Market Grade)</option>
                <option value="Grade C">Grade C (Processing Grade)</option>
              </select>
            </div>

            <!-- SECTION D: COMPLIANCE & STORAGE -->
            <div class="m-form-section-title">4. Compliance, Storage &amp; Packaging</div>
            <div class="m-form-group">
              <label>Organic Status</label>
              <select id="formOrganic" class="m-form-select">
                <option value="Certified Organic">Certified Organic (NPOP / Jaivik Bharat)</option>
                <option value="In Conversion">In Conversion (Year 2)</option>
                <option value="Conventional">Conventional Sustainable</option>
              </select>
            </div>
            <div class="m-form-group">
              <label>Storage Facility / Yard Name</label>
              <input type="text" id="formStorage" class="m-form-input" value="Cluster Cold Yard #1">
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
              <div class="m-form-group">
                <label>Packaging Type</label>
                <select id="formPackaging" class="m-form-select">
                  <option value="Plastic Crates">Plastic Crates</option>
                  <option value="Jute Gunny Bags">Jute Gunny Bags</option>
                  <option value="Corrugated Boxes">Corrugated Boxes</option>
                </select>
              </div>
              <div class="m-form-group">
                <label>Units Count</label>
                <input type="number" id="formUnits" class="m-form-input" value="25">
              </div>
            </div>
            <div class="m-form-group">
              <label>Estimated Value (₹) *</label>
              <input type="number" id="formValue" class="m-form-input" placeholder="e.g. 25000">
            </div>

            <button class="m-btn-add-lot" style="width: 100%; justify-content: center; padding: 12px; font-size: 14px; margin-top: 10px;" onclick="saveNewLot()">
              Save &amp; Generate Sovereign QR
            </button>
          </div>
        </div>

        <!-- MODAL 2: PENCIL EDIT LOT MODAL -->
        <div class="m-modal-overlay" id="modalEditLot">
          <div class="m-modal-sheet">
            <div class="m-modal-header">
              <span class="m-modal-title">Edit Harvest Lot (Farm Custody)</span>
              <button class="m-btn-close" onclick="closeModal('modalEditLot')">&times;</button>
            </div>
            <input type="hidden" id="editLotIndex">
            <div class="m-form-group">
              <label>Lot Identifier</label>
              <input type="text" id="editLotCode" class="m-form-input" readonly style="background: #021a12; color: #6ee7b7; font-family: 'JetBrains Mono', monospace;">
            </div>
            <div class="m-form-group">
              <label>Net Quantity (kg) *</label>
              <input type="number" id="editLotQty" class="m-form-input">
            </div>
            <div class="m-form-group">
              <label>Variety / Cultivar</label>
              <input type="text" id="editLotVariety" class="m-form-input">
            </div>
            <div class="m-form-group">
              <label>Moisture Content (%)</label>
              <input type="number" id="editLotMoisture" class="m-form-input" step="0.1">
            </div>
            <div class="m-form-group">
              <label>Storage Yard / Facility</label>
              <input type="text" id="editLotStorage" class="m-form-input">
            </div>
            <button class="m-btn-add-lot" style="width: 100%; justify-content: center; padding: 12px; font-size: 14px; margin-top: 8px;" onclick="saveEditedLot()">
              Save Changes to Ledger
            </button>
          </div>
        </div>

        <!-- MODAL 3: UNLIMITED QR CODE VIEW -->
        <div class="m-modal-overlay" id="modalQr">
          <div class="m-modal-sheet" style="align-items: center; text-align: center;">
            <div class="m-modal-header" style="width: 100%;">
              <span class="m-modal-title">Cryptographic Sovereign QR</span>
              <button class="m-btn-close" onclick="closeModal('modalQr')">&times;</button>
            </div>

            <div class="qr-preview-box">
              <div id="qrImageWrap">
                <!-- Dynamic SVG QR Code -->
              </div>
              <span class="qr-canonical-code" id="qrDisplayCode">AS-LOT-2026-X7803-001</span>
              <span style="font-size: 10.5px; color: #064e3b; font-weight: 600;">Government of India • Ministry of Agriculture</span>
            </div>

            <p style="font-size: 11px; color: #a7f3d0; line-height: 1.5; margin: 6px 0;">
              Cryptographically verified by C-DAC. Scan with any barcode reader or official AnnaSutra field scanner.
            </p>

            <div style="display: flex; gap: 8px; width: 100%;">
              <button class="m-btn-action" style="flex: 1; justify-content: center; padding: 10px;" onclick="alert('QR code downloaded for offline label printing!')">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                Download Slip
              </button>
              <button class="m-btn-qr" style="flex: 1; justify-content: center; padding: 10px;" onclick="closeModal('modalQr')">
                Done
              </button>
            </div>
          </div>
        </div>

        <!-- MODAL 4: DISPATCH SIMULATOR -->
        <div class="m-modal-overlay" id="modalDispatch">
          <div class="m-modal-sheet">
            <div class="m-modal-header">
              <span class="m-modal-title">Dispatch Custody Handover</span>
              <button class="m-btn-close" onclick="closeModal('modalDispatch')">&times;</button>
            </div>
            <p style="font-size: 12px; color: #a7f3d0;">Select a harvest lot currently in farm custody to dispatch to mandi or transporter.</p>
            <div class="m-form-group">
              <label>Select Lot</label>
              <select id="dispatchLotSelect" class="m-form-select">
                <!-- Populated dynamically -->
              </select>
            </div>
            <div class="m-form-group">
              <label>Destination Mandi / Warehouse</label>
              <input type="text" class="m-form-input" value="Kolkata APMC Mandi #4">
            </div>
            <div class="m-form-group">
              <label>Transporter Vehicle No.</label>
              <input type="text" class="m-form-input" value="WB-19-AF-4281">
            </div>
            <button class="m-btn-add-lot" style="width: 100%; justify-content: center; padding: 12px; margin-top: 8px;" onclick="executeDispatch()">
              Confirm Custody Transfer (Locks Lot)
            </button>
          </div>
        </div>

        <!-- MODAL 5: PROFILE VIEW -->
        <div class="m-modal-overlay" id="modalProfile">
          <div class="m-modal-sheet">
            <div class="m-modal-header">
              <span class="m-modal-title">Entity Profile &amp; Credentials</span>
              <button class="m-btn-close" onclick="closeModal('modalProfile')">&times;</button>
            </div>
            <div style="background: rgba(0,0,0,0.25); padding: 12px; border-radius: 10px; border: 1px solid #10b981; margin-top: 4px;">
              <strong style="color: #fff; font-size: 14px; display: block;">Dr. Niladri's Farm</strong>
              <span style="font-size: 11.5px; color: #a7f3d0; font-family: 'JetBrains Mono', monospace;">Registered Entity Code: X7803</span>
              <div style="margin-top: 8px; font-size: 11px; color: #94a3b8; line-height: 1.6;">
                Status: <strong style="color: #34d399;">VERIFIED PRODUCER</strong><br>
                Sovereign QR Allocation: <strong>UNLIMITED</strong><br>
                Verification Authority: <strong>C-DAC AgriTrace Unit</strong><br>
                Authorized Land Plots: <strong>3 Parcels (6.7 Hectares)</strong>
              </div>
            </div>
            <button class="m-btn-action" style="width: 100%; justify-content: center; padding: 10px; margin-top: 8px;" onclick="closeModal('modalProfile')">
              Close Profile
            </button>
          </div>
        </div>

      </div>
    </div>

    <!-- CONTROLS & DOWNLOAD PANEL -->
    <div class="controls-panel">

      <!-- LIVE DEV OVERVIEW CARD -->
      <div class="panel-card">
        <h3>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>
          Live Mobile Development
        </h3>
        <p>
          Test the AnnaSutra Mobile App live in your browser before flashing to physical devices. Any updates pushed to code are hot-deployed to this simulator!
        </p>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
          <span class="badge-sub50">&check; Dual-Tab Ledger &amp; Analytics</span>
          <span class="badge-sub50">&check; 29-Field Harvest Lots</span>
          <span class="badge-sub50">&check; Unlimited QR Generator</span>
          <span class="badge-sub50">&check; Strict i18n (EN/HI/BN)</span>
        </div>
      </div>

      <!-- DIRECT PRODUCTION APK DOWNLOAD CARD -->
      <div class="download-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <strong style="font-size: 16px; color: #fff;">Native Android App (APK)</strong>
          <span style="background: rgba(0,0,0,0.25); color: #a7f3d0; font-size: 11px; font-weight: 800; padding: 2px 8px; border-radius: 12px;">v1.0.0 Release</span>
        </div>
        <p style="font-size: 13px; color: #d1fae5; margin: 0; line-height: 1.5;">
          Compiled with ProGuard &amp; R8 shrinking. Strictly under 50MB. Installs on any Android phone (Android 7.0+).
        </p>

        <a href="/download/apk" class="btn-download-apk" download>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
          <span>Direct Download APK (&lt;50MB)</span>
        </a>

        <div class="apk-variants-list">
          <div class="apk-variant-item">
            <span><strong>Universal Release APK</strong> (Any phone)</span>
            <span style="font-family: monospace; font-weight: 700;">36.0 MB</span>
          </div>
          <div class="apk-variant-item">
            <span><strong>ARM64 Optimized APK</strong> (Modern phones)</span>
            <span style="font-family: monospace; font-weight: 700;">14.8 MB</span>
          </div>
        </div>
      </div>

      <!-- ON-DEVICE QR SCAN TO TEST -->
      <div class="panel-card" style="text-align: center;">
        <h3 style="justify-content: center;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
          Scan to Test on Smartphone
        </h3>
        <p style="margin-bottom: 12px;">Open your phone's camera to open this live mobile app directly in full-screen PWA mode or download the APK.</p>
        <div style="background: #fff; padding: 12px; border-radius: 12px; display: inline-block;">
          <img src="https://api.qrserver.com/v1/create-qr-code/?size=140x140&data=https%3A%2F%2Fannasutra.vercel.app%2Fmobile%2F" alt="Scan QR to Test Mobile App" style="width: 140px; height: 140px; display: block;">
        </div>
      </div>

    </div>

  </main>

  <!-- FOOTER -->
  <footer class="footer-bar">
    Government of India • Ministry of Agriculture &amp; Farmers Welfare • C-DAC Kolkata AgriTrace Consortium
  </footer>

  <script>
    // Live Clock in Status Bar
    function updateClock() {
      const now = new Date();
      const h = String(now.getHours()).padStart(2, '0');
      const m = String(now.getMinutes()).padStart(2, '0');
      const el = document.getElementById('statusClock');
      if (el) el.innerText = h + ':' + m;
    }
    setInterval(updateClock, 1000);
    updateClock();

    // Harvest Lot Data Model (Sorted Latest to Oldest)
    let lots = [
      {
        code: "AS-LOT-2026-X7803-003",
        crop: "Tomato",
        variety: "Hybrid Red F1",
        netQty: 650.0,
        harvestDate: "25 Oct 2026",
        plot: "Plot #1 (North Acre)",
        storage: "Cluster Cold Yard #1",
        moisture: 12.0,
        status: "FARM_CUSTODY", // Editable
        value: 26000
      },
      {
        code: "AS-LOT-2026-X7803-002",
        crop: "Potato",
        variety: "Kufri Jyoti",
        netQty: 1200.0,
        harvestDate: "24 Oct 2026",
        plot: "Plot #2 (East Yard)",
        storage: "Under-Ground Silo #2",
        moisture: 14.5,
        status: "IN_TRANSIT", // Locked
        value: 36000
      },
      {
        code: "AS-LOT-2026-X7803-001",
        crop: "Cauliflower",
        variety: "Snowball 16",
        netQty: 420.0,
        harvestDate: "22 Oct 2026",
        plot: "Plot #3 (South Green)",
        storage: "Cool Shed #3",
        moisture: 11.2,
        status: "FARM_CUSTODY", // Editable
        value: 14700
      }
    ];

    // Language strings
    const I18N = {
      en: {
        farmCustody: "Farm Custody",
        inTransit: "In Transit",
        dispatched: "Dispatched",
        lotValuation: "Lot Valuation",
        tabLedger: "Harvest Lots & Ledger",
        tabAnalytics: "Analytics & Insights",
        newLot: "+ Lot",
        chartTitle: "Monthly Harvest Volume vs Valuation",
        cropShare: "Crop Production Share",
        navLedger: "Ledger",
        navAnalytics: "Analytics",
        navDispatch: "Dispatch",
        navProfile: "Profile",
        editLot: "Edit Lot",
        locked: "Locked"
      },
      hi: {
        farmCustody: "फार्म अभिरक्षा",
        inTransit: "पारगमन में",
        dispatched: "मंडी प्रेषित",
        lotValuation: "लॉट मूल्यांकन",
        tabLedger: "फसल लॉट एवं लेज़र",
        tabAnalytics: "विश्लेषण एवं अंतर्दृष्टि",
        newLot: "+ लॉट",
        chartTitle: "मासिक फसल मात्रा बनाम मूल्यांकन",
        cropShare: "फसल उत्पादन भागीदारी",
        navLedger: "लेज़र",
        navAnalytics: "विश्लेषण",
        navDispatch: "प्रेषण",
        navProfile: "प्रोफ़ाइल",
        editLot: "संपादित करें",
        locked: "तालाबंद"
      },
      bn: {
        farmCustody: "খামার হেফাজতে",
        inTransit: "পরিবহনে",
        dispatched: "মান্ডি প্রেরিত",
        lotValuation: "লটের মূল্যায়ন",
        tabLedger: "ফসল লট ও লেজার",
        tabAnalytics: "বিশ্লেষণ ও পরিসংখ্যান",
        newLot: "+ লট",
        chartTitle: "মাসিক ফসল উৎপাদন বনাম মূল্যায়ন",
        cropShare: "ফসল উৎপাদনের অনুপাত",
        navLedger: "লেজার",
        navAnalytics: "বিশ্লেষণ",
        navDispatch: "প্রেরণ",
        navProfile: "প্রোফাইল",
        editLot: "সম্পাদনা",
        locked: "লক করা"
      }
    };

    let currentLang = "en";

    function changeMobileLang(lang) {
      currentLang = lang;
      const dict = I18N[lang] || I18N.en;
      document.querySelectorAll('[data-i18n]').forEach(el => {
        const k = el.getAttribute('data-i18n');
        if (dict[k]) el.innerText = dict[k];
      });
      renderLots();
    }

    // Switch Tabs
    function switchMobileTab(tab) {
      const ledgerTab = document.getElementById('tabContentLedger');
      const analyticsTab = document.getElementById('tabContentAnalytics');
      const btnLedger = document.getElementById('tabBtnLedger');
      const btnAnalytics = document.getElementById('tabBtnAnalytics');
      const navLedger = document.getElementById('navItemLedger');
      const navAnalytics = document.getElementById('navItemAnalytics');

      if (tab === 'ledger') {
        ledgerTab.style.display = 'block';
        analyticsTab.style.display = 'none';
        btnLedger.classList.add('active');
        btnAnalytics.classList.remove('active');
        navLedger.classList.add('active');
        navAnalytics.classList.remove('active');
      } else {
        ledgerTab.style.display = 'none';
        analyticsTab.style.display = 'flex';
        btnLedger.classList.remove('active');
        btnAnalytics.classList.add('active');
        navLedger.classList.remove('active');
        navAnalytics.classList.add('active');
      }
    }

    // Render Lots List
    function renderLots(filterText = "", cropFilter = "ALL", plotFilter = "ALL") {
      const container = document.getElementById('mHarvestLotContainer');
      if (!container) return;
      container.innerHTML = "";

      const filtered = lots.filter(l => {
        const matchesSearch = !filterText ||
          l.code.toLowerCase().includes(filterText.toLowerCase()) ||
          l.crop.toLowerCase().includes(filterText.toLowerCase()) ||
          l.variety.toLowerCase().includes(filterText.toLowerCase());
        const matchesCrop = cropFilter === "ALL" || l.crop === cropFilter;
        const matchesPlot = plotFilter === "ALL" || l.plot.includes(plotFilter);
        return matchesSearch && matchesCrop && matchesPlot;
      });

      if (filtered.length === 0) {
        container.innerHTML = `<div style="text-align: center; padding: 30px 10px; color: #94a3b8; font-size: 13px;">No harvest lots match the criteria.</div>`;
        return;
      }

      const dict = I18N[currentLang] || I18N.en;

      filtered.forEach((l, idx) => {
        const isCustody = l.status === "FARM_CUSTODY";
        const custodyClass = isCustody ? "custody-farm" : "custody-transit";
        const custodyText = isCustody ? (currentLang === 'hi' ? 'फार्म अभिरक्षा' : (currentLang === 'bn' ? 'খামার হেফাজতে' : 'In Farm Custody')) : (currentLang === 'hi' ? 'पारगमन में' : (currentLang === 'bn' ? 'পরিবহনে' : 'In Transit to Mandi'));

        let actionBtnHtml = "";
        if (isCustody) {
          actionBtnHtml = `
            <button class="m-btn-action" onclick="openEditLotModal(${idx})">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
              <span>${dict.editLot}</span>
            </button>
          `;
        } else {
          actionBtnHtml = `
            <button class="m-btn-action locked" title="Locked: In transit custody cannot be modified until delivered">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
              <span>${dict.locked}</span>
            </button>
          `;
        }

        const card = document.createElement('div');
        card.className = "m-lot-card";
        card.innerHTML = `
          <div class="m-lot-card-header">
            <span class="m-lot-code-pill">${l.code}</span>
            <span class="m-custody-pill ${custodyClass}">
              <span style="display:inline-block; width:6px; height:6px; border-radius:50%; background:currentColor;"></span>
              ${custodyText}
            </span>
          </div>
          <div class="m-lot-title">${l.crop} (${l.variety})</div>
          <div class="m-lot-details-grid">
            <span>Net Weight: <strong>${l.netQty.toLocaleString()} kg</strong></span>
            <span>Harvested: <strong>${l.harvestDate}</strong></span>
            <span>Plot: <strong>${l.plot.split('(')[0]}</strong></span>
            <span>Moisture: <strong>${l.moisture}%</strong></span>
          </div>
          <div class="m-lot-actions-row">
            ${actionBtnHtml}
            <button class="m-btn-qr" onclick="showQrModal('${l.code}', '${l.crop}', ${l.netQty})">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
              <span>QR Code</span>
            </button>
          </div>
        `;
        container.appendChild(card);
      });
      updateKpis();
    }

    function filterLots() {
      const q = document.getElementById('lotSearchInput').value;
      const crop = document.getElementById('filterCrop').value;
      const plot = document.getElementById('filterPlot').value;
      renderLots(q, crop, plot);
    }

    function updateKpis() {
      let farmKg = 0;
      let transitKg = 0;
      let totalVal = 0;

      lots.forEach(l => {
        if (l.status === 'FARM_CUSTODY') {
          farmKg += l.netQty;
        } else if (l.status === 'IN_TRANSIT') {
          transitKg += l.netQty;
        }
        totalVal += (l.value || (l.netQty * 35));
      });

      document.getElementById('kpiFarm').innerText = farmKg.toLocaleString() + ' kg';
      document.getElementById('kpiTransit').innerText = transitKg.toLocaleString() + ' kg';
      document.getElementById('kpiValuation').innerText = '₹ ' + totalVal.toLocaleString();
    }

    // Modal helpers
    function openModal(id) {
      const el = document.getElementById(id);
      if (el) el.style.display = 'flex';
    }
    function closeModal(id) {
      const el = document.getElementById(id);
      if (el) el.style.display = 'none';
    }

    // New Lot Modal
    function openNewLotModal() {
      calcNetWeight();
      openModal('modalNewLot');
    }

    function calcNetWeight() {
      const gross = parseFloat(document.getElementById('formGross').value) || 0;
      const tare = parseFloat(document.getElementById('formTare').value) || 0;
      const net = Math.max(0, gross - tare);
      document.getElementById('formNet').value = net;
      if (!document.getElementById('formValue').value && net > 0) {
        document.getElementById('formValue').value = net * 40;
      }
    }

    function saveNewLot() {
      const crop = document.getElementById('formCrop').value;
      const variety = document.getElementById('formVariety').value.trim() || "Local Select";
      const net = parseFloat(document.getElementById('formNet').value) || 0;
      if (net <= 0) {
        alert("Please enter a valid gross weight greater than tare weight.");
        return;
      }
      const plot = document.getElementById('formPlot').value;
      const storage = document.getElementById('formStorage').value;
      const moisture = parseFloat(document.getElementById('formMoisture').value) || 12.0;
      const val = parseFloat(document.getElementById('formValue').value) || (net * 40);

      const nextNum = lots.length + 1;
      const pad = String(nextNum).padStart(3, '0');
      const newCode = `AS-LOT-2026-X7803-${pad}`;

      // Prepend to maintain latest to oldest
      lots.unshift({
        code: newCode,
        crop: crop,
        variety: variety,
        netQty: net,
        harvestDate: "26 Oct 2026",
        plot: plot,
        storage: storage,
        moisture: moisture,
        status: "FARM_CUSTODY",
        value: val
      });

      closeModal('modalNewLot');
      renderLots();
      showQrModal(newCode, crop, net);
    }

    // Edit Lot Modal
    function openEditLotModal(idx) {
      const l = lots[idx];
      if (!l || l.status !== 'FARM_CUSTODY') return;

      document.getElementById('editLotIndex').value = idx;
      document.getElementById('editLotCode').value = l.code;
      document.getElementById('editLotQty').value = l.netQty;
      document.getElementById('editLotVariety').value = l.variety;
      document.getElementById('editLotMoisture').value = l.moisture;
      document.getElementById('editLotStorage').value = l.storage;

      openModal('modalEditLot');
    }

    function saveEditedLot() {
      const idx = parseInt(document.getElementById('editLotIndex').value, 10);
      if (isNaN(idx) || !lots[idx]) return;

      const qty = parseFloat(document.getElementById('editLotQty').value) || lots[idx].netQty;
      lots[idx].netQty = qty;
      lots[idx].variety = document.getElementById('editLotVariety').value.trim() || lots[idx].variety;
      lots[idx].moisture = parseFloat(document.getElementById('editLotMoisture').value) || lots[idx].moisture;
      lots[idx].storage = document.getElementById('editLotStorage').value.trim() || lots[idx].storage;

      closeModal('modalEditLot');
      renderLots();
    }

    // QR Modal
    function showQrModal(code, crop, qty) {
      document.getElementById('qrDisplayCode').innerText = code;
      const wrap = document.getElementById('qrImageWrap');
      const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https%3A%2F%2Fannasutra.vercel.app%2Fq%2F${encodeURIComponent(code)}`;
      wrap.innerHTML = `<img src="${qrUrl}" alt="QR" style="width: 140px; height: 140px; display: block; border-radius: 4px;">`;
      openModal('modalQr');
    }

    // Dispatch Simulator
    function openDispatchModal() {
      const sel = document.getElementById('dispatchLotSelect');
      sel.innerHTML = "";
      const farmLots = lots.filter(l => l.status === 'FARM_CUSTODY');
      if (farmLots.length === 0) {
        alert("All lots are already dispatched or in transit.");
        return;
      }
      farmLots.forEach(l => {
        const opt = document.createElement('option');
        opt.value = l.code;
        opt.innerText = `${l.code} • ${l.crop} (${l.netQty} kg)`;
        sel.appendChild(opt);
      });
      openModal('modalDispatch');
    }

    function executeDispatch() {
      const sel = document.getElementById('dispatchLotSelect');
      const code = sel.value;
      const found = lots.find(l => l.code === code);
      if (found) {
        found.status = 'IN_TRANSIT';
        closeModal('modalDispatch');
        renderLots();
        alert(`Custody of ${code} dispatched. Lot is now LOCKED against editing until mandi weighment.`);
      }
    }

    function openProfileModal() {
      openModal('modalProfile');
    }

    // Initial render
    renderLots();
  </script>

</body>
</html>
"""

def main():
    target = Path("backend/apps/publicview/templates/publicview/mobile_preview.html")
    target.write_text(TEMPLATE_CONTENT, encoding="utf-8")
    print(f"Successfully wrote {len(TEMPLATE_CONTENT)} bytes to {target}")

if __name__ == "__main__":
    main()
