# HelpBot Standalone Widget

The HelpBot widget is a browser-native Web Component (`<helpbot-assistant>`) encapsulated with Shadow DOM.

## Key Properties

- **Zero host framework dependency**: Works in Vue, React, Angular, or static HTML pages.
- **CSS isolation**: Styles are loaded inside the Shadow Root (`styles/helpbot-widget.css`), preventing host styles from breaking the widget or widget styles from leaking into the host.
- **Isolated API client**: `src/api-client.js` communicates directly with the configured `api_base_url` from `GET /api/widget-config`.
- **Context updates**: Listens for the `helpbot:context-changed` window event and queries the host adapter callback supplied during `configure(config, getContext)`.
- **Accessibility**: Includes ARIA dialog semantics, keyboard `Escape` to close, focus restoration to the launcher button, and `prefers-reduced-motion` support.

## Not Implemented in Baseline

The following UI capabilities are intentionally omitted until students complete their assignments:

- Voice microphone button and speech playback controls
- Video tutorial player cards and timestamp jump links
- Screenshot / image upload controls inside chat
