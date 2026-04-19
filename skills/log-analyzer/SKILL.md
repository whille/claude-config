---
version: 1.0.0
name: log-analyzer
description: "Analyze logs to identify errors, patterns, and root causes. Use when debugging production issues, investigating failures, or understanding log patterns. Triggers on: analyze logs, log analysis, debug logs, parse logs, error patterns, 日志分析, find root cause in logs."
user-invocable: true
argument-hint: "<log-file-path or log-directory>"
triggers:
  - "analyze logs"
  - "log analysis"
  - "debug logs"
  - "parse logs"
  - "error patterns"
  - "日志分析"
  - "find root cause"
  - "log investigation"
  - "trace errors"
last_updated: 2026-04-19
---

# Log Analyzer

A structured workflow for analyzing logs to identify errors, patterns, and root causes. Designed for production debugging, incident investigation, and systematic log analysis.

---

## The Job

Parse log files or directories, identify error patterns, cluster similar errors, and produce a root cause analysis with actionable recommendations.

---

## When to Activate

- User says "analyze logs", "log analysis", "debug logs", "parse logs"
- User asks about error patterns or root cause investigation
- User provides a log file or directory for investigation
- Production incident debugging scenarios
- CI/CD failure investigation
- Application crash analysis
- "find the error" or "what's causing this" with log context

---

## When NOT to Use

