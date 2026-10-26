import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'home_screen.dart';

/// Full-fidelity native Android web app shell.
/// Delivers the exact AnnaSutra Web Application (registration, plots, documents,
/// admin portal, harvest lot ledger, unlimited QR codes, and analytics)
/// directly inside the Android APK with native pull-to-refresh, hardware back button
/// navigation, camera access, and offline connection retry.
class WebPortalScreen extends StatefulWidget {
  final void Function(Locale)? onLocaleChanged;
  final String initialUrl;

  const WebPortalScreen({
    super.key,
    this.onLocaleChanged,
    this.initialUrl = 'https://annasutra.vercel.app/',
  });

  @override
  State<WebPortalScreen> createState() => _WebPortalScreenState();
}

class _WebPortalScreenState extends State<WebPortalScreen> {
  WebViewController? _controller;
  bool _isLoading = true;
  double _progress = 0.0;
  bool _hasError = false;
  String _errorMessage = '';
  bool _isNativeOfflineMode = false;

  @override
  void initState() {
    super.initState();
    if (!kIsWeb) {
      _initWebView();
    }
  }

  void _initWebView() {
    final controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(const Color(0xFF062319))
      ..setNavigationDelegate(
        NavigationDelegate(
          onProgress: (int progress) {
            if (mounted) {
              setState(() {
                _progress = progress / 100.0;
              });
            }
          },
          onPageStarted: (String url) {
            if (mounted) {
              setState(() {
                _isLoading = true;
                _hasError = false;
              });
            }
          },
          onPageFinished: (String url) {
            if (mounted) {
              setState(() {
                _isLoading = false;
              });
            }
          },
          onWebResourceError: (WebResourceError error) {
            // Only trigger offline error screen on main-frame network errors
            if (error.isForMainFrame ?? true) {
              if (mounted) {
                setState(() {
                  _hasError = true;
                  _errorMessage = error.description;
                  _isLoading = false;
                });
              }
            }
          },
        ),
      )
      ..loadRequest(Uri.parse(widget.initialUrl));

    _controller = controller;
  }

  Future<void> _handleRefresh() async {
    if (_controller != null) {
      await _controller!.reload();
    }
  }

  void _toggleNativeOfflineMode() {
    setState(() {
      _isNativeOfflineMode = !_isNativeOfflineMode;
    });
  }

  @override
  Widget build(BuildContext context) {
    // In headless test environments or Web preview, fall back to native HomeScreen
    if (kIsWeb || _isNativeOfflineMode || _controller == null) {
      return Stack(
        children: [
          HomeScreen(onLocaleChanged: widget.onLocaleChanged),
          if (!kIsWeb)
            Positioned(
              bottom: 70,
              right: 16,
              child: FloatingActionButton.extended(
                backgroundColor: const Color(0xFF064E3B),
                foregroundColor: Colors.white,
                icon: const Icon(Icons.public, size: 20),
                label: const Text('Back to Web Portal', style: TextStyle(fontWeight: FontWeight.bold)),
                onPressed: _toggleNativeOfflineMode,
              ),
            ),
        ],
      );
    }

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) async {
        if (didPop) return;
        if (_controller != null && await _controller!.canGoBack()) {
          await _controller!.goBack();
        } else {
          if (context.mounted) {
            Navigator.of(context).maybePop();
          }
        }
      },
      child: Scaffold(
        backgroundColor: const Color(0xFF091A14),
        appBar: AppBar(
          backgroundColor: const Color(0xFF064E3B),
          foregroundColor: Colors.white,
          elevation: 2,
          titleSpacing: 0,
          title: Row(
            children: [
              const SizedBox(width: 8),
              Container(
                width: 28,
                height: 28,
                decoration: BoxDecoration(
                  color: const Color(0xFF022C22),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: const Icon(Icons.eco, color: Color(0xFF10B981), size: 18),
              ),
              const SizedBox(width: 8),
              const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'AnnaSutra',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900, letterSpacing: 0.3),
                  ),
                  Text(
                    'Government of India AgriTrace',
                    style: TextStyle(fontSize: 10, color: Color(0xFFA7F3D0), fontWeight: FontWeight.w600),
                  ),
                ],
              ),
            ],
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.arrow_back_ios, size: 16),
              tooltip: 'Go Back',
              onPressed: () async {
                if (_controller != null && await _controller!.canGoBack()) {
                  await _controller!.goBack();
                }
              },
            ),
            IconButton(
              icon: const Icon(Icons.refresh, size: 20),
              tooltip: 'Reload Portal',
              onPressed: _handleRefresh,
            ),
            PopupMenuButton<String>(
              icon: const Icon(Icons.more_vert, size: 20),
              color: const Color(0xFF062319),
              itemBuilder: (context) => [
                const PopupMenuItem(
                  value: 'offline',
                  child: Row(
                    children: [
                      Icon(Icons.offline_pin_outlined, color: Color(0xFF10B981), size: 18),
                      SizedBox(width: 8),
                      Text('Offline Farm Ledger', style: TextStyle(color: Colors.white, fontSize: 13)),
                    ],
                  ),
                ),
                const PopupMenuItem(
                  value: 'home',
                  child: Row(
                    children: [
                      Icon(Icons.home_outlined, color: Color(0xFF10B981), size: 18),
                      SizedBox(width: 8),
                      Text('Portal Home', style: TextStyle(color: Colors.white, fontSize: 13)),
                    ],
                  ),
                ),
              ],
              onSelected: (val) {
                if (val == 'offline') {
                  _toggleNativeOfflineMode();
                } else if (val == 'home') {
                  _controller?.loadRequest(Uri.parse(widget.initialUrl));
                }
              },
            ),
            const SizedBox(width: 4),
          ],
          bottom: _isLoading
              ? PreferredSize(
                  preferredSize: const Size.fromHeight(3.0),
                  child: LinearProgressIndicator(
                    value: _progress > 0 ? _progress : null,
                    backgroundColor: const Color(0xFF04241A),
                    valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF10B981)),
                    minHeight: 3,
                  ),
                )
              : null,
        ),
        body: _hasError
            ? _buildOfflineErrorView()
            : RefreshIndicator(
                color: const Color(0xFF10B981),
                backgroundColor: const Color(0xFF064E3B),
                onRefresh: _handleRefresh,
                child: WebViewWidget(controller: _controller!),
              ),
      ),
    );
  }

  Widget _buildOfflineErrorView() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: const Color(0xFF062319),
                shape: BoxShape.circle,
                border: Border.all(color: const Color(0xFF10B981), width: 2),
              ),
              child: const Icon(Icons.wifi_off_rounded, size: 48, color: Color(0xFFF59E0B)),
            ),
            const SizedBox(height: 20),
            const Text(
              'No Internet Connection',
              style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              _errorMessage.isNotEmpty
                  ? _errorMessage
                  : 'Unable to reach AnnaSutra servers. Please check your data connection.',
              textAlign: TextAlign.center,
              style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13, height: 1.5),
            ),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF10B981),
                    foregroundColor: const Color(0xFF064E3B),
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  icon: const Icon(Icons.refresh, size: 18),
                  label: const Text('Retry Connection', style: TextStyle(fontWeight: FontWeight.w800)),
                  onPressed: _handleRefresh,
                ),
                const SizedBox(width: 12),
                OutlinedButton.icon(
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFFA7F3D0),
                    side: const BorderSide(color: Color(0xFF10B981)),
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  icon: const Icon(Icons.offline_pin, size: 18),
                  label: const Text('Offline Mode', style: TextStyle(fontWeight: FontWeight.w700)),
                  onPressed: _toggleNativeOfflineMode,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
