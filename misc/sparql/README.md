# SPARQL querying and loading rdf graphs using Apache Spark
More researchers are looking into how distributed systems such as Hadoop can be used to efficiently load and query RDF data sets.  The technology that has shown the most promise is [Apache Spark](https://spark.apache.org/).  The software in this repo both use the Hdoop File System as the RDF store and use Spark to quickily query the RDF dataset.

# [S2RDF (SPARQL on Spark for RDF)](https://github.com/aschaetzle/S2RDF)
**[Alexander Schatzle, Martin Przyjaciel-Zablocki, Simon Skilevic, Georg Lausen. S2RDF: RDF Querying with SPARQL on Spark. Proceedings of the VLDB Endowment, Volume 9, No. 10, 2016](http://www.vldb.org/pvldb/vol9/p804-schaetzle.pdf)**

S2RDF defines a new partitioning schema for RDF called Extended Vertical Partitioning (ExtVP).  ExtVP is derived from existing Vertical Partitioning (VP) tables. VP tables are two column tables for each predicate (where the columns are the subject and object respectively). ExtVP tables are the results of performing left joins on two VP tables based on three correlation triple patterns (subject-subject, subject-object and object-subject).  This means each predicate can have up to 6 tables (1 VP, 5 Ext VP).  A selectivity factor is the ratio of the size of the new ExtVP table vs. the size of the VP table that was used to generate.  This can be used to decrease the amout of ExtVP tables that are generated.  For query translation, the table with the lowest selectivity factor for each basic graph pattern in the triple is chosen. Each SELECT statement is then joined to create the (Spark) SQL query.

- Input: RDF file in N-Triples format/ SPARQL query file
- Output: CSV file/ [Apache Parquet](https://parquet.apache.org/) file
- Dataset: [Waterloo Diversity Test Suite](https://dsg.uwaterloo.ca/watdiv/) 100k/1 million


# [PRoST (Partitioned RDF on Spark Tables)](https://github.com/tf-dbis-uni-freiburg/PRoST#prost-partitioned-rdf-on-spark-tables)
**[Matteo Cossu, Michael Färber, Georg Lausen. PRoST: Distributed Execution of SPARQL Queries Using Mixed Partition Strategies. 21st International Conference on Extending Database Technology, 2018](https://github.com/tf-dbis-uni-freiburg/PRoST)**

PRoST stores the data twice using Vertical Partition Tables and Property Tables.  A property table consists of rows for each distinct subject (the key) and the columns contain all the object values for that subject.  The columns are identified by the property (predicate) to which they belong.  Property tables are great for subject-subject triple patterns.  PRoST models SPARQL queries using Join Trees.  A Join Tree is such that nodes are predicates.  Basic graph patterns that are subject-subject are represented together as a single node and marked with a special label denoting that a property table should be used.  All other nodes will use VP tables.  Join Trees are joined bottom-up.  Node placement is based on priority determined by the total number of triples and the number of distinct subjects for each predicate.  Triples with literals get high priority,

- Input: RDF file in N-Triples format/ SPARQL query file
- Output: CSV file/ [Apache Parquet](https://parquet.apache.org/) file
- Dataset: [Waterloo Diversity Test Suite](https://dsg.uwaterloo.ca/watdiv/) 100k/1 million

# Results
| Software | WatDiv 100k (Load Time, Dataset size) | WatDiv 1M (Load Time, Dataset size) |
|----------|---------------------------------------|-------------------------------------|
| S2RDF    | 43 min 19 sec,  2.7 MB                | 7 hours 58 min 48 sec, 1059.2 MB    |
| PRoST    | 55 min 37 sec , 5.1 MB                | 56 min 45 sec, 2.88 GB              |

|             | Star Query 7      | Snowflake Query 4 | Star Query 5 | Linear Query 4 | Linear Query 5 | Snowflake Query 2 | Complex Query 3 | Snowflake Query 3 | Linear Query 3 |
|-------------|-------------------|-------------------|--------------|----------------|----------------|-------------------|-----------------|-------------------|----------------|
| WatDiv 100k | 35 seconds        | 59 seconds        | 52 seconds   | 54 seconds     | 50 seconds     | 84 seconds        | 43 seconds      | 66 seconds        | 51 seconds     |
| WatDiv 1M   | Not enough memory | 110 seconds       | 76 seconds   | 67 seconds     | 48 seconds     | Not enough memory | 84 seconds      | Not enough memory | 85 seconds     |

# Run instructions
In order to submit a Spark job to my cluster you need to be authenticated.  There is a JSON file that the code needs access to that will be pointed to by an environment variable as follows:
```
export GOOGLE_APPLICATION_CREDENTIALS= /home/user/Downloads/[FILE_NAME].json
```
You will NOT BE ABLE TO SUBMIT A JOB WITHOUT THIS!

# [Video demonstraction](https://youtu.be/-kftXXLGreM)