- User just wants to read a single log line (use Read tool)
- User wants to modify log configuration
- User wants to set up logging (that's infrastructure work)
- User is asking about log shipping/ingestion pipelines

---

## Log Analysis Workflow

### Phase 1: Log Collection

```markdown
1. Identify log sources:
   - File path(s) provided by user
   - Standard locations: /var/log/, ~/.claude/logs/, .omc/logs/
   - Pattern matching: *.log, *.txt, errors.*

2. Gather metadata:
   - Log file size
   - Number of lines/entries
   - Time range (if timestamps available)
   - Log format detection

3. Report collection summary:
   ```
   Logs collected: 3 files, 15,432 lines
   Time range: 2026-04-19 10:00:00 to 2026-04-19 14:52:18
   Formats detected: JSON, Apache Combined
   ```
```

### Phase 2: Format Detection

Automatically detect log format from sample:

| Format | Detection Pattern | Parser |
|--------|------------------|--------|
| JSON | `{.*"timestamp".*}` | JSON parse |
| Apache Combined | `IP - - [date] "METHOD URL"` | Regex |
| Nginx | Similar to Apache | Regex |
| Syslog | `Month Day HH:MM:SS hostname` | Regex |
| Python | `YYYY-MM-DD HH:MM:SS,ms LEVEL module:message` | Regex |
| Java log4j | `YYYY-MM-dd HH:mm:ss,SSS LEVEL [thread] class - message` | Regex |
| Node.js | `timestamp level: message` or JSON | Flexible |
| Custom | User-specified pattern | Configurable |

### Phase 3: Error Pattern Recognition

#### Critical Patterns (Immediate Attention)

| Priority | Pattern Type | Regex/Match | Severity |
|----------|-------------|-------------|----------|
| P0 | Uncaught Exception | `Uncaught|Unhandled|FATAL|Fatal` | Critical |
| P0 | Stack Overflow | `StackOverflow|Maximum call stack` | Critical |
| P0 | Out of Memory | `OutOfMemory|OOM|cannot allocate` | Critical |
| P0 | Connection Refused | `Connection refused|ECONNREFUSED` | Critical |
| P0 | Database Failure | `database.*error|DB.*failed|connection pool exhausted` | Critical |

#### High Priority Patterns

| Priority | Pattern Type | Regex/Match | Severity |
|----------|-------------|-------------|----------|
| P1 | HTTP 5xx | `5[0-9]{2}|500|502|503|504` | High |
| P1 | Timeout | `timeout|timed out|ETIMEDOUT` | High |
| P1 | Authentication Failure | `authentication failed|invalid token|401|Unauthorized` | High |
| P1 | Permission Denied | `permission denied|403|Forbidden|EACCES` | High |

#### Medium Priority Patterns

| Priority | Pattern Type | Regex/Match | Severity |
|----------|-------------|-------------|----------|
| P2 | HTTP 4xx | `4[0-9]{2}|400|404` | Medium |
| P2 | Warnings | `WARN|Warning|warn` | Medium |
| P2 | Deprecation | `deprecated|DeprecationWarning` | Medium |
| P2 | Retry | `retrying|retry attempt` | Medium |

#### Common Error Signatures

```python
# Python Traceback
Pattern: r'Traceback \(most recent call last\):.*?(\w+Error|Exception): (.+)'
Extract: exception_type, error_message

# JavaScript Error
Pattern: r'(Error|TypeError|ReferenceError|SyntaxError): (.+)'
Extract: error_type, error_message

# Java Exception
Pattern: r'(\w+Exception|Error): (.+?)(?:\n\s+at )'
Extract: exception_type, error_message

# Connection Errors
Pattern: r'(ConnectionRefusedError|ConnectionResetError|TimeoutError)[:\s]+(.+)'
Extract: error_type, context

# HTTP Status
Pattern: r'(GET|POST|PUT|DELETE|PATCH) ([^\s]+) (\d{3})'
Extract: method, path, status_code
```

### Phase 4: Error Clustering

Group similar errors to identify patterns:

```markdown
Cluster Algorithm:
1. Normalize error messages (remove timestamps, IDs, variable data)
2. Extract error signature
3. Group by signature
4. Count occurrences per cluster
5. Rank by frequency and severity

Output:
| Cluster ID | Pattern | Count | First Seen | Last Seen | Severity |
|------------|---------|-------|------------|-----------|----------|
| E001 | Connection refused to database | 47 | 10:23:15 | 10:45:02 | Critical |
| E002 | HTTP 503 on /api/health | 23 | 10:25:00 | 10:50:00 | High |
| E003 | Rate limit exceeded | 156 | 10:00:00 | 10:55:00 | Medium |
```

### Phase 5: Root Cause Analysis

Trace error chains to identify root cause:

```markdown
Analysis Steps:
1. Identify triggering error (first error in chain)
2. Follow causal links (what caused subsequent errors)
3. Build error propagation graph
4. Identify root cause candidates
5. Score candidates by:
   - Timing (earliest errors)
   - Dependency graph position
   - Cross-reference with codebase

Root Cause Candidates:
| Rank | Error | Evidence | Confidence |
|------|-------|----------|------------|
| 1 | Database connection pool exhausted | 47 connection errors after 10:23, pool size = 10 | High |
| 2 | Memory pressure | GC logs show high frequency, heap at 95% | Medium |
```

### Phase 6: Time Series Analysis

Analyze error distribution over time:

```markdown
Timeline View:
10:00 ════════════════════════════════════ Normal
10:20 ═══════════════╔════════════════════ First errors appear
10:23 ═══════════════╬════════════════════ Connection pool exhaustion
10:25 ═══════════════╬════════════════════ Cascade: API failures start
10:30 ═══════════════╬════════════════════ Peak: 156 errors/min
10:45 ═══════════════╚════════════════════ Recovery starts
10:55 ════════════════════════════════════ Normal

Error Rate Graph:
  200 │
  150 │        ████
  100 │     ████████
   50 │   ████████████
    0 └──┬──────────────
       10:00  10:30  11:00
```

### Phase 7: Generate Report

```markdown
# Log Analysis Report

## Summary
- Total log entries: 15,432
- Errors found: 342 (2.2%)
- Unique error patterns: 15
- Root cause confidence: High

## Critical Findings

### Root Cause: Database Connection Pool Exhaustion
- **Impact**: 47 API failures, 23 health check failures
- **Evidence**: Connection pool limited to 10, traffic spike at 10:23
- **Recommendation**: Increase pool size or add connection pooling

### Secondary Issue: Memory Pressure
- **Impact**: GC pause time increased 3x
- **Evidence**: Heap usage at 95%, frequent full GC
- **Recommendation**: Increase heap size or investigate memory leaks

## Error Distribution
| Type | Count | Percentage |
|------|-------|------------|
| Connection Errors | 47 | 13.7% |
| HTTP 503 | 23 | 6.7% |
| Rate Limit | 156 | 45.6% |
| Warnings | 116 | 33.9% |

## Recommendations
1. [P0] Increase database connection pool from 10 to 25
2. [P0] Add connection pool monitoring and alerting
3. [P1] Increase JVM heap from 2GB to 4GB
4. [P2] Review rate limiting strategy (156 limit hits)
```

---

## Usage Examples

### Example 1: Single File Analysis

```
/log-analyzer /var/log/app/error.log
```

Output:
- File info: 5,432 lines, 2026-04-19 08:00 - 14:00
- 23 errors found across 5 unique patterns
- Root cause: Redis connection timeout

### Example 2: Directory Analysis

```
/log-analyzer /var/log/app/
```

Output:
- Scans all *.log files in directory
- Cross-file error correlation
- Time-synchronized timeline

### Example 3: Pattern-Specific Search

```
/log-analyzer /var/log/app/ --pattern "connection refused"
```

Output:
- All entries matching pattern
- Context around each match
- Aggregated statistics

### Example 4: Time Range Filter

```
/log-analyzer /var/log/app/ --from "2026-04-19 10:00" --to "2026-04-19 11:00"
```

Output:
- Only entries within time range
- Focused timeline analysis

---

## Integration with Other Tools

### With debugger Agent
```
/log-analyzer finds root cause
→ debugger agent fixes the code
```

### With code-reviewer
```
/log-analyzer identifies problematic patterns
→ code-reviewer checks for similar issues elsewhere
```

### With OMC trace
```
/log-analyzer provides evidence
→ /trace investigates causal chain deeper
```

---

## Output Formats

### Terminal Summary (Default)
```
Log Analysis Summary
━━━━━━━━━━━━━━━━━━━━━━
Files: 3 | Lines: 15,432 | Errors: 342
Root Cause: Database connection pool exhaustion
Confidence: High

Top 3 Errors:
  1. [47x] Connection refused to database
  2. [23x] HTTP 503 Service Unavailable
  3. [156x] Rate limit exceeded

Recommended Actions:
  1. Increase connection pool size
  2. Add connection monitoring
```

### JSON Output (--format json)
```json
{
  "summary": {
    "files": 3,
    "lines": 15432,
    "errors": 342,
    "uniquePatterns": 15
  },
  "rootCause": {
    "error": "Database connection pool exhaustion",
    "confidence": "high",
    "evidence": ["47 connection errors", "pool size = 10"]
  },
  "clusters": [
    {"id": "E001", "pattern": "Connection refused", "count": 47}
  ],
  "recommendations": [
    "Increase connection pool size to 25",
    "Add connection pool monitoring"
  ]
}
```

### Markdown Report (--format md)
Full markdown report suitable for documentation or PR comment.

---

## Error Pattern Library

### Infrastructure Errors

| Pattern | Signature | Likely Cause |
|---------|-----------|--------------|
| DNS Resolution Failure | `ENOTFOUND|getaddrinfo` | DNS issues, wrong hostname |
| Connection Refused | `ECONNREFUSED` | Service down, firewall |
| Connection Reset | `ECONNRESET` | Remote closed, timeout |
| Connection Timeout | `ETIMEDOUT|timed out` | Network issue, overload |

### Application Errors

| Pattern | Signature | Likely Cause |
|---------|-----------|--------------|
| Null Pointer | `NullPointerException|null|undefined` | Missing null check |
| Index Out of Bounds | `IndexError|ArrayIndexOutOfBounds` | Invalid array access |
| Type Error | `TypeError|ClassCastException` | Type mismatch |
| Memory Error | `OutOfMemoryError|MemoryError` | Memory leak, insufficient heap |

### Database Errors

| Pattern | Signature | Likely Cause |
|---------|-----------|--------------|
| Deadlock | `deadlock|Deadlock found` | Lock contention |
| Connection Pool | `pool exhausted|cannot get connection` | Too many concurrent requests |
| Query Timeout | `query timeout|lock wait timeout` | Slow query, missing index |
| Constraint Violation | `constraint|IntegrityError` | Data integrity issue |

---

## Command-Line Options

```
log-analyzer <path> [options]

Arguments:
  path                  Log file or directory to analyze

Options:
  --format <type>       Output format: summary, json, md (default: summary)
  --pattern <regex>     Search for specific pattern
  --level <level>       Filter by log level: error, warn, info, debug
  --from <timestamp>    Start time for analysis
  --to <timestamp>      End time for analysis
  --top <n>             Show top N errors (default: 10)
  --context <lines>     Lines of context around errors (default: 3)
```

---

## Best Practices

1. **Start with summary**: Get overview before diving deep
2. **Focus on critical errors first**: P0 patterns indicate core issues
3. **Look for patterns, not individual errors**: The 47th error is likely related to the 1st
4. **Correlate with deploy timeline**: Errors starting after deployment point to change
5. **Save reports for comparison**: Before/after analysis validates fixes

---

## Final Checklist

- [ ] Collected all relevant log files
- [ ] Detected log format correctly
- [ ] Applied pattern recognition rules
- [ ] Clustered similar errors
- [ ] Identified root cause with evidence
- [ ] Generated timeline visualization
- [ ] Provided actionable recommendations
- [ ] Output in requested format
