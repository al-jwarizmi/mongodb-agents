# Frodo - Multi-Agent Customer Support System

A conversational multi-agent system with db read/write operations. The system uses a router agent and operational agents for product details, customer reviews, and order management.

## Features

- 🤖 Data specific agents for different aspects of customer support
- 🔄 Intelligent query routing based on context
- 💬 Real-time chat interface with WebSocket support
- 📊 MongoDB integration for product and review data
- ⚙️ Configurable agent system through YAML configuration
- 🧪 Comprehensive test suite for reproducibility

![Demo](output.gif)

## Prerequisites

- Python 3.8+
- Docker (for MongoDB)
- OpenAI API key

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd floma
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up MongoDB with Docker**
   ```bash
   # Pull and run MongoDB container
   docker pull mongodb/mongodb-community-server
   docker run --name mongodb -d -p 27017:27017 mongodb/mongodb-community-server
   ```

5. **Configure Environment Variables**
   ```bash
   # Copy example environment file
   cp config/.env.example config/.env
   ```
   Edit `config/.env` and set your configuration:
   ```env
   OPENAI_API_KEY=your_api_key_here
   MONGODB_URI=mongodb://localhost:27017
   DATABASE_NAME=floma
   GPT_MODEL=gpt-4o
   TEMPERATURE=0.7
   ```

6. **Initialize Database**
   ```bash
   # Load initial product catalog and reviews
   python -c "from database.data_loader import DataLoader; loader = DataLoader(); loader.load_all_data()"
   ```

## Running the System

1. **Start the API Server**
   ```bash
   uvicorn api:app --reload --host 0.0.0.0 --port 8000
   ```
   The server will start at `http://localhost:8000`

2. **Access the Chat Interface**
   Open `static/index.html` in your web browser to use the chat interface.


## Agent Configuration

The system uses a YAML configuration file to manage agent availability. Edit `config/agents_config.yaml` to enable/disable agents:

```yaml
agents:
  product_details:
    enabled: true
    name: "Product Details Agent"
    description: "Handles product information, comparisons, and specifications"
  
  reviews:
    enabled: true
    name: "Reviews Agent"
    description: "Manages customer reviews and ratings"
  
  orders:
    enabled: true
    name: "Orders Agent"
    description: "Handles order processing, status checks, and purchase inquiries"
```

## Running Tests

1. **Database Operation Tests**
   ```bash
   pytest tests/test_db_operations.py
   ```
   Tests database CRUD operations including:
   - Creating and retrieving product reviews
   - Processing orders
   - Fetching product details
   - Handling invalid inputs
   - Database cleanup and reloading

2. **Agent Configuration Tests**
   ```bash
   pytest tests/test_agent_config.py
   ```
   Validates the agent configuration system:
   - Enabling/disabling agents via config
   - Handling invalid agent types
   - Testing router prompt generation
   - Validating config file parsing
   - Testing agent routing behavior

## Project Structure

```
floma/
├── agents/                 # Agent implementations
│   ├── base_agent.py      # Base agent class
│   ├── product_details_agent.py
│   ├── reviews_agent.py
│   └── orders_agent.py
├── config/                # Configuration files
│   ├── agents_config.yaml # Agent configuration
│   └── .env              # Environment variables
├── database/             # Database operations
│   ├── data_loader.py    # Data initialization
│   └── mongodb_client.py # MongoDB client
├── tests/                # Test suites
├── static/              # Frontend files
├── api.py              # FastAPI server
├── main.py            # CLI interface
└── requirements.txt   # Dependencies
```

## API Documentation

Once the server is running, access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`

## Troubleshooting

1. **MongoDB Connection Issues**
   - Verify Docker container is running: `docker ps`
   - Check MongoDB logs: `docker logs mongodb`
   - Ensure MongoDB URI is correct in `.env`

2. **OpenAI API Issues**
   - Verify API key in `.env`
   - Check API key permissions and quotas
   - Ensure selected model is available for your account

3. **Agent Configuration Issues**
   - Verify YAML syntax in `agents_config.yaml`
   - Check agent configuration using tests
   - Review logs for initialization errors