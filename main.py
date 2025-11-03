from fastapi import FastAPI, UploadFile, File, HTTPException
import boto3, os, PyPDF2, uuid
from dotenv import load_dotenv
from google import genai  # Gemini client
from fastapi.middleware.cors import CORSMiddleware
from boto3.dynamodb.conditions import Attr
from docx import Document  # for Word files

load_dotenv()
app = FastAPI()

# -------- CORS Middleware ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Gemini client ----------
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def summarize_with_gemini(text: str) -> str:
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Summarize this document briefly:\n\n{text}"
    )
    return response.text.strip()

# -------- DynamoDB ----------
dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url="http://localhost:8000",
    region_name="us-west-2",
    aws_access_key_id="fakeMyKeyId",
    aws_secret_access_key="fakeSecretAccessKey",
)
table = dynamodb.Table("DocumentSummaries")

# -------- Helper to extract text ----------
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

# -------- Upload route ----------
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        # Determine file type and extract text
        if file.filename.lower().endswith(".pdf"):
            text = extract_text_from_pdf(file.file)
        elif file.filename.lower().endswith(".docx"):
            text = extract_text_from_docx(file.file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Upload PDF or DOCX only.")

        if not text.strip():
            raise HTTPException(status_code=400, detail="No text found in document.")

        # Summarize using Gemini
        summary = summarize_with_gemini(text)

        # Store in DynamoDB
        table.put_item(
            Item={
                "docId": str(uuid.uuid4()),
                "filename": file.filename,
                "summary": summary
            }
        )
        return {"filename": file.filename, "summary": summary}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------- Retrieve summary by filename ----------
@app.get("/summary/{filename}")
def get_summary(filename: str):
    resp = table.scan(
        FilterExpression=Attr("filename").eq(filename)
    )
    items = resp.get("Items", [])
    if not items:
        raise HTTPException(status_code=404, detail="File not found")
    return items[0]

# -------- Retrieve all summaries ----------
@app.get("/summaries")
def get_all_summaries():
    try:
        response = table.scan()
        return response.get("Items", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
