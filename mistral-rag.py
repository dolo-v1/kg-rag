from neo4j import GraphDatabase
import subprocess


class Neo4jHandler:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def session(self, **kwargs):
        return self.driver.session(**kwargs)


def get_comp(tx, drug_name):
    query = """
    MATCH (d:Drug {name: $drug_name})-[:CONTAINS]->(c:Chemical)-[:QUANTITY]->(dos:Dosage), (d)-[:HAS_DOSAGE]->(dos)
    RETURN d.name AS Drug, c.name AS Chemical, dos.value AS Dosage
    """
    result = tx.run(query, drug_name=drug_name)
    return result.data()


def get_similar_drugs(tx, drug_name):
    query = """
    MATCH (d:Drug {name: $drug_name})-[:CONTAINS]->(c:Chemical)-[:QUANTITY]->(dos:Dosage), (d)-[:HAS_DOSAGE]->(dos)
    MATCH (d2)-[:CONTAINS]->(c), (d2)-[:HAS_DOSAGE]->(dos)
    WHERE d <> d2
    MATCH (d2)-[:CONTAINS]->(c2:Chemical)-[:QUANTITY]->(dos2:Dosage), (d2)-[:HAS_DOSAGE]->(dos2)
    RETURN d2.name AS Drug, c2.name AS Chemical, dos2.value AS Dosage
    """
    result = tx.run(query, drug_name=drug_name)
    return result.data()


def get_context(drug_name):
    with handler.session() as session:
        results = session.execute_read(get_similar_drugs, drug_name)
        context = ""
        prev = None
        l = []
        for record in results:
            if prev != record["Drug"]:
                if prev:
                    context += f"Drug : {prev}\n"
                    s = "\n".join(l)
                    context += f"Constituents : {s}\n"
                    l = []
            prev = record["Drug"]
            l.append(f"{record['Chemical']}, {record['Dosage']}")

        context = context[: 2**15]
        results = session.execute_read(get_comp, drug_name)
        context += f"Drug : {drug_name}\nConstituents : "
        for record in results:
            context += f"{record['Chemical']}, {record['Dosage']}\n"
    handler.close()
    return context


def run_sub(drug_name):
    context = get_context(drug_name)
    result = subprocess.run(
        [
            "ollama",
            "run",
            "mistral",
            f"given context {context}, select the tablet having the same combination of chemicals and dosage as {drug_name}",
        ],
        capture_output=True,
        text=True,
    )
    return result.stdout, result.stderr


with open("uri.txt", "r") as f:
    uri = f.read().strip()
    f.close()
with open("password.txt", "r") as f:
    password = f.read().strip()
    f.close()
handler = Neo4jHandler(
    uri,
    "neo4j",
    password,
)

out, err = run_sub("XREL Tablet")
print(out)
if err:
    print(err)
