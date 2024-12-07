## CRUD Agent
An chatbot agent that can automatically perform CRUD operations using a custom made REST API via simple messaging.

# Technologies used
**Framework**: LangChain <br>
**Web Interface**: Streamlit <br>
**LLM**: Mistral Small <br>
**REST API**: Django REST and Swagger(for OpenAPI docs) <br>

# Setup

Clone the repository:

```sh
> git clone https://github.com/Armaan457/CRUD-Agent.git
```

Create and activate a virtual environment:

```sh
> python -m venv venv
> venv\scripts\activate
```

Install dependencies:

```sh
> pip install -r requirements.txt
```

Run the API server in the correct directory:

```sh
> cd foods
> python manage.py runserver
```

Run the app server:

```sh
> streamlit run app.py
```

# Example
For demonstration, I have made REST APIs for performing CRUD operations on a SQL db for a Django project `foods`. In the `tools.py` the neccessary tools are defined and the Agent lies in the `app.py` file.
