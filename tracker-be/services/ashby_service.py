import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import requests
import base64
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()
API_KEY = os.getenv("ASHBY_API_KEY")
BASE_URL = "https://api.ashbyhq.com"


class AshbyService:
    @staticmethod
    def get_headers():
        return {
            "authorization": f"Basic {API_KEY}",
            "accept": "application/json",
            "content-type": "application/json",
        }

    def get_multipart_headers():
        return {
            "authorization": f"Basic {API_KEY}",
            "accept": "application/json",
        }

    @staticmethod
    def fetch_jobs() -> List[Dict]:
        headers = AshbyService.get_headers()
        response = requests.post(f"{BASE_URL}/job.list", headers=headers, json={})
        response.raise_for_status()
        return response.json().get("results", [])

    @staticmethod
    def fetch_candidates(job_id: str = None) -> List[Dict]:
        headers = AshbyService.get_headers()
        candidates = []
        next_cursor = None

        while True:
            data = (
                {"cursor": next_cursor, "jobId": job_id}
                if next_cursor
                else {"jobId": job_id}
            )
            print("here", data)
            response = requests.post(
                f"{BASE_URL}/application.list", headers=headers, json=data
            )
            response.raise_for_status()
            response_json = response.json()
            candidates.extend(response_json["results"])

            if not response_json["moreDataAvailable"]:
                break
            next_cursor = response_json["nextCursor"]

        return candidates

    @staticmethod
    def generate_assessment_pdf(
        candidate_name: str, job_title: str, job_id: str
    ) -> str:
        """Generate a PDF file with dummy assessment data."""
        # Dummy assessment data
        assessment_data = {
            "assessment": {
                "technical_skills": {
                    "justification": "Alex demonstrated limited technical knowledge and hands-on experience in AI engineering. While he showed some familiarity with concepts like RAG, LLMs, and sentiment analysis, his explanations lacked depth and specificity expected for a Senior AI Engineer role. He struggled with questions about model optimization, deployment, and scaling.",
                    "score": "30%",
                    "skills": [
                        {
                            "name": "AI/ML Engineering",
                            "expertise_level": "Beginner",
                            "justification": "Alex showed basic understanding of AI concepts but lacked depth in technical implementation and problem-solving.",
                        },
                        {
                            "name": "Cloud Platforms (AWS, Azure)",
                            "expertise_level": "Beginner",
                            "justification": "Alex mentioned experience with AWS and Azure but couldn't provide specific details about deployment or infrastructure management.",
                        },
                        {
                            "name": "NLP/LLMs",
                            "expertise_level": "Intermediate",
                            "justification": "Alex demonstrated some knowledge of LLMs and NLP concepts, but his explanations were often superficial.",
                        },
                    ],
                },
                "problem_solving": {"score": "40%"},
                "communication_skills": {"score": "70%"},
                "soft_skills": {
                    "skills": [
                        {
                            "name": "Teamwork",
                            "expertise_level": "Intermediate",
                            "justification": "Alex mentioned collaborating with DevOps teams, but didn't provide strong examples of cross-functional teamwork.",
                        },
                        {
                            "name": "Adaptability",
                            "expertise_level": "Beginner",
                            "justification": "Alex showed limited ability to adapt to technical questions outside his comfort zone.",
                        },
                    ]
                },
                "Recommendation_status": {"status": "Not Recommended"},
                "Candidate_summary": {
                    "summary": f"{candidate_name} demonstrated a background primarily in product management with some exposure to AI projects. While he showed enthusiasm and a basic understanding of AI concepts, his technical skills and hands-on experience fall short of the requirements for a Senior AI Engineer role at Unblocked. His strengths lie in communication and product-oriented thinking, but he lacks the deep technical expertise in AI engineering, model optimization, and cloud deployment that are crucial for this position."
                },
            }
        }

        # Create file name: job_name_id.pdf
        safe_job_title = "".join(c if c.isalnum() else "_" for c in job_title)
        file_name = f"{safe_job_title}_{job_id}.pdf"
        file_path = f"/tmp/{file_name}"

        # Generate PDF
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add title
        story.append(Paragraph("Candidate Assessment", styles["Title"]))
        story.append(Spacer(1, 12))

        # Add assessment data
        story.append(Paragraph("Technical Skills", styles["Heading2"]))
        story.append(
            Paragraph(
                f"Score: {assessment_data['assessment']['technical_skills']['score']}",
                styles["Normal"],
            )
        )
        story.append(
            Paragraph(
                f"Justification: {assessment_data['assessment']['technical_skills']['justification']}",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 12))

        for skill in assessment_data["assessment"]["technical_skills"]["skills"]:
            story.append(Paragraph(f"Skill: {skill['name']}", styles["Heading3"]))
            story.append(
                Paragraph(f"Expertise: {skill['expertise_level']}", styles["Normal"])
            )
            story.append(
                Paragraph(f"Justification: {skill['justification']}", styles["Normal"])
            )
            story.append(Spacer(1, 6))

        story.append(Paragraph("Problem Solving", styles["Heading2"]))
        story.append(
            Paragraph(
                f"Score: {assessment_data['assessment']['problem_solving']['score']}",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 12))

        story.append(Paragraph("Communication Skills", styles["Heading2"]))
        story.append(
            Paragraph(
                f"Score: {assessment_data['assessment']['communication_skills']['score']}",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 12))

        story.append(Paragraph("Soft Skills", styles["Heading2"]))
        for skill in assessment_data["assessment"]["soft_skills"]["skills"]:
            story.append(Paragraph(f"Skill: {skill['name']}", styles["Heading3"]))
            story.append(
                Paragraph(f"Expertise: {skill['expertise_level']}", styles["Normal"])
            )
            story.append(
                Paragraph(f"Justification: {skill['justification']}", styles["Normal"])
            )
            story.append(Spacer(1, 6))

        story.append(Paragraph("Recommendation Status", styles["Heading2"]))
        story.append(
            Paragraph(
                f"Status: {assessment_data['assessment']['Recommendation_status']['status']}",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 12))

        story.append(Paragraph("Candidate Summary", styles["Heading2"]))
        story.append(
            Paragraph(
                assessment_data["assessment"]["Candidate_summary"]["summary"],
                styles["Normal"],
            )
        )

        # Build PDF
        doc.build(story)
        return file_path

    @staticmethod
    def upload_file_to_candidate(candidate_id: str, file_path: str) -> bool:
        """Upload PDF to candidate's profile using /candidate.uploadFile."""
        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f, "application/pdf")}
                payload = {"candidateId": candidate_id}
                print("data2", files, payload)
                response = requests.post(
                    f"{BASE_URL}/candidate.uploadFile",
                    headers=AshbyService.get_multipart_headers(),
                    data=payload,
                    files=files,
                )
                response.raise_for_status()
                print(f"PDF {file_path} uploaded for candidate {candidate_id}")
                return True
        except Exception as e:
            print(f"Failed to upload PDF: {e}")
            return False
        # finally:
        #     # Clean up temporary file
        #     if os.path.exists(file_path):
        #         os.remove(file_path)
