import streamlit as st
import plotly.express as px
import uuid
from  pinecone import Pinecone
from openai import OpenAI

def plot_figure(df, kind, title):
    x_label = df.columns[0]
    y_label = df.columns[1]

    df[y_label] = df[y_label].astype(float)

    match kind: 
        case "bar":
            fig = px.bar(df, x=x_label, y=y_label)
        case "line":
            fig = px.line(df, x=x_label, y=y_label)
        case "pie":
            fig = px.pie(df, values=y_label, names=x_label)
        case "hist":
            fig = px.histogram(df, x=x_label, y=y_label)
        case _:
            raise ValueError(f"Invalid kind: {kind}")
    
    fig.update_layout(title=title)
    st.plotly_chart(fig, key=uuid.uuid4())

def get_memories(query, top_k=3):
    INDEX_NAME = st.secrets["PINECONE_INDEX"]
    PINECONE_NAMESPACE = st.secrets["PINECONE_NAMESPACE"] 
    PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]

    pc = Pinecone(PINECONE_API_KEY)
    index = pc.Index(INDEX_NAME)
    client = OpenAI()

    query_embedding = client.embeddings.create(input=query, model="text-embedding-ada-002")
    query_vector = query_embedding.data[0].embedding

    results = index.query(
        vector=query_vector,
        filter={"type": "recall"},
        namespace=PINECONE_NAMESPACE,
        include_metadata=True,
        top_k=top_k,
    )

    memories = [match.metadata["payload"] for match in results["matches"]]
    
    return memories