# Exa MCP

Exa MCP Server enables AI assistants like Claude to perform real-time web searches through the Exa Search API, allowing them to access up-to-date information from the internet. It is open-source, check out [GitHub](https://github.com/exa-labs/exa-mcp-server/).

## Get your API key

Before you begin, you'll need an Exa API key:

<Card title="Get your Exa API key" icon="key" horizontal href="https://dashboard.exa.ai/api-keys" />

## Remote Exa MCP

Connect directly to Exa's hosted MCP server using this URL instead of running it locally:

```
https://mcp.exa.ai/mcp?exaApiKey=your-exa-api-key
```

To configure Claude Desktop, add this to your configuration file:

```json
{
  "mcpServers": {
    "exa": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.exa.ai/mcp?exaApiKey=your-exa-api-key"
      ]
    }
  }
}
```

## Available Tools

Exa MCP includes several specialized search tools:

| Tool                    | Description                                                                                                                                                                 |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `deep_researcher_start` | Start a smart AI researcher for complex questions. The AI will search the web, read many sources, and think deeply about your question to create a detailed research report |
| `deep_researcher_check` | Check if your research is ready and get the results. Use this after starting a research task to see if it's done and get your comprehensive report                          |
| `web_search_exa`        | Performs real-time web searches with optimized results and content extraction                                                                                               |
| `company_research`      | Comprehensive company research tool that crawls company websites to gather detailed information about businesses                                                            |
| `crawling`              | Extracts content from specific URLs, useful for reading articles, PDFs, or any web page when you have the exact URL                                                         |
| `linkedin_search`       | Search LinkedIn for companies and people using Exa AI. Simply include company names, person names, or specific LinkedIn URLs in your query                                  |

## Usage Examples

Once configured, you can ask Claude to perform searches:

* "Research the company exa.ai and find information about their pricing"
* "Start a deep research project on the impact of artificial intelligence on healthcare, then check when it's complete to get a comprehensive report"

## Local Installation

### Prerequisites

* [Node.js](https://nodejs.org/) v18 or higher.
* [Claude Desktop](https://claude.ai/download) installed (optional). Exa MCP also works with other MCP-compatible clients like Cursor, Windsurf, and more).
* An Exa API key (see above).

### Using Claude Code

The quickest way to set up Exa MCP is using Claude Code:

```bash
claude mcp add exa -e EXA_API_KEY=YOUR_API_KEY -- npx -y exa-mcp-server
```

Replace `YOUR_API_KEY` with your Exa API key from above.

### Using NPX

The simplest way to install and run Exa MCP is via NPX:

```bash
# Install globally
npm install -g exa-mcp-server

# Or run directly with npx
npx exa-mcp-server
```

To specify which tools to enable:

```bash
# Enable only web search
npx exa-mcp-server --tools=web_search

# Enable deep researcher tools
npx exa-mcp-server --tools=deep_researcher_start,deep_researcher_check

# List all available tools
npx exa-mcp-server --list-tools
```

## Configuring Claude Desktop

To configure Claude Desktop to use Exa MCP:

1. **Enable Developer Mode in Claude Desktop**
   * Open Claude Desktop
   * Click on the top-left menu
   * Enable Developer Mode

2. **Open the Configuration File**

   * After enabling Developer Mode, go to Settings
   * Navigate to the Developer Option
   * Click "Edit Config" to open the configuration file

   Alternatively, you can open it directly:

   **macOS:**

   ```bash
   code ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

   **Windows:**

   ```powershell
   code %APPDATA%\Claude\claude_desktop_config.json
   ```

3. **Add Exa MCP Configuration**

   Add the following to your configuration:

   ```json
   {
     "mcpServers": {
       "exa": {
         "command": "npx",
         "args": [
           "-y",
          "exa-mcp-server"
          ],
         "env": {
           "EXA_API_KEY": "your-api-key-here"
         }
       }
     }
   }
   ```

   Replace `your-api-key-here` with your actual Exa API key.

4. **Enabling Specific Tools**

   To enable only specific tools:

   ```json
   {
     "mcpServers": {
       "exa": {
         "command": "npx",
         "args": [
           "-y",
           "exa-mcp-server",
           "--tools=web_search"
         ],
         "env": {
           "EXA_API_KEY": "your-api-key-here"
         }
       }
     }
   }
   ```

   To enable deep researcher tools:

   ```json
   {
     "mcpServers": {
       "exa": {
         "command": "npx",
         "args": [
           "-y",
           "exa-mcp-server",
           "--tools=deep_researcher_start,deep_researcher_check"
         ],
         "env": {
           "EXA_API_KEY": "your-api-key-here"
         }
       }
     }
   }
   ```

5. **Restart Claude Desktop**
   * Completely quit Claude Desktop (not just close the window)
   * Start Claude Desktop again
   * Look for the 🔌 icon to verify the Exa server is connected

## Troubleshooting

### Common Issues

1. **Server Not Found**
   * Ensure the npm package is correctly installed

2. **API Key Issues**
   * Confirm your EXA\_API\_KEY is valid
   * Make sure there are no spaces or quotes around the API key

3. **Connection Problems**
   * Restart Claude Desktop completely

## Additional Resources

For more information, visit the [Exa MCP Server GitHub repository](https://github.com/exa-labs/exa-mcp-server/).
