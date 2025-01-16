import streamlit as st
import plotly.express as px
import uuid

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



