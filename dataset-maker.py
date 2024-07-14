from neo4j import GraphDatabase
import json


class Neo4jHandler:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def session(self, **kwargs):
        return self.driver.session(**kwargs)


def get_similar_drugs(tx, drug_name):
    query = """
    MATCH (d:Drug {name: $drug_name})-[:CONTAINS]->(c:Chemical)-[:QUANTITY]->(dos:Dosage), (d)-[:HAS_DOSAGE]->(dos)
    MATCH (d2)-[:CONTAINS]->(c), (d2)-[:HAS_DOSAGE]->(dos)
    MATCH (d2)-[:CONTAINS]->(c2:Chemical)-[:QUANTITY]->(dos2:Dosage), (d2)-[:HAS_DOSAGE]->(dos2)
    RETURN d2.name AS Drug, c2.name AS Chemical, dos2.value AS Dosage
    """
    result = tx.run(query, drug_name=drug_name)
    return result.data()


def find_comp(tx, drug_name):

    query = """MATCH (d:Drug {name : $drug_name}) - [:CONTAINS] ->(c:Chemical)-[:QUANTITY]->(dos:Dosage),(d)-[:HAS_DOSAGE]->(dos)
            RETURN c.name as Chemical, dos.value as Dosage"""

    results = tx.run(query, parameters={"drug_name": drug_name})

    return [[i["Chemical"], i["Dosage"]] for i in results]


def drugs(tx):
    query = """
            MATCH (d: Drug)
            RETURN d.name as Drug"""
    results = tx.run(query)
    return [i["Drug"] for i in results]


if __name__ == "__main__":
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

    with handler.session() as session:
        listofdrugs = session.execute_read(drugs)
        for j, i in enumerate(listofdrugs[:1]):
            if j % 100 == 0:
                print(j)
            comp = session.execute_read(find_comp, i)
            results = session.execute_read(get_similar_drugs, i)
            d = {}
            drug = None

            c = 0
            l = []
            prevDrug = None
            for record in results:
                drug = record["Drug"]
                if drug == i:
                    continue
                if c == 3:
                    break
                if prevDrug != drug:
                    if prevDrug:
                        if l == comp:
                            d[prevDrug] = l
                            c += 1
                        l = []
                prevDrug = drug
                l.append([record["Chemical"], record["Dosage"]])
            if prevDrug and l == comp:
                d[prevDrug] = l

            with open(f"{i.replace('/', '_')}.json", "w") as f:
                json.dump(d, f, indent=4)

    handler.close()
