# document-summariser

The purpose of this Document is to prove that I can use databases locally. I have used a dynamo db as port 8000
this will store my summaries of which google gemini will write a shorten version of say the pdf or word document

The main part i wanted to do is continously store the documents locally whilst the power is in the system

The fast api (main.py) is where you can upload word or pdf documents and then this will store the documents to dynambo db. 




 create a directory like that at the end
C:\Users\jason\doctalk-local\dynamodb_local>cd C:\Users\jason\doctalk-local\dynamodb_local

java "-Djava.library.path=.\DynamoDBLocal_lib" -jar DynamoDBLocal.jar -sharedDb
Initializing DynamoDB Local with the following configuration:

to run the local dynamo db

and to run the fastapi of where you can upload the pdfs and word

C:\Users\jason\doctalk-local
python -m uvicorn main:app --reload --port 8001

This should start the both applications
and to start the main file index.html
and that we retrieve all the summarised documentation

I did spend a good majority of the day on this. I had problems with Google Gen AI. it just wouldnt work. 

Just remember to a create table for the dynamo db

cd C:\Users\jason\doctalk-local
python create_table.py

