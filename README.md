# Sakila Data Agent 🤖

A Streamlit-powered chatbot that helps users explore and visualize data from the Sakila database using natural language queries. The bot is powered by OpenAI's GPT model and can generate both data tables and visualizations.

## Features

- 💬 Natural language interface to query MySQL database
- 📊 Data visualization capabilities (bar, line, pie, histogram charts)
- 📋 Interactive data tables
- 🔄 Persistent chat history with results
- 🎨 Clean and intuitive user interface

## Prerequisites

- Python 3.11+
- MySQL with Sakila database installed
- OpenAI API key

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd data-agent
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:

```env
OPENAI_API_KEY=your_openai_api_key
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_DATABASE=sakila
```

## Usage

1. Start the Streamlit app:

```bash
streamlit run app.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Start chatting! Example queries:
   - "Show me the total rentals by month"
   - "What are the top 10 most rented movies?"
   - "Plot the average rental duration by category"

## Project Structure

```
data-agent/
├── app.py # Main Streamlit application
├── tools.py # Database and visualization tools
├── functions.py # Helper functions
├── prompts.py # System prompts for the AI
├── db_schema_fetcher.py # Database schema utility
└── schema.txt # Cached database schema
```

## Technologies Used

- [Streamlit](https://streamlit.io/) - Web interface
- [OpenAI GPT](https://openai.com/) - Natural language processing
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [Matplotlib](https://matplotlib.org/) - Data visualization
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database interaction
- [MySQL](https://www.mysql.com/) - Database

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
