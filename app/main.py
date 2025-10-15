import streamlit as st
from chains import Chain
from portfolio import Portfolio

chain_object = Chain()
portfolio_object = Portfolio()
portfolio_object.load_portfolio()
st.title("Cold Email Generator ")
url_text = st.text_input("Enter the URL of the offer",value = "https://careers.nike.com/software-engineer-iii-blue-yonder-itc/job/R-68432")
submit_button = st.button("Submit")
if submit_button : 
    jobs_description = chain_object.extract_jobs_description(url_text)
    for job_description in jobs_description :
        skills= job_description.get("skills",[""])
        portfolio_infos = portfolio_object.query_portfolio_infos(skills)
        cold_email = chain_object.write_email(job_description,portfolio_infos)
        
        st.code(cold_email,language="markdown")