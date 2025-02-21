from langchain.utilities import SQLDatabase
from langchain.llms import OpenAI
from langchain_experimental.sql import SQLDatabaseChain
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
import psycopg2
from dotenv import load_dotenv
load_dotenv()
def parse_dynamic_data(input_data):
    # Extract the first element of the outer tuple and list
    records = input_data[0][0]

    # Initialize dictionary with dynamic keys
    parsed_data = {key: [] for key in records[0].keys()}

    # Populate dictionary with values
    for record in records:
        for key, value in record.items():
            parsed_data[key].append(value)

    return parsed_data

def send_request(message):
    llm = ChatOpenAI(temperature=0)
    #llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    #chain = create_sql_query_chain(llm, db)


    prompt_template = PromptTemplate.from_template(
        """You Answer the question based on the context below.

    Context:
        In the database, there are entities,gdapi_entities, datasets,dataset_tables,entity_data tables. Use Below relationships. 
        entities table Stores name of customer.
        gdapi_entities is a link between entities table and datasets. gdapi_entities id is used as a foreign key by datasets table in entity_id column.
        dataset_tables has a column dataset_id this is a foreign key on datasets table on id column. dataset_tables has a column with name as table_name .
        entity_data table has the size of data stored for each entity . this table also has the table_name column.
        Use the table_name column in dataset_tables and entity_data for the join between two tables.
        
    Question: """
    )
    prompt = prompt_template.format()


    # llm.invoke(prompt)



    host = 'localhost'
    port = '5432'
    username = 'postgres'
    password = 'password'
    database_schema = 'delphis'
    #mysql_uri = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database_schema}"
    postgres_uri = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database_schema}"
    # postgres_uri = f"postgresql+psycopg2://{username}@{host}:{port}/{database_schema}"
    
    # Create a temporary SQLDatabase object to check available tables
    temp_db = SQLDatabase.from_uri(postgres_uri)
    # available_tables = temp_db.get_usable_table_names()
    # print("Available tables:", available_tables)

    # Check if the required tables exist in the database
    required_tables = ["entities", "gdapi_entities", "datasets", "dataset_tables", "entity_data","reports","report_types"]


    # Create the SQLDatabase object with the required tables
    db = SQLDatabase.from_uri(postgres_uri, include_tables=required_tables, sample_rows_in_table_info=2)

    chain = create_sql_query_chain(llm, db)
    context = """
    In the database, there are entities, gdapi_entities, datasets, dataset_tables, entity_data tables. Use the relationships below:
    - entities table stores the name of the customer. 
    - gdapi_entities is a link between entities table and datasets.
    - gdapi_entities has a column named as delphius_id, use delphius_id column to join with id column of entity table.
    - gdapi_entities id is used as a foreign key by datasets table in entity_id column.
    - dataset_tables has a column dataset_id which is a foreign key on datasets table on id column. dataset_tables has a column with name as table_name.
    - entity_data table has the size of data stored for each entity. This table also has the table_name column.
    - Use the table_name column in dataset_tables and entity_data for the join between two tables.
    - reports table has a column as entity_id which is a foreign key on entities table on id column.use this to join with entities table.
    - reports table has a column report_type_id which is a foreign key on report_types table on id column. reports table has a column with name as report_name.
    - 
    """

    prompt_template = PromptTemplate.from_template(
        f"""You are a PostgreSQL expert. Given an input question, first create a syntactically correct PostgreSQL query to run, then look at the results of the query and return the answer to the input question.
        Unless the user specifies in the question a specific number of examples to obtain, query for at most {{top_k}} results using the LIMIT clause as per PostgreSQL. You can order the results to return the most informative data in the database.
        Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
        Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
        Pay attention to use CURRENT_DATE function to get the current date, if the question involves "today".

        Use the following format:

        Question: Question here
        SQLQuery: SQL Query to run
        SQLResult: Result of the SQLQuery
        Answer: While Answering the question,please include the table header as well as the data.

        Only use the following context :
        {context}

        Question: {{input}}
        """
    )

    prompt = prompt_template.format(input=message, top_k=5)

    response = chain.invoke({"question": prompt})
    print(response)
    # Remove backticks from the response
    cleaned_response = f"SELECT json_agg(t) FROM ({response.replace('```', '').replace(';', '')}) t;"
    db_response = db.run(cleaned_response)
    #print(db_response)
    #print(type(eval(db_response)))
    parsed_output = parse_dynamic_data(eval(db_response))
    return parsed_output
# a = send_request("which entity has the most data stored?")
# "Which entity has the most number of reports created?"
# print(a)