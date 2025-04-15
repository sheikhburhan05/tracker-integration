from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from services.ashby_service import AshbyService
from services.email_service import EmailService

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/jobs")
async def get_jobs():
    jobs = AshbyService.fetch_jobs()
    return [
        {
            "id": job["id"],
            "title": job["title"],
            "status": job["status"],
            "employmentType": job["employmentType"],
            "createdAt": job["createdAt"],
        }
        for job in jobs
    ]


@app.get("/candidates")
async def get_candidates(job_id: str = None):
    applicants = AshbyService.fetch_candidates(job_id)
    return [
        {
            "id": applicant["id"],
            "name": applicant["candidate"]["name"],
            "email": applicant["candidate"]["primaryEmailAddress"]["value"],
            "stage": applicant["currentInterviewStage"]["title"],
            "stageId": applicant["currentInterviewStage"]["id"],
            "job": applicant["job"]["id"],
        }
        for applicant in applicants
    ]


@app.post("/webhook")
async def handle_candidate_stage_change(request: Request):
    """Handle candidateStageChange webhook from AshbyHQ."""
    # Verify webhook signature (if secret is provided)
    # if WEBHOOK_SECRET:
    #     signature = request.headers.get("X-Ashby-Signature")
    #     if not signature:
    #         raise HTTPException(status_code=401, detail="Missing webhook signature")

    #     payload = await request.body()
    #     computed_signature = hmac.new(
    #         WEBHOOK_SECRET.encode("utf-8"), payload, hashlib.sha256
    #     ).hexdigest()

    #     if not hmac.compare_digest(computed_signature, signature):
    #         raise HTTPException(status_code=401, detail="Invalid webhook signature")

    # Process webhook payload
    data = await request.json()
    print("data1", data)
    if data.get("action") != "candidateStageChange":
        raise HTTPException(status_code=400, detail="Invalid webhook action")

    application = data.get("data", {}).get("application", {})
    if not application:
        raise HTTPException(status_code=400, detail="Missing application data")

    # # Extract relevant details
    # candidate = application.get("candidate", {})
    # candidate_id = candidate.get("id", "N/A")
    # candidate_name = candidate.get("name", "Unknown Candidate")
    # candidate_email = candidate.get("primaryEmailAddress", {}).get("value", "N/A")

    # job = application.get("job", {})
    # job_id = job.get("id", "N/A")
    # job_title = job.get("title", "Unknown Job")

    # stage = application.get("currentInterviewStage", {})
    # stage_name = stage.get("title", "Unknown Stage")

    # application_status = application.get("status", "N/A")
    # updated_at = application.get("updatedAt", "N/A")

    # # Include custom fields
    # custom_fields = application.get("customFields", [])
    # custom_fields_text = (
    #     "\n".join([f"{field['title']}: {field['value']}" for field in custom_fields])
    #     if custom_fields
    #     else "None"
    # )

    # # Send email
    # subject = f"Candidate Stage Changed: {candidate_name} - {job_title}"
    # body = (
    #     f"Candidate: {candidate_name}\n"
    #     f"Email: {candidate_email}\n"
    #     f"Job: {job_title}\n"
    #     f"New Stage: {stage_name}\n"
    #     f"Application Status: {application_status}\n"
    #     f"Updated At: {updated_at}\n"
    #     f"Custom Fields:\n{custom_fields_text}"
    # )
    # success = EmailService.send_email(subject, body)

    # if not success:
    #     raise HTTPException(status_code=500, detail="Failed to send email")

    # Extract relevant details
    candidate = application.get("candidate", {})
    candidate_id = candidate.get("id", "N/A")
    candidate_name = candidate.get("name", "Unknown Candidate")

    job = application.get("job", {})
    job_id = job.get("id", "N/A")
    job_title = job.get("title", "Unknown Job")

    stage = application.get("currentInterviewStage", {})
    stage_name = stage.get("title", "Unknown Stage")

    # Generate and upload assessment file
    file_path = AshbyService.generate_assessment_pdf(candidate_name, job_title, job_id)
    success = AshbyService.upload_file_to_candidate(candidate_id, file_path)

    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
