# GravityWork - AI-Native Project Orchestration

## Project Description

GravityWork is an AI-native collaboration platform that aggregates tools (Jira, Slack, GitHub) into a single intelligence layer. It utilizes a Federated Context architecture via MCP (Model Context Protocol) to provide real-time, low-latency, and agentic automation.

## Architecture Overview

### Federated Context Architecture
- **MCP Servers**: Real-time data retrieval for dynamic data
  - `mcp-server-jira`: Ticket status and sprint velocity
  - `mcp-server-slack`: Thread history and sentiment analysis
  - `mcp-server-github`: PRs, commits, and blame history

### Static ETL Pipeline
- **Vector Database**: Qdrant (optimized for metadata filtering)
- **Chunking Strategy**: Hierarchical Chunking with strict metadata requirements

## Setup Instructions

### Prerequisites
- Docker
- Docker Compose
- Node.js 18+
- Python 3.11+
- Go 1.20+

### Installation

1. Clone the repository:
