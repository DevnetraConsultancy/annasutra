import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../auth/presentation/controllers/auth_controller.dart';
import '../../auth/domain/auth_state.dart';

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
          // Sync status header bar
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            color: Colors.green.shade50,
            child: Row(
              children: [
                Icon(Icons.cloud_done, color: Colors.green.shade800, size: 20),
                const SizedBox(width: 8),
                Text(
                  'Sync Status: All events synced',
                  style: TextStyle(
                    color: Colors.green.shade900,
                    fontWeight: FontWeight.w600,
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
                _buildListEmptyState('No incoming batches pending receipt.'),
                _buildListEmptyState('No batches currently held in stock.'),
                _buildListEmptyState('No handovers waiting for counterparties.'),
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
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Scan QR triggered')),
                      );
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
    showDialog(
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

  Widget _buildListEmptyState(String message) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Text(
          message,
          style: const TextStyle(fontSize: 16, color: Colors.black54),
          textAlign: TextAlign.center,
        ),
      ),
    );
  }
}
