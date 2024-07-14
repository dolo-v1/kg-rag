from transformers import RagTokenizer, RagTokenForGeneration, RagRetriever

tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")
retriever = RagRetriever.from_pretrained(
    "facebook/rag-token-nq", index_name="exact", use_dummy_dataset=True
)
model = RagTokenForGeneration.from_pretrained(
    "facebook/rag-token-nq", retriever=retriever
)

import os
from neo4j import GraphDatabase


def drug_query(chemical, dosage):
    query = """MATCH (d:Drug) -[:CONTAINS]->(c:Chemical {name: $chemical}), (d)-[:HAS_DOSAGE]->(dos:Dosage {value: $dosage})
        RETURN d.name as Drug"""

    results = neo4j_handler.query(
        query, parameters={"chemical": chemical, "dosage": dosage}
    )
    return set([i["Drug"] for i in results])


def find_comp(drug_name):

    query = """MATCH (d:Drug {name : $drug_name}) - [:CONTAINS] ->(c:Chemical)-[:QUANTITY]->(dos:Dosage),(d)-[:HAS_DOSAGE]->(dos)
            RETURN c.name as Chemical, dos.value as Dosage"""

    results = neo4j_handler.query(query, parameters={"drug_name": drug_name})

    return [[i["Chemical"], i["Dosage"]] for i in results]


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
