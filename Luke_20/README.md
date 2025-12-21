# Luke_20

### `gogs_cve.py` usage

Did not work.
Found:

```url
/css/gogs.min.css?v=5084b4a9b77a506f5e287e82e945e1c6882b827a
/js/gogs.js?v=5084b4a9b77a506f5e287e82e945e1c6882b827a
```

Its a git commit version hash:
<https://github.com/gogs/gogs/commit/5084b4a9b77a506f5e287e82e945e1c6882b827a>
yeah, version 0.13.3, whitch is an unaffected version of rce (CVE-2024-56731)
but CVE-2025-8110 should work, but it does not.