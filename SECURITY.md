# Security Policy

## Overview

FrameConverter takes security seriously. This document outlines our security measures and how to report vulnerabilities.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Measures

### 1. Command Injection Prevention

**✅ Protection Implemented**

- All FFmpeg commands are built using **argument lists** (not shell strings)
- `subprocess.Popen` is called with `shell=False` (default)
- No user input is directly concatenated into command strings
- All file paths are validated before use

**Example of secure command building:**
```python
# SECURE - Uses list of arguments
cmd = [
    '/usr/bin/ffmpeg',
    '-i', input_file,
    '-c:v', 'libx264',
    output_file
]
subprocess.Popen(cmd)  # shell=False by default

# INSECURE - DON'T DO THIS
# cmd = f"ffmpeg -i {input_file} -c:v libx264 {output_file}"
# subprocess.run(cmd, shell=True)  # Vulnerable to injection!
```

### 2. Path Traversal Prevention

**✅ Protection Implemented**

- All file paths are sanitized using `Path.resolve()`
- Suspicious patterns (`..`, `~`, `$`) are detected and logged
- Paths are converted to absolute paths before use
- File operations are restricted to valid directories

**Protection Function:**
```python
def sanitize_path(file_path: str) -> str:
    """Sanitize file path to prevent directory traversal attacks."""
    path = Path(file_path).resolve()
    # Additional validation...
    return str(path)
```

### 3. Input Validation

**✅ Protection Implemented**

All user inputs are validated before processing:

- **File paths**: Checked for existence, readability, and valid format
- **File extensions**: Only `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm` allowed
- **File sizes**: Minimum size check (prevents corrupted/empty files)
- **Directory permissions**: Write access verified before conversion
- **Disk space**: Checked before starting conversion

### 4. Resource Limits

**✅ Protection Implemented**

- **Timeouts**: All subprocess calls have timeout limits
  - FFprobe: 30 seconds
  - FFmpeg validation: 5 seconds
  - Conversion: No timeout (long videos), but cancellable
- **Graceful termination**: Cancel button safely terminates processes
- **Memory management**: Large files processed in streams, not loaded entirely

### 5. Error Handling

**✅ Protection Implemented**

- Detailed error logging without exposing sensitive information
- User-friendly error messages (technical details only in logs)
- No stack traces shown to users
- Failed conversions don't crash the application

### 6. File Permissions

**✅ Protection Implemented**

- Output directory creation uses `parents=True, exist_ok=True`
- Permission errors are caught and reported to user
- No elevation of privileges required
- Application runs with user permissions only

### 7. Dependency Security

**Dependencies:**
- `PyQt6 >= 6.6.0` - Official Qt framework for Python
- `ffmpeg` - System package, not bundled

**Security Considerations:**
- PyQt6 is actively maintained with security updates
- FFmpeg is a widely-used, well-audited tool
- No third-party network dependencies
- No automatic updates (user controls upgrades)

## What We DON'T Do

For transparency, here's what FrameConverter intentionally avoids:

- ❌ No network connections (fully offline application)
- ❌ No data collection or telemetry
- ❌ No automatic updates
- ❌ No code execution from user input
- ❌ No eval() or exec() anywhere in codebase
- ❌ No pickle or unsafe deserialization
- ❌ No shell=True in subprocess calls
- ❌ No SQL databases (no SQL injection risk)

## Reporting a Vulnerability

If you discover a security vulnerability, please follow responsible disclosure:

### DO:

1. **Email the maintainer privately**: Contact via X/Twitter DM [@pablothethinker](https://x.com/pablothethinker)
2. **Provide details**: Include steps to reproduce, impact assessment, and suggested fix (if any)
3. **Wait for response**: Allow reasonable time (7 days) for acknowledgment
4. **Coordinate disclosure**: Work with maintainer on timeline for public disclosure

### DON'T:

- ❌ Don't publicly disclose the vulnerability before a fix is available
- ❌ Don't exploit the vulnerability for malicious purposes
- ❌ Don't test on systems you don't own or have permission to test

## Vulnerability Response Process

When a vulnerability is reported:

1. **Acknowledgment** (within 7 days): Confirm receipt and provide timeline
2. **Assessment** (1-2 weeks): Evaluate severity and impact
3. **Fix Development** (2-4 weeks): Develop and test security patch
4. **Release** (coordinated): Release patch with security advisory
5. **Public Disclosure** (after fix): Publish details with credit to reporter

## Security Best Practices for Users

To stay secure when using FrameConverter:

### ✅ DO:

- **Keep software updated**: Update FrameConverter, PyQt6, and FFmpeg regularly
- **Verify downloads**: Only download from official GitHub repository
- **Check permissions**: Review file permissions in output directory
- **Use trusted sources**: Only convert videos from trusted sources
- **Monitor logs**: Check logs for suspicious activity
- **Run as user**: Don't run with sudo/root unless necessary

### ❌ DON'T:

- **Don't run as root**: No need for elevated privileges
- **Don't disable validation**: Don't modify security checks
- **Don't convert untrusted files**: Malformed videos can have issues
- **Don't ignore warnings**: Pay attention to security warnings in logs

## Security Audit History

| Date       | Auditor        | Findings | Status |
|------------|----------------|----------|--------|
| 2025-11-02 | Pablo (Author) | None     | ✅ Pass |

## Security Features Roadmap

Future security enhancements being considered:

- [ ] SHA-256 checksums for converted files
- [ ] Sandboxing for FFmpeg process (seccomp/AppArmor)
- [ ] File type validation using magic bytes (not just extensions)
- [ ] Optional file encryption for output
- [ ] Audit logging for all operations

## Contact

For security-related questions or concerns:

- **Security Issues**: DM on X/Twitter [@pablothethinker](https://x.com/pablothethinker)
- **General Issues**: [GitHub Issues](https://github.com/PabloTheThinker/frame-converter/issues)

## Acknowledgments

We thank the security research community for helping keep FrameConverter secure.

### Hall of Fame

No vulnerabilities have been reported yet. Be the first!

---

**Last Updated**: 2025-11-02  
**Next Review**: 2026-11-02
