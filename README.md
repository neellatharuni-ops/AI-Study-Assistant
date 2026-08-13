# 🤖 AI Study Assistant

An AI-powered personalized study assistant that helps students understand study topics, analyze their academic performance, and generate personalized study plans.

The project combines **Groq LLM, Snowflake, RAG, Python and Streamlit** to provide intelligent and personalized learning support.

---

## 🎯 Project Objective

The main objective of this project is to create an AI-based study assistant that can:

- Analyze student performance
- Identify weak and strong subjects
- Answer questions using study materials
- Retrieve relevant information using RAG
- Provide personalized study recommendations
- Generate personalized study plans
- Display student performance through a dashboard

---

## 🚀 Features

### 📊 Student Performance Analysis

Student marks are stored in Snowflake.

The system identifies:

- Strongest subject
- Weakest subject
- Average score
- Subject requiring the most attention

---

### 🤖 AI Study Assistant

Students can ask questions such as:

> What is normalization?

> Explain B-Tree in simple words.

> What is inheritance in Python?

The system uses the Groq LLM to generate easy-to-understand answers.

---

### 📚 RAG-Based Question Answering

The project uses Retrieval-Augmented Generation (RAG).

Study materials are stored as text files.

The system:

1. Loads study materials
2. Splits the material into chunks
3. Converts text into TF-IDF vectors
4. Finds the most relevant chunks
5. Sends the relevant information to the LLM
6. Generates an answer

---

### 📅 Personalized Study Plan

The AI analyzes student scores and generates a personalized study plan.

For example:

- DBMS → High priority
- Maths → Medium priority
- DSA → Revision
- Python → Maintenance

---

### 📈 Performance Dashboard

The Streamlit dashboard displays:

- Average score
- Strongest subject
- Weakest subject
- Subject-wise scores
- Performance chart

---

## 🏗️ System Architecture

```text
                 STUDENT
                    |
                    v
             STREAMLIT APP
                    |
          +---------+---------+
          |                   |
          v                   v
   STUDENT DATA             QUESTION
          |                   |
          v                   v
      SNOWFLAKE              RAG
          |                   |
          |             Study Materials
          |                   |
          |             TF-IDF Retrieval
          |                   |
          +---------+---------+
                    |
                    v
                GROQ LLM
                    |
          +---------+---------+
          |                   |
          v                   v
      AI ANSWER          STUDY PLAN