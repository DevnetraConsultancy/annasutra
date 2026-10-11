import 'package:flutter/material.dart';

class HomeScreen extends StatefulWidget {
  final void Function(Locale locale)? onLocaleChanged;

  const HomeScreen({super.key, this.onLocaleChanged});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  int _selectedTabIndex = 0;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _tabController.addListener(() {
      if (_tabController.indexIsChanging) {
        setState(() {
          _selectedTabIndex = _tabController.index;
        });
      }
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('AnnaSutra / অন্নসূত্র / अन्नसूत्र'),
        actions: [
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
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Create Batch triggered')),
                      );
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
