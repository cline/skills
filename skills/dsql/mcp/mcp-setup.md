## Plugin Default Configuration

The plugin ships with a documentation-only `.mcp.json` at the plugin root (no cluster endpoint, no `--allow-writes`). This means the MCP server provides DSQL documentation search, reading, and recommendations out of the box without requiring any cluster connection.

To enable database operations (queries, schema exploration, DDL, DML), users must update the plugin's `.mcp.json` with their cluster details.

### Default Documentation-Only Config

The plugin's `.mcp.json` is pre-configured as follows:

```json
{
  "mcpServers": {
    "aurora-dsql": {
      "command": "uvx",
      "args": ["awslabs.aurora-dsql-mcp-server@latest"],
      "env": { "FASTMCP_LOG_LEVEL": "ERROR" },
      "disabled": true
    }
  }
}
```

To upgrade to full database operations, add `--cluster_endpoint`, `--region`, `--database_user`, and optionally `--allow-writes` to the args array, and set `"disabled": false`.

---

# MCP Server Setup Instructions

## Prerequisites:

```bash
uv --version
```

**If missing:**

- Install from: [Astral](https://docs.astral.sh/uv/getting-started/installation/)

## General MCP Configuration:

Add the following configuration after checking if the user wants documentation-only functionality
or database operation support too.

### Documentation-Only Configuration

```json
{
  "mcpServers": {
    "aurora-dsql": {
      "command": "uvx",
      "args": [
        "awslabs.aurora-dsql-mcp-server@latest"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Database Operation Support Configuration

```json
{
  "mcpServers": {
    "aurora-dsql": {
      "command": "uvx",
      "args": [
        "awslabs.aurora-dsql-mcp-server@latest",
        "--cluster_endpoint",
        "[your dsql cluster endpoint, e.g. abcdefghijklmnopqrst234567.dsql.us-east-1.on.aws]",
        "--region",
        "[your dsql cluster region, e.g. us-east-1]",
        "--database_user",
        "[your dsql username, e.g. admin]",
        "--profile",
        "[your aws profile name, eg. default]",
        "--allow-writes"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR",
        "REGION": "[your dsql cluster region, eg. us-east-1, only when necessary]",
        "AWS_PROFILE": "[your aws profile name, eg. default]"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Optional Arguments and Environment Variables:

The following args and environment variables are not required, but may be required if the user
has custom AWS configurations or would like to allow/disallow the MCP server mutating their database.

- Arg: `--profile` or Env: `"AWS_PROFILE"` only need
  to be configured for non-default values.
- Env: `"REGION"` when the cluster region management is
  distinct from user's primary region in project/application.
- Arg: `--allow-writes` based on how permissive the user wants
  to be for the MCP server. Always ask the user if writes
  should be allowed.

## Coding Assistant Configuration

Configure the Aurora DSQL MCP server in the user's agent-specific MCP settings. Use the server command, arguments, and environment variables from the examples above, then restart or reload the agent so it discovers the new MCP tools. If the user's agent supports per-project MCP configuration, prefer project scope unless the user explicitly wants the server available globally.

## Additional Documentation

- [MCP Server Setup Guide](https://awslabs.github.io/mcp/servers/aurora-dsql-mcp-server)
- [DSQL MCP User Guide](https://docs.aws.amazon.com/aurora-dsql/latest/userguide/SECTION_aurora-dsql-mcp-server.html)
