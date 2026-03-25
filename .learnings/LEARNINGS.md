# Learnings

Raw lessons, corrections, and best practices that are not yet promoted.

## [LRN-20260324-001] gogcli-under-wsl-headless-may-need-file-keyring-

**Logged**: 2026-03-24T09:47:50-04:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
gogcli under WSL/headless may need file keyring + local password wrapper

### Details
Without a usable desktop keychain, gog auth token storage failed in WSL with 'no TTY available for keyring file backend password prompt'. A local password file plus wrapper exporting GOG_KEYRING_PASSWORD allowed the file backend to work.

### Suggested Action
If gog auth fails under WSL/headless, switch to file keyring and ensure GOG_KEYRING_PASSWORD is set non-interactively before exchanging the OAuth callback.

### Metadata
- Source: tool_failure
- Related Files: none
- Tags: gog, gogcli, wsl, oauth, keyring
- See Also: none

---
