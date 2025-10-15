import chromadb
import uuid
import pandas as pd
class Portfolio : 
    def __init__(self,resource_path = "app/resource/my_portfolio.csv") : 
        self.data = pd.read_csv(resource_path)
        self.client = chromadb.PersistentClient("vectorstore")
        self.collection = self.client.get_or_create_collection("portfolio")
    
    def load_portfolio(self) : 
        if not self.collection.count() : 
            for _ , row in self.data.iterrows():
                self.collection.add(
                    documents=[row["Techstack"]],
                    metadatas = [{"link":row["Links"]}], 
                    ids=[str(uuid.uuid4())]
                )
    def query_portfolio_infos(self,skills:list) : 
        portfolio_infos = []
        results = self.collection.query(query_texts=skills, n_results= 2)
        links = results.get("metadatas",[])
        print(links)
        documents = results.get("documents",[])
        for link_list , document_list in zip(links,documents ) : 
            for link , document in zip (link_list,document_list) : 
                print(link.get("link"))
                portfolio_infos.append(
                    {
                        "skills": document,
                        "portfolio_link":link.get("link")
                    }
                )
        return portfolio_infos
                
        