from neo4j import GraphDatabase


class Neo4jHandler:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()


def get_similar_drug(driver, drug_name):
    # query = """
    # MATCH (d:Drug)-[:CONTAINS]->(c:Chemical)<-[:CONTAINS]-(similar_drug:Drug),
    #       (d)-[:HAS_DOSAGE]->(dos:Dosage)<-[:HAS_DOSAGE]-(similar_drug)
    # WHERE d.name CONTAINS $drug_name
    # RETURN DISTINCT similar_drug.name AS SimilarDrug, dos.value AS Dosage, c.name AS Chemical
    # """

    query = """
    MATCH (d:Drug)-[:CONTAINS]->(c:Chemical)-[:QUANTITY]->(dos:Dosage)
    WHERE d.name CONTAINS $drug_name
    WITH d, collect(DISTINCT c.name) AS chemicalNames, collect(DISTINCT dos.value) AS dosageValues
    MATCH (similar_drug:Drug)-[:CONTAINS]->(c2:Chemical)-[:QUANTITY]->(dos2:Dosage)
    WHERE similar_drug.name <> d.name
    WITH similar_drug, chemicalNames, dosageValues, collect(DISTINCT c2.name) AS similarChemicalNames, collect(DISTINCT dos2.value) AS similarDosageValues
    WHERE chemicalNames = similarChemicalNames AND dosageValues = similarDosageValues
    RETURN DISTINCT similar_drug.name AS SimilarDrug


    """

    with driver.session() as session:
        result = session.run(query, drug_name=drug_name)
        return [record["SimilarDrug"] for record in result]


def get_drugs(driver, drug_name):
    # query = """
    #            MATCH (d:Drug {name:$drug_name})-[:CONTAINS]->(c:Chemical)-[:QUANTITY] ->(dos:Dosage),
    #             (d)-[:HAS_DOSAGE]->(dos)
    #             RETURN d.name AS Drug, c.name AS Chemical, dos.value as Dosage
    # """
    query = """
    MATCH (d:Drug {name:"Benadryl Syrup"})-[:CONTAINS]->(c:Chemical)-[:QUANTITY] ->(dos:Dosage), (d)-[:HAS_DOSAGE]->(dos),
     (o:Drug)-[:CONTAINS]->(c),
      (o)-[:HAS_DOSAGE]->(dos)
    RETURN o.name AS Drug
    """
    with driver.session() as session:
        result = session.run(query, drug_name=drug_name)
        return [i["Drug"] for i in result]

if __name__ == "__main__":
    with open("uri.txt", "r") as f:
        uri = f.read().strip()
        f.close()
    with open("password.txt", "r") as f:
        password = f.read().strip()
        f.close()

    user = "neo4j"

    handler = Neo4jHandler(uri, user, password)
    similar_drugs = get_drugs(handler.driver, "Benadryl Syrup")
    for i in similar_drugs:
        print(i)
    handler.close()
