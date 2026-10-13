import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../auth/presentation/controllers/auth_controller.dart';
import '../../auth/domain/auth_state.dart';
import '../../auth/presentation/dpdp_consent_dialog.dart';
import '../../sync/sync_service.dart';

class HomeScreen extends ConsumerStatefulWidget {
  final void Function(Locale locale)? onLocaleChanged;

  const HomeScreen({super.key, this.onLocaleChanged});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  String _selectedLang = 'en';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final AuthState authState = ref.watch(authControllerProvider);
    final SyncState syncState = ref.watch(syncControllerProvider);
    final theme = Theme.of(context);
    final screenWidth = MediaQuery.of(context).size.width;
    final isDesktop = screenWidth >= 900;

    return Scaffold(
      backgroundColor: const Color(0xFFF6F8F5),
      body: SafeArea(
        child: Column(
          children: [
            // 1. TOP UTILITY HEADER (NPCI / Govt. of India Style)
            _buildTopUtilityBar(context),

            // 2. MAIN BRAND NAVIGATION BAR
            _buildMainNavBar(context, authState),

            // 3. SCROLLABLE MAIN CONTENT (Hero + Entity Login + Console + Footer)
            Expanded(
              child: SingleChildScrollView(
                child: Center(
                  child: ConstrainedBox(
                    constraints: BoxConstraints(maxWidth: isDesktop ? 1160 : double.infinity),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Cinematic Hero Banner with Live Stats
                        _buildHeroBanner(context, isDesktop),

                        // Offline Sync & Org Verification Alert Bar
                        _buildSyncAndVerificationAlerts(context, authState, syncState),

                        // Universal Entity Access & Login Section (Right on Home Page)
                        _buildUniversalEntityLoginSection(context, authState),

                        const SizedBox(height: 12),

                        // Ground-level Live Custody & Inventory Console
                        _buildOperationalConsole(context, theme),

                        const SizedBox(height: 16),

                        // Quick Accessible Action Bar (Scan QR + Create Batch)
                        _buildAccessibleActionButtons(context),

                        const SizedBox(height: 16),

                        // Official C-DAC Developer Footer & Statutory Disclaimers
                        _buildOfficialFooter(context),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ===========================================================================
  // SECTION 1: TOP UTILITY BAR (C-DAC Tech Partner & Language Switcher Dropdown)
  // ===========================================================================
  Widget _buildTopUtilityBar(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      decoration: const BoxDecoration(
        color: Color(0xFF07271D), // Deep dark green utility bar
        border: Border(bottom: BorderSide(color: Color(0xFF144D3B), width: 1)),
      ),
      child: Row(
        children: [
          // Developer Badge
          Image.asset(
            'assets/images/cdac_logo.png',
            height: 18,
            fit: BoxFit.contain,
            errorBuilder: (_, __, ___) => const Icon(Icons.memory, color: Colors.white70, size: 16),
          ),
          const SizedBox(width: 8),
          const Expanded(
            child: Text(
              'Developed by C-DAC | MeitY, Govt. of India',
              style: TextStyle(
                color: Color(0xFFE2E8F0),
                fontSize: 11,
                fontWeight: FontWeight.w600,
                letterSpacing: 0.2,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),

          // Small Language Switch Dropdown (EN / HI / BN)
          Container(
            height: 28,
            padding: const EdgeInsets.symmetric(horizontal: 8),
            decoration: BoxDecoration(
              color: const Color(0xFF114232),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(color: const Color(0xFF23654E), width: 1),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: _selectedLang,
                icon: const Icon(Icons.arrow_drop_down, color: Colors.white, size: 18),
                dropdownColor: const Color(0xFF0B3D2E),
                style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                items: const [
                  DropdownMenuItem(value: 'en', child: Text('🌐 EN')),
                  DropdownMenuItem(value: 'hi', child: Text('🌐 हिन्दी')),
                  DropdownMenuItem(value: 'bn', child: Text('🌐 বাংলা')),
                ],
                onChanged: (String? val) {
                  if (val != null) {
                    setState(() => _selectedLang = val);
                    widget.onLocaleChanged?.call(Locale(val));
                  }
                },
              ),
            ),
          ),
          const SizedBox(width: 8),

          // DPDP Act Privacy Shield Icon
          IconButton(
            icon: const Icon(Icons.shield_outlined, color: Color(0xFFF59E0B), size: 18),
            tooltip: 'DPDP Act Privacy & Consent',
            visualDensity: VisualDensity.compact,
            padding: EdgeInsets.zero,
            constraints: const BoxConstraints(minWidth: 28, minHeight: 28),
            onPressed: () => DpdpConsentDialog.show(context),
          ),
        ],
      ),
    );
  }

  // ===========================================================================
  // SECTION 2: MAIN BRAND NAVIGATION BAR (AnnaSutra Brand Emblem + Login Status)
  // ===========================================================================
  Widget _buildMainNavBar(BuildContext context, AuthState authState) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: const BoxDecoration(
        color: Color(0xFF0B3D2E), // Primary National Forest Green
        boxShadow: [
          BoxShadow(color: Colors.black26, blurRadius: 4, offset: Offset(0, 2)),
        ],
      ),
      child: Row(
        children: [
          // AnnaSutra Main Brand Emblem
          ClipRRect(
            borderRadius: BorderRadius.circular(20),
            child: Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                border: Border.all(color: const Color(0xFFE67E22), width: 1.5),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Image.asset(
                'assets/images/annasutra_emblem.jpg',
                fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => const CircleAvatar(
                  backgroundColor: Color(0xFF14532D),
                  child: Text('AS', style: TextStyle(color: Colors.amber, fontWeight: FontWeight.bold)),
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),

          // AnnaSutra Brand Name & Multilingual Subtitle
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  children: [
                    Text(
                      'AnnaSutra',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.w900,
                        letterSpacing: -0.3,
                      ),
                    ),
                    SizedBox(width: 6),
                    Text(
                      'অন্নসূত্র / अन्नसूत्र',
                      style: TextStyle(
                        color: Color(0xFFFCD34D),
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
                Text(
                  'National Agri-Produce Traceability Platform',
                  style: TextStyle(
                    color: Color(0xFFCBD5E1),
                    fontSize: 11,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),

          // User Account or Direct Login Button
          if (authState.isAuthenticated) ...[
            InkWell(
              onTap: () => _showAccountDialog(context),
              borderRadius: BorderRadius.circular(8),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: const Color(0xFF14532D),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: const Color(0xFF22C55E), width: 1),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.verified_user, color: Color(0xFF86EFAC), size: 16),
                    const SizedBox(width: 6),
                    Text(
                      authState.orgType ?? 'Entity User',
                      style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ),
            ),
          ] else ...[
            ElevatedButton.icon(
              onPressed: () => context.push('/login'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFE67E22), // Saffron Accent
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                minimumSize: const Size(80, 36),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
              icon: const Icon(Icons.login, size: 16),
              label: const Text('Login / প্রবেশ', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
            ),
          ],
        ],
      ),
    );
  }

  // ===========================================================================
  // SECTION 3: CINEMATIC NPCI-STYLE HERO BANNER WITH LIVE STATS RIBBON
  // ===========================================================================
  Widget _buildHeroBanner(BuildContext context, bool isDesktop) {
    return Container(
      margin: EdgeInsets.all(isDesktop ? 16.0 : 12.0),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        boxShadow: const [
          BoxShadow(color: Colors.black12, blurRadius: 10, offset: Offset(0, 4)),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: Stack(
          children: [
            // Photographic Backdrop: Farmer + Agri-officer in field
            Positioned.fill(
              child: Image.asset(
                'assets/images/hero_farm.jpg',
                fit: BoxFit.cover,
                alignment: Alignment.centerRight,
                errorBuilder: (_, __, ___) => Container(color: const Color(0xFF0B3D2E)),
              ),
            ),

            // NPCI-Inspired Gradient Overlay (Dark forest green on left for high readability)
            Positioned.fill(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.centerLeft,
                    end: Alignment.centerRight,
                    colors: [
                      const Color(0xFF07271D).withOpacity(0.96),
                      const Color(0xFF0B3D2E).withOpacity(0.90),
                      const Color(0xFF0B3D2E).withOpacity(0.60),
                      Colors.black.withOpacity(0.35),
                    ],
                    stops: const [0.0, 0.45, 0.75, 1.0],
                  ),
                ),
              ),
            ),

            // Hero Text Content & Live Stats
            Padding(
              padding: EdgeInsets.symmetric(
                horizontal: isDesktop ? 32.0 : 20.0,
                vertical: isDesktop ? 32.0 : 24.0,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Verification Seal Pill
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: const Color(0xFFE67E22).withOpacity(0.25),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: const Color(0xFFF59E0B), width: 1),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.verified, color: Color(0xFFFCD34D), size: 14),
                        SizedBox(width: 6),
                        Text(
                          'NATIONAL REPOSITORY • 100% IMMUTABLE LEDGER',
                          style: TextStyle(
                            color: Color(0xFFFEF3C7),
                            fontSize: 10,
                            fontWeight: FontWeight.w800,
                            letterSpacing: 0.5,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),

                  // Headline
                  Text(
                    'Empowering Farmers.\nProtecting Consumers.',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: isDesktop ? 32 : 24,
                      fontWeight: FontWeight.w900,
                      height: 1.15,
                      letterSpacing: -0.5,
                    ),
                  ),
                  const SizedBox(height: 8),

                  // Multilingual Subtitle
                  ConstrainedBox(
                    constraints: BoxConstraints(maxWidth: isDesktop ? 600 : double.infinity),
                    child: const Text(
                      'Direct cryptographic custody from seed to plate. Tamper-evident batch tracking '
                      'guaranteed by immutable MySQL tables and local SQLite offline sync.',
                      style: TextStyle(
                        color: Color(0xFFE2E8F0),
                        fontSize: 13,
                        fontWeight: FontWeight.w400,
                        height: 1.4,
                      ),
                    ),
                  ),
                  const SizedBox(height: 18),

                  // Quick Action Buttons
                  Wrap(
                    spacing: 12,
                    runSpacing: 10,
                    children: [
                      ElevatedButton.icon(
                        onPressed: () {
                          context.push('/receive?code=7K3Q9XMD4T2B&qty=500.0');
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFFE67E22), // Saffron Gold
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                          elevation: 2,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                        icon: const Icon(Icons.qr_code_scanner, size: 18),
                        label: const Text('Scan QR Code', style: TextStyle(fontWeight: FontWeight.bold)),
                      ),
                      OutlinedButton.icon(
                        onPressed: () {
                          context.push('/create-batch');
                        },
                        style: OutlinedButton.styleFrom(
                          foregroundColor: Colors.white,
                          side: const BorderSide(color: Colors.white, width: 1.5),
                          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                        icon: const Icon(Icons.add_box, size: 18),
                        label: const Text('New Harvest Lot', style: TextStyle(fontWeight: FontWeight.bold)),
                      ),
                    ],
                  ),

                  const SizedBox(height: 24),

                  // Live Stats Strip (NPCI Homepage Metric Style)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    decoration: BoxDecoration(
                      color: const Color(0xFF051B14).withOpacity(0.85),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0xFF1E4E3D), width: 1),
                    ),
                    child: Wrap(
                      spacing: 24,
                      runSpacing: 12,
                      alignment: WrapAlignment.spaceBetween,
                      children: [
                        _buildStatMetric('26 Tables', 'Immutable Ledger'),
                        _buildStatMetric('100%', 'Append-Only Triggers'),
                        _buildStatMetric('Offline SQLite', 'Resilient Field Sync'),
                        _buildStatMetric('DPDP 2023', 'Consent Protected'),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatMetric(String value, String label) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          value,
          style: const TextStyle(
            color: Color(0xFFFCD34D),
            fontSize: 16,
            fontWeight: FontWeight.w900,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            color: Color(0xFF94A3B8),
            fontSize: 11,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  // ===========================================================================
  // SECTION 4: OFFLINE SYNC STATUS & UNVERIFIED ORG BANNER
  // ===========================================================================
  Widget _buildSyncAndVerificationAlerts(BuildContext context, AuthState authState, SyncState syncState) {
    return Column(
      children: [
        // Pending verification banner
        if (authState.isAuthenticated && authState.orgVerification == 'PENDING')
          Container(
            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: Colors.amber.shade100,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.amber.shade400),
            ),
            child: Row(
              children: [
                Icon(Icons.warning_amber_rounded, color: Colors.amber.shade900, size: 22),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'Organisation Pending Verification: Batch operations are disabled until approved.',
                    style: TextStyle(
                      color: Colors.amber.shade900,
                      fontWeight: FontWeight.w600,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
          ),

        // Live Offline Outbox Counter & Manual Sync Trigger
        Container(
          margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
          decoration: BoxDecoration(
            color: syncState.pendingCount > 0 ? const Color(0xFFFFFBEB) : const Color(0xFFF0FDF4),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: syncState.pendingCount > 0 ? const Color(0xFFFCD34D) : const Color(0xFFBBF7D0),
            ),
          ),
          child: Row(
            children: [
              Icon(
                syncState.pendingCount > 0 ? Icons.cloud_queue : Icons.cloud_done,
                color: syncState.pendingCount > 0 ? Colors.amber.shade800 : Colors.green.shade800,
                size: 18,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  syncState.pendingCount > 0
                      ? 'Offline Queue: ${syncState.pendingCount} events waiting to sync'
                      : 'Sync Status: All events synced with Aiven Cloud',
                  style: TextStyle(
                    color: syncState.pendingCount > 0 ? Colors.amber.shade900 : Colors.green.shade900,
                    fontWeight: FontWeight.w600,
                    fontSize: 12,
                  ),
                ),
              ),
              TextButton.icon(
                onPressed: syncState.isSyncing
                    ? null
                    : () => ref.read(syncControllerProvider.notifier).syncNow(),
                icon: syncState.isSyncing
                    ? const SizedBox(
                        width: 12,
                        height: 12,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.sync, size: 14),
                label: Text(
                  syncState.isSyncing ? 'Syncing...' : 'Sync Now',
                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  // ===========================================================================
  // SECTION 5: UNIVERSAL ENTITY LOGIN (ALL ENTITIES LOGIN FROM HOME PAGE)
  // ===========================================================================
  Widget _buildUniversalEntityLoginSection(BuildContext context, AuthState authState) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE2E8F0)),
        boxShadow: const [
          BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, 1)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: const Color(0xFF0B3D2E).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.hub_outlined, color: Color(0xFF0B3D2E), size: 20),
              ),
              const SizedBox(width: 10),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Universal Entity Access / সংস্থা প্রবেশাধিকার',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF0F172A),
                      ),
                    ),
                    Text(
                      'Select your supply-chain tier for dedicated operations and custody tools',
                      style: TextStyle(
                        fontSize: 12,
                        color: Color(0xFF64748B),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),

          // 5 Supply-Chain Entity Cards
          LayoutBuilder(
            builder: (context, constraints) {
              final isWide = constraints.maxWidth > 700;
              return Wrap(
                spacing: 10,
                runSpacing: 10,
                children: [
                  _buildEntityCard(
                    context: context,
                    roleKey: 'FARMER',
                    icon: Icons.grass,
                    title: 'Farmer / FPO Producer',
                    subtitle: 'কৃষক / কৃষক উৎপাদক',
                    description: 'Harvest lot creation, farm bag QR codes, dispatch to mandi.',
                    width: isWide ? (constraints.maxWidth - 20) / 3 : constraints.maxWidth,
                    currentRole: authState.orgType,
                    sampleOrg: 'Bardhaman Farmer Coop (FPO-WB-0492)',
                  ),
                  _buildEntityCard(
                    context: context,
                    roleKey: 'MANDI',
                    icon: Icons.storefront,
                    title: 'Mandi Aggregator / APMC',
                    subtitle: 'মাণ্ডি ব্যবসায়ী / मंडी',
                    description: 'Inbound receipt, lot grading, lot splitting & auction dispatch.',
                    width: isWide ? (constraints.maxWidth - 20) / 3 : constraints.maxWidth,
                    currentRole: authState.orgType,
                    sampleOrg: 'Kolkata Central APMC Traders Ltd',
                  ),
                  _buildEntityCard(
                    context: context,
                    roleKey: 'COLD_STORAGE',
                    icon: Icons.ac_unit,
                    title: 'Cold Storage / Warehouse',
                    subtitle: 'হিমাগার / কোল্ড স্টোরেজ',
                    description: 'Inward custody receipt, temperature log, cold-chain outward.',
                    width: isWide ? (constraints.maxWidth - 20) / 3 : constraints.maxWidth,
                    currentRole: authState.orgType,
                    sampleOrg: 'Hooghly Cold Chain Logistics Ltd',
                  ),
                  _buildEntityCard(
                    context: context,
                    roleKey: 'PROCESSOR',
                    icon: Icons.precision_manufacturing,
                    title: 'Packhouse & Processor',
                    subtitle: 'খাদ্য প্রক্রিয়াকরণ ইউনিট',
                    description: 'Raw intake, milling/sorting, retail pack QR generation.',
                    width: isWide ? (constraints.maxWidth - 20) / 3 : constraints.maxWidth,
                    currentRole: authState.orgType,
                    sampleOrg: 'Bengal Agro Processing Works Pvt Ltd',
                  ),
                  _buildEntityCard(
                    context: context,
                    roleKey: 'RETAILER',
                    icon: Icons.shopping_basket,
                    title: 'Wholesaler & Retailer',
                    subtitle: 'খুচরা বিক্রেতা / কিরানা',
                    description: 'Point-of-sale verification, batch sales recording, consumer audit.',
                    width: isWide ? (constraints.maxWidth - 20) / 3 : constraints.maxWidth,
                    currentRole: authState.orgType,
                    sampleOrg: 'Maa Durga Retail Fresh Mart',
                  ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildEntityCard({
    required BuildContext context,
    required String roleKey,
    required IconData icon,
    required String title,
    required String subtitle,
    required String description,
    required double width,
    required String? currentRole,
    required String sampleOrg,
  }) {
    final bool isActive = currentRole == roleKey;

    return Container(
      width: width,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isActive ? const Color(0xFFF0FDF4) : const Color(0xFFFAFAFA),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: isActive ? const Color(0xFF22C55E) : const Color(0xFFE2E8F0),
          width: isActive ? 1.5 : 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: isActive ? const Color(0xFF16A34A) : const Color(0xFF0B3D2E),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, color: Colors.white, size: 18),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                    ),
                    Text(
                      subtitle,
                      style: TextStyle(color: Colors.amber.shade900, fontSize: 11, fontWeight: FontWeight.w600),
                    ),
                  ],
                ),
              ),
              if (isActive)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: const Color(0xFF16A34A),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: const Text('ACTIVE', style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
                ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            description,
            style: const TextStyle(fontSize: 11, color: Color(0xFF64748B), height: 1.3),
          ),
          const SizedBox(height: 10),
          SizedBox(
            width: double.infinity,
            height: 38,
            child: ElevatedButton.icon(
              onPressed: () {
                _showDirectEntityLoginModal(context, roleKey, title, sampleOrg);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: isActive ? const Color(0xFF15803D) : const Color(0xFF0B3D2E),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 10),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
              icon: Icon(isActive ? Icons.check_circle : Icons.login, size: 16),
              label: Text(
                isActive ? 'Logged In as $roleKey' : 'Login as $roleKey',
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ===========================================================================
  // SECTION 6: DIRECT ENTITY LOGIN MODAL (PHONE OTP OR 1-CLICK FIELD TEST)
  // ===========================================================================
  void _showDirectEntityLoginModal(BuildContext context, String roleKey, String roleTitle, String sampleOrg) {
    final phoneController = TextEditingController(text: '+919876543210');

    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(
          left: 20,
          right: 20,
          top: 20,
          bottom: MediaQuery.of(ctx).viewInsets.bottom + 24,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: Image.asset(
                    'assets/images/annasutra_emblem.jpg',
                    width: 32,
                    height: 32,
                    errorBuilder: (_, __, ___) => const Icon(Icons.shield, color: Colors.green),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Login: $roleTitle',
                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                      Text(
                        'Direct Entity Portal Access',
                        style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.pop(ctx),
                ),
              ],
            ),
            const Divider(height: 24),

            // Option 1: One-Click Instant Demo Login (For Field Workers / Quick Testing)
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFF0FDF4),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: const Color(0xFF86EFAC)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.flash_on, color: Color(0xFF15803D), size: 18),
                      const SizedBox(width: 6),
                      Text(
                        'Quick Field Test Access (1-Tap)',
                        style: TextStyle(color: Colors.green.shade900, fontWeight: FontWeight.bold, fontSize: 13),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Authenticates as $sampleOrg instantly without waiting for SMS.',
                    style: TextStyle(color: Colors.green.shade800, fontSize: 11),
                  ),
                  const SizedBox(height: 10),
                  SizedBox(
                    width: double.infinity,
                    height: 42,
                    child: ElevatedButton.icon(
                      onPressed: () async {
                        Navigator.pop(ctx);
                        await ref.read(authControllerProvider.notifier).quickLoginAsEntity(
                          entityRole: roleKey,
                          orgName: sampleOrg,
                          phone: '+919876543210',
                        );
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text('Successfully authenticated as $roleTitle ($sampleOrg)'),
                              backgroundColor: const Color(0xFF0B3D2E),
                            ),
                          );
                        }
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF15803D),
                        foregroundColor: Colors.white,
                      ),
                      icon: const Icon(Icons.touch_app, size: 18),
                      label: const Text('1-Tap Sign In as this Entity', style: TextStyle(fontWeight: FontWeight.bold)),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Option 2: Live Mobile Phone OTP
            const Text('Or Enter Mobile Number for OTP Verification:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            TextFormField(
              controller: phoneController,
              keyboardType: TextInputType.phone,
              decoration: const InputDecoration(
                labelText: 'Mobile (+91)',
                prefixIcon: Icon(Icons.phone),
                border: OutlineInputBorder(),
                isDense: true,
              ),
            ),
            const SizedBox(height: 12),
            SizedBox(
              height: 44,
              child: OutlinedButton.icon(
                onPressed: () {
                  Navigator.pop(ctx);
                  context.push('/login');
                },
                icon: const Icon(Icons.sms, size: 18),
                label: const Text('Proceed to OTP Verification'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ===========================================================================
  // SECTION 7: OPERATIONAL CUSTODY CONSOLE (INCOMING / MY STOCK / WAITING TABS)
  // ===========================================================================
  Widget _buildOperationalConsole(BuildContext context, ThemeData theme) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE2E8F0)),
        boxShadow: const [
          BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, 1)),
        ],
      ),
      child: Column(
        children: [
          // Tab bar header with accessible contrast
          Container(
            decoration: const BoxDecoration(
              color: Color(0xFF0B3D2E),
              borderRadius: BorderRadius.vertical(top: Radius.circular(13)),
            ),
            child: TabBar(
              controller: _tabController,
              labelColor: const Color(0xFFFCD34D),
              unselectedLabelColor: Colors.white70,
              indicatorColor: const Color(0xFFE67E22),
              indicatorWeight: 3.5,
              labelStyle: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
              tabs: const [
                Tab(text: 'Incoming'),
                Tab(text: 'My Stock'),
                Tab(text: 'Waiting'),
              ],
            ),
          ),

          // Tab content view (fixed height container or auto scrollable)
          SizedBox(
            height: 380,
            child: TabBarView(
              controller: _tabController,
              children: [
                // 1. Incoming Tab
                _buildIncomingTabContent(context),

                // 2. My Stock Tab
                _buildMyStockTabContent(context),

                // 3. Waiting Tab
                _buildWaitingTabContent(context),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildIncomingTabContent(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(14.0),
      children: [
        Card(
          elevation: 1,
          child: Padding(
            padding: const EdgeInsets.all(14.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'BATCH: 7K3Q9XMD4T2B',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: Colors.blue.shade100,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        'In Transit',
                        style: TextStyle(
                          color: Colors.blue.shade900,
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                const Text('Tomato (hybrid) • Declared: 500.0 kg', style: TextStyle(fontSize: 13)),
                const Text('From: Bardhaman Farmer Coop', style: TextStyle(fontSize: 12, color: Colors.black54)),
                const SizedBox(height: 12),
                ElevatedButton.icon(
                  onPressed: () {
                    context.push('/receive?code=7K3Q9XMD4T2B&qty=500.0');
                  },
                  icon: const Icon(Icons.download_done, size: 18),
                  label: const Text('Receive Batch / গ্রহণ করুন'),
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size.fromHeight(44),
                    backgroundColor: const Color(0xFF0B3D2E),
                    foregroundColor: Colors.white,
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildMyStockTabContent(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(14.0),
      children: [
        Card(
          elevation: 1,
          child: Padding(
            padding: const EdgeInsets.all(14.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'BATCH: 7K3Q9XMD4T2B',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: Colors.green.shade100,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        'In Custody',
                        style: TextStyle(
                          color: Colors.green.shade900,
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                const Text('Tomato (hybrid) • On Hand: 500.0 kg', style: TextStyle(fontSize: 13)),
                const Text('Quality Grade: A (Fresh)', style: TextStyle(fontSize: 12, color: Colors.black54)),
                const SizedBox(height: 10),
                ElevatedButton.icon(
                  onPressed: () {
                    context.push('/dispatch?code=7K3Q9XMD4T2B');
                  },
                  icon: const Icon(Icons.upload, size: 18),
                  label: const Text('Dispatch Batch / প্রেরণ করুন'),
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size.fromHeight(44),
                    backgroundColor: const Color(0xFF1E3A8A), // Navy Blue
                    foregroundColor: Colors.white,
                  ),
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    OutlinedButton.icon(
                      onPressed: () {
                        context.push('/split?code=7K3Q9XMD4T2B&qty=500.0');
                      },
                      icon: const Icon(Icons.call_split, size: 14),
                      label: const Text('Split Lot / লট ভাগ করুন', style: TextStyle(fontSize: 12)),
                    ),
                    OutlinedButton.icon(
                      onPressed: () {
                        context.push('/inspection?code=7K3Q9XMD4T2B');
                      },
                      icon: const Icon(Icons.verified, size: 14),
                      label: const Text('Inspect Quality / গুণমান পরীক্ষা', style: TextStyle(fontSize: 12)),
                    ),
                    OutlinedButton.icon(
                      onPressed: () {
                        context.push('/waste?code=7K3Q9XMD4T2B&qty=500.0');
                      },
                      icon: const Icon(Icons.delete_outline, size: 14),
                      label: const Text('Record Waste / ক্ষতি নথিভুক্ত করুন', style: TextStyle(fontSize: 12)),
                    ),
                    OutlinedButton.icon(
                      onPressed: () {
                        context.push('/sale?code=7K3Q9XMD4T2B&qty=500.0');
                      },
                      icon: const Icon(Icons.point_of_sale, size: 14),
                      label: const Text('Record Retail Sale / বিক্রি নথিভুক্ত করুন', style: TextStyle(fontSize: 12)),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 10),

        // Statutory Recall Notice Alert Card
        Card(
          color: Colors.red.shade50,
          shape: RoundedRectangleBorder(
            side: BorderSide(color: Colors.red.shade400, width: 1.5),
            borderRadius: BorderRadius.circular(10),
          ),
          child: const Padding(
            padding: EdgeInsets.all(12.0),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.warning, color: Colors.red, size: 24),
                SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'RECALL ALERT: LOT-RECALL-001',
                        style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold, fontSize: 13),
                      ),
                      SizedBox(height: 2),
                      Text(
                        'WARNING: This lot has an active RECALL notice. Do not distribute / এই লটটির প্রত্যাহার বিজ্ঞপ্তি রয়েছে।',
                        style: TextStyle(color: Colors.red, fontSize: 11),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildWaitingTabContent(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(14.0),
      children: [
        Card(
          elevation: 1,
          child: Padding(
            padding: const EdgeInsets.all(14.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'BATCH: 7K3Q9XMD4T2B',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                ),
                const SizedBox(height: 6),
                const Text('Dispatched 500.0 kg to Kolkata Mandi Wholesaler', style: TextStyle(fontSize: 13)),
                const SizedBox(height: 4),
                Text(
                  'Status: Waiting for receiver confirmation',
                  style: TextStyle(color: Colors.amber.shade900, fontWeight: FontWeight.w600, fontSize: 12),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  // ===========================================================================
  // SECTION 8: ACCESSIBLE TOUCH TARGET ACTION BUTTONS (SCAN QR & CREATE BATCH)
  // ===========================================================================
  Widget _buildAccessibleActionButtons(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0),
      child: Row(
        children: [
          Expanded(
            child: ElevatedButton.icon(
              onPressed: () {
                context.push('/receive?code=7K3Q9XMD4T2B&qty=500.0');
              },
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(120, 52), // Meets ≥48x48dp accessible requirement
                backgroundColor: const Color(0xFF0B3D2E),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              icon: const Icon(Icons.qr_code_scanner, size: 22),
              label: const Text('Scan QR', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: OutlinedButton.icon(
              onPressed: () {
                context.push('/create-batch');
              },
              style: OutlinedButton.styleFrom(
                minimumSize: const Size(120, 52),
                foregroundColor: const Color(0xFF0B3D2E),
                side: const BorderSide(color: Color(0xFF0B3D2E), width: 1.8),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              icon: const Icon(Icons.add_box, size: 22),
              label: const Text('Create Batch', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ),
          ),
        ],
      ),
    );
  }

  // ===========================================================================
  // SECTION 9: OFFICIAL GOVERNMENT & C-DAC FOOTER & STATUTORY DISCLAIMER
  // ===========================================================================
  Widget _buildOfficialFooter(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 16),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
      decoration: const BoxDecoration(
        color: Color(0xFF07271D), // Dark Government Emerald
        border: Border(top: BorderSide(color: Color(0xFF144D3B), width: 1.5)),
      ),
      child: Column(
        children: [
          // Partner logos in footer
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: Image.asset(
                  'assets/images/annasutra_emblem.jpg',
                  width: 32,
                  height: 32,
                  errorBuilder: (_, __, ___) => const Icon(Icons.grain, color: Colors.amber),
                ),
              ),
              const SizedBox(width: 12),
              const Text(
                'AnnaSutra',
                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
              ),
              const SizedBox(width: 20),
              Container(width: 1, height: 24, color: Colors.white24),
              const SizedBox(width: 20),
              Image.asset(
                'assets/images/cdac_logo.png',
                height: 24,
                errorBuilder: (_, __, ___) => const Icon(Icons.memory, color: Colors.white70),
              ),
            ],
          ),
          const SizedBox(height: 12),

          const Text(
            'Developed by Centre for Development of Advanced Computing (C-DAC)',
            style: TextStyle(color: Color(0xFFE2E8F0), fontSize: 12, fontWeight: FontWeight.w600),
            textAlign: TextAlign.center,
          ),
          const Text(
            'Ministry of Electronics & Information Technology, Government of India',
            style: TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 14),

          // Mandatory Disclaimer required by docs/00_MASTER_BRIEF.md
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Colors.black.withOpacity(0.25),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.white12),
            ),
            child: const Text(
              'Notice: Records are based on information entered by supply-chain participants. '
              'They do not prove physical package contents.',
              style: TextStyle(fontSize: 11, color: Color(0xFFCBD5E1), height: 1.3),
              textAlign: TextAlign.center,
            ),
          ),
          const SizedBox(height: 10),

          // DPDP grievance link
          TextButton(
            onPressed: () => DpdpConsentDialog.show(context),
            child: const Text(
              'DPDP Act 2023 Compliance & Grievance Redressal Officer: grievance@annasutra.in',
              style: TextStyle(color: Color(0xFFFCD34D), fontSize: 11),
              textAlign: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }

  void _showAccountDialog(BuildContext context) {
    final authState = ref.read(authControllerProvider);
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('User Account'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Entity: ${authState.orgName ?? authState.orgType ?? "Authenticated Operator"}', style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            Text('Phone: ${authState.phone ?? "+919876543210"}'),
            const SizedBox(height: 4),
            Text('Status: ${authState.orgVerification ?? "VERIFIED"}', style: const TextStyle(color: Colors.green, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            const Text('Authenticated with cryptographic key-pair.', style: TextStyle(fontSize: 12, color: Colors.black54)),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(ctx);
              ref.read(authControllerProvider.notifier).logout();
            },
            child: const Text('Log Out', style: TextStyle(color: Colors.red)),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}
