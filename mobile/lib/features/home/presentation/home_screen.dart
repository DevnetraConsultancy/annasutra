import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../auth/presentation/controllers/auth_controller.dart';
import '../../auth/domain/auth_state.dart';
import '../../sync/sync_service.dart';

class HomeScreen extends ConsumerStatefulWidget {
  final void Function(Locale locale)? onLocaleChanged;

  const HomeScreen({super.key, this.onLocaleChanged});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

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

    return Scaffold(
      appBar: AppBar(
        title: const Text('AnnaSutra / অন্নসূত্র / अन्नसूत्र'),
        actions: [
          // Account / Login action icon
          IconButton(
            icon: Icon(
              authState.isAuthenticated ? Icons.account_circle : Icons.login,
              size: 28,
            ),
            tooltip: authState.isAuthenticated ? 'Account' : 'Login',
            onPressed: () {
              if (authState.isAuthenticated) {
                _showAccountDialog(context);
              } else {
                context.push('/login');
              }
            },
          ),
          PopupMenuButton<String>(
            icon: const Icon(Icons.language, size: 28),
            tooltip: 'Language / ভাষা / भाषा',
            onSelected: (String langCode) {
              widget.onLocaleChanged?.call(Locale(langCode));
            },
            itemBuilder: (BuildContext context) => <PopupMenuEntry<String>>[
              const PopupMenuItem<String>(
                value: 'en',
                child: Text('English', style: TextStyle(fontSize: 16)),
              ),
              const PopupMenuItem<String>(
                value: 'hi',
                child: Text('हिन्दी (Hindi)', style: TextStyle(fontSize: 16)),
              ),
              const PopupMenuItem<String>(
                value: 'bn',
                child: Text('বাংলা (Bengali)', style: TextStyle(fontSize: 16)),
              ),
            ],
          ),
          const SizedBox(width: 8),
        ],
        bottom: TabBar(
          controller: _tabController,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          indicatorColor: Colors.amber,
          indicatorWeight: 4,
          labelStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          tabs: const [
            Tab(text: 'Incoming'),
            Tab(text: 'My Stock'),
            Tab(text: 'Waiting'),
          ],
        ),
      ),
      body: Column(
        children: [
          // Unverified organisation banner
          if (authState.isAuthenticated && authState.orgVerification == 'PENDING')
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              color: Colors.amber.shade100,
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
                        fontSize: 13,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          // Sync status header bar with live outbox counter and manual sync button
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            color: syncState.pendingCount > 0 ? Colors.amber.shade50 : Colors.green.shade50,
            child: Row(
              children: [
                Icon(
                  syncState.pendingCount > 0 ? Icons.cloud_queue : Icons.cloud_done,
                  color: syncState.pendingCount > 0 ? Colors.amber.shade900 : Colors.green.shade800,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    syncState.pendingCount > 0
                        ? 'Offline Queue: ${syncState.pendingCount} events waiting to sync'
                        : 'Sync Status: All events synced',
                    style: TextStyle(
                      color: syncState.pendingCount > 0 ? Colors.amber.shade900 : Colors.green.shade900,
                      fontWeight: FontWeight.w600,
                      fontSize: 13,
                    ),
                  ),
                ),
                TextButton.icon(
                  onPressed: syncState.isSyncing
                      ? null
                      : () => ref.read(syncControllerProvider.notifier).syncNow(),
                  icon: syncState.isSyncing
                      ? const SizedBox(
                          width: 14,
                          height: 14,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.sync, size: 16),
                  label: Text(
                    syncState.isSyncing ? 'Syncing...' : 'Sync Now',
                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
          ),
          // Tab views
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                // Incoming Tab
                ListView(
                  padding: const EdgeInsets.all(16.0),
                  children: [
                    Card(
                      elevation: 2,
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                const Text(
                                  'BATCH: 7K3Q9XMD4T2B',
                                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: Colors.blue.shade100,
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Text(
                                    'In Transit',
                                    style: TextStyle(
                                      color: Colors.blue.shade900,
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            const Text('Tomato (hybrid) • Declared: 500.0 kg'),
                            const Text('From: Bardhaman Farmer Coop'),
                            const SizedBox(height: 12),
                            ElevatedButton.icon(
                              onPressed: () {
                                context.push('/receive?code=7K3Q9XMD4T2B&qty=500.0');
                              },
                              icon: const Icon(Icons.download_done),
                              label: const Text('Receive Batch / গ্রহণ করুন'),
                              style: ElevatedButton.styleFrom(
                                minimumSize: const Size.fromHeight(42),
                                backgroundColor: Colors.green.shade800,
                                foregroundColor: Colors.white,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
                // My Stock Tab
                ListView(
                  padding: const EdgeInsets.all(16.0),
                  children: [
                    Card(
                      elevation: 2,
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                const Text(
                                  'BATCH: 7K3Q9XMD4T2B',
                                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: Colors.green.shade100,
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Text(
                                    'In Custody',
                                    style: TextStyle(
                                      color: Colors.green.shade900,
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            const Text('Tomato (hybrid) • On Hand: 500.0 kg'),
                            const Text('Quality Grade: A (Fresh)'),
                            const SizedBox(height: 12),
                            ElevatedButton.icon(
                              onPressed: () {
                                context.push('/dispatch?code=7K3Q9XMD4T2B');
                              },
                              icon: const Icon(Icons.upload),
                              label: const Text('Dispatch Batch / প্রেরণ করুন'),
                              style: ElevatedButton.styleFrom(
                                minimumSize: const Size.fromHeight(42),
                                backgroundColor: Colors.blue.shade800,
                                foregroundColor: Colors.white,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
                // Waiting Tab
                ListView(
                  padding: const EdgeInsets.all(16.0),
                  children: [
                    Card(
                      elevation: 1,
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'BATCH: 7K3Q9XMD4T2B',
                              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                            ),
                            const SizedBox(height: 6),
                            const Text('Dispatched 500.0 kg to Kolkata Mandi Wholesaler'),
                            const SizedBox(height: 4),
                            Text(
                              'Status: Waiting for receiver confirmation',
                              style: TextStyle(color: Colors.amber.shade900, fontWeight: FontWeight.w600),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          // Action buttons bar with large accessible touch targets
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () {
                      context.push('/receive?code=7K3Q9XMD4T2B&qty=500.0');
                    },
                    icon: const Icon(Icons.qr_code_scanner, size: 24),
                    label: const Text('Scan QR'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      context.push('/create-batch');
                    },
                    icon: const Icon(Icons.add_box, size: 24),
                    label: const Text('Create Batch'),
                  ),
                ),
              ],
            ),
          ),
          // Disclaimer note required by docs/00_MASTER_BRIEF.md
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            color: Colors.grey.shade100,
            child: const Text(
              'Notice: Records are based on information entered by supply-chain participants. '
              'They do not prove physical package contents.',
              style: TextStyle(fontSize: 12, color: Colors.black54),
              textAlign: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }

  void _showAccountDialog(BuildContext context) {
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('User Account'),
        content: const Text('Logged in. Authenticated with hardware-backed key.'),
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
