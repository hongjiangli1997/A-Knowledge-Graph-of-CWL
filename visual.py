from py2neo import Graph
from sklearn.manifold import TSNE
import numpy as np
import altair as alt
import pandas as pd

driver = Graph("http://localhost:7474", auth=("neo4j", "neo4j"))

result = driver.run("""
MATCH (p:Place)-[:IN_COUNTRY]->(country)
WHERE country.code IN $countries
RETURN p.name AS place, p.embeddingNode2vec AS embedding, country.code AS country
""", {"countries": ["E", "GB", "F", "TR", "I", "D", "GR"]})
X = pd.DataFrame([dict(record) for record in result])


X_embedded = TSNE(n_components=2, random_state=6).fit_transform(list(X.embedding))

places = X.place
df = pd.DataFrame(data = {
    "place": places,
    "country": X.country,
    "x": [value[0] for value in X_embedded],
    "y": [value[1] for value in X_embedded]
})

alt.Chart(df).mark_circle(size=60).encode(
    x='x',
    y='y',
    color='country',
    tooltip=['place', 'country']
).properties(width=700, height=400)