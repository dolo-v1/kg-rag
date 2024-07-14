import os
from neo4j import GraphDatabase
from langchain_openai import OpenAI
from langchain.schema.runnable import RunnableSequence
from langchain_core.runnables import RunnableLambda
from langchain.prompts import PromptTemplate

# Set up OpenAI API key

# Initialize LangChain with OpenAI
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.7)


# Function to query Neo4j
class Neo4jQuery:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]


with open("uri.txt", "r") as f:
    uri = f.read().strip()
    f.close()
with open("password.txt", "r") as f:
    password = f.read().strip()
    f.close()
neo4j_handler = Neo4jQuery(
    uri,
    "neo4j",
    password,
)
query = (
    "MATCH (d:Drug)-[:CONTAINS]->(c:Chemical) RETURN d.name AS Drug, c.name AS Chemical"
)
results = neo4j_handler.query(query)


def generate_response(query_results):
    context = "\n".join(
        [
            f"Drug: {record['Drug']}, Chemical: {record['Chemical']}"
            for record in query_results
        ]
    )
    prompt = f"Given the following context:\n{context}\n\nProvide a summary or answer based on the context above."

    # Generate response using LangChain
    prompt_template = PromptTemplate(input_variables=[], template=prompt)
    runnable_prompt = RunnableLambda(lambda x: prompt_template.format(**x))

    # Wrap the llm call in a RunnableLambda for compatibility
    def openai_runnable(input_text):
        return llm.generate([input_text])

    openai_runnable_step = RunnableLambda(openai_runnable)

    sequence = RunnableSequence(*[runnable_prompt, openai_runnable_step])
    response = sequence.invoke({})
    return response


# Generate response based on query results
response = generate_response(results)
print(response)

# Close Neo4j connection
neo4j_handler.close()
